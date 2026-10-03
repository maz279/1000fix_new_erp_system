---
id: CG-011
title: Accessibility Content Standard
project: 1000FiX ERP System v2.0
content_type: Standard
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Content Design Lead
author: Content Design with Accessibility reviewer
reviewers: [Programme Content Lead, Localisation Lead, Design System, QA Lead]
approver: Programme Content Lead
purpose: >
  States the accessibility obligations that content authors — not developers — must discharge.
  WCAG 2.1 AA is a contractual standard under 04-00 PS-04 and 05-06 NFR-073. Most WCAG failures
  are content failures: a missing alt text, a link labelled "click here", an error message that
  names no remedy, a heading level skipped, colour used as the only signal. No amount of
  correct code fixes any of them.
traces_to: [04-00 PS-04, 05-06 NFR-073, 05-06 NFR-016, 05-06 NFR-074, CG-003, CG-010, TS-016, MM-002]
priority: P1
wave: W1
bilingual: no
bn_counterpart: n/a
sources:
  - source: W3C Web Content Accessibility Guidelines (WCAG) 2.1, Level AA success criteria
    verified: 2026-08-15
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §3 PS-04 — WCAG 2.1 AA accessibility, all web portals
    verified: 2026-08-15
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 §5 NFR-073, NFR-074 and §11 accessibility test cadence
    verified: 2026-08-15
  - source: NVDA screen reader Bengali support via eSpeak synthesiser — Centre for Internet and Society, Bangla eSpeak with NVDA
    verified: 2026-08-15
supersedes: none
review_due: 2027-02-15
---

# CG-011 — Accessibility Content Standard

> **`PS-04` makes WCAG 2.1 AA contractual across all web portals, and `05-06` NFR-073 restates
> it as a `P1` non-functional requirement. `05-06` §11 requires an automated scan plus a manual
> audit before each portal release.**
>
> A significant share of AA failures cannot be fixed in code. They are decisions an author
> makes: what the alt text says, whether the link text describes the destination, whether the
> error message offers a remedy, whether the heading hierarchy reflects the structure. **This
> standard assigns those decisions to content and makes them checkable.**

---

## 1. Scope

| In scope | Out of scope |
|---|---|
| Text alternatives authors write | Contrast ratios, focus indicators, target sizes — design (`VB-006`) |
| Link text, heading structure, labels, instructions | Keyboard navigation, focus order implementation — engineering |
| Error message content and remedy | Programmatic error association — engineering |
| Reading level and plain-language obligations | Reflow, orientation, text spacing — design and engineering |
| Table structure in authored content | ARIA implementation — engineering |
| Bengali accessibility considerations | Screen-reader engine behaviour — a known limitation, §8 |
| Accessibility of documents, help, training and knowledge | — |

**Applies to:** all 42 `UI` files, all 20 `HC` files, all 24 `TR` files, all 16 `KB` files, the
44 `DT` files where output is delivered digitally, and any content containing images, tables,
links or headings — which is nearly all of it.

---

## 2. The success criteria that are content decisions

WCAG 2.1 Level AA. These are the criteria a content author can pass or fail on their own.

| SC | Name | Level | What the author must do |
|---|---|:--:|---|
| **1.1.1** | Non-text Content | A | Provide a text alternative for every meaningful image, icon, chart and diagram; mark decorative images as decorative |
| **1.3.1** | Info and Relationships | A | Use real headings, real lists and real table headers — never visual formatting that only looks like structure |
| **1.4.1** | Use of Colour | A | Never make colour the only way information is conveyed |
| **2.4.2** | Page Titled | A | Give every page and document a title describing its topic or purpose |
| **2.4.4** | Link Purpose (In Context) | A | Make link text describe the destination |
| **2.4.6** | Headings and Labels | **AA** | Make headings and labels descriptive |
| **3.1.1** | Language of Page | A | Declare the page language |
| **3.1.2** | Language of Parts | **AA** | Mark language changes within content — critical on bilingual surfaces |
| **3.2.4** | Consistent Identification | **AA** | Name the same function the same way everywhere — this is `CG-004` |
| **3.3.1** | Error Identification | A | Identify the error in text and describe it |
| **3.3.2** | Labels or Instructions | A | Provide visible labels and instructions for every input |
| **3.3.3** | Error Suggestion | **AA** | Suggest a correction when one is known |
| **3.3.4** | Error Prevention (Legal, Financial, Data) | **AA** | Make legal, financial and data-changing submissions reversible, checkable or confirmable |

> **SC 3.2.4 is `CG-004`.** "Consistent Identification" is a WCAG requirement that the same
> function carries the same name across a site. The controlled vocabulary is therefore an
> accessibility control, not only a quality one. **A terminology defect is an AA failure.**

> **SC 3.3.3 is `BR-STD-04`.** "Error Suggestion" requires that a known correction be offered.
> `05-05` BR-STD-04 already requires every rule violation to state what is wrong and what to do.
> The two obligations coincide exactly.

> **SC 3.3.4 applies heavily here.** This ERP takes payments, issues invoices, approves
> estimates, submits warranty claims and processes payroll. Every one is a legal, financial or
> data submission requiring reversal, checking or confirmation.

---

## 3. Reading level and plain language

WCAG 2.1 has no AA reading-level requirement (SC 3.1.5 is AAA). This standard sets one anyway,
because the audience makes it necessary: 200–400 field technicians and 250,000+ monthly
customers with a wide range of literacy, reading on phones, often in a hurry.

| Audience | Target | Rationale |
|---|---|---|
| Customer-facing (`P01`, help, notifications, documents) | Comprehensible to a reader with 8 years of schooling | The general public |
| Field and branch staff (`P02`, `P09`, SOPs, knowledge) | Comprehensible to a technically trained reader; short sentences, no abstraction | Reading under time pressure, often outdoors |
| Corporate and partner users (`P04`, `P05`, `P08`) | Professional register; jargon permitted where it is the counterparty's own | They are specialists |
| Internal governance | No constraint | Specialist readers |

### 3.1 Plain-language rules

These extend `CG-003` §2 with accessibility intent.

| # | Rule |
|---|---|
| **PL-01** | One idea per sentence; maximum 25 words in UI, 30 in help |
| **PL-02** | Front-load the point. The first five words carry the meaning |
| **PL-03** | Expand every acronym on first use in each document — except `SLA`, `AMC`, `VAT`, `NID`, `TIN`, which the audience knows |
| **PL-04** | Prefer the common word to the precise-but-rare one, unless precision is legally required |
| **PL-05** | Never require the reader to hold more than one condition in mind at once. Split conditional sentences |
| **PL-06** | Use a table or list when the content has structure. Prose that hides a list is harder for everyone and much harder with a screen reader |
| **PL-07** | Instructions are numbered steps, one action each (`CG-003` L-04) |
| **PL-08** | Never rely on the reader having read a previous screen |

---

## 4. Text alternatives — SC 1.1.1

### 4.1 The decision tree

| Image type | Alternative |
|---|---|
| **Decorative** — adds no information | Marked decorative; empty alt. Say so explicitly in the content file so engineering does not guess |
| **Functional** — a button or link | Describe the **action**, not the picture: "Create service order", not "plus icon" |
| **Informative** — conveys a fact | Describe the fact in as few words as carry it |
| **Screenshot in help or training** | Describe what the reader should see and where, in the terms `CG-004` approves |
| **Chart or graph** | Short alt naming what it shows, plus a **long description or data table** carrying the actual values |
| **Diagram or process map** | Short alt plus a text description of the flow — usually a numbered list |
| **Photograph of a fault or repair step** | Describe the observable condition, not the aesthetics |

### 4.2 Rules

| # | Rule |
|---|---|
| **AT-01** | Every image in every content file has its alternative **authored in the content file**, never left to the implementer |
| **AT-02** | Alt text does not begin "Image of", "Picture of" or "Screenshot of" — assistive technology already announces the type |
| **AT-03** | Alt text is under 125 characters. Longer content goes in a long description |
| **AT-04** | Alt text uses `CG-004` approved terms |
| **AT-05** | On bilingual surfaces, alt text is bilingual. It is a user-visible string (`CG-010` §5) |
| **AT-06** | A chart is never the only carrier of its data. The table exists too (`RP-007`) |
| **AT-07** | Text in an image is duplicated in the alternative. Better: do not put text in images |
| **AT-08** | Screenshots use sample data with personal data redacted (`MM-002`, `CG-008` U-41) |

---

## 5. Error messages — SC 3.3.1, 3.3.2, 3.3.3

The convergence point of three obligations: WCAG AA, `BR-STD-04` and `PS-09`. Full mechanics in
`CG-003` §3; the accessibility-specific requirements are here.

| # | Rule | SC |
|---|---|---|
| **EA-01** | The error is identified **in text**. An icon, a red border or a colour change alone fails | 3.3.1, 1.4.1 |
| **EA-02** | The message names the **specific field** that failed, using its exact visible label | 3.3.1 |
| **EA-03** | Where a correction is known, it is stated. "Enter the date as DD/MM/YYYY" | 3.3.3 |
| **EA-04** | Where a correction is not known, the next action is stated — who to contact or what to try | `BR-STD-04` |
| **EA-05** | Every input has a **visible, persistent label**. Placeholder text is not a label; it disappears on focus | 3.3.2 |
| **EA-06** | Format requirements are stated **before** the user submits, not only after failure | 3.3.2 |
| **EA-07** | Legal, financial and data-changing submissions are reversible, checkable, or confirmed — this covers payments, estimate approvals, invoice posting, claim submission, payroll, and every destructive action | 3.3.4 |
| **EA-08** | Error text is written for announcement. A screen reader reads it out of visual context, so it must make sense alone | — |
| **EA-09** | The message is bilingual and both versions state the same remedy (`PS-09`) | 3.1.2 |

---

## 6. Structure — SC 1.3.1, 2.4.6

| # | Rule | SC |
|---|---|---|
| **ST-01** | Headings are a hierarchy. Levels increment by one and none is skipped | 1.3.1 |
| **ST-02** | A heading describes its section well enough that heading-only navigation makes sense | 2.4.6 |
| **ST-03** | Never use a heading for visual size, or bold text as a heading | 1.3.1 |
| **ST-04** | Lists are real lists. Never a paragraph with manual bullets | 1.3.1 |
| **ST-05** | Tables carry data, never layout | 1.3.1 |
| **ST-06** | Every data table has a header row, and a header column where rows are identified | 1.3.1 |
| **ST-07** | Complex tables get a caption and a summary. Better: split into simpler tables |
| **ST-08** | Every page and document has a descriptive, unique title | 2.4.2 |

---

## 7. Links, labels and colour

### 7.1 Link text — SC 2.4.4

| Do | Do not |
|---|---|
| See the [warranty claim process](.) | See [here](.) for the warranty claim process |
| Download the [service report](.) | [Click here](.) to download |
| [Bengali translation standard `BN-002`](.) | [Read more](.) |

| # | Rule |
|---|---|
| **LK-01** | Link text describes the destination and works out of context |
| **LK-02** | Banned link text: "click here", "here", "read more", "learn more", "this link", "more", a bare URL |
| **LK-03** | The same link text always leads to the same destination (SC 3.2.4) |
| **LK-04** | A link that opens a document or downloads a file says so, with format and size |
| **LK-05** | A link that leaves the ERP for an external site says so |

### 7.2 Colour — SC 1.4.1

| # | Rule |
|---|---|
| **CL-01** | Colour is never the only signal. A status shown only by colour fails |
| **CL-02** | Every status carries a **text label** alongside its colour (`MD-027`, `VB-008`) |
| **CL-03** | Content never instructs by colour alone: not "the red items", but "the overdue items, shown in red" |
| **CL-04** | Charts label series directly or provide a data table (`RP-007`) |
| **CL-05** | Required fields are marked in text as well as by any visual convention |

---

## 8. Bengali accessibility

`PS-03` makes the ERP Bengali-first on customer and field surfaces. `PS-04` requires WCAG 2.1 AA
on all web portals. **Both apply simultaneously**, and Bengali assistive-technology support is
materially less mature than English support. This section states what is achievable, what is a
known limitation, and how the limitation is managed rather than ignored.

### 8.1 Requirements

| # | Rule | SC |
|---|---|---|
| **BA-01** | Page and document language is declared as `bn-BD` on Bengali surfaces, `en` on English | 3.1.1 |
| **BA-02** | **Language changes within content are marked.** A Bengali sentence containing "Mushak 6.3" or a brand name in Latin script must mark the change, or a screen reader mispronounces it | **3.1.2** |
| **BA-03** | Do-not-translate items (`BN-004`) are the most common trigger for BA-02. Every such item in Bengali content is a language-part boundary |
| **BA-04** | Alt text, ARIA labels and screen-reader-only text are translated. They are user-visible strings (`CG-010` §5) |
| **BA-05** | Type size never falls below the `BN-006` minimum. Bengali conjuncts break at small sizes — a legibility failure before it is an accessibility one |
| **BA-06** | Text spacing adjustments must not break Bengali layout. Verified at the `BN-006` maxima |
| **BA-07** | Bengali content is written for **phonetic input users** (`NFR-074`). Search and matching accommodate spelling variation |
| **BA-08** | Numerals follow the `BN-007` policy consistently. Mixed numeral systems within a screen are announced inconsistently |

### 8.2 Known limitation, declared

Screen-reader support for Bengali exists — NVDA supports it through the open-source eSpeak
synthesiser, and Android TalkBack has Bengali support — but pronunciation quality, conjunct
handling and punctuation announcement are **less reliable than for English**.

**This programme's position:**

1. Bengali accessibility is **tested with real assistive technology** (`TS-016`), not assumed
   from a code review.
2. Where a limitation is in the screen-reader engine rather than in our content, it is
   **recorded in the accessibility statement** (`TP` equivalent, `LG-021` adjacent) rather than
   silently accepted.
3. Content is written to reduce dependence on engine quality: shorter sentences, fewer
   parenthetical asides, no reliance on punctuation to carry meaning, explicit language marking
   (BA-02).
4. **Bengali accessibility is never traded away** to make English accessibility easier. `PS-03`
   and `PS-04` both apply.

### 8.3 The bilingual accessibility trap

> A surface that is accessible in English and only partly accessible in Bengali is **not
> accessible**. The user who needs assistive technology in Bengali is exactly the user least
> able to switch to English.

Coverage is per surface per language (`CG-010` §5). Both languages pass, or the surface fails.

---

## 9. Accessibility by content type

| Content type | Additional requirement |
|---|---|
| `UI` UI copy | Alt and ARIA text authored in the pack; every error message meets §5; labels are visible and persistent |
| `HC` Help articles | Screenshots have alternatives describing what to see; steps are numbered; never "the button shown above" |
| `TR` Training | Videos carry captions and a transcript; slides are not the only carrier; exercises do not depend on colour |
| `KB` Knowledge | Safety warnings are text, never only an icon; diagrams have text descriptions of the flow |
| `DT` Documents | Digital PDFs are tagged with a heading structure and reading order; tables have headers; language is declared |
| `NT` Notifications | Meaning survives without images; subject alone conveys the essential fact |
| `RP` Reporting | Every chart has a data table; series labelled directly; colour is never the only encoding |
| `MM` Multimedia specs | Briefs state the accessibility deliverables — captions, transcripts, audio description, alt text — as acceptance criteria |

---

## 10. Verification

| Check | Method | When | Owner |
|---|---|---|---|
| Link text — no banned phrases | Automated (`CG-008` §6) | Every commit | Platform |
| Heading increment | Automated | Every commit | Platform |
| Alt text present for every image | Automated | Every commit | Platform |
| Alt text quality | Manual, at gate G1 | Per file | Content Design |
| Error messages state a remedy | Manual, at gate G1 | Per file | Content Design |
| Reading level | Sampled at gate G1 | Per file | Content Design |
| Colour not the only signal | Manual review | Per surface | Content Design + Design System |
| Language-part marking (BA-02) | Manual, at gate G4 | Per bilingual surface | Localisation |
| Screen-reader pass — English | `TS-016` | Before each portal release | QA |
| **Screen-reader pass — Bengali** | `TS-016` with a Bengali-speaking tester | Before each portal release | QA + Localisation |
| Automated WCAG scan | Per `05-06` §11 | Before each portal release | QA |
| Manual accessibility audit | Per `05-06` §11 | Before each portal release | QA |

### 10.1 Targets

| Measure | Target |
|---|---|
| WCAG 2.1 AA content-criteria failures at release | **Zero** |
| Images without a text alternative | **Zero** |
| Error messages without a stated remedy | **Zero** |
| Banned link text instances | **Zero** |
| Bengali surfaces released without a Bengali screen-reader pass | **Zero** |
| Reading-level sample failures | Under 10% |

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`CG-003_ERP_Product_Content_Style_Guide.md`](CG-003_ERP_Product_Content_Style_Guide.md) | Sentence structure, error-message mechanics, link text |
| [`CG-004_Terminology_and_Controlled_Vocabulary_Standard.md`](CG-004_Terminology_and_Controlled_Vocabulary_Standard.md) | SC 3.2.4 Consistent Identification |
| [`CG-010_Bilingual_Content_Policy.md`](CG-010_Bilingual_Content_Policy.md) | Which surfaces need Bengali accessibility |
| [`CG-008_Content_Definition_of_Done_and_QA_Checklist.md`](CG-008_Content_Definition_of_Done_and_QA_Checklist.md) | U-37 to U-41 |
| `VB-006` Design System Content Standards | Component-level copy and the visual criteria out of scope here |
| `VB-008` Status Colour and Label Semantics Register | CL-02 |
| `UI-004` Validation & Error Message Library | Where §5 is applied at scale |
| `UI-010` Accessibility Text Library | The alt, ARIA and screen-reader-only strings |
| `BN-006` Bengali Typography Standard | BA-05, BA-06 |
| `TS-016` Accessibility Test Script Pack | How §10 is executed |
| `MM-002` Screenshot, Annotation and Redaction Standard | AT-08 |
| `05-06` §5, §11 | NFR-073, NFR-074 and the test cadence |

---

## 12. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Thirteen WCAG 2.1 AA criteria assigned to content, reading-level targets by audience, text-alternative decision tree, error-message accessibility rules, link and colour rules, Bengali accessibility including a declared engine limitation, verification with zero-failure targets | Programme Content Lead (pending) |

---

## Definition of Done

- [x] Front matter complete
- [x] Success criteria that are content decisions are enumerated and assigned
- [x] The `CG-004` / SC 3.2.4 and `BR-STD-04` / SC 3.3.3 convergences are made explicit
- [x] Reading-level targets set per audience rather than one blanket number
- [x] Bengali accessibility addressed, including a declared and managed engine limitation
- [x] Verification methods distinguish automated from manual, with named owners
- [x] Targets are numeric
- [x] All internal links resolve
- [x] Bengali counterpart — n/a; internal governance
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
