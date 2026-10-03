---
id: RR-002
title: Identifier Convention Standard
category: 99 — Reference, Registers & Glossary
code: RR
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-19
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Enterprise Architecture
approver: Chief Technology Officer
standards_basis: ISO/IEC 11179-1:2023 · ISO/IEC 11179-5:2015 · ISO/IEC 11179-6:2023 · ISO 10007:2017 §5.3 · ISO 704:2022
traces_to: PGD-000 §2.1 row 21 · GV-011 §4.3, §4.4 · 00-06 C-02, C-03, H-03, H-04 · 00-07 H2-04, H2-06, H2-07 · AUDIT-016 AP-02 · AUDIT-015 RP-01 · AUDIT-018 EO-02 · RF-001 §4.2, §4.3 GL-01…GL-04 · PGD-A1-01, PGD-A2-03, PGD-A2-17, PGD-A2-19 · CHA-12 · MGA-15
depends_on: PGD-000 · GV-003 · GV-011 · RR-003
verified_on: 2026-08-19
priority: P0
needed_by: Now
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
enumeration_timestamp: 2026-08-19 02:41 (+06)
rule_prefix: IDC — verified to return zero occurrences in identifier form across all 782 markdown files of the workspace before allocation, at 2026-08-19 02:41 (+06). Candidates IDR, IDN and IDS were also free; IDC was chosen as the least likely to be read as an existing content code
---

# RR-002 — Identifier Convention Standard
# 1000FiX ERP System & Portal Suite v2.0

### Category 99 · Code `RR` · ISO/IEC 11179-1:2023 · ISO/IEC 11179-5:2015 · ISO/IEC 11179-6:2023

---

> **Before writing, read this.**
>
> 1. **`PG-01` Register-first.** This document's row exists in `PGD-000` Category 99 as `RR-002`,
>    status ⛔, priority **P0**, needed by **Now**. It was registered before it was written.
> 2. **`PG-03` / `RG-06` Count, do not consult.** Every figure below was counted from the
>    filesystem at **2026-08-19 02:41 (+06)** by the commands printed in §4.1. Where a figure
>    disagrees with a register, the register is cited and the disagreement is stated, not smoothed.
> 3. **`PG-06` Cite standards.** ISO/IEC 11179 Parts 1, 5 and 6 govern. Departures are declared in
>    §2.1.
> 4. **`PG-M4` Verify citations.** `verified_on: 2026-08-19`.

---

## 1. Purpose

This document is the single standard for **every identifier used anywhere in the 1000FiX ERP
programme**. It states, for each identifier space: what the identifier looks like, what it
denotes, who is allowed to allocate a new one, whether it may ever be reused, and what happens
when it is retired. Until this document exists, an identifier in this estate is a string that
looks authoritative and resolves to nothing in particular — and eight audit findings across five
audit reports are the same failure repeated.

The programme cannot open a build backlog without it. A sprint ticket that says *"implement
`CD-034`"* is not actionable while two registers hold different meanings for `CD-034`; a
permission test that asserts `R60` cannot pass while `R60` is an undefined duplicate of `R32`;
and a coverage report cannot quote a percentage while the requirement denominator is one of four
numbers. This document does not fix those defects — it makes each of them a **bounded, owned,
dated remediation** instead of a recurring discovery.

> **What this document changes on the day it is approved.** Three things, all mechanical.
> **(a)** No new identifier may be allocated in any space without a named allocating authority and
> a pre-allocation collision check (§7). **(b)** Nine spaces are **frozen** (§9) — no new
> allocation at all until a named remediation completes. **(c)** Six regular expressions become CI
> gates (§10), and a build that allocates outside them fails.

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | Every identifier space in the four ERP repositories — `1000fix_ERP_Module`, `primary-doc`, `project_content`, `project-guide-doc` — and in `old-primary-doc` where a live document still cites it |
| 2 | The **form** (lexical pattern) of each space, expressed as a regular expression that can be run |
| 3 | The **allocating authority** for each space — the single named document or role that may issue a new identifier |
| 4 | **Permanence, retirement and reuse** rules |
| 5 | **Scope** — whether an identifier is programme-wide, repository-local, module-local or file-local, and how a reader tells |
| 6 | The **allocation procedure**, including the pre-allocation collision check already practised by ten documents and ratified here |
| 7 | The **freeze list** — spaces where allocation stops until a named defect is remediated |
| 8 | **Enforcement** — the regular expressions, the checks, and where they run |
| 9 | Identifier spaces created by **this repository itself**, which has committed three identifier events of its own |

**Explicitly out of scope:**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| What each term *means* | `RR-001` | An identifier convention says `BRU-SRM-09` is well-formed and who allocated it. It does not say what a business rule is, or what "service order" means. That adjudication is terminology, and terminology is `RR-001` |
| Document file naming, versioning, status and approval | `GV-011` §4.2, §5 | `GV-011` is the configuration-management plan and owns the document lifecycle. This document owns the *identifier*; `GV-011` owns the *file*. `GV-011` §4.4 explicitly defers the identifier standard to here |
| The house template and section set per document type | `RR-003` | Front-matter **keys** are a template question. Front-matter **`id` values** are an identifier question and are here |
| Programme decision allocation (`D-nnn`), risk (`RSK-`), issue (`ISS-`), assumption (`ASM-`), dependency (`DEP-`) | `GV-003`, `GV-005` | Those registers already operate cleanly with a single named authority. This document registers them and does not take them over |
| The requirement denominator dispute | `RQ-004` §5.1 | `RQ-004` rules one denominator for coverage measurement. This document records that the `FR-` space is disputed and freezes allocation; it does not re-rule the denominator |
| Custom-module (`CD-nnn`) content and sizing | `BE-005` | `BE-005` is the CD master register. This document governs the `CD-` *space*; `BE-005` governs its *contents* |
| Database, table, field and Odoo model naming | `AR-007` §4, `DA-002` | Code-level naming is a build standard. The `fix.*` model namespace is registered here as a space (§5.7) because it is an identifier space, but its rules are `AR-007`'s |
| Content-estate identifier allocation | `CG-005` | Already has an allocating authority and operates cleanly. Registered here (§5.5), governed there |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| **Anyone about to write an identifier** | §7. Run the check, get the authority's assent, then write it |
| Implementation vendor | §5 and §10 — to know which identifiers in a tender pack are stable enough to price against, and which are frozen |
| Enterprise Architecture | §9 — the freeze/thaw plan is the work programme |
| PMO / Configuration Manager | §7.4 allocation log; §10 CI gates |
| QA Lead | §10 — six of the checks are quality gates that fail a build |
| Auditor | §8 — the measured defect list, and §4 for the method to reproduce it |
| New joiner | §3 and §5.1 — how to read any identifier in the estate |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause / section | How this document conforms | Departure and rationale |
|---|---|---|---|
| **ISO/IEC 11179-1:2023** *Metadata registries — Framework* | §5 (registry model), §6 (administered items) | Every identifier space in §5 is modelled as an *administered item class* with an identifier, a designation, a definition, a registration authority and a registration status | 11179 assumes a software registry. This programme has 782 markdown files and no registry, so §5 is a **document**-borne registry with §10's checks standing in for referential integrity. Declared as a departure, and `RR-006` is the route to a real one |
| **ISO/IEC 11179-5:2015** *Naming and definition principles* | §4 (naming conventions), §5 (identification) | §3.2 adopts 11179-5's four naming-convention components — scope, authority, syntax, semantics — as the four columns every space in §5 must fill | 11179-5 addresses data element naming; this document extends the same four components to *document*, *requirement*, *rule* and *finding* identifiers. An extension, not a departure |
| **ISO/IEC 11179-6:2023** *Registration* | §6 (registration authority), §7 (registration status), §8 (administrative record) | §5's **Allocating authority** column is 11179-6's *Registration Authority*. §3.5 adopts the registration-status lifecycle in a simplified four-state form | Simplified from the full lifecycle. The complete model needs a body that can approve; `PGD-A1-09` records that no such body exists. Declared |
| **ISO 10007:2017** *Configuration management* | §5.3 Configuration identification | The identifier is the configuration-identification attribute of every configuration item named in `GV-011` §3.1 | None |
| **ISO 704:2022** *Terminology work — Principles and methods* | §7 (term formation) | Cited for the boundary only: 704 governs `RR-001`, not this document | Not applied here |

> **A note on why 11179 is the right basis and 42010 or 29148 is not.** The estate reached for
> `ISO/IEC/IEEE 29148` for requirements and `42010` for architecture, and neither says anything
> about identifier space administration. **11179 is the only ISO standard that treats "who is
> allowed to allocate a new identifier" as a first-class question**, which is precisely the
> question eight audit findings answer with *"nobody, and several people."*

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| Master register | `../PGD-000_Master_Register_of_Project_Guiding_Documents.md` | This document's row; the `PGD` and `RR` code spaces; §2.1 critical path row 21 |
| Category overview | `./_CATEGORY_OVERVIEW.md` | The eight findings `RR-002` is asked to prevent; the `RF`/`RR` collision that produced this category's own code |
| Documentation control | `../00_Programme_Governance_and_Control/GV-011_Documentation_Control_and_Configuration_Management_Plan.md` §4.2–4.5 | File naming; the three-scheme finding `PGD-A2-17`; **the interim identifier table §4.4, which this document supersedes**; the two priority scales `AF-11` |
| Decision log | `../00_Programme_Governance_and_Control/GV-003_Decision_Log_and_Change_Control_Procedure.md` | `D-nnn` and `CR-nnn` allocating authority; rule `DL-06` forbidding bare `D-nn` in a document-local table |
| RAID register | `../00_Programme_Governance_and_Control/GV-005_RAID_Register.md` | `RSK-`, `ASM-`, `ISS-`, `DEP-` allocating authority |
| Module template | `../../1000fix_ERP_Module/03_Modules/_MODULE_TEMPLATE.md` §0 | The module-local identifier rules; `RG-01`…`RG-06`; the `AUT-<CODE>-nn` form |
| Master index | `../../1000fix_ERP_Module/00_Governance_and_Charter/00-01_Master_Index_and_Document_Map.md` §3 | The programme identifier table — 16 spaces, 30 module short codes; **the `AUT-nnn` form that contradicts the template** |
| Module catalogue | `../../1000fix_ERP_Module/02_Architecture/02-02_Module_Catalogue_Master_Register.md` | `M<nn>` allocation; the `CD-` origin |
| Role matrix | `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md` | `R01`–`R38`, `SOD-01`–`SOD-12` registered |
| Feature register | `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md` | `FR-` allocating authority; the 200-identifier register behind a ~3,500-identifier space |
| Repository audits | `../../1000fix_ERP_Module/00_Governance_and_Charter/00-06_Documentation_Audit_Report.md`, `00-07_Category_H_Audit_and_Repository_Integrity_Report.md` | Findings `C-02`, `C-03`, `H-03`, `H-04`, `H2-04`, `H2-06`, `H2-07` |
| Content glossary | `../../project_content/99_Reference_and_Registers/RF-001_ERP_Glossary_and_Acronym_Register.md` §4.2, §4.3 | **The prior art.** The content estate's prefix register and its four defects `GL-01`…`GL-04`. This document extends it to the engineering estate and does not restate it |
| Content governance | `../../project_content/00_Content_Governance_and_Standards/CG-005_*.md` | The content-estate allocating authority for 21 category codes |
| CD master register | `../07_Build_Engineering_and_Development_Standards/BE-005_Custom_Development_CD_Master_Register.md` | The `CD-` space as rebuilt; the `CD-M99-42` well-formed-but-meaningless example |

### 2.3 Audit findings this document closes

| Finding | Source audit | How this document closes it |
|---|---|---|
| `C-02` | `00-06` | §5.2 `M<nn>`: allocation authority named (`02-02`), range fixed at `M01`–`M67`, and §8.6 records that `M68` and `M99` are in use in this repository as *illustrative* values and are reserved-unallocated, not allocated |
| `C-03` | `00-06` | §5.3: `FR-<CODE>-nnn` — one code per module, `<CODE>` taken from the module's own `module_code` front matter, which is now the single source. The `FR-BFO-` residue is registered as retired-in-place (§8.4) |
| `H-03` | `00-06` | §5.4 `CD-nnn`: authority moved from `02-05` to **`BE-005`** by decision `RR-002-D-03`; the space is **frozen** (§9) until `BE-005`'s reconciliation is signed |
| `H-04` | `00-06` | §5.3.2 publishes **all 72 module short codes in use**, counted, against the 30 that `00-01` §3 lists — a 42-code gap, larger than the 37 the finding assumed |
| `H2-04` / `RP-01` | `00-07` / `AUDIT-015` | §5.6 `KPI-nnn`: **301 distinct identifiers counted against 95 registered**; space frozen; authority named as `06-02` pending `BM-002` |
| `H2-06` | `00-07` | §5.6 `SOD-nn`: closed in the content estate by `SP-006` registering `SOD-13`…`SOD-60`; **this document records that `05-04` §6 still registers only 12, so the engineering estate's copy of the finding is open**, and names the fix |
| `H2-07` | `00-07` | §5.6 `Rnn`: **53 distinct role identifiers counted against 38 registered**; `R60`/`R32` duplication registered as a defect with an owner; space frozen |
| `AP-02` | `AUDIT-016` | §5.6 `NFR-nnn`: space frozen; `NFR-088`…`NFR-092` listed as contested identifiers that may not be cited in a test case until `RQ-006` rules |
| `EO-02` | `AUDIT-018` | §5.3.3: `BRU-<CODE>-nn` is module-local, so an `M12` rule duplicated under a second identifier is a **within-space** duplication; rule `IDC-09` forbids it and §10 check `CHK-04` detects it |
| `PGD-A1-01` | `PGD-AUDIT-001` | §5.8 registers the audit-finding identifier spaces — the defect class that produced the finding |
| `PGD-A2-03` | `PGD-AUDIT-002` | §5.9 ratifies `DL-06` and generalises it as rule `IDC-07` (document-local spaces must be qualified) |
| `PGD-A2-17` | `PGD-AUDIT-002` | §8.2: the three-scheme finding is measured — 122 distinct `FIX-ERP2-` values across **six sub-forms**, with **one duplicate**, previously unrecorded |
| `PGD-A2-19` | `PGD-AUDIT-002` | §8.7 records this repository's three identifier events and §7 makes the fourth impossible |
| `GL-01`…`GL-04` | `RF-001` §4.3 | Adopted, not restated. §5.3 carries `GL-02`'s ruling on `SRM2`; §8.4 carries `GL-04`'s `FR-SLS-`/`FR-BFO-` residue; `GL-03`'s `D-nn` collision is closed by `IDC-07` |

> **What this document does *not* close.** It does not close `TS-01` (the coverage denominator),
> `AF-06` (the `05-01` restatement), or any finding whose remedy is to *change the content* of a
> register. A convention standard can say *"`05-01` is the allocating authority for `FR-`, and it
> currently registers 200 of ~3,500 identifiers."* It cannot register the other 3,300. Those are
> named with owners in §9 and are the thaw conditions.

---

## 3. The Identifier Model

### 3.1 What an identifier is, in this programme

An identifier is a **short, stable, machine-matchable string that denotes exactly one thing**, so
that a reader, a test, a ticket and a contract can all refer to that thing without ambiguity.

Three properties do the work, and the estate's defects are each a failure of one of them:

| Property | Statement | The failure when it is absent | Instance in this estate |
|---|---|---|---|
| **Uniqueness** | Within its space, one identifier denotes one thing | Two things share an identifier; a reader cannot tell which is meant | `NFR-090` (two requirements), `D-01` (two decisions), `FIX-ERP2-006` (two documents) |
| **Stability** | Once allocated, the identifier is never re-pointed at something else | A citation written last month now resolves to something different, silently | `CD-` reallocation `+26` for the twelve portals |
| **Resolvability** | The identifier resolves to a definition somewhere a reader can reach | The identifier is decoration | `R54`, `R57`, `SOD-31`…`SOD-61` in the engineering estate, `FR-SLS-001`…`030` |

### 3.2 The four things every identifier space must declare

Adopted from ISO/IEC 11179-5:2015 §4, which names *scope*, *authority*, *syntax* and *semantics*
as the four components of a naming convention. Every row of §5 fills all four:

| Component | 11179-5 term | This document's column | Question it answers |
|---|---|---|---|
| **Form** | Syntax | `Form` — a regular expression | Is this string well-formed? |
| **Scope** | Scope | `Scope` | Programme-wide, repository-local, module-local or file-local? |
| **Authority** | Authority | `Allocating authority` | Who may issue a new one? |
| **Meaning** | Semantics | `Denotes` | What class of thing does it name? |

Plus two the programme's own history requires:

| Component | Column | Question it answers |
|---|---|---|
| **Permanence** | `Permanence` | May a retired identifier be reused? |
| **State** | `State` | Is this space operating, frozen, disputed or retired? |

### 3.3 Scope, and how a reader tells

The estate's most common identifier misreading is a **file-local** identifier read as
programme-wide. `AC-06` in `M09` and `AC-06` in `M16` are unrelated acceptance criteria; a reader
who does not know that will cross-reference two different things.

| Scope | Meaning | How the reader knows | Citation form required |
|---|---|---|---|
| **Programme-wide** | One allocation across all four repositories | Listed in §5 with a single allocating authority | Bare: `NFR-018`, `M31`, `KPI-022` |
| **Repository-local** | One allocation within one repository | Listed in §5 with a repository named in the Scope column | Bare within the repository; qualified across it: `project_content` `DM-004` |
| **Module-local** | One allocation within one module or portal specification | The `<CODE>` element carries the module | Always carries its code: `BRU-SRM-09` |
| **Document-local** | One allocation within one file | Not in §5 at all — §5.9 registers the *classes* | **Always qualified**: `M09` `AC-06`, `RR-002` `IDC-07`, never bare |

> **Rule `IDC-07` in one line: a document-local identifier cited outside its document is written
> `<document-id> <identifier>`, with a space, never bare.** This is the generalisation of `DL-06`,
> which `GV-003` introduced for the decision space after a bare `D-01` in a template would have
> produced up to 140 different decisions with one identifier.

### 3.4 Permanence and retirement

Inherited from `RG-02` and made general:

| # | Rule |
|---|---|
| `IDC-04` | An allocated identifier is **permanent**. The thing it denotes may be renamed, re-scoped, deferred or cancelled; the identifier stays attached to it |
| `IDC-05` | A withdrawn identifier is **retired, never reissued**. The register keeps the row and marks it retired, with the date and the reason |
| `IDC-06` | A retired identifier still **resolves**. A reader who meets `FR-BFO-029` must reach a row that says *retired 2026-08-18 under audit `C-03`, superseded by `FR-FRD-029`* — not a 404 |

> **Why retirement-not-deletion, stated once.** `SC-008` §4.1 keeps repealed statutes in its
> register for exactly this reason: *"a citation of `ST-01` anywhere in the estate must resolve to
> a row that says repealed, not to nothing."* The same logic governs identifiers. Deleting a row
> does not delete the citations pointing at it; it only removes the explanation.

### 3.5 Registration status

Four states, simplified from ISO/IEC 11179-6:2023 §7:

| State | 11179-6 equivalent | Meaning | May a new identifier be allocated? |
|:--:|---|---|:--:|
| **Operating** | Standardised | Single named authority, register current, form enforced | **Yes** |
| **Disputed** | Qualified | Authority named, but the register's contents are contested by an open finding | Yes, **with the finding cited in the allocation log** |
| **Frozen** | Recorded | An open defect makes new allocation actively unsafe | **No** — until the named thaw condition completes |
| **Retired** | Superseded | The space is closed; existing identifiers resolve, none are added | **No, permanently** |

---

## 4. The Measured Position

### 4.1 Method

Every figure in §4 and §5 was produced by these commands, run against the workspace root at
**2026-08-19 02:41 (+06)**. They are printed so the count can be reproduced and challenged.

```bash
# The identifier-shaped token population
grep -rhoE '\b[A-Z]{1,6}(-[A-Z]{2,4})?-[0-9]{2,4}\b' --include='*.md' . | sort -u | wc -l
# Distinct prefixes (the "spaces", before de-noising)
grep -rhoE '\b[A-Z]{1,6}(-[A-Z]{2,4})?-[0-9]{2,4}\b' --include='*.md' . \
  | sed -E 's/-[0-9]+$//' | sort -u | wc -l
# Per-space population, e.g. the role space
grep -rhoE '\bR[0-9]{2}\b' --include='*.md' . | sort -u | wc -l
```

**What the pattern captures, and what it misses — stated so the figure is usable.**

| | |
|---|---|
| **Captures** | `PREFIX-nnn`, `PREFIX-CODE-nnn` in upper case with 2–4 digits |
| **Misses — by design** | Digit-suffixed forms without a separator (`M31`, `P07`, `R14`, `W4`, `G1`) — counted separately per space in §5. Dotted forms (`fix.service.order`, `service_order.delivered.v1`) — §5.7. Single-digit suffixes (`SOD-1`) — normalised in §5.6 |
| **False positives** | Cryptographic and protocol constants of the same shape: `SHA-256`, `AES-256`, `RSA-2048`, and bin locations such as `A-04`. Concentrated in single-letter prefixes and estimated at **≈17%** of the *prefix* population by inspection of a 200-token sample |
| **Consequence** | **1,094 distinct prefixes is an upper bound.** The de-noised estimate is **≈900**. Both are stated; neither is close to the ~46 the register names |

### 4.2 The counted population

| Measure | Counted 2026-08-19 02:41 (+06) | What `PGD-000` §99 records |
|---|---:|---|
| Markdown files in the workspace | **782** | 772 (at 02:10, 31 minutes earlier) |
| Distinct identifier-shaped **tokens** | **18,630** | not recorded anywhere in the estate |
| Total **occurrences** of those tokens | **152,518** | not recorded |
| Distinct **prefixes** (upper bound) | **1,094** | *"seven … plus"* ~39 named ⇒ **≈46** |
| Distinct prefixes (de-noised estimate) | **≈900** | — |
| Prefixes appearing in **3 or more** repositories | **109** | not recorded |
| Prefixes appearing in **all five** repositories | **15** — `UC` `RSK` `NFR` `MIG` `INT` `DEP` `CON` `CD` `C` `BRU-SRM` `BRU-INV` `BRU-HRM` `BRU-FIN` `BO` `ASM` `A` | not recorded |

Per repository:

| Repository | `.md` files | Distinct prefixes | Distinct identifiers |
|---|---:|---:|---:|
| `1000fix_ERP_Module` | 123 | 321 | 7,615 |
| `primary-doc` | 4 | 164 | 1,573 |
| `old-primary-doc` | 6 | 82 | 961 |
| `project_content` | 488 | 601 | 7,408 |
| `project-guide-doc` | **161** | **472** | **6,754** |
| **Workspace** | **782** | **1,094** *(union, not sum)* | **18,630** *(union)* |

> ### `IDC-F-01` — the identifier problem is roughly twenty times the size the register records
>
> `PGD-000` Category 99 states: *"The estate operates seven module-local and programme-wide
> identifier spaces — `FR`, `BRU`, `AUT`, `KPI`, `CD`, `R`, `SOD` — plus `NFR`, `INT`, `EVT`, `E`,
> `M`, `P`, `W`, `RSK`, twenty-one content codes, and now seventeen guiding-document codes."*
> That enumerates **46**.
>
> The filesystem returns **1,094**, of which **≈900** survive de-noising. Even taking the most
> conservative reading — count only prefixes with ten or more distinct identifiers — the figure is
> **over 300**.
>
> **This is not a criticism of the register.** The register named the spaces it knew had
> *allocating authorities*. The finding is that **the estate has been generating identifier spaces
> as a side effect of authoring**, at a rate nobody measured, and this document is the first
> enumeration of the space *as a space* in the engineering estate — as `RF-001` §4.3 was for the
> content estate. `RF-001` found four defects by doing this. This document finds **eleven** (§8).

### 4.3 The baseline moved during this document's own research

`RG-08` — timestamped enumeration — has been recommended nine times and never ratified. The
reason it keeps being recommended is visible in this document's own working:

| Time (+06) | `project-guide-doc` `.md` | Workspace `.md` | What appeared |
|---|---:|---:|---|
| 2026-08-19 **02:10** | 151 | 772 | `PGD-000` v1.6's enumeration |
| 2026-08-19 **02:29** | 157 | 778 | `SV-002`, `SV-003`, `RL-001`…`RL-003`, `CO-005` |
| 2026-08-19 **02:39** | 160 | 781 | `SV-004`, `CO-002`, `PGD-AUDIT-CAT-12` |
| 2026-08-19 **02:41** | **161** | **782** | one further file |

**Three enumerations, thirty-one minutes, ten files.** Two of the three movements happened *while
this document's evidence was being gathered*, which means any absence assertion in this document
carries the same risk `CHA-12` recorded against Category 13: **true when written, false when
read**. Every count above therefore carries a time, not a date — and §10 `CHK-06` makes the count
regenerable rather than quotable.

This is at least the **tenth** recorded baseline movement (`PGD-A1-03`, `AP-17`, `MGA-15`,
`CHA-12` and now this). `RG-08` is recommended for the tenth time in `RR-002-D-07`.

---

## 5. The Identifier Space Register

This is the normative register. It **supersedes `GV-011` §4.4**, which declared itself interim
pending this document.

### 5.1 How to read a row

| Column | Meaning |
|---|---|
| **Space** | The prefix, with its form |
| **Denotes** | The class of thing named |
| **Form** | A regular expression that matches a well-formed identifier and nothing else |
| **Scope** | Per §3.3 |
| **Authority** | The single document or role that may allocate |
| **Counted** | Distinct identifiers on disk at 2026-08-19 02:41 (+06) |
| **Registered** | Distinct identifiers the authority's register actually holds |
| **State** | Per §3.5 |

### 5.2 Structural spaces — modules, portals, waves, gates, categories

| Space | Denotes | Form | Scope | Authority | Counted | Registered | State |
|---|---|---|---|---|---:|---:|:--:|
| `M<nn>` | ERP module specification | `^M(0[1-9]\|[1-6][0-9])$` | Programme | `02-02` | 67 + 2 unallocated | 67 | **Operating** |
| `P<nn>` | Portal or application specification | `^P(0[1-9]\|1[0-2])$` | Programme | `04-00` | 12 | 12 | **Operating** |
| `W<n>` | Delivery wave | `^W[1-9]$` | Programme | `06-01` | 9 | 9 | **Operating** |
| `G<n>` / `G<n>-<nn>` | Wave gate / gate criterion | `^G[1-9](-[0-9]{2})?$` | Programme | `GV-009` | 4 gates | 4 | **Operating** |
| `A`…`K` | Module category letter | `^[A-K]$` | Programme | `02-01` | 11 | 11 | **Operating** |
| `L1`…`L6` | Delivery layer | `^L[1-6]$` | Programme | `00-01` §3 | 6 | 6 | **Operating** |
| `P0`…`P3` | Priority | `^P[0-3]$` | Programme | `00-01` §3 | 4 | 4 | **Operating** ⚠ |

> **⚠ `P<n>` is two spaces sharing a form.** `P07` is a portal; `P0` is a priority. The forms are
> distinguishable only by digit count, and `AF-11` records a *third* `P1`–`P4` priority scale in a
> neighbouring programme. Rule `IDC-14`: **a priority is always written `P0`–`P3` with one digit
> and a portal always `P01`–`P12` with two.** A one-digit portal reference or a two-digit priority
> is malformed. `CHK-02` enforces it.
>
> **`M68` and `M99` are in use and are not allocated.** Both appear in `BE-005` — `M99` inside the
> illustrative identifier `CD-M99-42` ("well-formed and denotes nothing") and `M68` in a row about
> a *hypothetical* future allocation. Neither is a module. §8.6 registers both as
> **reserved-unallocated**, and `CHK-01` treats a bare `M68` or `M99` outside those two contexts as
> an error. This is `C-02`'s failure mode caught before it happened.

### 5.3 Requirement and rule spaces — module-local

#### 5.3.1 The spaces

| Space | Denotes | Form | Scope | Authority | Counted | Registered | State |
|---|---|---|---|---|---:|---:|:--:|
| `FR-<CODE>-nnn` | Functional requirement | `^FR-[A-Z]{3}[0-9]?-[0-9]{3}$` | Module-local | `05-01` §1.3 | **3,504** | 200 | **Frozen** |
| `NFR-nnn` | Non-functional requirement | `^NFR-[0-9]{3}[a-c]?$` | Programme | `05-06` | **122** | 104 | **Frozen** |
| `BRU-<CODE>-nn` | Business rule | `^BRU-[A-Z]{3}-[0-9]{2}$` | Module-local | Module file §10 | **1,354** | — | **Disputed** |
| `BR-STD-nn` | Cross-cutting business rule | `^BR-STD-[0-9]{2}$` | Programme | `05-05` §1 | 6 | 6 | **Operating** |
| `AUT-<CODE>-nn` | Automation rule | `^AUT-[A-Z]{3}-[0-9]{2}$` | Module-local | Module file §11 | **1,438** | — | **Disputed** ⚠ |
| `AUT-nnn` | Automation rule *(legacy form)* | `^AUT-[0-9]{3}$` | Programme | `00-01` §3 | **60** | — | **Retired** ⚠ |
| `UC-nnn` | Use case | `^UC-[0-9]{3}$` | Programme | `RQ-008` | 33 | 33 | **Operating** |
| `AC-nn` | Acceptance criterion | `^AC-[0-9]{2}$` | **Document-local** | The document | 3,217 occ. | n/a | **Operating** |

> ### `IDC-F-02` — `AUT-` is one declared space with two incompatible conventions, and nobody noticed
>
> `00-01` §3 declares **`AUT-nnn`**, *"Automation / workflow, example `AUT-031`, defined in Doc 15"* —
> a **programme-wide** space. `_MODULE_TEMPLATE.md` §0 declares **`AUT-<CODE>-nn`**, *"Module-local,
> allocated by this file."* They are not variants of one convention; they differ in **form, scope
> and allocating authority simultaneously**.
>
> Counted: **1,438** identifiers in the module-local form and **60** in the programme-wide form.
> A reader who meets `AUT-031` cannot tell whether it is the 31st automation in the programme or a
> malformed module-local one, and the two documents that would tell them disagree.
>
> **Ruling `RR-002-D-01`.** The module-local form `AUT-<CODE>-nn` is **adopted**; the bare
> `AUT-nnn` form is **retired**. Rationale: 1,438 identifiers against 60, and module-locality is
> correct for a rule that only fires inside one module's workflow. The 60 legacy identifiers are
> **retired in place** under `IDC-06` — they resolve to a row saying *legacy programme-wide form,
> retired 2026-08-19, see the owning module's §11*. `00-01` §3 must be corrected; owner
> Enterprise Architecture, `RR-002-Q-02`.
>
> This defect is **not in any audit**. Five audits examined identifier *collisions*; none examined
> whether two documents declared the same space differently.

#### 5.3.2 The module short-code vocabulary — all 72, counted

`00-01` §3 lists **30** codes. `H-04` recorded the gap as *"lists 30 of 67."* The counted figure
is **72 distinct codes in `FR-` position** and **71 in `BRU-` position**, because the vocabulary
grew past the module count: some modules carry more than one code and three codes have no module.

```
ADM AIM APE ARB AST BFO BID BIL BPA CAI CAT CCE CPM CRM CTR CWM CXM DAT DMS DPL DTS EAM ECM ESG
FAC FIN FLT FPA FRD FSM FXA GLO GRC HCM HRM HSE INV IOT IPF ITC ITS KMS LMS LOG LOY MDM MKP MKT
PAY PCM PIC POR PPM PRC PRO PRT QMS QTE REV RMS RNT SCM SEC SLS SRM SRM2 SUB TAO TAX TRE TRF WFM
WMS WSR WTY
```

| Set relation | Codes | Consequence |
|---|---|---|
| In `FR-`, not in `BRU-` | `BFO`, `POR`, `SLS` | `POR`'s 358 portal requirements have **no business rules at all**; `BFO` and `SLS` are retired residue (§8.4) |
| In `BRU-`, not in `FR-` | `CWM`, `PRT` | Two rule families govern behaviour with no requirement family behind them |
| Declared in module front matter | **67** — one per module file | The single authoritative source |
| Malformed against the stated pattern | **`SRM2`** | 34 requirements silently dropped by any regex written to `FR-[A-Z]{3}-` |

> **`SRM2` is ruled, not corrected.** `RF-001` `GL-02` diagnosed it: `M42` needed `SRM`, `M01` held
> it, and a digit was appended. Renaming 34 identifiers would breach `IDC-04` (permanence) for a
> cosmetic gain. **Ruling `RR-002-D-02`: the form is widened to `[A-Z]{3}[0-9]?` and `SRM2` is
> registered as a valid, closed, one-off.** No further digit-suffixed code may be allocated —
> `IDC-10`. The `<CODE>` element is taken from the module's `module_code:` front-matter key, which
> §10 `CHK-03` makes the single source of truth.

#### 5.3.3 Within-space duplication

`EO-02` found six `M12` business rules duplicated under a second identifier. Because `BRU-` is
module-local, this is duplication *inside* one file, which no cross-file check would find.

**Rule `IDC-09`.** Within a module-local space, an identifier is allocated once. Two rows with the
same `BRU-<CODE>-nn` in one file, or two identifiers whose rule text is byte-identical, are both
defects. `CHK-04` detects the first mechanically and reports the second as a candidate.

### 5.4 Build and delivery spaces

| Space | Denotes | Form | Scope | Authority | Counted | Registered | State |
|---|---|---|---|---|---:|---:|:--:|
| `CD-nnn` | Custom Odoo module / custom development unit | `^CD-[0-9]{3}$` | Programme | **`BE-005`** *(moved from `02-05`)* | **261** | 199 | **Frozen** |
| `cd_<name>` | Odoo technical module name | `^cd_[a-z][a-z0-9_]*$` | Programme | `AR-007` §4 | 413 | — | **Disputed** |
| `INT-nnn` | Integration | `^INT-[0-9]{3}$` | Programme | `05-03` | **63** | 47 | **Disputed** |
| `TD-nn` | Technology decision | `^TD-[0-9]{2}$` | Programme | `02-05` | 15+ | — | **Disputed** |
| `IP-nn` | Integration principle | `^IP-[0-9]{2}$` | Programme | `05-03` §1 | 10 | 10 | **Operating** |
| `PS-nn` | Portal standard | `^PS-[0-9]{2}$` | Programme | `04-00` §3 | 12 | 12 | **Operating** |
| `DoD-nn` | Definition of done | `^DoD-[0-9]{2}$` | Programme | `02-02` | 17 | 17 | **Operating** |
| `SRC-nnn` | Legacy source system | `^SRC-[0-9]{3}$` | Programme | `MG-002` | 38+ | — | **Operating** |

> **`RR-002-D-03` — the `CD-` allocating authority moves to `BE-005`.** `00-01` §3 and
> `_MODULE_TEMPLATE` §0 both name `02-05` as the authority; `02-05` is a technology-stack document
> that acquired the register incidentally, and `H-03` found two incompatible registers with 48
> colliding identifiers as a result. `BE-005` (110 KB, Category 07) was written to be the CD master
> register. **The authority follows the register.** The space stays **frozen** — no build ticket may
> cite a `CD-` identifier — until `BE-005`'s reconciliation carries an approval record. Counted at
> **261 distinct identifiers against 199 registered** in `RF-001`, so the gap widened by 62 since
> 2026-08-18.

### 5.5 Repository document-code spaces

| Space | Denotes | Form | Scope | Authority | Counted | State |
|---|---|---|---|---|---:|:--:|
| `<CODE>-<nnn>` guiding document | A `project-guide-doc` document | `^(GV\|RQ\|AR\|DA\|IN\|SC\|UX\|BE\|QA\|MG\|PE\|SV\|RL\|CH\|CO\|BM\|RR)-[0-9]{3}$` | Repository | **`PGD-000`** | 140 registered, **125 on disk** | **Operating** |
| `<CODE>-<nnn>` content | A `project_content` file | 21 codes per `RF-001` §4.2.3 | Repository | **`CG-005`** | ~370 | **Operating** |
| `<nn>-<nn>` | A `1000fix_ERP_Module` programme file | `^[0-9]{2}-[0-9]{2}$` | Repository | `00-01` | 22 | **Operating** |
| `FIX-ERP2-*` | Module-repo front-matter `id` | six sub-forms — §8.2 | Repository | **none** | 122 distinct / 123 files | **Frozen** ⚠ |
| `PGD-*` | Guide-repo repository-level artefact | `^PGD-(000\|README\|CAT-[0-9]{2}\|AUDIT-.*)$` | Repository | `PGD-000` | 4 forms | **Disputed** ⚠ |

> **The `RF` / `RR` collision, and why this category's code is `RR`.** `project_content` category
> 99 uses `RF`; this category uses `RR`. `RF-001` and `RR-001` are different documents in different
> repositories with the same role. **Rule `IDC-11`: a document code is unique across the
> *workspace*, not across a repository.** Both codes are registered here so the next author does
> not have to rediscover the constraint. This is `AF-11`'s failure mode avoided by luck once and by
> rule from now on.

### 5.6 Programme registers — the frozen five

| Space | Denotes | Form | Authority | Counted | Registered | Gap | State |
|---|---|---|---|---:|---:|---:|:--:|
| `KPI-nnn` | Key performance indicator | `^KPI-[0-9]{3}$` | `06-02` | **301** | 95 | **206** | **Frozen** |
| `R<nn>` | User role | `^R[0-9]{2}$` | `05-04` | **53** | 38 | **15** | **Frozen** |
| `SOD-nn` | Segregation-of-duties rule | `^SOD-[0-9]{2}$` | `05-04` | **61** | 12 | **49** | **Frozen** |
| `NFR-nnn` | Non-functional requirement | `^NFR-[0-9]{3}[a-c]?$` | `05-06` | **122** | 104 | **18** | **Frozen** |
| `FR-<CODE>-nnn` | Functional requirement | §5.3.1 | `05-01` | **3,504** | 200 | **3,304** | **Frozen** |

> ### `IDC-F-03` — every gap is larger than the finding that recorded it
>
> | Space | The finding said | Counted 2026-08-19 | Multiple |
> |---|---|---:|---:|
> | `KPI-` | `RP-01`: "250 in use against 95" | **301 against 95** | 1.2× |
> | `SOD-` | `_MODULE_TEMPLATE`: "13–30 unregistered" (18) | **49 unregistered** | 2.7× |
> | `R<nn>` | `H2-07`: "R39–R46 plus three" (11) | **15 unregistered** | 1.4× |
> | `CD-` | `H-03`: "48 collide" | **62 unregistered** | 1.3× |
> | Module codes | `H-04`: "30 of 67" (37 missing) | **42 missing** | 1.1× |
>
> Five independent measurements, all in the same direction. **The estate's identifier gaps grow
> between audits because authoring continues and allocation does not stop.** That is the argument
> for the freeze in §9, and it is why the freeze is the operative control of this document rather
> than the register.
>
> **`SOD-` deserves a specific note.** `RF-001` records that `SP-006` (content estate) closed
> `H2-06` by registering `SOD-13`…`SOD-60`. That closure is real — **for the content estate**.
> `05-04` §6, which `_MODULE_TEMPLATE` §0 names as the allocating authority for the *engineering*
> estate, still registers only `SOD-01`…`SOD-12`. **A finding closed in one repository and open in
> another is the shape this whole category exists to prevent.** Owner: `SC-004`, thaw condition
> `TH-03`.

### 5.7 Technical namespaces

These are identifier spaces in every meaningful sense — they name things uniquely, they are cited
across documents, and a collision breaks a build — but no register governs them.

| Space | Denotes | Form | Authority | Counted | State |
|---|---|---|---|---:|:--:|
| `fix.<model>` | Odoo model / entity | `^fix\.[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)*$` | `DA-001` / `AR-007` §4 | **1,574** distinct | **Disputed** |
| `<domain>.<verb>.v<n>` | Domain event | `^[a-z][a-z_]*\.[a-z][a-z_]*\.v[0-9]+$` | **`IN-003`** | 953 registered by `AR-009`; 2 schema files on disk | **Operating** |
| `EVT-<domain>.<verb>` | Domain event *(legacy form)* | — | `00-01` §3 | **1** occurrence | **Retired** |
| `E-<MOD>-nn` | Data entity *(legacy form)* | — | `00-01` §3 | **1** occurrence | **Retired** |
| `FN-<MOD>-nnn` | Function *(legacy form)* | — | `00-01` §3 | **1** occurrence | **Retired** |

> ### `IDC-F-04` — three declared spaces are dead, and the table that declares them is still cited
>
> `00-01` §3 declares sixteen identifier spaces. Three of them — `E-<MOD>-nn`, `FN-<MOD>-nnn` and
> `EVT-<domain>.<verb>` — return **one occurrence each** across 782 files, and that occurrence is
> the declaration itself. The estate names entities with Odoo model names (`fix.service.order`,
> 1,574 distinct) and events with `domain.verb.vN` (`service_order.delivered.v1`), neither of which
> `00-01` §3 mentions.
>
> **Why this matters more than it looks.** `00-01` §3 is the document a new joiner, a vendor and an
> auditor are pointed at to learn the identifier conventions. **Three of its sixteen rows describe
> a convention nothing follows, and it omits the two conventions that actually carry 2,527
> identifiers.** A vendor writing an interface to the stated `EVT-` convention would produce code
> that matches nothing.
>
> **Ruling `RR-002-D-04`.** The three legacy forms are **retired** (`IDC-06`: they resolve to this
> row). `fix.<model>` and `<domain>.<verb>.v<n>` are **registered** here as programme identifier
> spaces with `DA-001`/`AR-007` and `IN-003` as authorities. `00-01` §3 must be restated —
> `RR-002-Q-02`.

### 5.8 Governance, risk and finding spaces

#### 5.8.1 Operating cleanly

These five are the estate's counter-example: a single named authority, a register that is the
authority, and no findings.

| Space | Denotes | Authority | Counted | State |
|---|---|---|---:|:--:|
| `D-nnn` | Programme decision | **`GV-003`** | 42 | **Operating** |
| `CR-nnn` | Change request | **`GV-003`** | — | **Operating** |
| `RSK-nnn` | Risk | **`GV-005`** | 59 | **Operating** |
| `ASM-nn` / `ISS-nn` / `DEP-nn` | Assumption / issue / dependency | **`GV-005`** | — | **Operating** |
| `SB-n` | Scope baseline | **`GV-006`** | 3 | **Operating** |

> **`GV-011` §4.4 already observed the pattern and this document confirms it by counting: the five
> clean spaces are exactly the five with a single named allocating authority whose register *is*
> the authority.** Every frozen space has an authority that is a document written for another
> purpose which acquired a register incidentally — `02-05` (a technology-stack document holding
> `CD-`), `05-01` (a summary holding `FR-`), `06-02` (a benefits document holding `KPI-`).
>
> **This is the design rule the standard extracts: `IDC-02` — an allocating authority must be a
> register whose primary purpose is that register.**

#### 5.8.2 Audit finding spaces — and this repository's own defect

| Space | Denotes | Authority | Counted | State |
|---|---|---|---:|:--:|
| `AF-nn` | Cross-repository audit finding | `AUDIT-001` | 18 | **Operating** |
| `<XX>-nn` | Category audit finding, content estate | `AUDIT-002`…`AUDIT-021` | 232+ | **Document-local** |
| `PGD-A<n>-nn` | Guide-repo audit finding, sequential audits | `PGD-AUDIT-001`…`009` | — | **Document-local** |
| `<XXX>-nn` | Guide-repo audit finding, category audits | `PGD-AUDIT-CAT-*` | — | **Document-local** |
| `PGD-AUDIT-<nnn>` | Audit report, sequential form | **none** | 9 | **Frozen** ⚠ |
| `PGD-AUDIT-CAT-<nn>` | Audit report, category-keyed form | **none** | 5 | **Disputed** ⚠ |

> ### `IDC-F-05` — the audit identifier space has no allocating authority, and has had nine events
>
> Fourteen audit reports exist in `project-guide-doc/_AUDIT/` at 2026-08-19 02:41. **Nine use a
> sequential form and five a category-keyed form**, and neither has an allocating authority. A
> `PGD-AUDIT-\d{3}` sweep — the obvious one to write — **misses five of fourteen**.
>
> `PGD-000` records that `PGD-AUDIT-009` was claimed by Category 10 four minutes before Category
> 13's enumeration; a duplicate `PGD-AUDIT-002` was created and resolved on 2026-08-18. Sequential
> allocation is **unsafe under concurrent authoring**, which is the operating condition of this
> repository — §4.3 measures ten files appearing in thirty-one minutes.
>
> **Ruling `RR-002-D-05`.** The **category-keyed form `PGD-AUDIT-CAT-<nn>` is adopted** as the sole
> form for category audits, because it is *collision-free by construction*: the category number is
> allocated by `PGD-000`, one audit per category, so two concurrent authors cannot collide. The
> nine sequential identifiers are **retired in place** with a mapping table (§8.5) so existing
> citations resolve. Repository-level audits that are not category audits take
> `PGD-AUDIT-REG-<nn>`, allocated by `PGD-000`.
>
> **This is the ninth identifier event in a repository whose own register names identifier
> collisions as the estate's largest defect class.** It is recorded, not smoothed, per the culture
> `PGD-000` §2.3 identifies as a genuine asset.

### 5.9 Document-local space *classes*

These are not registered individually — there are thousands — but the **classes** are registered
so that `IDC-07` can be enforced.

| Class | Form | Typical owner | Citation form outside the document |
|---|---|---|---|
| Acceptance criterion | `AC-nn` | Any document §15/§13 | `M09` `AC-06` |
| Open question | `Q-nn` | Any document | `M22` `Q-02` |
| Open item | `O-nn` | Content files | `OP-004` `O-03` |
| Local decision | `<DOC-ID>-D-nn` | Any document §4 | Already qualified — `GV-001-D-01` |
| Local rule | `<PREFIX>-nn` | Declared in `rule_prefix:` front matter | `RR-002` `IDC-07` |
| Finding, within an audit | `<PREFIX>-nn` | The audit report | `PGD-AUDIT-CAT-13` `CHA-12` |

> **The `rule_prefix:` front-matter key is ratified here.** Ten documents already declare a
> three-letter rule prefix in front matter *together with the evidence that it was free before
> allocation* — for example `RBS — verified to return zero occurrences … the candidate RBK was
> rejected because MG-007 owns it with 101 occurrences`. That is a correct, self-documenting
> allocation protocol invented in practice. **Rule `IDC-08` makes it mandatory** and §7.2 states
> the procedure. `RR-003` adds `rule_prefix:` to the front-matter schema.

---

## 6. The Rules

Fourteen rules. Each is testable; the enforcing check is named where one exists.

| # | Rule | Enforced by |
|---|---|---|
| `IDC-01` | **Every identifier space has exactly one allocating authority**, named in §5. A space with no authority is frozen | §5, `CHK-05` |
| `IDC-02` | **An allocating authority is a register whose primary purpose is that register.** A document that acquired a register incidentally may not remain its authority | §5.8.1, review at gate |
| `IDC-03` | **Register-first.** An identifier is allocated in its register before it is used in prose, a ticket or code | `CHK-05` |
| `IDC-04` | **Permanence.** An allocated identifier is never re-pointed | `CHK-05` |
| `IDC-05` | **No reuse.** A withdrawn identifier is retired, never reissued | `CHK-05` |
| `IDC-06` | **Retired identifiers still resolve.** The register keeps the row, marked retired, with date and reason | §8.4, §8.5 |
| `IDC-07` | **A document-local identifier cited outside its document is qualified** — `<document-id> <identifier>`, never bare | `CHK-05` |
| `IDC-08` | **A new document-local rule prefix is collision-checked before allocation** and the check recorded in `rule_prefix:` front matter | §7.2, `CHK-05` |
| `IDC-09` | **No within-space duplication.** One identifier, one row, per space per file | `CHK-04` |
| `IDC-10` | **No digit-suffixed module codes.** `SRM2` is a registered, closed one-off | `CHK-03` |
| `IDC-11` | **A document code is unique across the workspace**, not across a repository | `CHK-05` |
| `IDC-12` | **Every space carries a registration state** (§3.5), and a frozen space accepts no allocation | §9 |
| `IDC-13` | **Sequential allocation is forbidden where concurrent authoring is possible.** Use a key derived from something already uniquely allocated | §5.8.2 |
| `IDC-14` | **Where two spaces share a lexical form, the digit count disambiguates and is mandatory** — `P0`–`P3` priority, `P01`–`P12` portal | `CHK-02` |

> **`IDC-13` is the rule this repository most needed and least had.** Nine identifier events, all
> of them sequential-allocation races. A category-keyed, wave-keyed or module-keyed identifier
> cannot collide under concurrent authoring because the key was already uniquely allocated by
> somebody else. It costs nothing and removes an entire failure class.

---

## 7. Allocation Procedure

### 7.1 Allocating an identifier in an existing space

| Step | Action | Evidence produced |
|---:|---|---|
| 1 | Look the space up in §5. **If its state is Frozen, stop** — raise the thaw condition in §9 instead | — |
| 2 | Open the register named in the **Authority** column | — |
| 3 | Take the next identifier the register offers. **Never** the highest on disk + 1 — retired identifiers are not visible that way | — |
| 4 | Write the register row **before** the first use | The register row |
| 5 | Record the allocation in the allocation log (§7.4) | Log entry |

### 7.2 Allocating a new document-local rule prefix — `IDC-08`

The procedure ten documents already follow, stated:

```bash
# 1. Choose a candidate three-letter prefix. 2. Prove it is free:
grep -rhoE '\bCAND-[0-9]{1,4}\b' --include='*.md' . | wc -l      # must return 0
# 3. If non-zero, choose another and record why the candidate was rejected.
```

```yaml
# 4. Record the result in front matter, with the file count and timestamp:
rule_prefix: IDC — verified to return zero occurrences in identifier form across all 782
  markdown files of the workspace before allocation, at 2026-08-19 02:41 (+06)
```

> **The file count and the timestamp are both mandatory.** A collision check against an estate
> that gained ten files in thirty-one minutes (§4.3) is only meaningful with a stated denominator
> and a stated moment. This is `RG-08` applied to allocation.

### 7.3 Creating a new identifier space

Rare, and deliberately harder:

| Step | Action | Approval |
|---:|---|---|
| 1 | Establish the space does not already exist — §5, plus the §7.2 check | Author |
| 2 | Establish it is not a document-local class in disguise (§5.9). **Most candidates are** | Author |
| 3 | Name the allocating authority, and satisfy `IDC-02`: is that document's *primary purpose* this register? | Enterprise Architecture |
| 4 | Write the §5 row in full — form, scope, authority, permanence, state | Enterprise Architecture |
| 5 | Add the form to `CHK-01`'s pattern set | QA Lead |
| 6 | Raise a Change Request against `PGD-000` if the space is programme-wide | **CTO** |

### 7.4 The allocation log

`IDC-03` needs a record. Until `RR-006`'s generated index exists, the log is a table appended to
the allocating authority's register, with five columns: **identifier · date · allocated by · what
it denotes · the check output**. `RR-006` §5 specifies the generated replacement.

---

## 8. Measured Defects

Eleven. Five are new — they appear in no prior audit and were found by enumerating the space as a
space, the same method that produced `RF-001`'s four.

| # | Defect | Severity | New? | Owner | Fix |
|---|---|:--:|:--:|---|---|
| `IDC-F-01` | Identifier population is **≈20× the register's figure** — 1,094 prefixes / 18,630 tokens against ~46 named | **High** | **New** | Enterprise Architecture | §5 register; `RR-006` generation |
| `IDC-F-02` | **`AUT-` declared twice with different form, scope and authority** — 1,438 vs 60 identifiers | **High** | **New** | Enterprise Architecture | `RR-002-D-01`; correct `00-01` §3 |
| `IDC-F-03` | Every measured gap is **larger than the finding that recorded it** — five independent measurements, same direction | **High** | **New** | PMO | §9 freeze |
| `IDC-F-04` | **Three of `00-01` §3's sixteen declared spaces are dead**, and it omits the two carrying 2,527 identifiers | **High** | **New** | Enterprise Architecture | `RR-002-D-04`; restate `00-01` §3 |
| `IDC-F-05` | **Audit identifier space has no allocating authority**; nine events; a `\d{3}` sweep misses 5 of 14 | **High** | Partly — `PGD-000` records the events, not the cause | PMO | `RR-002-D-05` |
| `IDC-F-06` | **Duplicate front-matter `id`: `FIX-ERP2-006`** held by a live audit report and a superseded pillar file | **Medium** | **New** | Enterprise Architecture | §8.2 |
| `IDC-F-07` | `SOD-` closed in the content estate, **still open in the engineering estate** — 12 registered against 61 in use | **High** | Partly | `SC-004` | Thaw `TH-03` |
| `IDC-F-08` | `FR-SLS-` (30) and `FR-BFO-` (3) are **live identifiers whose only home is superseded** | Medium | No — `GL-04` | `RQ-004` | §8.4 retirement rows |
| `IDC-F-09` | `M68` and `M99` **in use in `BE-005` as illustrative values** with no reserved-unallocated status | Low | **New** | Enterprise Architecture | §8.6 |
| `IDC-F-10` | `POR` has **358 requirements and no business-rule family** | Medium | No — `GL-02` | `UX-002` / `RQ-009` | Backlog |
| `IDC-F-11` | This repository has committed **three identifier events** while naming collisions as the estate's largest defect class | Medium | No — `PGD-A2-19` | Enterprise Architecture | §7, `IDC-13` |

### 8.1 Severity basis

**High** = a build, test or contract artefact can be produced that is wrong and looks right.
**Medium** = a reader is misled but a mechanical check would catch it.
**Low** = a latent trap with no current instance.

### 8.2 `IDC-F-06` — the duplicate front-matter id, in full

`GV-011` §4.3 found three identifier schemes for the same documents and recorded it as
`PGD-A2-17`. Enumerating the `id:` key across the module repository at 2026-08-19 02:41 adds two
facts it did not have:

| Fact | Value |
|---|---|
| `id:` keys in `1000fix_ERP_Module` | **123** — one per file |
| Distinct values | **122** |
| **Duplicate** | **`FIX-ERP2-006`** |
| Held by | `00_Governance_and_Charter/00-06_Documentation_Audit_Report.md` — **live, authoritative** |
| And by | `99_Reference/_Superseded/SUPERSEDED_Pillar_B_Customer_Commercial_Revenue.md` — **superseded** |
| Sub-forms in the space | **six** — `-nnn`, `-nn-nn`, `-CAT-<X>`, `-CAT-<X>-AUDIT`, `-M<nn>`/`-P<nn>`, `-README`/`-STRUCT` |
| Numeric gaps | `004` and `021` are unallocated |

> **A live document and a superseded document share an identifier.** Any tool that resolves
> `FIX-ERP2-006` gets two answers, one of which is explicitly *not authoritative*. It is the exact
> failure `IDC-05` forbids, in the repository whose audits found the defect class.
>
> **Remediation `RR-002-D-06`: the `FIX-ERP2-*` space is frozen and scheduled for retirement.** It
> serves no purpose the file name does not serve better, it has six sub-forms and no authority, and
> `GV-011` §4.3 already records that a reader given `FIX-ERP2-017` cannot locate the file. The
> retirement is executed by `RR-003`, which sets the front-matter schema. Until then no new
> `FIX-ERP2-*` value is allocated, and the superseded file's row is corrected first, because a
> superseded document holding a live identifier is the more dangerous half.

### 8.3 Cross-repository prefix reuse

**109 prefixes appear in three or more repositories**; **15 in all five**. Reuse is not itself a
defect — `NFR-018` *should* mean the same thing everywhere. It is a defect when the same prefix
denotes different classes of thing:

| Prefix | Repository A | Repository B | Same thing? |
|---|---|---|:--:|
| `DM-nn` | `05-02` data-model standard | `project_content` `DM-001`…`DM-014` migration content files | **No** — `RF-001` records it; digit count disambiguates |
| `C-nn` | `00-06` critical audit finding | `project_content` finding series | Different documents, same class — harmless |
| `A-nn` | `00-07` finding | Warehouse bin location `A-04-C-12` | **No** — but the bin form is not citable, so harmless |
| `CD-nnn` / `CD-nn` | Custom development | `RF-006` **content decision** | **No** — see below |

> **`CD-` is the live one.** `RF-006` §4.2 allocated `CD-nn` for *content decisions* to escape the
> `D-nn` collision `GL-03` found — and in doing so landed on the programme's custom-development
> space. Two digits vs three is the only difference. **`RR-002-D-08`: `RF-006`'s content-decision
> space is asked to re-base to `CDN-nn`**, owner Programme Content Lead, raised as `RR-002-Q-04`.
> Recorded rather than imposed: this document has no authority over `project_content`, and saying
> so is the point of `IDC-01`.

### 8.4 Retirement rows — `IDC-06`

Live identifiers whose referent is superseded. They resolve here.

| Identifier(s) | Count | Status | Resolves to |
|---|---:|---|---|
| `FR-SLS-001`…`FR-SLS-030` | 30 | **Retired 2026-08-19** | v1.0 pillar architecture, replaced by v2.0 modules. Live only in `05-01` and `SUPERSEDED_Pillar_B`. Superseded by `FR-QTE-*` and `FR-PRC-*`; the mapping is `RQ-004`'s |
| `FR-BFO-001`…`FR-BFO-003` | 3 | **Retired 2026-08-18** | `M04` reverted from code `BFO` to `FRD` under audit `C-03`. Superseded by `FR-FRD-*` |
| `AUT-001`…`AUT-060` | 60 | **Retired 2026-08-19** | Legacy programme-wide automation form. See the owning module's §11 for the `AUT-<CODE>-nn` identifier |
| `E-<MOD>-nn`, `FN-<MOD>-nnn`, `EVT-<domain>.<verb>` | 3 forms | **Retired 2026-08-19** | Declared in `00-01` §3, never adopted. Entities are `fix.<model>` (`DA-001`); events are `<domain>.<verb>.v<n>` (`IN-003`) |
| `R60` | 1 | **Retired 2026-08-19** | Duplicate identity for `R32` GRC / Internal Audit (`H2-07`). Access-control rules citing `R60` must be restated to `R32` before any permission test is written |

### 8.5 Audit identifier mapping — `RR-002-D-05`

The nine sequential identifiers retire in place and resolve to their category-keyed equivalents.

| Sequential (retired) | Category-keyed (canonical) | Category |
|---|---|---|
| `PGD-AUDIT-001` | `PGD-AUDIT-REG-01` | Register integrity — not a category audit |
| `PGD-AUDIT-002` | `PGD-AUDIT-CAT-00` | 00 Governance |
| `PGD-AUDIT-003` | `PGD-AUDIT-CAT-02` | 02 Architecture |
| `PGD-AUDIT-004` | `PGD-AUDIT-CAT-01` | 01 Requirements |
| `PGD-AUDIT-005` | `PGD-AUDIT-CAT-03` | 03 Data |
| `PGD-AUDIT-006` | `PGD-AUDIT-CAT-06` | 06 Experience |
| `PGD-AUDIT-007` | `PGD-AUDIT-CAT-04` | 04 Integration |
| `PGD-AUDIT-008` | `PGD-AUDIT-CAT-05` | 05 Security |
| `PGD-AUDIT-009` | `PGD-AUDIT-CAT-10` | 10 Infrastructure |

> **Files are not renamed.** `IDC-04` makes the identifier permanent, and `GV-011` §9.2 governs
> file naming. This table is the resolution mechanism; renaming nine files would break every
> citation in fourteen audit reports to fix a cosmetic inconsistency. **The canonical form governs
> new audits only** — which is what makes `IDC-13` effective from today rather than retroactively.

### 8.6 Reserved-unallocated

| Identifier | Where it appears | Status |
|---|---|---|
| `M68` | `BE-005`, as a hypothetical future module | **Reserved-unallocated.** Not a module. `02-02` allocates if ever needed |
| `M99` | `BE-005`, inside `CD-M99-42`, explicitly *"well-formed and denotes nothing"* | **Reserved-unallocated — permanently.** `M99` is the canonical *invalid* module for test fixtures |
| `P13`, `TR-025`, `BN-019`, `DM-015`, `DM-016`, `SP-035` | Cited as though registered | **Proposed, unallocated.** `RF-007` §4.3 holds the content five; `P13` is `04-00`'s |

### 8.7 This repository's own record

Recorded because `PGD-000` §2.3 identifies the self-critical audit culture as a genuine asset, and
because a standard that exempts its author is not a standard.

| # | Event | Recorded as | Status |
|---|---|---|---|
| 1 | `RF` code collision with `project_content` category 99 | Category overview | Resolved by adopting `RR` — before this document existed, by luck |
| 2 | Bare `D-01` in the authoring template, which across 140 documents would have produced 140 decisions with one identifier | `PGD-A2-03` | Closed by `DL-06`, generalised here as `IDC-07` |
| 3 | Duplicate `PGD-AUDIT-002`, and `PGD-AUDIT-009` claimed by two categories four minutes apart | `PGD-A2-19`, `CHA-12` | Closed by `RR-002-D-05` and `IDC-13` |

---

## 9. The Freeze and Thaw Plan

`IDC-12`. Nine spaces are frozen. **A freeze is not a punishment; it is the recognition that
allocating into a space whose register is 3,304 identifiers behind produces an identifier nobody
can resolve.**

| Space | Why frozen | Thaw condition | Owner | Target |
|---|---|---|---|---|
| `FR-<CODE>-nnn` | 3,504 counted, 200 registered; denominator contested | `TH-01` — `05-01` restated as a register, not a summary; `RQ-004` §5.1's denominator adopted | Enterprise Architecture | W1 |
| `KPI-nnn` | 301 counted, 95 registered | `TH-02` — `06-02` KPI register regenerated; `BM-002` baselines measured | CFO / PMO | **Now** |
| `SOD-nn` | 61 in use, 12 registered in `05-04` | `TH-03` — `05-04` §6 adopts `SP-006`'s `SOD-13`…`SOD-60`, or states why not | `SC-004` owner | W1 |
| `R<nn>` | 53 in use, 38 registered; `R60` duplicates `R32` | `TH-04` — `05-04` registers `R39`–`R50`; `R54`/`R57` defined or retired; `R60` retired | `SC-004` owner | W1 |
| `NFR-nnn` | `NFR-088`…`092` each used twice | `TH-05` — `RQ-006` rules the five contested identifiers | Enterprise Architecture | W1 |
| `CD-nnn` | 261 counted, 199 registered; two incompatible registers | `TH-06` — `BE-005` reconciliation carries an approval record | Build Lead | **Now** |
| `FIX-ERP2-*` | Six sub-forms, one duplicate, no authority | `TH-07` — `RR-003` sets the front-matter schema and the space retires | Enterprise Architecture | W1 |
| `PGD-AUDIT-<nnn>` | No authority; nine events | `TH-08` — **discharged at this issue** by `RR-002-D-05` | PMO | ✔ Done |
| `AUT-nnn` (legacy) | Superseded by `AUT-<CODE>-nn` | `TH-09` — **discharged at this issue** by `RR-002-D-01`; retired | Enterprise Architecture | ✔ Done |

> **Two of nine thaw at this issue**, because their remedy was a ruling and this document could
> take it. **Seven need someone to update a register**, which this document cannot do without
> breaching `IDC-01` — the rule it is asking everyone else to follow. Naming the owner and the
> date is the most a standard may do, and doing more would be the defect.
>
> **The freeze has a cost and it should be stated.** Wave 1 authoring continues; a frozen space
> means an author who needs a new KPI or a new role cannot have one. The escape hatch is
> `RR-002-Q-01`: a **provisional identifier** in the form `<SPACE>-PROV-<nn>`, allocated by the
> PMO, valid for one wave, and mechanically detectable so none survives a gate. That needs a
> decision this document cannot take.

---

## 10. Enforcement

Six checks. Each is runnable today against markdown, and each survives into CI when
`PE-004`'s pipeline exists.

| # | Check | What it detects | Gate |
|---|---|---|---|
| `CHK-01` | **Form conformance** — every identifier-shaped token matches a §5 form | Malformed identifiers; new undeclared spaces | Warn at commit, fail at gate |
| `CHK-02` | **Digit-count disambiguation** — `P0`–`P3` vs `P01`–`P12`, `DM-nn` vs `DM-nnn` | `IDC-14` breaches | Fail |
| `CHK-03` | **Module-code source** — every `<CODE>` in `FR-`/`BRU-`/`AUT-` appears as a `module_code:` in some module file | Invented codes; `SRM2`-class drift | Fail |
| `CHK-04` | **Within-space uniqueness** — no identifier appears twice as a table-row key in one file | `EO-02`, `AP-02`, `IDC-F-06` | Fail |
| `CHK-05` | **Resolvability** — every cited identifier resolves to a register row or a retirement row | Orphans: `R54`, `SOD-31`, `FR-SLS-*` | Warn, then fail at W1 gate |
| `CHK-06` | **Enumeration freshness** — no document quotes an identifier count older than its own `enumeration_timestamp` | The §4.3 movement problem | Warn |

```bash
# CHK-04 — within-space uniqueness, the highest-yield check. Finds IDC-F-06 in one pass.
for f in $(find . -name '*.md'); do
  grep -oE '^\| *`?[A-Z]{1,6}(-[A-Z]{2,4})?-[0-9]{1,4}`? *\|' "$f" \
    | tr -d '|` ' | sort | uniq -d | sed "s|^|$f: DUPLICATE |"
done

# CHK-03 — every module code used must be declared. Returns the invented ones.
comm -23 \
  <(grep -rhoE '\bFR-[A-Z]{3}[0-9]?-[0-9]{3}\b' --include='*.md' . | sed -E 's/^FR-([A-Z]{3}[0-9]?)-.*/\1/' | sort -u) \
  <(grep -h '^module_code:' 1000fix_ERP_Module/03_Modules/*/M*.md | sed 's/module_code: *//' | tr -d '`' | sort -u)

# CHK-01 — spaces in use that §5 does not declare. Run it; the output is the backlog.
grep -rhoE '\b[A-Z]{1,6}(-[A-Z]{2,4})?-[0-9]{2,4}\b' --include='*.md' . \
  | sed -E 's/-[0-9]+$//' | sort | uniq -c | sort -rn
```

> **`CHK-05` is the one that matters and the one that cannot be switched on yet.** It needs a
> resolvable register per space, which is what §9's thaw conditions produce. It is specified here so
> that "make the identifiers resolvable" has a definition of done, and it is `RR-006`'s primary
> consumer.

---

## 11. Decisions Recorded

`DL-06` / `IDC-07`: identifiers take the form `RR-002-D-nn`.

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `RR-002-D-01` | Which `AUT-` convention governs | (a) `AUT-nnn` programme-wide per `00-01` §3; (b) `AUT-<CODE>-nn` module-local per `_MODULE_TEMPLATE`; (c) keep both, disambiguate by form | **(b)** | 1,438 identifiers against 60; module-locality is correct for a rule firing inside one module | 60 legacy identifiers retired in place; `00-01` §3 must be corrected |
| `RR-002-D-02` | `SRM2` — correct or ratify | (a) reallocate `M42` to a fresh code, renaming 34 identifiers; (b) widen the form and close the exception | **(b)** | `IDC-04` permanence outweighs cosmetic regularity; renaming breaks live citations | Form is `[A-Z]{3}[0-9]?`; `IDC-10` forbids any further instance |
| `RR-002-D-03` | `CD-` allocating authority | (a) `02-05` as declared; (b) `BE-005`; (c) a new register | **(b)** | `IDC-02` — `BE-005` exists to be the CD register; `02-05` acquired it incidentally and produced `H-03` | `00-01` §3 and `_MODULE_TEMPLATE` §0 must be corrected; space stays frozen |
| `RR-002-D-04` | The three dead spaces in `00-01` §3 | (a) adopt them and migrate 2,527 identifiers; (b) retire them and register what is actually used | **(b)** | Nothing follows them; migration cost is enormous and the benefit is zero | `fix.<model>` and `<domain>.<verb>.v<n>` registered; `00-01` §3 restated |
| `RR-002-D-05` | Audit identifier form | (a) sequential with an allocating authority; (b) category-keyed; (c) date-keyed | **(b)** | Collision-free *by construction* under concurrent authoring — `IDC-13` | Nine sequential identifiers retired in place (§8.5); files not renamed |
| `RR-002-D-06` | `FIX-ERP2-*` | (a) repair — assign an authority, fix the duplicate, regularise six sub-forms; (b) freeze and retire | **(b)** | It duplicates the file name, resolves for nobody (`GV-011` §4.3), and has a live/superseded duplicate | `RR-003` sets the replacement front-matter schema |
| `RR-002-D-07` | `RG-08` timestamped enumeration | (a) recommend again; (b) adopt it unilaterally for this category and demonstrate it | **(b)** | Nine recommendations produced no ratification. This document times every count and §4.3 shows why | Recommended for ratification a **tenth** time; applied here regardless |
| `RR-002-D-08` | `RF-006`'s `CD-nn` content-decision space | (a) leave it; (b) ask for re-basing to `CDN-nn` | **(b)**, as a request | Two-digit vs three-digit is too thin a distinction for a space that gates build tickets | `RR-002-Q-04`; this document has no authority over `project_content` and does not pretend to |

---

## 12. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `RR-002-Q-01` | Is a **provisional identifier** (`<SPACE>-PROV-<nn>`, PMO-allocated, one wave, mechanically detectable) accepted as the escape hatch for the nine frozen spaces? | **CTO** | **Now** | Wave 1 authoring in any frozen space |
| `RR-002-Q-02` | Who restates `00-01` §3 — three dead spaces, two missing spaces, a contradicted `AUT-` row, 30 of 72 module codes, and a superseded `CD-` authority? | Enterprise Architecture | W1 | `CHK-01`, `CHK-03` |
| `RR-002-Q-03` | Does `05-04` adopt `SP-006`'s `SOD-13`…`SOD-60`, or does the engineering estate keep a separate SOD register? A single register is assumed here | `SC-004` owner | W1 | `TH-03`, every permission test |
| `RR-002-Q-04` | Will `project_content` re-base `RF-006`'s content-decision space from `CD-nn` to `CDN-nn`? | Programme Content Lead | W1 | Nothing hard; prevents a class |
| `RR-002-Q-05` | `R54` and `R57` are cited and undefined. Define them, or retire the citations? Retirement is assumed pending a decision | `SC-004` owner | W1 | `TH-04` |
| `RR-002-Q-06` | Which body ratifies `IDC-01`…`IDC-14`? `PGD-A1-09` records that none exists | **Board** | **Now** | Every ✅ in this estate (`PGD-A2-25`) |

> Six questions, six named owners, six dates — per the template's rule that an open question
> without an owner and a date is an unrecorded risk. `RR-002-Q-01` and `RR-002-Q-06` are escalated
> to `GV-005` RAID at issue.

---

## 13. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | Every identifier space in use in the workspace either appears in §5 or is a §5.9 document-local class | `CHK-01` output reconciled against §5 — **residual work, see below** |
| `AC-02` | Every §5 row states form, scope, allocating authority, permanence and state — all five | Row inspection; **met at issue** |
| `AC-03` | Every space named by `GV-011` §4.4's interim table appears here with a state | 14 of 14 present; **met at issue** |
| `AC-04` | Each of the eight findings in `_CATEGORY_OVERVIEW.md` is addressed in §2.3 with a named mechanism | 8 of 8; **met at issue** |
| `AC-05` | Every figure carries the enumeration timestamp and a reproducible command | §4.1; **met at issue** |
| `AC-06` | The six checks are runnable as written | `CHK-01`, `CHK-03`, `CHK-04` verified during authoring; `CHK-02`, `CHK-05`, `CHK-06` specified, `CHK-05` blocked on §9 |
| `AC-07` | Every frozen space has a named thaw condition, owner and target | 9 of 9; **met at issue** |
| `AC-08` | This document's own rule prefix was collision-checked before allocation | `rule_prefix:` front matter; **met at issue** |
| `AC-09` | No identifier is allocated by this document outside its own document-local spaces | `IDC` and `RR-002-D-nn` only; **met at issue** |

**Definition of done.** Complete when every criterion above is met, `PGD-000`'s `RR-002` row is
updated with a fresh enumeration timestamp, and the approver has signed. `AC-01` and `AC-06` carry
residual work: `CHK-01`'s full reconciliation is `RR-006`'s output, and `CHK-05` cannot pass until
§9's thaw conditions complete. Both are stated rather than claimed, per `PG-M2`.

---

## 14. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `PGD-000` | Registers this document; allocates the `RR` code space |
| Upstream | `GV-011` §4.4 | Declares its identifier table interim pending this document. **Superseded by §5** |
| Upstream | `GV-003` `DL-06` | The decision-space rule generalised here as `IDC-07` |
| Upstream | `RF-001` §4.2–4.3 | The content estate's prefix register and four defects. Adopted, extended, not restated |
| Downstream | `RR-001` | Consumes §5 to state what each identifier *means* |
| Downstream | `RR-003` | Consumes `IDC-08` and `RR-002-D-06`; sets `rule_prefix:` and retires `FIX-ERP2-*` |
| Downstream | `RR-004` | Every source in the evidence register is cited by identifier under these rules |
| Downstream | `RR-006` | **The mechanical form of this document** — `CHK-05` is its primary consumer |
| Downstream | `BE-005` | Receives `CD-` allocating authority (`RR-002-D-03`) |
| Downstream | `SC-004` | Receives `R<nn>` and `SOD-nn` thaw conditions `TH-03`, `TH-04` |
| Downstream | `RQ-004`, `RQ-006` | Receive `FR-` and `NFR-` thaw conditions `TH-01`, `TH-05` |
| Downstream | `PE-004` | Hosts `CHK-01`…`CHK-06` as pipeline gates |
| Lateral | `../../1000fix_ERP_Module/00_Governance_and_Charter/00-01_Master_Index_and_Document_Map.md` §3 | Restated by `RR-002-Q-02` |
| Lateral | `../../1000fix_ERP_Module/03_Modules/_MODULE_TEMPLATE.md` §0 | `AUT-` and `CD-` rows corrected by `RR-002-D-01`, `-D-03` |
| Lateral | `../../project_content/00_Content_Governance_and_Standards/CG-005_*.md` | Retains authority over the 21 content codes; registered in §5.5 |

---

## 15. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` ·
`./_CATEGORY_OVERVIEW.md` · `./RR-001_Glossary_and_Acronym_Register.md` ·
`./RR-003_Document_Standards_and_Template_Library.md` ·
`./RR-004_Source_Document_Index_and_Evidence_Register.md` ·
`./RR-005_Standards_and_Regulatory_Currency_Register.md` ·
`./RR-006_Master_Cross_Reference_and_Traceability_Index.md` ·
`../00_Programme_Governance_and_Control/GV-003_Decision_Log_and_Change_Control_Procedure.md` ·
`../00_Programme_Governance_and_Control/GV-005_RAID_Register.md` ·
`../00_Programme_Governance_and_Control/GV-011_Documentation_Control_and_Configuration_Management_Plan.md` ·
`../01_Requirements_Engineering/RQ-004_Requirements_Traceability_Matrix.md` ·
`../04_Integration_and_API_Engineering/IN-003_Domain_Event_Catalogue_and_Schema_Registry.md` ·
`../05_Security_Privacy_and_Compliance/SC-004_Identity_Authentication_and_Authorisation_Design.md` ·
`../07_Build_Engineering_and_Development_Standards/BE-005_Custom_Development_CD_Master_Register.md` ·
`../10_Infrastructure_DevOps_and_Environments/PE-004_CI_CD_Pipeline_Design_Specification.md` ·
`../_AUDIT/PGD-AUDIT-001_Register_Integrity_Audit.md` ·
`../_AUDIT/PGD-AUDIT-002_Category_00_Governance_Audit.md`

**Workspace**
`../../1000fix_ERP_Module/00_Governance_and_Charter/00-01_Master_Index_and_Document_Map.md` §3 ·
`../../1000fix_ERP_Module/00_Governance_and_Charter/00-06_Documentation_Audit_Report.md` ·
`../../1000fix_ERP_Module/00_Governance_and_Charter/00-07_Category_H_Audit_and_Repository_Integrity_Report.md` ·
`../../1000fix_ERP_Module/02_Architecture/02-02_Module_Catalogue_Master_Register.md` ·
`../../1000fix_ERP_Module/03_Modules/_MODULE_TEMPLATE.md` §0 ·
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md` … `05-06_NonFunctional_Requirements_and_Standards.md` ·
`../../1000fix_ERP_Module/FOLDER_STRUCTURE.md` §5 ·
`../../project_content/99_Reference_and_Registers/RF-001_ERP_Glossary_and_Acronym_Register.md` §4.2–4.3 ·
`../../project_content/00_Content_Governance_and_Standards/CG-005_*.md`

**External standards**

| Standard | Title | Status | `verified_on` |
|---|---|---|---|
| ISO/IEC 11179-1:2023 | Metadata registries — Part 1: Framework | Current | 2026-08-19 |
| ISO/IEC 11179-5:2015 | Part 5: Naming principles | Current | 2026-08-19 |
| ISO/IEC 11179-6:2023 | Part 6: Registration | Current | 2026-08-19 |
| ISO/IEC 11179-31:2023, -32:2023 | Parts 31/32 | Current — cited by `DA-002`, not applied here | 2026-08-19 |
| ISO 10007:2017 | Quality management — Configuration management | Current | 2026-08-19 |
| ISO 704:2022 | Terminology work — Principles and methods | Current — governs `RR-001` | 2026-08-19 |

> Currency of every standard above is registered in `RR-005`; this table is the local copy and the
> register is the authority (`IDC-02`).

---

## 16. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-19 | Enterprise Architecture | Initial issue. Supersedes `GV-011` §4.4 interim table. Eleven measured defects, five new. Eight decisions, nine spaces frozen, six checks, fourteen rules | *(unsigned — no constituted body, `PGD-A1-09`)* |

---

*`RR-002` · Category 99 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
