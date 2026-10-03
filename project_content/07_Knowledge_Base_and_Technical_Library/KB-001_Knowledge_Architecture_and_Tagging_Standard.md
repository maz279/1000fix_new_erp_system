---
id: KB-001
title: Knowledge Architecture and Tagging Standard
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-16
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Knowledge Manager
author: Knowledge Manager with Enterprise Architecture and Technical Services
reviewers: [Quality Manager, Technical Director, CTO, Localisation Lead, BI Lead, Programme Content Lead]
approver: Quality Manager with Technical Director
content_class: E
purpose: >
  Defines the knowledge object model, the article type set, the code scheme and the mandatory
  tagging spine that binds every knowledge asset to registered master data. An untagged knowledge
  base is unsearchable at scale, cannot be scoped into an offline pack, cannot be measured for
  coverage, and is unusable as AI grounding — which means the M32 assistant answers from an
  unbounded corpus it cannot cite.
traces_to: [M61, M32, M26, M31, M01, P02, P10, P01, MD-021, MD-022, MD-024, MD-025, MD-010, MD-011, MD-017, SP-033, KB-002, KB-015]
priority: P1
wave: W2
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M61_Knowledge_Management_and_Technical_Library.md §3.1, §5.1, §5.2, §10 — article types, operational linkage, owned entities
    verified: 2026-08-16
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M61 §9 BRU-KMS-01…18 — module business rules (note: these are module-level rules, not 05-05 rules)
    verified: 2026-08-16
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md — P02 offline repair manuals, wiring diagrams and past repair notes; P10 knowledge search during a live conversation; P01 customer knowledge base
    verified: 2026-08-16
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 — KPI-004 first-time fix 70%→88%, KPI-025 self-service deflection, KPI-026 AI first-contact resolution
    verified: 2026-08-16
    class: P1
  - source: Knowledge-Centered Service (KCS) methodology — capture and refine knowledge in the workflow; solve-loop and evolve-loop separation; findability as a first-class design concern
    verified: 2026-08-16
    class: P2
supersedes: none
review_due: 2027-02-16
---

# KB-001 — Knowledge Architecture and Tagging Standard

> **Read this before writing any other `KB` file, and before authoring a single article.**
>
> Every other file in this category either produces knowledge assets (`KB-003`…`KB-014`,
> `KB-016`) or governs their currency (`KB-002`, `KB-015`). All of them depend on the object
> model and the tagging spine defined here. Change this file and every article in the library
> becomes retroactively non-conformant — which is why it is written first and changed rarely.

---

## 1. Purpose

`M61` gives the company a technical library. This file defines **what goes in it, what shape it
takes, and how it is indexed** so that four things become possible that are otherwise not:

| Capability | Why it fails without this standard |
|---|---|
| **Retrieval by context, not by search luck** | `M61` T-07 requires the right article to appear on a job in ≤ 200 ms from its model and fault code. That resolution is a *tag lookup*. With no mandatory tags there is nothing to look up, and search becomes the only path — which `M61` §4 explicitly names as the fallback, not the design |
| **Offline pack scoping** | `P02` carries a scoped article set bounded by a storage budget, computed from the technician's brands, models and skill level. Those are tags. An untagged corpus cannot be scoped, so the only options are "everything" (exceeds the budget) or "nothing" |
| **Coverage measurement** | The `M61` category KPI is **100% coverage of the top 100 fault codes**. Coverage is a join between the fault-code register (`MD-024`) and the article tag set. No tags, no join, no KPI |
| **AI grounding with citation** | `M61` §9 `BRU-KMS-12` requires every `M32` answer to cite its source article and version, and prohibits drawing on unapproved or superseded content. That is enforced by a governed, tagged corpus boundary — not by prompt wording |

**The consequence of absence, stated plainly (`CP-03`):** without this file, 150–250 authored
articles become an unsearchable pile that the technician application cannot scope, the coverage
KPI cannot be computed, and the AI assistant answers from whatever it happens to retrieve.

---

## 2. Scope

**In scope:** the knowledge object model; the article type set and what each type is for; the
permanent code scheme for every knowledge object; the mandatory and optional tagging facets and
their binding to registered master data; the tagging rules `KA-01`…`KA-18`; findability design
(context surfacing, search, ranking); the AI corpus boundary; offline pack scoping inputs;
coverage and gap measurement; and the taxonomy change-control process.

**Out of scope:**

| Subject | Owned by |
|---|---|
| The internal structure of an article — required sections, safety-warning rules, evidence rules | [`KB-002_Article_Template_and_Authoring_Standard.md`](KB-002_Article_Template_and_Authoring_Standard.md) |
| Review intervals, staleness thresholds, retirement | [`KB-015_Knowledge_Review_Currency_and_Retirement_Policy.md`](KB-015_Knowledge_Review_Currency_and_Retirement_Policy.md) |
| The fault and resolution taxonomies themselves | [`../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-024_Fault_Symptom_and_Diagnostic_Code_Taxonomy.md`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-024_Fault_Symptom_and_Diagnostic_Code_Taxonomy.md) · [`../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-025_Repair_Action_and_Resolution_Code_Taxonomy.md`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-025_Repair_Action_and_Resolution_Code_Taxonomy.md) |
| Diagnostic decision-tree content and its triage rules | [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-033_Diagnostic_and_Triage_Decision_Tree_Library.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-033_Diagnostic_and_Triage_Decision_Tree_Library.md) |
| Customer-facing help structure and its own information architecture | `HC-001` Help Centre Information Architecture |
| Search implementation, index technology, ranking code | `M61` T-05, T-06; this file states the requirement, not the implementation |
| Course design and curricula built *from* articles | `TR-001`, `TR-003`; `M61` §3.2 places training with `M22` |
| Records of what happened — job sheets, evidence packs, certificates | `M24`; `M61` §9 `BRU-KMS-01` is a hard block on storing records here |

> **The single most important boundary in this category.** `M61` holds *knowledge of how to do
> things*, continuously revised and retired. `M24` holds *records of what happened*, fixed and
> retained for legal defensibility. A disposal certificate is a record. The procedure for issuing
> one is knowledge. Conflating them puts revisable content into a retention regime and
> legally-fixed content into a revision workflow — both are wrong, and both are hard to unwind.

---

## 3. Audience

| Audience | Uses this file to… | Volume |
|---|---|---|
| **Knowledge Manager / Technical Library Owner** | Govern the taxonomy, approve new facet values, run coverage analysis | 1–2 |
| **R12 Specialist Technician** | Tag an article correctly at capture so it reaches the people who need it | 15–30 |
| **R10 Senior Technician** | Author and review within competence | 80–150 |
| **R32 Quality Manager** | Approve safety and brand-procedure content; audit tagging conformance | 2–4 |
| **Platform / integration engineers** | Build the tag model, the context-surfacing API and the offline scoping computation | Build team |
| **BI and AI teams** | Compute coverage; define the `M32` corpus boundary | `M25`, `M26`, `M32` |
| **Localisation Lead** | Understand which facets carry Bengali values and which do not | 1 |

---

## 4. Content

### 4.1 The knowledge object model

Six object classes exist. **Every knowledge asset in the programme is exactly one of them.**
A file that is none of these is not knowledge content and belongs elsewhere.

| # | Object | Code prefix | What it is | Governed by | Lives in `M61` entity |
|---:|---|---|---|---|---|
| 1 | **Knowledge article** | `KNW-` | A single unit of guidance — procedure, fault→fix, technique note, safety note, known issue, FAQ, how-to, tool guide | `KB-002` | `fix.knowledge.article` |
| 2 | **Troubleshooting tree** | `TRE-` | Versioned branching guidance from symptom to coded outcome | `SP-033` (content) · this file (tagging) | `fix.troubleshooting.tree` |
| 3 | **Library entry** | `LIB-` | A held manual, service manual, wiring or board diagram, schematic, exploded view or parts diagram | [`KB-003_Repair_Manual_Index_and_Source_Register.md`](KB-003_Repair_Manual_Index_and_Source_Register.md) | `fix.technical.library` |
| 4 | **Bulletin / notice** | `BUL-` | A brand technical bulletin, service notice or recall notification received from a brand partner | [`KB-010_Brand_Technical_Bulletin_and_Recall_Archive.md`](KB-010_Brand_Technical_Bulletin_and_Recall_Archive.md) | `fix.brand.bulletin` |
| 5 | **Known-issue record** | `KIS-` | A recurring defect by model, with interim workaround and permanent-fix status | [`KB-011_Known_Issue_and_Workaround_Register.md`](KB-011_Known_Issue_and_Workaround_Register.md) | `fix.knowledge.article` (type `known_issue`) with an issue extension |
| 6 | **Reference card** | `REF-` | A one-screen, offline-first quick reference curated into the `P02` pack | [`KB-016_Technician_Field_Reference_Card_Set.md`](KB-016_Technician_Field_Reference_Card_Set.md) | `fix.knowledge.article` (type `reference_card`), flagged `offline_pack` |

> **Why known-issue records and reference cards are article subtypes, not new entities.** `M61`
> §10 declares nineteen owned entities and none of them is a known-issue table. Inventing a
> nineteenth-and-a-half entity in a content standard would put the content register ahead of the
> module specification it traces to — the exact `CP-04` violation this programme audits for.
> Both are modelled as article types with a required facet set. The distinction is real and is
> carried by tags, not by a new table.

### 4.2 Article types

`M61` FR-KMS-001 requires distinct article types, each with its own template and required
sections. The set is closed — **an author may not invent a type** (`KA-03`).

| Type | Answers the question | Required facets beyond the mandatory spine | Review cycle (`KB-015`) | Customer derivative permitted |
|---|---|---|:--:|:--:|
| `procedure` | *How do I carry out this repair?* | Repair level, tools, parts, standard time | 12 months | Rarely — only where safe for a consumer to attempt |
| `fault_fix` | *This fault is confirmed; what fixes it?* | Fault code, resolution code, parts | 12 months | No |
| `technique` | *How is this technique performed?* — reballing, micro-soldering, crimping | Repair level, tools, competency | 24 months | No |
| `tool_guide` | *How do I operate this equipment safely and correctly?* | Equipment code (`MD-046`), calibration check | 24 months | No |
| `safety_note` | *What will hurt me or the customer, and what do I do about it?* | Hazard class, statutory reference | **6 months** | Yes — consumer safety guidance |
| `known_issue` | *Is this a known defect, and is there a workaround?* | Model, defect signature, permanent-fix status | **6 months** | Sometimes — with Quality approval |
| `faq` | *What is the short answer to a frequently asked question?* | Audience | 12 months | Yes |
| `how_to` | *How does a user perform this task?* | Audience, surface | 12 months | Yes |
| `reference_card` | *What must I be able to see with no signal and no time?* | Offline pack membership | **6 months** | No |

> **Safety notes, known issues and reference cards carry a six-month cycle** because all three
> are consumed under time pressure by someone who cannot verify them. `KB-015` §4 sets the
> intervals; they are repeated here only so that a person choosing a type sees the maintenance
> commitment they are taking on.

### 4.3 Code scheme

| Object | Format | Allocation | Reuse |
|---|---|---|---|
| Knowledge article | `KNW-nnnnn` | Sequential on first save, including on a rough capture | **Never reused.** Usage, feedback and attribution records reference it |
| Troubleshooting tree | `TRE-nnn` | Sequential per tree, not per node | Never reused |
| Tree node | `TRE-nnn.nn` | Ordinal within the tree | Reused only within a tree version |
| Library entry | `LIB-nnnnn` | Sequential on ingestion | Never reused |
| Bulletin | `BUL-nnnnn` | Sequential on receipt; the brand's own reference is a separate attribute | Never reused |
| Known issue | `KIS-nnnn` | Sequential on registration | Never reused |
| Reference card | `REF-nnn` | Sequential; card set version is separate | Never reused |

**`KA-01` — a code is allocated at capture, not at publication.** A rough Bengali capture from a
technician's phone gets a `KNW-` code immediately. `M61` §9 `BRU-KMS-08` forbids discarding an
unstructured capture; a capture with no code cannot be tracked into the improvement queue, and
untracked captures are how "we tried knowledge management once" happens.

### 4.4 The mandatory tagging spine

**Eight facets are mandatory on every knowledge object.** Each binds to a registered master-data
register — none is free text. This is the whole architecture in one table.

| # | Facet | Bound to | Cardinality | Bengali | Why mandatory |
|---:|---|---|---|:--:|---|
| 1 | `device_family` | [`MD-021`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-021_Device_Category_Make_and_Model_Catalogue.md) §2.1 — `DF-IT`, `DF-HA`, `DF-MB`, `DF-SRV`, `DF-SEC` | 1..n | — | The coarsest scoping facet; the first cut of every offline pack and every guide set |
| 2 | `model_scope` | `MD-021` `model_code` | 0..n, or `family_wide` | — | Context surfacing resolves from the model on the job. An article with no model scope can only ever be found by search |
| 3 | `brand` | [`MD-017`](../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-017_Brand_Partner_Master_Register.md) `brand_code` | 0..n | — | Brand-authorised procedures, bulletin linkage, and the redistribution scoping in `KB-003` |
| 4 | `fault_code` | [`MD-024`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-024_Fault_Symptom_and_Diagnostic_Code_Taxonomy.md) — `SYM-nnnnn` and/or `FLT-nnnnn` | 0..n | ✔ (label) | **The coverage KPI is computed on this facet.** An article tagged to no fault code contributes nothing to the top-100 measure |
| 5 | `resolution_code` | [`MD-025`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-025_Repair_Action_and_Resolution_Code_Taxonomy.md) — `RES-nnnnn` | 0..n | ✔ (label) | Binds guidance to what gets recorded on the job, and carries `standard_minutes` into `KB-014` |
| 6 | `repair_level` | `MD-010` competency — `L1` / `L2` / `L3_board` | exactly 1 | — | Offline pack scoping and the `BRU-SRM-14` restriction on board-level work |
| 7 | `hazard_class` | `MD-022` `hazard_class` — `none` / `lithium` / `refrigerant` / `chemical` / `sharp` / `esd_sensitive` | 1..n | — | Drives the mandatory safety block (`KB-002`) and the linkage to [`KB-013_ESD_Chemical_and_Battery_Safety_Data.md`](KB-013_ESD_Chemical_and_Battery_Safety_Data.md) |
| 8 | `audience` | `internal` / `customer` / `brand_partner` | 1..n | — | The publication boundary. `M61` §9 `BRU-KMS-11` requires a separate approval for customer derivatives; this facet is where that boundary is expressed |

**`KA-02` — no facet value may be minted in a knowledge asset.** Every value resolves in the
register named above. Where a needed value does not exist, it is registered there first. This is
rule `RG-01` applied to knowledge, and it is the same prohibition `SP-033` `DT-01` places on
diagnostic trees.

### 4.5 Optional facets

Optional facets improve retrieval; they never gate publication.

| Facet | Bound to | Used for |
|---|---|---|
| `part_family` / `part_code` | `MD-022` | Parts-led retrieval; feeds [`KB-009_Parts_Compatibility_and_Substitution_Notes.md`](KB-009_Parts_Compatibility_and_Substitution_Notes.md) |
| `equipment_code` | `MD-046` | Tool and test-equipment guides ([`KB-012_Tool_Jig_and_Test_Equipment_Operating_Guides.md`](KB-012_Tool_Jig_and_Test_Equipment_Operating_Guides.md)) |
| `certification_required` | `MD-011` | Brand-authorised procedures; supports the `BRU-SRM-09` assignment block |
| `service_mode` | `MD-020` — walk-in, on-site, pick & drop, remote, workshop, kiosk | Field-vs-bench applicability |
| `bulletin_ref` | `BUL-nnnnn` | Articles created or amended because of a brand bulletin |
| `known_issue_ref` | `KIS-nnnn` | Procedure articles carrying a live workaround |
| `symptom_phrase_bn` | free text, Bengali | Search synonym seeding — the one deliberately unbound facet, because real technicians search in words the taxonomy does not contain |
| `season` | `pre_monsoon` / `monsoon` / `summer_peak` / `winter` | AC and refrigeration demand spikes; supports pre-season pack refresh |

> **`symptom_phrase_bn` is the deliberate exception to `KA-02`.** A Bengali-speaking technician
> searching for a not-cooling AC does not type `SYM-00220`. Free-text symptom phrases in Bengali
> are the bridge between how people search and how the system indexes, and constraining them to a
> register would defeat their only purpose. They are additive to the bound facets, never a
> substitute for them (`KA-04`).

### 4.6 Tagging rules

| # | Rule | Class |
|---|---|:--:|
| **KA-01** | A code is allocated at capture, not at publication; a rough capture is never codeless | **H** |
| **KA-02** | No facet value is minted in a knowledge asset; every value resolves in its register (`RG-01`) | **H** |
| **KA-03** | The article type set in §4.2 is closed; an author may not invent a type | **H** |
| **KA-04** | Free-text symptom phrases are additive to bound facets, never a substitute | **H** |
| **KA-05** | All eight mandatory facets are populated before an article may leave `Draft` | **H** |
| **KA-06** | `repair_level` is exactly one value — the **minimum** level competent to act on the article | **H** |
| **KA-07** | An article touching a `lithium`, `refrigerant` or `chemical` hazard class must link to `KB-013` and carries the additional approval in `M61` §9 `BRU-KMS-03` | **H** |
| **KA-08** | `audience: customer` is set only on a separately-approved derivative record, never by editing an internal article's facet (`BRU-KMS-11`) | **H** |
| **KA-09** | An article tagged to a brand inherits that brand's redistribution scope from `KB-003`; it is not downloadable outside it (`BRU-KMS-16`) | **H** |
| **KA-10** | Two `Published` articles may not carry the same (`model_scope`, `fault_code`, `audience`) triple — publication supersedes (`BRU-KMS-04`) | **H** |
| **KA-11** | A `Superseded` or `Retired` article is removed from every offline pack and from the `M32` corpus (`BRU-KMS-05`) | **C** |
| **KA-12** | Only `Published`, non-superseded, in-review-cycle articles enter the `M32` corpus (`BRU-KMS-12`) | **C** |
| **KA-13** | Coverage is computed as a join of `MD-024` fault codes against the `fault_code` facet, weighted by job volume; it counts *quality of coverage*, not existence (`M61` §14) | **C** |
| **KA-14** | A tag change is a versioned change to the article, not a silent edit — retrieval behaviour changed | **H** |
| **KA-15** | Facet values withdrawn in their source register are archived on the article, never deleted; the article is flagged for re-tagging | **C** |
| **KA-16** | An article with no `fault_code` and no `resolution_code` is publishable but is reported as **unmeasurable** in the coverage report | **S** |
| **KA-17** | Bengali facet *labels* come from `BN-003`; the facet *codes* are language-neutral and never translated | **H** |
| **KA-18** | Offline pack membership is computed from facets, never hand-curated per technician — except for the `REF-` reference-card set, which is deliberately curated (`KB-016`) | **H** |

> Class: **H** hard block · **A** approved override · **S** soft warning · **C** computed —
> the same scale as `05-05` §1, so that a person who can read the business-rule register can read
> this one.

### 4.7 Findability — the three retrieval paths

`M61` §4 states the design position: *"Search is the fallback, not the path."* Three paths exist,
in priority order.

| Path | Trigger | Resolution | Latency requirement | Depends on |
|---|---|---|---|---|
| **1. Context surfacing** | Opening a service order, repair order, MSP ticket or live conversation | Match on (`model_scope`, `fault_code`, `brand`), fall back to (`device_family`, `fault_code`) | **≤ 200 ms p95** (`M61` T-07) | Facets 1, 2, 3, 4 |
| **2. Guided traversal** | Technician follows a diagnostic tree | Tree outcome node carries a `KNW-` link (`SP-033` `DT-10`) | Inherits the tree's | `TRE-` linkage |
| **3. Search** | Nothing surfaced, or the technician is looking ahead | Bilingual, typo-tolerant, transliteration-aware, ranked by demonstrated usefulness | **≤ 400 ms p95** (`M61` T-15) | All facets + `symptom_phrase_bn` |

**Ranking.** `M61` FR-KMS-014 requires ranking by demonstrated resolution rate and rating, not by
text relevance alone. The content standard's contribution to ranking is the tag set: an article
correctly tagged to the exact model outranks one tagged only to the family, and an article that
has resolved the fault outranks one that has merely been opened.

**`KA-16` in practice.** An article with rich prose and no fault-code tag will be found by a
determined searcher and by nobody else. It is publishable — refusing to publish useful content on
a metadata technicality is how knowledge programmes lose their authors — but it appears in the
weekly coverage report as unmeasurable, which is where it gets fixed.

### 4.8 The AI corpus boundary

`M32` answers customers and agents from this library. `M61` §9 `BRU-KMS-12` makes the boundary a
hard rule. The tagging standard makes it computable:

| Corpus admission test | Facet or state |
|---|---|
| State is `Published` | Article state |
| Not superseded, not retired | `superseded_by_id` empty |
| Within its review cycle, or overdue by less than the grace period in `KB-015` | `next_review_at` |
| `audience` includes the surface being answered — `customer` for `P01`, `internal` for `P02`/`P10` | Facet 8 |
| Hazard-class content carries its `KB-013` link | Facets 7 + `KA-07` |
| Brand-scoped content is within the answering surface's redistribution scope | Facet 3 + `KB-003` |

**Every answer cites the source article code and version.** An `M32` answer that cannot name a
`KNW-` code and a version number is a hallucination by definition, and the corpus boundary is
what makes that statement testable rather than aspirational.

> **A caution worth recording.** A governed corpus does not make an assistant correct; it makes
> an assistant *auditable*. If the underlying article is wrong, `M32` will confidently repeat it
> with a citation. That is why `KB-015` staleness control is a P2 file that behaves like a P0
> control, and why `M61` KPI-C61-08 sets **zero** stale articles served offline as the target.

### 4.9 Offline pack scoping inputs

`P02` carries a scoped article set inside a declared storage budget (`M61` T-01, FR-KMS-017).
The scoping computation reads facets only:

| Input | Facet | Source of the technician's value |
|---|---|---|
| Which device families this technician works | 1 `device_family` | `MD-010` competency + recent job history |
| Which models | 2 `model_scope` | Assignment history, 90-day window |
| Which brands they are certified for | 3 `brand` | `MD-011` certification register |
| What level they may act at | 6 `repair_level` | `MD-010` |
| Which hazards they are trained for | 7 `hazard_class` | `MD-011` + `M59` safety training |
| Reference card set | — | Always included in full (`KA-18` exception) |

**Media is the constraint, not text.** `M61` T-02 records that diagrams and video dominate the
payload. The tagging standard's contribution is that a diagram is a `LIB-` entry with its own
facets, so the pack can carry the *procedure* for a model without carrying the 400-page service
manual it references. `KB-003` §6 sets the diagram-extract rule that makes this workable.

### 4.10 Coverage and gap measurement

| Measure | Definition | Target | Reported in |
|---|---|---|---|
| **Top-100 fault-code coverage** | Of the 100 highest-volume `FLT-` codes in `MD-024` by 90-day job count, the proportion with at least one `Published`, in-cycle, ≥ 3.5-rated article | **100%** (`M61` KPI-C61-01, W9) | Weekly coverage backlog |
| Model coverage | Proportion of `MD-021` models with ≥ 50 jobs in 12 months carrying at least one article | Rising; no absolute target | Monthly |
| Unmeasurable articles | Articles publishable but untagged to any fault or resolution code (`KA-16`) | < 10% of corpus | Weekly |
| Orphan faults | `FLT-` codes with job volume and zero articles, ranked by volume | Drives the authoring backlog | Weekly (`M61` AUT-KMS-09) |
| Tag conformance | Articles with all eight mandatory facets populated | 100% at `Published` (`KA-05`) | Weekly |

> **Coverage counts quality, not existence.** `M61` §14 is explicit: the top-100 report shows
> *"coverage against the 100% category KPI, with quality of coverage not merely existence"*. An
> article that exists, is stale and rates 2.1/5 does not cover its fault code. Defining coverage
> any other way produces a KPI that is met on the day someone writes 100 empty stubs.

### 4.11 Taxonomy change control

| Change | Who may propose | Who approves | Effect on existing articles |
|---|---|---|---|
| Add an article type | Knowledge Manager | Quality Manager + Technical Director | None; existing articles keep their type |
| Add a mandatory facet | Knowledge Manager | Quality Manager + CTO + BI Lead | **All existing articles become non-conformant.** Requires a migration plan and a grace period before `KA-05` is enforced |
| Add an optional facet | Knowledge Manager | Knowledge Manager | None |
| Change a facet's bound register | Enterprise Architecture | Quality Manager + MDM | Re-tagging exercise; articles flagged, not blocked (`KA-15`) |
| Retire a facet value | The owning register (`MD-*`) | The register's approver | Articles archived-tagged and flagged for re-tagging (`KA-15`) |
| Change the code format | — | **Prohibited.** `CP-02` and `KA-01`; codes are permanent | — |

Every taxonomy change is logged in `RF-006` as a content decision, with the article count
affected stated at the time of the decision, not estimated afterwards (`CP-11`).

### 4.12 Worked example — one article, fully tagged

*A specialist technician completes a board-level repair on a common laptop model: a shorted power
rail traced to a failed load switch. The job took 40 minutes over the standard time and it is the
fourth occurrence this quarter.*

| Element | Value | Rule satisfied |
|---|---|---|
| Code | `KNW-01187`, allocated at capture on the phone | `KA-01` |
| Type | `fault_fix` | `KA-03` |
| Title EN / BN | "Latitude 5420 — no power, 3.3 V rail short at load switch" / Bengali equivalent | `KB-002` |
| 1 `device_family` | `DF-IT` | `KA-05` |
| 2 `model_scope` | `MDL-000101` (Latitude 5420), plus two generation-adjacent models added at review | `KA-05` |
| 3 `brand` | `BRD-011` | `KA-05` |
| 4 `fault_code` | `FLT-01044` mainboard power rail short circuit; symptom `SYM-00101` does not power on | `KA-13` — counts toward coverage |
| 5 `resolution_code` | A `RES-` code of class `repair`, `repair_level: L3_board`, `standard_minutes` set | `KB-014` reads this |
| 6 `repair_level` | `L3_board` | `KA-06`; `BRU-SRM-14` restricts who may act |
| 7 `hazard_class` | `esd_sensitive` | `KA-07` → links `KB-013` §3 ESD control |
| 8 `audience` | `internal` only | `KA-08` — no customer derivative for board-level work |
| Optional | `part_family` of the load switch; `equipment_code` of the hot-air station; `symptom_phrase_bn` "চার্জ নিচ্ছে না, লাইট জ্বলে না" | §4.5 |
| Cross-links | `KIS-0043` if the pattern is registered as a known issue; `TRE-002.07` outcome node | §4.1 |

**What the tagging buys, concretely.** The next junior technician who opens a job for
`MDL-000101` with symptom `SYM-00101` sees this article surfaced in under 200 ms without
searching. It enters the offline pack of every technician certified on `BRD-011` at `L3_board`.
It counts toward top-100 coverage for `FLT-01044`. `M32` may cite it to an internal agent but
never to a customer. And when the fourth occurrence becomes the fortieth, `KB-011` has the
signature it needs to raise a known issue and `KB-010` has what it needs to open a brand query.

**Without the tags it is a well-written note that one person can find.**

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| [`../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-021_Device_Category_Make_and_Model_Catalogue.md`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-021_Device_Category_Make_and_Model_Catalogue.md) | Facets 1 and 2 — device families and models |
| [`../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-024_Fault_Symptom_and_Diagnostic_Code_Taxonomy.md`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-024_Fault_Symptom_and_Diagnostic_Code_Taxonomy.md) | Facet 4 — and the entire coverage measure |
| [`../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-025_Repair_Action_and_Resolution_Code_Taxonomy.md`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-025_Repair_Action_and_Resolution_Code_Taxonomy.md) | Facet 5 — and `standard_minutes` into `KB-014` |
| [`../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-022_Spare_Part_Catalogue_and_Compatibility_Matrix.md`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-022_Spare_Part_Catalogue_and_Compatibility_Matrix.md) | Facet 7 `hazard_class`, and the optional parts facets |
| [`../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-017_Brand_Partner_Master_Register.md`](../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-017_Brand_Partner_Master_Register.md) | Facet 3 — and the redistribution scoping in `KB-003` |
| [`../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-010_Competency_and_Skill_Taxonomy.md`](../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-010_Competency_and_Skill_Taxonomy.md) · [`../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-011_Certification_and_Brand_Authorisation_Register.md`](../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-011_Certification_and_Brand_Authorisation_Register.md) | Facet 6, and offline pack scoping |
| [`KB-002_Article_Template_and_Authoring_Standard.md`](KB-002_Article_Template_and_Authoring_Standard.md) | The shape inside the object this file indexes |
| [`KB-015_Knowledge_Review_Currency_and_Retirement_Policy.md`](KB-015_Knowledge_Review_Currency_and_Retirement_Policy.md) | Cycle intervals referenced in §4.2 and the corpus boundary in §4.8 |
| `M61` §5.1, §5.2, §10 | The module that implements the object model |
| `BN-003` Bengali terminology base | Facet labels under `KA-17` |
| `CG-004` Terminology and Controlled Vocabulary Standard | The one approved term per business object — article titles obey it |

| Depended on by |
|---|
| Every other `KB` file · `SP-033` (tree outcomes link to `KNW-` codes) · `HC-001` (customer derivatives) · `TR-002` (courses built from articles) · `RP-001` (coverage KPI definition) · `M32` corpus boundary · `P02` offline pack computation |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **Annual**, and at every wave boundary that adds a portal consuming knowledge |
| Trigger for out-of-cycle review | A new mandatory facet is proposed · a bound register changes its code format · context-surfacing latency misses its target for two consecutive months · coverage cannot be computed for any reason |
| Owner | Knowledge Manager, with Technical Library Owner as delegate |
| Change log | `RF-006`; every taxonomy change records the affected article count at decision time |
| Conformance audit | Tag conformance reported weekly; full taxonomy audit at each wave boundary under `AUDIT_Checklist_Recurring.md` |

---

## 7. Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **The offline storage budget per device is undecided.** `M61` Q-04 raises it and it is unresolved. Facet-based scoping is computable at any budget, but the *pack composition* — how many models, how many diagrams — cannot be specified until the number exists | CTO with Ops Director | **Before W2 `P02` build** |
| **O-02** | `MD-021` is not yet populated with the actual serviced model range, so `model_scope` cannot be validated at authoring time. Same dependency `SP-033` O-02 records | MDM with Technical | Before authoring begins |
| **O-03** | The coverage attribution method is not agreed. `M61` Q-08 flags that a weak method makes the +4-point first-time-fix KPI unarguable in either direction. `KA-13` defines coverage; it does not define *attribution* | Quality Manager with CTO | **W6 — the KPI depends on it** |
| **O-04** | Whether `HC-001` reuses these facets or defines its own customer-facing taxonomy. Two taxonomies over one corpus is the drift `CP-01` exists to prevent; the decision belongs to `HC-001` and is recorded here so it is not made by accident | Content Design with Knowledge Manager | Before `HC-001` is authored |
| **O-05** | `M61` lands in W6 but `KB` content is needed from W2 (`P02`). Until then, tagging must be applied to content held outside the module. **The tagging standard is deliverable now; the system that enforces it is not.** `M61` §16.3 already records this as a board-level concern (Q-02) | Ops Director / CEO | **W2 — risk decision** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md` — all six sections present, §7 added and justified as an open-items register per category convention
- [x] Object model closed and reconciled against `M61` §10 owned entities — no entity invented
- [x] Every facet bound to a named register; the one unbound facet justified
- [x] Tagging rules carry a class on the `05-05` §1 scale
- [x] AI corpus boundary stated as a computable test, not as intent
- [x] Coverage defined as quality of coverage, per `M61` §14
- [x] Worked example demonstrates all eight mandatory facets
- [x] All internal links resolve
- [x] Every factual claim carries a source and verification date (`CG-012`)
- [x] `BRU-KMS-*` rules cited to `M61` §9, **not** to `05-05` — they are module rules and do not appear in the cross-cutting register
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] Named approvers recorded — **pending Quality Manager and Technical Director**
- [ ] `O-01` offline budget resolved — **outstanding; blocks pack composition**
- [ ] Walked against a populated `MD-021` — **outstanding (`O-02`)**
- [x] English-only, per `CG-010` §3.2 — governance content, head-office audience

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
