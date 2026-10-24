---
id: MM-001
title: Multimedia Asset Standard and Delivery Specification
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Brand Lead
author: Brand with Design System, Platform Engineering and Content Design
reviewers: [Content Design Lead, Design System Lead, Platform Engineering, Localisation Lead, Accessibility reviewer, Chief Technology Officer, Programme Content Lead]
approver: Content Design Lead
content_class: D
purpose: >
  The single production and delivery standard every visual, moving-image and audio asset in the
  programme is commissioned against and accepted against — formats, resolutions, colour, encoding,
  embedded metadata, accessibility deliverables, source-file handover and licence evidence. Eight
  content categories already cite this file as the governing media specification and none of them
  can commission a supplier without it; an asset delivered to no standard is re-commissioned, and
  under a fixed-price brief the cost of re-commissioning falls on the programme rather than on the
  supplier.
traces_to: [VB-003, VB-004, VB-005, VB-006, VB-007, VB-009, CG-005, CG-008, CG-010, CG-011, CG-012, DT-001, DT-044, TR-003, TR-009, HC-002, HC-020, UI-006, UI-010, TS-002, TS-016, BN-006, BN-016, AP-001, CM-005, EO-012, MM-002, MM-003, MM-004, MM-005, MM-006, MM-007, MM-008, MM-009, MM-010, MM-011, MM-012, 04-00 PS-04, 04-00 PS-05, 04-00 PS-06, 04-00 PS-08, 04-00 §P02, 05-06 NFR-073, 05-06 §9, 05-06 §11]
priority: P2
wave: W1
bilingual: no
bn_counterpart: n/a
sources:
  - source: project_content/01_Voice_Brand_and_Design_Content/VB-003_Brand_Application_in_Enterprise_UI.md §3 — measured WCAG contrast ratios for the full CB-001 palette; BC-01 excludes #39B1DF from text and from the 3:1 non-text threshold on white; §5 brand reduced on operational surfaces; §6 brand excluded from P02, P09 and the P11 offline bundle
    verified: 2026-08-18
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md §9 — "MM Multimedia specs — briefs state the accessibility deliverables (captions, transcripts, audio description, alt text) as acceptance criteria"; §4 AT-01…AT-08 text alternatives
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md §3 PS-04 (WCAG 2.1 AA on all web portals), PS-05 (responsive from 320px), PS-06 (one component library, one token set), PS-08 (offline-capable surfaces); §P02 non-negotiable requirement — runs acceptably on a mid-range Android 11 device with 3 GB RAM
    verified: 2026-08-18
    class: P1
  - source: project_content/08_Training_and_Enablement/08A_Framework/TR-003_Course_Design_Standard_and_Storyboard_Template.md §4.10 storyboard field "Media required — screenshot / diagram / video, with source and MM-001 spec"; O-04 records this file as unwritten
    verified: 2026-08-18
    class: P1
  - source: project_content/09_Help_Centre_and_Self_Service/HC-020_Video_Tutorial_Script_Library.md — 22 scripts, "Bengali authored and filmed", 44 productions; O-01 records this file as unwritten and states that nothing can be filmed without it
    verified: 2026-08-18
    class: P1
  - source: W3C Web Content Accessibility Guidelines (WCAG) 2.1 — SC 1.1.1 non-text content, SC 1.2.2 captions (prerecorded, Level A), SC 1.2.3 audio description or media alternative (Level A), SC 1.2.5 audio description (prerecorded, Level AA), SC 1.4.5 images of text (Level AA), SC 1.4.11 non-text contrast (Level AA), SC 2.3.1 three flashes
    verified: 2026-08-18
    class: P1
  - source: IPTC Photo Metadata Standard 2024.1 — IPTC Core and IPTC Extension schemas carried in Adobe XMP (ISO 16684-1); Core covers creator, description, copyright notice, credit line, usage terms and web statement of rights; Extension adds model and property release status and detailed licensor fields
    verified: 2026-08-18
    class: P2
  - source: Browser and platform support for modern raster formats as at 2026 — WebP support is effectively universal across Chrome, Firefox, Safari, Edge and Opera; AVIF support is above 95% globally, having landed in Chrome 2020, Firefox 2021 and Safari 2023; AVIF is reported 15–40% smaller than WebP at equivalent measured visual quality; JPEG XL remains unshipped outside Firefox and Safari Technology Preview and is not viable in production
    verified: 2026-08-18
    class: P3
    note: Corroborated across multiple independent technical sources. Converts to P1 (direct observation) on completion of the §4.11 device and client qualification matrix, which is mandatory before any asset class ships in a new format.
supersedes: none
review_due: 2027-02-18
---

# Multimedia Asset Standard and Delivery Specification

| Item | Value |
|---|---|
| Governs | **Every** visual, moving-image and audio asset produced for the ERP and its twelve portals |
| Consumed by | `MM-002` … `MM-012`, and by eight content categories that commission media |
| Audience | Design, video, photography and animation suppliers; Design System; Platform Engineering |
| Language | **English** — the brief is English; the **assets it governs are frequently bilingual** (`CG-010` §3.2) |
| Wave | W1 · Months 1–4 (`06-01` §3) |
| Content class | **D** — user-facing (`CG-002` §4.1) |
| Commercial status | **This file is what a supplier is paid against.** It is a schedule to a purchase order, not guidance |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3).
> All six sections retained in order. The `CG-009` addition required of every `MM` file — a
> **deliverable specification table** stating format, dimensions, colour, naming and metadata —
> is **§4.2**, placed inside §4 so that §5 and §6 keep their template positions. `CG-009` §6
> proposes template 17 `TPL_Asset_Specification.md`; it does not exist. See `O-02`.

---

## 1. Purpose

Eleven files across eight categories already cite this specification by identifier, and four of
them record it as an **open blocker in their own Definition of Done**:

| Cites `MM-001` for | File | Status recorded there |
|---|---|---|
| Media resolution, format and compression in every storyboard | [`TR-003`](../08_Training_and_Enablement/08A_Framework/TR-003_Course_Design_Standard_and_Storyboard_Template.md) §4.10, §5 | `O-04` — unwritten |
| The production specification behind 22 customer video scripts | [`HC-020`](../09_Help_Centre_and_Self_Service/HC-020_Video_Tutorial_Script_Library.md) | `O-01` — **"nothing can be filmed"** |
| Demonstration video for a mixed-literacy technician cohort | [`TR-009`](../08_Training_and_Enablement/08B_Course_Packs/TR-009_Course_Pack_Field_Technician.md) §7 | Cited |
| The design deliverable implementing the label payload contract | [`DT-044`](../05_Document_and_Print_Templates/05E_People_Quality_and_Labelling/DT-044_Label_Barcode_and_QR_Format_Specification.md) §10 | Cited |
| The asset delivery standard behind partner co-branding | [`EO-012`](../18_Ecosystem_Onboarding_Content/EO-012_Co_Marketing_and_Co_Branding_Asset_Guide.md) §4 | **Unwritten — `O-01` there** |
| Wave-launch kit layout authority | [`CM-005`](../16_Change_Management_and_Comms/CM-005_Wave_Launch_Communication_Kit.md) | `O-05` — *"`MM` holds zero files"* |
| Accessible media specifications for charts, video and images | [`TS-016`](../13_Test_and_Acceptance_Content/TS-016_Accessibility_Test_Script_Pack.md) | `O-07` — no owning specification |

**Consequence of absence (`CP-03`), stated as the commercial fact it is.** A supplier engaged
without an acceptance specification delivers to their own house standard. Their house standard
will not be sRGB-managed, will not embed IPTC rights metadata, will not carry a Bengali caption
file, will not be encoded for a mid-range Android on a congested cell, and will not include the
source file. Every one of those defects is discovered at integration, after the invoice is
approved, and **the re-work is a programme cost because the brief did not ask for it.**

**What this file is not.** It is not the brand identity (§4.12 — that is a live gap), not the
per-asset-class briefs (`MM-002`…`MM-011`), not the repository (`MM-012`), and not a style guide.
It is the **acceptance specification**: the list of things that must be true of a delivered file.

---

## 2. Scope

**In scope.** The production and delivery contract for eleven asset classes (§4.1): the format
and codec set; resolution and density; colour management; compression ceilings; the mandatory
embedded-metadata set; the accessibility deliverables that ship *with* the asset; source-file and
working-file handover; licence and release evidence; the package structure a delivery arrives in;
and the acceptance and rejection procedure.

**Out of scope.**

| Subject | Owned by |
|---|---|
| Screenshot capture, annotation and redaction | [`MM-002`](MM-002_Screenshot_Annotation_and_Redaction_Standard.md) |
| Diagram notation, shape and colour semantics | [`MM-003`](MM-003_Diagram_and_Process_Map_Visual_Standard.md) |
| Icon inventory, grid and states | [`MM-004`](MM-004_Icon_Set_Requirements.md) |
| Illustration style and empty-state inventory | [`MM-005`](MM-005_Illustration_and_Empty_State_Artwork_Brief.md) |
| Training video content and shot direction | [`MM-006`](MM-006_Video_Production_Brief_Training_Series.md) |
| Customer how-to video content | [`MM-007`](MM-007_Video_Production_Brief_Customer_How_To_Series.md) |
| Onboarding animation content | [`MM-008`](MM-008_Animated_Explainer_Brief_Portal_Onboarding.md) |
| Photography direction, consent and safety | [`MM-009`](MM-009_Photography_Brief_Branches_Workshop_and_Field.md) |
| Print-engine implementation of the page design | [`MM-010`](MM-010_PDF_and_Print_Template_Design_Specification.md) |
| Email-safe markup and email image assets | [`MM-011`](MM-011_Email_and_HTML_Asset_Specification.md) |
| Repository structure, naming, versioning, rights records, retirement | [`MM-012`](MM-012_Digital_Asset_Management_and_Naming_Standard.md) |
| Where brand applies, is reduced, or is excluded on a surface | [`VB-003`](../01_Voice_Brand_and_Design_Content/VB-003_Brand_Application_in_Enterprise_UI.md) |
| Page geometry, print type scale, bilingual print layout | [`VB-004`](../01_Voice_Brand_and_Design_Content/VB-004_Print_and_PDF_Brand_Template_Standard.md) |
| The email shell, dark-mode colour pairs, plain-text parity | [`VB-005`](../01_Voice_Brand_and_Design_Content/VB-005_Email_Brand_Template_Standard.md) |
| Chart and visualisation labelling | [`RP-007`](../14_Reporting_Analytics_and_KPI/RP-007_Chart_Label_and_Visualisation_Standard.md) |
| Export watermarking and confidentiality marking | [`RP-014`](../14_Reporting_Analytics_and_KPI/RP-014_Export_Watermark_and_Confidentiality_Marking_Rules.md) |
| Which content is Bengali at all | [`CG-010`](../00_Content_Governance_and_Standards/CG-010_Bilingual_Content_Policy.md) |

> **`CP-01` boundary with `MM-012`.** This file governs **what a compliant file is**. `MM-012`
> governs **where it lives, what it is called and how long it is kept**. Naming appears in §4.2
> only as a pointer to `MM-012` §4.3; no naming pattern is defined twice.

---

## 3. Audience

| Reader | Uses it for | Reads it |
|---|---|---|
| **External design / video / photography supplier** | The acceptance specification attached to their purchase order | Before quoting, and again before delivery |
| **Procurement (`R21`)** | The schedule referenced in the RFQ and PO ([`DT-022`](../05_Document_and_Print_Templates/05C_Supply_Chain_and_Logistics/DT-022_Request_for_Quotation.md), [`DT-023`](../05_Document_and_Print_Templates/05C_Supply_Chain_and_Logistics/DT-023_Purchase_Order.md)) | At sourcing |
| **Design System Lead** | Format and density rules for icons, illustration and component art | Continuously |
| **Platform Engineering** | What the build pipeline must accept, transcode, serve and cache | At integration |
| **L&D and Content Design** | What to ask for in a storyboard and what to reject on receipt | Per production |
| **Accessibility reviewer** | The accessibility deliverables that are acceptance criteria, not extras | At acceptance |
| **Localisation Lead** | The bilingual asset rules and the never-text-in-an-image prohibition | Per bilingual asset |
| **Brand Lead** | The colour and identity constraints, and the §4.12 gap | Continuously |

---

## 4. Content

### 4.1 The eleven asset classes

Every asset the programme commissions is in exactly one class. **A deliverable that fits no class
is not commissioned until a class is added here** (`AS-01`).

| # | Class | Typical origin | Governing brief | Ships to |
|---:|---|---|---|---|
| **A1** | **Product screenshot** | Sandbox capture | `MM-002` | Help, training, knowledge, release notes |
| **A2** | **Icon / glyph** | Design System | `MM-004` | All twelve portals, print, email |
| **A3** | **Illustration / empty-state artwork** | Design or supplier | `MM-005` | `UI-006` surfaces, first-run, error pages |
| **A4** | **Diagram / process map** | Business Process, EA | `MM-003` | SOPs, architecture, training, town halls |
| **A5** | **Chart / data visualisation** | BI | `RP-007` (labels) + this file (export) | Dashboards, board packs, reports |
| **A6** | **Photograph** | Commissioned shoot | `MM-009` | Brand, careers, help, corporate material |
| **A7** | **Video — training** | Commissioned production | `MM-006` | LMS (`M22`), `P02` microlearning |
| **A8** | **Video — customer how-to** | Commissioned production | `MM-007` | Help centre, in-product, contact centre |
| **A9** | **Animation / motion** | Commissioned production | `MM-008` | Portal onboarding, first-run tours |
| **A10** | **Audio** — narration, IVR prompt, alert tone | Studio | This file + [`NT-019`](../04_Notification_and_Messaging/04D_In_App_Voice_and_System/NT-019_IVR_and_Voice_Prompt_Scripts.md) / [`BN-017`](../11_Localisation_Bengali/BN-017_Bengali_Voice_IVR_and_Speech_Prompt_Pack.md) | IVR, video, app feedback |
| **A11** | **Print / document artwork** — logo lock-ups, watermarks, label artwork | Brand + Platform | `MM-010`, `DT-044` | Print engine, thermal, labels |

### 4.2 Deliverable specification — the acceptance table

**This is the `CG-009` §3 required addition for Category 19.** Every row is testable by
inspection of the delivered file. A delivery is accepted or rejected against this table and
nothing else (`AS-02`).

| Class | Master format (delivered) | Derived formats | Dimensions / resolution | Colour | Compression ceiling | Embedded metadata | Naming |
|---|---|---|---|---|---|---|---|
| **A1** Screenshot | **PNG-24, lossless** | AVIF + WebP + PNG for web | Capture at 2× the target CSS pixel size; `MM-002` §4.2 fixes the viewports | **sRGB IEC 61966-2.1** | Lossless master; derived ≤ 150 KB at 1× | **Stripped, then re-stamped** — `MM-002` `SC-19` | `MM-012` §4.3 |
| **A2** Icon | **SVG 1.1**, optimised, `currentColor` | Sprite; PNG @1×/2×/3× for email and print | 24 px design grid; `MM-004` §4.2 | Inherits; **no fill baked in** | ≤ 3 KB per glyph, optimised | XMP `dc:title`, `dc:rights` | `MM-012` §4.3 |
| **A3** Illustration | **SVG** (flat) or layered source + SVG export | AVIF/WebP/PNG @1×/2× | Artboard 800 × 600 px nominal, scalable | sRGB; palette from `MM-005` §4.4 | **≤ 40 KB SVG**, ≤ 60 KB raster @1× | XMP creator, rights, licence term | `MM-012` §4.3 |
| **A4** Diagram | **BPMN 2.0 XML** where BPMN; **SVG** always | PNG @2× for slides and print | Fits 1366 × 600 without horizontal scroll (`VB-003` `D-01`) | sRGB; **greyscale-survivable** (`MM-003` §4.3) | ≤ 120 KB SVG | SVG `<title>`/`<desc>` populated | `MM-012` §4.3 |
| **A5** Chart export | **SVG** | PNG @2×; CSV of the plotted data | Per target surface | sRGB | — | Data table accompanies (`CG-011` `AT-06`) | `MM-012` §4.3 |
| **A6** Photograph | **Camera raw + 16-bit TIFF master** | AVIF/WebP/JPEG @ 3 widths | Long edge ≥ 4000 px | Capture **Adobe RGB**, deliver **sRGB**; print profile on request | Derived JPEG q80, ≤ 300 KB at 1600 px | **IPTC Core + Extension, mandatory** — §4.9 | `MM-012` §4.3 |
| **A7** Video training | **ProRes 422 / DNxHD master** | H.264 ladder §4.5 | ≤ 1280 × 720 delivery; master 1920 × 1080 | Rec. 709 | Per §4.5 ladder | Title, language, duration, caption track IDs | `MM-012` §4.3 |
| **A8** Video customer | As A7 | H.264 ladder §4.5, **vertical variant** | 1080 × 1920 vertical master; 1280 × 720 landscape | Rec. 709 | Per §4.5 | As A7 | `MM-012` §4.3 |
| **A9** Animation | **Lottie JSON** (preferred) or layered source | MP4 fallback; **static first-frame PNG** | Vector; nominal 400 × 300 | sRGB | **≤ 100 KB Lottie**; ≤ 500 KB MP4 | Author, licence | `MM-012` §4.3 |
| **A10** Audio | **WAV 48 kHz / 24-bit** | **AAC-LC 128 kbps** stereo, **64 kbps mono** for IVR | — | — | Normalised to **−16 LUFS** (mono −19 LUFS), true peak ≤ −1 dBTP | Language, script reference, speaker | `MM-012` §4.3 |
| **A11** Print artwork | **Vector PDF/X-4** or SVG | 1-bit monochrome PNG for thermal | Per [`VB-004`](../01_Voice_Brand_and_Design_Content/VB-004_Print_and_PDF_Brand_Template_Standard.md) §3 | **Monochrome for thermal**; no gradients, no tints | — | Producer, colour profile | `MM-012` §4.3 |

| # | Rule |
|---|---|
| **AS-03** | **The master is delivered, not only the derivative.** A delivery consisting solely of a web-optimised export is rejected. The master is what the next five years of derivatives are made from |
| **AS-04** | Derived formats are **generated by the build pipeline, not by the supplier**, except where this table says otherwise. A supplier-generated derivative cannot be regenerated when the pipeline changes |
| **AS-05** | Every ceiling in this table is a **hard ceiling measured on the delivered file**, not a target |
| **AS-06** | Where a class has both a vector and a raster row, **the vector is the master.** A raster-only delivery of something that could be vector is rejected |

### 4.3 Colour management

| # | Rule |
|---|---|
| **CS-01** | **sRGB IEC 61966-2.1 is the delivery colour space for every screen asset**, with the profile **embedded**, not assumed. An untagged file renders differently on a wide-gamut phone than on a branch monitor |
| **CS-02** | Photography is **captured** in Adobe RGB or wider and **delivered** in sRGB. The wide-gamut master is retained in `MM-012` |
| **CS-03** | **Print artwork carries no colour.** `VB-004` §5 prohibits colour fills, gradients and background tints on documents; thermal output is monochrome only (`VB-004` `F-03`, `TH-02`) |
| **CS-04** | **The `VB-003` §3 contrast finding binds every asset, not only UI.** `#39B1DF` measures **2.46:1** on white and fails both SC 1.4.3 text contrast and the SC 1.4.11 3:1 non-text threshold. It may be a **fill**, a chart series, an illustration colour or the brand mark. It may never carry a glyph, a rule, a border, a focus ring or a status dot **on a light background** |
| **CS-05** | `#FFC107` Warning Yellow is a **fill only** (1.63:1 on white). Text on yellow is `#212529` |
| **CS-06** | **Every new colour pair introduced by an asset is measured and recorded before use** (`VB-005` `CL-02` applied to media). "It looked fine" is not a measurement |
| **CS-07** | Assets are checked in **greyscale** as well as colour. `CG-011` `CL-01` prohibits colour as the only signal, and a large share of this workforce reads printed and photocopied material (`VB-004` §5) |
| **CS-08** | **Dark-mode variants are authored, never derived by inversion.** An inverted logo, photograph or illustration is a different asset, not the same asset in another theme (`VB-005` `CL-07`) |

### 4.4 Raster formats and density

| Format | Use | Do not use for |
|---|---|---|
| **AVIF** | Primary web delivery for photography and illustration | **Email** (§4.11), print, anything a supplier must open |
| **WebP** | Universal web fallback | Email, print |
| **JPEG** | Final safety net; photography where AVIF/WebP are unavailable | Screenshots, line art, anything with hard edges |
| **PNG-24** | Screenshots, line art, anything needing alpha, **all email imagery** | Photography at scale — the file size is indefensible |
| **SVG** | Icons, illustration, diagrams, logos | Photography; anything with a raster embedded inside it |
| **GIF** | **Only** where an animation must run in email (`MM-011` §4.3) | Everything else. Use Lottie or MP4 |
| **JPEG XL** | **Not used.** Unshipped outside Firefox and Safari Technology Preview as at 2026 | — |

| # | Rule |
|---|---|
| **RA-01** | The web delivery chain is **AVIF → WebP → JPEG/PNG**, negotiated by the platform. AVIF is above 95% global support and is reported 15–40% smaller than WebP at equal measured quality; **the fallback chain exists for the remaining share and for corporate proxies that strip modern types** |
| **RA-02** | Density variants are **@1×, @2× and @3×**. `PS-05` responsive from 320 px means the 3× case is a real device in this market, not an Apple-only case |
| **RA-03** | **Every raster asset declares intrinsic width and height** so layout does not shift while it loads. This is a `NFR-073` accessibility consequence as well as a performance one |
| **RA-04** | **Text is never rendered into a raster asset** where it can be live text — WCAG SC 1.4.5 (Level AA), `CG-011` `AT-07`, `VB-005` `BF-05`, `VB-009` `BR-06`. The permitted exceptions are exactly three: a **logo**, a **screenshot** (where the text is the subject), and **on-screen text burned into video** (§4.5) |
| **RA-05** | Bengali is never set into an image to guarantee a font (`VB-009` `BR-06`). The three `RA-04` exceptions are the only places Bengali may appear as pixels, and each carries a text alternative |

### 4.5 Moving image — the encoding ladder

The constraint is not the national average. **Bangladesh's Ookla-measured mobile download average
was 41.72 Mbps for the September–November 2025 period, ranking 86th globally**, and it is a
national mean over a network with acute spectrum shortage, uneven 4G reach and heavy subscriber
density. `MM-006` and `MM-007` are watched by a **field technician on a congested cell at a
customer's premises** and by a **customer paying for the megabytes**, which is the case the ladder
is designed for.

| Rung | Resolution | Video bitrate | Audio | Intended case |
|---|---|---:|---|---|
| **L0 audio-only** | — | — | AAC 64 kbps mono | Transcript-plus-audio fallback where video will not start |
| **L1** | 426 × 240 | **200 kbps** | AAC 64 kbps mono | Edge of coverage; the rung that must always play |
| **L2** | 640 × 360 | **500 kbps** | AAC 96 kbps | The **default** rung on mobile data |
| **L3** | 854 × 480 | 900 kbps | AAC 128 kbps | Good 4G; branch Wi-Fi |
| **L4** | 1280 × 720 | 1,800 kbps | AAC 128 kbps | **Ceiling.** Branch Wi-Fi and desktop only |

| # | Rule |
|---|---|
| **VE-01** | **H.264 High Profile, Level 4.0 maximum.** Hardware decode on a mid-range Android 11 with 3 GB RAM (`04-00` §P02) is the compatibility floor. **HEVC and AV1 are not delivered** — decode support on that device class cannot be assumed |
| **VE-02** | **720p is a ceiling, not a target.** No 1080p or 4K delivery rung exists. Masters are 1080p; nothing above 720p is ever served |
| **VE-03** | Adaptive delivery is **HLS with the ladder above**; a **progressive MP4 at L2** is always published alongside for offline download and for clients that cannot negotiate |
| **VE-04** | **Every training video is downloadable for offline viewing** at L2 or below. `PS-08` surfaces operate offline for 24 hours and a technician cannot stream in a basement plant room |
| **VE-05** | Keyframe interval **2 seconds**, closed GOP, so scrubbing and segment switching behave |
| **VE-06** | **`faststart` / `moov` atom at the head** of every MP4. Without it playback waits for the whole file |
| **VE-07** | A **poster frame** is delivered with every video: a real frame from the first 5 seconds, never a title card |
| **VE-08** | **No auto-play with sound, anywhere.** Much of this audience watches in public, and `CG-011` treats an unrequested time-based change as an accessibility failure |
| **VE-09** | **Nothing flashes more than three times in any one second** — WCAG SC 2.3.1. This is checked, not assumed |
| **VE-10** | On-screen text respects the Bengali floors in [`VB-009`](../01_Voice_Brand_and_Design_Content/VB-009_Bengali_Typography_and_Brand_Standard.md) §3 **measured at the L1 rung**, not at the master resolution. Text legible at 720p and illegible at 240p is a defect |

### 4.6 Audio

| # | Rule |
|---|---|
| **AU-01** | Narration is **recorded**, never synthesised, for anything a customer or a field employee hears — the same position `CP-05` takes on machine translation, for the same reason |
| **AU-02** | Bengali narration is **spoken by a native speaker and recorded from a Bengali-authored script** (`DS-17`, `VS-07`). An English recording with a Bengali track laid over it is not a Bengali asset |
| **AU-03** | Loudness is normalised to **−16 LUFS integrated** (−19 LUFS mono), true peak **≤ −1 dBTP**. A library where every item has a different level is a library nobody uses on a phone speaker |
| **AU-04** | **Speech is intelligible on a phone loudspeaker in a workshop.** Music beds sit **at least 18 dB below** speech, or are omitted |
| **AU-05** | **Audio is never the only carrier.** Every audio asset ships a transcript (§4.7). A workforce that often works without headphones, in noise, is the design case |
| **AU-06** | IVR prompts are produced to [`NT-019`](../04_Notification_and_Messaging/04D_In_App_Voice_and_System/NT-019_IVR_and_Voice_Prompt_Scripts.md) and [`BN-017`](../11_Localisation_Bengali/BN-017_Bengali_Voice_IVR_and_Speech_Prompt_Pack.md), delivered as discrete files per prompt — never as one concatenated recording, which cannot be re-recorded in part |

### 4.7 Accessibility deliverables — acceptance criteria, not extras

`CG-011` §9 states the obligation on this category directly: *"`MM` Multimedia specs — briefs
state the accessibility deliverables — captions, transcripts, audio description, alt text — as
acceptance criteria."* **This section is that statement, made testable.**

| Asset class | Mandatory accessibility deliverables | WCAG SC |
|---|---|---|
| A1 Screenshot | Alt text **in both languages**; long description where the screenshot carries a procedure | 1.1.1 |
| A2 Icon | Accessible name per `VB-007` §5/§6; **3:1 non-text contrast verified** | 1.1.1, 1.4.11 |
| A3 Illustration | Marked **decorative with empty alt** (`UI-006` §7); if it carries information, it is the wrong asset | 1.1.1 |
| A4 Diagram | `<title>` + `<desc>` in the SVG, **plus** a text alternative that is the step table or numbered flow | 1.1.1, 1.3.1 |
| A5 Chart | Data table accompanying, series labelled directly, colour never the only encoding | 1.1.1, 1.4.1 |
| A6 Photograph | Alt text in both languages; **decorative photography marked decorative** | 1.1.1 |
| A7 / A8 Video | **Captions in both languages (SC 1.2.2, Level A)**; **transcript**; **audio description or a full text media alternative (SC 1.2.3)** — and **audio description where AA conformance is claimed (SC 1.2.5)**; no auto-play; no flashing | 1.2.2, 1.2.3, **1.2.5**, 2.3.1 |
| A9 Animation | Static first frame carrying the same meaning; **honours `prefers-reduced-motion`**; no flashing; not the only carrier | 2.2.2, 2.3.1, 2.3.3 |
| A10 Audio | Transcript in the same language | 1.2.1 |
| A11 Print artwork | Text alternative in the tagged PDF (`VB-004` `AC-03`) | 1.1.1 |

| # | Rule |
|---|---|
| **AC-01** | **Captions are delivered as a separate timed-text file** — WebVTT — never burned into the picture. Burned captions cannot be turned off, cannot be translated, and cannot be read by a search index |
| **AC-02** | **Captions are authored, not auto-generated.** Automatic Bengali speech recognition is not accurate enough to caption safety or money content, and an inaccurate caption is worse than none |
| **AC-03** | Captions carry **speaker changes and meaningful non-speech sound** (an alarm, a click that confirms a scan) |
| **AC-04** | The **transcript is a document, not a caption dump** — paragraphs, headings and the on-screen text included, so it works as a text alternative under SC 1.2.3 |
| **AC-05** | **Where audio description would be needed because the picture carries information the narration does not, the correct fix is usually to change the narration.** A video whose narration already describes what is shown needs no separate description track, and this is cheaper and better than adding one |
| **AC-06** | **The accessibility deliverables are line items on the purchase order.** A supplier who has not priced captions will not produce captions, and `AS-15` makes the delivery incomplete without them |
| **AC-07** | Alt text is **authored in the consuming content file**, not by the media supplier (`CG-011` `AT-01`). The supplier delivers the asset; `HC-`, `TR-` and `UI-` files author its alternative |

### 4.8 Bilingual assets

`CG-010` §3.2 places Category 19 **English-only, 12 of 12**, with the rationale: *"Specifications
for suppliers, who work in English. The assets they produce are bilingual; the briefs are not."*

> **That rationale is correct here, and it is worth recording why.** `AUDIT-017` `OP-13` and
> `AUDIT-018` `EO-13` both found `CG-010`'s per-file model unable to express *"a file whose
> outputs are bilingual"*. For Category 19 the register **anticipated the case and stated it in
> the rationale column**. `MM` therefore does not add a fourth instance to that finding — but the
> obligation it creates lands here, in `AS-16`…`AS-19`.

| # | Rule |
|---|---|
| **AS-16** | **A bilingual asset is two assets**, not one asset with a language switch, wherever the language is baked in — video, screenshot, on-screen text, print artwork. They share a stem and differ by the `_bn` / `_en` element in `MM-012` §4.3 |
| **AS-17** | **Cost is stated per language at quotation.** `HC-020` already records the consequence: 22 scripts become **44 productions**, and that figure is not in the content estimate |
| **AS-18** | Where an asset can be built so the text layer is **separable** — a diagram, an animation, a print template — it is, so the second language is a re-render rather than a re-production (`MM-003` `DG-15`, `MM-008` `AN-12`) |
| **AS-19** | **A missing Bengali variant blocks publication of the pair, not only of the Bengali** (`CM-R6`, `CG-010` `BP-05`). A surface that is 80% Bengali teaches the user the product is not for them |

### 4.9 Embedded metadata

Metadata that travels **inside** the file. The repository record is `MM-012`; this is what must
be present in the bytes so the asset is still identifiable after it has been emailed, copied and
found on a laptop three years later.

| Field | Standard | A1 | A2/A3/A4 | A6 | A7/A8/A9 | A10 |
|---|---|:--:|:--:|:--:|:--:|:--:|
| Title / headline | XMP `dc:title` | ✔ | ✔ | ✔ | ✔ | ✔ |
| Description | XMP `dc:description` | ✔ | ✔ | ✔ | ✔ | ✔ |
| Creator | IPTC Core Creator | — | ✔ | **✔** | ✔ | ✔ |
| Credit line | IPTC Core Credit Line | — | — | **✔** | ✔ | — |
| Copyright notice | IPTC Core Copyright Notice | ✔ | ✔ | **✔** | ✔ | ✔ |
| **Usage terms** | IPTC Core Rights Usage Terms | — | ✔ | **✔** | ✔ | ✔ |
| Web statement of rights | IPTC Core | — | — | **✔** | — | — |
| **Model release status** | IPTC Extension | — | — | **✔ mandatory** | **✔ mandatory** | — |
| **Property release status** | IPTC Extension | — | — | **✔ mandatory** | ✔ | — |
| Licensor | IPTC Extension | — | — | ✔ | ✔ | — |
| Date created | XMP `xmp:CreateDate` | ✔ | ✔ | ✔ | ✔ | ✔ |
| Language | XMP / container | ✔ | ✔ | — | ✔ | ✔ |
| Owning content ID | XMP `dc:relation` = `MM-nnn` / consuming ID | ✔ | ✔ | ✔ | ✔ | ✔ |

| # | Rule |
|---|---|
| **MT-01** | **IPTC Core and IPTC Extension carried in XMP** is the metadata standard for this programme. IPTC Core supplies creator, description, copyright notice, credit line and usage terms; **IPTC Extension supplies the model and property release fields that make a photograph safe to publish** |
| **MT-02** | **Every photograph and every video containing an identifiable person carries a release status.** An asset whose release status is empty is treated as **unreleased** and is not published (`MM-009` §4.2) |
| **MT-03** | **Location metadata is stripped from every asset before publication.** EXIF GPS coordinates on a photograph of a branch, a customer's premises or a technician's home are a security and privacy disclosure, and they survive every casual copy of the file |
| **MT-04** | Camera serial, device identifiers and author software strings are stripped. They are attributable to an individual |
| **MT-05** | **Metadata is stripped, then re-stamped from the `MM-012` record** — never edited in place. Stripping alone loses rights; editing alone leaves residue (`MM-002` `SC-19` applies the same order to screenshots) |
| **MT-06** | The build pipeline **must not strip XMP on optimisation.** Most image optimisers do this by default; the pipeline is configured to preserve the IPTC block and this is a tested condition |

### 4.10 Delivery, source files and licence evidence

| # | Rule |
|---|---|
| **DL-01** | A delivery is a **package with a manifest**, not a folder of files. The manifest lists every file, its class, its variants, its language and its `MM-012` record |
| **DL-02** | **Editable source is delivered with the output** — layered design file, project file, After Effects or Lottie source, camera raw, uncut footage, session files. **This is a payment condition, not a courtesy** |
| **DL-03** | **Fonts used in source files are named, and their licence is evidenced.** A source file that cannot be re-opened without an unlicensed font is not a source file. Inter and Hind Siliguri are the programme faces (`VB-004` `T-02`, `VB-009` `TF-01`) |
| **DL-04** | **Third-party material carries its licence** — stock, music, footage, typefaces, model releases — with term, territory, media and expiry, recorded in `MM-012` §4.5 |
| **DL-05** | **Rights are assigned in writing.** Under Bangladesh copyright law the creator is the default owner and a commissioning party owns the copyright only where an agreement so provides; **moral rights remain with the author regardless** (`MM-009` §4.6). A purchase order that does not assign copyright has not bought it |
| **DL-06** | **No perpetual dependency on a supplier's account.** Assets hosted only in a supplier's cloud tenancy, or dependent on their licence subscription, are not delivered |
| **DL-07** | Delivery is to the repository (`MM-012`), not to an individual's mailbox. An asset that exists only in an email thread does not exist |

### 4.11 Acceptance and rejection

| Check | Method | Blocking? |
|---|---|:--:|
| Class declared and the §4.2 row satisfied in full | Automated file inspection | **Yes** |
| Master format present alongside derivatives (`AS-03`) | Manifest check | **Yes** |
| sRGB profile embedded (`CS-01`) | Automated | **Yes** |
| Ceiling not exceeded (`AS-05`) | Automated | **Yes** |
| IPTC/XMP mandatory fields populated (§4.9) | Automated | **Yes** |
| **Location and device metadata stripped (`MT-03`, `MT-04`)** | Automated | **Yes** |
| **Release status present for every identifiable person (`MT-02`)** | Manual + automated | **Yes** |
| Accessibility deliverables present (§4.7) | Manual | **Yes** |
| Bengali variant present where required (`AS-19`) | Manual | **Yes** |
| Contrast of any new colour pair measured (`CS-06`) | Automated | **Yes** |
| Editable source and licence evidence present (`DL-02`, `DL-04`) | Manual | **Yes** |
| **Plays / renders on the qualification matrix** below | **Physical device test** | **Yes** |
| Greyscale legibility (`CS-07`) | Manual | No — recorded |

**The qualification matrix.** Nothing is accepted on a designer's monitor alone.

| Surface | Qualified on | Authority |
|---|---|---|
| Web portals | Chrome, Firefox, Safari, Edge — desktop and Android | `VB-009` §7 |
| `P02`, `P09`, `P11` | **A mid-range Android 11 device with 3 GB RAM** | `04-00` §P02 |
| `P01` app | Android and iOS, low and high density | `VB-009` §7 |
| Email | Outlook desktop, Gmail web, Gmail Android, Apple Mail iOS | `VB-005` `CB-05` |
| Print | **Every supported printer model** | `05-06` §9, `VB-004` `BL-08` |
| Thermal | **Every supported thermal printer model** | `VB-004` `TH-08` |
| Video | The `P02` baseline device **on a throttled connection at the L1 rung** | `VE-01`, `VE-04` |

> **`AS-20`: a rejection is stated against a rule identifier from this file.** "It doesn't look
> right" is not a rejection a supplier can act on, and it is not a rejection they can be held to
> commercially.

### 4.12 The master identity — a stated gap, not an assumption

**`AUDIT-018` finding `EO-13` records that no file in this content set holds the 1000FiX logo, its
clear space, minimum size, colour system or misuse rules.** `EO-012` §4.4 sets an approval
checklist for partner use of the marks whose items 3, 4 and 5 *"have nothing to check against"*,
and recommendation **R-13** asks the Brand Lead either to register the identity standard in `VB`
or to accept `MM-001` as its home, **before a mark is issued to any partner**.

**This file does not silently become the identity standard.** The position taken here:

| Question | Position |
|---|---|
| Does `MM-001` hold the identity? | **No.** This is a production and delivery specification. An identity standard states construction, clear space, minimum size, misuse and lock-ups — a different document with a different owner and a different review cycle |
| Where does the identity live today? | Only in `CB-001` in the **corporate-website content set** — *"a separate content set with a separate approval authority"* (`EO-012`), which `LG-022` `CC-06` already names as a likely origin of an overstated claim |
| What does `MM-001` do about it? | It governs **how identity assets are produced and delivered once the standard exists** — §4.2 class A11, §4.3 colour, §4.9 metadata — and it **records the gap as `O-01`**, with the two available resolutions and the decision owner |
| Can a mark be issued to a partner now? | **No.** `EO-012` `CB-03` is unenforceable until the identity standard is registered, and this file does not make it enforceable |

> **Why the distinction is worth the paragraph.** Accepting `MM-001` as the identity home would
> close `R-13` on paper and leave `EO-012` with the same nothing to check against. **A recorded
> gap with a named owner is a better answer than a false home** — which is the position `CG-012`
> §6 takes on unsourceable claims generally.

### 4.13 Rules

| # | Rule |
|---|---|
| **AS-01** | Every commissioned asset is in exactly one §4.1 class. A deliverable fitting no class is not commissioned until a class is added here |
| **AS-02** | Acceptance is against §4.2 and §4.11 only. No informal acceptance criterion binds a supplier |
| **AS-07** | **This file is attached to the purchase order.** A media purchase order that does not reference `MM-001` by version is a procurement defect (`DT-023`) |
| **AS-08** | The supplier confirms in writing, before starting, that they can meet §4.2 for their classes. A capability discovered at delivery is discovered too late |
| **AS-09** | **Nothing is produced from a production system.** Screenshots come from the sandbox (`MM-002`), photography carries consent (`MM-009`), and no asset contains live customer, employee or partner data |
| **AS-10** | Assets are **designed at the smallest surface they will appear on**, then scaled up — never the reverse. `PS-05` responsiveness starts at 320 px |
| **AS-11** | **Weight is a design constraint, not a build-time optimisation.** `HC-002` §4.9 treats page weight on 3G as an accessibility issue in this market, and an asset over its ceiling is a defect at design review |
| **AS-12** | Motion honours `prefers-reduced-motion`; nothing autoplays with sound; nothing flashes more than three times a second |
| **AS-13** | **No asset is the sole carrier of information** (`CG-011` `AT-06`, `CL-01`). Every one has a text equivalent that is authored somewhere |
| **AS-14** | Assets carrying a statutory or safety statement are **approved by the owning function** — HSE for safety (`SP-030`, `KB-013`), Legal for statutory — and are **never abbreviated for pace or composition** |
| **AS-15** | **A delivery missing its accessibility deliverables is incomplete, not late.** It is not accepted, not partially paid and not published |
| **AS-21** | A change to this file's §4.2 table is a **MAJOR** change (`CG-006` §6.2) and triggers an impact assessment on every open purchase order referencing it |
| **AS-22** | Assets are versioned; a published asset is **immutable** and a change is a new version (`MM-012` §4.4). Overwriting a served file changes documents already issued |
| **AS-23** | **Every decision taken under this standard is logged in [`RF-006`](../99_Reference_and_Registers/RF-006_Content_Decision_Log_and_Change_Control.md)** — including format decisions, ceiling waivers and accepted deviations. **The log exists; the `MM` entries do not yet.** See `O-05` |
| **AS-24** | Where this file and a per-class brief (`MM-002`…`MM-011`) differ, **the per-class brief governs on content and this file governs on format, delivery and acceptance** |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| [`VB-003_Brand_Application_in_Enterprise_UI.md`](../01_Voice_Brand_and_Design_Content/VB-003_Brand_Application_in_Enterprise_UI.md) | §3 measured contrast findings (`CS-04`, `CS-05`); §5 and §6 where imagery and illustration are permitted at all |
| [`VB-004_Print_and_PDF_Brand_Template_Standard.md`](../01_Voice_Brand_and_Design_Content/VB-004_Print_and_PDF_Brand_Template_Standard.md) | Class A11; the no-colour-fill and thermal-monochrome constraints |
| [`VB-005_Email_Brand_Template_Standard.md`](../01_Voice_Brand_and_Design_Content/VB-005_Email_Brand_Template_Standard.md) | Why email is excluded from the modern raster chain; `MM-011` implements it |
| [`VB-006_Design_System_Content_Standards.md`](../01_Voice_Brand_and_Design_Content/VB-006_Design_System_Content_Standards.md) | The component slots assets fill; empty-state contract |
| [`VB-007_Iconography_and_Label_Pairing_Register.md`](../01_Voice_Brand_and_Design_Content/VB-007_Iconography_and_Label_Pairing_Register.md) | Icon meanings and accessible names `MM-004` produces glyphs for |
| [`VB-009_Bengali_Typography_and_Brand_Standard.md`](../01_Voice_Brand_and_Design_Content/VB-009_Bengali_Typography_and_Brand_Standard.md) | Bengali minimum sizes in on-screen text; the never-Bengali-as-an-image rule |
| [`CG-005_Content_ID_and_Naming_Convention.md`](../00_Content_Governance_and_Standards/CG-005_Content_ID_and_Naming_Convention.md) | §5 counterpart naming and the `assets/` convention `MM-012` extends |
| [`CG-008_Content_Definition_of_Done_and_QA_Checklist.md`](../00_Content_Governance_and_Standards/CG-008_Content_Definition_of_Done_and_QA_Checklist.md) | `U-41` and `HC-c`, which make media conformance a Definition-of-Done item |
| [`CG-010_Bilingual_Content_Policy.md`](../00_Content_Governance_and_Standards/CG-010_Bilingual_Content_Policy.md) | §3.2 English-only briefs, bilingual outputs (§4.8) |
| [`CG-011_Accessibility_Content_Standard.md`](../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md) | §9 `MM` row — the obligation §4.7 discharges |
| [`CG-012_Content_Sourcing_and_Evidence_Rules.md`](../00_Content_Governance_and_Standards/CG-012_Content_Sourcing_and_Evidence_Rules.md) | Source classes; the P3 note on format-support figures |
| [`DT-001_Document_Template_Standard_and_Branding_Rules.md`](../05_Document_and_Print_Templates/DT-001_Document_Template_Standard_and_Branding_Rules.md) | The document content standard `MM-010` implements |
| [`DT-044_Label_Barcode_and_QR_Format_Specification.md`](../05_Document_and_Print_Templates/05E_People_Quality_and_Labelling/DT-044_Label_Barcode_and_QR_Format_Specification.md) | Class A11 label artwork; the payload contract this file must not re-define |
| [`TR-003_Course_Design_Standard_and_Storyboard_Template.md`](../08_Training_and_Enablement/08A_Framework/TR-003_Course_Design_Standard_and_Storyboard_Template.md) | The storyboard field that cites this file; `DS-12`…`DS-16` screenshot discipline |
| [`HC-002_Help_Article_Template_and_Style_Rules.md`](../09_Help_Centre_and_Self_Service/HC-002_Help_Article_Template_and_Style_Rules.md) | `HS-17`…`HS-22` screenshot regime; page weight as accessibility |
| [`HC-020_Video_Tutorial_Script_Library.md`](../09_Help_Centre_and_Self_Service/HC-020_Video_Tutorial_Script_Library.md) | The 22 scripts `MM-007` produces; `VS-03`, `VS-07`, `VS-08`, `VS-15` |
| [`UI-006_Empty_State_and_First_Run_Copy_Library.md`](../03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-006_Empty_State_and_First_Run_Copy_Library.md) · [`UI-010_Accessibility_Text_Library.md`](../03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-010_Accessibility_Text_Library.md) | Where illustration and alt text are consumed |
| [`TS-002_Test_Data_Pack_and_Persona_Set.md`](../13_Test_and_Acceptance_Content/TS-002_Test_Data_Pack_and_Persona_Set.md) · [`TS-016_Accessibility_Test_Script_Pack.md`](../13_Test_and_Acceptance_Content/TS-016_Accessibility_Test_Script_Pack.md) | The sandbox every capture comes from; where §4.7 is executed |
| [`BN-006_Bengali_Typography_Font_and_Numeral_Standard.md`](../11_Localisation_Bengali/BN-006_Bengali_Typography_Font_and_Numeral_Standard.md) · [`BN-016_Bengali_Help_and_Training_Content_Plan.md`](../11_Localisation_Bengali/BN-016_Bengali_Help_and_Training_Content_Plan.md) | Bengali typography; `HC-B05` language-specific screenshots |
| [`RP-007_Chart_Label_and_Visualisation_Standard.md`](../14_Reporting_Analytics_and_KPI/RP-007_Chart_Label_and_Visualisation_Standard.md) · [`RP-014_Export_Watermark_and_Confidentiality_Marking_Rules.md`](../14_Reporting_Analytics_and_KPI/RP-014_Export_Watermark_and_Confidentiality_Marking_Rules.md) | Class A5 labelling; export marking on delivered artefacts |
| [`AP-001_Developer_Portal_Information_Architecture.md`](../15_Integration_and_Developer_Content/AP-001_Developer_Portal_Information_Architecture.md) | Cites `MM-010` for developer-portal visual design |
| [`CM-005_Wave_Launch_Communication_Kit.md`](../16_Change_Management_and_Comms/CM-005_Wave_Launch_Communication_Kit.md) | `O-05` there — the kit has no layout authority until this category exists |
| [`EO-012_Co_Marketing_and_Co_Branding_Asset_Guide.md`](../18_Ecosystem_Onboarding_Content/EO-012_Co_Marketing_and_Co_Branding_Asset_Guide.md) | §4.12; partner asset supply and the identity gap |
| [`MM-012_Digital_Asset_Management_and_Naming_Standard.md`](MM-012_Digital_Asset_Management_and_Naming_Standard.md) | Naming, versioning, rights records and retirement |
| `04-00` `PS-04`…`PS-08`, §P02 | Accessibility, responsiveness, offline and the device floor |
| `05-06` §9, §11 | Locale standards, printer verification, accessibility test cadence |

| Depended on by |
|---|
| `MM-002` … `MM-011` · every media purchase order · `TR-003` storyboards · `HC-020` productions · the Design System asset pipeline · `TS-016` accessibility execution |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **Per wave** while assets are in production; annually thereafter |
| Trigger for out-of-cycle review | A new device or printer model in the qualification matrix · a browser or email-client format-support change · a `CB-001` or identity revision · an accessibility finding · a rejected delivery whose defect this file did not prohibit |
| Owner | **Brand Lead**, with Platform Engineering for the pipeline and Content Design for the accessibility deliverables |
| Approver | Content Design Lead (`CG-002` §5.4, class D) |
| Change control | A change to §4.2 is **MAJOR** and re-opens every open media purchase order (`AS-21`); a change to §4.7 re-opens the accessibility line items |
| Effectiveness measure | **Deliveries rejected at first acceptance**, and the rule identifier each was rejected against. A rule that never rejects anything is either perfect or unenforced |
| Change log | [`RF-006`](../99_Reference_and_Registers/RF-006_Content_Decision_Log_and_Change_Control.md) — **written; Category 99 completed 2026-08-18**. Every decision under this file is logged there |

---

## 7. Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **No file in this content set holds the 1000FiX master identity** — logo construction, clear space, minimum size, colour system, misuse, lock-ups. `AUDIT-018` `EO-13` found it and `R-13` asks for a decision: **register a new file in the `VB` category**, whose identifier is allocated by the Programme Content Lead from the `VB` growth range under `CG-005` `ID-04` — **this file does not name a number, because content cites identifiers and never allocates them** (`ID-07`) — **or** adopt `CB-001` from the corporate-website set by reference, accepting its separate approval authority. **§4.12 declines to make `MM-001` the silent home.** `EO-012` `CB-03` is unenforceable until this lands | **Brand Lead** with Programme Content Lead | **W1 — and before a mark is issued to any partner (`R-13` says W7; the earlier date governs)** |
| **O-02** | **Template 17 `TPL_Asset_Specification.md` does not exist.** `CG-009` §6 proposes it at P3 and recommends adding it *"before their categories are authored"*. All 12 `MM` files therefore use template 1 with a declared adaptation. **This is the sixth category to do so**, after `KB`, `TR`, `HC`, `TS` and `EO` (`AUDIT-018` `EO-06`) | Content Design | **W2 — `AUDIT-018` R-06 is already the fifth request** |
| **O-03** | **`TS-002` sandbox does not exist**, and `AS-09` prohibits production capture with no alternative source. This blocks class A1 entirely and any A7/A8 screen recording. Recorded independently by `HC-002` `O-02`, `TR-003` `O-01` and `HC-020` `O-04` | Test Lead with Content Design | **W1 — blocks every screenshot in the programme** |
| **O-04** | **No media production budget exists.** `HC-020` `O-02` records 44 customer productions unbudgeted; `MM-006` adds the training series; `MM-009` adds photography; `MM-008` adds animation. **The Master Index §7 estimate of 45–70 person-days for Category 19 is explicitly *"specification only; production cost is separate"* — and the separate cost appears in no plan** | Content Design Lead with Finance | **W1 — it is a budget question, not a content one** |
| **O-05** | **`RF-006` Content Decision Log now exists** — Category 99 was authored concurrently with Category 19 and completed 2026-08-18, so the obligation changes shape rather than disappearing. `AS-23` requires **every format decision, ceiling waiver and accepted deviation under this standard to be written into [`RF-006`](../99_Reference_and_Registers/RF-006_Content_Decision_Log_and_Change_Control.md)**, and **none has been.** `AUDIT-017` `OP-12` recorded ninety-four open decisions against a log that did not exist; the log exists now and **the backlog of `MM` decisions must be entered into it, not assumed to have been** | Programme Content Lead with Brand Lead | **W1 — a read-across, no longer a gap** |
| **O-06** | **No accessibility reviewer is named**, and §4.11 makes accessibility deliverables a blocking acceptance gate with no owner to operate it. This is the **fourth** file to record the same gap, after `TR-003` `O-02`, `HC-002` `O-04` and `HC-016` `O-04` | Content Design Lead | **W1** |
| **O-07** | **The device and client qualification matrix (§4.11) has no owned test set.** `VB-004` §14 assigns a printer test set to Platform Engineering and records it as outstanding; `VB-005` §14 does the same for email clients. **Neither exists, and this file adds a video-on-throttled-connection case to both** | Platform Engineering | **W1 — before the first acceptance** |
| **O-08** | **The AVIF and WebP support figures in §4.4 carry `class: P3`.** `CG-012` `EV-02` permits P3 for context but not as the sole basis of a capability claim, and `RA-01` is a capability claim about the delivery chain. It converts to P1 on completion of `O-07`'s qualification matrix — **the same shape as `VB-005`'s email-client evidence, which is also still P3** | Platform Engineering with Brand | **W2 — before the pipeline is built** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md` — all six sections in order; the `CG-009` `MM` addition placed at §4.2 and the placement justified; §7 added per category convention
- [x] **Eleven asset classes defined, each mapped to its governing brief and its consuming surface**
- [x] **Deliverable specification table states format, dimensions, colour, compression, metadata and naming for every class** — the `CG-009` §3 requirement
- [x] Colour management carries the `VB-003` §3 contrast finding into asset production, not only into UI
- [x] Raster and video formats chosen against the device floor `04-00` §P02 sets, with the evidence class stated honestly
- [x] **Encoding ladder designed for the congested-cell case, not the national average speed**
- [x] **Accessibility deliverables stated as blocking acceptance criteria with their WCAG success criteria** — the `CG-011` §9 obligation
- [x] Captions required as separate authored timed text, not burned in and not auto-generated
- [x] Bilingual asset cost stated per language, with the 22-to-44 consequence carried from `HC-020`
- [x] IPTC Core + Extension metadata set specified per class, with location and device metadata stripped
- [x] **Rights assignment required in writing, with the Bangladesh default ownership position and surviving moral rights stated**
- [x] Acceptance and rejection made a rule-identified procedure a supplier can be held to
- [x] **The master-identity gap declared rather than silently absorbed (`AUDIT-018` `EO-13` / `R-13`)**
- [x] `CP-01` boundaries stated against `MM-002`…`MM-012`, `VB-003`…`VB-009`, `DT-001`, `DT-044`, `RP-007`, `RP-014`, `CG-010`
- [x] All internal links resolve
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [x] English-only per `CG-010` §3.2, and the outputs-are-bilingual position recorded against `AUDIT-017` `OP-13`
- [ ] **`O-01` master identity unowned — outstanding; `EO-012` `CB-03` unenforceable**
- [ ] **`O-03` `TS-002` sandbox absent — outstanding; class A1 cannot be produced**
- [ ] **`O-04` production budget absent — outstanding**
- [ ] **`O-07` qualification test set absent — outstanding; acceptance cannot be executed**
- [ ] Named approver recorded — **pending Content Design Lead**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
