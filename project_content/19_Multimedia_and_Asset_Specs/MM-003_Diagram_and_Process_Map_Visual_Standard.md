---
id: MM-003
title: Diagram and Process Map Visual Standard
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Business Process Lead with Design System
author: Business Process with Design System, Enterprise Architecture and Content Design
reviewers: [Business Process Lead, Enterprise Architecture, Content Design Lead, Design System Lead, Accessibility reviewer, Quality Manager, Localisation Lead, Programme Content Lead]
approver: Content Design Lead with Business Process Lead
content_class: D
purpose: >
  The visual half of process and architecture documentation — canvas, geometry, shape and colour
  semantics, typography, export format and the accessibility of a diagram. SP-003 fixes the
  notation and rules that text governs and the diagram derives; this file fixes what the drawn
  artefact must look like and what must be delivered with it. Twenty-eight SOPs, a value-stream
  map, an architecture set, a data model and nine waves of slide decks will otherwise be drawn by
  four groups in four tools to four conventions, and a diagram set that cannot be compared cannot
  be reviewed, maintained, translated or trained from.
traces_to: [SP-001, SP-002, SP-003, SP-004, SP-005, SP-006, CG-004, CG-005, CG-008, CG-010, CG-011, CG-012, VB-003, VB-008, VB-009, MD-027, MD-028, RP-007, AP-003, AP-004, CM-010, TR-003, TR-022, KB-001, TS-016, BN-006, MM-001, MM-002, MM-010, MM-012, 04-00 §P03, 05-02, 05-03, 05-04, 05-05, 05-06 NFR-073]
priority: P2
wave: W1
bilingual: no
bn_counterpart: n/a
sources:
  - source: project_content/06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-003_To_Be_Process_Design_Standard_and_Notation.md §4.2 permitted and forbidden BPMN 2.0 element subset; PD-01 text is authoritative and the diagram derivative; §4.5 swimlane rules PD-06…PD-09; §4.11 tooling — BPMN 2.0 XML exported to SVG, Bengali diagrams not produced, every embedded SVG carries a text alternative that is the SOP §5 step table
    verified: 2026-08-18
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md §4.1 — "Diagram or process map — short alt plus a text description of the flow, usually a numbered list"; CL-01 colour is never the only signal
    verified: 2026-08-18
    class: P1
  - source: project_content/01_Voice_Brand_and_Design_Content/VB-003_Brand_Application_in_Enterprise_UI.md §5.1 D-01 — the primary work area is designed to 1366x600 and anything requiring more is a defect; §3 measured contrast ratios
    verified: 2026-08-18
    class: P1
  - source: OMG Business Process Model and Notation (BPMN) 2.0.2 — element set, pool and lane semantics, gateway types, BPMN 2.0 XML interchange format
    verified: 2026-08-18
    class: P1
  - source: W3C Web Content Accessibility Guidelines (WCAG) 2.1 — SC 1.1.1 non-text content, SC 1.3.1 info and relationships, SC 1.4.1 use of colour, SC 1.4.5 images of text, SC 1.4.11 non-text contrast
    verified: 2026-08-18
    class: P1
  - source: Accessible SVG practice — the reliable pattern across tested browser and screen-reader combinations is an inline svg element carrying role="img" with a title element for the short name and a desc element for the longer description, referenced by aria-labelledby; where an SVG is embedded through an img element the alt attribute carries the text alternative
    verified: 2026-08-18
    class: P3
    note: Corroborated across multiple independent accessibility practitioner sources. Converts to P1 on completion of the TS-016 screen-reader pass, which is mandatory before any diagram set is published.
supersedes: none
review_due: 2027-02-18
---

# Diagram and Process Map Visual Standard

| Item | Value |
|---|---|
| Governs | Every drawn artefact the programme publishes — process maps, architecture, data model, sequence, journey and value-stream diagrams |
| Notation authority | [`SP-003`](../06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-003_To_Be_Process_Design_Standard_and_Notation.md) for process; this file for **everything visual** |
| Audience | Business process analysts, enterprise architects, implementation-partner consultants, instructional designers, comms |
| Language | **English.** `SP-003` §4.11 decided that **Bengali diagrams are not produced**; §4.4 explains what carries the Bengali |
| Wave | W1 · Months 1–4 (`06-01` §3) |
| Content class | **D** — user-facing (`CG-002` §4.1) |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3). All
> six sections retained in order. The `CG-009` `MM` **deliverable specification table** is §4.8.
> §7 Open Items added per category convention.

---

## 1. Purpose

`SP-003` §1 already names the failure precisely: four groups working in parallel produce, for the
same process, *"one BPMN diagram, one flowchart, one numbered list and one slide"*. It then fixes
the **notation** — the permitted BPMN subset, the forbidden elements, the swimlane rule, the
exhaustive-branch rule.

**It does not fix what the drawing looks like.** Two analysts can both obey `SP-003` §4.2 and
produce diagrams that cannot be placed on the same page: different canvases, different line
weights, different type sizes, colour used to mean two different things, one exported as a 4 MB
PNG and one as SVG, neither carrying a text alternative.

| Absent | Consequence |
|---|---|
| A fixed canvas and geometry | Diagrams that do not fit 1366 × 600, which `VB-003` `D-01` calls a defect, and that cannot be placed side by side in a review |
| Shape and colour semantics | Colour meaning "external party" in one diagram and "manual step" in the next — and `SP-003` §4.2 already **forbids colour carrying meaning at all** |
| A stated export contract | Bitmap-only diagrams that cannot be diffed in version control, cannot be re-rendered at print resolution, and cannot be made accessible |
| An accessibility deliverable | A `NFR-073` AA failure on every surface carrying a diagram, and a process library unusable by a screen-reader user |
| A Bengali position | Twenty-eight bilingual SOPs with a redrawing question nobody answered, or twenty-eight redrawn diagrams doubling maintenance for no comprehension gain |

**Consequence of absence (`CP-03`).** A process and architecture library that cannot be compared,
maintained, printed, embedded or read aloud — and that becomes distrusted at the first release,
which `SP-003` `PD-02` warns is what happens to process documents that describe unstable detail.

**What this file is not.** It is not the notation (`SP-003`), not the value streams (`SP-001`),
not the chart standard (`RP-007`), not the icon set (`MM-004`), and not a tool choice — §4.7 makes
a tooling requirement, not a product selection.

---

## 2. Scope

**In scope.** The five diagram families and their notation authority; canvas, grid and geometry;
line, arrowhead and shape specification; the greyscale-survivable palette and the colour-carries-
nothing rule; typography and label length; the Bengali position; export formats and the source-of-
truth pairing; **accessibility of a diagram**, including the SVG pattern and the text alternative;
diagrams in print, in slides and at 1366 × 600; the deliverable specification; and rules
`DG-01`…`DG-26`.

**Out of scope.**

| Subject | Owned by |
|---|---|
| BPMN element subset, gateways, lanes, decomposition depth, naming | [`SP-003`](../06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-003_To_Be_Process_Design_Standard_and_Notation.md) §4.2–§4.9 |
| The value streams and L0/L1 structure | [`SP-001`](../06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-001_Process_Architecture_and_Value_Stream_Map.md) |
| Approval limits, escalation paths, duty pairs cited on a diagram | [`SP-004`](../06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-004_Approval_Matrix_and_Delegation_of_Authority.md), [`SP-005`](../06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-005_Escalation_Matrix.md), [`SP-006`](../06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-006_Segregation_of_Duties_Register.md) |
| Chart and data-visualisation labelling | [`RP-007`](../14_Reporting_Analytics_and_KPI/RP-007_Chart_Label_and_Visualisation_Standard.md) — **a chart is not a diagram** |
| Status colour semantics in the product | [`VB-008`](../01_Voice_Brand_and_Design_Content/VB-008_Status_Colour_and_Label_Semantics_Register.md) — **not reused for diagrams**, see `DG-11` |
| Icon glyphs a diagram may reference | [`MM-004`](MM-004_Icon_Set_Requirements.md) |
| File format, colour management, delivery, acceptance | [`MM-001`](MM-001_Multimedia_Asset_Standard_and_Delivery_Specification.md) §4.2 class A4 |
| Naming, versioning, storage | [`MM-012`](MM-012_Digital_Asset_Management_and_Naming_Standard.md) |
| Slide design and deck structure | [`CM-010`](../16_Change_Management_and_Comms/CM-010_Town_Hall_and_Roadshow_Content.md) — **which cites this file for notation** |

---

## 3. Audience

| Reader | Uses it for | Reads it |
|---|---|---|
| **Business process analyst** | Drawing an L1 or L2 diagram that will pass `SP-003` §4.10 review | Before drawing |
| **Implementation-partner consultant** | The convention their deliverables are accepted against | At mobilisation |
| **Enterprise architect** | Architecture, integration and data-model diagram families | Per artefact |
| **Branch SME describing their own work** | The simplest permitted form — usually a numbered list, not a diagram (`DG-02`) | Once |
| **Instructional designer** | What a diagram must carry to be usable in a course and in a job aid | Per storyboard |
| **Comms** | Diagrams in a town-hall deck at the back of a room | Per wave |
| **Accessibility reviewer** | §4.6, which is where most diagram sets fail | At gate |
| **Quality Manager** | The ISO 9001 process library's visual consistency | At surveillance |

---

## 4. Content

### 4.1 The five diagram families

| # | Family | Notation | Authority | Where it appears |
|---:|---|---|---|---|
| **F1** | **Process / process map** | **BPMN 2.0**, constrained subset | `SP-003` §4.2 | SOPs, training, ISO library |
| **F2** | **Value stream / journey** | Left-to-right stage band with measures | `SP-001` §4.3–4.8 | `SP-001`, executive material |
| **F3** | **Architecture / landscape** | Boxes-and-connectors, layered | `02-05` layers `L1`–`L6` | Architecture set, `AP-001` developer portal |
| **F4** | **Integration / sequence** | Sequence diagram, participants as columns | `05-03` integration set, [`AP-004`](../15_Integration_and_Developer_Content/AP-004_Webhook_and_Callback_Integration_Guide.md) | Developer content, runbooks |
| **F5** | **Data model / entity** | Crow's-foot ERD | `05-02` | Data model, migration mapping |

| # | Rule |
|---|---|
| **DG-01** | **A diagram is drawn only where the artefact's owning standard says one is drawn.** `SP-003` §4.3 draws at L1 and at L2 only where three or more parallel paths exist; **L3 is never drawn** |
| **DG-02** | **A numbered list beats a weak diagram.** Where a process is linear, the step table in the SOP §5 is the artefact and no diagram is produced. `PD-01` already makes the text authoritative |
| **DG-03** | A family is declared in the source file. **A diagram mixing two families' notations is rejected** — a sequence diagram with swimlanes, or an ERD with gateways, is neither |
| **DG-04** | **No family may invent notation.** Where an artefact needs something the family does not have, the need is raised to the family's authority, not solved on the canvas (`SP-003` `PD-14`, `ID-07`) |

### 4.2 Canvas and geometry

| Property | Value |
|---|---|
| **Base grid** | **8 px**, matching the design system's spacing base (`VB-003` §5) |
| **Canvas width** | **1280 px nominal**, so the rendered diagram fits **1366 × 600** with margin (`VB-003` `D-01`) |
| **Canvas height** | Unbounded downward; **a diagram taller than 1.5 canvas widths is decomposed**, not scrolled (`DG-06`) |
| **Outer margin** | 24 px on all sides |
| **Node minimum size** | 120 × 64 px for a task; 64 × 64 px for a gateway or event |
| **Node spacing** | ≥ 48 px horizontal, ≥ 32 px vertical |
| **Lane height** | ≥ 120 px; **maximum six lanes** (`SP-003` `PD-07`) |
| **Connector** | **Orthogonal only.** No diagonal, no curved, no crossing where a route exists |
| **Line weight** | **2 px** sequence flow · **2 px dashed** message flow · **1 px** association |
| **Arrowhead** | Solid filled triangle for sequence flow · open for message flow · none for association — **the three are distinguishable in monochrome** |
| **Corner radius** | 4 px on tasks, matching the product's own radius (`VB-003` §5) |

| # | Rule |
|---|---|
| **DG-05** | **Flow runs left to right; exception paths run downward.** A reader scanning a diagram should meet the happy path without effort. `PD-12` requires at least one exception path in every L2 process, and downward is where it goes |
| **DG-06** | **A diagram that does not fit 1366 × 600 at 100% is a decomposition failure, not a canvas problem.** Reducing the zoom to fit is prohibited; collapse a sub-process instead (`SP-003` `PD-02`, `PD-03`) |
| **DG-07** | **Connectors do not cross where a route exists.** Where a crossing is unavoidable it uses a jump, and more than three crossings means the lane order is wrong (`SP-003` `PD-08`) |
| **DG-08** | **Nothing overlaps.** No node over a lane boundary, no label over a connector, no annotation over a node |
| **DG-09** | Alignment is to the grid. **A diagram whose nodes are eyeballed cannot be edited by a second author without drifting** |

### 4.3 Shape and colour semantics

> **`SP-003` §4.2 lists "colour carrying meaning" among the forbidden elements**, on the grounds
> that it fails `CG-011` accessibility. **This file does not soften that.** Meaning is carried by
> **shape, label and annotation**; colour may only reinforce.

| Element | Shape | Fill | Stroke | Reinforcing colour |
|---|---|---|---|---|
| **User task** | Rounded rectangle | `#FFFFFF` | `#212529` 2 px | — |
| **Service task** | Rounded rectangle **with a gear marker** | `#F8F9FA` | `#212529` 2 px | — |
| **Manual task** | Rounded rectangle **with a hand marker** | `#F8F9FA` | `#212529` 2 px | — |
| **Collapsed sub-process** | Rounded rectangle **with a `+` marker** | `#FFFFFF` | `#212529` 2 px | — |
| **Exclusive gateway** | Diamond **with an `×`** | `#FFFFFF` | `#212529` 2 px | — |
| **Parallel gateway** | Diamond **with a `+`** | `#FFFFFF` | `#212529` 2 px | — |
| **Start event** | Thin circle | `#FFFFFF` | `#212529` 2 px | — |
| **End event** | **Thick** circle | `#FFFFFF` | `#212529` 4 px | — |
| **Timer boundary event** | Circle with a clock | `#FFFFFF` | `#212529` 2 px, dashed | — |
| **Error boundary event** | Circle with a lightning glyph | `#FFFFFF` | `#212529` 2 px, dashed | `#DC3545` stroke permitted **in addition** |
| **Message event** | Circle with an envelope | `#FFFFFF` | `#212529` 2 px | — |
| **Data object** | Page with folded corner | `#FFFFFF` | `#495057` 1 px | — |
| **Text annotation** | Open bracket | none | `#495057` 1 px | — |
| **Pool — 1000FiX** | Container | `#FFFFFF` | `#212529` 2 px | — |
| **Pool — external party** | Container, **collapsed, with a hatched header band** | `#F8F9FA` | `#212529` 2 px | — |
| **Lane** | Horizontal band | alternating `#FFFFFF` / `#F8F9FA` | `#E9ECEF` 1 px | — |

| # | Rule |
|---|---|
| **DG-10** | **Every diagram is legible printed in monochrome on a branch printer.** `VB-004` §5 already states why: these are photocopied, faxed and re-printed at 51+ sites, and a design that depends on colour is illegible by the third copy |
| **DG-11** | **The `VB-008` status palette is not reused in diagrams.** `VB-008` gives meaning to colour in the product's status system; reusing those colours on a canvas creates a second meaning for the same hue and breaks both |
| **DG-12** | **`#39B1DF` is not used on a diagram at all.** At 2.46:1 on white it fails the SC 1.4.11 3:1 non-text threshold, so it cannot carry a stroke, a border or a marker (`VB-003` `BC-01`) |
| **DG-13** | Where colour reinforces — the permitted error-path red — the **shape or the label already carries the meaning without it**, and the diagram is checked with colour removed |
| **DG-14** | **Distinguishing external parties uses a hatch and a collapsed pool, not a colour**, so the distinction survives greyscale, photocopying and colour-blind vision |

### 4.4 Typography and the Bengali position

| Slot | Size | Weight | Rule |
|---|---:|---:|---|
| Diagram title | 16 px | 600 | Sentence case; states the process and its level |
| Pool / lane label | 13 px | 600 | The exact `05-04` role with its `Rnn` (`SP-003` `PD-06`) |
| Task label | 13 px | 500 | `<Verb> <object>`, ≤ 5 words (`SP-003` `PD-04`, `PD-05`) |
| Gateway label | 13 px | 500 | **A question with an enumerated answer** |
| Branch label | 12 px | 500 | **Every branch labelled** — `SP-003` forbids an unlabelled flow out of a gateway |
| Annotation | 12 px | 400 | Rule identifier and nothing else where possible |
| **Absolute floor** | **12 px** | — | Below this a diagram is decomposed, not shrunk |

| # | Rule |
|---|---|
| **DG-15** | **Text lives on a separate layer in the source and is never converted to outlines.** An outlined label cannot be corrected, searched, translated or read by a machine, and `SP-003` `PD-04` requires labels to come from `CG-004`, which means they will change |
| **DG-16** | Type is **Inter** (`VB-004` `T-02`); identifiers are monospaced (`VB-003` `TY-04`) |
| **DG-17** | **Diagrams are not redrawn in Bengali** — the decision is `SP-003` §4.11, taken with the Localisation Lead, on the grounds that the text is authoritative (`PD-01`) and redrawing 28 diagrams doubles maintenance for no comprehension gain. **The Bengali SOP text carries the translated step names**, and §4.6's text alternative is where a Bengali reader meets the flow |
| **DG-18** | **`DG-17` is a decision, not a default, and it is restated here so it is not quietly reversed.** If it is reversed, `DG-15`'s separate text layer is what makes the reversal affordable — which is why `DG-15` exists |
| **DG-19** | A label that does not fit its node is **shortened at the source** — in `CG-004` — or the node is enlarged. **It is never abbreviated on the canvas**, which creates a synonym `PD-04` prohibits |

### 4.5 Export and the source pairing

| Artefact | Format | Purpose |
|---|---|---|
| **Process (F1) source** | **BPMN 2.0 XML** | Diffable in version control; tool-portable |
| **All families — publication** | **SVG 1.1**, text as live text | Scales; accessible; small |
| Slides, print, embedding where SVG is unsupported | **PNG @2×** | Derived, never authored |
| Editable source where not BPMN | The native tool file | Delivered per `MM-001` `DL-02` |

| # | Rule |
|---|---|
| **DG-20** | **Every diagram is delivered as SVG, and F1 diagrams also as BPMN 2.0 XML.** A PNG-only diagram is rejected (`MM-001` `AS-06`) |
| **DG-21** | The SVG and the source live **beside the governing text, sharing its stem** — the `MD` convention of data beside specification (`SP-003` §4.11, Master Index §3.1, `CG-005` §5) |
| **DG-22** | **The text governs. Where the SVG and the SOP disagree, the SOP is right and the SVG is corrected** (`PD-01`) — never the reverse, and never by editing the text to match a picture |
| **DG-23** | SVG is **optimised but not mangled**: no embedded raster, no base64 payloads, no editor metadata, **and `<title>`/`<desc>` preserved** (§4.6). Most SVG optimisers strip them by default |
| **DG-24** | A diagram embedded in a document, a slide or a course is embedded **by reference to the registered asset**, never pasted. A pasted copy cannot be updated when the source changes (`MM-012` §4.4) |

### 4.6 Accessibility — the section diagram sets fail

`CG-011` §4.1 states the requirement in one line: a diagram gets a **short alt plus a text
description of the flow, usually a numbered list**. `SP-003` §4.11 says what that description is
for a process diagram: **the SOP's §5 step table**.

#### 4.6.1 The markup pattern

```html
<!-- Inline SVG -->
<svg role="img" aria-labelledby="dg-t1 dg-d1" viewBox="0 0 1280 720">
  <title id="dg-t1">Walk-in intake, level 2 process</title>
  <desc id="dg-d1">Seven steps across three roles, from customer arrival to
    device custody. The full step table follows this diagram.</desc>
  …
</svg>

<!-- SVG referenced through img -->
<img src="…/SP-007_walk_in_intake_l2.svg" role="img"
     alt="Walk-in intake, level 2 process — seven steps across three roles">
```

| # | Rule |
|---|---|
| **DG-25** | **Every published SVG carries a `<title>` and a `<desc>`, referenced by `aria-labelledby`, with `role="img"` on the `<svg>`.** Where the SVG is referenced through an `<img>`, the `alt` attribute carries the short name. This is the pattern that behaves most consistently across tested browser and screen-reader combinations, and it is verified in [`TS-016`](../13_Test_and_Acceptance_Content/TS-016_Accessibility_Test_Script_Pack.md), not assumed |
| **DG-26** | **The diagram is never the only carrier of its information** (`CG-011` `AT-06` applied to diagrams). The text alternative is: **F1** the SOP §5 step table · **F2** the stage table in `SP-001` · **F3** the layer and component list · **F4** the numbered message sequence · **F5** the entity and relationship table |
| **DG-27** | The text alternative is **the same artefact the diagram was derived from**, not a second description written to satisfy a checker. A separately written description drifts, and then two versions of the process exist |
| **DG-28** | Colour is never the only signal (§4.3); shape and label carry meaning; **the diagram is reviewed with colour removed** |
| **DG-29** | **Non-text contrast of every stroke, marker and boundary meets 3:1** against its fill (SC 1.4.11). `#212529` on `#FFFFFF` measures 15.43:1 and `#495057` measures 8.18:1; the 1 px `#E9ECEF` lane divider at 1.19:1 is **decorative only and carries no meaning** |
| **DG-30** | **Text in the SVG is live text, never outlined** (`DG-15`, SC 1.4.5). It resizes to 200% without loss (SC 1.4.4) |
| **DG-31** | A diagram used as a **navigation or interactive element** — a clickable architecture map in the developer portal — meets keyboard and focus requirements, and each interactive region has an accessible name. **Where that cannot be delivered, the diagram is static and a list carries the navigation** |

### 4.7 Diagrams in print, in slides and on a wall

| Surface | Constraint | Rule |
|---|---|---|
| **A4 print** | Monochrome, 1 pt rules, no fills (`VB-004` §5) | The SVG renders to `VB-004` geometry; a diagram that needs colour to be read is redrawn |
| **A4 landscape** | Permitted for a wide L1 map with a stated reason (`VB-004` `F-04`) | Declared in the artefact |
| **Slides** ([`CM-010`](../16_Change_Management_and_Comms/CM-010_Town_Hall_and_Roadshow_Content.md)) | Read from the back of a room | **Type floor rises to 18 px equivalent**; a slide carries **at most one L1 diagram or one collapsed L2**, never a full process |
| **Job aid** ([`TR-022`](../08_Training_and_Enablement/08B_Course_Packs/TR-022_Job_Aid_and_Quick_Reference_Library.md)) | A5 or card, often laminated, often monochrome | Simplified derivative, **registered as a separate asset**, not a shrunk original |
| **Wall / branch poster** | Viewed at 2 m | Derivative with its own type scale; the same source |
| **`P03` at 1366 × 600** | `VB-003` `D-01` | §4.2 canvas is sized for this case |

| # | Rule |
|---|---|
| **DG-32** | **A derivative for a different surface is a registered asset in its own right** (`MM-012`), linked to its parent. Otherwise the wall poster and the SOP diverge and nobody notices |
| **DG-33** | **A diagram is never shrunk below its type floor to fit a slide.** `CM-010` §4 already treats an unreadable slide as a defect; the fix is to collapse the diagram, not the type |

### 4.8 Deliverable specification

**The `CG-009` §3 required addition for Category 19.**

| Attribute | Specification |
|---|---|
| **Master format** | **SVG 1.1** (all families) **+ BPMN 2.0 XML** (family F1) |
| **Derived formats** | PNG @2× for slides, print embedding and clients without SVG |
| **Dimensions** | 1280 px nominal canvas width; fits **1366 × 600** rendered (`VB-003` `D-01`) |
| **Colour** | sRGB; **greyscale-survivable**; `#212529`, `#495057`, `#FFFFFF`, `#F8F9FA`, `#E9ECEF`; `#DC3545` reinforcement only; **no `#39B1DF`** |
| **Typography** | Inter; 12 px floor; **live text, never outlined** |
| **Compression / weight** | **≤ 120 KB SVG**; PNG @2× ≤ 400 KB |
| **Accessibility** | `role="img"` + `<title>` + `<desc>` + `aria-labelledby`; **text alternative is the owning step/stage/entity table** |
| **Metadata** | XMP `dc:title`, `dc:description`, `dc:relation` = owning content ID, family, level, source-of-truth file |
| **Naming** | `MM-012` §4.3, sharing the stem of the governing text (`DG-21`) |
| **Pairing** | Delivered **with** its governing text; a diagram with no matching text is rejected (`SP-003` §4.2 forbidden list) |
| **Editable source** | Native tool file where not BPMN (`MM-001` `DL-02`) |

### 4.9 Rules — summary

| # | Rule |
|---|---|
| **DG-34** | This standard is enforced at `SP-003` §4.10's fifteen-question review; **a non-conformant diagram does not reach `Review`** |
| **DG-35** | A diagram may **cite** identifiers and may **never mint** them (`SP-003` `PD-14`, `CG-005` `ID-07`) |
| **DG-36** | **A diagram is versioned with its governing text and carries the same version.** A diagram at v1.0 beside an SOP at v1.2 is a defect visible to any reader |
| **DG-37** | **Every diagram names its source of truth in its `<desc>`** — the SOP, the architecture document or the data model it derives from |
| **DG-38** | A change to this file's §4.3 semantics is **MAJOR** (`CG-006` §6.2) and requires an impact assessment across the drawn set |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| [`SP-003_To_Be_Process_Design_Standard_and_Notation.md`](../06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-003_To_Be_Process_Design_Standard_and_Notation.md) | The notation this file makes visible; `PD-01` text-authoritative; §4.11 tooling and the Bengali decision |
| [`SP-001_Process_Architecture_and_Value_Stream_Map.md`](../06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-001_Process_Architecture_and_Value_Stream_Map.md) · [`SP-002_As_Is_Process_Baseline_Register.md`](../06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-002_As_Is_Process_Baseline_Register.md) | Family F2; the L0/L1 structure and the site clusters `PD-09` refers to |
| [`SP-004_Approval_Matrix_and_Delegation_of_Authority.md`](../06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-004_Approval_Matrix_and_Delegation_of_Authority.md) · [`SP-005_Escalation_Matrix.md`](../06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-005_Escalation_Matrix.md) · [`SP-006_Segregation_of_Duties_Register.md`](../06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-006_Segregation_of_Duties_Register.md) | The identifiers annotations cite rather than restate (`PD-13`) |
| [`CG-011_Accessibility_Content_Standard.md`](../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md) | §4.1 diagram alternative; `CL-01`; `ST-01`…`ST-08` structure |
| [`CG-004_Terminology_and_Controlled_Vocabulary_Standard.md`](../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md) | Every label on a canvas (`PD-04`, `DG-19`) |
| [`CG-008_Content_Definition_of_Done_and_QA_Checklist.md`](../00_Content_Governance_and_Standards/CG-008_Content_Definition_of_Done_and_QA_Checklist.md) | Where `SP-003` §4.10 is referenced as a gate |
| [`VB-003_Brand_Application_in_Enterprise_UI.md`](../01_Voice_Brand_and_Design_Content/VB-003_Brand_Application_in_Enterprise_UI.md) | `D-01` 1366 × 600; the contrast findings behind `DG-12` |
| [`VB-004_Print_and_PDF_Brand_Template_Standard.md`](../01_Voice_Brand_and_Design_Content/VB-004_Print_and_PDF_Brand_Template_Standard.md) | Print rendering, monochrome and the no-fill position |
| [`VB-008_Status_Colour_and_Label_Semantics_Register.md`](../01_Voice_Brand_and_Design_Content/VB-008_Status_Colour_and_Label_Semantics_Register.md) | The palette `DG-11` deliberately does **not** reuse |
| [`VB-009_Bengali_Typography_and_Brand_Standard.md`](../01_Voice_Brand_and_Design_Content/VB-009_Bengali_Typography_and_Brand_Standard.md) · [`BN-006_Bengali_Typography_Font_and_Numeral_Standard.md`](../11_Localisation_Bengali/BN-006_Bengali_Typography_Font_and_Numeral_Standard.md) | The floors that would apply if `DG-17` were reversed |
| [`MD-027_Status_and_Lifecycle_State_Label_Register.md`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-027_Status_and_Lifecycle_State_Label_Register.md) · [`MD-028_Priority_Severity_and_SLA_Definition_Register.md`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-028_Priority_Severity_and_SLA_Definition_Register.md) | End-event labels (`PD-11`); timer durations cited, never typed inline |
| [`RP-007_Chart_Label_and_Visualisation_Standard.md`](../14_Reporting_Analytics_and_KPI/RP-007_Chart_Label_and_Visualisation_Standard.md) | The boundary — charts are not diagrams |
| [`AP-003_Domain_Event_Catalogue_Descriptions.md`](../15_Integration_and_Developer_Content/AP-003_Domain_Event_Catalogue_Descriptions.md) · [`AP-004_Webhook_and_Callback_Integration_Guide.md`](../15_Integration_and_Developer_Content/AP-004_Webhook_and_Callback_Integration_Guide.md) | Family F4 sequence diagrams and their message names |
| [`CM-010_Town_Hall_and_Roadshow_Content.md`](../16_Change_Management_and_Comms/CM-010_Town_Hall_and_Roadshow_Content.md) | §4.7 slides — **it cites this file and records `MM` as holding zero files** |
| [`TR-003_Course_Design_Standard_and_Storyboard_Template.md`](../08_Training_and_Enablement/08A_Framework/TR-003_Course_Design_Standard_and_Storyboard_Template.md) · [`TR-022_Job_Aid_and_Quick_Reference_Library.md`](../08_Training_and_Enablement/08B_Course_Packs/TR-022_Job_Aid_and_Quick_Reference_Library.md) | Diagrams in storyboards and job aids (`DG-32`) |
| [`KB-001_Knowledge_Architecture_and_Tagging_Standard.md`](../07_Knowledge_Base_and_Technical_Library/KB-001_Knowledge_Architecture_and_Tagging_Standard.md) | Diagrams in knowledge articles; the shared citation convention |
| [`TS-016_Accessibility_Test_Script_Pack.md`](../13_Test_and_Acceptance_Content/TS-016_Accessibility_Test_Script_Pack.md) | Where `DG-25` is verified rather than assumed |
| [`MM-001_Multimedia_Asset_Standard_and_Delivery_Specification.md`](MM-001_Multimedia_Asset_Standard_and_Delivery_Specification.md) · [`MM-002_Screenshot_Annotation_and_Redaction_Standard.md`](MM-002_Screenshot_Annotation_and_Redaction_Standard.md) · [`MM-010_PDF_and_Print_Template_Design_Specification.md`](MM-010_PDF_and_Print_Template_Design_Specification.md) · [`MM-012_Digital_Asset_Management_and_Naming_Standard.md`](MM-012_Digital_Asset_Management_and_Naming_Standard.md) | Class A4 delivery; the screenshot-versus-diagram choice; print rendering; registration |
| `05-02` · `05-03` · `05-04` · `05-05` | Families F3, F4, F5; roles for lanes; rules and automations cited on annotations |

| Depended on by |
|---|
| All 28 SOPs in `06B` · `SP-001` · the architecture and integration sets · `CM-010` decks · `TR-*` storyboards and job aids · `AP-001` developer portal · the ISO 9001 process library |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **At every wave boundary while `06B` is being authored**, then annually — matching `SP-003` §6 so the pair does not drift |
| Trigger for out-of-cycle review | A `SP-003` notation change · a BPM or diagram tool adoption (`SP-003` DoD records tooling as pending) · an accessibility finding · a reversal of `DG-17` · a new diagram family |
| Owner | **Business Process Lead with Design System.** `SP-003` is owned by Business Process alone; **this file is co-owned because half of it is a design-system concern** |
| Approver | Content Design Lead with Business Process Lead |
| Enforcement | `SP-003` §4.10's fifteen-question review, extended by §4.8's deliverable table; a non-conformant diagram does not reach `Review` (`DG-34`) |
| Effectiveness measure | Diagrams rejected at `SP-003` §4.10, by rule identifier; and **the count of diagrams with no text alternative — target zero** |
| Change log | [`RF-006`](../99_Reference_and_Registers/RF-006_Content_Decision_Log_and_Change_Control.md) — **written; Category 99 completed 2026-08-18**. Every decision under this file is logged there |

---

## 7. Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **No diagram tooling is procured and no BPMN validation profile is configured.** `SP-003`'s own Definition of Done records this as pending. §4.2, §4.5 and §4.6 describe a pipeline — grid-snapped geometry, BPMN 2.0 XML export, SVG with preserved `<title>`/`<desc>` — that **no chosen tool has been shown to produce**, and most SVG optimisers strip exactly the elements `DG-23` requires | Business Process Lead with Platform Engineering | **W1 — before the first L1 diagram** |
| **O-02** | **`DG-25`'s SVG accessibility pattern carries `class: P3`.** It is corroborated practitioner guidance, not a verified observation on this programme's stack. `CG-012` `EV-02` permits P3 for context and not as the sole basis of a capability claim. **It converts to P1 on the `TS-016` screen-reader pass**, which `TS-016` `O-07` already records as having no owning media specification — this file is that specification, and the pass still has no Bengali-speaking tester (`CG-011` §8.2) | Accessibility reviewer *(unnamed)* with QA | **W2 — before the first diagram set publishes** |
| **O-03** | **`DG-17` — Bengali diagrams not produced — was taken in `SP-003` §4.11 and is restated here, but 28 of 34 `SP` files are bilingual and the decision is not recorded in `RF-006`.** `CG-010` `RD-01` requires language decisions to be logged there. **[`RF-006`](../99_Reference_and_Registers/RF-006_Content_Decision_Log_and_Change_Control.md) now exists** — Category 99 completed 2026-08-18 — **so the decision must be entered into it.** A decision this consequential surviving only inside two files' §4 is exactly the `AF-04` shape, and it is now avoidable rather than merely regrettable | Localisation Lead with Business Process Lead | **W1** |
| **O-04** | **No accessibility reviewer is named** for §4.6 — the **sixth** file to record it, after `TR-003` `O-02`, `HC-002` `O-04`, `HC-016` `O-04`, `MM-001` `O-06` and `MM-002` `O-04` | Content Design Lead | **W1** |
| **O-05** | **Families F3, F4 and F5 have their notation authority outside the content repository** — `02-05`, `05-03` and `05-02` — and **none of those documents states a visual convention.** This file supplies one; if Enterprise Architecture disagrees, it must say so before the architecture set is drawn, not after | Enterprise Architecture | **W1** |
| **O-06** | **`CM-010` records that Category 19 holds zero files** and cites `MM-003` for slide diagram notation. §4.7 now answers it, **but `CM-010`'s own wave is earlier than the first diagram set**, and `AUDIT-018` `EO-03` asked that the register-wide sequencing basis be corrected once rather than patched per file. Recorded, not patched | Programme Content Lead | W2 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md` — six sections in order; the `CG-009` `MM` deliverable table at §4.8; §7 added per category convention
- [x] Five diagram families defined, each with its notation authority named and no notation invented here
- [x] **`SP-003`'s text-authoritative decision (`PD-01`) carried through rather than re-litigated**
- [x] Canvas sized to the 1366 × 600 constraint `VB-003` `D-01` sets, with over-size treated as a decomposition failure
- [x] **Shape-and-label semantics specified so that colour carries nothing** — `SP-003`'s forbidden-element rule made concrete
- [x] Every colour value checked against the `VB-003` §3 measured ratios; `#39B1DF` excluded with the ratio stated
- [x] **Live text required and outlining prohibited, which is what makes label change and any future Bengali reversal affordable**
- [x] The Bengali not-redrawn decision restated with its owner and its rationale, and flagged as unlogged
- [x] **Export contract requires SVG plus BPMN XML; PNG-only delivery rejected**
- [x] **Accessibility pattern given as markup, with the text alternative bound to the artefact the diagram derives from rather than to a separate description**
- [x] Non-text contrast checked; the decorative-only divider identified by ratio
- [x] Surface derivatives (slide, job aid, poster, print) required to be registered assets
- [x] All internal links resolve
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [x] English-only per `CG-010` §3.2
- [ ] **`O-01` diagram tooling unprocured — outstanding; the pipeline is unproven**
- [ ] **`O-02` SVG accessibility pattern unverified on this stack — outstanding, `class: P3`**
- [ ] **`O-03` the Bengali diagram decision is unlogged — outstanding; `RF-006` now exists and the entry has not been made**
- [ ] Named approvers recorded — **pending Content Design Lead and Business Process Lead**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
