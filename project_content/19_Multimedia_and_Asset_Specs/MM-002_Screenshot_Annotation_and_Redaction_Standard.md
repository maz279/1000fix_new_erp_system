---
id: MM-002
title: Screenshot, Annotation and Redaction Standard
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Content Design with Security
author: Content Design with Security, Localisation and Platform Engineering
reviewers: [Content Design Lead, Chief Data Officer, Chief Information Security Officer delegate, Localisation Lead, Accessibility reviewer, Knowledge Manager, Learning & Development Lead, Programme Content Lead]
approver: Content Design Lead with Security
content_class: D
purpose: >
  The capture, annotation, redaction and currency rules for every screenshot in the programme.
  Help, training, knowledge, release notes and onboarding kits will together contain many hundreds
  of screen images across twelve portals and nine waves of UI change, and every one of them is
  taken from a system that holds National ID numbers, bank accounts, customer addresses, employee
  salaries and marketplace seller KYC documents. A screenshot standard in this programme is a
  data-protection control before it is a style guide: an unredacted capture published in a help
  article is a disclosure of restricted personal data to every reader of that article, and it is
  not retractable once indexed.
traces_to: [CG-003, CG-008, CG-010, CG-011, CG-012, CG-013, VB-003, VB-007, VB-008, VB-009, UI-002, UI-003, UI-010, HC-002, HC-016, HC-020, TR-003, TR-022, TR-024, KB-002, BN-003, BN-006, BN-016, TS-002, TS-016, AP-012, LG-008, LG-009, LG-020, MD-027, MM-001, MM-003, MM-004, MM-012, OP-006, 04-00 PS-03, 04-00 PS-04, 04-00 §P03, 05-02 §10, 05-04 §4, 05-06 NFR-073, 05-06 NFR-086]
priority: P1
wave: W1
bilingual: no
bn_counterpart: n/a
sources:
  - source: project_content/00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md §4.2 AT-08 — "Screenshots use sample data with personal data redacted (MM-002, CG-008 U-41)"; AT-02 alt text does not begin "Screenshot of"; AT-03 under 125 characters; AT-05 bilingual alt text
    verified: 2026-08-18
    class: P1
  - source: project_content/09_Help_Centre_and_Self_Service/HC-002_Help_Article_Template_and_Style_Rules.md §4.6 HS-17…HS-22 — teach the task not the screen; maximum one screenshot per article; sandbox only; registered against the release; alt text in both languages; three screenshots means it is a video or too complex a task
    verified: 2026-08-18
    class: P1
  - source: project_content/08_Training_and_Enablement/08A_Framework/TR-003_Course_Design_Standard_and_Storyboard_Template.md §4.6 DS-12…DS-16 — the nine-wave maintenance trap; maximum one screenshot per segment; captured from the sandbox; registered against the release; UI labels quoted from UI-002/UI-003 rather than transcribed from pixels
    verified: 2026-08-18
    class: P1
  - source: project_content/15_Integration_and_Developer_Content/AP-012_Data_Sharing_and_Field_Level_Disclosure_Register.md §4.5.6 — claim-evidence photographs "must not contain a person or an identifying document — MM-002 redaction standard"; the register records itself as depending on this file
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02 §10 data classification S0–S3 and the S3 field inventory; 05-04 §4 restricted tier T5 with allow-list access, step-up authentication and logged access
    verified: 2026-08-18
    class: P1
  - source: project_content/10_Legal_Policy_and_Compliance/LG-008_Privacy_Notice_and_Consent_Copy.md §4.2 P-01…P-20 processing inventory and the residency-restricted field set; PI-05 bulk export of personal data requires approval and is logged
    verified: 2026-08-18
    class: P1
  - source: project_content/11_Localisation_Bengali/BN-016_Bengali_Help_and_Training_Content_Plan.md HC-B05 — "Screenshots are language-specific. A Bengali article showing an English screenshot teaches the wrong screen (MM-002)"
    verified: 2026-08-18
    class: P1
  - source: W3C Web Content Accessibility Guidelines (WCAG) 2.1 — SC 1.1.1 non-text content, SC 1.4.5 images of text (Level AA), SC 1.4.1 use of colour
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2027-02-18
---

# Screenshot, Annotation and Redaction Standard

| Item | Value |
|---|---|
| Governs | Every screen image published in help, training, knowledge, release notes, onboarding kits, developer content and internal documentation |
| Applies to | All twelve portals and the fourteen `P03` workspaces |
| Audience | Content designers, instructional designers, knowledge authors, technical writers, external vendors |
| Language | **English** — the standard. **The screenshots it governs are language-specific** (`SC-22`) |
| Wave | W1 · Months 1–4 (`06-01` §3) |
| Content class | **D** — user-facing (`CG-002` §4.1) |
| Priority | **`P1` — the only `P1` in Category 19**, and the reason is in §1 |
| Joint owner | **Content Design with Security.** No other file in this category has a second owner |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3). All
> six sections retained in order. The `CG-009` `MM` addition — the **deliverable specification
> table** — is **§4.9**. §7 Open Items is added per the category convention established by
> `HC-002`, `TR-003` and `HC-016`.

---

## 1. Purpose

### 1.1 Why this file is `P1` and the other eleven are not

Five files in three other categories delegate a **personal-data control** to this one, by
identifier, and one of them is a data-disclosure register:

| Delegating file | What it delegates | Where |
|---|---|---|
| [`CG-011`](../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md) | *"Screenshots use sample data with personal data redacted"* | `AT-08` |
| [`CG-008`](../00_Content_Governance_and_Standards/CG-008_Content_Definition_of_Done_and_QA_Checklist.md) | The Definition-of-Done item every file is checked against | `U-41`, `HC-c` |
| [`HC-002`](../09_Help_Centre_and_Self_Service/HC-002_Help_Article_Template_and_Style_Rules.md) | Sandbox-only capture; sample data; redaction; bilingual alt text | `HS-19`, `HS-21` |
| [`UI-010`](../03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-010_Accessibility_Text_Library.md) | *"Screenshots use sample data, redacted"* | `A-07` |
| [`AP-012`](../15_Integration_and_Developer_Content/AP-012_Data_Sharing_and_Field_Level_Disclosure_Register.md) | **Claim-evidence photographs "must not contain a person or an identifying document"** | §4.5.6 |
| [`TPL_Help_Article.md`](../_templates/TPL_Help_Article.md) | The instruction every help author reads | Template body |

**The system these images are taken from holds `S3` restricted data**: National ID and passport
numbers, TIN, biometric attendance templates, bank account details, recovered customer data,
marketplace seller KYC documents and criminal-record checks (`05-02` §10, `05-06` §6.4). Access
to those fields is tier `T5` — allow-list, step-up authenticated and **logged on every access**
(`05-04` §4).

> **A screenshot defeats every one of those controls at once.** It is an unlogged, unauthenticated,
> permanent, freely copyable extract of a `T5` field, published to an audience of 250,000+
> customers a month or 500–2,000 marketplace sellers. `LG-008` `PI-05` requires bulk export of
> personal data to be approved and logged; **a screenshot in a help article is an export that is
> neither.**

**Consequence of absence (`CP-03`).** Without this standard, hundreds of screen images are
captured by several authors and vendors from whatever environment they can log into — which, until
`TS-002` exists, is production. Each one is a potential disclosure under the Personal Data
Protection Act 2026, whose enforcement mechanisms activate around **13 May 2027**, inside Wave 4
(`LG-008` §8). The exposure `05-06` §6.3 records is **BDT 25 lakh, rising to BDT 50 lakh for a
significant data fiduciary**.

### 1.2 The second failure this file prevents

The first is disclosure. The second is decay.

| Without the standard | By W5 |
|---|---|
| Screenshots used freely | Most help articles and course segments show a UI that no longer exists |
| Captured at whatever size the author's screen was | Illegible on the branch hardware baseline, or 4 MB each |
| Labels transcribed from pixels rather than quoted from `UI-002`/`UI-003` | A label change is a hunt through fifteen help sets instead of a find-and-replace |
| No release registered against the capture | Nobody can tell which images a release orphaned |
| Bengali articles carrying English screenshots | The Bengali reader is taught the wrong screen (`BN-016` `HC-B05`) |

`HC-002` `HS-17`…`HS-22` and `TR-003` `DS-12`…`DS-16` already contain this decay from the
**consuming** side. **This file contains it from the production side**, and the two are written to
age at the same rate deliberately.

---

## 2. Scope

**In scope.** The capture environment and its prohibition; capture geometry, density, chrome,
theme and language; the sample-data contract; the redaction obligation, method and verification;
annotation style; alt text and long descriptions; Bengali screenshot rules; release registration
and currency; the deliverable specification; and rules `SC-01`…`SC-30`.

**Out of scope.**

| Subject | Owned by |
|---|---|
| Whether an article or segment should contain a screenshot at all | [`HC-002`](../09_Help_Centre_and_Self_Service/HC-002_Help_Article_Template_and_Style_Rules.md) `HS-17`, `HS-18`, `HS-22` · [`TR-003`](../08_Training_and_Enablement/08A_Framework/TR-003_Course_Design_Standard_and_Storyboard_Template.md) `DS-12`, `DS-13` |
| The sandbox, its personas and its data | [`TS-002`](../13_Test_and_Acceptance_Content/TS-002_Test_Data_Pack_and_Persona_Set.md) |
| The UI labels a screenshot shows | [`UI-002`](../03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-002_Global_Navigation_and_Label_Register.md), [`UI-003`](../03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-003_Field_Label_Placeholder_and_Help_Text_Library.md) — **quoted, never transcribed** |
| The alt-text strings themselves | [`UI-010`](../03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-010_Accessibility_Text_Library.md), and the consuming `HC-`/`TR-` file (`CG-011` `AT-01`) |
| Which data is `S3` / residency-restricted | `05-02` §10 · [`LG-008`](../10_Legal_Policy_and_Compliance/LG-008_Privacy_Notice_and_Consent_Copy.md) §4.2 · [`AP-012`](../15_Integration_and_Developer_Content/AP-012_Data_Sharing_and_Field_Level_Disclosure_Register.md) |
| File format, colour and delivery mechanics | [`MM-001`](MM-001_Multimedia_Asset_Standard_and_Delivery_Specification.md) §4.2 class A1 |
| Diagrams drawn from a screen rather than captured | [`MM-003`](MM-003_Diagram_and_Process_Map_Visual_Standard.md) |
| Repository naming, versioning and retirement | [`MM-012`](MM-012_Digital_Asset_Management_and_Naming_Standard.md) |
| Watermarking and confidentiality marking on exported reports | [`RP-014`](../14_Reporting_Analytics_and_KPI/RP-014_Export_Watermark_and_Confidentiality_Marking_Rules.md) |
| **Photographs of devices, premises or people** | [`MM-009`](MM-009_Photography_Brief_Branches_Workshop_and_Field.md) — **except the redaction obligation in §4.4, which this file owns for both** |

> **`CP-01` note on the `MM-009` split.** `AP-012` §4.5.6 delegates *photograph* redaction to this
> file, not to `MM-009`. That is correct and is preserved: **§4.4 is the single redaction standard
> for any captured or photographed image in the programme**, and `MM-009` cites it rather than
> restating it. Splitting redaction across two files is exactly the drift `CP-01` exists to
> prevent, and in this case it would be a compliance drift.

---

## 3. Audience

| Reader | Uses it for | Reads it |
|---|---|---|
| **Content designer authoring help** | What may be captured, from where, and what must be removed | Before the first capture |
| **Instructional designer** | The one-screenshot-per-segment discipline and the release registration | Per storyboard |
| **Knowledge author (senior technician, `R12`/`R13`)** | Capturing a diagnostic screen without capturing a customer | Per article |
| **External documentation vendor** | The clause in their contract that makes an unredacted capture a breach | Before starting |
| **Security / the Chief Data Officer function** | The control this file is, and its verification points | At review, and after any incident |
| **Localisation Lead** | Why the Bengali set doubles the screenshot count | At planning |
| **Accessibility reviewer** | Alt text, long description and the images-of-text position | At gate |
| **Release manager** | Which images a release has orphaned | Per release |

---

## 4. Content

### 4.1 Capture environment — the first and hardest rule

| # | Rule |
|---|---|
| **SC-01** | **Screenshots are captured from the sandbox. Never from production. No exception, no waiver.** A production screenshot contains customer-identifiable content by definition (`TR-003` `DS-14`, `HC-002` `HS-19`) |
| **SC-02** | The sandbox is [`TS-002`](../13_Test_and_Acceptance_Content/TS-002_Test_Data_Pack_and_Persona_Set.md) and its persona set. **It does not yet exist** — `O-01` |
| **SC-03** | **A demonstration or training tenant seeded from a production copy is production.** Masking applied after the fact is not a sandbox; `BRU-SEC-08` requires masking in non-production and that is a system control, not a capture control |
| **SC-04** | The capturing account is a **purpose-created documentation account** with the role being documented — never a personal account, never an elevated one. The account name appears in the chrome and is itself content |
| **SC-05** | **Capture is done on the surface's own target device class**, not on a designer's monitor: `1366 × 768` for `P03` workspaces (`04-00` §P03), a mid-range Android for `P02`/`P09`, a phone for `P01` |
| **SC-06** | **No capture from a screen-sharing session, a recorded call, a customer's device, or a photograph of a monitor.** Each carries content the capturer did not choose |
| **SC-07** | Where a screen genuinely cannot be reproduced in sandbox — a live integration response, a rare error — **the screen is described in words or drawn as a diagram (`MM-003`), not captured**. `HC-002` `HS-17` already prefers the description |

> **`SC-01` has no waiver clause and that is deliberate.** `CG-008` `WV-03` makes the
> machine-translation prohibition unwaivable for the same class of reason. A waiver process for
> production capture would be used under deadline pressure, by the author least able to judge what
> is in frame.

### 4.2 Capture geometry

Captured at **2× the target CSS pixel size** so the image survives a retina display and a print
render without resampling (`MM-001` §4.2 class A1).

| Surface | Logical viewport | Capture at 2× | Notes |
|---|---|---|---|
| **`P03` workspaces and desktop portals** | **1366 × 768** | 2732 × 1536 | The branch hardware baseline (`04-00` §P03). **Not 1920 — a screenshot taken at 1920 shows a layout most users never see** |
| `P03` usable work area | 1366 × 600 | 2732 × 1200 | After browser and OS chrome (`VB-003` §5.1) |
| `P01` / `P07` / `P12` web | 1280 × 800 | 2560 × 1600 | |
| **`P01` mobile app** | 390 × 844 | 780 × 1688 | |
| **`P02` / `P09` technician and rider** | **360 × 800** | 720 × 1600 | The mid-range Android class (`04-00` §P02) |
| `P11` auditor, offline | 360 × 800 | 720 × 1600 | |
| Cropped detail | Any | 2× | See `SC-10` |

| # | Rule |
|---|---|
| **SC-08** | **Browser chrome is excluded.** The URL bar, tabs, bookmarks, extensions and the operating-system taskbar are the author's environment, not the product's — and they leak the author's identity, tenancy and installed software |
| **SC-09** | Application chrome — the product header, workspace switcher, breadcrumb — is **included only where the article or segment refers to it**. `VB-003` `D-02` caps that chrome at 96 px vertical, and it consumes the same share of a screenshot |
| **SC-10** | **Crop to the smallest region that carries the point**, then show it at full size. A full-screen capture reduced to fit an article column is illegible on a phone and is the most common screenshot defect |
| **SC-11** | Where a crop needs context, use a **crop with a full-screen inset**, not a full screen with a small highlight |
| **SC-12** | The **light theme is the default** for all published screenshots. A dark-theme capture is produced only where the article is about the theme |
| **SC-13** | The captured state is a **realistic populated state**, never an empty list — unless the subject *is* the empty state, in which case it comes from [`UI-006`](../03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-006_Empty_State_and_First_Run_Copy_Library.md) and its artwork from [`MM-005`](MM-005_Illustration_and_Empty_State_Artwork_Brief.md) |
| **SC-14** | **No cursor, no tooltip mid-hover, no focus ring on an unrelated control, no browser autofill dropdown, no notification toast from another task.** Each of these is a transient state that reads as part of the interface |
| **SC-15** | The clock, date and any relative timestamp visible in the capture are **from the sandbox's fixed reference date** (`TS-002`), so a screenshot does not silently date itself |

### 4.3 The sample-data contract

| # | Rule |
|---|---|
| **SC-16** | **All visible data is `TS-002` sample data.** Not anonymised production data, not "made-up-looking" production data, not a colleague's real record |
| **SC-17** | **Sample data is not invented at capture time.** An author who invents a customer name invents a name that will differ from every other article's, and will eventually collide with a real one. The persona set is the source (`TS-002`) |
| **SC-18** | Sample identifiers follow the real masks so they are recognisable and testable — `SR-2026-114882` for a service order (`MD-040`), a valid-format **13-digit e-BIN**, a valid-format NID and TIN — **but every value is reserved sample data that resolves to nothing** |
| **SC-19** | **Sample phone numbers, emails and addresses are from a reserved, non-routable set.** A plausible Bangladeshi mobile number printed in a help article read by 250,000 customers a month is a number that will be called |
| **SC-20** | Money values are plausible and consistent across the article set. A repair quoted at BDT 3,200 in one article and BDT 32,000 in the next teaches nothing and invites a pricing complaint |
| **SC-21** | **Sample data is bilingual.** A Bengali screenshot showing English customer names is not a Bengali screenshot (`BN-016`, `TS-002`) |
| **SC-22** | **Screenshots are language-specific** (`BN-016` `HC-B05`). A Bengali article shows the Bengali interface. **This doubles the capture count for every bilingual surface** and the count is stated in §4.10 rather than discovered |

### 4.4 Redaction — the control

**This section is the control `CG-011` `AT-08`, `CG-008` `U-41`, `UI-010` `A-07` and `AP-012`
§4.5.6 all delegate here.** It applies to screenshots **and to photographs** (`MM-009` cites it).

#### 4.4.1 What must never appear

| Category | Examples | Class | Action |
|---|---|:--:|---|
| **Government identifiers** | National ID, passport, TIN, e-BIN of a natural person, driving licence | **S3 / T5** | **Never in frame.** Not redacted — **not captured** |
| **Biometric data** | Attendance template, fingerprint, face-match capture | **S3 / T5** | **Never in frame** |
| **Financial instruments** | Bank account number, card number, cheque, bKash/Nagad wallet number, payout destination | **S3** | **Never in frame** |
| **Recovered customer data** | Any content from a data-recovery case | **S3, dual-control** | **Never in frame** (`BRU-DTS-14`, `BRU-DTS-16`) |
| **Marketplace seller KYC** | Uploaded licence, NID image, criminal-record check | **S3 / T5** | **Never in frame** (`BRU-MKP-19`) |
| **Employee personal data** | Salary, payslip figures, disciplinary record, home address, next of kin | **S3** | **Never in frame** |
| Customer contact detail | Name, mobile, email, full address | S2 | Sample data only |
| Device identity tied to a person | IMEI, serial where paired with an owner | S2 | Sample data only |
| **Third-party material in frame** | A brand partner's portal, a competitor's system, a supplier price list, a customer's own screen | Varies | **Never in frame** |
| **The capturing person's identity** | Account name, avatar, email in the header, session identifier | S1 | Documentation account only (`SC-04`) |
| Internal endpoints and infrastructure | Hostnames, internal URLs, ticket IDs, stack traces, debug panels | S1 | Removed |

> **The rule the table is built on — `SC-23`: restricted data is not redacted, it is not
> captured.** Redaction is the second line of defence, for the thing that got into frame anyway.
> **A workflow that relies on redacting an NID has already put an NID into an image file on
> somebody's laptop**, and that file is the disclosure, not the published article.

#### 4.4.2 How redaction is done

| # | Rule |
|---|---|
| **SC-24** | **Redaction is destructive and applied to the pixels.** The image is flattened and re-encoded from the redacted raster. **A shape drawn over a layer, a PDF annotation, a CSS overlay or a "black box" in an editable file is not redaction** — the content is still in the file and is recovered by anyone who opens it |
| **SC-25** | **Blur and pixelation are prohibited.** Both are reversible in principle and unreliable in practice, particularly on short numeric strings, which is precisely what is being hidden. **Solid fill only** |
| **SC-26** | The redaction fill is a **flat neutral block with a visible label** — `Sample`, `Redacted`, or the field name — so the reader knows something was removed and does not read the block as an interface element |
| **SC-27** | **The source capture containing the unredacted content is destroyed, not archived.** It is not an asset, it is an incident waiting for a backup restore. `MM-012` §4.7 must never receive it |
| **SC-28** | **Metadata is stripped before publication** — every screenshot carries capture software, machine name, user name, and on mobile captures a device identifier. Stripped, then re-stamped from the `MM-012` record (`MM-001` `MT-05`) |
| **SC-29** | **Redaction is verified by a second person against §4.4.1, and the verification is recorded.** `CO-04` makes the approver never the author; the same principle applies to the control that matters most in this file |
| **SC-30** | **An unredacted publication is a data incident, not a documentation defect.** It is raised under [`OP-004`](../17_Operations_Support_and_Runbooks/OP-004_Incident_Communication_Template_Set.md) and [`CG-013`](../00_Content_Governance_and_Standards/CG-013_Content_Risk_and_Legal_Escalation_Rules.md), assessed for breach notification under `LG-008` §4.8, and the asset is withdrawn from every surface **including caches and search indexes** before the correction is published |

#### 4.4.3 The photograph case — `AP-012` §4.5.6

`AP-012` classifies claim-evidence photographs `S1` and states they **"must not contain a person
or an identifying document"**, delegating the standard here. Applied:

| In frame | Position |
|---|---|
| A person — customer, technician, bystander, reflection in a screen or a polished surface | **Not permitted.** Reflection is the case authors miss |
| An identifying document — invoice, NID, warranty card, delivery note with an address | **Not permitted** |
| A second device's serial or asset tag | **Not permitted** — `AP-012` names this leak path |
| A screen showing another customer's record | **Not permitted** |
| Premises signage identifying a customer's home or business | **Not permitted** in claim evidence; permitted in commissioned photography under `MM-009` §4.2 with consent |
| The device under repair, its fault, its serial | **Required** — this is the evidence |

> **Why the same standard covers both.** A technician photographing a cracked screen and an author
> capturing a workspace are performing the same act — freezing whatever was in front of them into
> a file that will be sent somewhere. The failure modes are identical and the rules should not be
> two sets that drift apart.

### 4.5 Annotation

| Element | Specification |
|---|---|
| **Callout numbers** | Filled circle, **24 px at 1×**, white numeral on `#1E5F8A` (6.86:1). Numbered in reading order, never in narrative order |
| **Highlight box** | **2 px** stroke, `#1E5F8A`, square corners, no fill, no shadow |
| **Arrow** | Straight only, 2 px, solid head. **No curved or hand-drawn arrows** |
| **Dimming** | Permitted at **40% black** over the non-relevant region, only where a highlight box is insufficient |
| **Redaction block** | Flat `#495057` with a `Sample` / `Redacted` label at ≥ 12 px |
| **Text in the image** | **Prohibited** — see `SC-33` |

| # | Rule |
|---|---|
| **SC-31** | **Annotation colour is never the only signal** (`CG-011` `CL-01`, WCAG SC 1.4.1). A callout is a **numbered** circle, and the number is what the prose refers to — not "the item in the blue box" |
| **SC-32** | **`#39B1DF` is never used for annotation.** It measures 2.46:1 on white and fails the SC 1.4.11 3:1 non-text threshold, so a brand-blue highlight box on a light interface is an accessibility failure (`VB-003` `BC-01`) |
| **SC-33** | **No text is baked into a screenshot** — WCAG SC 1.4.5, `CG-011` `AT-07`. Labels, captions and step text live in the article, keyed to callout numbers. Text in an image cannot be translated, searched, resized, read aloud or corrected |
| **SC-34** | **Maximum five callouts per image.** More than five is two images, or a task that `HC-002` `HS-22` says should be simplified in the product |
| **SC-35** | Annotation never obscures a label, a value or a state the reader must see |
| **SC-36** | Annotation is applied on a **separate layer in the source file** so it can be moved when the UI moves, and so a translated variant does not require re-annotation |
| **SC-37** | **No decorative annotation.** No drop shadows, no browser mock-ups, no device frames, no perspective. A device frame adds 40% weight and no information |

### 4.6 Alt text and long description

Authored in the **consuming content file**, not by the capturer (`CG-011` `AT-01`) — but specified
here so the capturer delivers what the author needs.

| # | Rule |
|---|---|
| **SC-38** | Every screenshot carries alt text **in both languages** where its surface is bilingual (`HC-002` `HS-21`, `CG-011` `AT-05`) |
| **SC-39** | Alt text describes **what the reader should see and where**, in `CG-004` approved terms — not what the picture contains. *"The estimate approval panel, with Approve and Request change buttons below the parts list"* |
| **SC-40** | Alt text **never begins "Screenshot of", "Image of" or "Picture of"** (`CG-011` `AT-02`) and stays **under 125 characters** (`AT-03`) |
| **SC-41** | Where the screenshot carries a procedure or a value set, a **long description** carries it as text — the image is never the only carrier (`CG-011` `AT-06`) |
| **SC-42** | The alt text is also **what the help search index reads** (`HC-002` `HS-21`), so it uses the words a reader would search for |

### 4.7 Currency — surviving nine waves

| # | Rule |
|---|---|
| **SC-43** | **Every screenshot is registered against the release it was captured from** (`HC-002` `HS-20`, `TR-003` `DS-15`), in the `MM-012` record. An unregistered screenshot cannot be found when its screen changes |
| **SC-44** | A release that changes a screen **lists the screenshots it orphans**, produced by querying the register — not by memory. This is a [`TR-024`](../08_Training_and_Enablement/08B_Course_Packs/TR-024_Release_Training_and_Refresher_Standard.md) `RL-04` and [`OP-006`](../17_Operations_Support_and_Runbooks/OP-006_Release_Notes_Standard_and_Wave_Note_Set.md) release-note obligation |
| **SC-45** | **An orphaned screenshot is removed or replaced. It is not left.** An image of a screen that no longer exists is worse than no image: it teaches a reader to look for something that is not there, and it destroys trust in the rest of the article |
| **SC-46** | **UI labels quoted in prose come from `UI-002`/`UI-003`, never transcribed from a screenshot's pixels** (`HC-002` `HS-08`, `TR-003` `DS-16`). This is what makes a label change a find-and-replace instead of a re-capture |
| **SC-47** | The screenshot count per article and per segment is capped by the consuming standard — **one per help article** (`HS-18`), **one per training segment** (`DS-13`) — and this file does not relax either |

### 4.8 Bengali screenshots

| # | Rule |
|---|---|
| **SC-48** | Bengali screenshots are **captured from the Bengali interface** with Bengali sample data. They are not English captures with Bengali labels overlaid |
| **SC-49** | The Bengali capture is **visually inspected for conjunct rendering** against the `VB-009` §7.1 test string before publication. A screenshot is a permanent record of a rendering defect |
| **SC-50** | Bengali interface text in a capture must meet the `VB-009` §3 floors **in the published image at its display size**, not at capture size. A 2× capture displayed at 50% halves the effective type size |
| **SC-51** | **The Bengali set is planned and costed, not produced opportunistically.** `SC-22` doubles the count; §4.10 states the arithmetic |

### 4.9 Deliverable specification

**The `CG-009` §3 required addition for Category 19.** A capture is accepted against this table.

| Attribute | Specification |
|---|---|
| **Master format** | **PNG-24, lossless, sRGB profile embedded** (`MM-001` §4.2 class A1) |
| **Derived formats** | AVIF + WebP + PNG, generated by the platform pipeline — **not by the author** |
| **Dimensions** | 2× the §4.2 logical viewport for the surface; cropped per `SC-10` |
| **Colour** | sRGB IEC 61966-2.1, embedded. Light theme (`SC-12`) |
| **Compression** | Master lossless. Derived **≤ 150 KB at 1×**; an article's total image weight is bounded by the `HC-002` §4.9 page-weight budget |
| **Annotation layer** | Delivered **separately and editable** (`SC-36`) |
| **Redaction** | Applied destructively, verified by a second person, verification recorded (`SC-24`, `SC-29`) |
| **Metadata** | Stripped, then re-stamped: `dc:title`, `dc:description`, `dc:relation` = owning content ID, capture release, surface, language, capture date (`MM-001` §4.9) |
| **Naming** | `MM-012` §4.3 — carries the owning content ID, the surface, the language and the release |
| **Alt text** | Supplied **by the consuming file**; the capture is not published without it |
| **Register entry** | `MM-012` record created **before** publication, carrying the release (`SC-43`) |
| **Source capture** | **Destroyed if it contained unredacted restricted data** (`SC-27`); otherwise retained with the asset |

### 4.10 The volume this creates, stated rather than discovered

**Counted from the consuming standards, not estimated.**

| Consumer | Cap | Files | Screenshots (EN) | Bilingual? | Total captures |
|---|---|---:|---:|---|---:|
| Help articles | 1 per article (`HS-18`) | 15 help sets | Bounded by article count | **18 of 20 `HC` files bilingual** | ×2 for bilingual sets |
| Training segments | 1 per segment (`DS-13`) | 20 course packs | 3–6 segments per module | **20 of 24 `TR` files bilingual** | ×2 |
| Knowledge articles | Per `KB-002` | 16 `KB` files | — | 13 of 16 bilingual | ×2 |
| Release notes | Per release | 9 waves | — | Per `OP-006` | — |
| Onboarding kits | Per `EO` kit | 14 | — | 8 of 14 bilingual | ×2 |

| # | Rule |
|---|---|
| **SC-52** | **The screenshot inventory is enumerated per wave and reported**, not estimated. `CP-11` applies to this count as to every other |
| **SC-53** | **Bengali capture is a separate line of effort with its own owner.** It is the item most likely to be dropped under schedule pressure, and dropping it produces exactly the failure `BN-016` `HC-B05` names |

> **The honest position on volume.** The register's Category 19 estimate is **45–70 person-days for
> specification only**; the Master Index states production cost is separate. **Capture, redaction,
> second-person verification, annotation, registration and per-release re-capture across two
> languages is a recurring operational load for the life of the product, and it appears in no
> plan.** See `O-05`.

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| [`TS-002_Test_Data_Pack_and_Persona_Set.md`](../13_Test_and_Acceptance_Content/TS-002_Test_Data_Pack_and_Persona_Set.md) | The only lawful capture source (`SC-01`, `SC-02`) — **does not exist** |
| [`CG-011_Accessibility_Content_Standard.md`](../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md) | `AT-01`…`AT-08`; the obligation this file discharges |
| [`CG-008_Content_Definition_of_Done_and_QA_Checklist.md`](../00_Content_Governance_and_Standards/CG-008_Content_Definition_of_Done_and_QA_Checklist.md) | `U-41` and `HC-c` make conformance a Definition-of-Done item |
| [`CG-013_Content_Risk_and_Legal_Escalation_Rules.md`](../00_Content_Governance_and_Standards/CG-013_Content_Risk_and_Legal_Escalation_Rules.md) | The escalation route `SC-30` uses |
| [`HC-002_Help_Article_Template_and_Style_Rules.md`](../09_Help_Centre_and_Self_Service/HC-002_Help_Article_Template_and_Style_Rules.md) | `HS-17`…`HS-22`; the consuming discipline this file supplies |
| [`TR-003_Course_Design_Standard_and_Storyboard_Template.md`](../08_Training_and_Enablement/08A_Framework/TR-003_Course_Design_Standard_and_Storyboard_Template.md) | `DS-12`…`DS-16`; the same discipline for training |
| [`TR-024_Release_Training_and_Refresher_Standard.md`](../08_Training_and_Enablement/08B_Course_Packs/TR-024_Release_Training_and_Refresher_Standard.md) | `RL-04` release-triggered review (`SC-44`) |
| [`UI-002_Global_Navigation_and_Label_Register.md`](../03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-002_Global_Navigation_and_Label_Register.md) · [`UI-003_Field_Label_Placeholder_and_Help_Text_Library.md`](../03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-003_Field_Label_Placeholder_and_Help_Text_Library.md) | The labels quoted rather than transcribed (`SC-46`) |
| [`UI-006_Empty_State_and_First_Run_Copy_Library.md`](../03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-006_Empty_State_and_First_Run_Copy_Library.md) · [`UI-010_Accessibility_Text_Library.md`](../03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-010_Accessibility_Text_Library.md) | Empty-state capture; `A-07` alt-text delegation |
| [`LG-008_Privacy_Notice_and_Consent_Copy.md`](../10_Legal_Policy_and_Compliance/LG-008_Privacy_Notice_and_Consent_Copy.md) | The processing inventory and residency-restricted fields §4.4.1 is built from; `PI-05`; §4.8 breach |
| [`LG-009_Data_Retention_and_Deletion_Schedule.md`](../10_Legal_Policy_and_Compliance/LG-009_Data_Retention_and_Deletion_Schedule.md) · [`LG-020_Acceptable_Use_and_Internal_Access_Policy.md`](../10_Legal_Policy_and_Compliance/LG-020_Acceptable_Use_and_Internal_Access_Policy.md) | Retention of captures; the internal-access position `SC-04` rests on |
| [`AP-012_Data_Sharing_and_Field_Level_Disclosure_Register.md`](../15_Integration_and_Developer_Content/AP-012_Data_Sharing_and_Field_Level_Disclosure_Register.md) | §4.5.6 photograph redaction delegated here (§4.4.3) |
| [`BN-016_Bengali_Help_and_Training_Content_Plan.md`](../11_Localisation_Bengali/BN-016_Bengali_Help_and_Training_Content_Plan.md) · [`BN-006_Bengali_Typography_Font_and_Numeral_Standard.md`](../11_Localisation_Bengali/BN-006_Bengali_Typography_Font_and_Numeral_Standard.md) | `HC-B05`; Bengali capture and rendering verification |
| [`VB-003_Brand_Application_in_Enterprise_UI.md`](../01_Voice_Brand_and_Design_Content/VB-003_Brand_Application_in_Enterprise_UI.md) · [`VB-009_Bengali_Typography_and_Brand_Standard.md`](../01_Voice_Brand_and_Design_Content/VB-009_Bengali_Typography_and_Brand_Standard.md) | The 1366×768 baseline, contrast constraints on annotation, Bengali floors |
| [`MM-001_Multimedia_Asset_Standard_and_Delivery_Specification.md`](MM-001_Multimedia_Asset_Standard_and_Delivery_Specification.md) | Class A1 format, colour, metadata, acceptance |
| [`MM-009_Photography_Brief_Branches_Workshop_and_Field.md`](MM-009_Photography_Brief_Branches_Workshop_and_Field.md) | Cites §4.4 as the single redaction standard |
| [`MM-012_Digital_Asset_Management_and_Naming_Standard.md`](MM-012_Digital_Asset_Management_and_Naming_Standard.md) | Naming, the release register, retirement of orphaned captures |
| [`OP-004_Incident_Communication_Template_Set.md`](../17_Operations_Support_and_Runbooks/OP-004_Incident_Communication_Template_Set.md) · [`OP-006_Release_Notes_Standard_and_Wave_Note_Set.md`](../17_Operations_Support_and_Runbooks/OP-006_Release_Notes_Standard_and_Wave_Note_Set.md) | `SC-30` incident route; `SC-44` release listing |
| [`TS-016_Accessibility_Test_Script_Pack.md`](../13_Test_and_Acceptance_Content/TS-016_Accessibility_Test_Script_Pack.md) | `O-07` there — where §4.6 is executed |
| `05-02` §10 · `05-04` §4 | The `S3` inventory and the `T5` access tier §4.4.1 is derived from |

| Depended on by |
|---|
| `CG-008` `U-41` and `HC-c` · `CG-011` `AT-08` · `HC-002` `HS-19`/`HS-21` · `TR-003` `DS-14` · `UI-010` `A-07` · `AP-012` §4.5.6 · `TPL_Help_Article.md` · `MM-009` · every help set, course pack and knowledge article |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **Per release** for §4.7 currency; **annually** for the standard; **immediately** after any §4.4 incident |
| Trigger for out-of-cycle review | A change to the `S3` inventory in `05-02` §10 or `LG-008` §4.2 · a new surface or device class · an unredacted publication · a `TS-002` change · an accessibility finding |
| Owner | **Content Design with Security.** Security owns §4.4 and may change it without Content Design's agreement; **the reverse is not true** |
| Approver | Content Design Lead with Security (`CG-002` §5.4) |
| Verification | §4.4 redaction is second-person verified and recorded (`SC-29`); §4.7 currency is queried from the `MM-012` register per release, not remembered |
| Effectiveness measure | **Unredacted publications: target zero.** Orphaned screenshots at each release: target zero. Both counted, not asserted |
| Change log | [`RF-006`](../99_Reference_and_Registers/RF-006_Content_Decision_Log_and_Change_Control.md) — **written; Category 99 completed 2026-08-18**. Every decision under this file is logged there |

---

## 7. Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **`TS-002` sandbox and persona set does not exist**, and `SC-01` prohibits production capture with no alternative. **Until it exists, no screenshot may lawfully be produced anywhere in the programme.** Recorded independently by `HC-002` `O-02`, `TR-003` `O-01`, `HC-020` `O-04` and `MM-001` `O-03` — **five files, one cause** | Test Lead with Content Design and Security | **W1 — blocking, absolutely** |
| **O-02** | **No documentation-capture account or environment access is provisioned.** `SC-04` requires purpose-created accounts per documented role; `OP-015` defines joiner-mover-leaver but no documentation role profile exists among the 38 access profiles `AUDIT-017` `OP-10` records as documented and non-existent | Security with Content Design | **W1** |
| **O-03** | **The second-person redaction verification in `SC-29` has no named owner.** Content Design cannot self-verify a Security control, and no Chief Data Officer is appointed — `LG-008` `O-05` records that every `M33` §9 rule has no owner | Chief Data Officer *(unappointed)* with Content Design Lead | **W1 — before the first capture** |
| **O-04** | **No accessibility reviewer is named** for §4.6. The **fifth** file to record it, after `TR-003` `O-02`, `HC-002` `O-04`, `HC-016` `O-04` and `MM-001` `O-06` | Content Design Lead | **W1** |
| **O-05** | **Screenshot production is a recurring operational load with no resource and no budget.** §4.10 makes the arithmetic visible: capped at one per article and one per segment, doubled for Bengali, re-captured on every release that touches the screen, across 15 help sets, 20 course packs, 16 knowledge files and nine waves. **It is not in the Master Index §7 estimate, which is specification-only** | Content Design Lead with Finance | **W1** |
| **O-06** | **Whether the sandbox will contain Bengali sample data is unconfirmed.** `SC-21` and `SC-48` require it; `TS-002` is unwritten and `BN-016` does not commit to it. A sandbox seeded only in English makes half the screenshot set unproducible | Test Lead with Localisation Lead | **W1** |
| **O-07** | **No tooling decision has been made** for capture, redaction verification, metadata stripping and register stamping. `SC-24`, `SC-28` and `SC-43` describe a pipeline; **a manual pipeline at this volume will fail at exactly the step that matters** (redaction), and the failure is silent | Platform Engineering with Content Design | **W2 — before the first help set** |
| **O-08** | **`MM-002` is registered at W1 and `HC-002` needs it at W2, which is correct — but `HC-005` `P03` help is W1**, and `AUDIT-018` `EO-03` records thirty-nine instances of content registered after its first consumption. This file is on the right side of that line and **is recorded here so the W1 date is not later moved without checking `HC-005`** | Programme Content Lead | W1 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md` — six sections in order; the `CG-009` `MM` deliverable table at §4.9; §7 added per category convention
- [x] **The `P1` priority justified by the five files that delegate a personal-data control here**
- [x] **Sandbox-only capture stated without a waiver clause, and the reason for having no waiver given**
- [x] Capture geometry fixed per surface at the device classes `04-00` actually names, not at a designer's monitor
- [x] Sample-data contract bound to `TS-002` and prohibiting invention, with non-routable contact data required
- [x] **Restricted-data list built from `05-02` §10 and `LG-008` §4.2, with "not captured" preferred over "redacted"**
- [x] **Redaction specified as destructive with blur and pixelation prohibited, and the unredacted source destroyed**
- [x] Second-person verification required and recorded
- [x] **`AP-012` §4.5.6 photograph case answered in full, including the reflection path**
- [x] **An unredacted publication classified as a data incident with a named route, not as a documentation defect**
- [x] Annotation specified with measured contrast, no colour-only signalling and no baked-in text
- [x] Alt text and long description obligations carried from `CG-011` with the search-index consequence stated
- [x] Currency rules aligned with `HC-002` `HS-17`…`HS-22` and `TR-003` `DS-12`…`DS-16` so help and training age together
- [x] **Bengali screenshots required to be captured from the Bengali interface, with the doubling stated and costed**
- [x] Volume enumerated from the consuming caps rather than estimated
- [x] All internal links resolve
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [x] English-only per `CG-010` §3.2
- [ ] **`O-01` `TS-002` absent — outstanding; no screenshot may be produced**
- [ ] **`O-03` redaction verifier unowned — outstanding; the control cannot be operated**
- [ ] **`O-05` screenshot production unresourced — outstanding**
- [ ] **`O-07` redaction tooling undecided — outstanding**
- [ ] Named approver recorded — **pending Content Design Lead with Security**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
