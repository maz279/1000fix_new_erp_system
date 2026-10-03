---
id: CG-001
title: Content Master Index — Registration and Maintenance Procedure
project: 1000FiX ERP System v2.0
content_type: Governance
version: 1.0
date: 2026-08-15
status: Approved
classification: CONFIDENTIAL — Internal Use Only
owner: Programme Content Lead
author: Programme Content Lead
reviewers: [Enterprise Architecture, PMO]
approver: Chief Technology Officer
purpose: >
  Registers the ERP & Portal Content Master Index under a permanent content identifier and
  defines how it is maintained. Without a single authoritative answer to "what content does
  this programme owe?", content is discovered late and blocks wave go-live.
traces_to: [ALL, 02-02 §1, 00-04 §5]
priority: P0
wave: W0
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/README.md (v2.2, enumerated 2026-08-15)
    verified: 2026-08-15
  - source: project_content/_AUDIT/AUDIT-001_Content_and_Repository_Integrity_Audit.md
    verified: 2026-08-15
supersedes: none
review_due: 2026-11-15
---

# CG-001 — Content Master Index
### Registration and maintenance procedure

---

## 0. Where the register actually lives

> **This file is not the register.** The register itself is
> [`../1000FiX_ERP_Content_Master_Index.md`](../1000FiX_ERP_Content_Master_Index.md).

Principle **CP-01** — *one content asset, one file* — forbids maintaining the same content in
two places. Reproducing the 452-row register here would create a second copy that drifts from
the first, which is precisely the failure mode that produced audit findings **AF-02** and
**AF-03** in the module repository.

This file therefore does three things the register cannot do for itself:

1. **Registers** the Master Index under the permanent content identifier `CG-001`, so it is
   governed by the same rules as everything it governs.
2. **Defines the maintenance procedure** — how a row is added, changed or retired, and how the
   counts are regenerated.
3. **Records the register's own control state** — version, enumeration date, owner, and the
   conditions under which it becomes non-authoritative.

| Attribute | Value |
|---|---|
| Content ID | `CG-001` |
| Governed artefact | `project_content/1000FiX_ERP_Content_Master_Index.md` |
| Artefact version | 1.0 |
| Artefact status | DRAFT FOR APPROVAL |
| Files registered | 452 |
| Categories | 21 |
| Last enumeration | 2026-08-15 |
| Owner | Programme Content Lead |
| Approver | Chief Technology Officer |
| Review cadence | Every wave boundary (rule `CM-R9`) |

---

## 1. Why the register exists

The 1000FiX ERP programme holds 67 module specifications and 12 portal specifications. Those
documents state what the system must **do**. Almost none states who produces the data, wording,
document or course that the doing depends on.

Audit `AUDIT-001` §7 lists eighteen enforcement points where a specification assumes content
exists and no workstream produces it. Two examples make the pattern concrete:

| The specification says | The content it assumes | Registered as |
|---|---|---|
| `BRU-SRM-09` — a service order cannot be assigned to a technician lacking current certification for that brand's warranty work | A certification and brand-authorisation register for the rule to evaluate against | `MD-011` |
| `P02` non-negotiable #3 — the Bengali interface must be complete, **including error messages** | A complete Bengali string bundle covering every error state | `BN-010` |

Neither rule can execute without its content. Neither piece of content was owned before this
register existed. **That is what the register is for.**

---

## 2. What the register contains

| § | Section | What it settles |
|---|---|---|
| §0 | How to read | The distinction between specification, content and code |
| §1 | Master statistics | 452 files, distribution by category, priority and wave |
| §2 | Governing principles | `CP-01` … `CP-11` — the eleven rules that make the set maintainable |
| §3 | Folder tree | The on-disk structure, its rationale, and the naming convention |
| §4 | **The register** | 452 rows: ID, file, contents, justification, priority, wave, owner, traceability |
| §5 | Portal coverage | Which content each of the twelve portals depends on |
| §6 | Production roadmap | Six phases mapped to waves W0–W9 with gate conditions |
| §7 | Effort estimate | 2,595–3,875 person-days (520–775 PW), stated as an estimate under rule `RG-05` |
| §8 | Audit summary | The 18 findings from `AUDIT-001` |
| §9 | Maintenance rules | `CM-R1` … `CM-R10` |
| §10 | Reading paths | Ten role-based entry routes |
| §11 | Website relationship | Why the two content sets stay separate, and their four interfaces |
| §12 | Status | Current position, counted not projected |

---

## 3. Maintenance procedure

### 3.1 Adding a content file — register first

**Rule `CM-R1` is absolute: the register entry is created before the file.** This is rule
`RG-01` from the module repository (`02-02` §1) applied to content, and it exists because the
inverse failure has already cost this programme two audits — a specification with no register
entry (M31, audit finding C-02), and 44 specifications whose register entries denied they were
written (audit finding H2-01).

| Step | Action | Who |
|---|---|---|
| 1 | Establish that no existing file already covers it (principle `CP-01`) | Requester |
| 2 | Allocate the next free ID in the category from `CG-005` | Programme Content Lead |
| 3 | Write the **"Why it is needed"** justification — the consequence of the file's absence. A row with no consequence is refused, not written (principle `CP-03`) | Requester |
| 4 | Name the module, portal or specification it traces to (principle `CP-04`). Content with no upstream requirement is scope creep | Requester |
| 5 | Set priority (`P0`–`P3`), wave (`W0`–`W9`) and accountable function | Programme Content Lead |
| 6 | Add the row to §4 of the register, in ID order | Programme Content Lead |
| 7 | Update §1 statistics **by enumeration**, never by increment (rule `CM-R2`) | Programme Content Lead |
| 8 | Log the addition in `RF-006` | Programme Content Lead |
| 9 | **Only now** create the file, from the correct template in `_templates/` | Author |

### 3.2 Changing a row

| Change | Permitted | Procedure |
|---|:--:|---|
| Description, justification, owner | Yes | Edit in place; log in `RF-006` |
| Priority or wave | Yes | Requires the accountable function's agreement; log in `RF-006` |
| File name | Yes | Update the name and every reference; **the ID never changes** (`CP-02`, rule `CM-R4`) |
| Content ID | **No** | IDs are permanent. If a file's scope changes beyond recognition, retire the ID and allocate a new one |
| Category | Exceptionally | Requires Content Lead approval and a new ID in the destination category; the old ID is retired, not moved |

### 3.3 Retiring a row

1. Mark the register row `WITHDRAWN` with the date and reason. **Do not delete the row** — a
   deleted row makes the ID look free, and `CG-005` forbids reuse.
2. Move any written file to `_ARCHIVE/` with a `SUPERSEDED_` prefix and a header note
   (principle `CP-10`, rule `CM-R5`).
3. Record the retirement in `RF-006` and in the `CG-005` retirement log.
4. Re-enumerate §1 statistics.

### 3.4 Regenerating the statistics

**Rule `CM-R2` and principle `CP-11`: figures are generated, never projected.** This is rule
`RG-06` from the module repository, applied to content, plus the extension proposed as `RG-07`
in `AUDIT-001` §3 — *authors* count, not only auditors, and every figure carries its
enumeration date.

```bash
# Total registered rows
grep -cE "^\| [A-Z]{2}-[0-9]{3} \|" 1000FiX_ERP_Content_Master_Index.md

# Rows per category
for p in CG VB MD UI NT DT SP KB TR HC LG BN DM TS RP AP CM OP EO MM RF; do
  printf "%s %s\n" "$p" "$(grep -cE "^\| $p-[0-9]{3} \|" 1000FiX_ERP_Content_Master_Index.md)"
done

# Files actually written on disk
find . -name "??-[0-9][0-9][0-9]_*.md" -not -path "./_*" | wc -l
```

Every completeness figure published from these commands **must** carry the date it was run.
A figure without an enumeration date is not authoritative and must not be quoted to the
Steering Committee.

### 3.5 Auditing the register

Run `_AUDIT/AUDIT_Checklist_Recurring.md` at every wave boundary and before any Steering
Committee paper that quotes a completeness figure. Findings are filed as `AUDIT-nnn` and
indexed in `RF-012`.

---

## 4. When the register stops being authoritative

The register is **non-authoritative**, and must be re-verified before use, if any of the
following is true:

| Condition | Why it invalidates the register |
|---|---|
| The last enumeration date is more than one wave old | Files are written continuously; counts decay |
| A file exists on disk with no register row | Rule `CM-R1` has been breached; the register no longer describes reality |
| Two documents state different counts for the same thing | Finding `AF-02` recurring; neither figure can be trusted |
| A completeness percentage appears without an enumeration date | Proposed rule `RG-07` breached |
| An open critical audit finding affects the register's own structure | The structure being described is not the structure in force |

---

## 5. Open items carried by the register

These are recorded here because they are the register's own risks, not the programme's.

| # | Item | Consequence if unresolved | Owner | Audit ref |
|---|---|---|---|---|
| 1 | No Programme Content Lead is appointed | Every row in the register has an accountable *function* but no accountable *person* | Programme Director | `AF-09`, R-07 |
| 2 | Content effort (520–775 PW) is not in the business case | Phase 0 content is already on the W1 critical path and unfunded | Programme Director | `AF-09` |
| 3 | `CG-002` Content Operating Model is not yet approved | No content may reach `Approved` status until it is | Programme Content Lead | — |
| 4 | The twelve portal specifications are misfiled | `RF-005` portal coverage cannot be maintained mechanically | CTO | `AF-01` |

---

## 6. Related documents

| Document | Relationship |
|---|---|
| [`../1000FiX_ERP_Content_Master_Index.md`](../1000FiX_ERP_Content_Master_Index.md) | The register this file registers and governs |
| [`CG-002_Content_Operating_Model_and_RACI.md`](CG-002_Content_Operating_Model_and_RACI.md) | Who does the work the register describes |
| [`CG-005_Content_ID_and_Naming_Convention.md`](CG-005_Content_ID_and_Naming_Convention.md) | How IDs in the register are allocated and retired |
| [`CG-006_Content_Lifecycle_and_Versioning_Policy.md`](CG-006_Content_Lifecycle_and_Versioning_Policy.md) | The status values a register row may report |
| `RF-003` Content-to-Requirement Traceability Matrix | Proves `CP-04` is being honoured |
| `RF-006` Content Decision Log | Records every register change |
| `02_Architecture/02-02` §1 | The module register rules this procedure mirrors |

---

## 7. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Registers the Master Index v1.0 (452 files, enumerated 2026-08-15) and defines the maintenance procedure | CTO (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to the governance template
- [x] Every factual claim carries a source and a verification date
- [x] Terminology matches `CG-004`
- [x] All internal links resolve
- [x] Accessibility standard `CG-011` applied — n/a, internal governance document
- [x] Bengali counterpart — n/a, `bilingual: no` per `CG-010`
- [ ] Named approver recorded — **pending CTO approval**
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [x] Decisions logged in `RF-006`

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
