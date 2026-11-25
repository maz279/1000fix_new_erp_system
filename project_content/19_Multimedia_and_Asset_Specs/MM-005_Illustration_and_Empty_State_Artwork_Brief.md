---
id: MM-005
title: Illustration and Empty State Artwork Brief
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Design System Lead
author: Design System with Brand, Content Design and Localisation
reviewers: [Content Design Lead, Brand Lead, Localisation Lead, Accessibility reviewer, portal owners, HR Director, Programme Content Lead]
approver: Content Design Lead
content_class: D
purpose: >
  The illustration style, the cultural brief for Bangladesh, and the enumerated empty-state artwork
  inventory the twelve portals need at launch. UI-006 states the position plainly — on day one of
  every wave, every screen is an empty state — which makes this the most-seen artwork the
  programme produces and the artwork most likely to be bought as generic stock under time
  pressure. Generic illustration of people who do not look, dress or work like this workforce
  tells 800+ internal users and 250,000+ monthly customers that the product was made for somebody
  else, at exactly the moment the programme is asking them to adopt it.
traces_to: [UI-005, UI-006, UI-008, UI-009, VB-001, VB-002, VB-003, VB-006, VB-008, CG-003, CG-008, CG-010, CG-011, CG-012, HC-016, CM-005, CM-016, TR-003, MM-001, MM-002, MM-004, MM-009, MM-011, MM-012, 04-00 PS-03, 04-00 PS-04, 04-00 PS-05, 04-00 PS-08, 04-00 §P02, 05-06 NFR-073]
priority: P3
wave: W2
bilingual: no
bn_counterpart: n/a
sources:
  - source: project_content/03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-006_Empty_State_and_First_Run_Copy_Library.md §3.1–§3.5 the enumerated empty-state and first-run copy set; §7 "Illustration — decorative, empty alt (MM-005)"; the header position "on day one of every wave, every screen is an empty state"
    verified: 2026-08-18
    class: P1
  - source: project_content/01_Voice_Brand_and_Design_Content/VB-006_Design_System_Content_Standards.md §5.6 ES-01…ES-07 — four kinds of empty state, never blank, never jokey, "this is the first thing 800+ internal users see"
    verified: 2026-08-18
    class: P1
  - source: project_content/01_Voice_Brand_and_Design_Content/VB-003_Brand_Application_in_Enterprise_UI.md §5 — illustration permitted in empty states only, "the only place a picture helps"; §6 brand assets excluded from the P02 job flow, P09 and the P11 offline bundle; §4 full brand on sign-in, error, maintenance and first-run surfaces
    verified: 2026-08-18
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md §4.1 decorative images are marked decorative with empty alt, stated explicitly in the content file so engineering does not guess; CL-01 colour is never the only signal
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md §3 PS-03 Bengali default on customer and field surfaces, PS-05 responsive from 320px, PS-08 offline-capable surfaces; §P02 mid-range Android 11 with 3 GB RAM
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2027-02-18
---

# Illustration and Empty State Artwork Brief

| Item | Value |
|---|---|
| Governs | Every illustration the ERP and its twelve portals display, and the empty-state artwork set |
| Copy authority | [`UI-006`](../03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-006_Empty_State_and_First_Run_Copy_Library.md) — **this file draws; `UI-006` writes** |
| Component contract | [`VB-006`](../01_Voice_Brand_and_Design_Content/VB-006_Design_System_Content_Standards.md) §5.6 `ES-01`…`ES-07` |
| Audience | Illustrators (internal or commissioned), Design System, portal teams |
| Language | **English** — the brief. **The artwork carries no text at all** (`IL-09`) |
| Wave | W2 · Months 5–8 (`06-01` §3) — **and `UI-006` is W1. See `O-01`** |
| Content class | **D** — user-facing (`CG-002` §4.1) |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3). All
> six sections retained in order. The `CG-009` `MM` **deliverable specification table** is §4.7.
> §7 Open Items added per category convention.

---

## 1. Purpose

`UI-006`'s opening line is the whole argument: **"On day one of every wave, every screen is an
empty state. They are not an edge case; they are the launch experience."** `VB-006` `ES-06` says
the same thing from the component side and `ES-07` adds the constraint that makes it hard:
**never jokey — this is the first thing 800+ internal users see.**

`VB-003` §5 then makes empty states the *only* place illustration is permitted in an operational
view: *"Illustration — brand illustration → empty states only — the only place a picture helps."*

**So the artwork set is small, highly visible, and load-bearing for adoption.**

| Absent | Consequence |
|---|---|
| An enumerated inventory | The illustrations that exist are for the screens somebody remembered, and the dispatch console launches with a blank panel |
| A style position | Twelve portals with illustration from three sources, none of which sit together |
| **A cultural brief** | Stock illustration of a Western office, a Western uniform, a device this workforce does not repair, and a technician who does not look like the person reading it |
| A weight budget | 400 KB of decorative SVG shipped into a `P02` bundle whose device has 3 GB of RAM |
| An accessibility position | Decorative artwork announced to a screen reader as a meaningless graphic on every empty screen |
| A "what is *not* illustrated" rule | Illustration creeping from empty states into operational views, which `VB-003` §5 excludes |

**Consequence of absence (`CP-03`).** The most-seen screens at every one of nine wave launches
are either blank — which `ES-06` prohibits — or carry generic artwork that undermines the
credibility of the thing being launched. `CM-016` adoption campaigns and `CM-005` wave-launch
kits are running at the same moment, saying this system was built for you.

**What this file is not.** It is not the empty-state *copy* (`UI-006`), not the component contract
(`VB-006` §5.6), not photography (`MM-009` — and §4.2 states why an illustration is often the
safer choice), and not the icon set (`MM-004` — an illustration is not a large icon, `IL-04`).

---

## 2. Scope

**In scope.** The illustration style position; the cultural brief for Bangladesh; where
illustration is permitted, excluded and prohibited; the enumerated empty-state and first-run
artwork inventory drawn from `UI-006`; error, maintenance and offline artwork; the accessibility
position; weight, motion and dark-mode rules; the deliverable specification; and rules
`IL-01`…`IL-24`.

**Out of scope.**

| Subject | Owned by |
|---|---|
| Empty-state and first-run copy, keys and character budgets | [`UI-006`](../03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-006_Empty_State_and_First_Run_Copy_Library.md) |
| The four kinds of empty state and the component contract | [`VB-006`](../01_Voice_Brand_and_Design_Content/VB-006_Design_System_Content_Standards.md) §5.6 |
| No-permission wording and what must not be revealed | [`UI-005`](../03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-005_System_Permission_and_Session_Message_Library.md) |
| Loading, progress and offline copy | [`UI-008`](../03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-008_Loading_Progress_and_Long_Running_Job_Copy.md), [`UI-009`](../03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-009_Offline_Sync_and_Conflict_Resolution_Copy.md) |
| Icons | [`MM-004`](MM-004_Icon_Set_Requirements.md) |
| Photography of real people and places | [`MM-009`](MM-009_Photography_Brief_Branches_Workshop_and_Field.md) |
| Motion and animated explainers | [`MM-008`](MM-008_Animated_Explainer_Brief_Portal_Onboarding.md) |
| Format, colour management, delivery, acceptance | [`MM-001`](MM-001_Multimedia_Asset_Standard_and_Delivery_Specification.md) §4.2 class A3 |
| Naming, versioning, licensing records | [`MM-012`](MM-012_Digital_Asset_Management_and_Naming_Standard.md) |
| Where brand applies, is reduced or is excluded | [`VB-003`](../01_Voice_Brand_and_Design_Content/VB-003_Brand_Application_in_Enterprise_UI.md) §4–§6 |

---

## 3. Audience

| Reader | Uses it for | Reads it |
|---|---|---|
| **Illustrator (commissioned)** | The style, the cultural brief, the inventory and the acceptance criteria | Before drawing |
| **Design System Lead** | The library contract and the permitted-surface boundary | Continuously |
| **Portal team** | Which artwork exists for their surface and what to do where none does | Per portal |
| **Content Design** | The pairing with `UI-006` copy, and the never-jokey position | At review |
| **Localisation Lead** | Confirmation that no artwork carries text, and the cultural review route | At review |
| **Accessibility reviewer** | §4.6 — decorative marking, and the one case where it is not decorative | At gate |
| **Brand Lead** | The style's relationship to a brand identity that does not yet exist (`MM-001` `O-01`) | At approval |

---

## 4. Content

### 4.1 The style position

| Property | Position |
|---|---|
| **Register** | **Calm, plain, matter-of-fact.** These screens appear when something is absent, blocked or unfinished. The illustration's job is to make an empty screen look intentional, not to entertain |
| **Form** | **Geometric, flat, single-weight line with restrained flat fill.** No gradients, no shadows, no texture, no 3D, no isometric perspective |
| **Line** | 2 px stroke at the nominal artboard, matching the icon set's weight so the two read as one family (`MM-004` §4.2) |
| **People** | **Present but not the subject.** Where a person appears they are mid-task and small in frame. **No faces at expressive scale**, no emotion carried by a face |
| **Objects** | The real objects of this business — a laptop, an air conditioner, a mobile phone, a workbench, a parts bin, a delivery bag, a service counter |
| **Colour** | **Two-colour maximum plus neutrals.** Brand blue `#39B1DF` **as a fill** (permitted — `VB-003` `BC-03`), `#1E5F8A`, and the `#E9ECEF`/`#495057` neutrals |
| **Scale in layout** | **160 px maximum height** in a list or panel empty state; 240 px on a full-page state |
| **Density** | **One idea per illustration.** A scene with three things happening reads as none |

| # | Rule |
|---|---|
| **IL-01** | **The illustration never carries the message.** `UI-006` supplies a heading, a body line and an action; the artwork is what remains when those are removed, and the state must still be comprehensible without it |
| **IL-02** | **Never jokey, never apologetic, never cute** (`VB-006` `ES-07`). No mascots, no shrugging characters, no "oops", no error-face. A dispatcher meets the empty dispatch queue several times a day |
| **IL-03** | **No text, no numerals, no UI chrome inside the artwork.** Text in an image cannot be translated (WCAG SC 1.4.5, `CG-011` `AT-07`), and drawn UI ages faster than real UI |
| **IL-04** | **An illustration is not a large icon and an icon is not a small illustration.** Where the answer is a single object at a single weight, use the icon set at 48 px (`MM-004` §4.3) and commission nothing |
| **IL-05** | **The set is one family.** An illustration commissioned in W7 must sit beside one drawn in W1 without either looking dated. This is why the style is restrained: fashionable illustration ages inside a 36-month programme |

### 4.2 The cultural brief — Bangladesh

**This section is the reason the file exists at `P3` rather than not at all.** The register's own
justification is that *"generic stock illustration undermines credibility"*, and the failure mode
is specific and avoidable.

| Get right | Detail |
|---|---|
| **Dress** | Everyday Bangladeshi working dress. Men in shirt and trousers; women in shalwar kameez or sari as appropriate to role. **Branch and workshop staff in the actual 1000FiX uniform** where one exists — and where it does not, in plain workwear rather than an invented one |
| **Head covering** | Depicted naturally where a woman would wear one, and naturally where she would not. **Both are ordinary; neither is a statement** |
| **Workplace** | A Bangladeshi service counter and workshop — steel shelving, a ceiling fan, a tiled floor, a roller shutter. **Not an open-plan Western office with a potted fern** |
| **Vehicles** | The vehicles this network actually uses — motorcycle, CNG auto-rickshaw, small van. **Not a Western delivery truck** |
| **Devices** | The categories the business services: laptops, desktops, printers, air conditioners, refrigerators, televisions, mobile phones, servers, CCTV. **Drawn generically — no recognisable brand form** (`IL-07`) |
| **Environment** | Dhaka and district-town streetscape where a street appears at all |
| **Script** | **None.** `IL-03` prohibits text entirely, which removes the whole question of which language a drawn sign is in |
| **Skin tone and build** | The range actually present in Bangladesh, drawn without exaggeration |

| Get wrong and it is noticed | Why it matters |
|---|---|
| Western office furniture, Western uniforms, Western street furniture | The reader concludes the product was configured for somebody else and localised afterwards — which is the impression `PS-03` and `CP-05` exist to prevent |
| Religious or political symbolism of any kind | Not the company's to place in a workplace tool |
| A woman drawn only in support roles, or absent from technical roles | Untrue of the business and visible to every employee |
| A technician working without the PPE `SP-030` requires | **A safety statement.** See `IL-08` |
| Recognisable brand-partner product forms | 17+ manufacturer authorisations; drawing a recognisable product implies an endorsement the agreement does not give (`EO-012`) |
| Anything that reads as a caricature | — |

| # | Rule |
|---|---|
| **IL-06** | **Every illustration containing a person or a workplace is reviewed by Bangladeshi reviewers** — at minimum one branch employee and one field technician, plus HR. **A style approval by head office alone does not discharge this**, and the review is recorded |
| **IL-07** | **Devices are drawn generically.** No recognisable brand-partner product form, no logo, no distinctive silhouette that identifies a manufacturer |
| **IL-08** | **Illustrated work is compliant work.** A drawn technician wears the PPE `SP-030` and [`KB-013`](../07_Knowledge_Base_and_Technical_Library/KB-013_ESD_Chemical_and_Battery_Safety_Data.md) require for the task shown, uses the right tool, and is never shown doing something the SOP prohibits. **HSE approves any illustration depicting a physical task** — the same gate `TR-003` `DS-26` gate 5 applies to training content |
| **IL-09** | **No text in artwork, in either language** (`IL-03`). This is also what makes the set language-neutral and halves its cost |
| **IL-10** | **Stock illustration is not used as delivered.** Where a stock library is the starting point, the licence permits modification, the modification brings it to §4.1 and §4.2, and the licence is recorded in `MM-012` §4.5. **An unmodified stock image on the busiest screen in the product is the failure this file exists to prevent** |

### 4.3 Where illustration is permitted, excluded and prohibited

| Surface | Position | Authority |
|---|---|---|
| **Empty states** in any portal | **Permitted** — the primary case | `VB-003` §5 |
| First-run and onboarding screens | **Permitted**, full brand | `VB-003` §4 |
| Sign-in and sign-out | **Permitted**, full brand | `VB-003` §4 |
| Error pages, maintenance and status pages | **Permitted**, full brand — *"brand reassurance is the only content available"* | `VB-003` §4 |
| Public tracking link (no login) | **Permitted**, full brand | `VB-003` §4 |
| `P01`, `P07`, `P12` generally | **Permitted** — full-brand external surfaces | `VB-003` §4 |
| **Operational views — lists, tables, consoles, forms** | **Excluded.** *"Photography in a dispatch console is noise"*, and illustration is permitted in empty states only | `VB-003` §5 |
| **`P02` technician job execution** | **Excluded.** No brand colour in the job flow beyond a 24 px header mark; sunlight legibility and battery govern | `VB-003` §6 |
| **`P09` rider** | **Excluded.** As `P02` | `VB-003` §6 |
| **`P11` auditor offline bundle** | **Excluded — not downloaded at all.** Payload is the constraint | `VB-003` §6 |
| System and administrator consoles | **Excluded.** Neutral only | `VB-003` §6 |
| Print and PDF documents | **Prohibited.** `VB-004` §5 permits no colour fills, no gradients, no background tints | `VB-004` §5 |
| Thermal output | **Prohibited.** Monochrome, 203 dpi | `VB-004` `TH-02` |

| # | Rule |
|---|---|
| **IL-11** | **`P02`, `P09` and `P11` empty states are text-only.** They still exist — `ES-06` prohibits a blank screen — but they are a heading, a body line and an action, with no artwork. `UI-006` §3.1's `p02.empty.jobs` is one of these |
| **IL-12** | **An illustration never appears in an operational view even where a designer thinks it would soften it.** Softening a dense console is what `VB-003` §5 measured against seven hours a day of use |

### 4.4 The empty-state artwork inventory

**Enumerated from `UI-006` §3, not estimated.** `UI-006` defines four kinds of empty state plus
first run; artwork is commissioned per **kind and surface family**, not per key — which is what
keeps a set of this visibility to a producible size.

#### 4.4.1 "Nothing yet" — `common.empty.none_yet.*`

| # | `UI-006` key | Surface | Artwork | Illustrated? |
|---:|---|---|---|:--:|
| 1 | `p01.empty.orders` | Customer services list | **A device on a counter, waiting** | ✔ |
| 2 | `p01.empty.devices` | Customer devices | **A device with a tag** | ✔ |
| 3 | `p02.empty.jobs` | Technician jobs | — | ✖ `IL-11` |
| 4 | `ws.empty.dispatch_queue` | Dispatch console | — | ✖ operational view |
| 5 | `ws.empty.workshop` | Workshop bench | — | ✖ operational view |
| 6 | `ws.empty.invoices` | Invoices | — | ✖ operational view |

#### 4.4.2 "No results" — `common.empty.no_results.*`

| # | `UI-006` key | Artwork | Illustrated? |
|---:|---|---|:--:|
| 7 | `common.empty.no_results.search` | **One shared "nothing matched" mark** across every portal | ✔ — one asset |
| 8 | `common.empty.no_results.filter` | As above | ✔ — reused |
| 9 | `common.empty.no_results.date` | As above | ✔ — reused |

> **One asset, three keys.** The state differs in *copy* — `UI-006` §3.2 names the filter count so
> the user can see **why** nothing is shown (`ES-03`) — and not in picture.

#### 4.4.3 "Not configured" — `common.empty.not_configured.*`

| # | `UI-006` key | Artwork | Illustrated? |
|---:|---|---|:--:|
| 10 | `not_configured.master_data` | **One shared "setup incomplete" mark** | ✔ — one asset |
| 11 | `not_configured.price_list` | As above | ✔ — reused |
| 12 | `not_configured.zone` | **A map area outside coverage** — customer-facing, so illustrated distinctly | ✔ |

#### 4.4.4 "No permission" — `common.empty.no_permission.*`

| # | `UI-006` key | Artwork | Illustrated? |
|---:|---|---|:--:|
| 13 | `no_permission.list` | **Neutral, non-punitive mark.** **No lock, no barrier, no red** | ✔ — one asset |

> **`IL-13`: the no-permission state is never drawn as a prohibition.** `UI-006` §3.4 and `UI-005`
> `S-01` forbid revealing that data exists; a padlock over a vault implies there is something
> behind it. A neutral mark, and copy that names who grants access.

#### 4.4.5 First run — `common.firstrun.*`

| # | `UI-006` key | Surface | Illustrated? |
|---:|---|---|:--:|
| 14 | `p01.firstrun.welcome` | `P01` first login | ✔ full brand |
| 15 | `p02.firstrun.welcome` | `P02` first login | ✖ `IL-11` — **but see `O-03`** |
| 16 | `ws.firstrun.welcome` | `P03` workspace chooser | ✔ restrained |
| 17 | `p09.firstrun.welcome` | `P09` first login | ✖ `IL-11` |

#### 4.4.6 System states

| # | State | Artwork | Copy |
|---:|---|---|---|
| 18 | Full-page error | **A single "something is broken here" mark** — one asset, all portals | `VB-006` §5.7 |
| 19 | Maintenance / status page | **One asset** | [`OP-005`](../17_Operations_Support_and_Runbooks/OP-005_Status_Page_and_Maintenance_Notice_Copy.md) |
| 20 | Offline (web surfaces only) | **One asset** | [`UI-009`](../03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-009_Offline_Sync_and_Conflict_Resolution_Copy.md) |
| 21 | Session expired / signed out | **Reuses 14's family** | [`UI-005`](../03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-005_System_Permission_and_Session_Message_Library.md) |
| 22 | Search-index unavailable | **Reuses 7** | `UI-008` |

**Inventory total: 22 states · 14 illustrated · 8 text-only · 11 distinct artworks** (reuse
collapses 14 illustrated states onto 11 assets).

| # | Rule |
|---|---|
| **IL-14** | **Artwork is commissioned per kind, not per key.** Eleven assets serve twenty-two states. A one-to-one set would be four times the cost and would make the four kinds harder to tell apart, not easier |
| **IL-15** | **The four `ES-01` kinds must be visually distinguishable from each other at a glance.** *Nothing yet*, *no results*, *not configured* and *no permission* are different situations with different remedies, and a user who cannot tell them apart takes the wrong action |
| **IL-16** | **New surfaces reuse an existing asset unless they are a genuinely new kind.** The inventory grows by decision, and the decision is logged (`MM-004` `IC-01` pattern) |

### 4.5 Weight, motion and theme

| # | Rule |
|---|---|
| **IL-17** | **≤ 40 KB per SVG optimised** (`MM-001` §4.2 class A3); ≤ 60 KB raster at 1× where raster is unavoidable |
| **IL-18** | **Illustration is not shipped into a surface that does not display it.** `P02`, `P09` and `P11` bundles carry none, and `VB-003` §6 makes that a payload rule, not a preference |
| **IL-19** | **Empty-state artwork does not animate.** It appears when the user is already blocked; motion on a blocked screen is noise. Any motion anywhere honours `prefers-reduced-motion` (WCAG SC 2.3.3) and never flashes (SC 2.3.1) |
| **IL-20** | **Dark-mode variants are authored, not inverted** (`MM-001` `CS-08`). An inverted illustration produces the wrong tonal relationships and, with a two-colour palette, usually an unreadable one |
| **IL-21** | Artwork is **legible at 160 px height on a 320 px-wide viewport** (`PS-05`), and is checked there — not at artboard size |

### 4.6 Accessibility

| # | Rule |
|---|---|
| **IL-22** | **Empty-state illustration is decorative and carries an empty alt attribute.** `UI-006` §7 states this directly, and `CG-011` §4.1 requires it to be **said explicitly in the content file so engineering does not guess** |
| **IL-23** | **Because it is decorative, it may carry no information** (`IL-01`). The two rules are one rule stated twice: an illustration that is marked decorative and carries meaning is inaccessible, and an illustration that carries meaning and is announced is noise on every empty screen |
| **IL-24** | **The one case that is not decorative** is `not_configured.zone` (#12), where a coverage map communicates something the copy also states. **The copy states it; the artwork remains decorative.** If a future artwork carries information the copy does not, it is the wrong artwork |
| **IL-25** | Colour is never the only signal (`CG-011` `CL-01`); the four kinds differ by **form**, not by hue (`IL-15`) |
| **IL-26** | Non-text contrast of any shape a user must perceive meets 3:1 (SC 1.4.11) — though `IL-23` means, correctly, that there should be no such shape |

### 4.7 Deliverable specification

**The `CG-009` §3 required addition for Category 19.**

| Attribute | Specification |
|---|---|
| **Master format** | **SVG 1.1**, flat, paths merged, no embedded raster, no editor metadata |
| **Derived formats** | AVIF + WebP + PNG @1×/2× where raster is required (`MM-001` §4.4) |
| **Dimensions** | 800 × 600 px nominal artboard; renders at **160 px height in-panel, 240 px full-page**; legible at 320 px viewport |
| **Colour** | sRGB; **two colours plus neutrals** — `#39B1DF` fill, `#1E5F8A`, `#E9ECEF`, `#495057`; **light and dark variants authored separately** |
| **Compression** | **≤ 40 KB SVG optimised**; ≤ 60 KB raster @1× |
| **Text** | **None** (`IL-03`) |
| **Motion** | **None** for empty states (`IL-19`) |
| **Accessibility** | Decorative, empty alt, stated in `UI-006` §7 (`IL-22`) |
| **Metadata** | XMP `dc:title`, `dc:description`, `dc:relation` = `UI-006` key set served, `dc:rights`, **licence terms where stock-derived** (`IL-10`) |
| **Naming** | `MM-012` §4.3 — stem names the *kind* served, not the screen |
| **Source** | Layered editable source (`MM-001` `DL-02`) |
| **Evidence** | **Cultural review record** (`IL-06`) and **HSE approval** where a physical task is depicted (`IL-08`) |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| [`UI-006_Empty_State_and_First_Run_Copy_Library.md`](../03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-006_Empty_State_and_First_Run_Copy_Library.md) | The key set §4.4 enumerates; §7 the decorative/empty-alt position |
| [`UI-005_System_Permission_and_Session_Message_Library.md`](../03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-005_System_Permission_and_Session_Message_Library.md) | `S-01` — why `IL-13` forbids a padlock |
| [`UI-008_Loading_Progress_and_Long_Running_Job_Copy.md`](../03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-008_Loading_Progress_and_Long_Running_Job_Copy.md) · [`UI-009_Offline_Sync_and_Conflict_Resolution_Copy.md`](../03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-009_Offline_Sync_and_Conflict_Resolution_Copy.md) | States 20 and 22 |
| [`VB-006_Design_System_Content_Standards.md`](../01_Voice_Brand_and_Design_Content/VB-006_Design_System_Content_Standards.md) | §5.6 `ES-01`…`ES-07`; §5.7 full-page error |
| [`VB-003_Brand_Application_in_Enterprise_UI.md`](../01_Voice_Brand_and_Design_Content/VB-003_Brand_Application_in_Enterprise_UI.md) | §4/§5/§6 — the permitted, excluded and prohibited table in §4.3; `BC-03` brand blue as a fill |
| [`VB-002_Persona_and_Portal_Tone_Matrix.md`](../01_Voice_Brand_and_Design_Content/VB-002_Persona_and_Portal_Tone_Matrix.md) · [`VB-001_ERP_Product_Voice_and_Tone_Guide.md`](../01_Voice_Brand_and_Design_Content/VB-001_ERP_Product_Voice_and_Tone_Guide.md) | The register `IL-02`'s never-jokey rule expresses visually |
| [`VB-004_Print_and_PDF_Brand_Template_Standard.md`](../01_Voice_Brand_and_Design_Content/VB-004_Print_and_PDF_Brand_Template_Standard.md) | §5 — why illustration is prohibited in print and thermal |
| [`CG-011_Accessibility_Content_Standard.md`](../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md) | §4.1 decorative marking; `CL-01`; §4.6 obligations |
| [`CG-003_ERP_Product_Content_Style_Guide.md`](../00_Content_Governance_and_Standards/CG-003_ERP_Product_Content_Style_Guide.md) | The tone the artwork must not contradict |
| [`SP-030_SOP_Health_Safety_and_Incident_Reporting.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-030_SOP_Health_Safety_and_Incident_Reporting.md) · [`KB-013_ESD_Chemical_and_Battery_Safety_Data.md`](../07_Knowledge_Base_and_Technical_Library/KB-013_ESD_Chemical_and_Battery_Safety_Data.md) | `IL-08` — illustrated work is compliant work |
| [`HC-016_In_Product_Help_Tour_and_Coach_Mark_Copy.md`](../09_Help_Centre_and_Self_Service/HC-016_In_Product_Help_Tour_and_Coach_Mark_Copy.md) | First-run surfaces where artwork and tour copy meet |
| [`CM-005_Wave_Launch_Communication_Kit.md`](../16_Change_Management_and_Comms/CM-005_Wave_Launch_Communication_Kit.md) · [`CM-016_Adoption_Campaign_Content.md`](../16_Change_Management_and_Comms/CM-016_Adoption_Campaign_Content.md) | The launch moment §1 describes |
| [`OP-005_Status_Page_and_Maintenance_Notice_Copy.md`](../17_Operations_Support_and_Runbooks/OP-005_Status_Page_and_Maintenance_Notice_Copy.md) | State 19 |
| [`MM-001_Multimedia_Asset_Standard_and_Delivery_Specification.md`](MM-001_Multimedia_Asset_Standard_and_Delivery_Specification.md) | Class A3 format, colour, metadata, acceptance |
| [`MM-004_Icon_Set_Requirements.md`](MM-004_Icon_Set_Requirements.md) | The stroke weight this style matches; the `IL-04` boundary |
| [`MM-008_Animated_Explainer_Brief_Portal_Onboarding.md`](MM-008_Animated_Explainer_Brief_Portal_Onboarding.md) · [`MM-009_Photography_Brief_Branches_Workshop_and_Field.md`](MM-009_Photography_Brief_Branches_Workshop_and_Field.md) | Motion and photography — the two alternatives to illustration |
| [`MM-011_Email_and_HTML_Asset_Specification.md`](MM-011_Email_and_HTML_Asset_Specification.md) | Where illustration is rasterised for email |
| [`MM-012_Digital_Asset_Management_and_Naming_Standard.md`](MM-012_Digital_Asset_Management_and_Naming_Standard.md) | Naming, licence records for stock-derived work (`IL-10`) |
| `04-00` `PS-03`, `PS-05`, `PS-08`, §P02 | Bengali default, 320 px responsiveness, offline surfaces, the device floor |

| Depended on by |
|---|
| `UI-006` §7 and §10 · the shared component library's empty-state component · every portal's launch surface · `CM-005` wave-launch assets |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **Per wave while portals are launching**, then annually |
| Trigger for out-of-cycle review | A new `UI-006` key or empty-state kind · a new portal · an adoption finding at a wave launch · a cultural review objection · a `VB-003` change to where illustration is permitted |
| Owner | **Design System Lead**, with Brand for style and Content Design for the pairing with copy |
| Approver | Content Design Lead (`CG-002` §5.4, class D) |
| Cultural review | **Recurring, not one-off** (`IL-06`). Repeated at each material addition to the set |
| Effectiveness measure | **Empty-state screens shipped with no artwork and no text-only design — target zero**; and adoption-survey comment themes at each wave launch |
| Change log | [`RF-006`](../99_Reference_and_Registers/RF-006_Content_Decision_Log_and_Change_Control.md) — **written; Category 99 completed 2026-08-18**. Every decision under this file is logged there |

---

## 7. Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **This file is registered at W2 and `UI-006` is `P1` at W1.** `UI-006`'s own position is that *"on day one of every wave, every screen is an empty state"*, and W1 is the first wave with users on it — `P03` and its fourteen workspaces. **The artwork is therefore needed one wave before it is scheduled.** `AUDIT-018` `EO-03` recorded thirty-nine instances of this shape across six categories and `AUDIT-014` R-02, `AUDIT-015` R-04 and `AUDIT-018` R-03 all asked for the sequencing basis to be corrected **once, register-wide, rather than patched per file**. **It is reported here and deliberately not patched** | Programme Content Lead with Design System | **W1 — reported, not patched** |
| **O-02** | **`UI-006` `bilingual: yes` and its Bengali counterpart is outstanding; `BN-003` is unwritten, so its terminology is indicative.** `IL-09` removes text from the artwork, which insulates the set from that — **but the pairing of artwork to copy cannot be reviewed in context until the Bengali exists**, and `IL-15`'s four-kinds distinguishability is a joint property of picture and words | Localisation Lead with Content Design | W2 |
| **O-03** | **`p02.firstrun.welcome` is text-only under `IL-11`, and it is the first screen 200–400 technicians ever see.** `VB-003` §4 permits full brand on first-run screens and §6 excludes brand from `P02`; **the two positions meet exactly here and neither resolves it.** This file takes the exclusion as governing and records the conflict rather than deciding it | Brand Lead with Design System | **W2 — before `P02` build** |
| **O-04** | **No illustrator is engaged and no cultural review panel exists.** `IL-06` requires named Bangladeshi reviewers including a branch employee and a field technician; **no such review route is defined anywhere in `CG-002` §8's cadence**, and the Master Index §7 Category 19 estimate is specification-only | Design System Lead with HR and Finance | **W2** |
| **O-05** | **The 1000FiX uniform is unspecified.** §4.2 requires illustrated branch and workshop staff to wear it. **No file in this content set describes it**, which is the same shape as the master-identity gap `MM-001` `O-01` records against `AUDIT-018` `EO-13` | Brand Lead with HR | W2 |
| **O-06** | **`IL-08` requires HSE approval for any illustration depicting a physical task, and no HSE reviewer is named for content.** `TR-003` `DS-26` gate 5 has the same requirement for training and the same gap | HSE Lead with Content Design Lead | **W2** |
| **O-07** | **Whether the design system's empty-state component supports a per-kind illustration slot is unconfirmed**, and `IL-14`'s eleven-assets-for-twenty-two-states model assumes it does. If the component takes a single fixed illustration, the model collapses to one asset or to twenty-two | Design System with Platform Engineering | W2 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md` — six sections in order; the `CG-009` `MM` deliverable table at §4.7; §7 added per category convention
- [x] Style position stated as a set of buildable properties, with the ageing argument for restraint
- [x] **Cultural brief written as specifics — dress, workplace, vehicles, devices, environment — not as a sentiment**
- [x] **Cultural review required from named Bangladeshi reviewers including a field technician, and recorded**
- [x] Illustrated work required to be compliant work, with HSE approval where a task is depicted
- [x] **Recognisable brand-partner product forms prohibited, tied to the 17+ authorisations**
- [x] Permitted / excluded / prohibited stated per surface with `VB-003` and `VB-004` cited per row
- [x] **Inventory enumerated from `UI-006` §3 — 22 states, 14 illustrated, 11 distinct assets — counted, not estimated**
- [x] Commissioning per kind rather than per key, with the four kinds required to be distinguishable
- [x] **The no-permission state prohibited from being drawn as a prohibition, tied to `UI-005` `S-01`**
- [x] Weight, motion, theme and payload rules stated, with `P02`/`P09`/`P11` excluded from the bundle
- [x] **Decorative marking and the may-carry-no-information consequence stated as one rule in two halves**
- [x] No text in artwork, in either language — removing the translation question entirely
- [x] All internal links resolve
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [x] English-only per `CG-010` §3.2
- [ ] **`O-01` W2 registration against a W1 need — reported, not patched, per `AUDIT-018` R-03**
- [ ] **`O-03` the `P02` first-run brand conflict is unresolved — outstanding**
- [ ] **`O-04` no illustrator engaged and no cultural review panel exists — outstanding**
- [ ] **`O-05` the uniform is unspecified — outstanding**
- [ ] Named approver recorded — **pending Content Design Lead**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
