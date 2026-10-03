---
id: PGD-CAT-99
category: 99 — Reference, Registers & Glossary
code: RR
project: 1000FiX ERP System v2.0
version: 1.2
date: 2026-08-19
status: DRAFT FOR APPROVAL
owner: Enterprise Architecture / PMO
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
revision_note: "v1.2 records all six RR documents authored and audited on 2026-08-19 (PGD-AUDIT-CAT-99), replaces the seventeen-hour-stale '0 written' status line, and assesses the category against its own five done-criteria. v1.1 corrected the code from RF to RR (collision with project_content category 99) and re-enumerates after RF-001/RF-002 were authored at 01:27 and 01:30 on 2026-08-18"
---

# Category 99 — Reference, Registers & Glossary (`RR`)

## Purpose

These are the documents that make a 601-file estate **navigable and internally consistent**.

They are the least glamorous category and, measured by audit findings prevented, the highest
leverage.

> ⚠ **Code note.** `project_content` category 99 already uses the code **`RF`**. This category
> therefore uses **`RR`**, so that `RF-001` (content glossary) and `RR-001` (engineering glossary)
> are never confused. This is the failure mode raised as finding `AF-11`, where the website and
> ERP content sets used identical-looking priority letters with different meanings.

## Documents

| ID | Document | Rule space | Status | Pri | Needed by |
|---|---|:--:|:--:|:--:|:--:|
| `RR-001` | Glossary & Acronym Register | `TRM` | ✅ | P1 | W1 |
| `RR-002` | **Identifier Convention Standard** | `IDC` | ✅ | **P0** | **Now** |
| `RR-003` | Document Standards & Template Library | `DSL` | ✅ | P1 | W1 |
| `RR-004` | Source Document Index & Evidence Register | `EVR` | ✅ | P1 | W1 |
| `RR-005` | **Standards & Regulatory Currency Register** | `CUR` | ✅ | **P0** | **Now** |
| `RR-006` | Master Cross-Reference & Traceability Index | `XRF` | ✅ | P1 | W2 |

**Status at 2026-08-19 20:22:** **6 written · 0 partial · 0 absent.** Audited in
[`PGD-AUDIT-CAT-99`](../_AUDIT/PGD-AUDIT-CAT-99_Category_99_Reference_Registers_and_Glossary_Audit.md)
— **29 findings, 2 critical, 6 against the category's own authoring and all six corrected before
issue, 11 closed.**

> **The ✅ is qualified by `PGD-A2-25`**, as every ✅ in this estate is: tests (a), (b) and (c) of
> `PGD-000` §0.3 are met and verified; test (d)'s **approval record** does not exist and cannot,
> until `GV-001` `CC-01` constitutes a body able to create one.

> ### ⚠ The status line above was wrong for seventeen hours, and that is this category's own subject
>
> It read *"0 written · 2 partially covered · 4 absent"* from 2026-08-18 01:42 until this update,
> while `RR-001`, `RR-002` and `RR-003` were written at 02:53, 02:59 and 03:08 on 2026-08-19 and
> `RR-004`–`RR-006` between 20:04 and 20:18. **A category overview is a second place a figure
> lives, and `PG-M10` says a figure in two places is only correct in the one somebody remembered.**
> Recorded as `RR-004` `EVR-F-08`, which found the same staleness in Categories 14 and 15's
> overviews, and it is the argument for `RR-006`'s generated index over any hand-maintained
> roll-up.

## What the six delivered — the five figures the estate did not previously hold

Counted at 2026-08-19 20:22, never quoted:

| Fact | Premise before | Counted |
|---|---|---:|
| Identifier prefixes in use | *"seven … plus"* ⇒ ~46 | **1,094** (≈900 de-noised) |
| Distinct identifier tokens | not recorded | **18,630** |
| Files in the estate | 601 | **798** |
| External-citation forms in this repository | not recorded | **248** |
| Document citation edges / nodes / orphans | not recorded | **3,320 / 138 / 0** |

**Three defects found by set difference that fourteen category audits had not found by reading:**
`RR-008`, a document cited seven times including in two *governing rules* and never registered;
`P38`, a portal cited in `M10`'s API consumer list where the space is `P01`–`P12`; and `BO-1`
against `BO-01`, **two objective sets in two digit forms denoting different objectives**, one of
them the basis of the BDT 876 lac benefit case.

**Two corrections applied to other categories at audit:** `UX-005` and `UX-007` — `RR-008` →
`RR-005`, seven citations; `RL-001` and `RL-005` — `M66` moved from a `G_Platform_and_Technology`
path that does not exist to `K_Platform_and_Technology`.

### Baseline movement during authoring

`project_content/99_Reference_and_Registers/` was an **empty folder** when this register's first
enumeration ran at **01:16** on 2026-08-18. Two files appeared during authoring:

| File | Written | Size | Covers |
|---|---|---:|---|
| `RF-001_ERP_Glossary_and_Acronym_Register.md` | 01:27 | 38 KB | `RR-001` for the **content** estate; explicitly substitutes for `99-01` |
| `RF-002_Source_Document_and_Evidence_Index.md` | 01:30 | 26 KB | `RR-004` for the **content** estate's source base |

Four `MM-*` multimedia specification files also appeared between 01:18 and 01:29.

`RR-001` and `RR-004` are therefore **◐, not ⛔**. What remains absent in both cases is the
**engineering** half: `RF-001` adjudicates content vocabulary, not the service-lifecycle terms used
across `M01`/`M02`/`M04`/`M31`; `RF-002` indexes content sources, not the module or engineering
estates. Recorded as finding `PGD-A1-03`.

## `RR-002` prevents eight existing audit findings

Every one of these findings is an identifier-space failure, and one standard prevents the class:

| Finding | What broke |
|---|---|
| `00-06` **C-02** | M31 exists in no register; the same applies to M32–M67 |
| `00-06` **C-03** | M04 carries two identifier sets (`FR-FRD-*` and `FR-BFO-*`); `FR-BFO-029` used twice |
| `00-06` **H-03** | Two incompatible CD registers; **48 identifiers collide** |
| `00-06` **H-04** | Module short-code table lists 30 of 67 codes |
| `AUDIT-016` **AP-02 (critical)** | `NFR-090/091/092` each used for **two different requirements** |
| `AUDIT-018` **EO-02** | Six `M12` business rules duplicated under a second identifier |
| `_MODULE_TEMPLATE` §0 | `R39–R50` roles and `SOD-13…30` used and unregistered |
| `AUDIT-015` **RP-01** | 250 KPI identifiers in use against 95 registered |

The estate operates seven module-local and programme-wide identifier spaces — `FR`, `BRU`, `AUT`,
`KPI`, `CD`, `R`, `SOD` — plus `NFR`, `INT`, `EVT`, `E`, `M`, `P`, `W`, `RSK`, twenty-one content
codes, and now seventeen guiding-document codes. Allocation authority is split across five
documents with no single standard.

`RR-002` consolidates them, states the allocating authority per space, and makes permanence and
retirement rules explicit. **The `RF`/`RR` collision this category had to resolve during its own
authoring is the argument for it.**

## `RR-005` prevents a second class of finding

Three findings are the same control failure — a citation that went stale and nobody re-checked:

| Finding | Stale citation | Current position |
|---|---|---|
| `00-06` **C-04a** | Digital Security Act 2018 | **Repealed twice** → Cyber Security Act 2023 → Cyber Security Ordinance 2025 |
| `00-06` **H-01** | NIST SP 800-88 **r1** | **Withdrawn 26 September 2025**; r2 published same day, requires IEEE 2883 |
| `00-06` **M-01** | "Odoo 19 released October 2025" | Released **18 September 2025** |

`00-06` §9 proposes exactly this register as the fix: *"Every statutory and standards citation
carries a verified-on date and is re-verified at each wave gate."* It remains a proposal.

## The vocabulary problem `RR-001` must still close

The estate uses **"job card", "service order", "work order", "repair order"** and **"service
request"** across 601 files with no adjudicated definition — while `M01`, `M02`, `M31` and `M04`
each own part of that lifecycle.

For a bilingual programme this compounds: `BN-003` supplies a bilingual terminology glossary for
customer-facing content and `RF-001` now covers content acronyms. Neither adjudicates the
engineering lifecycle vocabulary. A term that means two things in English means four in two
languages.

## What "done" looks like for this category

1. `RR-002` exists and every identifier in the estate resolves to exactly one allocating authority
   — including the newly-created `PGD` code space.
2. `RR-005` carries a verified-on date against every statute, standard and vendor version claim,
   with the next review date bound to a wave gate.
3. `RR-001` extends `RF-001` to adjudicate the service-lifecycle vocabulary across
   `M01`/`M02`/`M04`/`M31`, bilingually.
4. `RR-004` extends `RF-002` to index the module and engineering estates, not only content.
5. `RR-006` is **generated, not hand-maintained** — a hand-maintained cross-reference index over
   601 files will be wrong within a month. This category's own baseline moved twice in
   twenty-three minutes.

### Assessed against those five criteria at 2026-08-19 20:22

| # | Criterion | Verdict | Evidence |
|---:|---|:--:|---|
| 1 | `RR-002` exists; every identifier resolves to one allocating authority | **Partly** | `RR-002` §5 registers the spaces and names an authority for each, and §9 **freezes nine** whose registers are too far behind to allocate into. *Resolution* is `RR-006` `CHK-X1`, which now runs and **fails** — two phantoms, four dangling IDs, ten absent module documents. **A check that runs and fails is a control; one that cannot run is a plan.** The residue is `RR-002` §9's seven open thaw conditions |
| 2 | `RR-005` carries a verified-on date on every claim, next review bound to a gate | **✅ Met** | 118 rows, each with a verification source, a verified-on date and a next-review gate; §9's calendar is gate-bound with **one declared calendar exception**, the Finance Act / Mushak row |
| 3 | `RR-001` adjudicates the service-lifecycle vocabulary, bilingually | **✅ Met, with the residue named** | `RR-001` §5 rules the lifecycle as a concept system; §10.2 states that **three engineering terms with a customer surface are not settled bilingually**, rather than implying they are |
| 4 | `RR-004` indexes the module and engineering estates | **✅ Met** | Five repositories, 798 files, evidence-graded by family; supersedes `01-05` and `99-04`, both unwritten |
| 5 | `RR-006` is generated, not hand-maintained | **✅ Met** | Six scripts printed in full; a full regeneration in **under one second**, demonstrated eight minutes after issue. `XRF-01` forbids hand-editing §5 |

**Four of five met; one partly met with its residue named and owned.** The unmet half of criterion 1
is not a drafting gap — it needs seven registers updated by seven owners, which `RR-002` `IDC-01`
forbids this category from doing on their behalf.

## Dependencies

| Direction | Category | Relationship |
|---|---|---|
| Downstream | **All** | `RR-002` must precede any further identifier allocation anywhere |
| Downstream | `05_Security` | `RR-005` currency review is the control behind `SC-008` |
| Upstream | `00_Governance` | `RR-003` templates are enforced by `GV-011` document control |
| Peer | `01_Requirements` | `RR-006` index is the mechanical form of `RQ-004` traceability |
| Peer | `project_content/99_RF` | `RF-001` and `RF-002` cover the content half; `RR-001` and `RR-004` cover the engineering half |

## Audience and change frequency

| Attribute | Value |
|---|---|
| Primary audience | Everyone — this is the category new joiners and auditors read first |
| Change frequency | **Low for standards, continuous for registers and the generated index** |
| Standards basis | ISO/IEC 11179 · ISO 704 / ISO 1087 (terminology) · ISO 30401 · repository rules `RG-01`…`RG-08` |

## Existing material to build from

`1000fix_ERP_Module/FOLDER_STRUCTURE.md` §5 (naming), `03_Modules/_MODULE_TEMPLATE.md` §0 (identifier rules) ·
`1000fix_ERP_Module/00_Governance_and_Charter/00-01` §3 (identifier conventions, 30 of 67 codes) ·
`1000fix_ERP_Module/02_Architecture/02-02` §1, §5, §6 ·
`1000fix_ERP_Module/00_Governance_and_Charter/00-06` §9 and §10 (verification sources) ·
`project_content/99_Reference_and_Registers/RF-001`, `RF-002` *(new, 2026-08-18)* ·
`project_content/00_Content_Governance_and_Standards/CG-004`, `CG-005`, `CG-009` ·
`project_content/11_Localisation_Bengali/BN-003`, `BN-004`

---

*Category 99 · `RR` · 1000FiX ERP System v2.0 · CONFIDENTIAL*
