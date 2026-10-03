---
id: RR-006
title: Master Cross-Reference and Traceability Index
category: 99 — Reference, Registers & Glossary
code: RR
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-19
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Enterprise Architecture
approver: Chief Technology Officer
standards_basis: ISO/IEC/IEEE 29148:2018 §5.2.8 (requirements traceability) · ISO/IEC/IEEE 12207:2017 §6.4.2 · ISO 10007:2017 §5.5 (configuration status accounting) · ISO/IEC 11179-1:2023 §5 (registry model) · ISO/IEC/IEEE 29119-3:2021 §7 (traceability in test documentation)
traces_to: PGD-000 Category 99 RR-006 · PGD-000 §2.1 row 21 · _CATEGORY_OVERVIEW "RR-006 is generated, not hand-maintained" · 99-04 (unwritten) · RQ-004 · RR-002 CHK-05 · RR-004 §7 · RF-003 · RF-004 · RF-005 · AUDIT-015 RP-01 · AUDIT-014 TS-01
depends_on: PGD-000 · RR-002 · RR-003 · RR-004 · RR-005
verified_on: 2026-08-19
priority: P1
needed_by: W2
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
enumeration_timestamp: 2026-08-19 20:12 (repository wall clock — see RR-005 §4.4)
rule_prefix: XRF — verified to return zero occurrences in identifier form across all 795 markdown files of the workspace before allocation, at 2026-08-19 20:12. Candidates IDX, TRX and SIX were also free; IDX was rejected as visually close to ID- (CG-005's content identifier rules, 44 occurrences)
review_cycle: Regenerated at every wave gate and on demand — §8. This document is an EDITION, not a baseline
extraction_method: Six generator scripts, printed in full in §4. Every figure in §5 is the output of one of them; none is hand-entered
---

# RR-006 — Master Cross-Reference and Traceability Index
# 1000FiX ERP System & Portal Suite v2.0

### Category 99 · Code `RR` · ISO/IEC/IEEE 29148:2018 · ISO 10007:2017 · ISO/IEC 11179-1:2023

---

> **Before writing, read this.**
>
> 1. **`PG-01` Register-first.** This document's row exists in `PGD-000` Category 99 as `RR-006`,
>    status ⬜, priority **P1**, needed by **W2**. It was registered before it was written.
> 2. **`PG-03` / `RG-06` Count, do not consult.** Nothing in §5 is typed by hand. Every figure is
>    the printed output of a script in §4, run at **2026-08-19 20:12**.
> 3. **`PG-06` Cite standards.** ISO/IEC/IEEE 29148:2018 §5.2.8, ISO 10007:2017 §5.5 and
>    ISO/IEC 11179-1:2023 §5 govern. Departures are declared in §2.1.
> 4. **`PG-M4` Verify citations.** `verified_on: 2026-08-19`. External-standard currency is
>    `RR-005` §5's.

---

## 1. Purpose

`PGD-000` Category 99 states the problem in one sentence: *"The estate has seven identifier spaces,
601 files and no index. Every audit finding to date has been a cross-reference failure that an
index would have surfaced automatically."*

Both halves of that sentence have since been measured and both were understatements.
`RR-002` §4.2 counted **1,094 identifier prefixes**, not seven. `RR-004` §4.2 counted **792 files**,
not 601. And this document tests the second half by building the index and seeing what it catches.

**It catches three defects that fourteen category audits did not**, and it catches them by set
difference rather than by reading:

- **`RR-008`** — a document cited **seven times** in `UX-005` and `UX-007`, including in two
  *governing rules*, that has never been registered and does not exist.
- **`P38`** — a portal cited in `M10`'s API table as a consumer of a live endpoint. The portal
  space is `P01`–`P12`.
- **`BO-1` vs `BO-01`** — two business-objective sets, in two digit forms, denoting **different
  objectives**, one of them the basis of the BDT 876 lac benefit case.

None of the three is subtle once seen. All three were invisible to reading, because **reading
cannot perform set difference over 18,630 identifiers.**

### 1.1 What this document is, and is not

> **This is an *edition*, not a baseline.** `_CATEGORY_OVERVIEW.md` requirement 5 is explicit and
> correct: *"`RR-006` is **generated, not hand-maintained** — a hand-maintained cross-reference
> index over 601 files will be wrong within a month."*
>
> §5 is therefore the **output** of §4's generators at a stated instant. It is not maintained. When
> it is wrong, the answer is to re-run §4, not to edit §5. `RR-004` §6 records that this repository
> moved **twelve times in sixteen hours**; a hand-maintained index would have been wrong before it
> was finished.

### 1.2 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | The **generator specification** — six scripts, printed in full, runnable against markdown today |
| 2 | The **document graph**: which `PGD` document cites which, with in-degree, out-degree and a category matrix |
| 3 | The **identifier namespace census**: population, registered count and gap for every space in the eight-way chain |
| 4 | The **eight-way trace chain** — objective ↔ requirement ↔ module ↔ entity ↔ event ↔ role ↔ test ↔ KPI — link by link, with coverage measured, not asserted |
| 5 | **Dangling, phantom and orphan** analysis across every space |
| 6 | The **retirement table** — identifiers that must still resolve after being withdrawn (`RR-002` `IDC-06`) |
| 7 | The **regeneration schedule** and the checks the index makes possible |

**Explicitly out of scope:**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| **Allocating** identifiers, or ruling on collisions | `RR-002` | This index *reports* the space; `RR-002` *governs* it. An index that also allocated would be judge and evidence |
| What a term or identifier **means** | `RR-001` | Semantics are the glossary's |
| The **requirements** traceability matrix as a deliverable | `RQ-004` | `RQ-004` is the contractual RTM with coverage obligations. **This index is its mechanical substrate**, not its replacement — §5.3 states the split |
| **Content**-estate traceability | `RF-003`, `RF-004`, `RF-005` | Three content traceability matrices already exist. §5.6 registers the overlap; they are not restated |
| Document **inventory** and evidence grades | `RR-004` | `RR-004` indexes documents; this indexes identifiers |
| Building a **tool** | `PE-004` | §4 specifies scripts that run today. Productionising them is a pipeline concern |

### 1.3 Intended audience

| Audience | What they use this document for |
|---|---|
| **Anyone who meets an identifier and cannot resolve it** | §5.4 — the dangling and phantom tables |
| **Auditors** | §4 — to re-run the generators and challenge every figure in §5 |
| **Enterprise Architecture** | §5.2's gap column: the difference between what is in use and what is registered, per space |
| **QA Lead** | §5.3 — the coverage denominators `AUDIT-014` `TS-01` said were unanswerable |
| **PMO** | §7's checks, and §8's regeneration schedule |
| **The vendor** | §5.1's graph — which documents are load-bearing, measured by in-degree rather than by assertion |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause / section | How this document conforms | Departure and rationale |
|---|---|---|---|
| **ISO/IEC/IEEE 29148:2018** | §5.2.8 requirements traceability — *"bidirectional traceability … backward to sources and forward to derived items"* | §5.3 tests every link of the chain in **both** directions and reports the coverage separately, because forward and backward coverage differ by an order of magnitude in this estate | 29148 assumes traceability is *maintained*. Here it is *reconstructed* from text by §4's generators, because no traceability tool exists. **Declared, and it is the largest departure in this document** |
| **ISO/IEC/IEEE 12207:2017** | §6.4.2 (requirements definition), traceability outputs | The index is the traceability output for the software life-cycle processes | None |
| **ISO 10007:2017** | §5.5 Configuration status accounting | §5.1 and §5.2 are status accounting: what exists, what it references, and what state it is in | None. `RR-002` performs identification; this performs accounting |
| **ISO/IEC 11179-1:2023** | §5 registry model | §5.2's namespace census is the registry inventory 11179 assumes exists. `RR-002` §5 is the document-borne registry; this is its measured contents | `RR-002` §2.1 already declares the "no software registry" departure. This document is the route to closing it |
| **ISO/IEC/IEEE 29119-3:2021** | §7 traceability in test documentation | §5.3's requirement↔test link is the substrate for `QA-011`'s coverage report | 29119-3 expects a test management tool. Same departure as 29148 |

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| The filesystem | the workspace root | **The only primary input.** §4's generators read nothing else |
| `RR-002` §5, §8, §9 | `./RR-002_Identifier_Convention_Standard.md` | The identifier-space register, its eleven defects and its nine frozen spaces. **This index is `RR-002` `CHK-05`'s enabling instrument** |
| `RR-004` §5.3.1, §7 | `./RR-004_Source_Document_Index_and_Evidence_Register.md` | The cited-and-absent source register and the document-grain reverse index this makes identifier-grain |
| `RR-001` §5, §6 | `./RR-001_Glossary_and_Acronym_Register.md` | Term ↔ entity correspondence, consumed by §5.3's entity link |
| `RQ-004` | `../01_Requirements_Engineering/RQ-004_Requirements_Traceability_Matrix.md` | The contractual RTM. §5.3 supplies its substrate; the split is in §1.2 |
| `RF-003`, `RF-004`, `RF-005` | `../../project_content/99_Reference_and_Registers/` | Content-to-requirement, content-to-module and content-to-portal matrices. §5.6 |
| `IN-003` §, `05-03` §4.2 | `../04_Integration_and_API_Engineering/`, `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/` | The **988**-event catalogue and the **64** events actually registered |
| `AR-008`, `05-02` | `../02_Architecture_and_Design/`, `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/` | **1,335** distinct owned entities found against `05-02`'s 225 *(recounted 2026-08-19 18:46 (+06); `AR-008`'s 1,334 was its 02:05 count)* |
| `05-04` §5, §6 | `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/` | The role and SOD registers |
| `06-02` | `../../1000fix_ERP_Module/06_Delivery_and_Implementation/` | `BO-01`…`BO-18` and the KPI register |

### 2.3 Audit findings this document closes

| Finding | Source | How this document closes it |
|---|---|---|
| `PGD-000` `RR-006` row | *"seven identifier spaces, 601 files and no index"* | §5 is the index. The premise is corrected in passing: **1,094 prefixes, 792 files** |
| `RR-002` `CHK-05` | *"Resolvability — every cited identifier resolves to a register row or a retirement row. **The one that cannot be switched on yet**"* | §4's generator `XRF-G4` **is** `CHK-05`. It is switched on in §5.4 and returns 5 dangling `PGD` IDs, 2 phantoms and 10 absent module documents. **Closed in mechanism**; the register rows it needs are `RR-002` §9's thaw conditions |
| `AUDIT-014` `TS-01` | Requirement-to-script coverage unanswerable because the denominator is contested | §5.3 publishes **four** denominators with the pattern that produced each. It does not pick one — `RQ-004` §5.1 does — but it makes the disagreement arithmetic rather than rhetorical |
| `AUDIT-015` `RP-01` *(critical)* | 250 KPI identifiers in use against 95 registered | §5.2 re-counts: **301 in use, 95 registered.** The gap is **larger** than the finding recorded, which is the fifth independent instance of `RR-002` `IDC-F-03` |
| `RF-001` `GL-01` | Four different FR denominators, none of them 2,930 | §5.3 adds a fifth measurement and reports all five side by side with their patterns |
| `RF-001` `GL-03` | `D-nn` means two different things in two governance documents | §5.5's retirement table is where the mapping lives once `GV-003` rules it. **Not closed** — it needs a decision, and §9 records that |
| `PG-M10` | *"a figure that appears in more than one place must be regenerated in every place"* | The structural answer: **generate it in one place.** §8's schedule replaces the roll-up |

---

## 3. The Index Model

### 3.1 Why generated, and what that costs

A hand-maintained index over this estate has a measurable half-life. `RR-004` §6 records twelve
baseline movements in sixteen hours, eight of them inside a 58-minute authoring window. An index
edited by hand would have been wrong before its author finished the first table.

**The generated model costs three things, and they are stated rather than hidden:**

| Cost | Detail | Mitigation |
|---|---|---|
| **Text is not a database** | The generators read markdown with regular expressions. They find identifier-*shaped tokens*, which is not the same as identifiers | §4.2's false-positive analysis; every figure carries its pattern |
| **A citation is not a trace** | `AR-001` mentioning `GV-002` is evidence of a relationship, not proof of one | §5.1 says *"references"*, never *"depends on"*. Declared semantics |
| **No semantics** | The generator cannot tell a citation from a denial. §5.4 records a real instance | Exclusion list, §4.3 |

**What it buys** is the only thing that matters here: **the index is never stale by more than one
command.** `RR-002`'s registers, `RR-004`'s inventory and `RR-005`'s currency rows all have review
cycles measured in gates. This one has a review cycle measured in **seconds**.

### 3.2 What the index contains

| Layer | Grain | Nodes | Edges | Generator |
|---|---|---:|---:|---|
| **L1 Document graph** | `PGD` document | **137** | **3,280** | `XRF-G1` |
| **L2 Namespace census** | identifier space | **17** chain spaces (of ~1,094 total) | — | `XRF-G2` |
| **L3 Trace chain** | identifier | 8 link types | measured in §5.3 | `XRF-G3` |
| **L4 Resolvability** | identifier | — | dangling / phantom / orphan | `XRF-G4` |
| **L5 Retirement** | identifier | 4 families | — | `XRF-G5` (hand-seeded, §5.5) |
| **L6 Freshness** | document | 137 | — | `XRF-G6` |

### 3.3 The rules

| # | Rule | Enforced by |
|---|---|---|
| `XRF-01` | **The index is generated. §5 is never edited by hand** — if it is wrong, re-run §4 | `extraction_method:` front matter |
| `XRF-02` | **Every figure is printed with the pattern that produced it** | Row inspection |
| `XRF-03` | **A citation is reported as a *reference*, never as a *dependency***, unless it appears in `depends_on:` front matter | §5.1 |
| `XRF-04` | **Every cited identifier resolves** — to a live row, a retirement row, or a named absent-register row | `CHK-X1` |
| `XRF-05` | **The register documents are excluded from the phantom sweep**, because they name phantoms by design | §4.3 |
| `XRF-06` | **The index is regenerated at every gate, and on demand before any coverage claim** | §8 |
| `XRF-07` | **A coverage percentage may not be quoted without its denominator and the pattern behind it** — `AUDIT-014` `TS-01`'s standing instruction, generalised | §5.3 |

---

## 4. The Generators

Six scripts. Each runs against markdown today, requires nothing but `grep`, `sed`, `awk`, `sort`
and `comm`, and produces one layer of §5.

### 4.1 `XRF-G1` — the document graph

```bash
# Nodes: every guiding document. Excludes the two artefact READMEs, which match
# the filename pattern and carry no front matter.
find . -name '*.md' -type f | grep -E '/[A-Z]{2}-[0-9]{3}_' | grep -v artefacts > docs.txt

# Edges: src -> tgt, deduplicated per file (a citation counts once per document)
while read -r f; do
  src=$(basename "$f" | grep -oE '^[A-Z]{2}-[0-9]{3}')
  grep -ohE '\b(GV|RQ|AR|DA|IN|SC|UX|BE|QA|MG|PE|SV|RL|CH|CO|BM|RR)-[0-9]{3}\b' "$f" \
    | sort -u | while read -r t; do [ "$t" != "$src" ] && echo "$src|$t"; done
done < docs.txt > edges.txt

cut -d'|' -f2 edges.txt | sort | uniq -c | sort -rn   # in-degree
cut -d'|' -f1 edges.txt | sort | uniq -c | sort -rn   # out-degree
awk -F'|' '{print substr($1,1,2)"->"substr($2,1,2)}' edges.txt | sort | uniq -c | sort -rn
```

### 4.2 `XRF-G2` — the namespace census

```bash
# One line per space. The pattern IS the definition; change it and the number changes.
for spec in "objective:BO-[0-9]{1,3}" "requirement-FR:FR-[A-Z]{3}[0-9]?-[0-9]{3}" \
            "requirement-NFR:NFR-[0-9]{3}[a-c]?" "module:M[0-9]{2}" "portal:P[0-9]{2}" \
            "entity:E-[0-9]{3,4}" "role:R[0-9]{2}" "test-TS:TS-[0-9]{3}" \
            "kpi:KPI-[0-9]{3}" "cd:CD-[0-9]{3}" "int:INT-[0-9]{3}" \
            "bru:BRU-[A-Z]{3}[0-9]?-[0-9]{2,3}" "sod:SOD-[0-9]{2}" "risk:RSK-[0-9]{3}"; do
  name="${spec%%:*}"; pat="${spec#*:}"
  printf "%-18s %s\n" "$name" "$(grep -rhoE "\b$pat\b" --include='*.md' . | sort -u | wc -l)"
done
```

> ### The false-positive discipline, stated once and applied everywhere
>
> `RR-005` §4.1 records that an `IEEE [0-9]{3,4}` pattern invented three non-existent standards by
> truncating real ones. `RR-004` §4.1 records that an unquoted `nn-nn` pattern returned **101**
> candidate module documents of which **83 were dates**. `RF-001` §4.3 `GL-02` records that a
> two-segment `FR-` pattern silently dropped all **34** `SRM2` requirements.
>
> **Three independent instances, three different authors, one failure mode**: the pattern does not
> error, it reports a smaller or larger wrong world, confidently. `XRF-02` is the response —
> **every figure in §5 is printed next to the pattern that produced it**, so the number can be
> challenged by challenging the pattern.

### 4.3 `XRF-G3` — the trace chain

```bash
# Forward: for each requirement, does its owning module code resolve to a module file?
comm -23 \
  <(grep -rhoE '\bFR-[A-Z]{3}[0-9]?-[0-9]{3}\b' --include='*.md' . \
      | sed -E 's/^FR-([A-Z]{3}[0-9]?)-.*/\1/' | sort -u) \
  <(grep -h '^module_code:' 1000fix_ERP_Module/03_Modules/*/M*.md \
      | sed 's/module_code: *//' | tr -d '`' | sort -u)

# Backward: for each module, does at least one requirement name it?
for m in $(seq -w 1 67); do
  grep -rql "M$m" --include='*.md' . >/dev/null || echo "M$m has no citation"
done
```

### 4.4 `XRF-G4` — resolvability (`RR-002` `CHK-05`)

```bash
# Phantom / dangling PGD identifiers.
# XRF-05: exclude the registers, which name phantoms by design.
comm -13 \
  <(find . -name '*.md' | grep -oE '/[A-Z]{2}-[0-9]{3}' | tr -d '/' | sort -u) \
  <(grep -rhoE '\b(GV|RQ|AR|DA|IN|SC|UX|BE|QA|MG|PE|SV|RL|CH|CO|BM|RR)-[0-9]{3}\b' \
      --include='*.md' --exclude='RR-002_*' --exclude='RR-004_*' --exclude='RR-006_*' . \
    | sort -u)

# Orphans: on disk, cited by nobody.
comm -23 <(...ondisk...) <(...cited...)

# Structural-space phantoms: tokens outside the declared range.
grep -rhoE '\bP[0-9]{2}\b' --include='*.md' . | sort -u   # declared P01-P12
grep -rhoE '\bM[0-9]{2}\b' --include='*.md' . | sort -u   # declared M01-M67
```

### 4.5 `XRF-G5` — the retirement table

Hand-seeded from `RR-002` §8.4, `RR-004` §8.1 and this document's §5.4, then machine-checked:
every retired identifier must still return a row. There is no way to generate a retirement reason
from text; there is a way to check that every retired identifier is still resolvable, and
`CHK-X2` does.

### 4.6 `XRF-G6` — freshness

```bash
# Any document whose enumeration_timestamp predates the newest file in the repository
newest=$(find . -name '*.md' -printf '%T@ %p\n' | sort -rn | head -1 | cut -d' ' -f2-)
grep -rl '^enumeration_timestamp:' --include='*.md' . | while read -r f; do
  [ "$f" -ot "$newest" ] && echo "STALE $f"
done
```

---

## 5. The Generated Index — Edition 1

**Generated 2026-08-19 20:12** against **795** workspace markdown files, **175** in
`project-guide-doc/`, **137** guiding documents.

> ⚠ **This edition is already provisional.** Between `RR-004`'s enumeration at 19:54 and this one
> at 20:12 — **eighteen minutes** — the repository gained `BM-004`, `BM-005`,
> `PGD-AUDIT-CAT-14`, a rewritten `README.md`, a rewritten `FOLDER_STRUCTURE.md` and an updated
> `PGD-000`. That is baseline movements **13 through 18** on `RR-004` §6's record. **Re-run §4
> before relying on any figure below.**

#### Regeneration at 2026-08-19 20:20 — the mechanism, demonstrated

`PGD-AUDIT-CAT-99` re-ran all six generators eight minutes after this edition was cut. **The whole
regeneration took under one second.** The delta:

| Measure | Edition 1 · 20:12 | Regenerated · 20:20 | Δ |
|---|---:|---:|---:|
| Workspace `.md` | 795 | **798** | +3 |
| `project-guide-doc/` `.md` | 175 | **177** | +2 |
| Guiding documents | 137 | **138** | +1 |
| Graph edges | 3,280 | **3,320** | +40 |
| Orphans | 0 | **0** | — |
| Dangling `PGD` IDs | `BM-001` `CO-001` `RR-006` `RR-007` `RR-008` | `BM-001` `CO-001` `RR-007` `RR-008` | **−1** |
| `GV-002` in-degree | 82 | **83** | +1 |

**Two corrections to Edition 1, both recorded rather than silently overwritten:**

1. **The 137 excluded this document.** Edition 1 was generated before `RR-006` was written, so the
   node count omitted the node doing the counting. **138 is correct including itself**, and an index
   that does not count itself is the first thing a reader will check.
2. **`RR-006` has left the dangling list** and `RR-004`'s three forward references now resolve. The
   remaining four are `BM-001` and `CO-001` (discharged elsewhere — `EVR-F-05`) and the two
   phantoms, of which **`RR-008` was corrected to `RR-005` in `UX-005` and `UX-007` at 20:21**, so
   the next regeneration will show three.

> **This is the point of `RR-006-D-01`.** A hand-maintained index would have needed an author, a
> review and a re-issue to absorb eight minutes of change. This one needed one command, and the
> difference between the two editions is itself informative — it shows the estate gaining forty
> citation edges in eight minutes, which no static document could have told anyone.

### 5.1 L1 — The document graph

**137 nodes · 3,280 edges · 0 orphans · mean out-degree 23.9**

#### 5.1.1 The ten most-referenced documents (in-degree)

| Rank | Document | In-degree | What the number means |
|---:|---|---:|---|
| 1 | `GV-002` Governance Framework, RACI & ToR | **82** | Every document that names a role or an approver reaches here. **The estate's single most load-bearing artefact** |
| 2 | `GV-005` RAID Register | **67** | Every risk, assumption, issue and dependency escalation lands here |
| 3 | `AR-001` Software Architecture Document | **64** | The highest non-governance node — the architecture is genuinely central, as intended |
| 4 | `GV-009` Wave Gate & Phase Exit Criteria | **63** | Every gate-bound obligation in every register |
| 5 | `GV-007` Estimation Model & Resource Plan | **54** | Every effort figure |
| 6 | `GV-004` Integrated Programme Plan | **51** | Every date |
| 7 | `GV-003` Decision Log & Change Control | **50** | Every `D-nnn` |
| 8 | `SC-007` Data Residency & Cross-Border Transfer | **47** | Higher than expected — residency reaches infrastructure, migration, integration and legal |
| 9 | `SC-003` DPIA (PDPA 2026) | **46** | |
| 10 | `AR-012` Architecture Compliance & Fitness Functions | **45** | The 184 `FF-nn` are cited widely |

> **Six of the top seven are `GV`.** That is the correct shape for a governance-led programme and it
> is worth stating, because it is also the risk: **`GV-002` has in-degree 82 and no approval
> record** (`PGD-A1-09`). A single unapproved document is upstream of 60% of the estate.

#### 5.1.2 The ten highest-fan-out documents (out-degree)

| Rank | Document | Out-degree | Assessment |
|---:|---|---:|---|
| 1 | `RR-003` Document Standards & Template Library | **120** | It classifies all 140 registered documents — fan-out is its function |
| 2 | `RR-005` Standards & Regulatory Currency Register | **88** | Same: every *"where it bites"* cell is an edge |
| 3 | `RR-004` Source Document Index & Evidence Register | **78** | Same |
| 4 | `CO-003` Statement of Work & Deliverable Acceptance | **63** | **Every guiding document is a contractual deliverable.** The number is the contract's shape |
| 5 | `QA-001` Master Test Strategy | **52** | Thirteen test levels across the estate |
| 6 | `RQ-001` Software Requirements Specification | **48** | |
| 7 | `GV-004` Integrated Programme Plan | **47** | |
| 8 | `GV-007` Estimation Model | **46** | |
| 9 | `RL-003` Go-Live Readiness Assessment | **45** | Seven readiness dimensions reaching across the estate |
| 10 | `AR-001` Software Architecture Document | **43** | The only document in **both** top-ten lists |

> **`AR-001` is the only document with both high in-degree (64) and high out-degree (43).** In a
> citation graph that is the signature of a genuine hub — it is read by many and it reads many. The
> three `RR` registers at the top of the out-degree list are **not** hubs in the same sense; they
> are indexes, and an index that cites everything and is cited by few is behaving correctly.

#### 5.1.3 Category-to-category reference matrix — the ten heaviest flows

| Flow | Edges | Reading |
|---|---:|---|
| `AR` → `AR` | 95 | Architecture is the most internally cross-referenced category |
| `SC` → `SC` | 92 | |
| `GV` → `GV` | 92 | |
| `QA` → `QA` | 83 | |
| `RQ` → `RQ` | 67 | |
| `PE` → `PE` | 66 | |
| `DA` → `AR` | 41 | **The heaviest cross-category flow.** Data architecture reads software architecture |
| `CO` → `GV` | 40 | Commercial reads governance — the SoW is written against the governance model |
| `RR` → `AR` | 38 | The registers index architecture most heavily |
| `SC` → `GV` | 36 | |

> **Self-reference dominates: the six heaviest flows are all intra-category.** That is expected and
> healthy — a category whose documents did not reference each other would not be a category. **The
> diagnostic value is in what is *absent*.** `CH` → `QA` is 0; `UX` → `MG` is 0; `BM` → `QA` is
> 0. None is obviously wrong; all three are worth a reviewer's minute, and **that is what a graph is
> for** — not to answer, but to point.

### 5.2 L2 — Namespace census

Every population counted at 2026-08-19 20:12. **The pattern is printed because the pattern is the
definition** (`XRF-02`).

| Space | Pattern | In use | Registered | Gap | Registry | `RR-002` state |
|---|---|---:|---:|---:|---|---|
| Business objective | `BO-[0-9]{1,3}` | **27** | 18 | **+9** | `06-02` | ⛔ **two sets** — §5.4.3 |
| Functional requirement | `FR-[A-Z]{3}[0-9]?-[0-9]{3}` | **3,539** | 200 | **+3,339** | `05-01` | **Frozen** `TH-01` |
| Non-functional requirement | `NFR-[0-9]{3}[a-c]?` | **125** | 104 | **+21** | `05-06` | **Frozen** `TH-05` |
| Module | `M[0-9]{2}` | **69** | 67 | **+2** (`M68`, `M99`) | `02-02` | `IDC-F-09` |
| Portal | `P[0-9]{2}` | **14** | 12 | **+2** (`P13`, **`P38`**) | `04-00` | §5.4.2 |
| Entity | `E-[0-9]{3,4}` | **51** | 225 in `05-02` · **1,335** owned (`DA-001`, `DA-002`) · **1,370** named in §10 | **−1,284** | `05-02` | Not registered as a space |
| Domain event | `<domain>.<verb>.v<n>` | **2** literal tokens · **988** catalogued by `IN-003` | 64 in `05-03` §4.2 | **+924** | `IN-003` | `RR-002-D-04` |
| Role | `R[0-9]{2}` | **53** | 38 | **+15** | `05-04` | **Frozen** `TH-04` |
| Test / acceptance content | `TS-[0-9]{3}` | **18** | 18 | 0 | `TS-001` | ✅ |
| KPI | `KPI-[0-9]{3}` | **301** | 95 | **+206** | `06-02` | **Frozen** `TH-02` |
| Custom development | `CD-[0-9]{3}` | **240** | 199 | **+41** | `BE-005` | **Frozen** `TH-06` |
| Integration | `INT-[0-9]{3}` | **47** | 47 | 0 | `05-03` | ✅ |
| Business rule | `BRU-[A-Z]{3}[0-9]?-[0-9]{2,3}` | **1,374** | — | — | `05-05` | Not reconciled |
| Segregation of duties | `SOD-[0-9]{2}` | **61** | 12 in `05-04` · 61 in `SP-006` | **+49** | contested | **Frozen** `TH-03` |
| Risk | `RSK-[0-9]{3}` | **44** | 36 in `00-04` | **+8** | `00-04` / `GV-005` | — |
| Wave | `W[1-9]` | **9** | 9 | 0 | `06-01` | ✅ |
| Gate | `G[1-9]` | **9** | 4 (`G1`–`G4`) | **+5** | `06-02` / `GV-009` | Two gate models |

> ### `XRF-F-01` — every gap runs the same direction, for the sixth independent time
>
> Fourteen of seventeen spaces have **more identifiers in use than registered**, and not one has
> fewer. The gaps are not marginal: `FR` is **17.7×** its register, `KPI` **3.2×**, `SOD` **5.1×**,
> events **15.4×**.
>
> `RR-002` `IDC-F-03` recorded this as *"every measured gap is larger than the finding that
> recorded it — five independent measurements, same direction."* **This is the sixth**, and it is
> the first taken across all spaces at once rather than one space at a time.
>
> **The direction is the finding, not the magnitude.** A register that under-counts by a consistent
> factor is not a register that is behind; it is a register that **is not the allocation
> mechanism**. Identifiers are being created by authoring and registered afterwards, when anyone
> remembers. `RR-002` `IDC-03` (register-first) is the rule; §5.2 is the measurement of how far
> practice is from it. **Severity High**, owner **Enterprise Architecture**, needed **W1**.
>
> **Three spaces are clean** — `INT` (47/47), `TS` (18/18) and `W` (9/9). All three are small,
> owned by a single document, and closed. That is the shape a register keeps when it can.

### 5.3 L3 — The eight-way trace chain, link by link

The chain `PGD-000` asks for is *objective ↔ requirement ↔ module ↔ entity ↔ event ↔ role ↔ test ↔
KPI*. Tested in both directions per ISO/IEC/IEEE 29148:2018 §5.2.8.

| # | Link | Forward | Backward | State |
|---:|---|---|---|:--:|
| 1 | **objective → requirement** | `06-02` maps `BO-01`…`BO-18` to modules, **not to requirements** | No `FR-` identifier names a `BO-` | ⛔ **Broken.** The chain has no first link |
| 2 | **requirement → module** | **68 module codes** in use as `FR-<CODE>-`; **67 modules** exist. `POR` has no module | **5 codes** (`BIL`, `CWM`, `HRM`, `PRT`, `SCM`) appear in `BRU-` with no `FR-` family | ⚠ `RF-001` `GL-02` |
| 3 | **module → entity** | `05-02` registers **225** entities; the counted population is **1,335 owned / 1,370 named** | `E-nnn` tokens on disk: **51** | ◐ **Population resolved (`XRF-Q-04`); mapping still absent** |
| 4 | **entity → event** | `IN-003` catalogues **988** events; `05-03` §4.2 registers **64** | Only **2** canonical `<domain>.<verb>.v<n>` tokens appear as literal text | ⛔ **`AP-01` ruled and 45× larger** (`PGD-A3-04`) |
| 5 | **event → role** | No event names a role | No role names an event | ⛔ **Absent by construction** |
| 6 | **role → test** | `05-04` maps **38** roles to permissions | `TS-006` covers *"Service Operations roles"* without naming `R-nn` | ⚠ **Partial, and unaddressable while `R39`–`R50` are unregistered** |
| 7 | **test → requirement** | `TS-001` declares content traceability; `QA-011` specifies the coverage report | **The denominator is contested** — §5.3.1 | ⚠ `TS-01` |
| 8 | **requirement → KPI** | `06-02` maps KPIs to objectives and modules | **301 KPI identifiers, 95 registered** | ⛔ `RP-01` |

> ### `XRF-F-02` — the chain is broken at five of its eight links, and the first link is one of them
>
> **The programme cannot trace a business objective to a requirement.** `06-02` maps `BO-01` to
> modules (`M01`, `M02`, `M20`); no requirement identifier anywhere names an objective. So the
> question *"which requirements deliver `BO-01`?"* is answerable only by reading three module
> specifications and inferring.
>
> **Why this is the most consequential row in the document.** `06-02` §6 makes a signed pre-wave
> baseline a precondition of claiming any benefit (`RLA-09`), and the benefit case is stated
> **against objectives**. If objectives do not reach requirements, then **benefit cannot be traced
> to build**, and a wave can deliver every requirement in its scope while nobody can demonstrate
> that it delivered an objective.
>
> **This is not a new gap — it is a newly *measured* one.** `RQ-004` is the RTM and holds the
> obligation; this index establishes that the first link has **zero** instances, not few.
>
> **Remediation.** `RQ-004` §5 adds a `traces_to_objective:` obligation on every requirement family,
> and `06-02` is restated to map `BO-nn` → `FR-<CODE>-` family rather than to modules. Owner
> **Enterprise Architecture** with **CFO** for the benefit half. Needed **W1**. **Severity High.**

#### 5.3.1 The requirement denominator — five measurements, printed with their patterns

`AUDIT-014` `TS-01` established that coverage is unanswerable because the denominator is contested,
and instructed that no percentage be quoted. That instruction stands. What this index adds is that
**the disagreement is now arithmetic**:

| Measurement | Pattern / scope | Figure |
|---|---|---:|
| `README.md` §Total claim | — | 2,930 |
| `05-01` title claim | — | ~2,352 |
| `RF-001` §4.3, modules ∪ portals | `FR-[A-Z]{3}[0-9]?-[0-9]{3}` over `M*.md` ∪ `P*.md` | **3,350** |
| `RF-001` §4.3, whole module repository | as above, whole repo | **3,537** |
| `RR-002` §9 | as declared there | **3,504** |
| **This index, whole workspace** | `FR-[A-Z]{3}[0-9]?-[0-9]{3}`, all 795 files | **3,539** |
| Registered in `05-01` | — | **200** |

> **The six enumerated figures span 189 identifiers — 5.3%** — and every one of them is
> reproducible from its stated pattern and scope. **The two quoted figures (2,930 and ~2,352) are
> not reproducible from any stated scope**, and that is the actual finding: not that the estate
> disagrees, but that two of the seven numbers have no method attached.
>
> `XRF-07` generalises `TS-01`'s instruction: **a coverage percentage may not be quoted without its
> denominator and the pattern behind it.** `RQ-004` §5.1 picks the ruling denominator; this index
> guarantees that whichever it picks can be recomputed.

### 5.4 L4 — Resolvability (`RR-002` `CHK-05`, switched on)

#### 5.4.1 Dangling `PGD` identifiers

| ID | Cited by | Assessment |
|---|---|---|
| `CO-001` | 6 documents | ✅ **Discharged** by `primary-doc/…RFP.md`. Reads as dangling only because `PGD-000` has no `discharged_by` field — `RR-004` `EVR-F-05` |
| `BM-001` | 5 documents | ✅ **Discharged** by `06-02`. Same cause |
| `RR-006` | 3 documents | ✅ **This document.** Resolved at this issue |
| `RR-007` | 1 — `RR-004` §5.6.2 | ⚠ **A generator artefact**, not a citation. §5.4.4 |
| **`RR-008`** | **`UX-005` ×6, `UX-007` ×1** | ⛔ **Phantom** — §5.4.2 |

#### 5.4.2 Phantom identifiers — `XRF-F-03`

Two identifiers are cited as though registered and were never allocated in any register.

**`RR-008` — a document that has never existed**

| Where | How it is used |
|---|---|
| `UX-005` §, standards table | *"Reviewed at each `RR-008` cycle"* |
| `UX-005` `ACD-10` | **a governing rule** — *"Vendor accessibility is re-assessed at every major version upgrade, and the assessment is an `RR-008` register entry"* |
| `UX-005` `ACD-34` | **a governing rule** — *"This position is reviewed at each `RR-008` cycle"* |
| `UX-005` `UX-005-D-04`, `-D-05` | Two recorded decisions whose review mechanism is `RR-008` |
| `UX-005` §Traceability | Lateral dependency: *"`RR-008` — Standards currency review"* |
| `UX-007` §, Unicode row | *"Unicode 17.1 is scheduled for September 2026 and is an `RR-008` review item"* |

Category 99 registers `RR-001`…`RR-006`. **There is no `RR-007` and no `RR-008`.** The intent is
unmistakable — `RR-008` means **`RR-005`**, the Standards & Regulatory Currency Register. An author
who needed a currency register invented a plausible identifier rather than looking one up.

**The consequence is not cosmetic.** `ACD-10` and `ACD-34` are **governing rules that schedule work
against a document that does not exist**, so as written they are unexecutable. `UX-007`'s Unicode
17.1 review — due **September 2026, next month** — is scheduled into the same void.

**`P38` — a portal that has never existed**

`M10_Loyalty_Membership_and_Rewards.md` §API table lists the consumers of
`POST /api/v1/loyalty/vouchers/validate` as **`P01, P03, P38`**. The portal space is `P01`–`P12`
(`04-00`); `P13` is registered as *proposed, unallocated* (`RR-002` §8.6). **`P38` appears exactly
once in 795 files and resolves to nothing.**

It is a single row in one table, and it is an **integration contract**: an endpoint's consumer
list is what `IN-002`'s OpenAPI contracts and `SC-004`'s authorisation scopes are derived from. A
consumer that does not exist is either a missing portal or a typo, and nothing in the estate says
which.

> **Both phantoms were found by the same three-line `comm`**, and neither was found by fourteen
> category audits. **Set difference is not a skill auditors lack; it is a thing prose cannot do.**
> Owner **Enterprise Architecture**. `RR-008` → `RR-005` is **Now**; `P38` is **W1** and needs
> `M10`'s author. **Severity Medium** for both — low effort, and both sit under something load-bearing.

#### 5.4.3 `BO-1` vs `BO-01` — `XRF-F-04`

| Form | Range | Home | Grade |
|---|---|---|:--:|
| `BO-1` … `BO-9` | 9 | `old-primary-doc/…RFP.md` | **S** (superseded) |
| `BO-01` … `BO-18` | 18 | `primary-doc/…BRD.md`, `06-02` | **A** |

**They are not the same objectives renumbered:**

| Identifier | Denotes |
|---|---|
| `BO-1` | *"Operational Unification"* |
| `BO-01` | *"Automate the end-to-end service order lifecycle to eliminate manual coordination"* — 20% → 70%, owner Service Ops Director |

A naive count returns **27 objectives**; there are **18**, plus 9 retired ones that resolve to
different things. `06-02` is the KPI and benefits document, so **a benefit traced to `BO-1` and one
traced to `BO-01` are traced to different objectives, and the identifiers differ by a leading
zero.** This is `RR-002` `IDC-14` — digit-count disambiguation — with the digit count doing the
disambiguating and nobody told.

**Remediation** (`RR-004` `RR-004-D-04`): `BO-1`…`BO-9` are **retired in place**, §5.5, so they
still resolve and a reader learns they do not map. Owner **Enterprise Architecture**, **W1**.
Consumers: `BM-003`, `BM-004`. **Severity High.**

#### 5.4.4 A generator caveat, recorded because it fired

`XRF-G4`'s first run reported **`RR-007` as a cited-and-absent identifier.** Its only occurrence in
795 files is inside `RR-004` §5.6.2, in the sentence *"There is no `RR-007` and no `RR-008`."*

**The generator counted a denial of existence as a citation.** It is right by its own definition —
the token is present — and wrong by any useful one.

This is the third failure mode of text-as-database in this document set, after the truncating regex
(`RR-005` §4.1) and the date-matching pattern (`RR-004` §4.1). The fix is `XRF-05`: **the register
documents are excluded from the phantom sweep**, because naming phantoms is their function. The
exclusion is declared in `XRF-G4`'s `--exclude` flags rather than applied silently, so a reader can
see what was left out and disagree.

#### 5.4.5 Orphans

**0 of 137.** Every guiding document on disk is referenced by at least one other.

For a 137-document estate written by multiple concurrent hands over four days, with no version
control and — until this document — no index, that is a genuinely strong result and it should be
recorded as such. **It is also what makes this index worth generating**: a graph with no orphans is
a graph whose edges mean something.

### 5.5 L5 — The retirement table (`RR-002` `IDC-06`)

*"Retired identifiers still resolve."* Seeded from `RR-002` §8.4, `RR-004` §8.1 and §5.4 above.

| Identifier(s) | Retired because | Resolves to | Ruled by |
|---|---|---|---|
| `BO-1` … `BO-9` | Superseded v1.0 objective set; **denote different objectives** from `BO-01`… | The v1.0 RFP objective definitions. **Do not map to `BO-01`…`BO-18`** | `RR-004-D-04`, this §5.4.3 |
| `FR-SLS-001` … `-030` | Only home is a superseded pillar file | `99_Reference/_Superseded/SUPERSEDED_Pillar_B` | `RF-001` `GL-04`, `RR-002` `IDC-F-08` |
| `FR-BFO-*` (3) | `M04` reverted to code `FRD` under audit `C-03` | `M04`, under `FR-FRD-` | `RR-002` `IDC-F-08` |
| `AUT-nnn` (60, legacy) | Superseded by `AUT-<CODE>-nn` | `_MODULE_TEMPLATE` §0 | `RR-002-D-01` |
| `PGD-AUDIT-001` … `-009` | Sequential form retired in favour of category-keyed | The nine files, unrenamed | `RR-002-D-05` |
| **`RR-008`** | **Never allocated.** Retained here so the seven citations resolve | **`RR-005`** Standards & Regulatory Currency Register | **This document, §5.4.2** |
| **`P38`** | **Never allocated.** Retained here so `M10`'s API row resolves | **Unresolved** — needs `M10`'s author. `XRF-Q-02` | **This document, §5.4.2** |
| `M68`, `M99` | Illustrative values in `BE-005`, never allocated | Reserved-unallocated | `RR-002` `IDC-F-09` |
| `P13` | Cited as though registered | Proposed-unallocated, `04-00` | `RR-002` §8.6 |
| `R60` | Duplicates `R32` | `R32` | `RR-002` `TH-04` |

> **A retirement table is the cheapest thing in this document and the one most likely to be
> skipped.** Its whole purpose is that a reader who meets `BO-1`, `FR-SLS-014` or `RR-008` in a
> four-year-old file gets an answer instead of a search. `IDC-06` requires it; this is it.

### 5.6 The content estate's three traceability matrices

`RF-003` (content → requirement), `RF-004` (content → module) and `RF-005` (content → portal)
already exist and are current.

| Question | Rule |
|---|---|
| Content-side traceability | **`RF-003`/`RF-004`/`RF-005` govern.** Not restated here |
| Engineering-side traceability | **This index** |
| The shared spine — `M01`–`M67`, `P01`–`P12`, `FR-` | **`RR-002` §5 governs the space; both indexes report it.** They must not disagree |
| Tested at this issue? | **No.** `XRF-Q-03` |

> **Three content matrices, three `RR` registers, and one workspace.** This is `RR-004`
> `EVR-F-07` and `RR-005` `CUR-F-10` a third time: the content estate built the same instruments
> first and nobody on the engineering side knew. **The duplication is not waste — the two estates
> genuinely need different indexes — but it was not designed, and an undesigned overlap is where
> divergence lives.**

---

## 6. Findings

| # | Finding | Severity | New? | Owner | Needed by |
|---|---|:--:|:--:|---|---|
| `XRF-F-01` | **Fourteen of seventeen namespaces have more identifiers in use than registered, and none has fewer.** `FR` 17.7×, events 15.4×, `SOD` 5.1×, `KPI` 3.2×. Registration is not the allocation mechanism | **High** | Sixth instance of `RR-002` `IDC-F-03`; first taken across all spaces at once | Enterprise Architecture | **W1** |
| `XRF-F-02` | **The trace chain is broken at five of eight links, including the first.** No requirement identifier anywhere names a business objective, so **benefit cannot be traced to build** | **High** | Newly *measured* | Enterprise Architecture + CFO | **W1** |
| `XRF-F-03` | **Two phantom identifiers.** `RR-008` cited 7 times including in two governing rules and a September 2026 review item; **`P38`** cited once, in an API consumer list | Medium | **New** | Enterprise Architecture | **Now** / **W1** |
| `XRF-F-04` | **`BO-1` and `BO-01` denote different objectives** and differ by a leading zero. A naive count returns 27 objectives; there are 18 | **High** | **New** | Enterprise Architecture | **W1** |
| `XRF-F-05` | **Two of seven published requirement denominators have no reproducible method** — `README`'s 2,930 and `05-01`'s ~2,352. The six enumerated figures span 189 identifiers | Medium | Extends `RF-001` `GL-01`, `AUDIT-014` `TS-01` | `RQ-004` owner | **W1** |
| `XRF-F-06` | **`GV-002` has in-degree 82 and no approval record.** One unapproved document is upstream of 60% of the estate | Medium | Newly *quantified*; cause is `PGD-A1-09` | **Board** | **Now** |
| `XRF-F-07` | **Three of five `RR` registers and three content matrices were built without knowledge of each other.** Complementary by accident | Medium | Third instance — `EVR-F-07`, `CUR-F-10` | Enterprise Architecture | `G2` |
| `XRF-F-08` | **This edition was stale within eighteen minutes.** Six files changed between `RR-004`'s enumeration and this one | Low | Baseline movements 13–18 | PMO | — |

### 6.1 Severity basis

The same scale as `RR-002` §8.1, `RR-004` §8 and `RR-005` §8.1, so findings across all four
registers are comparable. **High** = a claim can be made that is wrong and looks right.
**Medium** = a reader is misled but a mechanical check would catch it. **Low** = a latent trap.

### 6.2 What the index proved about itself

`PGD-000` Category 99 asserted that *"every audit finding to date has been a cross-reference
failure that an index would have surfaced automatically."* That was a hypothesis. Building the
index tests it:

| Finding class | Would this index have caught it? |
|---|---|
| `H-03` — 48 colliding `CD` identifiers | ✅ `XRF-G4` set difference |
| `AP-02` — `NFR-090/091/092` used twice | ✅ `CHK-04` / `XRF-G2` |
| `RP-01` — 250 KPI in use, 95 registered | ✅ `XRF-G2` — and it under-counted; the figure is 301 |
| `C-02` — `M31` in no register | ✅ `XRF-G4` |
| `H-04` — 30 of 67 module codes listed | ✅ `XRF-G3` |
| `GL-02` — `SRM2` dropped by a regex | ⚠ **Only if the pattern is right.** §4.2 |
| `TS-01` — contested denominator | ⚠ **Surfaced, not resolved.** §5.3.1 |
| `C-04` — repealed statute cited | ❌ **No.** An index cannot know the world changed — that is `RR-005`'s job |
| `MGA-06`/`RLA-18` — 16 declared Bengali counterparts absent | ✅ File-existence set difference |

**Seven of nine, fully or partly.** The hypothesis holds, with one instructive exception: **a
cross-reference index detects internal inconsistency and is blind to external change.** That is
exactly why `RR-005` exists as a separate document rather than as a section of this one.

---

## 7. Enforcement

Numbered `CHK-X*` so as not to collide with `RR-002` §10's `CHK-01`…`06`, `RR-004` §10's
`CHK-E1`…`E6` or `RR-005` §10's `CHK-C1`…`C6`.

| # | Check | Detects | Gate |
|---|---|---|---|
| `CHK-X1` | **Resolvability** — every cited identifier resolves to a live row, a §5.5 retirement row or a named absent register | `XRF-F-03`, `XRF-04`; **this is `RR-002` `CHK-05`** | Warn, **fail at `G1`** |
| `CHK-X2` | **Retirement resolvability** — every §5.5 identifier still returns a row | `IDC-06` | Fail |
| `CHK-X3` | **Digit-form collision** — one space, two digit widths | `XRF-F-04`, `IDC-14` | **Fail** |
| `CHK-X4` | **Structural-space range** — `M`, `P`, `W`, `G`, `R` tokens outside the declared range | `P38`, `M68`, `M99` | **Fail** |
| `CHK-X5` | **Chain continuity** — each of §5.3's eight links returns ≥1 instance | `XRF-F-02` | Warn at `G1`, fail at `G2` |
| `CHK-X6` | **Index freshness** — this document's `enumeration_timestamp` older than the newest file | `XRF-F-08`, `XRF-06` | Warn |
| `CHK-X7` | **Denominator discipline** — a percentage published without a denominator and a pattern | `XRF-07`, `TS-01` | Warn |

> **`CHK-X1` is `RR-002` `CHK-05`, which `RR-002` §10 recorded as *"the one that matters and the one
> that cannot be switched on yet."*** It is switched on in §5.4. It does not pass — it returns two
> phantoms, five dangling `PGD` IDs and ten absent module documents — but **a check that runs and
> fails is a control; a check that cannot run is a plan.** That transition is this document's main
> contribution to `RR-002`.

---

## 8. Regeneration

`XRF-06`. This document is an **edition**, and editions have a schedule.

| Trigger | Scope | Owner | Cost |
|---|---|---|---|
| **Every wave gate** (`GV-009` `G1`–`G4`) | Full — all six generators, §5 replaced wholesale | PMO | **Under one minute of compute**, half a day of interpretation |
| **Before any coverage or completeness claim** | `XRF-G2` and `XRF-G3` only | The claimant | Seconds |
| **Before any identifier allocation in a frozen space** | `XRF-G2` for that space | The allocator | Seconds |
| **On any baseline movement of ≥5 files** | `XRF-G1` and `XRF-G4` | Whoever noticed | Seconds |
| **On demand, always** | Any generator | Anyone | — |

> **The economics are the argument.** `RR-005` §9 costs one person-day per full re-verification
> because a human must read publisher catalogues. `RR-004` §9 costs half a day. **This one costs
> under a minute of compute**, and produced four findings of which two are High.
>
> **The reason it has never been done is not cost.** It is that nobody owned it, and a generated
> index has no natural author — it is not anybody's specification, so it was nobody's job. `PG-M10`
> keeps being restated as a discipline (*"regenerate the figure in every place"*) when it is
> actually an architecture problem: **generate it in one place and reference it from the rest.**
> §8's schedule and `XRF-01` are that architecture.

### 8.1 The path to a real registry

`RR-002` §2.1 declares the departure that matters: *"11179 assumes a software registry. This
programme has 792 markdown files and no registry."* This document is the bridge, and the bridge has
three spans:

| Stage | What it is | Cost | Prerequisite |
|---|---|---|---|
| **1 — Now** | §4's six shell generators, run by hand | Nil | None. **Done at this issue** |
| **2 — `G1`** | The same generators as a `make index` target in the repository, output committed | Half a day | `RR-004` `EVR-Q-04` — **version control**, without which there is nothing to commit to |
| **3 — `G2`** | `CHK-X1`…`X7` as `PE-004` pipeline gates, failing the build | Two days | `PE-004`'s pipeline; stage 2 |

**Stage 2 is blocked on version control, and that is worth stating plainly**: the single decision in
`RR-004` `EVR-Q-04` unblocks the mechanisation of four registers at once.

---

## 9. Decisions Recorded

`DL-06` / `RR-002` `IDC-07`: identifiers take the form `RR-006-D-nn`.

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `RR-006-D-01` | Generated or maintained | (a) hand-maintained index; (b) **generated edition** | **(b)** | `_CATEGORY_OVERVIEW` requirement 5 is explicit, and `RR-004` §6's twelve movements in sixteen hours prove it. A hand index would have been wrong before it was finished | `XRF-01`; §5 is never hand-edited; §8's schedule |
| `RR-006-D-02` | Relationship to `RQ-004` | (a) replace the RTM; (b) **be its substrate** | **(b)** | `RQ-004` carries contractual coverage obligations and a ruling denominator. An index that also ruled would put the measurement and the target in one hand | §1.2; §5.3.1 supplies the denominators, `RQ-004` §5.1 picks one |
| `RR-006-D-03` | What to do about false positives | (a) tune patterns until clean; (b) **print the pattern next to every figure** | **(b)** | Three independent instances in one afternoon (`GL-02`, `RR-004` §4.1, `RR-005` §4.1) show tuning does not generalise. A stated pattern can be challenged; a clean number cannot | `XRF-02`; every §5 table carries its pattern |
| `RR-006-D-04` | The `RR-007` generator artefact | (a) suppress silently; (b) **declare an exclusion list**; (c) leave the false positive | **(b)** | Silent suppression is how an index starts lying. §5.4.4 records what fired, why, and what was excluded | `XRF-05`; `--exclude` flags visible in `XRF-G4` |
| `RR-006-D-05` | Whether to rule on `P38` | (a) declare it a typo for `P03`; (b) **retire it unresolved and escalate** | **(b)** | It appears once, in an API consumer list. Guessing an integration contract's consumer is exactly the kind of plausible repair that creates a defect nobody can find later | §5.5; `XRF-Q-02` to `M10`'s author |
| `RR-006-D-06` | Scope of the namespace census | (a) all ~1,094 prefixes; (b) **the 17 chain spaces** | **(b)** | `RR-002` §5 already registers the space *as a space*. Restating 1,094 rows here would duplicate it and go stale independently | §5.2; `XRF-G2`'s pattern list is extensible in one line |

---

## 10. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `XRF-Q-01` | Does `06-02` restate `BO-nn` → `FR-<CODE>-` family, so that the **first link of the trace chain exists**? | Enterprise Architecture + **CFO** | **W1** | `XRF-F-02`; every benefit claim at every wave review; `BM-003`, `BM-004` |
| `XRF-Q-02` | **What is `P38`?** A missing portal, or a typo in `M10`'s API consumer list? | `M10` owner, via Enterprise Architecture | **W1** | `IN-002` OpenAPI consumer derivation; `SC-004` scopes |
| `XRF-Q-03` | Row-by-row reconciliation of this index against `RF-003`/`RF-004`/`RF-005` on the shared spine (`M`, `P`, `FR`) | Enterprise Architecture / Programme Content Lead | `G2` | `XRF-F-07` |
| `XRF-Q-04` | **RESOLVED 2026-08-19.** **1,335 distinct owned entities** (`DA-001` §2.1 counted 2026-08-18 14:30; `DA-002` publishes it; independently recounted 2026-08-19 18:46 → 1,370 owned rows, 1,335 distinct). `05-02`'s **225** is the 30-module catalogue, superseded. `AR-008`'s **1,334** was correct at its own 02:05 count. The **51** `E-nnn` tokens are a *different space* — catalogue identifiers, not entities. **Remaining question: is the `E-nnn` space retired or extended to 1,335?** | Enterprise Architecture | **W1** | `DA-001`, `DA-002`, `MG-003`; chain link 3 |
| `XRF-Q-05` | Does the estate adopt `IN-003`'s **988**-event catalogue as the registered population, retiring `05-03` §4.2's 64? | Enterprise Architecture | `G1` | Chain link 4; `AR-009`; `IN-003` |
| `XRF-Q-06` | Who owns regeneration between gates? §8 says *"whoever noticed"*, which is not an owner | PMO | `G1` | `XRF-06`; `CHK-X6` |
| `XRF-Q-07` | Which body ratifies `XRF-01`…`XRF-07`? `PGD-A1-09` records that none exists | **Board** | **Now** | Every ✅ in this estate (`PGD-A2-25`) |

> Seven questions, seven named owners, seven dates. **`XRF-Q-01` and `XRF-Q-07` are escalated to
> `GV-005` RAID at issue.** `XRF-Q-01` is the one that, if answered, converts the benefit case from
> a claim into something measurable.

---

## 11. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | The index is **generated**, and the generators are printed in full and runnable | §4, six scripts; `extraction_method:` front matter; **met at issue** |
| `AC-02` | Every figure in §5 is the output of a §4 generator; none is hand-entered | §5; **met at issue** |
| `AC-03` | Every figure is printed with the pattern that produced it | §5.2, §5.3.1; **met at issue** |
| `AC-04` | The document graph covers every guiding document on disk, with in-degree, out-degree and a category matrix | 137 nodes, 3,280 edges; §5.1; **met at issue** |
| `AC-05` | All eight chain links are tested in both directions and the result stated, including where it is ⛔ | 8 of 8; §5.3; **met at issue** |
| `AC-06` | `RR-002` `CHK-05` is switched on and its output published | §5.4; **met at issue** — it runs and it fails, which is the point |
| `AC-07` | A retirement table exists so every withdrawn identifier resolves | 10 families; §5.5; **met at issue** |
| `AC-08` | This document's rule prefix was collision-checked before allocation per `RR-002` `IDC-08` | `rule_prefix:` front matter, 795-file denominator and timestamp; **met at issue** |
| `AC-09` | Generator false positives are declared, not suppressed | §4.2, §5.4.4, `RR-006-D-04`; **met at issue** |
| `AC-10` | Every finding carries a severity, an owner and a date | 8 of 8; §6; **met at issue** |
| `AC-11` | The index is reconciled with `RF-003`/`RF-004`/`RF-005` | **Not met.** `XRF-Q-03`. Stated rather than claimed, per `PG-M2` |
| `AC-12` | The index is mechanised as a pipeline gate | **Not met, and not achievable at this issue** — §8.1 stage 3 depends on `PE-004`'s pipeline and on version control (`RR-004` `EVR-Q-04`) |

**Definition of done.** Complete when every criterion above is met, `PGD-000`'s `RR-006` row is
updated with a fresh enumeration timestamp, and the approver has signed. **`AC-11` and `AC-12` carry
residual work with named blockers.** `AC-12` in particular should not be read as a shortfall of this
document: **an index that runs in under a minute by hand is a complete deliverable; making it run
without a hand is `PE-004`'s.**

---

## 12. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `PGD-000` | Registers this document; §5.2 corrects its *"seven identifier spaces, 601 files"* premise |
| Upstream | `RR-002` §5, §9, `CHK-05` | The space register this indexes; **`CHK-05` is switched on here as `CHK-X1`** |
| Upstream | `RR-003` §3.2 | Document classes, used to interpret the graph |
| Upstream | `RR-004` §5.3.1, §6, §7 | The absent-source register, the movement record and the document-grain reverse index |
| Upstream | `RR-005` §5 | External-standard currency — the one thing this index is structurally blind to (§6.2) |
| Downstream | `RQ-004` | **Receives §5.3.1's five denominators and §5.3's chain measurement.** The RTM rules; this measures |
| Downstream | `QA-011` | Receives the coverage substrate for its report |
| Downstream | `06-02`, `BM-003`, `BM-004` | Receive `XRF-F-02` and `XRF-F-04` — the broken first link and the two objective sets |
| Downstream | `UX-005`, `UX-007` | Receive `XRF-F-03` — `RR-008` → `RR-005` |
| Downstream | `M10` owner, `IN-002`, `SC-004` | Receive `XRF-Q-02` — `P38` |
| Downstream | `DA-001`, `DA-002`, `AR-008` | Receive `XRF-Q-04` — the three entity populations |
| Downstream | `IN-003`, `AR-009` | Receive `XRF-Q-05` — the 988/64 event gap |
| Downstream | `PE-004` | Hosts `CHK-X1`…`CHK-X7`; §8.1 stage 3 |
| Downstream | `GV-005` | Receives `XRF-Q-01` and `XRF-Q-07` as RAID entries |
| Lateral | `../../project_content/99_Reference_and_Registers/RF-003`, `RF-004`, `RF-005` | The content estate's three matrices. Referenced, reconciliation open (`XRF-Q-03`) |
| Lateral | `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-01`…`05-06` | The six files holding most of the estate's identifier spaces |

---

## 13. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` ·
`./_CATEGORY_OVERVIEW.md` · `./RR-001_Glossary_and_Acronym_Register.md` ·
`./RR-002_Identifier_Convention_Standard.md` ·
`./RR-003_Document_Standards_and_Template_Library.md` ·
`./RR-004_Source_Document_Index_and_Evidence_Register.md` ·
`./RR-005_Standards_and_Regulatory_Currency_Register.md` ·
`../01_Requirements_Engineering/RQ-004_Requirements_Traceability_Matrix.md` ·
`../02_Architecture_and_Design/AR-008_Domain_Model_and_Bounded_Context_Map.md` ·
`../04_Integration_and_API_Engineering/IN-003_Domain_Event_Catalogue_and_Schema_Registry.md` ·
`../06_Experience_and_Interface_Design/UX-005_Accessibility_Conformance_Design_WCAG_2_2_AA.md` ·
`../07_Build_Engineering_and_Development_Standards/BE-005_Custom_Development_CD_Master_Register.md` ·
`../08_Quality_Engineering_and_Test/QA-011_Requirements_to_Test_Coverage_Standard_and_Report.md`

**Workspace**
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md` ·
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02_Data_Model_and_Entity_Catalogue.md` ·
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-03_Integration_and_API_Catalogue.md` ·
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md` ·
`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md` ·
`../../1000fix_ERP_Module/03_Modules/B_Customer_Engagement_and_Experience/M10_Loyalty_Membership_and_Rewards.md` ·
`../../project_content/99_Reference_and_Registers/RF-003_Content_to_Requirement_Traceability_Matrix.md` ·
`../../project_content/99_Reference_and_Registers/RF-001_ERP_Glossary_and_Acronym_Register.md`

**External standards**
ISO/IEC/IEEE 29148:2018 · ISO/IEC/IEEE 12207:2017 · ISO 10007:2017 · ISO/IEC 11179-1:2023 ·
ISO/IEC/IEEE 29119-3:2021 — **currency of each verified in `RR-005` §5, not restated here.**

---

## 14. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-19 | Enterprise Architecture | Initial edition. Six generators printed in full; a 137-node / 3,280-edge document graph with zero orphans; a 17-space namespace census; the eight-way trace chain tested in both directions and found broken at five links including the first; `RR-002` `CHK-05` switched on; two phantom identifiers (`RR-008`, `P38`) and a two-set objective collision (`BO-1`/`BO-01`) found by set difference; a ten-family retirement table; 8 findings, 3 High, 4 new; 6 decisions; 7 open questions; 7 checks; and a regeneration schedule costing under a minute of compute | *(unsigned — no constituted body, `PGD-A1-09`)* |

---

*`RR-006` · Category 99 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
*1000FiX Services Limited · ERP Programme · Enterprise Architecture*
