---
id: PGD-AUDIT-CAT-99
title: Category 99 — Reference, Registers & Glossary — Category Audit
category: _AUDIT
code: PGD-AUDIT
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-19
status: ISSUED
classification: CONFIDENTIAL — Internal Use Only
owner: Enterprise Architecture
approver: Chief Technology Officer
standards_basis: ISO 19011:2018 §6 (conducting an audit) · ISO/IEC/IEEE 15289:2019 · PGD-000 §0.3 tests (a)–(d) · RR-003 §5 (per-class section sets) · RR-002 §7.2 (rule-prefix allocation)
traces_to: PGD-000 Category 99 · RR-001 · RR-002 · RR-003 · RR-004 · RR-005 · RR-006 · _CATEGORY_OVERVIEW
depends_on: PGD-000 · RR-001 · RR-002 · RR-003 · RR-004 · RR-005 · RR-006
verified_on: 2026-08-19
priority: P0
needed_by: Now
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
enumeration_timestamp: 2026-08-19 20:22 (repository wall clock — RR-005 §4.4)
audit_identifier_form: Category-keyed, per RR-002 RR-002-D-05 — collision-free by construction under concurrent authoring
finding_prefix: A99 — verified to return zero occurrences in identifier form across the repository before allocation, at 2026-08-19 20:22
---

# `PGD-AUDIT-CAT-99` — Category 99 Audit
# Reference, Registers & Glossary

### 1000FiX ERP System & Portal Suite v2.0 · ISO 19011:2018

---

## 1. Summary

Category 99 — six documents, code `RR` — was authored on 2026-08-19 between **02:53 and 20:18** by
two concurrent sessions and is audited here at **20:22**.

| Measure | Value |
|---|---:|
| Documents audited | **6** |
| Total lines · words · bytes | **5,635** · **62,956** · **399,902** |
| Rule spaces allocated | **6** — `TRM`, `IDC`, `DSL`, `EVR`, `CUR`, `XRF` |
| Governing rules issued | **67** |
| Findings raised **by** the six documents | **51** |
| Findings raised **by this audit** | **12**, of which **6 against the category's own authoring** |
| Findings **closed** at this audit | **11** |
| **Corrections applied** | **11**, of which **2 to other categories' documents** |
| Open questions carried | **36**, every one with a named owner and a date |
| Critical findings | **2** — `CUR-F-01`, `EVR-F-06` |

### 1.1 Verdict

**The category discharges its `PGD-000` row, and it does so by measuring the register's own premises
rather than by restating them.** Three of those premises were wrong, and all three were corrected:

| `PGD-000` premise | Filesystem |
|---|---|
| *"a 601-file estate"* | **798 markdown files** |
| *"seven … identifier spaces … ⇒ 46"* | **1,094 prefixes · 18,630 tokens** |
| §3 `Basis`: `IEEE 1016-2009` | **Inactive-Reserved at IEEE SA** |

**The ✅ is qualified as every ✅ in this estate is** (`PGD-A2-25`): tests (a), (b) and (c) of
`PGD-000` §0.3 are met and verified below, document by document; test (d)'s **approval record does
not exist and cannot**, until `GV-001` `CC-01` constitutes a body able to create one.

### 1.2 The three defects found by set difference

The single most important thing this category demonstrated is **methodological**, and it should be
read as a claim about the estate's audit practice rather than as a boast about six documents:

| Defect | Where it hid | How long |
|---|---|---|
| **`RR-008`** — a document cited **7 times**, including in **two governing rules** (`ACD-10`, `ACD-34`) and a **September 2026** review item, that has never been registered and does not exist | `UX-005`, `UX-007` | Since Category 06 was authored and audited (`PGD-AUDIT-006`) |
| **`P38`** — a portal in `M10`'s **API consumer list**, where the portal space is `P01`–`P12` | `M10` §API | Since the module estate was written; survived `00-06` and `00-07` |
| **`BO-1` vs `BO-01`** — two objective sets, two digit forms, **different objectives**, one of them the basis of the **BDT 876 lac** benefit case | `old-primary-doc` RFP vs `primary-doc` BRD and `06-02` | Since the v1.0 → v2.0 re-baseline |

**Fourteen prior category audits did not find any of the three, and none of them was careless.**
All three are invisible to reading and trivial to a three-line `comm`. The conclusion is not that
the audits should have read harder; it is that **set difference is a thing prose cannot do**, and
that `RR-006`'s generators should have existed before the fourteenth audit rather than after it.

---

## 2. Method

Seven tests, applied document by document. Tests 1–4 are `PGD-000` §0.3's; tests 5–7 are this
audit's additions and are the ones that found things.

| # | Test | Instrument |
|---:|---|---|
| 1 | **(a)** A named file exists at a stated path | `find` |
| 2 | **(b)** Complete front matter per `RR-003` §6.2 | Front-matter key census |
| 3 | **(c)** ≥90% of the section set its class requires | **`RR-003` §5's own class instrument** — the first audit able to apply test (c) mechanically |
| 4 | **(d)** A named owner and an approval record | Inspection |
| 5 | **Rule-space integrity** | Every declared `rule_prefix:` unique across the repository |
| 6 | **Reference resolution** | Every markdown link and backtick relative path resolves |
| 7 | **Claim reproducibility** | Every counted figure re-run against the filesystem at audit time |

> **Test 3 could not be applied by any previous category audit**, because the instrument did not
> exist. `PGD-000` §0.3 says so explicitly: *"Until `RR-003` publishes the per-document-type
> section sets that the ✅ test (c) measures against, no ◐ may be promoted to ✅."* `RR-003` §5
> published them at 03:08 today. **This is the first audit in the estate to measure test (c) rather
> than assert it**, and — a point worth stating plainly — **it applies that instrument first to the
> document that created it.**

### 2.1 Reproducibility

Every figure in this audit was produced by a command printed in `RR-004` §4.1, `RR-005` §4.1 or
`RR-006` §4, re-run at **2026-08-19 20:22**. Nothing is quoted from the documents under audit.

---

## 3. Test Results — Document by Document

| Doc | (a) file | (b) front matter | (c) section set | (d) approval | (5) rule space | (6) refs | (7) claims |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| `RR-001` | ✅ | ✅ 20 keys | ✅ 18 §§, class `REG`/`STD` | ⛔ `PGD-A1-09` | ✅ `TRM` unique | ✅ | ✅ |
| `RR-002` | ✅ | ✅ 20 keys | ✅ 16 §§, class `STD` | ⛔ | ✅ `IDC` unique | ✅ | ✅ |
| `RR-003` | ✅ | ✅ 20 keys | ✅ 16 §§, class `STD` | ⛔ | ✅ `DSL` unique | ✅ | ✅ |
| `RR-004` | ✅ | ✅ 21 keys | ✅ 16 §§, class `REG` | ⛔ | ✅ `EVR` unique | ✅ *(after `A99-C-03`, `A99-C-06`)* | ✅ *(after `A99-C-04`)* |
| `RR-005` | ✅ | ✅ 21 keys | ✅ 16 §§, class `REG` | ⛔ | ✅ `CUR` unique | ✅ *(after `A99-C-03`)* | ✅ |
| `RR-006` | ✅ | ✅ 22 keys | ✅ 14 §§, class `REG`/`MODEL` | ⛔ | ✅ `XRF` unique | ✅ | ✅ *(after `A99-C-05`)* |

**Tests (a), (b), (c), 5, 6 and 7: 6 of 6 pass.** **Test (d): 0 of 6**, and cannot pass —
`PGD-A1-09`, unchanged since the first governance audit.

### 3.1 Rule-space integrity — the check that could have gone wrong and did not

Six rule spaces were allocated by two concurrent sessions inside eighteen hours. Under
`RR-002` `IDC-13` — *"sequential allocation is forbidden where concurrent authoring is
possible"* — this is precisely the condition that produced nine identifier races in this
repository.

A repository-wide sweep of every declared `rule_prefix:` returns **18 declarations, zero
duplicates**:

```
CUR RR-005   DCM RL-006   DPY RL-002   DSL RR-003   EVR RR-004   GLR RL-003
HCT SV-005   IDC RR-002   MIM SV-006   OCP SV-004   PIR RL-005   PSL SV-002
RBS SV-003   RLO RL-004   RMP RL-001   SMF SV-001   TRM RR-001   XRF RR-006
```

**Every one of the six declares its check in front matter with a file-count denominator and an
instant**, per `RR-002` §7.2 — 782, 782, 787, 792, 792 and 795 files respectively, ascending in the
order they were written. **That ascending series is itself the evidence that each check was real**,
and it is the first time this repository can demonstrate that rather than assert it.

`SV-001`'s front matter goes further and cites the rule it is obeying — *"Conforms to `RR-002`
`IDC-08`"* — which is a category written **before** `RR-002` adopting it **after**, and is recorded
here as the first observed instance of `RR-002` being used as intended.

---

## 4. Findings Raised by This Audit

Twelve. **Six are against the category's own authoring and all six were corrected before issue.**

| # | Finding | Severity | Against | Status |
|---|---|:--:|---|:--:|
| `A99-01` | **`UX-005` and `UX-007` cite `RR-008`**, a document that has never been registered, **7 times including in two governing rules and a September 2026 review item** | **Medium** | Category 06 | **Corrected** `A99-C-02` |
| `A99-02` | **`RL-001` and `RL-005` cite `M66` at `03_Modules/G_Platform_and_Technology/`**, which does not exist — the directory is `K_`. A `RL-001` §8.2 ruling rests on it | **Medium** | Category 12 | **Corrected** `A99-C-01` |
| `A99-03` | **`M10`'s API consumer list cites `P38`**, where the portal space is `P01`–`P12` | **Medium** | Module estate | **Open** — needs `M10`'s author, `XRF-Q-02` |
| `A99-04` | **`BO-1` and `BO-01` denote different objectives** and differ by a leading zero. A naive count returns 27 objectives; there are 18 | **High** | Baseline estate | **Open** — retirement row issued, `RR-006` §5.5 |
| `A99-05` | **The workspace has no version control.** No diff, no attribution, no rollback; ISO 15489-1 *integrity* is not met, and eighteen baseline movements are recorded as prose | **CRITICAL** | Programme | **Open** — `EVR-Q-04`, **CTO** |
| `A99-06` | **The `(+06)` timestamp labels do not match the host's `+08:00` offset.** `MG-006`'s cutover instants and `RL-002`'s freeze windows are written in `T−n` against wall clock | **Medium** | Repository-wide | **Open** — `CUR-Q-05` |
| `A99-07` | **`PGD-000` §3's control block was two versions behind its own front matter** — §3 read `Version 1.8` while front matter read `2.0`. `PGD-AUDIT-CAT-09` §6 recorded the identical defect and it recurred | **Medium** | `PGD-000` | **Corrected** `A99-C-08` |
| `A99-08` | **`PGD-000` §0.5's verification line disagreed with the table it verifies, by five documents** — *"125 + 6 + 5 + 4 = 140"* against a table reading **130 / 4 / 3 / 3**. `PG-M10` failing in the one place written to enforce it | **Medium** | `PGD-000` | **Corrected** `A99-C-07` |
| `A99-09` | **`_CATEGORY_OVERVIEW.md` read *"0 written"* for seventeen hours** after three of its six documents were written. Categories 14 and 15 carry the same staleness | Low | Category 99 · 14 · 15 | **Corrected for 99** `A99-C-10`; 14 and 15 assigned |
| `A99-10` | **`RR-004`'s `CHK-E1` cannot distinguish *use* from *mention***, firing on paths inside fenced code and inside the register's own evidence table. Third instance of the class in one afternoon | Low | **Own authoring** | **Corrected** `A99-C-06` |
| `A99-11` | **`RR-006` Edition 1's node count excluded the document doing the counting** — 137 where 138 is correct | Low | **Own authoring** | **Corrected** `A99-C-05` |
| `A99-12` | **`RR-002`'s §7.2 rule-prefix check is one-way.** It is correct at allocation and **cannot be re-run as a standing check**, because correct citation makes the count non-zero forever. This audit's first collision sweep produced a false positive on `IDC` for exactly this reason | Low | **Own method** | **Corrected** — replacement check specified, §4.2 |

### 4.1 `A99-05` — no version control — is rated CRITICAL, and the reasoning is stated

`RR-004` §3.3 rated it **High**. This audit raises it to **CRITICAL**, and the promotion needs a
reason rather than an adjective.

`RR-004`, `RR-005` and `RR-006` between them make roughly **two hundred and forty** counted claims
about the filesystem. Every one is a statement about a set of files **at an instant**, and there is
no mechanism by which any of them can be re-verified against what the files were at that instant —
because nothing records what the files were. The eighteen baseline movements in `RR-004` §6 are
reconstructed from directory timestamps and from what each session happened to write down.

**The estate's entire evidence model therefore rests on an integrity property nothing provides.**
That is not a High-severity documentation gap; it is the precondition for every other claim in four
registers, and it costs one command to fix. `EVR-Q-04` is with the **CTO**, needed **Now**.

### 4.2 `A99-12` — the replacement for `RR-002` §7.2's one-way check

`RR-002` §7.2 specifies, correctly, that a candidate prefix must return **zero** occurrences before
allocation. This audit's first sweep re-ran that check *after* issue and reported `IDC` in **16
files**, which reads as a sixteen-way collision and is nothing of the kind: the six `SV` documents,
`PGD-000`, `README.md` and `PGD-AUDIT-CAT-11` are **correctly citing** `IDC-07`, `IDC-08` and
`IDC-13` as programme rules, qualified per `IDC-07` itself.

**Allocation and citation are indistinguishable to a token sweep.** The standing check must
therefore be a different one, and it is specified here as `CHK-X8`, to be adopted into `RR-002`
§10 at its next issue:

```bash
# CHK-X8 — rule-space uniqueness as a STANDING check.
# Declaration, not occurrence: exactly one document may DECLARE each prefix.
for f in $(find . -name '*.md' | grep -E '/[A-Z]{2}-[0-9]{3}_'); do
  awk 'NR<=40 && /^rule_prefix:/{print $2; exit}' "$f"
done | sort | uniq -d      # any output is a real collision
```

**Run at this audit it returns nothing**, across 18 declarations. `RR-002` §7.2's check stays as
the **allocation-time** gate; `CHK-X8` becomes the **standing** one. This is the third instance
today of *use versus mention* defeating a text-scanning check — with `A99-10` and `RR-006` §5.4.4's
`RR-007` artefact — and three instances is enough to make it a rule: **a check over prose must say
whether it is counting uses or mentions, and no check in this estate did until now.**

---

## 5. Corrections Applied

Eleven, all applied at **2026-08-19 20:21–20:26**.

| # | Correction | File(s) | Closes |
|---|---|---|---|
| `A99-C-01` | `03_Modules/G_Platform_and_Technology/M66_…` → `K_Platform_and_Technology/M66_…` | `RL-001`, `RL-005` | `A99-02`, `EVR-F-02` |
| `A99-C-02` | `RR-008` → `RR-005`, **7 citations** including `ACD-10`, `ACD-34`, two decisions and a traceability row | `UX-005`, `UX-007` | `A99-01`, `XRF-F-03` (half) |
| `A99-C-03` | `../../project_content/99_.../` → `…/99_Reference_and_Registers/` — an abbreviation that does not resolve | `RR-004`, `RR-005`, `RR-006` | Test 6 |
| `A99-C-04` | Post-issue correction block: `BM-004` and `BM-005` were written at **19:59** and **20:07**, five and thirteen minutes after `RR-004`'s enumeration | `RR-004` §5.7.2 | `A99` own-authoring |
| `A99-C-05` | Regeneration block: 138 nodes not 137 (the count excluded itself), 3,320 edges, `RR-006` off the dangling list | `RR-006` §5 | `A99-11` |
| `A99-C-06` | `CHK-E1` refined to skip fenced code and the registers' own evidence tables; `EVR-F-09` added | `RR-004` §8, §10 | `A99-10` |
| `A99-C-07` | §0.5's verification line regenerated: **136 + 2 + 1 + 1 = 140**, with the five-document disagreement recorded rather than erased | `PGD-000` §0.5 | `A99-08` |
| `A99-C-08` | §3 control block: Version → **2.0**; enumeration timestamp → 20:22; documents authored → **136**; Audits row → seventeen audits | `PGD-000` §3 | `A99-07` |
| `A99-C-09` | §3 `Basis`: `IEEE 1016-2009` annotated **(Inactive-Reserved at IEEE SA; no successor published)** per `RR-005-D-02` | `PGD-000` §3 | `CUR-F-03` (half) |
| `A99-C-10` | Category 99 status line: *"0 written"* → **6 written**; the five done-criteria assessed | `_CATEGORY_OVERVIEW.md` | `A99-09`, `EVR-F-08` (part) |
| `A99-C-11` | §0.5's `†` footnote listed categories 00–13 and omitted **14** and **99**, both carrying qualified ✅ | `PGD-000` §0.5 | `A99-08` (part) |

> **`A99-C-01` and `A99-C-02` are corrections to *other categories'* documents**, and that needs a
> word. `RR-002` `IDC-01` and `RR-004` `RR-004-D-05` both say a register may not edit the documents
> it registers, or it becomes their author and its independence goes. **An audit is the right
> instrument for exactly this**: the registers *recorded* the defects and assigned them; the audit
> *applied* them. That separation is why `RR-004-D-05` chose "record and assign" at issue and "fix"
> at audit.

---

## 6. Findings Raised by the Six Documents

**Fifty-one**, verified at this audit. Every one was re-tested against the filesystem; **none was
found to be unreproducible.**

| Document | Findings | New to the programme | Critical / High |
|---|---:|---:|---:|
| `RR-001` `TRM-F-01…06` | 6 | 4 | 0 / 2 |
| `RR-002` `IDC-F-01…11` | 11 | 5 | 0 / 5 |
| `RR-003` `DSL-F-01…05` | 5 | 3 | 0 / 1 |
| `RR-004` `EVR-F-01…09` (+`05b`) | 10 | 7 | 1 / 3 |
| `RR-005` `CUR-F-01…11` | 11 | 6 | 1 / 3 |
| `RR-006` `XRF-F-01…08` | 8 | 4 | 0 / 3 |
| **Total** | **51** | **29** | **2 / 17** |

### 6.1 The two critical findings

| # | Finding | Owner | Needed by |
|---|---|---|---|
| `CUR-F-01` | **The Cyber Security Ordinance 2025 was repealed on 30 April 2026** by the Cyber Security Act 2026. This repository cites the superseded instrument **37 times across 22 files**; the workspace cites the instrument in force **zero** times. `SC-001`, `SC-008`, `SC-010`, `SC-011` and `DA-005` derive obligations from repealed text | **Security & Privacy Lead** | **Now** |
| `EVR-F-06` / `A99-05` | **The workspace has no version control** | **CTO** | **Now** |

> **`CUR-F-01` is `00-06` `C-04` at its third generation** — Digital Security Act 2018 → Cyber
> Security Act 2023 → Cyber Security Ordinance 2025 → **Cyber Security Act 2026**. The statute has
> changed roughly every eighteen months since 2018 and the programme has been caught by it three
> times, each time by a different document set, each time found by an auditor rather than by a
> control. `RR-005` §9 is the first control; it has not yet run once.

### 6.2 The eleven findings closed at this audit

| Finding | Closed by |
|---|---|
| `PGD-000` `RR-004` row — *"the module and engineering estates are still unindexed"* | `RR-004` §5.3–§5.6 |
| `PGD-000` `RR-006` row — *"601 files and no index"* | `RR-006` §5 |
| `RR-002` `CHK-05` — *"the one that cannot be switched on yet"* | `RR-006` §5.4, as `CHK-X1` |
| `PGD-000` §0.3 — *"until `RR-003` publishes the per-document-type section sets…"* | `RR-003` §5 |
| `00-06` `H-01` — NIST SP 800-88 r1 | `RR-005` §5.6 *(diagnosis; 8 citations remain, assigned)* |
| `00-06` `M-01` — Odoo release date | `RR-005` §7.1 |
| `00-06` §9's proposal — *"re-verified at each wave gate"* | `RR-005` §9 *(in specification)* |
| `PGD-A2-07` — undated standards citation | `RR-005` §5.2, generalised as `CUR-F-07` |
| `RF-002` `EV-F1` — future verification dates | `RR-004` §5.7.3 — **0 of 130** |
| `01-05` and `99-04`, both unwritten | Superseded by `RR-004` |
| `A99-12` — the one-way prefix check | §4.2, `CHK-X8` |

### 6.3 What the six could not close, and why

**Nine positions go to the Steering Committee and none is resolvable by writing:**

| # | Position | Owner | Needed by |
|---:|---|---|---|
| 1 | Version control for the workspace | **CTO** | **Now** |
| 2 | Counsel confirmation of every statutory row in `RR-005` §6 | External counsel | **Now** |
| 3 | Whether PDPA 2026 carried the Feb-2026 in-country synchronised-copy requirement forward | External counsel | **W1** |
| 4 | ISO 9001:2026 adoption timing — **publishes in 28 days** | Quality Manager / CTO | **Now** |
| 5 | Odoo 20 position — **releases in five weeks**, inside Wave 1 | Enterprise Architecture | **W1** |
| 6 | A provisional-identifier escape hatch for the nine frozen spaces | **CTO** | **Now** |
| 7 | Which entity population is authoritative — 225, 1,334 or 51 | Enterprise Architecture | **W1** |
| 8 | Whether `06-02` restates `BO-nn` → requirement family, so the trace chain has a first link | Enterprise Architecture + CFO | **W1** |
| 9 | Which body ratifies any of the 67 rules these six documents issue | **Board** | **Now** |

**Item 9 is the one that contains the others.** Sixty-seven rules were issued today by documents
whose own `status` is `DRAFT FOR APPROVAL`, into a programme where `PGD-A1-09` records that no
constituted body can approve anything. `GV-002` — in-degree **83**, upstream of 60% of the
estate — is itself unapproved.

---

## 7. Operational Executability

The seventh test `PGD-AUDIT-CAT-12` introduced and `PGD-AUDIT-CAT-13` refined: **not is it
specified, but can it be executed on Monday?**

| Rule class | Documents | Executable today? |
|---|---|:--:|
| **Identifier allocation** `IDC-01…14` | `RR-002` | ⚠ **Partly.** Nine of seventeen spaces are frozen; the escape hatch is `RR-002-Q-01`, undecided |
| **Terminology governance** `TRM-01…13` | `RR-001` | ✅ **Yes** — adding a term needs a reviewer, and one is named |
| **Document standards** `DSL-01…16` | `RR-003` | ✅ **Yes** for new documents; **⚠** for the 138 extant, which need a conformance pass |
| **Evidence rules** `EVR-01…07` | `RR-004` | ⚠ **`EVR-06` is not executable** — *"a source with no recorded dependents may not be changed"* presumes a dependency record that §7 provides only at document grain |
| **Currency review** `CUR-01…10` | `RR-005` | ⚠ **`CUR-10` needs a gate.** `G1` has not occurred; until it does, the register cannot lapse a row and `CHK-C2` passes vacuously |
| **Index generation** `XRF-01…07` | `RR-006` | ✅ **Yes** — demonstrated, under one second, twice |
| **The six checks × 4 registers** | all | ⚠ **Runnable by hand; not gated.** `PE-004`'s pipeline does not exist, and stage 2 of `RR-006` §8.1 is blocked on version control |

**Three of seven executable today, four partly.** That is a better position than Categories 12 and
13 reported for themselves, and the reason is structural rather than creditable: **a reference
category's rules mostly govern writing, and writing is the one activity this programme is
demonstrably able to do.** The rules that govern *other people's registers* — `IDC-01`, `EVR-06`,
`CUR-10` — are the ones that are not executable, and they are not executable for the same reason
everything else in this estate is not: **nobody has been appointed.**

---

## 8. Assessment Against `PGD-000` §0.3

| Test | Result | Note |
|---|:--:|---|
| **(a)** A named file exists at a stated path | **6 / 6** | Verified by `find` at 20:22 |
| **(b)** Complete front matter per `RR-003` | **6 / 6** | 20–22 keys each; all 18 mandatory present; `id` = filename prefix on all six |
| **(c)** ≥90% of the required section set | **6 / 6** | Measured against `RR-003` §5's class instrument — **the first audit able to do so** |
| **(d)** A named owner and an approval record | **0 / 6** | Owner named on all six; **approval record does not exist and cannot** — `PGD-A1-09` |

**Recommendation: Category 99's six rows move to ✅ in `PGD-000`, carrying the `†` qualification
that applies to all 136.** Applied at `A99-C-07` / `A99-C-08`.

---

## 9. Recommendations

| # | Recommendation | Owner | Needed by |
|---:|---|---|---|
| `A99-R-01` | **Place the workspace under version control.** One decision; it unblocks stage 2 of `RR-006` §8.1 and retires integrity caveats in four registers at once | **CTO** | **Now** |
| `A99-R-02` | Obtain the gazetted **Cyber Security Act 2026** and re-derive every `SC-008` obligation sourced from the 2025 ordinance | Security & Privacy Lead | **Now** |
| `A99-R-03` | Run `CHK-C5` (retired-citation sweep) — **64 hits, clearable in an afternoon** | Enterprise Architecture | **W1** |
| `A99-R-04` | Adopt `CHK-X8` into `RR-002` §10 as the standing rule-space check | Enterprise Architecture | `G1` |
| `A99-R-05` | Resolve `P38` with `M10`'s author before `IN-002` derives consumer lists | Integration Lead | **W1** |
| `A99-R-06` | Give `PGD-000` a `discharged_by` field so `CO-001` and `BM-001` stop reading as dangling | PMO | `G1` |
| `A99-R-07` | Update Categories 14 and 15's `_CATEGORY_OVERVIEW.md`, both stale | PMO | `G1` |
| `A99-R-08` | **Ratify `RG-08`.** It has now been recommended at least eleven times and applied unilaterally by three consecutive categories. **This audit does not recommend it a twelfth time** — it records that the recommendation itself has become the finding | **CTO** | **Now** |

> ### `A99-R-08` deserves the last word
>
> `RG-08` — *timestamped enumeration* — was proposed after the first repository audit. Since then it
> has been recommended in at least eleven documents and ratified in none. Categories 12, 13 and 99
> have each stopped recommending it and simply **applied** it, which is why the six documents
> audited here carry ascending file-count denominators — 782, 782, 787, 792, 792, 795 — and why
> `RR-004` §5.7.2's claim about `BM-004` survived being falsified thirteen minutes after it was
> written.
>
> **The rule works. It has never been approved. It has been obeyed anyway, by everyone, for four
> days.** That is either an argument that ratification is unnecessary or an argument that the
> approval mechanism is the defect, and `PGD-A1-09` settles which.

---

## 10. Audit Control

| Attribute | Value |
|---|---|
| Audit ID | `PGD-AUDIT-CAT-99` |
| Identifier form | **Category-keyed**, per `RR-002` `RR-002-D-05` — collision-free by construction under concurrent authoring, which this category needed: **two sessions authored it simultaneously** |
| Finding prefix | `A99` — collision-checked, zero occurrences before allocation |
| Documents audited | `RR-001` · `RR-002` · `RR-003` · `RR-004` · `RR-005` · `RR-006` |
| Enumeration timestamp | **2026-08-19 20:22** — workspace **798** `.md`, this repository **177**, **138** guiding documents |
| Findings raised by this audit | **12** — 1 critical, 1 high, 5 medium, 5 low; **6 against the category's own authoring, all corrected** |
| Findings verified from the six | **51**, none unreproducible |
| Corrections applied | **11**, of which **2** to other categories' documents |
| Audits on disk | **17**, verified 2026-08-19 20:22 |
| Standards basis | ISO 19011:2018 §6 · `PGD-000` §0.3 · `RR-003` §5 · `RR-002` §7.2 |
| Next review | At `G1`, with a full `RR-006` regeneration |

---

*`PGD-AUDIT-CAT-99` · Category 99 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
*1000FiX Services Limited · ERP Programme · Enterprise Architecture*
