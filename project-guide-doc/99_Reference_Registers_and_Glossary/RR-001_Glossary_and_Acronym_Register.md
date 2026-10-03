---
id: RR-001
title: Glossary and Acronym Register
category: 99 — Reference, Registers & Glossary
code: RR
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-19
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Enterprise Architecture
approver: Chief Technology Officer
standards_basis: ISO 704:2022 · ISO 1087:2019 · ISO 30042:2019 (TBX) · ISO/IEC 11179-5:2015 §5 (definition principles) · ISO 12620:2019
traces_to: PGD-000 Category 99 RR-001 · _CATEGORY_OVERVIEW "The vocabulary problem RR-001 must still close" · 99-01 (unwritten) · RF-001 · BN-003 · BN-004 · CG-004 · 00-06 C-02 · 05-02 §3
depends_on: RR-002 · RR-003
verified_on: 2026-08-19
priority: P1
needed_by: W1
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
enumeration_timestamp: 2026-08-19 02:41 (+06)
rule_prefix: TRM — verified to return zero occurrences in identifier form across all 782 markdown files of the workspace before allocation, at 2026-08-19 02:41 (+06). Candidates GLS, VOC and LEX were also free; GLS was rejected as visually close to the GL- defect series in RF-001 §4.3
---

# RR-001 — Glossary and Acronym Register
# 1000FiX ERP System & Portal Suite v2.0

### Category 99 · Code `RR` · ISO 704:2022 · ISO 1087:2019 · ISO 30042:2019

---

> **Before writing, read this.**
>
> 1. **`PG-01` Register-first.** Registered in `PGD-000` as `RR-001`, status ◐, `P1`, needed by `W1`.
> 2. **`PG-03` / `RG-06` Count, do not consult.** Every usage figure was counted from the
>    filesystem at **2026-08-19 02:41 (+06)**; the commands are in §4.1.
> 3. **`PG-06` Cite standards.** ISO 704:2022 and ISO 1087:2019 govern term formation and
>    definition; departures in §2.1.
> 4. **`PG-M4` Verify citations.** `verified_on: 2026-08-19`.

---

## 1. Purpose

This document adjudicates **what the words mean**. Where `RR-002` says an identifier is
well-formed and who allocated it, this document says what the thing it names *is* — and, where
the estate uses several words for one thing or one word for several things, which usage is
correct and what happens to the rest.

It exists because **782 files across five repositories were written by different authors against
different benchmarks and no document ever adjudicated the vocabulary.** The visible symptom is
the service-delivery lifecycle: *service order*, *work order*, *repair order*, *job card*, *job
sheet*, *dispatch job*, *job batch*, *service request* and *RMA* are all in live use, across at
least fifteen module specifications, with no single statement of how they relate. The
consequence is not stylistic. A technician's mobile app that shows "your jobs" and a workshop
board that shows "repair orders" are showing **different database entities**, and a report that
counts "jobs completed" is answerable in five ways.

> **What this document is not.** It is not the customer-facing bilingual glossary — that is
> `BN-003`, which binds one approved Bengali form to 227 controlled terms and is authoritative for
> everything a customer sees. It is not the content-estate acronym register — that is `RF-001`,
> which resolves 21 identifier families and the programme's abbreviations. **This document is the
> *engineering* half of both**, and its central deliverable is §5: the adjudicated
> service-lifecycle model that neither of them covers.

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | **The service-delivery lifecycle vocabulary** — the adjudication `_CATEGORY_OVERVIEW.md` asks for (§5) |
| 2 | The **entity-name vocabulary** — the `fix.*` model namespace, where a term and an entity must agree (§6) |
| 3 | **Engineering and architecture terms** used across the guiding-document estate without definition (§7) |
| 4 | **Programme-specific terms** whose ordinary-English meaning is misleading here (§8) |
| 5 | The **deprecated-term register** — terms in live use that this document rules against, with replacements (§9) |
| 6 | The **bilingual position** for engineering terms, extending `BN-003`'s customer-facing bindings (§10) |
| 7 | **Terminology governance** — how a term is added, changed or deprecated, and by whom (§11) |

**Explicitly out of scope:**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| Customer-facing Bengali term bindings | `BN-003` | 227 terms already bound, with a divergence register and an approval workflow. This document defers to it entirely and extends it only where an engineering term has no customer surface (§10) |
| Do-not-translate and transliteration rules | `BN-004` | Three classes, already ruled |
| Programme and content acronyms (`Mushak`, `BEFTN`, `NBR`, `PDPA`) | `RF-001` §4.4–4.7 | Covered, verified 2026-08-18, and better placed with the content estate that uses them most |
| Content vocabulary and tone | `CG-004` | The controlled-term list for written content |
| Identifier form, allocation and permanence | `RR-002` | A glossary says what `BRU-SRM-09` *means*; `RR-002` says the string is well-formed and who may issue the next one |
| Data-element definitions, field by field | `DA-002` | A data dictionary defines `fix.service.order.promised_date`. This glossary defines *service order* |
| Odoo model naming rules | `AR-007` §4 | The *convention*. §6 here registers the *vocabulary defects* the convention would have prevented |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| **Implementation vendor** | §5 and §6 before writing a line of code. Five of the twelve portals show the same object under different words |
| Module authors | §5's adjudication, and §11 before inventing a term |
| Test authors | §5 — a test that asserts "the job is closed" must name which entity |
| Localisation Lead | §10, and the three new bindings it asks `BN-003` to make |
| Data / integration engineers | §6 — the entity-name defects, including one entity with two names in five documents |
| Trainers and content authors | §9's deprecated list, so training material does not teach a retired word |
| New joiner | §7 and §8 — the estate's private vocabulary, in one place |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause / section | How this document conforms | Departure and rationale |
|---|---|---|---|
| **ISO 704:2022** *Terminology work — Principles and methods* | §5 (concepts and concept relations), §6 (definitions), §7 (term formation) | §5 builds a **concept system** first — a part-whole hierarchy of the service lifecycle — and only then assigns terms, which is 704's core discipline. Every definition in §5–§8 is *intensional*: genus plus distinguishing characteristics | 704 expects a full concept diagram per domain. §5 provides one for the service lifecycle only; the other domains are term lists. Declared, and §11 names the trigger for extending it |
| **ISO 1087:2019** *Terminology work — Vocabulary* | §3.2 (designation), §3.4 (definition types) | Terminology about terminology: *preferred*, *admitted*, *deprecated* used with 1087's meanings, stated in §3.2 | None |
| **ISO 30042:2019** *TermBase eXchange (TBX)* | Core structure | §11.4 specifies the machine-readable form this register takes when `BN-008`'s term base is built — one TBX `termEntry` per §5–§8 row | Not implemented at this issue; this document is markdown. Declared as planned, with the trigger in §11.4 |
| **ISO/IEC 11179-5:2015** | §5 definition principles — a definition is single-concept, non-circular, non-negative, states essence | Applied to every definition; §3.3 lists the six tests and §12 `AC-02` measures against them | None |
| **ISO 12620:2019** *Data categories* | Data-category selection | §3.1's row schema uses 12620 categories: term, definition, part of speech, usage note, term status, source | Subset only — six categories of the several dozen available |

> **Why a concept system before a term list.** The estate's failure was not that authors chose bad
> words. It is that eight modules each named a *different concept* and reached for the nearest
> available English word, and several reached for the same one. ISO 704 §5 exists precisely for
> that: settle the concepts and their relations, then name them. §5.2 is that concept system, and
> it is the reason this document can rule that *job card* and *repair order* are **not** competing
> names for one thing — a conclusion a word-by-word comparison cannot reach.

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| Category overview | `./_CATEGORY_OVERVIEW.md` | The vocabulary problem this document must close; the `RF-001` boundary |
| Identifier standard | `./RR-002_Identifier_Convention_Standard.md` | The identifier spaces whose *meaning* this document supplies |
| Content glossary | `../../project_content/99_Reference_and_Registers/RF-001_ERP_Glossary_and_Acronym_Register.md` | 21 identifier families, programme acronyms, Bangladesh statutory abbreviations, six misreadable module codes. **Adopted wholesale; not restated** |
| Bilingual glossary | `../../project_content/11_Localisation_Bengali/BN-003_Bilingual_Terminology_Glossary.md` §4, §11 | 227 Bengali bindings including `service order`, `work order`, `task`, `job`, `service request`. **Authoritative for every term it covers** |
| DNT register | `../../project_content/11_Localisation_Bengali/BN-004_Do_Not_Translate_and_Transliteration_Register.md` | Classes A/B/C — what stays in Latin script |
| Term base management | `../../project_content/11_Localisation_Bengali/BN-008_Translation_Memory_and_Term_Base_Management.md` | The term-base instrument §11.4 targets |
| Entity catalogue | `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02_Data_Model_and_Entity_Catalogue.md` §2, §3 | The shared kernel and the `fix.*` namespace |
| `M01` | `../../1000fix_ERP_Module/03_Modules/A_Service_Delivery_and_Operations/M01_Service_Request_and_Order_Management.md` | *"M01 owns the **service order** — the single master record"*; `fix.service.order`, `fix.work.order`, `fix.work.order.task`, `fix.job.batch` |
| `M02` | `.../M02_Field_Service_and_Dispatch_Management.md` | `fix.dispatch.job`, `fix.dispatch.assignment` |
| `M04` | `.../M04_Branch_and_Front_Desk_Operations.md` | *"Job card issued at the counter, gate pass on device release"* — South Asian counter practice |
| `M31` | `.../M31_Workshop_and_Depot_Repair_Management.md` | `FR-WSR-001` *"Create a repair order from a service order (M01), a refurbishment order (M14), an internal request or an RMA"*; `fix.repair.order` |
| `M03` | `.../M03_Service_Logistics_and_Reverse_Logistics.md` | `fix.rma`, `fix.rma.line` |
| `M12`, `P07` | `.../M12_Marketplace_and_Seller_Ecosystem.md`, `.../P07_*.md` | `fix.marketplace.job` / `fix.mp.job` — the §6.3 defect |
| Design system | `../06_Experience_and_Interface_Design/UX-001_*.md` | The surface at which a term becomes a label |

### 2.3 Audit findings this document closes

| Finding | Source | How this document closes it |
|---|---|---|
| `_CATEGORY_OVERVIEW` "vocabulary problem" | Category 99 | §5 adjudicates all nine lifecycle terms with a concept system, entity bindings and a deprecation list |
| `C-02` (partial) | `00-06` | §6.1 records that `05-02`'s entity catalogue covers **30 of 67 modules**, so `M31`–`M67` entity vocabulary is unadjudicated — the vocabulary half of the same finding |
| `GL-02` | `RF-001` §4.3 | Adopted. §7.3 carries the six misreadable module codes into the engineering estate's reading guide |
| **New — `TRM-F-01`…`TRM-F-06`** | This document | Six vocabulary defects, all previously unrecorded (§13) |

---

## 3. How This Register Works

### 3.1 The row schema

Every term row carries six ISO 12620 data categories:

| Column | ISO 12620 category | Meaning |
|---|---|---|
| **Term** | `/term/` | The designation |
| **Status** | `/administrativeStatus/` | Preferred · Admitted · Deprecated (§3.2) |
| **Definition** | `/definition/` | Intensional: genus + differentiae, per ISO 704 §6 |
| **Entity** | `/conceptIdentifier/` | The `fix.*` model that realises the concept, or `—` if it is not an entity |
| **Owner** | `/subjectField/` | The module that owns the concept |
| **Note** | `/usageNote/` | Where the term is misused, and against what |

### 3.2 Term status, with ISO 1087:2019 meanings

| Status | ISO 1087 | Meaning here |
|---|---|---|
| **Preferred** | 3.4.15 | The term to use. One per concept |
| **Admitted** | 3.4.16 | Acceptable in a named context — usually a printed document or a customer surface — but never in a specification, a test or a ticket |
| **Deprecated** | 3.4.17 | Not to be used. Existing uses are corrected at source; §9 lists them with replacements |

> **A deprecated term is not deleted from the estate.** The same logic `RR-002` `IDC-06` applies to
> identifiers applies to terms: a reader who meets *job sheet* in a 2026 training pack must reach a
> row that says *deprecated, use job card*, not silence.

### 3.3 What makes a definition acceptable

ISO/IEC 11179-5:2015 §5, applied. A definition is rejected if it fails any of six tests, and §12
`AC-02` measures this register against them.

| # | Test | A failure looks like |
|---|---|---|
| `TRM-01` | **Single concept** | "A service order or work order used to…" |
| `TRM-02` | **Non-circular** | "A job card is a card recording a job" |
| `TRM-03` | **Stated positively** | "Not a work order" |
| `TRM-04` | **States essence, not use** | "Used by the front desk to print things" |
| `TRM-05` | **Precise genus** | "A thing that…" |
| `TRM-06` | **No embedded rationale or example inside the definition** | Definition and note kept separate — the note column exists for this |

### 3.4 The rules

| # | Rule |
|---|---|
| `TRM-07` | **One concept, one preferred term.** A second term for the same concept is *admitted* or *deprecated*, never a second preferred |
| `TRM-08` | **One term, one concept.** Where a term already names something, a new concept takes a new term — however natural the reuse feels. This is the `job` failure (§5.4) |
| `TRM-09` | **A term that names an entity must match that entity's name.** *Repair order* ↔ `fix.repair.order`. Divergence is a defect in one or the other, and §6 says which |
| `TRM-10` | **A term is not approved until its Bengali counterpart is approved** — `CG-004` `T-07`, `CM-R6`. Inherited, not invented here |
| `TRM-11` | **Benchmark vocabulary is not adopted by default.** Where a benchmark system's word (Oracle's *repair order*, SAP's *service order*) is adopted, the adoption is recorded with the benchmark named |
| `TRM-12` | **A deprecated term is corrected at source**, by the owning document's owner, under `CG-007`'s re-approval triggers where the source is content. This register records; it does not edit other people's files |

---

## 4. The Measured Vocabulary Position

### 4.1 Method

```bash
# Term frequency and spread, word-boundary matched
for t in "job card" "service order" "work order" "repair order" "service request" "job sheet"; do
  printf "%-16s occ=%-6s files=%s\n" "$t" \
    "$(grep -rihoE "\b$t\b" --include='*.md' . | wc -l)" \
    "$(grep -rilE  "\b$t\b" --include='*.md' . | wc -l)"
done
# Which module specifications use each term
grep -rilE '\brepair order\b' --include='M*.md' 1000fix_ERP_Module/03_Modules/
# The entity namespace behind the vocabulary
grep -rhoE '\bfix\.[a-z_.]*(repair|job|work|dispatch|rma)[a-z_.]*\b' --include='*.md' . | sort -u
```

> **Case-insensitive matching without word boundaries is wrong here and produced a wrong figure on
> the first pass.** A naive `grep -i RMA` returns 8,311 hits because *info**rma**tion* contains the
> string. The word-boundary count is **65**. The figure is recorded because it is the same class of
> error `GL-02` describes — a regular expression that silently mismatched — and because anyone
> reproducing §4.2 will otherwise get the wrong answer.

### 4.2 The counted position

Counted 2026-08-19 02:41 (+06) across 782 markdown files.

| Term | Occurrences | Files | Module specifications using it |
|---|---:|---:|---:|
| **service order** | 754 | 208 | most |
| **work order** | 221 | 69 | **15** |
| **repair order** | 104 | 22 | **5** |
| **service request** | 96 | 49 | many |
| **job card** | 59 | 33 | **5** |
| **RMA** | 65 | 15 | 4 |
| **job sheet** | 21 | 9 | 3 |
| **job batch** | 7 | 6 | 2 |
| **work item** | 6 | 6 | 4 |
| **service ticket** | 2 | 2 | 1 |

**The entity namespace behind them** — counted from the `fix.*` model names in use:

| Entity | Owner | Concept |
|---|---|---|
| `fix.service.order` | `M01` | The customer's engagement |
| `fix.work.order` | `M01` | A unit of executable work under it |
| `fix.work.order.task` | `M01` | A step within a work order |
| `fix.job.batch` | `M01` | A grouping of service orders for one site visit |
| `fix.dispatch.job` | `M02` | The dispatchable unit given to a field technician |
| `fix.dispatch.assignment` | `M02` | The binding of a dispatch job to a technician |
| `fix.repair.order` | `M31` | The workshop's unit of work on a device |
| `fix.repair.stage.log`, `fix.repair.operation`, `fix.repair.bom` | `M31` | Its stages, operations, parts |
| `fix.rma`, `fix.rma.line` | `M03` | Return authorisation |
| `fix.facility.work.order` | `M47` | A maintenance job on a *building*, not a customer device |
| `fix.marketplace.job` / `fix.mp.job` | `M12` | A marketplace transaction — **two names, one entity** (§6.3) |
| `fix.job.posting`, `fix.job.profile` | `M58` | A recruitment vacancy |
| `fix.scheduled.job`, `fix.batch.job.run`, `fix.patch.job`, `fix.migration.job` | platform | Technical background execution |

> ### `TRM-F-01` — there are not four competing terms; there are ten distinct concepts and one overloaded word
>
> The register's brief asks this document to adjudicate between *"job card", "service order",
> "work order" and "repair order"*. The concept system (§5.2) shows that framing is wrong in a way
> that matters: **those four terms name four different things, and all four are needed.** The
> actual defect is elsewhere — the word **`job`** is used for **at least six unrelated concepts**
> across four business domains and the technical platform:
>
> | `job` means | Entity | Domain |
> |---|---|---|
> | A dispatchable field visit | `fix.dispatch.job` | Field service |
> | A grouping of service orders | `fix.job.batch` | Service intake |
> | A marketplace transaction | `fix.marketplace.job` | Marketplace |
> | A recruitment vacancy | `fix.job.posting` | HR |
> | A background execution | `fix.scheduled.job`, `fix.patch.job`, `fix.migration.job` | Platform |
> | A printed counter document | *job card* | Branch operations |
>
> `BN-003` already caught the edge of this: it binds *job* → **জব** and adds *"Never কাজ alone —
> কাজ is generic work, not the dispatchable unit."* That note is correct and is exactly `TRM-08`.
> **A programme that says "1,200 jobs completed today" has said nothing measurable.**

---

## 5. The Service-Delivery Lifecycle — Adjudicated

This section is this document's principal deliverable.

### 5.1 The ruling, in one paragraph

**A customer engagement is a `service order`.** Work done to fulfil it is a `work order` where it
happens in the field or at the branch, and a `repair order` where it happens on a bench in a
workshop. A `dispatch job` is a work order that has been scheduled to a named technician for a
named time. A `job card` is a **printed document**, not a record type. A `service request` is a
**phase**, not an entity. `Job sheet` and `service ticket` are **deprecated**.

### 5.2 The concept system

ISO 704 §5 part-whole and generic relations. Read `└─` as *is part of the line above it*.

```
CUSTOMER ENGAGEMENT
│
├── service request .................. a PHASE: the act of asking, before a record exists
│                                      no entity — M01 §3, BN-003 §4
│
└── fix.service.order ................ the master record of one customer engagement   [M01]
    │                                  one per engagement, all 12 intake channels
    │
    ├── fix.job.batch ................ OPTIONAL grouping of service orders for one    [M01]
    │                                  site visit. A batch is ABOVE the order,
    │                                  not below it — the only upward relation here
    │
    ├── fix.estimate ................. the priced proposal requiring customer approval [M01]
    │
    ├── fix.work.order .............. a unit of executable work                       [M01]
    │   │                             field, branch or on-site
    │   │
    │   ├── fix.work.order.task ..... a step within it                                [M01]
    │   │
    │   └── fix.dispatch.job ........ a work order SCHEDULED to a named technician    [M02]
    │       └── fix.dispatch.assignment .. the technician binding                     [M02]
    │
    ├── fix.repair.order ............ a unit of bench work on a device in a workshop  [M31]
    │   │                             created from a service order, a refurbishment
    │   │                             order (M14), an internal request or an RMA
    │   │                             — FR-WSR-001
    │   ├── fix.repair.operation .... a standard operation within it                  [M31]
    │   ├── fix.repair.stage.log .... its stage history                               [M31]
    │   └── fix.repair.bom .......... the parts it consumes                           [M31]
    │
    └── fix.rma ..................... authorisation for a device to be returned       [M03]
                                      may PRECEDE the service order (customer-initiated
                                      return) or follow it (warranty replacement)

PRINTED ARTEFACTS — documents, not records
    job card ........................ the counter document accompanying a device      [M04]
    gate pass ....................... the release document                            [M04]
    service report .................. the completion document given to the customer   [M01]

SEPARATE CONCEPTS THAT REUSE THE WORD — see TRM-F-01
    fix.facility.work.order ......... maintenance on a BUILDING                       [M47]
    fix.marketplace.job ............. a marketplace transaction                       [M12]
    fix.job.posting ................. a recruitment vacancy                           [M58]
    fix.scheduled.job ............... a background execution                          platform
```

### 5.3 The term register

| Term | Status | Definition | Entity | Owner | Note |
|---|:--:|---|---|:--:|---|
| **service order** | **Preferred** | The master record of a single customer engagement, from intake through to closure, against which all work, parts, cost, price and evidence are accumulated | `fix.service.order` | `M01` | *"M01 owns the service order — the single master record"*. 754 occurrences, the most-cited object in the estate. `BN-003`: **সার্ভিস অর্ডার** |
| **service request** | **Preferred** | The act of a customer asking for service, occurring before a service order exists | — | `M01` | **A phase, not an entity** — `BN-003` §4 states this and it is adopted. A document that says "the service request record" is wrong |
| **work order** | **Preferred** | A unit of executable work created under a service order and performed at a customer site, on-site, or at a branch | `fix.work.order` | `M01` | Used in 15 module specifications, most correctly. `BN-003`: **ওয়ার্ক অর্ডার**, and **কার্যাদেশ** on Class A/B printed documents |
| **task** | **Preferred** | A single step within a work order, with its own status and duration | `fix.work.order.task` | `M01` | `BN-003`: **টাস্ক** |
| **dispatch job** | **Preferred** | A work order that has been scheduled to a named technician for a named time window | `fix.dispatch.job` | `M02` | The dispatchable unit. **`job` alone is deprecated in specifications** — §9 |
| **repair order** | **Preferred** | A unit of work performed on a device at a workshop bench, tracked through repair stages and consuming a repair bill of materials | `fix.repair.order` | `M31` | `FR-WSR-001`. Adopted from **Oracle Depot Repair** and **Odoo `repair`** under `TRM-11`; `M31` §4 names both. **Not a synonym for work order** — the bench context is the differentia |
| **job batch** | **Preferred** | A grouping of service orders executed together at one site or in one visit | `fix.job.batch` | `M01` | The only concept in the model that sits *above* the service order |
| **RMA** | **Preferred** | Return Merchandise Authorisation — the authorisation permitting a device to be returned into the network, with its expected handling | `fix.rma` | `M03` | Latin script, `BN-004` Class C. May precede *or* follow the service order |
| **job card** | **Admitted** *(printed documents only)* | The document issued at a branch counter that accompanies a device through intake, identifying the customer, the device, the reported symptom and the accepted terms | — *(a `DT-*` template)* | `M04` | **A document, not a record type.** `M04` §4 records it as South-Asian authorised-service-centre practice. In a specification, name the record (`fix.service.order`) and the document (`DT-*`) separately |
| **gate pass** | **Admitted** *(printed documents only)* | The document authorising a device to leave a branch or workshop | — *(a `DT-*` template)* | `M04` | As above |
| **service report** | **Preferred** | The completion document given to the customer, stating what was found, what was done and what was replaced | `fix.service.report` | `M01` | `BN-003`: **সার্ভিস রিপোর্ট** |
| **estimate** | **Preferred** | A priced proposal for identified work, requiring customer approval before that work proceeds | `fix.estimate` | `M01` | `BN-003`: **এস্টিমেট**, with divergence `D-1` recorded and resolved there |
| **quotation** | **Preferred** | A priced commercial proposal to an organisation, including a tender response | — | `M36` | Reserved by `BN-003` §5. **Not a synonym for estimate**: an estimate prices *identified* work on a device already in the network |
| **job sheet** | **Deprecated** | — | — | — | 21 occurrences in 9 files. Use **job card** (document) or **work order** (record). §9 |
| **service ticket** | **Deprecated** | — | — | — | 2 occurrences. Use **service order**. A *ticket* in this estate is an internal IT service-management record (`M66`) |
| **work item** | **Deprecated** | — | — | — | 6 occurrences. Use **task** or **work order** as the concept system requires |
| **job** *(unqualified)* | **Deprecated in specifications; Admitted in UI copy** | — | — | — | See `TRM-F-01`. In a specification, test or ticket, always qualify: *dispatch job*, *job batch*, *marketplace job*, *background job*. `BN-003` binds the UI surface **জব** to `fix.dispatch.job` and that binding stands |

### 5.4 Why `repair order` is kept rather than merged into `work order`

This is the ruling most likely to be challenged, so the reasoning is recorded.

| Argument for merging | Why it is rejected |
|---|---|
| Both are "work under a service order"; one entity is simpler | The two have **different lifecycles, different state machines and different cost models**. A repair order has repair *stages*, a bench, a repair BOM, a standard repair time and level 1/2/3 board-level tracking (`fix.repair.stage.log`, `fix.repair.operation`, `fix.standard.repair.time`). A work order has tasks, a technician and a site |
| Odoo has one `repair` model | Odoo has **both** — `repair` and the OCA field-service work order. `M31` §4 adopts `repair` for the bench and `fieldservice` for the field, which is the benchmark position, not a local invention |
| Fewer terms is fewer misunderstandings | The misunderstanding this estate actually suffers is the opposite: **one word for several concepts** (`TRM-F-01`), not several words for one concept |
| A repair order can be created from an RMA or a refurbishment order, with no service order at all | **This is the decisive argument, and it argues for keeping them separate.** `FR-WSR-001` creates a repair order from four sources, only one of which is a service order. A `fix.work.order` that is not under a `fix.service.order` would break `M01`'s master-record model |

**Ruling `RR-001-D-01`: `work order` and `repair order` are distinct concepts and both are
preferred terms.** The differentia is stated once: **a work order is performed where the customer
is; a repair order is performed where the bench is.**

### 5.5 Boundary cases a reader will hit

| Situation | Which term |
|---|---|
| A technician repairs a device at the customer's premises | **Work order.** No bench, no repair order |
| A device is collected, repaired at a workshop, and returned | **Service order** → logistics → **repair order** → logistics. The work order covers collection and return if a technician performs them |
| A branch does a 15-minute counter fix | **Service order** with a **work order**. A **job card** is printed. No repair order — no bench allocation |
| A customer returns a device under warranty for replacement | **RMA**, then a **service order** if any work follows |
| A refurbishment run on stock the company owns | **Repair order** with no service order — `M14` is the source. `FR-WSR-001` |
| Air-conditioning maintenance at a branch office | **`fix.facility.work.order`** — `M47`. Not a customer work order, and this is the entity most likely to be conflated in a report |

---

## 6. Entity-Name Vocabulary

Where `TRM-09` requires a term and its entity to agree, this section records where they do not.

### 6.1 Coverage

`05-02_Data_Model_and_Entity_Catalogue.md` carries the title *"225 Entities Across 30 Modules"*.
The programme has **67 modules**. `AR-008` counted **1,335 entities** in the estate; the `fix.*`
namespace returns **1,574 distinct model names** at 2026-08-19 02:41.

> ### `TRM-F-02` — the entity vocabulary of 37 modules is unadjudicated
>
> `05-02` covers `M01`–`M30`. `M31`–`M67` — including `M31` Workshop, which owns `fix.repair.order`
> and every term in §5's workshop branch — have entities declared **only inside their own module
> files**. There is no cross-module review of those names, which is where `TRM-F-03` came from.
>
> This is the vocabulary half of `C-02` (*"M31 exists in no register; the same applies to
> M32–M67"*). It is recorded here rather than closed: closing it means extending `05-02`, which is
> `DA-001`'s and `DA-002`'s work, not a glossary's. Owner **Enterprise Architecture**, `W1`.

### 6.2 Where a preferred term and its entity agree

All eleven §5 preferred terms bind to an entity whose name matches the term, with one intentional
exception: **service request**, which is a phase and correctly has no entity.

### 6.3 Where they do not

> ### `TRM-F-03` — one entity, two names, five documents
>
> | Name | Appears in |
> |---|---|
> | `fix.marketplace.job` | `M12` §—, `M20`, `M51`, `M53` |
> | `fix.mp.job` | `05-02` §5 (the entity catalogue itself), `P07` |
>
> `M12` defines it as *"the marketplace transaction"*; `05-02` lists it among `M12`'s entities as
> `fix.mp.job`, alongside `fix.mp.seller`, `fix.mp.listing` and `fix.mp.offer` — a consistent
> `fix.mp.*` prefix. `M12`'s own body uses `fix.marketplace.*`.
>
> **The catalogue and the module disagree about the name of the same entity, and three finance
> modules read it by the name the catalogue does not use.** `M53` calculates commission against
> `fix.marketplace.job`; `P07` presents `fix.mp.job` to the seller. An integration written from
> either document alone is wrong against the other.
>
> **Ruling `RR-001-D-02`: `fix.mp.*` is preferred**, because `05-02` is the entity catalogue and
> the prefix is consistent across six sibling entities. `fix.marketplace.job` is deprecated. Owner
> `DA-002`, `W1`. Raised as `RR-001-Q-02` because a glossary may rule on the *term* and only
> `DA-002` may rename the *entity*.
>
> **A second, smaller defect in the same trail.** `M20` line 562 lists
> `` `fix.marketplace.job`, `fix.marketplace.job` `` — the same entity twice in one cell, which is
> the `RR-002` `IDC-09` failure in the entity namespace. Corrected by `M20`'s owner.

| Term | Entity as declared | Issue | Ruling |
|---|---|---|---|
| marketplace job | `fix.marketplace.job` / `fix.mp.job` | Two names | `fix.mp.job` preferred — `RR-001-D-02` |
| facility work order | `fix.facility.work.order` | Reads as a sub-type of `fix.work.order`; it is not | Entity name retained; **the term is always written *facility work order*, never *work order***. `TRM-13` |
| job batch | `fix.job.batch` | Sits *above* the service order but is named as though below it | Retained. Noted in §5.2 so a reader is not misled |

### 6.4 New rule

| # | Rule |
|---|---|
| `TRM-13` | **Where an entity name is a prefixed form of another entity's name, the term is always written in full.** `fix.facility.work.order` is a *facility work order*, never a *work order*. Applies equally to `fix.service.order.rental`, `fix.service.order.msp`, `fix.service.order.data` and `fix.service.order.marketplace` — four `M01` sub-types that must never be shortened to *service order* in a context where the sub-type matters |

---

## 7. Engineering and Architecture Vocabulary

Terms used across the 125 guiding documents that a business reader, a vendor or a new joiner will
not be able to resolve from context.

### 7.1 Architecture and delivery

| Term | Definition | Note |
|---|---|---|
| **Delivery layer** | The provenance of a capability: `L1` Odoo 19 CE native · `L2` OCA module · `L3` community third-party · `L4` complementary open-source system · `L5` custom development · `L6` external SaaS | `00-01` §3. **The single most load-bearing vocabulary in the cost model** — an `L1` claim and an `L5` claim differ by the entire build cost of a capability |
| **Custom development unit / `CD`** | A discrete unit of custom Odoo code with its own identifier, register row and sizing | `BE-005`. `RR-002` §5.4 — the space is frozen |
| **Wave** | One of nine delivery increments, `W1`–`W9`, each with a scope, a gate and a go-live | `06-01` |
| **Gate** | A decision point at the end of a wave, `G1`–`G4`, with exit criteria that must be evidenced | `GV-009` |
| **Bounded context** | A boundary within which one domain model and one vocabulary apply consistently | `AR-008`. **The architectural expression of `TRM-08`** — `job` means different things in different contexts precisely because the contexts are bounded |
| **Fitness function** | An automated test asserting an architectural property rather than a functional one | `AR-012` |
| **Transactional outbox** | The pattern by which a state change and its published event commit atomically | `AR-009`; `fix.domain.event` |
| **Offline-first** | A design in which the client is authoritative between synchronisations and reconciles on reconnect | `AR-010`, `UX-006`. **Not** "works offline sometimes" |
| **Idempotent** | Producing the same result whether applied once or many times | `IP-04`, `AR-001` `T-01` |
| **Odoo model** | A persisted business object in Odoo, named `fix.<domain>.<object>`, mapping to a table | `AR-007` §4 |
| **OCA** | Odoo Community Association — the publisher of the `L2` module set | `BN-004` Class B, Latin script |

### 7.2 Requirements, quality and assurance

| Term | Definition | Note |
|---|---|---|
| **Requirement row** | One row of a requirement table. **The programme's counting unit** | `RG-06`. *"The requirement count is the number of requirement rows, not the highest allocated identifier"* — the distinction behind the largest finding in both repository audits |
| **Functional requirement (`FR`)** | A statement of what the system shall do, owned by one module | `RR-002` §5.3; space frozen |
| **Non-functional requirement (`NFR`)** | A constraint on how well the system does it | `05-06`, `RQ-006`; space frozen |
| **Business rule (`BRU`)** | A constraint on business behaviour, classified H(ard) / A(dvisory) / S(oft) / C(onfigurable) | `_MODULE_TEMPLATE` §0 |
| **Automation (`AUT`)** | A trigger–action–exception triple executed without human initiation | `RR-002` `RR-002-D-01` — the module-local form governs |
| **Denominator** | The agreed total against which coverage is measured | `TS-01`, `RQ-004` §5.1. Contested across four figures; `RF-001` `GL-01` diagnoses it |
| **Traceability** | A directed, typed link between two artefacts, asserted in both directions | `RQ-004` §3.3, `RR-006` |
| **Estimate class** | The AACE RP 17R-97 confidence band of a cost or effort figure, 1 (tightest) to 5 | `GV-007`, `GV-008` |
| **Person-week (PW)** | The programme's effort unit. One person, one week, at declared productivity | `GV-007` |
| **Qualified ✅** | A document meeting `PGD-000` §0.3 tests (a)–(c) but **not** (d), because no body can approve | `PGD-A1-09`, `PGD-A2-25`. **Applies to every ✅ in this estate** |
| **◐ Partial** | *"Absent, with useful source material"* — **not** "nearly done" | `PGD-000` §0.3, `PGD-A1-08`. The status most likely to be misread as progress |

### 7.3 The six module codes a reader will misread

Adopted verbatim from `RF-001` §4.2.5 because the engineering estate hits them constantly and a
reader should not need two documents.

| Code | Reads as | Actually means |
|---|---|---|
| `SRM` | Supplier Relationship Management | **Service Request Management** — `M01` |
| `SRM2` | A version number | **Supplier Relationship Management** — `M42`, a collision workaround (`RR-002` `RR-002-D-02`) |
| `FRD` | Fraud | **FRont Desk** — `M04` |
| `POR` | Portfolio | **PORtal** — the portal requirement space, 358 requirements |
| `DTS` | Date/Time Standard | **Data & Technology Services** — `M06` |
| `WSR` | Web Service Request | **WorkShop Repair** — `M31` |

---

## 8. Programme Terms Whose Ordinary Meaning Misleads

> ### `TRM-F-04` — nine terms in daily use mean something narrower or different here
>
> Each of these has an everyday English meaning that a reader will apply by default, and a
> programme meaning that is narrower. Every one has produced at least one observable
> misunderstanding in the estate.

| Term | Everyday reading | Programme meaning | Where the reading goes wrong |
|---|---|---|---|
| **Engineer** | Any technical staff member | An **external marketplace freelancer** — `CG-004` | `BN-003` `D-2`: the website glossary uses the everyday reading. A permission rule written on the everyday reading grants marketplace scope to employees |
| **Partner** | A commercial partner | In Odoo, **any** party: customer, employee, vendor, seller — `res.partner`, `fix.party` | A "partner report" may mean brand partners (`M40`) or every party in the database |
| **Fault** vs **symptom** | Interchangeable | **Fault** = the confirmed defect. **Symptom** = what the customer reported | `BN-003` §4 states they are never interchangeable. `MD-024` codes both |
| **Estimate** vs **quotation** | Interchangeable | **Estimate** prices identified work on a device in the network; **quotation** is a commercial proposal to an organisation | Different modules, different approval paths |
| **Reject** vs **decline** | Interchangeable | Customer refusing an estimate = **reject**. Technician refusing a job = **decline** | `BN-003` `D-3`: both rendered as প্রত্যাখ্যান in two approved packs. Raised as `AUDIT-012` `BN-06` |
| **Rework** | Doing something again | A **quality measure with contractual weight** — `BRU-SRM-06` | `BN-003`: never পুনরায় মেরামত, which describes any second repair |
| **Ticket** | Any work record | An **internal IT service-management** record — `M66` | *service ticket* is deprecated for exactly this reason (§5.3) |
| **Consignment** | A delivery | A custody transfer of goods — `fix.consignment` | `BN-003` deliberately does **not** bind it to চালান, which is *challan* |
| **Partial (◐)** | Nearly complete | **Absent, with useful source material** | `PGD-A1-08`. 38 of 140 documents carried ◐ at the last register issue |

---

## 9. Deprecated Term Register

`TRM-12`: recorded here, corrected at source by the owning document's owner.

| Deprecated term | Occurrences | Files | Replacement | Owner of the correction | Target |
|---|---:|---:|---|---|:--:|
| **job sheet** | 21 | 9 | **job card** (the printed document) or **work order** (the record) — §5.5 decides which | Owning module / content authors | W1 |
| **service ticket** | 2 | 2 | **service order** | Owning module | W1 |
| **work item** | 6 | 6 | **task** or **work order** | Owning module | W1 |
| **job** *(unqualified, in specifications)* | — | — | **dispatch job**, **job batch**, **marketplace job**, **background job** | All module authors | W1 |
| `fix.marketplace.job` | 5 | 4 | **`fix.mp.job`** — `RR-001-D-02` | `DA-002` | W1 |
| **AUT-nnn** *(as a term for "the automation")* | 60 | — | The module-local `AUT-<CODE>-nn` — `RR-002` `RR-002-D-01` | Enterprise Architecture | W1 |

> **Correction cost is small and the benefit is asymmetric.** Thirty-four occurrences across
> seventeen files, none of them in a statutory or contractual document. Left uncorrected, each one
> is a term a trainer teaches, a test asserts and a vendor implements.

---

## 10. The Bilingual Position

### 10.1 What is already settled

`BN-003` binds **227 terms**, including every §5 preferred term that has a customer surface:

| Term | Bengali | Tier | Note |
|---|---|:--:|---|
| service order | **সার্ভিস অর্ডার** | 2 | Customer surfaces may present **আমার সার্ভিস** |
| work order | **ওয়ার্ক অর্ডার** | 2 | **কার্যাদেশ** on Class A/B printed documents — `BN-002` `RD-C` |
| task | **টাস্ক** | 2 | |
| service request | **সার্ভিসের অনুরোধ** | 3 | The act, not an entity |
| job *(dispatchable unit)* | **জব** | 2 | *"Never কাজ alone"* |
| estimate | **এস্টিমেট** | 2 | Divergence `D-1` recorded and resolved |
| service report | **সার্ভিস রিপোর্ট** | 2 | |
| fault / symptom | **ত্রুটি** / **লক্ষণ** | 3 | Never interchangeable |

**This document changes none of them.** `BN-003` is the authority for every term it covers, and
`TRM-10` (a term is not approved until its Bengali counterpart is) is inherited from `CG-004`
`T-07`, not invented here.

### 10.2 What is not settled — three engineering terms with a customer surface

> ### `TRM-F-05` — three §5 terms have a customer or technician surface and no Bengali binding
>
> | Term | Surface | Why it needs a binding |
> |---|---|---|
> | **repair order** | `P02` technician app; `P01` customer status tracking; the `M31` workshop board | A customer tracking a device sent to a workshop sees its state. `BN-003` binds *work order* but not *repair order*, so a Bengali surface will either invent a form per portal — the exact failure `BN-003`'s purpose statement warns about — or fall back to ওয়ার্ক অর্ডার and conflate two concepts |
> | **job card** | `P01`, `P04` and the branch counter; printed under `DT-*` | The most customer-visible printed artefact in the branch network. **কার্ড** alone is insufficient |
> | **RMA** | `P01` returns flow; `P05` vendor portal | `BN-004` Class C keeps the acronym in Latin script, but the *expansion* shown on first use needs a Bengali form |
>
> **Raised as `RR-001-Q-01` to the Localisation Lead**, with `BN-003` §15.1 (*Adding*) as the
> route. Three terms, one review cycle. **This document does not propose Bengali forms** —
> `BN-003` §15.1 vests that in Localisation with a named reviewer set, and a glossary written by
> Enterprise Architecture proposing Bengali terminology would breach `TRM-12` and `CG-007`.

### 10.3 Latin-script terms

`BN-004` Class C keeps technical identifiers, codes and units in Latin script. Every identifier in
`RR-002` §5, every `fix.*` model name, every `CD-` identifier and every `FR-`/`NFR-`/`BRU-`
reference is Class C and is **never transliterated**, in any surface, in either language.

---

## 11. Terminology Governance

### 11.1 Adding a term

| Step | Action | Who |
|---:|---|---|
| 1 | Establish the **concept** is new, not a new name for an existing one — §5.2, `TRM-07` | Author |
| 2 | Establish the **term** is not already in use for another concept — `TRM-08`; run the §4.1 command | Author |
| 3 | Write an intensional definition passing `TRM-01`…`TRM-06` | Author |
| 4 | Bind it to an entity if it names one, matching the entity name — `TRM-09` | Author + `DA-002` |
| 5 | Request the Bengali counterpart via `BN-003` §15.1 if it has any customer or technician surface | Localisation Lead |
| 6 | Add the row here | Enterprise Architecture |

### 11.2 Changing or deprecating a term

Deprecation follows `BN-003` §15.3 and `TRM-12`: the row moves to §9 with a replacement, an owner
and a target wave. **The occurrences are corrected by the owning document's owner**, not by
Enterprise Architecture editing other people's files.

### 11.3 Review cadence

| Trigger | Action |
|---|---|
| Every wave gate | Re-run §4.1; any term appearing in ≥3 files and absent from §5–§8 is a candidate row |
| A new module specification | Its §1 vocabulary is checked against §5 before the documentation gate |
| A `BN-003` change | This register's §10.1 is re-verified |
| An `05-02` extension to `M31`–`M67` | `TRM-F-02` re-measured |

### 11.4 The machine-readable form

This register is markdown, which is not queryable. **When `BN-008`'s term base is built, every row
in §5–§8 becomes one ISO 30042:2019 TBX `termEntry`**, with `<termNote type="administrativeStatus">`
carrying §3.2's status and `<descrip type="definition">` carrying the definition. `RR-006` §5's
generator emits the TBX; the trigger is `BN-008` reaching implementation. Until then the markdown
is the authority and the duplication risk is real and accepted.

---

## 12. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | The nine lifecycle terms named in `_CATEGORY_OVERVIEW.md` are each adjudicated with a status, a definition and an entity binding | §5.3 — **met at issue**; ten terms adjudicated, one more than asked |
| `AC-02` | Every definition passes `TRM-01`…`TRM-06` | §3.3 tests applied during authoring; **met at issue**, self-assessed |
| `AC-03` | No term in §5–§8 contradicts `BN-003` | §10.1 reproduces `BN-003`'s bindings unchanged; **met at issue** |
| `AC-04` | No content is duplicated from `RF-001` except §7.3, which is marked as adopted | §1.1 out-of-scope table; **met at issue** |
| `AC-05` | Every deprecated term has a replacement, an occurrence count, an owner and a target | §9 — 6 of 6; **met at issue** |
| `AC-06` | Every usage figure carries the enumeration timestamp and a reproducible command | §4.1; **met at issue** |
| `AC-07` | Terms with a customer surface and no Bengali binding are identified and raised, not invented | §10.2, `RR-001-Q-01`; **met at issue** |
| `AC-08` | The entity vocabulary of `M31`–`M67` is adjudicated | **NOT met** — `TRM-F-02`. Blocked on `05-02`'s extension; owner and date recorded |

**Definition of done.** Complete when every criterion is met, `PGD-000`'s `RR-001` row moves from
◐ to ✅ with a fresh enumeration timestamp, and the approver signs. `AC-08` is **open and stated as
open**: 37 modules' entity vocabulary cannot be adjudicated from a catalogue that stops at `M30`.

---

## 13. Findings Raised

| # | Finding | Severity | New? | Owner | Target |
|---|---|:--:|:--:|---|:--:|
| `TRM-F-01` | **`job` names at least six unrelated concepts** across four domains and the platform; "jobs completed" is unmeasurable | **High** | **New** | Enterprise Architecture | W1 |
| `TRM-F-02` | **Entity vocabulary of 37 modules is unadjudicated** — `05-02` covers `M01`–`M30` of 67 | **High** | Partly — `C-02`'s vocabulary half | Enterprise Architecture | W1 |
| `TRM-F-03` | **One entity, two names, five documents** — `fix.marketplace.job` / `fix.mp.job`; three finance modules read the name the catalogue does not use | **High** | **New** | `DA-002` | W1 |
| `TRM-F-04` | **Nine terms have a misleading everyday reading**, two of which have already produced defects in approved packs | Medium | Partly — `BN-003` `D-2`, `D-3` | Content authors | W1 |
| `TRM-F-05` | **Three engineering terms have a customer surface and no Bengali binding** — *repair order*, *job card*, *RMA* | Medium | **New** | Localisation Lead | W1 |
| `TRM-F-06` | **`M20` lists the same entity twice in one cell** — the `IDC-09` failure in the entity namespace | Low | **New** | `M20` owner | W1 |

---

## 14. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `RR-001-D-01` | *work order* vs *repair order* | (a) merge into one term and one entity; (b) keep both as distinct concepts | **(b)** | Different lifecycles, state machines and cost models; and `FR-WSR-001` creates a repair order from three sources that are not service orders, which a merged entity could not represent | Both are preferred terms. Differentia stated in §5.4: *the customer's location vs the bench* |
| `RR-001-D-02` | `fix.marketplace.job` vs `fix.mp.job` | (a) prefer the `M12` body form; (b) prefer the `05-02` catalogue form | **(b)** | `05-02` is the entity catalogue and the `fix.mp.*` prefix is consistent across six sibling entities | `fix.marketplace.job` deprecated; **the rename is `DA-002`'s to execute**, raised as `RR-001-Q-02` |
| `RR-001-D-03` | *job card* — record type or document | (a) register it as a record type; (b) rule it a printed document | **(b)** | `M04` §4 sources it to counter practice, not to a data model. No entity exists or is needed | Admitted for printed documents; forbidden in specifications, tests and tickets |
| `RR-001-D-04` | Bengali forms for the three unbound terms | (a) propose forms here; (b) raise to Localisation | **(b)** | `BN-003` §15.1 vests term approval in Localisation with a named reviewer set. A glossary proposing Bengali terms would breach `TRM-12` and `CG-007` | `RR-001-Q-01`; three terms, one review cycle |

---

## 15. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `RR-001-Q-01` | Bengali bindings for **repair order**, **job card** and **RMA** — three terms with a customer or technician surface | **Localisation Lead** | W1 | `P01`, `P02` Bengali string bundles; `BN-009`, `BN-010` |
| `RR-001-Q-02` | Does `DA-002` accept `RR-001-D-02` and rename `fix.marketplace.job` → `fix.mp.job`, or does it prefer the reverse? Either is acceptable; **having both is not** | `DA-002` owner | W1 | `M53` commission calculation; `P07` seller surface |
| `RR-001-Q-03` | When `05-02` extends to `M31`–`M67`, does the entity vocabulary get a cross-module review, or is per-module declaration sufficient? Per-module declaration produced `TRM-F-03` | Enterprise Architecture | W1 | `AC-08`, `TRM-F-02` |
| `RR-001-Q-04` | Is *engineer* = external marketplace freelancer (`CG-004`) tenable once `M22` certifies internal technicians as engineers? The two readings will collide in training material | Programme Content Lead | W2 | `CH-002` course design; `SC-004` role naming |

---

## 16. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `PGD-000` | Registers this document |
| Upstream | `RR-002` | Supplies the identifier spaces whose meaning this document states |
| Upstream | `RF-001` | The content estate's glossary. Adopted for acronyms and module codes; not restated |
| Upstream | `BN-003`, `BN-004` | Authoritative for every bilingual binding. Extended, never overridden |
| Upstream | `05-02`, `M01`, `M02`, `M03`, `M04`, `M31`, `M12` | The specifications from which §5's concept system is derived |
| Downstream | `RR-003` | The vocabulary a document template's section headings must use |
| Downstream | `RR-006` | Term ↔ entity ↔ module links are index dimensions |
| Downstream | `DA-002` | Receives `RR-001-D-02` and `TRM-F-03` |
| Downstream | `QA-003` | Test case titles use preferred terms; §9 is a review checklist |
| Downstream | `CH-002`, `TR-*` | Training material may not teach a deprecated term |
| Lateral | `../../project_content/11_Localisation_Bengali/BN-008_*.md` | The term base §11.4 targets |
| Lateral | `../../1000fix_ERP_Module/03_Modules/*/M*.md` | 15 module specifications carry the corrections in §9 |

---

## 17. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` · `./_CATEGORY_OVERVIEW.md` ·
`./RR-002_Identifier_Convention_Standard.md` · `./RR-003_Document_Standards_and_Template_Library.md` ·
`./RR-006_Master_Cross_Reference_and_Traceability_Index.md` ·
`../02_Architecture_and_Design/AR-007_Odoo_Module_Architecture_and_Code_Structure_Standard.md` ·
`../02_Architecture_and_Design/AR-008_Domain_Model_and_Bounded_Context_Map.md` ·
`../03_Data_and_Information_Architecture/DA-002_Data_Dictionary.md` ·
`../06_Experience_and_Interface_Design/UX-001_Design_System_and_Component_Library_Specification.md`

**Workspace**
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02_Data_Model_and_Entity_Catalogue.md` ·
`../../1000fix_ERP_Module/03_Modules/A_Service_Delivery_and_Operations/M01_Service_Request_and_Order_Management.md` · `M02_*.md` · `M03_*.md` · `M04_*.md` · `M31_Workshop_and_Depot_Repair_Management.md` ·
`../../1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M12_Marketplace_and_Seller_Ecosystem.md` ·
`../../project_content/99_Reference_and_Registers/RF-001_ERP_Glossary_and_Acronym_Register.md` ·
`../../project_content/11_Localisation_Bengali/BN-003_Bilingual_Terminology_Glossary.md` · `BN-004_*.md` · `BN-008_*.md` ·
`../../project_content/00_Content_Governance_and_Standards/CG-004_*.md`

**External standards**

| Standard | Title | Status | `verified_on` |
|---|---|---|---|
| ISO 704:2022 | Terminology work — Principles and methods | Current, edition 4 | 2026-08-19 |
| ISO 1087:2019 | Terminology work and terminology science — Vocabulary | Current, edition 2 | 2026-08-19 |
| ISO 30042:2019 | Management of terminology resources — TermBase eXchange (TBX) | Current | 2026-08-19 |
| ISO 12620:2019 | Management of terminology resources — Data category specifications | Current | 2026-08-19 |
| ISO/IEC 11179-5:2015 | Metadata registries — Naming and definition principles | Current | 2026-08-19 |

> Currency is registered in `RR-005`; this table is the local copy.

---

## 18. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-19 | Enterprise Architecture | Initial issue. Service-lifecycle concept system and ten-term adjudication; six findings, four new; six deprecated terms; three Bengali bindings raised | *(unsigned — no constituted body, `PGD-A1-09`)* |

---

*`RR-001` · Category 99 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
