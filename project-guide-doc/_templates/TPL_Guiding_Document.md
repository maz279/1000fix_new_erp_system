---
id: <CODE>-<nnn>
title: <Full Document Name>
category: <nn> — <Category Name>
code: <CODE>
project: 1000FiX ERP System v2.0
version: 1.0
date: <YYYY-MM-DD>
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: <Role — never a personal name>
approver: <Role with authority to baseline this document>
standards_basis: <e.g. ISO/IEC/IEEE 29148:2018>
traces_to: <requirement, module, portal, NFR or audit finding that requires this document>
depends_on: <PGD IDs that must exist first>
verified_on: <YYYY-MM-DD — MANDATORY if this document cites a statute, standard or vendor version>
priority: P0 | P1 | P2 | P3
needed_by: W<n> | Now
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# <CODE>-<nnn> — <Full Document Name>

### Category <nn> · Code `<CODE>` · <Standards basis>

---

> **Before writing, read this.**
>
> 1. **`PG-01` Register-first.** This document may not exist unless its row is already in
>    `PGD-000`. If you are creating a new document, register it first.
> 2. **`PG-03` Count, do not consult.** Every figure describing what this document contains — item
>    counts, coverage, effort — is **counted at the time of writing**. A number quoted from another
>    register is not evidence. This rule caused the largest finding in both repository audits.
> 3. **`PG-06` Cite standards.** Name the standard this document conforms to, and where it
>    deliberately departs from it, say so and say why.
> 4. **`PG-M4` Verify citations.** Any statute, standard or vendor version claim carries a
>    `verified_on` date in the front matter above. Three critical audit findings — `C-04`, `H-01`,
>    `M-01` — were stale citations.

---

## 1. Purpose

> One paragraph, in plain language, stating what this document is for and what decision or
> activity it unblocks. Written so a business owner understands it, not only an engineer.

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | … |

**Explicitly out of scope:**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| … | `<CODE>-<nnn>` | … |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| … | … |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause / section | How this document conforms | Departure and rationale |
|---|---|---|---|
| … | … | … | … |

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| … | `../…` | … |

### 2.3 Audit findings this document closes

| Finding | Source audit | How this document closes it |
|---|---|---|
| … | `00-06` / `00-07` / `AUDIT-nnn` | … |

---

## 3. <Body — structured per the standard named in the front matter>

> Replace this section with the structure the governing standard requires. For example:
>
> - An **SRS** follows ISO/IEC/IEEE 29148:2018 **§9.6** (clauses 9.6.1–9.6.20): SRS overview,
>   purpose, scope, product perspective, product functions, user characteristics, limitations,
>   assumptions and dependencies, apportioning, specified requirements, external interfaces,
>   functions, usability, performance, logical database, design constraints, standards compliance,
>   software system attributes, verification, supporting information.
>   **§9.5 is the *System* Requirements Specification (SyRS)**, clauses 9.5.1–9.5.19 — a different
>   information item, above the software boundary. *(Corrected 2026-08-18; the prior text cited
>   §9.5 for the SRS. Finding `RQA-01`, `_AUDIT/PGD-AUDIT-002`.)*
> - A **SAD** follows ISO/IEC/IEEE 42010:2022: stakeholders, concerns, viewpoints, views,
>   correspondences, rationale.
> - An **SDD** follows IEEE 1016-2009: design viewpoints — context, composition, logical,
>   dependency, information, interface, structure, interaction, state dynamics, resource.
> - A **test plan** follows ISO/IEC/IEEE 29119-3:2021.
>
> Do not invent a structure where a standard exists.

---

## 4. Decisions Recorded

Local decisions of this document. **Identifiers take the form `<DOCUMENT-ID>-D-nn`** — for example
`GV-001-D-01`, `RQ-003-D-02`.

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `<CODE>-<nnn>-D-01` | … | … | … | … | … |

> **Rule `DL-06` — never use the bare form `D-01` here.** `D-nnn` is the **programme** decision
> space and is allocated **only** by `GV-003`. Applied literally across 140 documents, a bare
> `D-01` would produce up to 140 different decisions with the same identifier — the defect class
> behind `H-03` (48 colliding CD identifiers), `H2-04` (22 colliding KPI identifiers) and
> `PGD-A1-01`. Corrected at issue of `GV-003`; recorded as finding `PGD-A2-03`.
>
> Significant architecture decisions are additionally recorded as ADRs in
> `02_Architecture_and_Design/AR-004_*`. This table is the local record; the ADR is the programme
> record. A decision with programme-wide effect is raised as a `D-nnn` in `GV-003`.

---

## 5. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| Q-01 | … | `<Role>` | W<n> | … |

> An open question with no owner and no needed-by date is not an open question — it is an
> unrecorded risk. Escalate it to `GV-005` RAID.

---

## 6. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | … | … |

**Definition of done.** This document is complete when every acceptance criterion above is met,
its `PGD-000` status is updated with a fresh enumeration date, and its approver has signed.

---

## 7. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `<CODE>-<nnn>` | This document depends on it |
| Downstream | `<CODE>-<nnn>` | It depends on this document |
| Lateral | `../1000fix_ERP_Module/…` | Module or portal specification realised here |
| Lateral | `../project_content/…` | Content this document governs or consumes |

---

## 8. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` ·
`./\_CATEGORY_OVERVIEW.md` · `<other PGD documents>`

**Workspace**
`../../1000fix_ERP_Module/…` · `../../project_content/…` · `../../primary-doc/…`

**External standards and sources**
`<each with a verification date where regulatory>`

> Verify every path resolves before issuing. Nine module files carried references to superseded
> filenames until the August 2026 audits corrected them.

---

## 9. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | <YYYY-MM-DD> | <Role> | Initial issue | <Role> |

---

*`<CODE>-<nnn>` · Category <nn> · 1000FiX ERP System v2.0 · CONFIDENTIAL*
