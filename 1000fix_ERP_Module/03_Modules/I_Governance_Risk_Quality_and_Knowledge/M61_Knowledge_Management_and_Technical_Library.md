---
id: FIX-ERP2-M61
module_id: M61
module_code: KMS
module_name: Knowledge Management & Technical Library
category: I — Governance, Risk, Quality & Knowledge
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Quality Manager
system_owner: Governance Squad
priority: P2
wave: W6
---

# M61 — Knowledge Management & Technical Library
### Category I · Code `KMS` · ★ New in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M61 |
| **Module code** | `KMS` |
| **Category** | I — Governance, Risk, Quality & Knowledge |
| **Status** | ★ New — created in v2.1 after benchmarking found that technical knowledge had no owner and was being conflated with document management |
| **Priority** | **P2** |
| **Delivery wave** | W6 (Months 23–26) |
| **Business owner** | Quality Manager |
| **System owner** | Governance Squad |
| **Delivery layers** | L2 (OCA `document_page`, `document_page_approval`, `attachment_indexation`) + L4 (offline article store in P02) + L5 (custom) |
| **Custom modules** | `cd_knowledge_article`, `cd_troubleshooting_tree`, `cd_knowledge_capture`, `cd_knowledge_search`, `cd_brand_bulletin` |
| **Requirement range** | FR-KMS-001 … FR-KMS-036 |
| **Requirement count** | **36** *(measured; register estimate 24)* |
| **Effort estimate** | **16 person-weeks** *(measured; register estimate 13 PW)* |
| **Depends on** | M24 Document · M37 Catalogue · M17 Asset Registry · M29 Identity · M28 Integration · M01 SRM · M31 Workshop |
| **Depended on by** | M01, M31, M02, M05, M06, M22, M23, M27, M32, M34, M09, M40, M26 · Portals **P01**, **P02**, **P10** |

> **Register note.** Measured scope exceeds the pre-specification estimate by 50% in
> requirements and 23% in effort, concentrated in troubleshooting-tree authoring and offline
> distribution. `02-02` §3 must be restated when all four Category I specifications are complete.

---

## 2. Purpose

M61 exists to stop the company losing what it knows.

1000FiX performs board-level repair across 17+ brands. That capability lives in the heads of a
small number of senior and specialist technicians — perhaps fifteen to thirty people out of a
technical workforce of several hundred. None of it is written down. When one of them resigns,
retires or is unavailable, a class of repair simply stops being possible until someone else
rediscovers it.

The category overview names this exactly: *"senior technicians retire with undocumented
expertise"* — rated **High**, with the consequence *"capability loss across board-level repair"*.

M61 is the answer: a technical library of repair procedures, wiring and board diagrams,
fault→fix mappings, troubleshooting decision trees, technique notes, video demonstrations and
brand technical bulletins — searchable in Bengali, available offline on the technician's phone
at the bench and in the field, rated for usefulness by the people who use it, and continuously
revised rather than written once.

It is deliberately **not** the document repository. The category overview draws the line: M24
holds *records of what happened*, valued for legal defensibility, created once and disposed at
end of retention, with restricted and logged access. M61 holds *knowledge of how to do things*,
valued for technician capability, continuously revised, broadly searchable and offline. Their
quality measures differ too — M24's is retrievability and integrity; M61's is **usefulness: does
it resolve the fault?**

### Why It Exists

Three pressures created this module.

**Capability risk.** A repair business whose hardest capability is undocumented has a single
point of failure it cannot see on any balance sheet.

**First-time fix.** M01 targets **88% first-time fix**. A technician who arrives without the
knowledge to complete the repair must leave and return — the defining failure of field service.
Industry evidence on knowledge-centred practice is strong: organisations adopting it report
materially improved first-resolution times within the first three to nine months. The category
KPI sets a **+4 percentage-point first-time-fix improvement attributable to knowledge use**.

**A stated commitment.** The business plan already describes a knowledge base with FAQ articles,
troubleshooting guides, video tutorials and user manuals, for customers as well as staff. It has
no system.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| `_CATEGORY_OVERVIEW.md` §4 | The knowledge/records distinction, and why 1000FiX specifically needs M61: undocumented expertise in a small number of senior technicians is a single point of failure |
| `_CATEGORY_OVERVIEW.md` §5 | Boundary map: repair procedures, diagrams and solution articles are M61's; training courses are M22's; brand bulletins are received by M61 and acted on by M01 |
| `_CATEGORY_OVERVIEW.md` §8 | KPIs: 100% coverage of the top 100 fault codes, +4 pts first-time fix, > 4.0/5 usefulness |
| `_CATEGORY_OVERVIEW.md` §10 | Two named risks: undocumented expertise, and the knowledge base becoming stale and distrusted |
| Business Plan §Knowledge Base | FAQ articles, troubleshooting guides, video tutorials, user manuals |
| `04-00` P02 §Knowledge | "Offline repair manuals, wiring diagrams and past repair notes" — a non-negotiable technician app capability |
| `04-00` P10 §Handling | Contact-centre knowledge-base search during a live conversation |
| `04-00` P01 §Support | Customer-facing knowledge base and FAQ |
| M01 §5.3 FR-SRM-021…023 | Diagnostic templates and fault coding — the structure knowledge articles attach to |
| M37 §5.3 | Repair operations, rBOM and standard repair times — the operational spine articles document |
| M23 §12 | Failure patterns and verified fixes worth documenting as articles |

---

## 3. Scope Boundary

> **This is the anti-overlap control.** Both sides of every boundary must agree.

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | The knowledge article: authoring, structure, media, versioning, review and publication |
| 2 | Article types: repair procedure, fault→fix solution, technique note, tool guide, safety note, FAQ, how-to, known issue |
| 3 | **Troubleshooting decision trees** — authored, versioned, branching guidance from symptom to resolution |
| 4 | Technical library: repair manuals, service manuals, wiring and board diagrams, schematics, exploded views, parts diagrams |
| 5 | Video and image content: demonstrations, technique captures, annotated photographs |
| 6 | **Knowledge taxonomy and linkage** — articles bound to fault codes, repair operations, brands, models, device categories and parts |
| 7 | **Search** — bilingual, typo-tolerant, symptom-oriented, context-aware and ranked by demonstrated usefulness |
| 8 | **Context-aware surfacing** — the right article presented automatically on the job, the ticket or the conversation |
| 9 | **Offline distribution** — a scoped, current article set on the technician application, available with no connectivity |
| 10 | **Knowledge capture in the flow of work** — capturing a solution at the moment a difficult repair is completed |
| 11 | Capture prompts and definition-of-done linkage on complex, novel and first-time repairs |
| 12 | Article review workflow: technical review, approval, publication and controlled superseding |
| 13 | **Usefulness feedback** — rating, "did this resolve it?", comments and improvement suggestions from users |
| 14 | Article health: review dates, staleness detection, usage decay, low-rating flagging and retirement |
| 15 | Coverage analysis: fault codes, models and operations with no article, ranked by volume |
| 16 | **Brand technical bulletins, service notices and recall notifications** — receipt, classification, distribution and acknowledgement |
| 17 | Customer-facing knowledge: FAQs, self-help guides and troubleshooting for P01, with separate publication control |
| 18 | Contribution recognition and contributor analytics |
| 19 | Expertise mapping: who knows what, derived from contribution, resolution and review activity |
| 20 | Knowledge analytics: usage, resolution attribution, coverage, gaps and the first-time-fix contribution |
| 21 | The knowledge API consumed by the technician app, contact-centre console, AI assistant and customer portal |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| Records of what happened — job sheets, reports, invoices, evidence packs | **M24** Document | Records are fixed and retained; knowledge is revised and retired *(category overview §4)* |
| Document storage infrastructure, versioning of stored files, retention, legal hold | **M24** Document | M61 authors content; M24 stores the underlying manual and diagram files |
| Training courses, curricula, assessment and certification | **M22** Competency | M22 *turns knowledge into courses*; M61 does not deliver training *(category boundary map)* |
| Competency assessment and technician qualification | **M22** Competency | — |
| Quality checklists, non-conformance, CAPA | **M23** Quality | M23 identifies what should be documented; M61 documents it |
| Diagnostic templates executed on a job | **M01** SRM | A diagnostic template is an executed, recorded instrument; a troubleshooting tree is guidance |
| Fault taxonomy, repair operations, rBOM, standard repair times | **M37** Catalogue | M61 links to the taxonomy; it does not define it |
| Acting on a recall or technical bulletin | **M01** SRM | M61 receives and distributes; M01 executes the campaign *(category boundary map)* |
| Brand partner relationship and authorisation management | **M40** Partner | M61 receives bulletins; M40 owns the relationship |
| The conversational AI assistant itself | **M32** Conversational AI | M32 consumes M61 as a source; it is not an M61 feature |
| Customer complaint handling | **M34** Customer Experience | — |
| Marketing and campaign content | **M35** Marketing | Customer FAQs are support content, not marketing content |
| Product catalogue content and specifications | **M37** Catalogue | Specifications are catalogue attributes |
| Internal IT service knowledge for staff systems | **M66** Internal IT Service Management | Different audience, different lifecycle |

### 3.3 Shared Concepts

| Concept | M61's Role | Owning Module |
|---|---|---|
| Knowledge article | **Owner** | M61 |
| Troubleshooting tree | **Owner** | M61 |
| Diagnostic template | Not owned; linked | M01 |
| Fault code, repair operation, model | Links to; never defines | M37 |
| Manual, diagram, schematic file | **Owner** of the library entry; M24 stores the file | M61 (entry) / M24 (file) |
| Training course | Not owned; M22 may derive one from an article | M22 |
| Brand technical bulletin | **Owner** of receipt and distribution; M01 acts | M61 |
| Recall notice | Receives and distributes; M09 and M01 execute | M61 → M09 / M01 |
| Customer FAQ | **Owner**, with separate publication control | M61 |
| Expertise map | **Owner** | M61 |
| Article usefulness | **Owner** of the measure | M61 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **Knowledge-Centered Service (KCS)** | Knowledge captured and refined *in the workflow* as issues are solved, rather than by a separate authoring team; articles improved by use; contribution as part of the job, not extra to it | **The central methodology.** Capture at the moment of resolution, improve on reuse, and treat knowledge contribution as part of doing the work. Industry evidence reports materially improved first-resolution times within three to nine months of adoption | KCS's full licensing and coaching apparatus; the practices are adopted, the certification programme is not |
| **Field service knowledge practice** | Technicians arriving with the knowledge and tools to fix it first time; documented failure data shared across the workforce | **Offline, context-aware article delivery on the technician app** — the single design decision that determines whether the module changes first-time fix or merely exists | Desktop-oriented knowledge portals; a technician at a bench or on a rooftop does not open a laptop |
| **ServiceNow / Salesforce Knowledge** | Article types, versioning, approval workflow, feedback, context-aware surfacing on the case, knowledge-from-case creation | **Article types with distinct templates**, **context-aware surfacing on the work item**, and **create-article-from-resolution** as a one-tap flow | Their platform coupling and the assumption of a desk-based support agent as the primary author |
| **IFS Knowledge Management** | Service knowledge tied to equipment, fault and operation structures | **Linkage to the operational spine** — fault code, repair operation, brand, model and part — so retrieval is by *what the technician is looking at*, not by keyword luck | — |
| **Automotive technical information systems** (Mitchell, Alldata class) | Wiring diagrams, component locations, procedures and bulletins indexed by vehicle and system | **Model-indexed diagram and procedure library with bulletin integration** — directly analogous to indexing by device model and brand | Licensing a third-party technical database: none covers the Bangladeshi mobile, appliance and IT device mix, so the library must be built and curated internally |
| **Stack Overflow / community Q&A patterns** | Voting, accepted answers, reputation, duplicate detection, decay of unmaintained content | **Usefulness voting and contributor recognition**, and **staleness detection**. The category risk *"knowledge base becomes stale and distrusted"* is exactly what these mechanisms exist to prevent | Open unmoderated contribution; brand-authorised repair procedures require technical review before publication |
| **Odoo 19 + OCA** — `document_page`, `document_page_approval`, `attachment_indexation`, `knowledge` | Page-based articles with hierarchy, approval workflow and full-text indexing of attachments | **`document_page` with approval as the L2 authoring base**, and shared indexing with M24 | Its assumption that articles are internal wiki pages — offline distribution, tree authoring and context surfacing have no equivalent |

**Design position.** 1000FiX differs from the benchmarks in six ways.

First, **capture happens at the bench, in Bengali, on a phone**. The dominant author is a
specialist technician who has just solved something difficult, not a technical writer. Capture
must take under three minutes, accept voice and photographs, tolerate rough language, and be
improved later by a reviewer. A knowledge system that requires an author to sit at a desk and
write English prose will capture nothing — this is the most common failure mode of corporate
knowledge bases and the one most likely to defeat this module.

Second, **offline is the primary mode, not a degraded one**. P02's non-negotiable requirements
include full offline operation for 24 hours and offline access to repair manuals, diagrams and
past repair notes. A scoped, current article set — for the technician's brands, models and
skill level — is resident on the device. Diagrams are the largest payload and the most valuable
content, so the sync strategy is a genuine engineering problem, not a checkbox.

Third, **articles are indexed against the operational spine, not a folder tree**. A technician
opens a job for a specific model with a specific fault code; the relevant procedure, diagram and
known issues are already there. Search is the fallback, not the path.

Fourth, **usefulness is measured and acted on**. Every article carries "did this resolve it?"
answered in one tap on the job. Articles that stop resolving faults, stop being used, or fall
below a rating threshold are flagged for revision or retirement. The category KPI is a **> 4.0/5
usefulness rating** — a measure of whether the content works, not whether it exists.

Fifth, **knowledge capture is a definition-of-done item on complex repairs**. The category risk
mitigation states it directly. A Level 3 board-level repair, a first-time model, or a repair
that took materially longer than its standard time all prompt capture before the job closes.
This is the mechanism that converts tacit expertise into institutional knowledge, and it works
only because it is attached to work that is already happening.

Sixth, **customer-facing knowledge is the same content with different publication control**. A
troubleshooting guide that helps a technician can, edited and approved separately, help a
customer avoid raising a job at all. One authoring system, two audiences, two approval paths —
never two systems that drift apart.

---

## 5. Functional Areas & Features

### 5.1 Authoring, Structure & Publication

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-KMS-001 | Article types | Support distinct article types — repair procedure, fault→fix solution, technique note, tool guide, safety note, known issue, FAQ, how-to — each with its own template and required sections | P0 | L2 |
| FR-KMS-002 | Bilingual authoring | Author in Bengali or English with the other language optional, and never block publication of a useful Bengali article for lack of an English translation | P0 | L5 |
| FR-KMS-003 | Rich content | Support text, annotated images, diagrams, short video, voice notes and step-by-step structured procedures | P0 | L5 |
| FR-KMS-004 | Technical library entries | Register manuals, service manuals, wiring and board diagrams, schematics, exploded views and parts diagrams as library entries indexed by brand and model, with files stored in M24 | P0 | L5 |
| FR-KMS-005 | **Troubleshooting trees** | Author versioned branching decision trees from symptom to resolution, with measurements, checks and outcomes at each node, and links to procedures and parts | P0 | L5 |
| FR-KMS-006 | Operational linkage | Link every article and tree to fault codes, repair operations, brands, models, device categories and parts from M37 | P0 | L5 |
| FR-KMS-007 | Versioning and superseding | Version articles, retain prior versions, mark superseded content clearly, and never leave two contradictory articles both current | P0 | L2 |
| FR-KMS-008 | Technical review and approval | Route articles for technical review by a qualified reviewer before publication, with reviewer competence checked against M22 | P0 | L2 |
| FR-KMS-009 | Safety and warranty gating | Require additional approval for articles touching safety, brand-authorised procedures or anything that could void a warranty | P0 | L5 |
| FR-KMS-010 | Customer-facing publication | Publish an approved, separately-edited derivative to the customer knowledge base with its own approval path and plain-language check | P1 | L5 |
| FR-KMS-011 | Article templates and quality | Enforce required sections per type — symptom, applicability, safety, tools, steps, verification, common mistakes — and score completeness | P1 | L5 |
| FR-KMS-012 | Bulk import of manuals | Import brand manual and diagram sets in bulk, index by model, and make them searchable including their text content | P1 | L5 |

### 5.2 Search, Surfacing & Offline Access

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-KMS-013 | Bilingual search | Search articles, trees and library content in Bengali and English with typo tolerance, transliteration handling and symptom-phrase matching | P0 | L5 |
| FR-KMS-014 | Ranking by usefulness | Rank results by demonstrated resolution rate and rating, not only by text relevance | P0 | L5 |
| FR-KMS-015 | **Context-aware surfacing** | Present the relevant procedure, diagram, tree and known issues automatically on a service order, repair order, MSP ticket or live conversation, from its model and fault code | P0 | L5 |
| FR-KMS-016 | Search within a diagram set | Search inside manual and diagram content by extracted text, and open at the relevant page | P1 | L5 |
| FR-KMS-017 | **Offline article set** | Maintain a scoped, current offline set on the technician application by the technician's brands, models, skill level and recent work, within a declared storage budget | P0 | L4 |
| FR-KMS-018 | Offline sync strategy | Synchronise incrementally, prioritise by likely need, defer large media on metered connections, and never leave a stale article presented as current | P0 | L4 |
| FR-KMS-019 | Offline usage capture | Record which articles were opened and whether they resolved the fault while offline, and replay on reconnection | P1 | L4 |
| FR-KMS-020 | Contact-centre surfacing | Surface articles and customer-safe guidance in the P10 agent console during a live conversation, with one-tap send to the customer | P1 | L5 |
| FR-KMS-021 | AI assistant source | Expose approved, current articles as a governed source for M32, with citation of the source article and exclusion of unapproved content | P1 | L5 |
| FR-KMS-022 | Customer self-help | Serve the customer knowledge base in P01 with symptom-led navigation, in Bengali, on a 3G connection | P1 | L5 |

### 5.3 Capture in the Flow of Work

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-KMS-023 | One-tap capture from a job | Create a draft article from a completed job, pre-filled with model, fault code, operation, parts used and evidence photographs already captured | P0 | L5 |
| FR-KMS-024 | Three-minute capture | Allow a technician to capture a solution in under three minutes on a phone, in Bengali, using voice, photographs and short text | P0 | L5 |
| FR-KMS-025 | Capture prompts | Prompt for capture on Level 3 repairs, first-time models, repairs materially exceeding standard time, and repairs resolving a fault with no existing article | P0 | L5 |
| FR-KMS-026 | Definition-of-done linkage | Make knowledge capture a completion condition on declared complex-repair classes, configurable by repair level and device category | P1 | L5 |
| FR-KMS-027 | Draft improvement queue | Route rough captured drafts to a reviewer or technical writer for structuring, without discarding the technician's original words | P0 | L5 |
| FR-KMS-028 | Capture from quality and warranty | Create draft articles from M23 verified fixes and recurring M09 claim-rejection causes | P1 | L5 |
| FR-KMS-029 | Contribution recognition | Track contribution, review and resolution-attribution per contributor, and surface it for recognition and in M57 performance context | P1 | L5 |

### 5.4 Health, Bulletins & Analytics

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-KMS-030 | Usefulness feedback | Capture "did this resolve it?", a rating and optional comment at the point of use, in one tap, online or offline | P0 | L5 |
| FR-KMS-031 | Article health and staleness | Compute health from review date, usage trend, resolution rate and rating; flag stale, unused and low-rated articles for revision or retirement | P0 | L5 |
| FR-KMS-032 | Mandatory review cycle | Require review of every published article at its declared cycle, escalate overdue reviews, and mark overdue articles visibly to users | P0 | L5 |
| FR-KMS-033 | **Coverage and gap analysis** | Report fault codes, models and repair operations with no article or a poor one, ranked by job volume, and drive the authoring backlog from it | P0 | L5 |
| FR-KMS-034 | Brand bulletins and notices | Receive brand technical bulletins, service notices and recall notifications; classify, link to models and faults, distribute to affected technicians and require acknowledgement | P0 | L5 |
| FR-KMS-035 | Expertise mapping | Derive who knows what from contribution, review and resolution activity, and surface it for escalation routing and succession planning | P2 | L5 |
| FR-KMS-036 | Knowledge analytics | Report usage, resolution attribution, first-time-fix contribution, coverage, contributor activity and time-to-publish | P0 | L5 |

*(Full requirement text is mirrored in `05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md`.)*

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Offline set scoping** | The offline article set is computed per technician from brands, models, skill level and recent work, bounded by a declared storage budget, and recomputed as assignments change |
| T-02 | **Media budget discipline** | Diagrams and video are the bulk of the payload. Media is served at device-appropriate resolution with progressive enhancement, and large assets are deferred on metered connections |
| T-03 | **Staleness is visible offline** | A cached article carries its version and review status; an article that has been superseded or has gone overdue for review is visibly marked even before the device reconnects |
| T-04 | **Content-addressed media** | Media is stored in M24's content-addressed storage and referenced, never duplicated per article version |
| T-05 | **Bilingual search index** | Typo-tolerant index over Bengali and English with transliteration handling and symptom-phrase synonyms; index lag ≤ 60 s after publication |
| T-06 | **Ranking from behaviour** | Ranking blends text relevance with observed resolution rate and rating; the weighting is configurable and its effect measurable |
| T-07 | **Context resolution performance** | Surfacing relevant knowledge for a job resolves in ≤ 200 ms p95, because anything slower will not be looked at |
| T-08 | **Idempotent offline feedback** | Usefulness feedback captured offline replays exactly once on reconnection |
| T-09 | **Tree execution is guidance, not a record** | Troubleshooting tree traversal is advisory. Where a decision must be *recorded*, it belongs to M01's diagnostic template, not here — the two must never be confused in the data |
| T-10 | **Governed AI source** | Only approved, current, non-superseded articles are exposed to M32; every AI answer cites its source article and its version |
| T-11 | **Separate customer publication** | Customer-facing derivatives are separate records with their own approval state; an internal edit never propagates to customers automatically |
| T-12 | **Attribution integrity** | Resolution attribution links an article view to a subsequent successful resolution with a declared, auditable method — no causal claim is made that the data does not support |
| T-13 | **Bulk manual ingestion** | A brand manual set of thousands of pages ingests, extracts text, indexes by model and becomes searchable without manual page handling |
| T-14 | **Article-to-record separation** | M61 stores no records. Any content that constitutes a record is filed in M24 and referenced — enforced by review, not left to convention |
| T-15 | **Performance envelope** | Search ≤ 400 ms p95 · context surfacing ≤ 200 ms p95 · article open ≤ 500 ms online and ≤ 100 ms offline · offline set sync ≤ 5 minutes on a 3G connection for an incremental update |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M61 |
|---|---|---|
| **Junior technician** | Phones a senior technician, or guesses, or returns the device unfixed | Opens the job and sees the procedure, the diagram and the known issues for that exact model and fault |
| **Senior / specialist technician** | Is interrupted constantly; their expertise leaves with them | Captures a solution once in three minutes; is recognised for it; is interrupted less |
| **Workshop supervisor** | Allocates the hard jobs to the same two people | Sees the expertise map, and sees capability spreading as articles land |
| **Field technician** | Arrives without the information needed and must return | Carries a scoped offline library on the phone, including diagrams, with no connectivity required |
| **Contact centre agent** | Escalates anything technical | Resolves common faults on the call using customer-safe guidance |
| **Customer** | Raises a job for something they could have resolved | Finds symptom-led self-help in Bengali on their phone |
| **Quality Manager** | Sees the same fault recur with no shared fix | Turns verified fixes into articles and watches the recurrence fall |
| **HR / training** | Builds courses from scratch | Builds courses in M22 from articles the workforce already uses |
| **CEO** | Carries an invisible capability risk in a handful of people | Sees coverage of the top fault codes and the expertise concentration behind them |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **First-time fix improvement** | Context-aware, offline knowledge at the point of work | **+4 percentage points attributable to knowledge use** *(category KPI)*, contributing to M01's **88% first-time fix** target. Each avoided return visit removes a full technician journey and a second customer appointment |
| **Technician productivity** | Less searching, less phoning, less rediscovery of solved problems | Contributes to the **BDT 130 lac/year** technician productivity benefit attributed to M02 and M26 |
| **Capability protection** | Documented board-level procedures across 17+ brands | Mitigates a **High**-rated risk of capability loss. The exposure is not a margin figure — it is whether a class of repair remains possible at all when a specific person is unavailable |
| **Reduced escalation load on specialists** | Junior technicians self-serve on documented faults | Releases scarce Level 3 capacity for genuinely novel work, which is where its value actually is |
| **Faster competence ramp** | New technicians learn from articles used in real work rather than only in classrooms | Shortens time-to-productive for new hires; supports M22's competency progression |
| **Contact-centre resolution** | Agents resolve common faults without dispatch | Supports the **> 78% first-contact resolution** target in P10 |
| **Customer deflection** | Self-help resolves faults that would otherwise become jobs | Supports the P01 self-service targets and removes low-value job volume from the network |
| **Coverage of the top 100 fault codes** | Systematic authoring backlog driven by gap analysis | **100% coverage** *(category KPI)* — the concrete, measurable form of "we have written down what we know" |

> **Discipline note.** The +4 point first-time-fix figure is the category's own target and is
> **attributable**, not additive — it is a component of M01's first-time-fix improvement, not a
> separate benefit. No standalone revenue is claimed for M61, and the capability-protection
> benefit is deliberately stated as risk mitigation rather than converted into a number the data
> does not support.

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Institutional memory** | Expertise stops being personal property and becomes a company asset that survives resignation, retirement and illness |
| **Reduced key-person dependency** | A business whose hardest capability rests on fifteen people is fragile in a way that does not appear on any report until it fails |
| **Equity of capability** | A junior technician in a district branch gets the same knowledge as a specialist in Dhaka. This is the clearest way the ERP reduces the gap between the centre and the network |
| **Recognition of craft** | Contribution tracking makes expertise visible and creditable, which is how a technical culture retains its best people |
| **Bengali as a technical language** | Most technical documentation in this field exists only in English. Building a Bengali technical library is a genuine contribution to the workforce's capability, not merely a localisation task |
| **Brand partner confidence** | Documented, reviewed, brand-consistent procedures are evidence of a controlled service operation |
| **Foundation for AI assistance** | M32 and M26 are only as good as the corpus behind them. A curated, rated, current article set is the difference between a useful assistant and a plausible one |
| **Succession planning** | The expertise map tells the company where its knowledge is concentrated, before that concentration becomes a crisis |

---

## 8. Lifecycle & State Model

M61 owns two lifecycles: the **article** and the **brand bulletin**.

### 8.1 Knowledge Article

```
              ┌──────────┐
              │ CAPTURED │ from a job, a quality fix, a claim cause, or direct authoring
              └────┬─────┘ (rough, Bengali, voice and photographs accepted)
                   │ enters the improvement queue
              ┌────▼──────────┐
              │     DRAFT     │ structured against the type template
              └────┬──────────┘
                   │ submitted for technical review
              ┌────▼──────────┐
              │  IN REVIEW    │──── returned ──► DRAFT (reviewer comments retained)
              └────┬──────────┘
                   │ reviewer qualified; safety/warranty gate applied where needed
              ┌────▼──────────┐
     ┌───────►│   PUBLISHED   │  live internally; in offline sets; usable by M32
     │        └────┬──────────┘
     │             │
     │      ┌──────┼───────────────────┬──────────────────┐
     │      │      │                   │                  │
     │      ▼      ▼                   ▼                  ▼
     │  ┌────────────┐        ┌────────────────┐  ┌────────────────┐
     │  │ CUSTOMER   │        │  REVIEW DUE    │  │    FLAGGED     │
     │  │ PUBLISHED  │        │ (cycle reached;│  │ (low rating,   │
     │  │ (separate  │        │  visibly marked│  │  low resolution│
     │  │  approval) │        │  to users)     │  │  rate, unused) │
     │  └────────────┘        └───────┬────────┘  └───────┬────────┘
     │                                │                    │
     │                                └──────────┬─────────┘
     │                                           │
     │                                  ┌────────▼────────┐
     └──────────────────────────────────┤    REVISION     │
                                        └────────┬────────┘
                                                 │ superseded by a new version
                                        ┌────────▼────────┐
                                        │   SUPERSEDED    │ retained, visibly marked,
                                        └────────┬────────┘ removed from offline sets
                                                 │ no longer applicable
                                        ┌────────▼────────┐
                                        │     RETIRED     │ searchable in archive only
                                        └─────────────────┘

  An article overdue for review is marked as such wherever it appears, including
  offline — the direct control against "the knowledge base becomes stale and distrusted".
```

### 8.2 Brand Bulletin / Notice

```
RECEIVED ──► CLASSIFIED (bulletin / service notice / recall) ──► LINKED (models, faults, parts)
   ──► DISTRIBUTED (affected technicians and branches) ──► ACKNOWLEDGED (tracked)
   ──► ACTIONED (recall → M09/M01 campaign; procedure change → article revision)
   ──► CLOSED
```

### Transition Guards

| From | To | Guard | Actor |
|---|---|---|---|
| Captured | Draft | Assigned to the improvement queue; original contributor's words retained | Reviewer / technical writer |
| Draft | In Review | Required sections for the article type complete; operational links (model, fault, operation) present | Author |
| In Review | Published | Reviewer holds current competence on the relevant brand or repair level per M22; reviewer ≠ author | Qualified reviewer |
| In Review | Published *(safety/warranty content)* | Additional approval obtained from the Quality Manager or brand-authorised reviewer | Quality Manager |
| Published | Customer Published | Separately edited derivative approved for plain language and customer safety | Quality Manager + Customer Service Manager |
| Published | Review Due | Review cycle reached | System |
| Published | Flagged | Rating below threshold, resolution rate falling, or no use within the declared window | System |
| Review Due / Flagged | Revision | Owner accepts the revision task | Owner |
| Revision | Superseded | A new version published | Reviewer |
| Any | Retired | No longer applicable — model obsolete, procedure withdrawn, brand guidance changed — with a reason recorded | Quality Manager |
| Received | Distributed *(bulletin)* | Classified and linked to affected models, faults or parts | Technical library owner |
| Distributed | Actioned | Recall routed to M09/M01; procedure change routed to article revision | System |

---

## 9. Business Rules

Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-KMS-01 | M61 stores knowledge, never records; anything constituting a record is filed in M24 and referenced | **H** | Quality Manager |
| BRU-KMS-02 | An article cannot be published without technical review by a qualified reviewer who is not its author | **H** | Quality Manager |
| BRU-KMS-03 | Articles touching safety, brand-authorised procedures or warranty validity require additional approval | **H** | Quality Manager |
| BRU-KMS-04 | Two contradictory articles cannot both be Published for the same model and fault; publication supersedes | **H** | Quality Manager |
| BRU-KMS-05 | A superseded or retired article is removed from offline sets and from the M32 source corpus | **C** | CTO |
| BRU-KMS-06 | An article overdue for review is visibly marked wherever it appears, including offline | **C** | Quality Manager |
| BRU-KMS-07 | Every published article carries a review cycle and an owner at all times | **H** | Quality Manager |
| BRU-KMS-08 | A rough Bengali capture is never discarded for being unstructured; it enters the improvement queue | **H** | Quality Manager |
| BRU-KMS-09 | The contributor's original words are retained alongside any edited version | **H** | Quality Manager |
| BRU-KMS-10 | Knowledge capture is a completion condition on declared complex-repair classes | **H** | Ops Director |
| BRU-KMS-11 | Customer-facing derivatives have a separate approval; an internal edit never propagates automatically to customers | **H** | Customer Service Manager |
| BRU-KMS-12 | Only approved, current articles are exposed to M32, and every AI answer cites the source article and version | **H** | CTO |
| BRU-KMS-13 | A troubleshooting tree is guidance; where a decision must be recorded it belongs to M01's diagnostic template | **H** | CTO |
| BRU-KMS-14 | Brand technical bulletins are distributed to every affected technician with acknowledgement tracked | **H** | Quality Manager |
| BRU-KMS-15 | A recall notice is routed to M09 and M01 for execution and is never actioned within M61 | **H** | Warranty Officer |
| BRU-KMS-16 | Brand manuals and diagrams are used within the terms of the brand agreement, and their redistribution is scoped accordingly | **H** | Finance Director / Legal |
| BRU-KMS-17 | Resolution attribution states its method and makes no causal claim the data does not support | **H** | CTO |
| BRU-KMS-18 | An article flagged for low usefulness is revised or retired within the declared period; it is not left published | **A** | Quality Manager |

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.knowledge.article` | `fix_knowledge_article` | The article | code, type, title_bn, title_en, body_bn, body_en, state, version, owner_id, author_id, reviewer_id, review_cycle_months, next_review_at, published_at, superseded_by_id, health_score |
| `fix.knowledge.article.version` | `fix_knowledge_article_version` | Version history | article_id, version, body_snapshot, changed_by, changed_at, change_note, original_capture_text |
| `fix.knowledge.link` | `fix_knowledge_link` | Operational linkage | article_id, link_type, fault_code_id, operation_id, brand_id, model_id, category_id, part_item_id, relevance_weight |
| `fix.knowledge.media` | `fix_knowledge_media` | Media references | article_id, media_type (image/diagram/video/voice), document_ref, caption_bn, caption_en, sequence, size_class |
| `fix.technical.library` | `fix_technical_library` | Manuals and diagrams | entry_type, brand_id, model_ids, title, document_ref, page_count, extracted_text_ref, source, licence_terms, indexed_at |
| `fix.troubleshooting.tree` | `fix_troubleshooting_tree` | Tree header | code, title_bn, title_en, category_id, brand_id, model_ids, version, state, owner_id |
| `fix.troubleshooting.node` | `fix_troubleshooting_node` | Tree nodes | tree_id, parent_id, node_type (question/check/measurement/outcome), text_bn, text_en, options_json, article_id, part_item_ids, safety_note |
| `fix.knowledge.feedback` | `fix_knowledge_feedback` | Usefulness feedback | article_id, version, user_id, context_ref, resolved (yes/no/partial), rating, comment, captured_at, captured_offline |
| `fix.knowledge.usage` | `fix_knowledge_usage` | Usage events | article_id, version, user_id, context_type, context_ref, opened_at, duration_s, offline, followed_by_resolution |
| `fix.knowledge.attribution` | `fix_knowledge_attribution` | Resolution attribution | article_id, service_order_ref, method, confidence, first_time_fix, attributed_at |
| `fix.knowledge.health` | `fix_knowledge_health` | Computed health | article_id, period, usage_count, resolution_rate, avg_rating, days_since_review, staleness_flag, health_score, action_required |
| `fix.knowledge.gap` | `fix_knowledge_gap` | Coverage gaps | subject_type (fault/model/operation), subject_id, job_volume, existing_article_id, gap_type (none/poor/stale), priority_rank |
| `fix.knowledge.capture.prompt` | `fix_knowledge_capture_prompt` | Capture triggers | trigger_type, condition_json, repair_level, category_id, is_dod_condition, active |
| `fix.knowledge.capture` | `fix_knowledge_capture` | Raw captures from the field | source_ref, captured_by, captured_at, raw_text_bn, voice_ref, media_refs, model_id, fault_code_id, state, resulting_article_id |
| `fix.customer.article` | `fix_customer_article` | Customer-facing derivative | source_article_id, title_bn, title_en, body_bn, body_en, state, approved_by, published_at, plain_language_checked |
| `fix.brand.bulletin` | `fix_brand_bulletin` | Bulletins and notices | brand_id, reference, type (bulletin/notice/recall), title, content_ref, received_at, affected_models, affected_faults, affected_parts, state, action_ref |
| `fix.bulletin.acknowledgement` | `fix_bulletin_acknowledgement` | Acknowledgement tracking | bulletin_id, user_id, notified_at, acknowledged_at, method |
| `fix.expertise.map` | `fix_expertise_map` | Derived expertise | user_id, subject_type, subject_id, contribution_score, resolution_score, review_score, computed_at, concentration_flag |
| `fix.offline.set` | `fix_offline_set` | Per-technician offline scope | user_id, article_ids, media_refs, total_size, computed_at, last_synced_at, budget_bytes |

### 10.2 Referenced Entities

| Entity | Owned By | Access Pattern |
|---|---|---|
| `fix.document` — manual, diagram and media files | M24 | Storage service; referenced never duplicated |
| `fix.fault.taxonomy`, `fix.repair.operation`, `fix.brand`, `fix.device.model`, `fix.part.item` | M37 | Master data projection |
| `fix.service.order`, diagnosis, resolution, duration vs standard | M01 | Event intake + live read |
| `fix.repair.order`, bench outcomes | M31 | Event intake |
| `fix.asset` — device history | M17 / M49 | Live read |
| `fix.competency`, competence | M22 | Live read — reviewer qualification |
| `fix.nonconformance`, verified fixes | M23 | Event intake |
| `fix.brand.claim` rejection causes | M09 | Event intake |
| `fix.employee`, assignments, skills | M21 | Live read — offline set scoping |
| Brand agreement terms governing manual use | M40 / M08 | Live read |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-KMS-01 | Complex repair completed (Level 3, first-time model, or materially over standard time) | Prompt for knowledge capture, pre-filled with model, fault, operation, parts and evidence photographs | Log the missed prompt; report in coverage analytics |
| AUT-KMS-02 | Repair resolves a fault with no existing article | Prompt for capture and create a gap record if declined | Log |
| AUT-KMS-03 | Capture submitted | Place in the improvement queue and assign a reviewer or technical writer, retaining the original words | Escalate after the declared interval; never discard |
| AUT-KMS-04 | Article submitted for review | Check reviewer competence against M22 and reviewer ≠ author; apply the safety/warranty gate where the content requires | Block submission with the reason |
| AUT-KMS-05 | Article published | Index for search, add to affected technicians' offline sets, expose to M32, notify subscribers to the model or fault | Retry; flag as unindexed rather than blocking publication |
| AUT-KMS-06 | Article superseded or retired | Remove from offline sets and from the M32 corpus; mark visibly in search and archive | Force removal; alert on failure — a stale offline copy is the failure mode this exists to prevent |
| AUT-KMS-07 | Review cycle reached | Assign the review to the owner, mark the article overdue everywhere it appears, and escalate on the declared ladder | Repeat escalation |
| AUT-KMS-08 | Nightly health computation | Compute usage, resolution rate, rating and staleness; flag articles requiring revision or retirement | Log; retry |
| AUT-KMS-09 | Weekly gap analysis | Rank fault codes, models and operations by job volume against article coverage and quality; publish the authoring backlog | Log; retry |
| AUT-KMS-10 | Technician assignment or skill changes | Recompute the offline set within the storage budget and queue an incremental sync | Retain the prior set; retry |
| AUT-KMS-11 | Device reconnects | Sync incrementally, prioritise by likely need, replay offline usage and feedback idempotently | Retry; never drop feedback |
| AUT-KMS-12 | Brand bulletin received | Classify, link to affected models, faults and parts, distribute to affected technicians and branches, track acknowledgement | Escalate to the technical library owner |
| AUT-KMS-13 | Bulletin classified as a recall | Route to M09 and M01 for campaign execution and link the campaign back to the bulletin | Escalate to the Warranty Officer |
| AUT-KMS-14 | Bulletin unacknowledged beyond the declared period | Escalate to the branch manager and workshop supervisor | Repeat |
| AUT-KMS-15 | M23 verifies a CAPA fix of a recurring technical failure | Create a draft article pre-filled from the non-conformance and its root cause | Create a gap record |
| AUT-KMS-16 | M09 records a recurring claim-rejection cause with a technical remedy | Create a draft article and link it to the fault and brand | Log |
| AUT-KMS-17 | Article receives repeated "did not resolve" feedback | Flag for urgent revision, reduce its ranking, and notify the owner | Escalate to the Quality Manager |
| AUT-KMS-18 | Quarterly expertise computation | Recompute the expertise map and flag subjects where knowledge is concentrated in fewer than the declared number of people | Log; report to Ops Director and HR |

---

## 12. Interfaces

### 12.1 Upstream — M61 Consumes

| Source | What | Mechanism |
|---|---|---|
| M37 Catalogue | Fault taxonomy, repair operations, brands, models, parts — the linkage spine | Master data projection |
| M24 Document | Storage for manuals, diagrams, video and images; text extraction | Service call |
| M01 SRM | Completed jobs, diagnosis, resolution, duration vs standard, evidence photographs | Events + REST |
| M31 Workshop | Bench-level repair outcomes and technique context | Events |
| M23 Quality | Verified fixes and failure patterns worth documenting | Events |
| M09 Warranty | Recurring claim-rejection causes with technical remedies; recall notices from brands | Events |
| M22 Competency | Reviewer qualification and technician skill level | Live read |
| M21 Core HR | Assignments and roles for offline set scoping | Live read |
| M17 Asset Registry | Device model context | Live read |
| M40 Partner / M08 Contract | Brand agreement terms governing manual use and redistribution | Live read |
| Brand partners | Technical bulletins, service notices, manual and diagram sets, recall notifications | INT-KMS-01…03 |

### 12.2 Downstream — M61 Provides

| Consumer | What | Mechanism |
|---|---|---|
| **P02 Technician App** | Context-aware articles, diagrams, trees and the offline set; one-tap capture and feedback | REST + offline sync |
| M01 SRM · M31 Workshop | Knowledge surfaced on the job; capture prompts and definition-of-done conditions | REST + projection |
| M02 Field Service | Offline knowledge for field work | Via P02 |
| M05 Managed Services · M06 Data Services | Procedures and known issues for remote and data work | REST |
| **P10 Contact Centre** | Article search and customer-safe guidance during a live conversation | REST |
| **M32 Conversational AI** | Approved, current articles as a governed source corpus with citation | Governed corpus API |
| **P01 Customer Portal** | Customer knowledge base, FAQs and symptom-led self-help | REST |
| M22 Competency | Articles as source material for course construction | REST |
| M23 Quality | Article coverage of known failure modes; documentation status of verified fixes | Projection |
| M09 Warranty · M01 SRM | Recall and bulletin distribution requiring action | Events |
| M34 Customer Experience | Self-help deflection signals | Events |
| M57 Performance | Contribution recognition data *(context only, not a metric)* | Projection |
| M25 BID · M26 AIM | Knowledge usage, resolution attribution, coverage and expertise fact streams | Warehouse extract |

### 12.3 Domain Events Published

| Event | Payload Summary | Principal Consumers |
|---|---|---|
| `knowledge.article_published` | article id, version, links, applicability | P02, M32, M22, M23 |
| `knowledge.article_superseded` / `retired` | article id, successor, reason | **P02 (offline set), M32** |
| `knowledge.capture_submitted` | capture id, contributor, model, fault | Improvement queue, M57 |
| `knowledge.capture_declined` | job ref, prompt type, reason | Coverage analytics |
| `knowledge.gap_identified` | subject, volume, gap type, priority | Authoring backlog, M23 |
| `knowledge.article_flagged` | article id, cause, health score | Owner, Quality Manager |
| `knowledge.review_overdue` | article id, owner, days overdue | Owner, Quality Manager |
| `knowledge.resolution_attributed` | article id, service order, first-time fix | M25, M26 |
| `bulletin.received` | brand, reference, type, affected models | M01, M09, M23 |
| `bulletin.recall_notified` | brand, campaign scope, affected serials context | **M09, M01** |
| `bulletin.unacknowledged` | bulletin, technicians, days overdue | Branch managers, M23 |
| `knowledge.expertise_concentrated` | subject, contributor count, risk flag | Ops Director, HR Director |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-KMS-01 | Brand technical documentation portals (17+) | Inbound | Manual, diagram and schematic acquisition within agreement terms |
| INT-KMS-02 | Brand bulletin and service-notice feeds | Inbound | Technical bulletins and service notices |
| INT-KMS-03 | Brand recall notification channels | Inbound | Recall notices routed to M09 and M01 |
| INT-KMS-04 | Video storage and streaming *(via M24 / CDN)* | Bidirectional | Demonstration video hosting at device-appropriate quality |
| INT-KMS-05 | OCR engine *(shared with M24)* | Outbound | Text extraction from manuals and diagrams for search |

### 12.5 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/knowledge/search` | GET | Bilingual, usefulness-ranked search | P02, P03, P10, P01 |
| `/api/v1/knowledge/context` | POST | Articles, trees and known issues for a job, model and fault | **M01, M31, P02, P10** |
| `/api/v1/knowledge/articles/{id}` | GET | Article with media and version | All consumers |
| `/api/v1/knowledge/articles` | POST | Create a draft or submit a capture | P02, P03 |
| `/api/v1/knowledge/captures` | POST | One-tap capture from a completed job | **P02** |
| `/api/v1/knowledge/articles/{id}/feedback` | POST | Usefulness feedback, offline-replayable | P02, P03, P10 |
| `/api/v1/knowledge/trees/{id}` | GET | Troubleshooting tree for guided traversal | P02, P10 |
| `/api/v1/knowledge/library` | GET | Manuals and diagrams by brand and model | P02, P03 |
| `/api/v1/knowledge/offline-set` | GET | The technician's scoped offline set manifest and delta | **P02** |
| `/api/v1/knowledge/ai-corpus` | GET | Approved, current articles for M32 with version and citation metadata | **M32** |
| `/api/v1/knowledge/customer` | GET | Customer-facing knowledge base | P01, website |
| `/api/v1/knowledge/bulletins` | GET/POST | Bulletins, notices and acknowledgement | P02, P03 |
| `/api/v1/knowledge/gaps` | GET | Coverage gaps ranked by volume | P03, P06 |
| `/api/v1/knowledge/expertise` | GET | Expertise map and concentration flags | P03, P06 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R32 Quality Manager / ISO Coordinator | C R U D A | All — the module's principal owner; safety and warranty approval |
| R05 Operations Director | R A | All — capture definition-of-done policy, expertise concentration |
| R09 Workshop Supervisor | C R U A | Own workshop's domain — review and approve within competence |
| R12 Specialist Technician (L3) | C R U | Author and review within competence — the module's most important contributors |
| R10 Senior Technician | C R U | Author, review within competence |
| R11 Junior Technician | C R | Read, capture, feedback |
| R13 Remote Support Engineer · R14 Data Services Technician | C R U | Own technical domain |
| R08 Service Centre Agent | C R | Read and feedback |
| R34 Contact Centre Agent | R | Read internal and customer-safe content; send to customer |
| R35 Contact Centre Supervisor | C R U | Customer-facing article proposals |
| R28 Warranty Claims Officer | C R | Bulletin and recall handling |
| R22 Account Manager (Corporate) | R | Customer-facing content for corporate clients |
| R30 HR Manager | R | Expertise map for succession planning *(aggregate)* |
| R33 IT / System Administrator | R U | Configuration, offline budgets, integrations |
| R36 Customer | R | **Customer-published content only** |
| R38 External Party — brand partner | R U | Own brand's bulletins and library entries only *(EA-05)* |
| — Technical Library Owner *(new position under R32)* | C R U | Library, bulletins, improvement queue, coverage backlog |

**Field-level restrictions.** Internal articles are never exposed on customer surfaces; only
approved customer derivatives are. Brand manuals and diagrams are scoped by the brand agreement's
redistribution terms and are not downloadable outside declared scope. Contributor identity is
visible internally for recognition; the expertise map's concentration flags are visible only to
R05, R30 and R32. `internal_note` is never exposed externally.

**Segregation of duties.** The reviewer of an article cannot be its author (BRU-KMS-02).
Safety-, warranty- and brand-procedure content requires a second approval beyond technical review
(BRU-KMS-03).

---

## 14. Reports & Analytics

| Report / Dashboard | Audience | Frequency | Key Content |
|---|---|---|---|
| **Coverage and gap backlog** | Quality Manager, Ops Director | Weekly | Fault codes, models and operations with no article or a poor one, ranked by job volume — the authoring priority list |
| Top-100 fault code coverage | Quality Manager, CEO | Monthly | Coverage against the 100% category KPI, with quality of coverage not merely existence |
| Article usefulness | Quality Manager, Technical Library Owner | Weekly | Rating and resolution rate by article, type, brand and model; articles below threshold |
| Article health and staleness | Technical Library Owner | Weekly | Overdue reviews, unused articles, declining resolution rates, retirement candidates |
| Knowledge usage | Ops Director, Quality Manager | Monthly | Opens by role, context, brand, model and offline vs online; most and least used |
| **First-time-fix attribution** | Ops Director, CEO | Monthly | First-time fix on jobs where knowledge was used vs not, with the attribution method stated |
| Capture performance | Ops Director, Workshop Supervisors | Weekly | Capture prompts fired, accepted, declined; captures published; time from capture to publication |
| Contributor recognition | Ops Director, HR Director | Monthly | Contributions, reviews and resolution attribution per contributor |
| **Expertise concentration** | CEO, Ops Director, HR Director | Quarterly | Subjects where knowledge sits with fewer than the declared number of people — the capability-risk report |
| Offline set health | CTO, Ops Director | Weekly | Sync currency, size against budget, stale-article incidents, failed syncs |
| Bulletin distribution and acknowledgement | Quality Manager, Warranty Officer | Per bulletin | Distributed, acknowledged, outstanding, by branch and technician |
| Customer self-help performance | Customer Service Manager, CCO | Monthly | Self-help usage, resolution, and jobs deflected |
| AI source quality | CTO, Quality Manager | Monthly | M32 answers by source article, citation accuracy, answers from stale or missing content |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W7 Target | W9 Target |
|---|---|---|---|---|
| KPI-C61-01 | Knowledge articles covering the top 100 fault codes | 0% | 70% | **100%** |
| KPI-C61-02 | First-time fix improvement attributable to knowledge use | n/a | +2 pts | **+4 pts** |
| KPI-C61-03 | Article usefulness rating | n/a | > 3.6 / 5 | **> 4.0 / 5** |
| KPI-C61-04 | Articles overdue for review | n/a | < 10% | **< 3%** |
| KPI-C61-05 | Capture prompts accepted on complex repairs | 0% | 55% | **> 75%** |
| KPI-C61-06 | Median time from capture to publication | n/a | < 10 days | **< 4 days** |
| KPI-C61-07 | Technicians with a current offline set | 0% | 90% | **> 98%** |
| KPI-C61-08 | Stale articles served offline | n/a | 0 | **0** |
| KPI-C61-09 | Context surfacing latency p95 | n/a | ≤ 300 ms | **≤ 200 ms** |
| KPI-C61-10 | Jobs where knowledge was consulted | 0% | 40% | **> 65%** |
| KPI-C61-11 | Bulletins acknowledged by affected technicians within the declared period | unmeasured | 90% | **100%** |
| KPI-C61-12 | Subjects with knowledge concentrated in fewer than 3 people | unknown | measured | **declining trend** |
| KPI-C61-13 | Contact-centre conversations resolved using knowledge | 0% | 25% | **> 40%** |
| KPI-C61-14 | Customer self-help sessions resolving without a job | 0% | 15% | **> 30%** |

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo `mail`, `portal` | 4% |
| L2 | OCA `document_page`, `document_page_approval`, `attachment_indexation`, `queue_job` | 22% |
| L4 | Offline article and media store within the P02 technician application | 18% |
| L5 | `cd_knowledge_article`, `cd_troubleshooting_tree`, `cd_knowledge_capture`, `cd_knowledge_search`, `cd_brand_bulletin` | 56% |

### 16.2 Custom Development

| CD ID | Component | Type | Effort |
|---|---|---|---|
| CD-C61-01 | `cd_knowledge_article` — article types, bilingual authoring, operational linkage, review workflow, versioning, health scoring, customer derivatives | Odoo module | 4 PW |
| CD-C61-02 | `cd_troubleshooting_tree` — tree authoring, versioning, traversal API, node types and part linkage | Odoo module | 3 PW |
| CD-C61-03 | `cd_knowledge_capture` — one-tap capture from a job, voice and photo capture, improvement queue, prompts and definition-of-done conditions | Odoo module + service | 3 PW |
| CD-C61-04 | `cd_knowledge_search` — bilingual index, usefulness ranking, context surfacing, gap analysis, AI corpus API | Service | 3 PW |
| CD-C61-05 | Offline set computation, delta sync and stale-content invalidation *(with the P02 team)* | Service + mobile | 2 PW |
| CD-C61-06 | `cd_brand_bulletin` — bulletin receipt, classification, distribution, acknowledgement, recall routing; technical library and expertise map | Odoo module | 1 PW |
| | | **Total** | **16 PW** |

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| M24 Document *(W3)* | Manuals, diagrams, video and images are stored there; M61 holds entries and references |
| M37 Catalogue *(W1)* | Fault taxonomy, operations, brands, models and parts are the linkage spine |
| M01 SRM *(W1–W2)* · M31 *(W2)* | Capture originates from completed work; surfacing targets the job |
| P02 Technician App *(W2)* | The primary consumption surface; offline distribution is built with the P02 team |
| M22 Competency *(W5)* | Reviewer qualification |
| M23 Quality *(W5)* | Verified fixes as an authoring source; shared review discipline |
| M40 Partner *(W7)* | Brand agreement terms governing manual use — **scheduled after M61** |

> **Sequencing note.** M61 lands in W6 and M40 in W7, so the brand-agreement terms governing
> manual and diagram redistribution (BRU-KMS-16) are not yet held as structured data when the
> technical library is built. The interim control is to record licence terms as free text on each
> library entry at ingestion and reconcile to M40's authorisation register when it lands. This is
> a known, bounded gap rather than an oversight, and it is why FR-KMS-004 carries `licence_terms`
> on the library entry itself.
>
> **A second concern deserves the board's attention:** M61 is P2/W6, but the capability risk it
> addresses is rated **High** and exists from day one. If a senior specialist leaves in Wave 2,
> nothing in the programme captures what they knew. A **manual capture programme from Wave 2**,
> outside this module, is the pragmatic mitigation — recorded here because M61 inherits the
> consequence.

### 16.4 Data Migration

| Source | Volume | Target Entity | Wave |
|---|---|---|---|
| Brand manual and diagram sets (17+ brands) | Thousands of documents | `fix.technical.library` + M24 storage | W6 |
| Existing informal notes, WhatsApp groups, personal files | Unknown — profiling required | `fix.knowledge.capture` → improvement queue | W6 |
| Business plan FAQ and troubleshooting content | ~50–100 items | `fix.customer.article` | W6 |
| Historical job resolution notes for high-volume faults | Sampled from M01 | Source material for the initial authoring backlog | W6 |

**Migration rule.** There is no legacy knowledge base to migrate — that is the point of the
module. The Wave 6 task is **acquisition and initial authoring**, not migration: ingesting brand
manuals, and writing the first tranche of articles covering the top fault codes by volume.

**This is a content programme, not a software task.** Reaching 100% coverage of the top 100 fault
codes requires perhaps 150–250 authored, reviewed articles. At a realistic rate that is several
months of part-time specialist effort, and it must be resourced explicitly — the build delivers
the system, not the content. A knowledge module delivered empty will be judged a failure
regardless of how well it works.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | A technician captures a solution from a completed job in under three minutes, in Bengali, on a mid-range Android phone, using voice and photographs | Timed observation, twenty samples with real technicians |
| AC-02 | Opening a service order surfaces the relevant procedure, diagram, tree and known issues for that model and fault in ≤ 200 ms | Performance test across ten model/fault combinations |
| AC-03 | A technician works a full day offline with the scoped article set including diagrams, and no article is presented as current when it has been superseded | 24-hour offline field test with an induced supersession |
| AC-04 | A superseded or retired article is removed from every offline set and from the M32 corpus within the declared window | Propagation test |
| AC-05 | An article cannot be published without technical review by a qualified reviewer who is not its author | Negative test via UI and API |
| AC-06 | Safety, warranty and brand-procedure content requires the additional approval | Negative test per content class |
| AC-07 | A rough Bengali capture is never lost; it appears in the improvement queue with the contributor's original words retained | End-to-end test |
| AC-08 | Search returns usefulness-ranked bilingual results in ≤ 400 ms p95 over the full corpus | Load test |
| AC-09 | Usefulness feedback captured offline replays exactly once on reconnection | Chaos test with duplicated sync |
| AC-10 | Gap analysis ranks uncovered fault codes by job volume and drives a visible authoring backlog | Demonstration against real M01 volume data |
| AC-11 | A brand recall notice routes to M09 and M01 and is never actioned within M61 | Negative and positive test |
| AC-12 | Bulletin distribution reaches every affected technician with acknowledgement tracked and escalated | Scripted scenario |
| AC-13 | M32 answers cite the source article and version, and never draw on unapproved or superseded content | AI corpus test |
| AC-14 | Coverage of the top 100 fault codes reaches 100% with reviewed, rated articles at the Wave 9 gate | Coverage report + usefulness ratings |
| AC-15 | Named business super-users — including at least three specialist technicians — sign off UAT for all P0 and P1 requirements; zero critical or high security findings | Signed UAT record + security review record |

**Definition of done:** all 17 criteria in `02-02` §8 plus the criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | Who authors the first 150–250 articles, and is that effort resourced? The build delivers the system; the content is a separate programme | Quality Manager / Ops Director | **W5 — blocking for the KPI targets** |
| Q-02 | Should a manual knowledge-capture programme start in Wave 2, given that M61 arrives in Wave 6 and the capability risk exists now? | Ops Director / CEO | **W2 — risk decision** |
| Q-03 | Do brand agreements permit 1000FiX to hold, index and redistribute manuals and diagrams internally, and on what terms? *(cross-reference M37 Q-03)* | Finance Director / Legal | **W6 — blocking for the technical library** |
| Q-04 | What is the offline storage budget per technician device, given that diagrams dominate the payload and P02 targets a 3 GB RAM mid-range Android? | CTO / Ops Director | W6 build |
| Q-05 | Which repair classes carry knowledge capture as a definition-of-done condition, and does that risk slowing job closure? | Ops Director / Quality Manager | W6 build |
| Q-06 | What is the article review cycle — 6, 12 or 24 months — and does it vary by article type? | Quality Manager | W6 build |
| Q-07 | Should contribution feed M57 incentives, or remain recognition only? The design supplies context only | Ops Director / HR Director | W6 build |
| Q-08 | What attribution method is defensible for the "+4 points first-time fix attributable to knowledge use" KPI? A weak method makes the KPI unarguable in either direction | Quality Manager / CTO | **W6 — the KPI depends on it** |
| Q-09 | Is customer-facing knowledge owned by Customer Service or by Quality, given it derives from internal technical content? | Customer Service Manager / Quality Manager | W6 build |

---

## 19. References

**Internal**
`03_Modules/I_Governance_Risk_Quality_and_Knowledge/_CATEGORY_OVERVIEW.md` §4, §5, §8, §10 ·
`M24_Document_Records_and_ESignature.md` §3, §12 ·
`M23_Quality_Management_System.md` §12 ·
`M60_Governance_Risk_and_Compliance.md` §3 ·
`03_Modules/A_Service_Delivery_and_Operations/M01_Service_Request_and_Order_Management.md` §5.3, §5.6 ·
`03_Modules/C_Commercial_Pricing_and_Revenue/M37_Product_and_Service_Catalogue_Management.md` §5.3, §5.6 ·
`03_Modules/C_Commercial_Pricing_and_Revenue/M09_Warranty_Protection_Plans_and_Claims.md` §5.5 FR-WTY-059 ·
`03_Modules/C_Commercial_Pricing_and_Revenue/M40_Partner_Channel_Alliance_and_Franchise.md` §5.2 ·
`02_Architecture/02-02_Module_Catalogue_Master_Register.md` §2, §8 ·
`05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md` ·
`05-04_Role_Permission_and_Access_Matrix.md` §5, §8 EA-05 ·
`04_Portals_and_Applications/04-00_Portal_Suite_Overview.md` P01 §Support, P02 §Knowledge, P10 §Handling ·
`06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md`

**Workspace evidence**
`1000FiX Business Plan` §Knowledge Base — FAQ articles, troubleshooting guides, video tutorials, user manuals ·
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` §8.22 ·
`1000FiX_ERP_System_Comprehensive_URD.md` §15 ·
`1000FiX_Services_Company_Profile.md` §Core Services

**External benchmark**
Knowledge-Centered Service (KCS) — capture and refine knowledge in the workflow; reported improvements in first-resolution time within 3–9 months of adoption ·
Field service knowledge practice — first-time fix depends on the technician arriving with the knowledge; documented failure data shared across the workforce ·
ServiceNow / Salesforce Knowledge — article types, versioning, approval, context-aware surfacing, knowledge-from-case creation ·
IFS Knowledge Management — knowledge tied to equipment, fault and operation structures ·
Automotive technical information systems (Mitchell, Alldata) — model-indexed diagrams, procedures and bulletins ·
Community Q&A patterns — usefulness voting, contributor recognition, content decay detection ·
Odoo 19 / OCA `document_page`, `document_page_approval`, `attachment_indexation`

---

*Module M61 · Category I · 1000FiX ERP System v2.0 · CONFIDENTIAL*
