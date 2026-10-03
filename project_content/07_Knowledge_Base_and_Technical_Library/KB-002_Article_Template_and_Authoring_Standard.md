---
id: KB-002
title: Article Template and Authoring Standard
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-16
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Knowledge Manager
author: Knowledge Manager with Content Design and Technical Services
reviewers: [Quality Manager, Technical Director, HSE Lead, Localisation Lead, Content Design Lead]
approver: Quality Manager
content_class: C
purpose: >
  The structure, writing rules, safety-warning convention and evidence requirements that every
  knowledge article must satisfy, plus the capture-to-publication path that turns a three-minute
  Bengali voice note from a technician at a bench into a reviewed, translatable article. Knowledge
  authored by 80–150 senior technicians with no common shape cannot be reviewed, cannot be
  translated, and cannot be trusted by the person who reads it under time pressure.
traces_to: [M61, M31, M22, M23, P02, KB-001, KB-013, KB-015, CG-003, CG-008, CG-011, BN-003]
priority: P2
wave: W2
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M61 §5.1 FR-KMS-001…012, §5.3 FR-KMS-023…029 — article types, three-minute capture, improvement queue, original words retained
    verified: 2026-08-16
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M61 §9 BRU-KMS-02, -03, -08, -09 — reviewer ≠ author, safety approval gate, rough captures never discarded, original words retained
    verified: 2026-08-16
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M61 §4 Design position — capture happens at the bench, in Bengali, on a phone; a system requiring desk-written English prose will capture nothing
    verified: 2026-08-16
    class: P1
  - source: ANSI Z535.6 safety-information signal-word convention (DANGER / WARNING / CAUTION / NOTICE) as applied to product and procedure documentation
    verified: 2026-08-16
    class: P2
  - source: ISO 9001:2015 clause 7.5 documented information — creation, update, identification, review and approval for suitability
    verified: 2026-08-16
    class: P1
supersedes: none
review_due: 2027-02-16
---

# KB-002 — Article Template and Authoring Standard

> **`KB-001` says how an article is indexed. This file says what is inside it.**
>
> The two are deliberately separate because they change at different rates and are owned by
> different concerns. Tagging changes when the master-data registers change. Article structure
> changes when we learn something about how technicians actually read under pressure.

---

## 1. Purpose

`M61` §4 records the design position that governs this entire file:

> *"Capture happens at the bench, in Bengali, on a phone. The dominant author is a specialist
> technician who has just solved something difficult, not a technical writer… A knowledge system
> that requires an author to sit at a desk and write English prose will capture nothing — this is
> the most common failure mode of corporate knowledge bases and the one most likely to defeat this
> module."*

An authoring standard therefore has to do two contradictory things at once. It must impose enough
structure that 150–250 articles by 80–150 authors are reviewable, translatable and safe. And it
must impose **none of that structure at the moment of capture**, or nothing will ever be captured.

This file resolves the contradiction by separating **capture** (unstructured, three minutes,
Bengali, voice and photographs) from **authoring** (structured, reviewed, bilingual), and putting
a named human — not the contributor — in between.

**The consequence of absence (`CP-03`).** Without this standard, a technician's rough note and a
brand-authorised board-level procedure are the same kind of object with the same weight. Reviewers
have nothing to review against. Translators receive text with no predictable structure. And a
safety warning appears wherever the author happened to think of it, which on a lithium or
refrigerant procedure is a physical-injury exposure, not a style defect.

---

## 2. Scope

**In scope:** the universal article skeleton; required sections by article type; the safety-warning
signal-word convention and its placement rules; writing rules `AU-01`…`AU-20`; step-construction
rules; media and evidence rules; bilingual authoring rules; the completeness score; the review
gates and who may pass them; and the capture-to-publication path including the improvement queue.

**Out of scope:**

| Subject | Owned by |
|---|---|
| Tagging, facets, codes, article types as an indexing concern | [`KB-001_Knowledge_Architecture_and_Tagging_Standard.md`](KB-001_Knowledge_Architecture_and_Tagging_Standard.md) |
| Review intervals, staleness, retirement | [`KB-015_Knowledge_Review_Currency_and_Retirement_Policy.md`](KB-015_Knowledge_Review_Currency_and_Retirement_Policy.md) |
| The hazard data that safety blocks cite | [`KB-013_ESD_Chemical_and_Battery_Safety_Data.md`](KB-013_ESD_Chemical_and_Battery_Safety_Data.md) |
| Product-wide voice, tense, person and capitalisation | [`../00_Content_Governance_and_Standards/CG-003_ERP_Product_Content_Style_Guide.md`](../00_Content_Governance_and_Standards/CG-003_ERP_Product_Content_Style_Guide.md) |
| Approved terminology and banned synonyms | [`../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md`](../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md) |
| Bengali typography, numerals and technical term base | `VB-009`, `BN-003` |
| Help-article structure for customer self-service | `HC-002` |
| Diagnostic tree node construction | [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-033_Diagnostic_and_Triage_Decision_Tree_Library.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-033_Diagnostic_and_Triage_Decision_Tree_Library.md) `DT-04` |

> **This standard governs knowledge articles only.** The `KB-*` files in this repository are
> *content specifications* and conform to `_templates/`, not to the article skeleton below. The
> skeleton applies to the `KNW-` objects those specifications describe. Confusing the two produces
> a category of files that conform to nothing.

---

## 3. Audience

| Audience | Role in authoring | Volume |
|---|---|---|
| **R12 Specialist Technician** | Primary contributor. Captures at the bench; reviews within competence | 15–30 |
| **R10 Senior Technician** | Contributor and reviewer | 80–150 |
| **R11 Junior Technician** | Reader and feedback provider; may capture | 120–250 |
| **R09 Workshop Supervisor** | Reviewer and approver within own workshop's domain | 20–40 |
| **R32 Quality Manager** | Approves safety, warranty and brand-procedure content; owns this standard | 2–4 |
| **Technical Library Owner** | Runs the improvement queue; structures rough captures without discarding them | 1 |
| **Localisation Lead** | Translates and validates in context | 1 |
| **HSE Lead** | Approves every safety block on hazard-class content | 1 |

---

## 4. Content

### 4.1 Three authoring paths, one output

| Path | Who starts it | Input | Time | Ends as |
|---|---|---|---|---|
| **A — Capture in the flow of work** | R10–R12 on `P02`, prompted at job completion | Voice note in Bengali, photographs already on the job, rough text | **Under 3 minutes** (`M61` FR-KMS-024) | A `CAPTURED` record in the improvement queue |
| **B — Structured authoring** | R12, R09, R32 or the Technical Library Owner | A blank article of a declared type | 30–120 minutes | A `DRAFT` conforming to §4.2 |
| **C — Derived** | System, from `M23` verified CAPA fixes or `M09` recurring claim-rejection causes | An existing record | Automatic | A pre-filled `DRAFT` (`M61` AUT-KMS-15/16) |

**`AU-01` — Path A imposes no structure whatsoever.** No required fields beyond what the job
already supplies. No English. No spelling standard. No section headings. Every requirement in
§4.2 onward applies from the moment the capture enters the improvement queue and **not before**.

**`AU-02` — the contributor's original words are retained verbatim on the article, permanently**
(`M61` §9 `BRU-KMS-09`). They are not deleted when the structured version is written. They are
shown to the reviewer, retained in `fix.knowledge.article.version.original_capture_text`, and
visible to the contributor so that a technician can see their own words survived contact with an
editor. This single rule is why senior technicians will keep contributing after the first time.

**`AU-03` — a rough capture is never rejected for being rough** (`BRU-KMS-08`). It may be merged,
deprioritised or found to duplicate an existing article. It is never discarded.

### 4.2 The universal article skeleton

Every `KNW-` article carries these blocks in this order. Blocks marked ● are mandatory for every
type; ○ are type-dependent per §4.3.

| # | Block | ●/○ | Content | Rule |
|---:|---|:--:|---|---|
| 1 | **Identity** | ● | Code, type, version, state, owner, review due, the eight `KB-001` facets | `KA-05` |
| 2 | **Title** | ● | Model or scope + observable symptom + confirmed cause. Never a question, never a bare noun | `AU-04` |
| 3 | **Applicability** | ● | Exactly what this applies to and — explicitly — what it does not | `AU-05` |
| 4 | **Safety** | ● | Signal-word block(s) per §4.4. **Always before any procedure** | `AU-06` |
| 5 | **Symptoms** | ○ | Symptom codes (`SYM-`) with EN and BN descriptions as the customer or technician states them | `AU-07` |
| 6 | **Likely causes** | ○ | Ranked, with observed frequency and the test that confirms each | `AU-08` |
| 7 | **Tools and equipment** | ○ | `MD-046` equipment codes; consumables; anything the reader must have before starting | `AU-09` |
| 8 | **Parts** | ○ | `MD-022` part codes, OEM/compatible class, quantity, substitution notes | `AU-10` |
| 9 | **Diagnostic procedure** | ○ | Numbered steps: action → expected result → if not | `AU-11` |
| 10 | **Repair procedure** | ○ | Numbered steps with tool, part, torque or specification per step | `AU-11` |
| 11 | **Verification and QC** | ● | The test that proves it worked, its pass criterion, and where the result is recorded | `AU-12` |
| 12 | **Resolution coding** | ○ | Which `RES-` code to record, and when each applies | `AU-13` |
| 13 | **Common mistakes** | ● | What people get wrong here. `M61` FR-KMS-011 makes this a required section | `AU-14` |
| 14 | **Escalation** | ● | When to stop, to whom, with what evidence | `AU-15` |
| 15 | **Sources and currency** | ● | Where the guidance came from, verified date, next review | `AU-16` |

> **Block 13 is the one most often argued about and the one that pays for itself fastest.**
> `M61` FR-KMS-011 lists it among the required sections precisely because a procedure tells you
> the right path and a common-mistakes block tells you the wrong ones people actually take. In a
> workforce with 120–250 junior technicians and high turnover, the second is worth more.

### 4.3 Required blocks by article type

| Type | 5 Symptoms | 6 Causes | 7 Tools | 8 Parts | 9 Diagnostic | 10 Repair | 12 Coding |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| `procedure` | ○ | ○ | ● | ● | ○ | ● | ● |
| `fault_fix` | ● | ● | ● | ● | ● | ● | ● |
| `technique` | — | — | ● | ○ | — | ● | ○ |
| `tool_guide` | — | — | ● | — | ○ | ○ | — |
| `safety_note` | ○ | ○ | ○ | — | — | ○ | — |
| `known_issue` | ● | ● | ○ | ○ | ● | ○ | ● |
| `faq` | ○ | — | — | — | — | — | — |
| `how_to` | — | — | ○ | — | — | ● | — |
| `reference_card` | ○ | — | — | — | ○ | ○ | ○ |

● required · ○ include where applicable · — omit

**`AU-17` — completeness is scored, not merely checked.** `M61` FR-KMS-011 requires the system to
score completeness. The score is the proportion of *required* blocks that are non-empty and pass
their block rule. An article below **80%** cannot be submitted for review. An article at 100% is
not thereby correct — completeness is a floor, not a quality measure, and §4.10 review is where
correctness is established.

### 4.4 Safety-warning convention

Signal words follow the ANSI Z535.6 hierarchy, which is the convention every equipment manual a
1000FiX technician has ever read already uses. **Do not invent a local scheme.**

| Signal word | Means | Use when | Rendering |
|---|---|---|---|
| **⛔ DANGER** | Will cause death or serious injury if not avoided | Live mains work, lithium thermal runaway in progress, refrigerant under pressure near ignition | Red band, full width, first thing on the article |
| **⚠ WARNING** | Could cause death or serious injury | Working near stored energy, capacitor discharge, battery puncture risk, refrigerant handling, working at height | Amber band, before the relevant procedure |
| **⚠ CAUTION** | Could cause minor or moderate injury | Sharp edges, hot surfaces, ESD exposure to the technician, chemical contact | Yellow band, at the step |
| **NOTICE** | Property or data damage, no personal injury | Will void warranty, will erase customer data, will damage the board | Grey band, at the step |

**Placement rules**

| # | Rule |
|---|---|
| **AU-06a** | Every safety block appears **before** the procedure it protects, never after and never in a footer |
| **AU-06b** | `DANGER` blocks appear at the very top of the article, before applicability |
| **AU-06c** | Each block states, in order: **the hazard · the consequence · the avoidance action** — three parts, always all three |
| **AU-06d** | A safety block is never the only content of a step; the step still says what to do |
| **AU-06e** | Any article with `hazard_class` other than `none` **must** carry at least one block and a link to the relevant `KB-013` section (`KA-07`) |
| **AU-06f** | Safety blocks are translated by a human, in context, and re-approved by HSE after translation. Machine translation of a safety block is **prohibited** (`CG-010`) |
| **AU-06g** | An author may not weaken or remove a safety block written by another author. Escalate to HSE instead |

> **Why `AU-06c` is written as three parts.** "Be careful with the battery" is not a warning; it
> is an anxiety. "A punctured lithium cell can enter thermal runaway and ignite within seconds
> (hazard + consequence). Isolate the device in the steel battery container before any further
> work (avoidance)." is a warning. The three-part form is what makes the difference testable at
> review.

### 4.5 Writing rules

| # | Rule | Why |
|---|---|---|
| **AU-04** | Titles state scope + observable symptom + confirmed cause. `"Latitude 5420 — no power, 3.3 V rail short at load switch"`, not `"Laptop power problem"` | Titles are what search ranks and what a technician scans in a list of nine results |
| **AU-05** | Applicability states what is *excluded*, not only what is included | The commonest article failure is being applied to an adjacent model it does not fit |
| **AU-07** | Symptoms are written as the person *states* them, not as the taxonomy names them, with the `SYM-` code alongside | A technician searches in their own words; `KB-001` §4.5 `symptom_phrase_bn` exists for the same reason |
| **AU-08** | Causes are ranked by observed frequency, and each names its confirming test | An unranked cause list is a list of everything that could ever be wrong |
| **AU-09** | Tools name `MD-046` equipment codes where the tool is a controlled instrument | Ties the article to calibration status (`KB-012`) |
| **AU-10** | Parts name `MD-022` codes and the `part_class` (`oem` / `oem_equivalent` / `compatible` / `refurbished`) | `part_class` affects warranty and claim eligibility. Naming a part without its class is how a claim gets rejected |
| **AU-11** | One action per step. A step containing "and" is usually two steps | Steps are read one at a time, often one-handed, on a phone |
| **AU-12** | Verification states a **pass criterion with a number or an observable state**, and where it is recorded | "Check it works" is not a verification |
| **AU-13** | Resolution coding names the `RES-` code and when each applies, never "code as appropriate" | `RES-01` blocks job completion without a code; the article is where the technician learns which |
| **AU-14** | Common mistakes are written from real rework and claim-rejection data where it exists, not imagined | Sources: `M31` rework records, `M09` claim rejections, `M23` non-conformances |
| **AU-15** | Escalation names **who**, **when** and **what evidence** — all three | An escalation route with no evidence requirement produces escalations that bounce |
| **AU-16** | Every factual, statutory or specification claim carries a source and a verification date (`CG-012`, `CM-R8`) | A torque figure or a voltage tolerance with no source is a guess wearing a number |
| **AU-18** | Present tense, imperative mood, second person, sentence case — per `CG-003` | One product voice across twelve surfaces |
| **AU-19** | Approved terms only; banned synonyms per `CG-004`, Bengali technical terms per `BN-003` | "Job", "ticket", "order" and "case" cannot all mean one thing |
| **AU-20** | No brand-disparaging, speculative or blame-attributing language about a brand's product | Articles are visible to `R38` brand partners on `P08` and are a commercial surface |

### 4.6 Media and evidence rules

| # | Rule |
|---|---|
| **AU-21** | A photograph replaces a paragraph wherever it can. Annotate it — an unannotated board photo shows a board |
| **AU-22** | Media is referenced from `M24` content-addressed storage, never duplicated per version (`M61` T-04) |
| **AU-23** | Every image carries alt text in both languages (`CG-011`) — screen-reader use is not the only reason; alt text is what the search index reads |
| **AU-24** | Video is used for technique, not for procedure. A technician mid-repair cannot scrub a video to find step 7 |
| **AU-25** | Video is capped at **90 seconds** per clip and served at device-appropriate resolution (`M61` T-02); longer content is split |
| **AU-26** | Customer-identifiable content — serial numbers, names, addresses, visible data on a screen — is removed before an article leaves `Draft`. This is a hard block |
| **AU-27** | Brand manual pages and diagrams are **referenced as `LIB-` entries**, never pasted into an article. Copying breaks the redistribution scope in `KB-003` |

> **`AU-26` is the rule most likely to be broken by Path A capture**, because the photographs
> pre-filled from a job are evidence photographs of a real customer's device. The improvement
> queue reviewer checks it on every capture. It is listed in §4.10 as a named review gate rather
> than left to the author, because the author was holding a phone in a workshop.

### 4.7 Bilingual authoring

`CG-010` places `KB` at 13 bilingual files of 16. The articles themselves are more strongly
bilingual than that: **the primary reading language of the technical library is Bengali.**

| # | Rule |
|---|---|
| **AU-28** | An article may be authored in Bengali with English absent, and **publication is never blocked for lack of an English translation** (`M61` FR-KMS-002) |
| **AU-29** | The reverse is not true. An article authored in English that will be read by field technicians is not `Published` until the Bengali exists |
| **AU-30** | Whichever language was authored first is the source of truth for meaning; the other is the source of truth for its own wording once signed off in context (`BN-018`) |
| **AU-31** | Codes, part numbers, model names, measurements and units are never translated (`KA-17`); `MD-021` marks model names do-not-translate |
| **AU-32** | Bengali runs 20–40% longer than English (`VB-007`); step text and reference cards are laid out for the Bengali length, not the English |
| **AU-33** | Safety blocks are human-translated in context and re-approved by HSE (`AU-06f`) |
| **AU-34** | Numerals follow `VB-009`; a measurement never changes digit system between the two versions of the same step |

### 4.8 The capture-to-publication path

| Stage | Who | What happens | Gate | `M61` reference |
|---|---|---|---|---|
| 1 `CAPTURED` | R10–R12 | Voice, photos, rough Bengali text, pre-filled model / fault / parts from the job | None — by design (`AU-01`) | FR-KMS-023/024 |
| 2 Improvement queue | Technical Library Owner | Structure into §4.2 blocks; original words retained (`AU-02`); `AU-26` PII check; duplicate check against `KA-10` | Never discard (`AU-03`) | FR-KMS-027 |
| 3 `DRAFT` | Owner or contributor | Facets completed (`KA-05`); completeness ≥ 80% (`AU-17`) | Cannot submit below 80% | FR-KMS-011 |
| 4 `IN REVIEW` | **A qualified reviewer who is not the author** | Technical correctness, safety, applicability, coding, terminology | **Hard block** — reviewer ≠ author, competence checked against `M22` | `BRU-KMS-02` |
| 4b Safety gate | HSE Lead | Any `hazard_class` ≠ `none`, or any brand-authorised procedure, or anything that could void a warranty | **Second approval required** | `BRU-KMS-03` |
| 5 `PUBLISHED` | System | Indexed, added to affected offline packs, exposed to `M32`, subscribers notified | Supersession applied (`KA-10`) | AUT-KMS-05 |
| 5b Customer derivative | Quality Manager + Customer Service Manager | Separately edited, plain-language checked, separately approved | **Never automatic** | `BRU-KMS-11` |

**Time budget.** `M61` KPI-C61-06 targets **median capture-to-publication under 4 days** at W9,
under 10 days at W7. The improvement queue is the only stage with elastic duration, which makes
the Technical Library Owner's capacity the rate limiter for the whole knowledge programme — a
resourcing fact recorded in §7 `O-01` rather than left to be discovered.

### 4.9 Review roles — who may pass which gate

| Gate | Who may pass it | Who may not |
|---|---|---|
| Technical review | A reviewer holding current `M22` competence at or above the article's `repair_level`, for the relevant brand | The author, in any circumstance (`BRU-KMS-02`) |
| Safety gate | HSE Lead, or Quality Manager where HSE has delegated in writing | The technical reviewer acting alone |
| Brand-authorised procedure | Quality Manager, with the brand authorisation current in `MD-011` | A technician certified for the brand but not authorised to publish |
| Warranty-affecting content | Quality Manager with Warranty Claims Officer (R28) consulted | Technical reviewer alone |
| Bengali sign-off | Localisation Lead with a technical reviewer, in context (`BN-018`) | Either alone |
| Customer derivative | Quality Manager + Customer Service Manager | Quality Manager alone |
| Retirement | Quality Manager, reason recorded | The owner alone |

### 4.10 Named review checks

The reviewer works a fixed list. This is what "technical review" means operationally, so that two
reviewers reach the same conclusion on the same article.

| # | Check |
|---|---|
| 1 | Does the procedure actually work on the stated models? Reviewer has performed or witnessed it |
| 2 | Is applicability correct, and is the **exclusion** explicit (`AU-05`)? |
| 3 | Is every safety block present, in three-part form, and placed before its procedure (`AU-06`)? |
| 4 | Does the `repair_level` match the hardest step, not the average step (`KA-06`)? |
| 5 | Are `MD-022` part codes real, current, and is `part_class` stated (`AU-10`)? |
| 6 | Are torque, voltage, pressure and temperature figures sourced (`AU-16`)? |
| 7 | Does verification have a numeric or observable pass criterion (`AU-12`)? |
| 8 | Is the `RES-` coding guidance correct and complete (`AU-13`)? |
| 9 | **Is any customer-identifiable content present (`AU-26`)?** Hard block |
| 10 | Are brand manual pages referenced rather than pasted (`AU-27`)? |
| 11 | Does it contradict an existing `Published` article for the same (model, fault, audience) (`KA-10`)? |
| 12 | Is the terminology `CG-004`-conformant and the Bengali `BN-003`-conformant? |
| 13 | Is the contributor's original capture text still attached (`AU-02`)? |

### 4.11 Worked example — a rough capture becomes an article

**What the technician sent at 18:42, one-handed, in Bengali (Path A, 2 minutes 10 seconds):**

> *Voice note, transcribed:* "এই মডেলে বারবার একই সমস্যা — চার্জার লাগালে LED জ্বলে কিন্তু বোর্ড
> পাওয়ার নেয় না। 3.3 ভোল্ট রেইল শর্ট। লোড সুইচটা চেঞ্জ করলে ঠিক হয়ে যায়। আগেও দুইবার পাইছি।"
> *Plus:* 3 photographs from the job, model `MDL-000101`, fault `FLT-01044`, part issued.

**What the improvement queue produced (Path A → stage 2 → `DRAFT`):**

| Block | Content |
|---|---|
| Title | `Latitude 5420 — charger LED lights but board does not power; 3.3 V rail short at load switch` |
| Applicability | `MDL-000101` and two generation-adjacent models. **Not applicable** to the AMD variant, whose power topology differs |
| Safety | **⚠ CAUTION** — the board is ESD-sensitive (hazard). Handling without wrist strap and mat can destroy the replacement part and produce a latent failure that returns as rework (consequence). Work at a grounded ESD station per [`KB-013`](KB-013_ESD_Chemical_and_Battery_Safety_Data.md) §3 (avoidance). **⚠ WARNING** — disconnect and isolate the battery before any board work; a shorted rail with the battery connected can cause thermal runaway |
| Symptoms | `SYM-00101` does not power on · charger LED illuminates · no fan spin. Bengali as stated by the customer |
| Likely causes | 1. Load switch failure — *most frequent, 3 of 4 observed* — confirmed by 3.3 V rail resistance to ground below spec · 2. Downstream capacitor short · 3. PCH failure — *rare, escalate* |
| Tools | Bench PSU with current limit · DMM (`EQP-` code) · hot-air station · thermal camera or freeze spray |
| Parts | Load switch, `PRT-` code, `part_class: oem_equivalent`, quantity 1 |
| Diagnostic | 5 steps, each: action → expected → if not. Step 1 measures rail resistance to ground with the board unpowered |
| Repair | 7 steps with air temperature, dwell and flux specification per step |
| Verification | Rail measures within spec unpowered; board powers and holds under load for 30 minutes; recorded on the repair order |
| Coding | `RES-` code of class `repair`, `repair_level: L3_board` |
| Common mistakes | Replacing the switch without finding the downstream short — the new part fails within minutes. **This is the paragraph the article exists for** |
| Escalation | If the rail remains shorted after switch replacement, escalate to a second L3 specialist with the resistance readings before ordering a board |
| Sources | Contributor's observation across 4 units · rail specification from `LIB-` service manual entry, verified 2026-08-16 |
| Original words | **The Bengali voice transcript above, retained verbatim (`AU-02`)** |

**Elapsed contributor time: 2 minutes 10 seconds. Elapsed reviewer time: about 40 minutes.**
That ratio is the design. The scarce resource is the specialist's time, not the library owner's.

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| [`KB-001_Knowledge_Architecture_and_Tagging_Standard.md`](KB-001_Knowledge_Architecture_and_Tagging_Standard.md) | Article types, facets, codes — the skeleton's block 1 |
| [`KB-013_ESD_Chemical_and_Battery_Safety_Data.md`](KB-013_ESD_Chemical_and_Battery_Safety_Data.md) | The hazard data every safety block cites (`AU-06e`) |
| [`KB-015_Knowledge_Review_Currency_and_Retirement_Policy.md`](KB-015_Knowledge_Review_Currency_and_Retirement_Policy.md) | Review cycle recorded in block 15 |
| [`KB-003_Repair_Manual_Index_and_Source_Register.md`](KB-003_Repair_Manual_Index_and_Source_Register.md) | `LIB-` references under `AU-27`, and the redistribution scope they inherit |
| [`../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-022_Spare_Part_Catalogue_and_Compatibility_Matrix.md`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-022_Spare_Part_Catalogue_and_Compatibility_Matrix.md) | `part_class` under `AU-10` |
| [`../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-025_Repair_Action_and_Resolution_Code_Taxonomy.md`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-025_Repair_Action_and_Resolution_Code_Taxonomy.md) | Resolution coding under `AU-13` |
| [`../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-046_Test_Equipment_and_Calibration_Master.md`](../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-046_Test_Equipment_and_Calibration_Master.md) | Equipment codes under `AU-09` |
| [`../00_Content_Governance_and_Standards/CG-003_ERP_Product_Content_Style_Guide.md`](../00_Content_Governance_and_Standards/CG-003_ERP_Product_Content_Style_Guide.md) · [`../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md`](../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md) | `AU-18`, `AU-19` |
| [`../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md`](../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md) | Alt text under `AU-23` |
| `M22` Learning, Competency and Certification | Reviewer competence check at gate 4 |
| `BN-003` · `BN-018` | Bengali term base and in-context sign-off |

| Depended on by |
|---|
| Every article in `KB-004`…`KB-014`, `KB-016` · `M61` `cd_knowledge_article` template enforcement · `TR-005` question bank (items derived from articles) · `HC-002` (which adapts this shape for customers) |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **Annual**, and after the first 50 published articles — the first 50 will show what this standard got wrong |
| Trigger for out-of-cycle review | Median capture-to-publication misses its `KPI-C61-06` target for two quarters · a safety incident traced to an article · reviewers systematically disagreeing on the same check · completeness score gaming |
| Owner | Knowledge Manager |
| Change log | `RF-006` |
| Enforcement | Completeness score at submission (`AU-17`); named review checks in §4.10; DoD in `CG-008` |

---

## 7. Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **The Technical Library Owner position is not established or resourced.** `M61` §13 creates it as a new position under R32 and this standard makes it the rate limiter for capture-to-publication. One person cannot structure captures from 200–400 technicians. The capacity model is unwritten | Quality Manager with HR Director | **W5 — before `P02` capture goes live** |
| **O-02** | The article review cycle length is undecided — `M61` Q-06 offers 6, 12 or 24 months. §4.2 of `KB-001` assumes 6/12/24 by type; that assumption needs ratifying, not inheriting | Quality Manager | W6 build |
| **O-03** | Whether knowledge capture is a hard completion condition on complex repairs, and the risk of slowing job closure (`M61` Q-05, `BRU-KMS-10`). This standard is neutral on it; the decision changes how much rough content the queue receives | Ops Director with Quality Manager | W6 build |
| **O-04** | The completeness scoring weights are not defined. §4.2 declares required blocks; the score in `AU-17` needs an agreed weighting, or every article scores 100% by writing one word per block | Knowledge Manager with CTO | Before `cd_knowledge_article` build |
| **O-05** | Bengali technical terminology for board-level electronics does not substantially exist. `AU-19` requires `BN-003` conformance; `BN-003` will need a technical extension authored with R12 specialists. `M61` §7.3 names building a Bengali technical library as a genuine contribution, which is another way of saying nobody has done it yet | Localisation Lead with Technical Director | **W2 — blocks Bengali article publication** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md` — six sections present, §7 added per category convention
- [x] Capture separated from authoring, with no structure imposed at capture (`AU-01`)
- [x] Contributor's original words mandated as permanently retained (`AU-02`, `BRU-KMS-09`)
- [x] Safety signal-word convention adopted from an external standard rather than invented
- [x] Three-part hazard/consequence/avoidance form specified and justified
- [x] Reviewer ≠ author stated as a hard block with the competence check named
- [x] Bilingual rules permit Bengali-only publication (`AU-28`) per `M61` FR-KMS-002
- [x] Worked example runs a real capture through to a draft
- [x] All internal links resolve
- [x] `BRU-KMS-*` cited to `M61` §9, not to `05-05`
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] Named approver recorded — **pending Quality Manager**
- [ ] `O-01` Technical Library Owner resourced — **outstanding; this standard does not function without it**
- [ ] `O-05` Bengali technical term base extended — **outstanding; blocks Bengali publication**
- [x] English-only, per `CG-010` §3.2 — governance content

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
