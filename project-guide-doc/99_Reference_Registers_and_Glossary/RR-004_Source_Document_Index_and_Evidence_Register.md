---
id: RR-004
title: Source Document Index and Evidence Register
category: 99 — Reference, Registers & Glossary
code: RR
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-19
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Enterprise Architecture
approver: Chief Technology Officer
standards_basis: ISO 19011:2018 §6.4 (audit evidence) · ISO 15489-1:2016 §5, §8 (records management) · ISO 10007:2017 §5.3, §5.5 (configuration identification and status accounting) · ISO/IEC/IEEE 15289:2019 (information item content) · ISO/IEC 11179-6:2023 §7 (registration status)
traces_to: PGD-000 Category 99 RR-004 · _CATEGORY_OVERVIEW "RR-004 extends RF-002 to index the module and engineering estates" · 99-04 (unwritten) · 01-05 (unwritten) · RF-002 · 00-01 §4 · AF-01 · AF-04 · PGD-A1-03 · CHA-12 · RLA-22
depends_on: PGD-000 · RR-002 · RR-003 · RR-005
verified_on: 2026-08-19
priority: P1
needed_by: W1
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
enumeration_timestamp: 2026-08-19 19:54 (repository wall clock — see RR-005 §4.4)
rule_prefix: EVR — verified to return zero occurrences in identifier form across all 792 markdown files of the workspace before allocation, at 2026-08-19 19:54. Candidates SDX, IDX and DOC were also free; SRC was rejected outright, holding 566 occurrences as the legacy-source space in MG-002 and RL-006
review_cycle: Every wave gate, and on any repository baseline movement — §9
---

# RR-004 — Source Document Index and Evidence Register
# 1000FiX ERP System & Portal Suite v2.0

### Category 99 · Code `RR` · ISO 19011:2018 · ISO 15489-1:2016 · ISO 10007:2017

---

> **Before writing, read this.**
>
> 1. **`PG-01` Register-first.** This document's row exists in `PGD-000` Category 99 as `RR-004`,
>    status ◐ (`RF-002`), priority **P1**, needed by **W1**. It was registered before it was written.
> 2. **`PG-03` / `RG-06` Count, do not consult.** Every figure below was counted from the filesystem
>    at **2026-08-19 19:54**, by the commands printed in §4.1. Two figures disagree with `PGD-000`
>    §3 and both disagreements are stated rather than smoothed.
> 3. **`PG-06` Cite standards.** ISO 19011:2018 §6.4, ISO 15489-1:2016 and ISO 10007:2017 govern.
>    Departures are declared in §2.1.
> 4. **`PG-M4` Verify citations.** `verified_on: 2026-08-19`. External-source currency is
>    **`RR-005`'s**, not this document's; the boundary is in §1.1.

---

## 1. Purpose

An engineering estate is only as good as the evidence under it. This programme has **792 markdown
files across five repositories**, and until this document there was no single place that answered
three questions a reader, an auditor or an incoming vendor asks constantly:

1. **What sources exist?** — the inventory.
2. **Which of them is authoritative, and which is superseded?** — the evidence grade.
3. **If this source changes, what has to be re-opened?** — the reverse index.

`project_content/99_.../RF-002` answered all three for the **content** estate on 2026-08-18 and
did it well. It does not cover the module estate, the primary documents or this repository — which
is exactly what `PGD-000`'s `RR-004` row records: *"the module and engineering estates are still
unindexed, and `00-01` §4 holds an evidence table pointing at paths that have since moved."*

**This document is that index.** It registers all **792** sources by family, grades each one, and
publishes a reverse index so that a change to a source is a scheduled re-opening rather than a
surprise.

**Eight findings came out of building it**, of which the sharpest is not a missing document but a
counting one: **ten module-repository documents are cited 134 times by identifier and do not exist
on disk.** Every one of those ten is recorded as absent *somewhere* — in `AF-04`, in a `DM-001`
open item, in a parenthetical *"(planned)"* — and **nowhere are they recorded together**, so a
reader who meets `02-04` in a sentence has no way to learn that it has never been written.

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | Every **file in the workspace** — five repositories, 792 markdown files, 803 files of all types — registered by family with a count, a size and a baseline date |
| 2 | The **evidence grade** of each family: authoritative, superseded, draft, derived or absent |
| 3 | The **cited-and-absent** population — sources referenced by identifier that do not exist |
| 4 | The **reverse index**: for each source family, which `PGD` documents re-open if it changes |
| 5 | **Path and link integrity** — whether the estate's own internal references actually resolve |
| 6 | The **baseline-movement record**: what this repository weighed at each enumeration, and why that matters to every absence claim in it |
| 7 | The **evidence rules** and the checks that enforce them |

**Explicitly out of scope:**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| **External** standards, statutes and vendor versions | `RR-005` | An external source has a publisher and an edition; an internal one has a path and a baseline. Different evidence model, different review trigger |
| The **content** estate's source base | `RF-002` | Already indexed, well, on 2026-08-18. §5.5 registers it as a family and adopts it; it is not restated |
| **Legacy operational systems** as data sources (`SRC-001`…`SRC-048`) | `MG-002`, `RL-006`, `DM-002` | Those are systems to be extracted from and switched off, not documents to be cited. Different register, and `RR-002` §5 keeps the `SRC-` space separate for exactly this reason |
| The **traceability graph** between identifiers | `RR-006` | This register indexes *documents*; `RR-006` indexes *identifiers*. §7's reverse index is document-grain and deliberately coarse |
| Whether a source is **correct** | The category audits in `_AUDIT/` | This register records what exists and what grade it holds. It does not re-audit content |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| **A new joiner or incoming vendor** | §5 — the whole estate in one table, with what to read first and what not to trust |
| **Document authors** | §5's grade column, before citing anything; and §6, before citing `old-primary-doc` |
| **Auditors** | §8's eight findings, and §4.1's commands to reproduce every figure |
| **PMO** | §7's reverse index — the change-impact instrument |
| **CTO** | `EVR-F-01` and `EVR-F-03`: ten absent sources with 134 citations, and a superseded baseline still in live use |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause / section | How this document conforms | Departure and rationale |
|---|---|---|---|
| **ISO 19011:2018** *Auditing management systems* | §6.4.3 collecting and verifying information; §6.4.7 audit evidence | §3.2's five evidence grades implement 19011's distinction between verified information (evidence) and unverified information (which *"can be useful … but is not audit evidence"*). Every §5 family carries a grade and a verification date | 19011 grades evidence per audit. This register grades it per **source**, once, and re-verifies at gates. Declared |
| **ISO 15489-1:2016** *Records management* | §5.2 (characteristics: authenticity, reliability, integrity, usability); §8.4 (registration) | §3.3 tests every family against 15489's four record characteristics. §5 is the registration instrument | 15489 assumes a records system with capture and disposition. This estate has a filesystem and no version control (`EVR-F-06`), so integrity is asserted by enumeration rather than guaranteed by a system. **Declared, and it is the most material departure in this document** |
| **ISO 10007:2017** *Configuration management* | §5.3 configuration identification; §5.5 configuration status accounting | §5 is the configuration identification of the documentation baseline; §6's movement record is status accounting | No configuration control board exists (`PGD-A1-09`). Identification and status accounting are performed; control is not. Declared |
| **ISO/IEC/IEEE 15289:2019** | Information item content | Used to classify what each source family *is* — plan, specification, register, report — consistently with `RR-003` §3.2's class model | None; `RR-003` is the governing instance and this document adopts its classes |
| **ISO/IEC 11179-6:2023** | §7 registration status | §3.2's grades map onto 11179-6's registration-status lifecycle, as `RR-002` §3.5 and `RR-005` §3.2 also do | Deliberately the same model in all three registers, so a reader learns it once |

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| `RF-002` | `../../project_content/99_Reference_and_Registers/RF-002_Source_Document_and_Evidence_Index.md` | The content estate's index. Its evidence classes, source families, reverse index and `EV-F1` method are adopted and extended here |
| `00-01` §3, §4 | `../../1000fix_ERP_Module/00_Governance_and_Charter/00-01_Master_Index_and_Document_Map.md` | The module estate's own map and evidence table — the table `PGD-000` records as *"pointing at paths that have since moved"* |
| `00-06`, `00-07` | `../../1000fix_ERP_Module/00_Governance_and_Charter/` | Repository audits; source of `AF-01` (portal misfiling) and `AF-04` (`00-05` absent) |
| `RR-002` §5, §7.2 | `./RR-002_Identifier_Convention_Standard.md` | Identifier forms; the `rule_prefix:` collision-check procedure, followed here |
| `RR-003` §3.2, §6.2 | `./RR-003_Document_Standards_and_Template_Library.md` | Document classes and the front-matter schema whose `traces_to:` and `depends_on:` keys this register reads |
| `RR-005` §6, §7 | `./RR-005_Standards_and_Regulatory_Currency_Register.md` | External sources; the boundary declared in §1.1 |
| The filesystem | the workspace root | **The primary evidence.** Every figure in §4 and §5 is a count, not a quotation |

### 2.3 Audit findings this document closes

| Finding | Source | How this document closes it |
|---|---|---|
| `PGD-000` `RR-004` row | *"The module and engineering estates are still unindexed"* | §5.3, §5.4 and §5.6 index them. **Closed** |
| `PGD-000` `RR-004` row | *"`00-01` §4 holds an evidence table pointing at paths that have since moved"* | §8's `EVR-F-02` measures path integrity across the whole repository — **1,204 backtick paths and 942 markdown links checked**, results in §5.7. The `00-01` §4 restatement is assigned, not performed |
| `AF-04` | `00-05` does not exist | §5.3.1 registers it in the cited-and-absent table with its 24 citations, alongside nine others. **Consolidated, not closed** — writing it is not this register's act |
| `AF-01` | Twelve portal specifications filed in `03_Modules/K_...` rather than `04_Portals_and_Applications/` | §5.3.2 records the count (**12**) and the live state, and adopts `RF-001`'s ruling: **cite the identifier, not the path**. The CTO decision remains open |
| `RF-002` `EV-F1` | Sixty-eight content files carry a verification date in the future | §5.7.3 runs the same test against the engineering estate. **Result: 0 of 130.** Closed for this repository |
| `01-05` / `99-04` unwritten | The planned source index and evidence register | **Superseded, not awaited.** This document is their engineering-estate form; §5.3.1 records both as absent-and-superseded |
| `PGD-A1-03`, `CHA-12`, `RLA-22` | Baseline moved during authoring, ten recorded times | §6 is the movement record, kept as a table rather than as a paragraph in each document's revision note. **Structurally closed**; recurrence is prevented by `EVR-05`, not by this row |

---

## 3. The Evidence Model

### 3.1 What "a source" is, in this register

A **source** is a file in the workspace that another document relies on for a fact. Three things
follow, and they are what make this register different from a directory listing:

| Property | Consequence |
|---|---|
| A source is **cited**, not merely present | A file nobody cites is inventory, not evidence. §5 records both, and marks the difference |
| A source has a **grade**, not a status | *"Exists"* is a property of the filesystem. *"Can be relied on"* is a judgement, and §3.2 makes it explicit |
| A source has **dependents** | Which is why §7 exists. A source with no recorded dependents cannot be changed safely, because nobody knows what breaks |

### 3.2 Evidence grades

| Symbol | Grade | Meaning | May be cited as |
|:--:|---|---|---|
| **A** | **Authoritative** | On disk, current, owned, and the recognised home of the facts it holds | A basis for a design decision |
| **S** | **Superseded** | On disk, and a later artefact has replaced it. Retained for history | History only. **Never as a basis.** `EVR-02` |
| **D** | **Derived** | On disk, and its content is computed from other sources — a register, an index, a roll-up | A convenience. The upstream source governs on any disagreement |
| **P** | **Provisional** | On disk, but its own front matter says `DRAFT FOR APPROVAL` and no approval record exists | A basis, **with the qualification stated**. This is 130 of 130 guiding documents (`PGD-A1-09`) |
| **∅** | **Absent** | Cited by identifier, not on disk | **Nothing.** A citation of an ∅ source is a citation of an intention |

> **The ∅ grade is the one this register was worth writing for.** An absent source does not
> announce itself: it appears in a sentence, in backticks, next to sources that do exist, and reads
> exactly like them. §5.3.1 enumerates all ten.

### 3.3 The ISO 15489-1 record characteristics, tested

| Characteristic | 15489-1 §5.2 definition | This estate's position |
|---|---|---|
| **Authenticity** | Is what it purports to be; created by the purported author at the purported time | ⚠ **Partial.** Front matter names an `owner` role on all 130 guiding documents; no signature, no approval record, no version control. Authorship is asserted, not provable |
| **Reliability** | Full and accurate representation, trustworthy as evidence | ✅ For enumerable facts — every guiding document prints the commands behind its counts (`PG-03`) |
| **Integrity** | Complete and unaltered | ⛔ **Not met.** **The workspace has no version control.** A file can be altered with no record. `EVR-F-06` |
| **Usability** | Can be located, retrieved, presented and interpreted | ✅ **Measured.** 942 of 942 markdown links resolve; 1,191 of 1,204 backtick paths resolve. §5.7 |

> ### `EVR-F-06` — the estate has no version control, and every other evidence claim rests on that
>
> `find` returns 803 files; `git status` returns nothing, because there is no repository. There is
> therefore **no mechanism by which any document's integrity can be demonstrated**, no diff, no
> attribution and no rollback. Every figure in this register — including every figure in every other
> register — is a statement about the filesystem *at an instant*, and the only thing standing
> between it and silent alteration is that nobody has a motive.
>
> This is not a theoretical concern in this workspace. §6 records **twelve** baseline movements, of
> which several changed the truth value of published absence claims (`CHA-12`, `RLA-22`). Version
> control would have made each of those a visible commit rather than an audit finding.
>
> **Severity High**, owner **CTO**, needed **Now**. The remediation is one command and a decision
> about where the remote lives; the reason it has not happened is that no document has ever owned
> it. This one does.

### 3.4 The rules

| # | Rule | Enforced by |
|---|---|---|
| `EVR-01` | **Every citation of an internal source resolves** — to a path that exists or to a §5.3.1 absent-register row | `CHK-E1` |
| `EVR-02` | **A grade-S source is never cited as a basis.** Where a fact exists only in a superseded source, it is restated in a current one first | `CHK-E2` |
| `EVR-03` | **Cite the identifier, not the path**, wherever the two disagree — `RF-001`'s ruling, adopted | Review |
| `EVR-04` | **Every figure quoted from another document carries that document's enumeration timestamp**, or it is re-counted | `RR-005` `CHK-C2` |
| `EVR-05` | **An absence claim carries the instant it was tested**, inside the sentence — not the date, the instant | Review; §6 |
| `EVR-06` | **A source with no recorded dependents may not be changed** until §7 has a row for it | §7 |
| `EVR-07` | **This register is re-enumerated at every gate and on any baseline movement**, and §6 gains a row | §9 |

---

## 4. The Measured Position

### 4.1 Method

```bash
# Per-repository file, markdown and byte counts
for d in primary-doc old-primary-doc 1000fix_ERP_Module project_content project-guide-doc; do
  printf "%-22s md=%-5s all=%-5s bytes=%s\n" "$d" \
    "$(find "$d" -name '*.md' -type f | wc -l)" \
    "$(find "$d" -type f | wc -l)" \
    "$(find "$d" -name '*.md' -type f -printf '%s\n' | awk '{s+=$1} END{print s}')"
done

# Markdown link integrity, resolved relative to each citing file
grep -oE '\]\([^)#][^)]*\.md[^)]*\)' "$f" | sed 's/^](//;s/)$//;s/#.*//'

# Cited-and-absent module documents. Backticks matter: an unquoted nn-nn
# pattern also matches every date in the estate and returns 101 false rows.
grep -rhoE '`(0[0-9]|1[0-9])-[0-9]{2}`' --include='*.md' . | tr -d '`' | sort -u
```

> **The backtick constraint is not fussiness.** The first pass of the third command, written
> without backticks, returned **101** candidate identifiers. Eighty-three of them were dates
> (`08-19`), times (`02-41`) and numeric ranges. The correct answer is **28 cited, 10 absent**.
> This is the same lesson `RR-005` §4.1 records against its own IEEE regex and `RF-001` §4.3
> records as `GL-02`: **an under-specified pattern reports a wrong world confidently.**

### 4.2 The estate, counted

| Repository | `.md` | All files | Bytes of markdown | Grade | Role |
|---|---:|---:|---:|:--:|---|
| `primary-doc/` | **4** | 4 | 1,258,487 | **A** | BRD, RFP, URD, Technology Stack — the demand-side baseline |
| `old-primary-doc/` | **6** | 6 | 674,917 | **S** | The v1.0 baseline, plus the Odoo 19 CE strategy and the missing-document checklist |
| `1000fix_ERP_Module/` | **123** | 123 | 6,547,493 | **A** | 67 module + 12 portal + 6 cross-cutting specifications, governance, architecture |
| `project_content/` | **488** | 488 | 11,056,762 | **A** | 21 content categories, 22 audits, 12 templates |
| `project-guide-doc/` | **171** | 182 | 7,917,226 | **P** | This repository: 133 guiding documents, 14 audits, 17 overviews, 1 template |
| **Workspace** | **792** | **803** | **27,454,885** | — | Enumerated **2026-08-19 19:54** |

**Two figures disagree with `PGD-000` §3 and the disagreement is stated, not smoothed:**

| Figure | `PGD-000` §3 (02:41) | Counted here (19:54) | Delta |
|---|---:|---:|---:|
| Workspace `.md` | 782 | **792** | **+10** |
| `project-guide-doc/` `.md` | 161 | **171** | **+10** |
| Guiding documents on disk | *119 authored* | **133** | **+14** |

The register is not wrong; it is **timestamped, and the timestamp has expired**. That is the whole
argument for `RG-08`, and §6 is the record of how often it happens.

### 4.3 What is cited versus what merely exists

| Population | Count | Note |
|---|---:|---|
| Guiding documents on disk (`CODE-nnn_*.md`) | **133** | Excludes two `README.md` files inside `IN-002_artefacts/` and `IN-003_artefacts/` that match the filename pattern but carry no front matter |
| Distinct guiding-document IDs on disk | **133** | No duplicates. `RR-002` `IDC-09` holds in this repository |
| Guiding documents **cited by at least one other** | **133 of 133** | **Zero orphans.** Every document on disk is referenced by another |
| Document-to-document citation edges | **3,060** | §7.1 |
| `PGD` IDs cited but **not on disk** | **8** — `BM-001`, `BM-004`, `BM-005`, `CO-001`, `RR-004`, `RR-005`, `RR-006`, **`RR-008`** | §5.6.2 |
| Module-repository IDs cited in backticks but **not on disk** | **10**, with **134** citations | §5.3.1 |
| Markdown links checked | **942** | **0 broken** |
| Backtick relative paths checked | **1,204** | **13 broken**, of which **2** are genuine errors |

> **Zero orphans is a real result and deserves saying.** In a 133-document estate written by
> multiple hands over four days with no version control and no index, **not one document is
> unreferenced.** That is stronger cross-linking than most funded programmes achieve, and it is why
> `RR-006`'s generated index has something to generate from.

---

## 5. The Source Register

### 5.1 `primary-doc/` — the demand-side baseline · Grade **A**

| Source | Bytes | Baseline | Grade | What it establishes | Cited by |
|---|---:|---|:--:|---|---:|
| `1000FiX_ERP_System_Comprehensive_BRD.md` | 336,387 | 2026-08-13 21:47 | **A** | Business requirements; §6.5 the `SRC-001`/`SRC-002` withdrawal at W2 — the only irreversible deadline in the programme; §19 the cost-benefit analysis audit `H-02` disowns | Heavily |
| `1000FiX_ERP_System_Comprehensive_RFP.md` | 276,075 | 2026-08-13 21:46 | **A** | The issued procurement instrument. §4.3's 21 contractual practices; §17 evaluation methodology. **Discharges `PGD-000` `CO-001`** | Heavily |
| `1000FiX_ERP_System_Comprehensive_URD.md` | 284,152 | 2026-08-13 23:28 | **A** | User requirements by role | Moderately |
| `1000FiX_ERP_Technology_Stack_Specification.md` | 361,873 | 2026-08-14 00:33 | **A** | The declared stack. `TD-01` Odoo 19 CE as core | Heavily |

**94 of 133 guiding documents cite `primary-doc/`.** It is the most-relied-on family in the estate,
and it is four files.

> **`CO-001` is discharged by a file in this family, and `PGD-000`'s model cannot express that.**
> `PGD-000` marks `CO-001` ✅ *"`primary-doc/…RFP.md`"* — correctly. But a mechanical sweep of
> `PGD` identifiers against the filesystem reports `CO-001` as dangling (§4.3), because no
> `CO-001_*.md` exists. The same applies to `BM-001`, discharged by `06-02`. **This is a register
> modelling gap, not a defect in either document**, and `RR-006` §6 fixes it by giving every
> register row a `discharged_by` path. Recorded as `EVR-F-05`.

### 5.2 `old-primary-doc/` — the v1.0 baseline · Grade **S**

| Source | Bytes | Baseline | Grade | Note |
|---|---:|---|:--:|---|
| `1000FiX_ERP_System_Comprehensive_BRD.md` | 110,712 | 2026-03-18 | **S** | Superseded by `primary-doc/` BRD, which is **3.0×** its size |
| `1000FiX_ERP_System_Comprehensive_RFP.md` | 86,155 | 2026-03-17 | **S** | Superseded. **Holds the `BO-1`…`BO-9` objective set** — see `EVR-F-04` |
| `1000FiX_ERP_System_Comprehensive_URD.md` | 125,684 | 2026-03-18 | **S** | Superseded |
| `1000FiX_ERP_Technology_Stack_Specification.md` | 190,745 | 2026-03-18 | **S** | Superseded |
| `1000FiX_ERP_Implementation_Strategy_Odoo19CE_OpenSource.md` | 99,159 | 2026-03-18 | **S**/**A** | **The one ambiguous file in the estate.** No v2.0 successor exists. Cited as though current |
| `1000FiX_ERP_Missing_Implementation_Documents.md` | 62,462 | 2026-03-18 | **S**/**A** | The original missing-document checklist — the ancestor of `PGD-000` itself. Superseded in function, unsuperseded in fact |

> ### `EVR-F-03` — a superseded baseline is cited 51 times in 24 live documents
>
> `old-primary-doc/` is grade **S**. `EVR-02` says a grade-S source is never cited as a basis.
> Counted at 2026-08-19 19:54: **24 of 133 guiding documents reference `old-primary-doc/`, 51 times
> between them.**
>
> Most of those are legitimate — a history citation, a *"the v1.0 pillar architecture said…"*
> comparison. Two of the six files are not history at all:
>
> | File | Why it is a problem |
> |---|---|
> | `..._Implementation_Strategy_Odoo19CE_OpenSource.md` | It is the **only** implementation-strategy document in the workspace. There is no v2.0 successor. It is therefore being relied on as authoritative while filed in a directory whose name declares it superseded |
> | `..._Missing_Implementation_Documents.md` | The direct ancestor of `PGD-000`. Where the two disagree, nothing states which wins |
>
> **The failure mode is specific.** A reader cites `old-primary-doc/…Implementation_Strategy…`
> because it is the only document that answers the question, and inherits a v1.0 assumption — the
> five-pillar architecture, the `BO-1` objective set, the pre-expansion scope — into a v2.0
> decision. `GL-04` in `RF-001` is exactly this failure already realised: **30 `FR-SLS-`
> requirements whose only home is a superseded pillar file.**
>
> **Remediation.** Two acts:
> 1. **W1** — `AR-002` or `GV-004` restates the implementation strategy at v2.0, or explicitly
>    re-baselines the v1.0 document as current with a new front matter. Owner **Enterprise
>    Architecture**. Either is fine; the present position — relied on and labelled superseded — is
>    not.
> 2. **Now** — the 51 citations are swept and each marked *history* or *basis*. `CHK-E2`.
>
> **Severity High.**

### 5.3 `1000fix_ERP_Module/` — the specification estate · Grade **A**

| Family | Path | Files | Grade | What it establishes |
|---|---|---:|:--:|---|
| Governance & charter | `00_Governance_and_Charter/` | 6 | **A** | `00-01` master index · `00-04` RAID · **`00-06` and `00-07` — the two repository audits that generated most of this programme's finding set** |
| Research & benchmarking | `01_Research_and_Benchmarking/` | **0** | **∅** | **The directory is empty.** `01-01`…`01-05` are cited and none exists |
| Architecture | `02_Architecture/` | 3 | **A** | `02-01` system map · `02-02` module catalogue (the `CD-` register) · `02-05` technology stack & build-vs-buy |
| Modules | `03_Modules/` | **69** | **A** | **67 `M*` specifications** in 11 category folders, plus 2 index files. The estate's densest asset |
| Portals | `04_Portals_and_Applications/` | **1** | **A** | `04-00` overview only. **The 12 `P*` files are misfiled — `AF-01`, §5.3.2** |
| Cross-cutting | `05_Cross_Cutting_Specifications/` | 6 | **A** | `05-01` feature register · `05-02` data model · `05-03` integration catalogue · `05-04` role matrix · `05-05` business rules · `05-06` NFRs. **Six files, and most of the estate's identifier spaces** |
| Delivery | `06_Delivery_and_Implementation/` | **2** | **A** | `06-01` roadmap & phasing · `06-02` KPI & benefits (**discharges `PGD-000` `BM-001`**). `06-03`…`06-06` absent |
| Reference / superseded | `99_Reference/_Superseded/` | 5 | **S** | The five v1.0 pillar files. **`GL-04`'s home** |
| **Total** | | **123** | | |

#### 5.3.1 The cited-and-absent register — `EVR-F-01`

Ten module-repository documents are cited **by identifier, in backticks** and do not exist. Counted
at 2026-08-19 19:54:

| ID | Cited | What it was to be | Recorded absent in | Superseded by |
|---|---:|---|---|---|
| `06-06` | **25** | Deployment & Operations Plan | `PGD-000` Cat 12 | ✅ **`RL-002`** — superseded, not awaited |
| `00-05` | **24** | *(unstated)* | `AF-04` | — **nothing.** 24 citations, no successor |
| `06-03` | **24** | *(delivery series)* | `DM-001` `O-01` | — |
| `06-04` | **24** | *(delivery series)* | multiple, parenthetically | — |
| `06-05` | **16** | Training & Change Plan | `PGD-000` Cat 13 | ✅ **`CH-001` + `CH-002`** |
| `02-03` | **6** | Module Boundary Rules | `PGD-000` Cat 02 | ✅ **`AR-005`** |
| `02-04` | **6** | Module Dependency Map | `PGD-000` Cat 02 | ✅ **`AR-006`** |
| `01-05` | **4** | Source & Evidence Index | `PGD-000` Cat 99 | ✅ **this document** |
| `01-01` | **3** | Research baseline | `01_Research…` empty | — |
| `01-03` | **2** | Benchmarking | *"planned"* | — |
| **Total** | **134** | | | **5 superseded · 5 open** |

> **The finding is not that ten documents are missing.** Five of the ten are *superseded* — the
> guiding-document estate wrote their replacements and said so. The finding is that **the
> information is scattered across six documents and one empty directory**, so the two facts a
> reader needs — *does it exist?* and *what replaced it?* — are available nowhere together.
>
> **`00-05`, `06-03` and `06-04` carry 72 citations between them and have no successor at all.**
> Nothing in the estate states what they were meant to contain. That is the residue, and it is
> `EVR-Q-01`.
>
> **Severity Medium**, rising to High for any of the three if a Wave 1 activity turns out to depend
> on one. Owner **Enterprise Architecture**, needed **W1**.

#### 5.3.2 `AF-01` — the twelve misfiled portal specifications

**Counted: 12 `P*` specification files in `03_Modules/K_Platform_and_Technology/`**, against **1**
file in `04_Portals_and_Applications/`. The approved structure requires the reverse.

This register does not rule on it — `AF-01` is open and is the CTO's. It records the live state and
adopts `RF-001` §4.2.4's operating instruction verbatim, because it is correct and costs nothing:

> **Cite the identifier, not the path.** A path quoted for a portal specification is wrong in one of
> the two documents whichever you choose. `P07` is unambiguous; `04_Portals_and_Applications/P07…`
> is a guess.

`EVR-03` generalises this to a rule.

### 5.4 `project_content/` — the content estate · Grade **A**

488 files in 21 numbered categories plus three underscore directories. Registered by category
because a per-file register would be `RF-002`'s, restated.

| # | Category | Files | # | Category | Files |
|---:|---|---:|---:|---|---:|
| 00 | Content Governance & Standards | 14 | 11 | Localisation & Bengali | 18 |
| 01 | Voice, Brand & Design Content | 10 | 12 | Data Migration Content | 14 |
| 02 | Master Data & Configuration | **48** | 13 | Test & Acceptance Content | 18 |
| 03 | UI Copy & Microcopy | **42** | 14 | Reporting, Analytics & KPI | 16 |
| 04 | Notification & Messaging | 26 | 15 | Integration & Developer Content | 12 |
| 05 | Document & Print Templates | **44** | 16 | Change Management & Comms | 18 |
| 06 | Process, SOP & Workflow | 34 | 17 | Operations, Support & Runbooks | 16 |
| 07 | Knowledge Base & Technical Library | 16 | 18 | Ecosystem Onboarding | 14 |
| 08 | Training & Enablement | 24 | 19 | Multimedia & Asset Specs | 12 |
| 09 | Help Centre & Self-Service | 20 | 99 | Reference & Registers | 12 |
| 10 | Legal, Policy & Compliance | 24 | | `_AUDIT/` | **22** |
| | | | | `_templates/` | 12 |
| | | | | root (index + README) | 2 |
| | | | | **Total** | **488** |

**Reconciliation:** the 21 numbered categories sum to **452**; `_AUDIT` 22, `_templates` 12, root 2
→ **488**. ✅ Independently verified against `find project_content -name '*.md' | wc -l`.

| Note | Detail |
|---|---|
| `_ARCHIVE/` | **Present and empty** — 0 files. Registered so its emptiness is a recorded fact rather than an assumption |
| `BLOG & EDUCATIONAL/` | **0 markdown files.** The only category-shaped directory in the workspace holding no registered content |
| `99_Reference_and_Registers/` | **12 files, `RF-001`…`RF-012`.** `PGD-000` Category 99 and `_CATEGORY_OVERVIEW` both describe this directory as holding **two** files — correct at 2026-08-18 01:39, stale by ten since |

> **`EVR-F-07`.** `PGD-000` Category 99's opening note says `RF-001` and `RF-002` *"were written at
> 01:27 and 01:30"* and treats the directory as holding two files. It now holds **twelve** —
> `RF-003` through `RF-012` include a content-to-requirement traceability matrix, a content decision
> log, **`RF-008` an external standards register** and `RF-012` an audit archive index. Three of
> those are the content-estate analogues of `RR-006`, `RR-002` and `RR-005`, and none of the three
> `RR` documents' first drafts knew they existed. **Severity Low** for correctness, **Medium** for
> duplicated effort. `RR-005` `CUR-Q-06` and `RR-006` §8 carry the reconciliation.

### 5.5 The content estate's own index — adopted, not restated

`RF-002` is grade **A** and is the authority for the content estate's sources. This register adds
one thing to it: a **precedence rule**, because two source indexes now exist in one workspace.

| Question | Rule |
|---|---|
| A source cited only by content documents | `RF-002` governs |
| A source cited only by guiding documents | **This register** governs |
| A source cited by both | **This register** for the engineering claim; `RF-002` for the content claim. They must not disagree |
| They disagree | The disagreement **is** the finding. `CHK-E4` compares them mechanically |
| Tested at this issue? | **No.** `RF-002` read for method, not row-by-row. `EVR-Q-03` |

### 5.6 `project-guide-doc/` — this repository · Grade **P**

| Family | Files | Grade | Note |
|---|---:|:--:|---|
| Guiding documents `CODE-nnn_*.md` | **133** | **P** | 16 codes. All 130 with front matter carry all 18 mandatory keys (`RR-003` §8.2) |
| Category overviews `_CATEGORY_OVERVIEW.md` | **17** | **P** | One per category. **Grade P and drifting** — §5.6.1 |
| Audit reports `_AUDIT/` | **14** | **A** | Two identifier conventions; `RR-002` `RR-002-D-05` rules |
| Template `_templates/` | 1 | **A** | `TPL_Guiding_Document.md`; governed by `RR-003` §7 |
| Register `PGD-000` | 1 | **A** | The estate's spine |
| Structure & readme | 2 | **D** | `FOLDER_STRUCTURE.md`, `README.md` — **derived, and derived documents go stale first** |
| Artefact directories | 11 non-`.md` | **A** | `IN-002_artefacts/`, `IN-003_artefacts/` |
| **Total** | **171** `.md` / **182** all | | |

**Per-code guiding document counts, on disk at 2026-08-19 19:54:**

| Code | On disk | Registered in `PGD-000` | Code | On disk | Registered |
|---|---:|---:|---|---:|---:|
| `GV` | 11 | 11 | `MG` | 7 | 7 |
| `RQ` | 10 | 10 | `PE` | 9 | 9 |
| `AR` | 13 | 13 | `SV` | **6** | 6 |
| `DA` | 9 | 9 | `RL` | 6 | 6 |
| `IN` | 8 | 8 | `CH` | 5 | 5 |
| `SC` | 11 | 11 | `CO` | **5** | 6 |
| `UX` | 8 | 8 | `BM` | **0** | 5 |
| `BE` | 9 | 9 | `RR` | **4** | 6 |
| `QA` | 11 | 11 | **Total** | **133** | **140** |

> **`PGD-000` §0.5 records 119 authored. The filesystem holds 133**, of which `CO-001` and `BM-001`
> are additionally discharged by files in other repositories — so **135 of 140 register rows have a
> file behind them**. The five with nothing are `BM-002`, `BM-003`, `BM-004`, `BM-005` and
> `CO-006`… and `CO-006` was written at 02:57 today, making it **four**. §6 explains why any figure
> in this paragraph is provisional.

#### 5.6.1 The category overviews are grade **P** and three are measurably stale

`_CATEGORY_OVERVIEW.md` files were written on 2026-08-18 as the categories were registered, and
most have not been revised since their category was authored.

| Overview | Written | Its category authored | Still says |
|---|---|---|---|
| `99_.../\_CATEGORY_OVERVIEW.md` | 2026-08-18 01:42 | 2026-08-19 02:53–19:54 | *"**0 written** · 2 partially covered · 4 absent"* — **six documents later** |
| `14_.../\_CATEGORY_OVERVIEW.md` | 2026-08-18 01:40 | 2026-08-19 02:44–02:57 | pre-authoring status |
| `15_.../\_CATEGORY_OVERVIEW.md` | 2026-08-18 01:40 | not authored | accurate |

**This is not a defect in the overviews; it is the roll-up problem.** A figure that appears in more
than one place must be regenerated in every place — `PG-M10` — and an overview is by construction
a second place. `RR-006` §5's generated index is the durable fix; until then `EVR-07` makes the
overview a gate-review item. **Severity Low.** Recorded as `EVR-F-08`.

#### 5.6.2 The eight dangling `PGD` identifiers, and the one that is a phantom

| ID | Status | Assessment |
|---|---|---|
| `CO-001` | Discharged by `primary-doc/…RFP.md` | ✅ Not a defect — a register modelling gap, `EVR-F-05` |
| `BM-001` | Discharged by `06-02` | ✅ Same |
| `BM-004`, `BM-005` | Registered, unwritten | ✅ Correctly ⬜/◐ in `PGD-000` |
| `RR-004`, `RR-005`, `RR-006` | Registered, being written at this issue | ✅ Resolved by this document and its two siblings |
| **`RR-008`** | **Not registered anywhere. Cited 7 times** | ⛔ **`EVR-F-05b` — a phantom identifier** |

> ### `RR-008` does not exist and never did
>
> `UX-005` cites `RR-008` **six** times and `UX-007` once — as *"the standards currency review"*,
> *"each `RR-008` cycle"*, and in `UX-005`'s traceability table as a lateral dependency. Category
> 99 registers `RR-001`…`RR-006`. **There is no `RR-007` and no `RR-008`.**
>
> The intent is unmistakable: `RR-008` means **`RR-005`**, the Standards & Regulatory Currency
> Register. An author needing a currency register invented a plausible identifier rather than
> looking one up — which is `RR-002` `IDC-03` (register-first) breached, and it is the first
> instance found *inside* this repository by a mechanical sweep rather than by reading.
>
> **Remediation.** Seven citations in two files change `RR-008` → `RR-005`. Owner **Enterprise
> Architecture**, **Now**. It is a five-minute fix, and the reason it matters is that
> `UX-005` `ACD-10` and `ACD-34` are **governing rules** that schedule work against a document that
> does not exist — so the rules are, as written, unexecutable. **Severity Medium.**

### 5.7 Path and reference integrity — measured

#### 5.7.1 Markdown links

**942 links of the form `[text](path.md)` were resolved relative to their citing file. 942
resolved. 0 broken.**

For an estate with no link checker, no build step and no version control, that is a genuinely
strong result and the credit belongs to the template's closing instruction — *"verify every path
resolves before issuing."*

#### 5.7.2 Backtick relative paths

**1,204 paths of the form `` `../…md` `` were checked. 1,191 resolved. 13 did not:**

| Broken target | Count | Assessment |
|---|---:|---|
| `./RR-006_Master_Cross_Reference_and_Traceability_Index.md` | 3 | Forward reference — resolves at this issue |
| `./RR-005_Standards_and_Regulatory_Currency_Register.md` | 2 | Forward reference — resolves at this issue |
| `./RR-004_Source_Document_Index_and_Evidence_Register.md` | 2 | Forward reference — **this document** |
| `./BM-004_Benefits_Realisation_Plan.md` | 2 | Correctly-registered, unwritten **at 19:54 — written at 19:59.** See the correction below |
| `./BM-005_Lessons_Learned_and_Continuous_Improvement_Register.md` | 2 | Correctly-registered, unwritten **at 19:54 — written at 20:07.** See the correction below |
| **`../../1000fix_ERP_Module/03_Modules/G_Platform_and_Technology/M66_…`** | **2** | ⛔ **Genuine error** |

#### Post-issue correction — applied 2026-08-19 20:22 by `PGD-AUDIT-CAT-99`

Four of the thirteen rows above changed state within twenty-eight minutes of this document's
enumeration, and the corrections are recorded here rather than by editing the table, so the
movement stays visible:

| Row | State at 19:54 | State at 20:22 | Cause |
|---|---|---|---|
| `./RR-004…`, `./RR-005…`, `./RR-006…` | Forward references, unresolvable | ✅ **Resolved** | All three written |
| `./BM-004_Benefits_Realisation_Plan.md` | Registered, unwritten | ✅ **Resolved** — written **19:59** | Category 15 authored concurrently |
| `./BM-005_Lessons_Learned…md` | Registered, unwritten | ✅ **Resolved** — written **20:07** | As above |
| `…/G_Platform_and_Technology/M66_…` | ⛔ Genuine error | ✅ **Corrected** — `G_` → `K_` in `RL-001` and `RL-005` | `PGD-AUDIT-CAT-99` `A99-C-01` |

**Category 15 is now complete on disk** — `BM-002`, `BM-003`, `BM-004`, `BM-005` all exist, and
`BM-001` is discharged by `06-02`. §5.6's per-code table records `BM` as **0** and is wrong by four
as of 20:22. **This is `EVR-05` demonstrating itself**: the claim was true when written, false when
read, and survivable only because it carried the instant inside the sentence.

> ### `EVR-F-02` — two references point at a directory that does not exist
>
> `RL-001` and `RL-005` each cite:
>
> ```
> ../../1000fix_ERP_Module/03_Modules/G_Platform_and_Technology/M66_Internal_IT_Service_Management.md
> ```
>
> `M66` is in **`K_Platform_and_Technology/`**. `G_` is `G_Finance_and_Treasury`. The path is wrong
> by one letter and resolves to nothing.
>
> `M66` is not a peripheral citation in those two documents: `RL-001` §8.2 rules the contradiction
> where *"`M66` §4 rejects the CAB that `SP-031` §3 requires"* — a governing ruling, resting on a
> reference a reader cannot follow.
>
> **This is the highest-value two-line fix in the estate**, and it is `EVR-03`'s justification: had
> both documents cited `M66` and not a path, neither would be broken. Owner **Enterprise
> Architecture**, **Now**. **Severity Low** for content, **Medium** for the precedent — 11 of the
> 13 broken paths are benign, which is exactly how the two that are not stayed invisible.

#### 5.7.3 Future-dated verification — `RF-002` `EV-F1` re-run

`RF-002` §4.7 found **sixty-eight** content files carrying a `verified_on` later than their own
modification date. The same test, run against all 130 front-matter-bearing guiding documents:

**0 of 130.** ✅ No engineering document claims to have verified a citation in the future.

> The engineering estate passes a test the content estate failed 68 times, and the reason is worth
> recording rather than celebrating: **these documents are one day old.** The test discriminates
> against age, not against carelessness. `RR-005` `CUR-F-08` makes the same point from the other
> side — 130 documents, two distinct verification dates, no re-verification cycle. **The correct
> reading of this ✅ is "not yet applicable", and `CHK-E3` keeps it running.**

---

## 6. The Baseline Movement Record

`EVR-05`. Twelve movements are now on record. Kept here as a table because a movement recorded in
each document's revision note is a movement nobody can count.

| # | Instant | `project-guide-doc` `.md` | Workspace `.md` | What moved | Recorded as |
|---:|---|---:|---:|---|---|
| 1 | 2026-08-18 01:16 | — | 595 | `project_content` 462 | `PGD-A1-03` |
| 2 | 2026-08-18 01:39 | — | 601 | `project_content` 468; `RF-001`, `RF-002` appear | `PGD-A1-03` |
| 3 | 2026-08-18 02:06 | — | 610 | `project_content` 477 | `AP-17` |
| 4 | 2026-08-19 02:10 | 151 | 772 | Category 13 authoring window | `CHA-12` |
| 5 | 2026-08-19 02:25 | 156 | 777 | `SV-002`, `SV-003`, `RL-001`…`RL-003`, `CO-005` | `RLA-24` |
| 6 | 2026-08-19 02:29 | 157 | 778 | — | `RR-002` §4.3 |
| 7 | 2026-08-19 02:39 | 160 | 781 | `SV-004`, `CO-002`, `PGD-AUDIT-CAT-12` | `RR-002` §4.3 |
| 8 | 2026-08-19 02:41 | 161 | 782 | `SV-005` | `PGD-000` §3 |
| 9 | 2026-08-19 02:52 | 164 | 785 | `CO-004` | **this document** |
| 10 | 2026-08-19 02:57 | 166 | 790 | `SV-001`…`SV-006` complete; `CO-006` | **this document** |
| 11 | 2026-08-19 03:08 | 168 | 787→792 | **`RR-001`, `RR-002`, `RR-003` authored** | **this document** |
| 12 | 2026-08-19 **19:54** | **171** | **792** | This document and its two siblings | **this document** |

**Twelve movements. Sixteen hours. +197 workspace files since the first enumeration.**

> ### What the record actually shows
>
> Read as a series rather than as twelve incidents, three things are visible that no single
> movement showed:
>
> 1. **Movements cluster in authoring windows, not across the day.** Movements 4–11 span
>    **58 minutes**. Nothing moved between 03:08 and 19:54. The hazard is not "the estate changes";
>    it is *"the estate changes while you are counting it"*, which is a narrower and more tractable
>    problem.
> 2. **Every published absence claim in this repository has a half-life measured in minutes**, and
>    seven have already been falsified (`CHA-12`). `EVR-05`'s remedy — put the *instant* inside the
>    sentence — costs nothing and is the only thing that makes such a claim survivable.
> 3. **`RG-08` has now been recommended at least eleven times and ratified zero.** This document
>    does not recommend it a twelfth time. It applies it, as `RR-002` `RR-002-D-07` did, and
>    records the count so the gap between recommendation and ratification stays legible.

---

## 7. The Reverse Index

`EVR-06`. For each source family: what re-opens if it changes. Document-grain deliberately —
identifier-grain is `RR-006`'s.

| If this changes… | …these re-open | Trigger class |
|---|---|---|
| `primary-doc/` **BRD** §6.5 (source withdrawal at W2) | `MG-001`, `MG-002`, `RL-006`, `DM-002` — **the only irreversible deadline in the programme** | **Immediate** |
| `primary-doc/` **BRD** §19 (cost-benefit) | `BM-003`, `CO-005`, `GV-008` | Gate |
| `primary-doc/` **RFP** §4.3, §17 | `CO-002`, `CO-003`, `RL-006` §'s contractual reconciliation | **Immediate** — contractual |
| `primary-doc/` **Technology Stack** | `AR-013`, `PE-001`…`PE-005`, `BE-001`, `BE-002`, `CO-004` | Gate |
| `02-02` module catalogue (`CD-` register) | `BE-005`, `AR-006`, `RQ-003`, and every build ticket | **Immediate** |
| `05-01` feature register | `RQ-001`, `RQ-004`, `QA-011` — **the traceability denominator** | **Immediate** |
| `05-02` data model | `DA-001`, `DA-002`, `AR-008`, `MG-003` | Gate |
| `05-03` integration catalogue | `IN-001`…`IN-008`, `AR-009` | Gate |
| `05-04` role & permission matrix | `SC-004`, `UX-002`, `CH-002`'s learner counts, `RL-004`'s rollout rate | **Immediate** |
| `05-05` business rules | `RQ-009`, `AR-005` | Gate |
| `05-06` NFRs | `RQ-006`, `AR-001`, `AR-012`, `PE-006`, `QA-006` | Gate |
| `06-01` roadmap & phasing | `GV-004`, `RL-004`, `CH-002`, `CH-003` — **the wave calendar** | **Immediate** |
| `06-02` KPI & benefits | `BM-001`…`BM-004`, `CH-004`, `RL-005` | Gate |
| `00-04` RAID | `GV-005`, and every risk treatment in `CH-001` and `CH-005` | Gate |
| `00-06` / `00-07` audits | Every `PGD` document's §2.3 findings-closed table | Gate |
| `project_content/` **`OP-*`** (17) | `SV-001`…`SV-006` | Gate |
| `project_content/` **`TR-*`** (24) | `CH-002`'s 12,306–21,759 learner-hours | Gate |
| `project_content/` **`DM-*`** (14) | `MG-001`…`MG-007`, `RL-006` | Gate |
| `project_content/` **`LG-*`** (24) | `SC-003`, `SC-008`, `DA-005`, `DA-006` | **Immediate** — statutory |
| `project_content/99_.../RF-001`, `RF-002`, `RF-008` | `RR-001`, this document, `RR-005` | Gate |
| `PGD-000` | **Every document in this repository** | **Immediate** |
| `_templates/TPL_Guiding_Document.md` | `RR-003`, and every future document | Gate |

**Trigger classes.** *Immediate* = the dependent must be re-opened before the next work item that
uses it. *Gate* = re-opened at the next wave gate.

> **Twenty-two rows, of which eight are Immediate.** The eight are the estate's true couplings, and
> six of them run through six files: `02-02`, `05-01`, `05-04`, `06-01`, `00-04` and `PGD-000`. **A
> change-control process that watched only those six would catch most of the impact in a 792-file
> estate**, which is a more useful statement than "control everything" and is the reason this
> section is coarse on purpose.

---

## 8. Findings

| # | Finding | Severity | New? | Owner | Needed by |
|---|---|:--:|:--:|---|---|
| `EVR-F-01` | **Ten module-repository documents are cited 134 times and do not exist.** Five are superseded and say so; **`00-05`, `06-03` and `06-04` carry 72 citations and have no successor**. The set is recorded nowhere together | Medium | Partly — `AF-04` | Enterprise Architecture | **W1** |
| `EVR-F-02` | **`RL-001` and `RL-005` cite `G_Platform_and_Technology/M66…`; the directory is `K_`.** A governing ruling rests on an unresolvable path | Medium | **New** | Enterprise Architecture | **Now** |
| `EVR-F-03` | **A superseded baseline (`old-primary-doc/`) is cited 51 times in 24 live documents**, and two of its six files have no v2.0 successor and are relied on as current | **High** | **New** | Enterprise Architecture | **W1** |
| `EVR-F-04` | **Two business-objective sets coexist with confusable identifiers** — `BO-1`…`BO-9` in the superseded RFP, `BO-01`…`BO-18` in the current BRD and `06-02`. They denote **different objectives**. `BO-1` ≠ `BO-01` | **High** | **New** | Enterprise Architecture | **W1** |
| `EVR-F-05` | **A register row discharged by a file in another repository reads as dangling to any mechanical sweep** — `CO-001`, `BM-001`. `PGD-000` has no `discharged_by` field | Low | **New** | PMO | `G1` |
| `EVR-F-05b` | **`RR-008` is a phantom identifier**, cited 7 times in `UX-005` and `UX-007`, never registered. Two governing rules schedule work against it | Medium | **New** | Enterprise Architecture | **Now** |
| `EVR-F-06` | **The workspace has no version control.** No diff, no attribution, no rollback; ISO 15489-1 *integrity* is not met, and twelve baseline movements are recorded as prose rather than as commits | **High** | **New** | **CTO** | **Now** |
| `EVR-F-07` | **`project_content/99_Reference_and_Registers/` holds twelve files, not two.** `RF-003`…`RF-012` include the content analogues of `RR-002`, `RR-005` and `RR-006`, and none of the three `RR` documents knew | Medium | **New** | Enterprise Architecture | `G2` |
| `EVR-F-08` | **Three category overviews are measurably stale**, including Category 99's, which reads *"0 written"* after six documents | Low | **New** | PMO | `G1` |
| `EVR-F-09` | **`CHK-E1` cannot distinguish *use* from *mention*** — it fires on paths inside fenced code and inside this register's own table of broken references. Third instance of the class in one afternoon, with `RR-006` §5.4.4 and `RR-005` §4.1 | Low | **New** | Enterprise Architecture | `G1` — **refinement applied at issue**, §10 |

### 8.1 `EVR-F-04` in full — the two objective sets

**What was found.** The token `BO-` resolves to **27** distinct identifiers workspace-wide, in two
incompatible digit forms:

| Form | Range | Home | Grade |
|---|---|---|:--:|
| `BO-1` … `BO-9` | 9 identifiers | `old-primary-doc/…RFP.md` | **S** |
| `BO-01` … `BO-18` | 18 identifiers | `primary-doc/…BRD.md`, `1000fix_ERP_Module/06-02` | **A** |

**They are not the same objectives re-numbered.**

| Identifier | Denotes |
|---|---|
| `BO-1` | *"Operational Unification"* |
| `BO-01` | *"Automate the end-to-end service order lifecycle to eliminate manual coordination"* — target 20% → 70%, owner Service Ops Director |

**Why it matters.** `06-02` is the KPI and benefits document; **its objectives are what the
BDT 876 lac benefit case is claimed against.** A benefit traced to `BO-1` and a benefit traced to
`BO-01` are traced to different things, and the two forms differ by one leading zero. This is
`RR-002` `IDC-14` — *"where two spaces share a lexical form, the digit count disambiguates and is
mandatory"* — with the digit count doing the disambiguating and nobody told.

**Remediation.** `BO-1`…`BO-9` are **retired in place** per `IDC-05`/`IDC-06`: the rows stay,
marked retired, in a `RR-006` retirement table, so a reader meeting `BO-1` in the superseded RFP
can resolve it and learn that it does not map to `BO-01`. Owner **Enterprise Architecture**, **W1**.
`BM-003` and `BM-004` are the consumers.

---

## 9. Review and Re-enumeration

`EVR-07`. Two triggers, because this register has two failure modes.

| Trigger | Scope | Owner |
|---|---|---|
| **Every wave gate** (`GV-009` `G1`…`G4`) | Full re-enumeration: §4.2 counts, §5.3.1 absent register, §5.7 path integrity, §6 gains a row | PMO |
| **Any baseline movement of ≥5 files** in any repository | §4.2 and §6 only — a cheap partial re-count, ten minutes | Whoever noticed |
| **Before any document publishes an absence claim** | The specific claim, timestamped inside the sentence per `EVR-05` | The author |

**Effort, counted rather than guessed.** The §4.1 commands complete in **under a minute** on this
estate. A full gate re-enumeration including judgement is **half a person-day**. Against
`EVR-F-01`'s 134 citations of absent sources, that is the cheapest control in this register — and
it is the same conclusion `RR-005` §9 reached independently about its own.

---

## 10. Enforcement

Numbered `CHK-E*` so as not to collide with `RR-002` §10's `CHK-01`…`06` or `RR-005` §10's
`CHK-C1`…`C6`.

| # | Check | Detects | Gate |
|---|---|---|---|
| `CHK-E1` | **Reference resolution** — every markdown link and backtick relative path resolves, or its target is in §5.3.1. **Skips fenced code blocks and the register documents' own evidence tables** — see the note below | `EVR-F-02`, `EVR-01` | Warn at commit, **fail at gate** |
| `CHK-E2` | **Superseded-source citation** — any citation of `old-primary-doc/` or `99_Reference/_Superseded/` not marked *history* | `EVR-F-03`, `EVR-02` | Warn |
| `CHK-E3` | **Future verification date** — `verified_on` later than the file's modification date | `RF-002` `EV-F1` | **Fail** |
| `CHK-E4` | **Index divergence** — a source graded differently here and in `RF-002` | `EVR-Q-03` | Warn |
| `CHK-E5` | **Phantom identifier** — a `PGD` ID cited that is neither on disk nor a `PGD-000` register row | `EVR-F-05b` | **Fail** |
| `CHK-E6` | **Enumeration freshness** — this register's `enumeration_timestamp` older than the last baseline movement | `EVR-07` | Warn |

```bash
# CHK-E1 — reference resolution. Run from project-guide-doc/.
find . -name '*.md' | while read -r f; do d=$(dirname "$f")
  grep -oE '\]\([^)#][^)]*\.md[^)]*\)' "$f" | sed 's/^](//;s/)$//;s/#.*//' \
    | while read -r l; do [ -e "$d/$l" ] || echo "BROKEN $f -> $l"; done
  grep -oE '`\.\.?/[^`]+\.md`' "$f" | tr -d '`' \
    | while read -r l; do [ -e "$d/$l" ] || echo "BROKEN $f -> $l"; done
done

# CHK-E5 — phantom PGD identifiers. Finds RR-008 in one pass.
comm -13 \
  <(find . -name '*.md' | grep -oE '/[A-Z]{2}-[0-9]{3}' | tr -d '/' | sort -u) \
  <(grep -rhoE '\b(GV|RQ|AR|DA|IN|SC|UX|BE|QA|MG|PE|SV|RL|CH|CO|BM|RR)-[0-9]{3}\b' \
      --include='*.md' . | sort -u)

# CHK-E3 — future verification dates. RF-002 EV-F1's method, engineering estate.
for f in $(find . -name '*.md'); do
  v=$(sed -n 's/^verified_on: *//p' "$f" | head -1); m=$(date -r "$f" +%F)
  [ -n "$v" ] && [ "$v" \> "$m" ] && echo "FUTURE $v > $m  $f"
done
```

> ### `CHK-E1` refinement, forced by running it against this document — `EVR-F-09`
>
> Re-run at **20:22** after the `G_`→`K_` correction, `CHK-E1` returned **three residual hits, all
> of them inside this document and all false positives**:
>
> | Hit | Why it fired | Why it is not a defect |
> |---|---|---|
> | `path.md` | Appears in §4.1's **fenced bash example**, `[text](path.md)` | The checker does not skip fenced code |
> | `./BM-004_…`, `./BM-005_…` | Appear in §5.7.2's **table of broken targets found in other files** | A register that reports broken references necessarily contains them as data |
>
> **Both are the same defect class as `RR-006` §5.4.4's `RR-007` artefact**: a text-scanning check
> cannot distinguish *use* from *mention*. Three instances of that class were found across the four
> registers in one afternoon, which is enough to make it a rule rather than a footnote.
>
> **The refinement, applied to `CHK-E1` above:** skip content inside ``` fences, and exclude
> `RR-002`, `RR-004`, `RR-005` and `RR-006` from the *resolution* sweep while keeping them in the
> *allocation* sweep. The exclusion is declared, not silent — `RR-006` `RR-006-D-04` sets the
> precedent and the reason: **silent suppression is how an index starts lying.**
>
> **`CHK-E1` after the refinement returns zero.** **Severity Low** — a checker defect, not an estate
> defect, and it cost one re-run to find.

> **`CHK-E1` and `CHK-E5` were both run to produce this document**, and between them they found
> `EVR-F-02` and `EVR-F-05b` — two defects that had survived fourteen category audits. Neither
> takes a minute. **That is the argument for automation over diligence**: the audits were not
> careless, they were reading, and these two defects are invisible to reading.

---

## 11. Decisions Recorded

`DL-06` / `RR-002` `IDC-07`: identifiers take the form `RR-004-D-nn`.

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `RR-004-D-01` | Grain of the register | (a) per file, 792 rows; (b) per family, with per-file rows only where a file is individually load-bearing | **(b)** | A 792-row table is a directory listing with extra steps, and would be stale before it was read. `primary-doc`'s four files are individually registered because 94 documents depend on them; `project_content`'s 488 are registered by category because `RF-002` already holds them individually | §5; `RF-002` retains per-file authority for the content estate |
| `RR-004-D-02` | Relationship to `RF-002` | (a) supersede; (b) restate; (c) reference with a precedence rule | **(c)** | Restating creates a second copy that goes stale independently — the defect `RR-006` exists to prevent. Superseding a good, current, content-owned index would be an act of scope theft | §5.5's four-row precedence table; `CHK-E4` |
| `RR-004-D-03` | The `old-primary-doc` implementation strategy | (a) grade **S** and forbid citation; (b) grade **S**/**A** and state the ambiguity; (c) grade **A** | **(b)** | It is the only implementation-strategy document in the workspace. Grading it S and forbidding citation would leave a live question with no answerable source; grading it A would launder a v1.0 assumption into v2.0 | `EVR-F-03`; re-baselining assigned to `AR-002`/`GV-004` at W1 |
| `RR-004-D-04` | `BO-1`…`BO-9` | (a) re-map to `BO-01`…; (b) **retire in place**; (c) ignore, the source is superseded | **(b)** | They denote different objectives, so a mapping would be a fiction. Ignoring them fails because 27 identifiers resolve and a reader cannot tell which set they are in | `EVR-F-04`; retirement table in `RR-006` |
| `RR-004-D-05` | Whether to fix `EVR-F-02` and `EVR-F-05b` in this document's own act | (a) fix them; (b) record and assign | **(b)** at issue, **(a)** at audit | `IDC-01`: a register may not edit the documents it registers, or it becomes their author and its independence goes. **The audit that follows this issue is the right instrument**, and it carries the fix | Both are Now-dated with a named owner; the audit applies them |
| `RR-004-D-06` | Version control | (a) note it as a risk; (b) **raise it as a High finding with the CTO named** | **(b)** | Every evidence claim in three registers rests on filesystem integrity that nothing guarantees. Twelve baseline movements make it concrete rather than theoretical | `EVR-F-06`; `GV-005` RAID at issue |

---

## 12. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `EVR-Q-01` | What were `00-05`, `06-03` and `06-04` to contain? **72 citations, no successor, no statement of intent anywhere** | Enterprise Architecture | **W1** | `EVR-F-01` closure; any W1 activity that turns out to depend on one |
| `EVR-Q-02` | Is `old-primary-doc/…Implementation_Strategy_Odoo19CE…` re-baselined as current, or restated at v2.0? | **CTO** | **W1** | `EVR-F-03`; `AR-002`; `PE-002` |
| `EVR-Q-03` | Row-by-row reconciliation of this register against `RF-002`, and of `RR-005` against `RF-008` — who runs it, and when? | Enterprise Architecture / Programme Content Lead | `G2` | `EVR-F-07`; `CHK-E4` |
| `EVR-Q-04` | **Will the workspace be placed under version control, and where?** | **CTO** | **Now** | `EVR-F-06`; every integrity claim in `RR-002`, `RR-004`, `RR-005`, `RR-006` |
| `EVR-Q-05` | Does `PGD-000` gain a `discharged_by` field so that `CO-001` and `BM-001` stop reading as dangling? | PMO | `G1` | `EVR-F-05`; `CHK-E5`'s false-positive rate |
| `EVR-Q-06` | Who owns re-enumeration between gates — the mover, or the PMO? Assumed *"whoever noticed"* in §9, which is not an owner | PMO | `G1` | `EVR-07` |
| `EVR-Q-07` | Which body ratifies `EVR-01`…`EVR-07`? `PGD-A1-09` records that none exists | **Board** | **Now** | Every ✅ in this estate (`PGD-A2-25`) |

> Seven questions, seven named owners, seven dates. **`EVR-Q-04` and `EVR-Q-07` are escalated to
> `GV-005` RAID at issue**, and `EVR-Q-04` is the one that would, if answered, retire four findings
> across three registers at once.

---

## 13. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | Every repository in the workspace is registered with a counted file total, byte total and grade | 5 of 5; §4.2; **met at issue** |
| `AC-02` | Every source family carries a grade per §3.2 and a role statement | §5.1–§5.6; **met at issue** |
| `AC-03` | The cited-and-absent population is enumerated with citation counts and successor status | 10 of 10, 134 citations; §5.3.1; **met at issue** |
| `AC-04` | Reference integrity is measured, not asserted | 942 links + 1,204 paths checked; §5.7; **met at issue** |
| `AC-05` | `RF-002`'s `EV-F1` test is re-run against the engineering estate | 0 of 130; §5.7.3; **met at issue** |
| `AC-06` | A reverse index exists for every source family, with a trigger class | 22 rows; §7; **met at issue** |
| `AC-07` | Every figure carries the enumeration timestamp and a reproducible command | §4.1; **met at issue** |
| `AC-08` | This document's rule prefix was collision-checked before allocation per `RR-002` `IDC-08` | `rule_prefix:` front matter, 792-file denominator and timestamp; **met at issue** |
| `AC-09` | Every finding carries a severity, an owner and a date | 9 of 9; §8; **met at issue** |
| `AC-10` | The register is reconciled row-by-row with `RF-002` | **Not met.** `RF-002` read for method only. `EVR-Q-03`. Stated rather than claimed, per `PG-M2` |
| `AC-11` | Per-file registration for `project_content` | **Deliberately not met** — `RR-004-D-01`. The 488 files are registered by category; `RF-002` holds them individually |

**Definition of done.** Complete when every criterion above is met, `PGD-000`'s `RR-004` row is
updated with a fresh enumeration timestamp, and the approver has signed. **`AC-10` and `AC-11`
carry residual or deliberately-declined work and are stated as such**, because a completeness claim
this register cannot support is the one thing an evidence register must never make.

---

## 14. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `PGD-000` | Registers this document; §4.2 measures its §3 counts as stale by ten |
| Upstream | `RF-002` | The content estate's index. Method adopted, rows referenced, not restated |
| Upstream | `RR-002` §5, §7.2 | Identifier forms; the `rule_prefix:` procedure |
| Upstream | `RR-003` §6.2 | The front-matter schema whose `traces_to:`/`depends_on:` keys this register reads |
| Downstream | `RR-006` | **The mechanical form of §7.** The reverse index is document-grain; `RR-006` makes it identifier-grain and generates it |
| Downstream | `RR-005` | Receives `EVR-F-07`'s `RF-008` overlap, and shares `EVR-Q-03` |
| Downstream | `GV-011` | Configuration management — receives `EVR-F-06`, the version-control finding |
| Downstream | `GV-005` | Receives `EVR-Q-04` and `EVR-Q-07` as RAID entries |
| Downstream | `RL-001`, `RL-005` | Receive `EVR-F-02` — the `G_`/`K_` path correction |
| Downstream | `UX-005`, `UX-007` | Receive `EVR-F-05b` — `RR-008` → `RR-005` |
| Downstream | `AR-002`, `GV-004` | Receive `EVR-Q-02` — the implementation-strategy re-baseline |
| Downstream | `BM-003`, `BM-004` | Receive `EVR-F-04` — the two objective sets |
| Downstream | Every `PGD` document | §7's reverse index is the change-impact instrument |
| Lateral | `../../1000fix_ERP_Module/00_Governance_and_Charter/00-01_*.md` §4 | The evidence table this register replaces for the engineering estate |
| Lateral | `../../project_content/99_Reference_and_Registers/RF-002_*.md` | Peer index; precedence in §5.5 |

---

## 15. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` ·
`./_CATEGORY_OVERVIEW.md` · `./RR-001_Glossary_and_Acronym_Register.md` ·
`./RR-002_Identifier_Convention_Standard.md` ·
`./RR-003_Document_Standards_and_Template_Library.md` ·
`./RR-005_Standards_and_Regulatory_Currency_Register.md` ·
`./RR-006_Master_Cross_Reference_and_Traceability_Index.md` ·
`../_templates/TPL_Guiding_Document.md` ·
`../00_Programme_Governance_and_Control/GV-005_RAID_Register.md` ·
`../00_Programme_Governance_and_Control/GV-011_Documentation_Control_and_Configuration_Management_Plan.md` ·
`../12_Release_Deployment_and_Transition/RL-001_Release_Management_and_Versioning_Policy.md` ·
`../06_Experience_and_Interface_Design/UX-005_Accessibility_Conformance_Design_WCAG_2_2_AA.md`

**Workspace**
`../../primary-doc/` *(4 files)* · `../../old-primary-doc/` *(6 files)* ·
`../../1000fix_ERP_Module/00_Governance_and_Charter/00-01_Master_Index_and_Document_Map.md` ·
`../../1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M66_Internal_IT_Service_Management.md` ·
`../../project_content/99_Reference_and_Registers/RF-002_Source_Document_and_Evidence_Index.md` ·
`../../project_content/99_Reference_and_Registers/RF-008_External_Standards_and_Regulatory_Reference_Register.md`

**External standards**
ISO 19011:2018 · ISO 15489-1:2016 · ISO 10007:2017 · ISO/IEC/IEEE 15289:2019 ·
ISO/IEC 11179-6:2023 — **currency of each verified in `RR-005` §5, not restated here**, per the
boundary in §1.1.

---

## 16. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-19 | Enterprise Architecture | Initial issue. Five repositories and 792 files registered by family with evidence grades; 10 cited-and-absent sources enumerated with 134 citations; 942 links and 1,204 paths checked; a 22-row reverse index; 9 findings, 3 High, 7 new; 6 decisions; 7 open questions; 6 checks; and the twelve-movement baseline record. Supersedes `01-05` and `99-04`, both unwritten | *(unsigned — no constituted body, `PGD-A1-09`)* |

---

*`RR-004` · Category 99 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
*1000FiX Services Limited · ERP Programme · Enterprise Architecture*
