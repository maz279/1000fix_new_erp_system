---
id: PGD-AUDIT-CAT-12
title: Category 12 — Release, Deployment & Transition — Category Audit
category: 12 — Release, Deployment & Transition
code: RL
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-19
status: ISSUED
classification: CONFIDENTIAL — Internal Use Only
auditor: Enterprise Architecture (NOT INDEPENDENT — see §12)
scope: >
  The six documents of Category 12 — RL-001…RL-006 — audited against PGD-000 §0.3's four ✅ tests,
  the seventh method (operational executability) added by PGD-AUDIT-CAT-09, and the register's own
  rules PG-01, PG-03, PG-06, PG-M4, PG-M10, DL-06 and MST-01.
enumeration_timestamp: 2026-08-19 02:41 (+06) — fifth enumeration of the session
audited_documents: 6
findings: 24
findings_closed_by_this_category: 9
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# `PGD-AUDIT-CAT-12` — Category 12 Audit
# Release, Deployment & Transition

**Six documents · 272 governing rules · 24 findings · 9 closures · enumerated from disk 2026-08-19 02:41 (+06)**

---

## 1. Scope and Method

### 1.1 What was audited

| ID | Document | Version | Rule space | Rules | Priority |
|---|---|:--:|:--:|---:|:--:|
| `RL-001` | Release Management & Versioning Policy | 1.1 | `RMP` | **47** | P1 |
| `RL-002` | Deployment Plan & Go-Live Checklist | 1.1 | `DPY` | **49** | **P0** |
| `RL-003` | Go-Live Readiness Assessment & Gate Criteria | 1.1 | `GLR` | **31** | **P0** |
| `RL-004` | Rollout & Branch Wave Deployment Plan | 1.1 | `RLO` | **43** | **P0** |
| `RL-005` | Post-Implementation Review Standard | 1.1 | `PIR` | **45** | P2 |
| `RL-006` | Legacy Decommissioning Plan | 1.1 | `DCM` | **57** | P1 |
| | **Total** | | | **272** | |

Rule counts obtained by `grep -oE '`<PREFIX>-[0-9]{1,3}[a-z]?`' | sort -u | wc -l` per file at
2026-08-19 02:41 (+06), and reconciled against each document's own consolidated rules table.

### 1.2 Method

Seven tests. The first four are `PGD-000` §0.3's; the fifth and sixth are this repository's
standing audit practice; the seventh was added by `PGD-AUDIT-CAT-09` and is retained because this
category, like Category 09, specifies an **operation** rather than a design.

| # | Test | Applied how |
|:--:|---|---|
| **T1** | A named file exists at a stated path | `test -f` on all six; all pass |
| **T2** | Complete front matter per `RR-003` | Field-by-field against `_templates/TPL_Guiding_Document.md` |
| **T3** | ≥ 90% of the governing standard's section set, counted section by section | §4 |
| **T4** | A named owner and an approval record | §5 — **fails**, as it does for all 119 ✅ documents |
| **T5** | Identifier integrity — no collision, no gap, no duplicate | §6 |
| **T6** | Every quantitative claim reproducible from the cited source | §7 |
| **T7** | **Operational executability** — could the thing specified actually be done tomorrow? | §8 |

### 1.3 Enumeration, and why every count in this audit carries an instant

The estate moved **five times** during this category's authoring and audit window:

| # | Time (+06) | `project-guide-doc` `.md` | What changed |
|:--:|---|---:|---|
| 1 | 2026-08-18 23:27 | **133** | Category 12 folder empty but for its overview |
| 2 | 2026-08-19 01:15 | **147** | **Category 10 `PE-001`…`PE-009` authored**; `CH-001`…`CH-004` authored |
| 3 | 2026-08-19 01:40 | **156** | `CH-005`, `SV-001`…`SV-003`, `PGD-AUDIT-009`, `PGD-AUDIT-CAT-13` authored |
| 4 | 2026-08-19 02:25 | **156** | Category 12's six documents issued and corrected |
| **5** | **2026-08-19 02:41** | **161** | **`SV-004` and `SV-005` authored** — a fifth movement, during this audit |

Workspace total at the final enumeration: **782** markdown files (`primary-doc` 4 ·
`1000fix_ERP_Module` 123 · `project_content` 488 · `old-primary-doc` 6 · `project-guide-doc` 161).

> **The fifth movement is the most instructive of the five.** `SV-004` and `SV-005` were issued
> while this audit was being written, and they invalidated fourteen absence assertions across four
> Category 12 documents. **All fourteen were corrected and not one changed a status**, because every
> one of them was already blocked by a missing *capability* — no rota staffed, no paging platform,
> no test performed — and only the *attribution* moved. `RL-003` `GLR-31`, written before `SV-004`
> existed, states the principle that made the correction mechanical: **an evidence item is
> discharged by the evidence, never by the issue of the specifying document.**

> **This is `RG-08` / `PGD-A1-03` / `AP-17` / `CHA-12` occurring again — Category 13's audit,
> issued the same night, called it *"at least the ninth recorded baseline movement during
> authoring"* — and for the first time it caused measurable damage to a **ruling** rather than only
> to a count.** Findings `RLA-13`, `RLA-14`, `RLA-16` and `RLA-17` are all one defect: three of this
> category's documents made status assertions about Category 10 that were true when written and
> false three hours later. §9 treats it as the category's principal process finding.

---

## 2. Summary of Findings

| Severity | Count | IDs |
|---|---:|---|
| **CRITICAL** | **2** | `RLA-07`, `RLA-18` |
| **HIGH** | **4** | `RLA-06`, `RLA-09`, `RLA-22`, `RLA-23` |
| **MEDIUM** | **9** | `RLA-01`, `RLA-08`, `RLA-10`, `RLA-11`, `RLA-13`, `RLA-14`, `RLA-19`, `RLA-21`, `RLA-24` |
| **LOW** | **9** | `RLA-02`, `RLA-03`, `RLA-04`, `RLA-05`, `RLA-12`, `RLA-15`, `RLA-16`, `RLA-17`, `RLA-20` |
| | **24** | |

**Five findings are against this category's own work** — `RLA-13`, `RLA-14`, `RLA-15`, `RLA-16`,
`RLA-17` — and **all five are corrected at v1.1** before this audit issued.

### 2.1 What the category closed

| # | Closed | Was recorded in | Closed by |
|:--:|---|---|---|
| 1 | `RL-001` ◐ — *"the release process that produces them is undefined"* | `PGD-000` | `RL-001` §4, §5, §7, §8 |
| 2 | `RL-002` ⛔ — *"`06-06` planned, never written"* | `PGD-000` | `RL-002` — `06-06` **superseded**, not awaited |
| 3 | `RL-003` ⛔ | `PGD-000` | `RL-003`, scoped to the residual gap after `GV-009` |
| 4 | `RL-004` ◐ — *"the site-by-site plan does not exist"* | `PGD-000` | `RL-004` §4, §5, §7, §11 |
| 5 | `RL-005` ⬜ | `PGD-000` | `RL-005` |
| 6 | `RL-006` ⛔ | `PGD-000` | `RL-006` |
| 7 | **`MG-006` `Q-01`** — *"`RL-002` is unwritten; this rule is the interface it must honour"* | `MG-006` §2.3 `CUT-01` | `RL-001` `RMP-25`/`RMP-26` supply the two missing dates; `RL-002` §7 and §10 make *"smoke-tested"* and *"stable"* measurable |
| 8 | **`MG-007` `Q-04`** — *"`RL-006` must not retire a source until … a declared stabilisation period has passed"* | `MG-007` `RBK-16` | `RL-006` §6.3 `DCM-13` derives the period |
| 9 | **`SP-031`'s open Definition-of-Done item** — *"CAB membership, cadence and quorum defined — outstanding"* | `SP-031` §DoD | `RL-001` §8.2 constitutes the CAB |

---

## 3. Findings

### 3.1 CRITICAL

---

#### `RLA-07` — A wave's rollout outlasts the wave

**Raised by** `RL-004` §7.6 · **Against** `06-01` §6, `OP-002` §4.3/`HD-03` · **Severity CRITICAL**

`OP-002` §4.3 sets hypercare duration per wave — W2 at **6 weeks** — and `HD-03` runs the wave-level
hypercare clock **from the last tranche** where a wave rolls out to branches in tranches. `RL-004`
§7 computes the tranche rate for the first time, from `05-04` §5's branch-resident headcount
(**538 – ≥873**, counted) and `OP-002` §4.4's floor-walking ratios: **2–3 sites per week**, giving
**15–30 weeks** for the 45 subsequent sites.

**W2 occupies Months 5–8 — approximately 17 weeks.** At the high-population rate the rollout alone
exceeds the wave, and its hypercare then ends inside W3, whose cutover carries a witnessed cash
count at every site.

| Route out | Cost | Decision sits with |
|---|---|---|
| Fund contracted floor-walkers | 45–90 floor-walker-weeks plus travel to eight divisions | Steering Committee via `GV-008` |
| Extend the wave schedule | W2 and W4–W5 lengthen; the 36-month programme moves | Steering Committee via `GV-004` |
| Reduce the floor-walking ratio | **Not available** — `RLO-26`; `OP-002` §4.4 names it the highest-yield activity and the first one cut; `06-01` §7 rates field adoption risk **Critical** | — |

**Remediation `R-01`:** `RL-004` `Q-02` to the Steering Committee by **W1**. The two available
routes spend different currencies and neither is a delivery decision.
**Status: OPEN.**

---

#### `RLA-18` — Sixteen declared Bengali counterpart files do not exist

**Raised by** `MG-006` §7.3 as `MGA-06`; **independently re-verified** by `RL-004` §12.2 ·
**Against** `project_content` Categories 16 `CM` and 17 `OP` · **Severity CRITICAL**

Counted at 2026-08-19 02:25 (+06):

| Measure | Count |
|---|---:|
| Files in `16_CM` and `17_OP` declaring `bilingual: yes` and naming a `_BN.md` counterpart | **16** |
| `_BN.md` files present anywhere in `project_content` | **0** |

The sixteen include **`CM-012_Branch_Readiness_Communication_Checklist_BN.md`** — the checklist every
branch manager works from — and **`OP-014_Manual_Fallback_Procedure_Set_BN.md`** — the fallback
51+ branches would work from during a rollback.

**What it blocks, beyond the cutover rules `MG-006` raised it against:**

| Rule | Document | Effect |
|---|---|---|
| `RLO-15` | `RL-004` | The per-site readiness bar is issued in a language much of the branch population does not work in |
| `RLO-35`, `RLO-36` | `RL-004` | `OP-014` fallback cannot be physically present in Bengali before `S−0` |
| `RLO-39` | `RL-004` | A pause cannot be declared to every site within one working day |
| `RL-003` `RD-5` `O-4` | `RL-003` | Cannot be evidenced |
| `CV-09`, `CUT-23` | `DM-014`, `MG-006` | Already recorded; unchanged |

`CM-012` is additionally registered **`P1`** against a **`P0`** rollout that cannot proceed without it.

**Remediation `R-02`:** translate `CM-012` and `OP-014` first; re-prioritise `CM-012` to `P0`.
Owner: Content Design with the Change Lead, by **W1 minus 2 months** (`RL-004` `Q-04`, `Q-05`).
**Status: OPEN — this is the single item that most directly prevents Wave 1 rollout.**

---

### 3.2 HIGH

---

#### `RLA-06` — The rollout rate had never been computed

**Raised by** `RL-004` §7 · **Against** `06-01` §6 · **Severity HIGH**

`06-01` §6 and RFP §12.6 give a geographic *direction* — pilot → Dhaka → major cities → national —
and imply the network is live by W4–W5. **No document multiplies the floor-walking ratios by the
headcount by the team model.** `RL-004` §7 does, and the answer bounds everything else in the
rollout. The finding is that a programme with 51+ sites and a 36-month schedule had no rate.

**Remediation `R-03`:** `RLO-25` — recompute from measured walker-hours after the W1 pilot;
`RL-005` `DP-2`/`DP-3` make it a standing wave-review measure so the estimate is corrected at W1
rather than discovered at W5. **Status: CLOSED in specification; open in execution.**

---

#### `RLA-09` — No wave review may claim any benefit until `BM-002` issues

**Raised by** `RL-005` §7.3 · **Against** `BM-002` ⛔ · **Severity HIGH**

`06-02` §6: *"Every KPI's baseline is measured and signed off **before** the relevant wave begins.
**A KPI without a baseline cannot claim a benefit.**"* `BM-002` (KPI Baseline Measurement Report) is
**⛔** and registered `needed_by: Now`.

This is a **precondition, not a quality standard**. `PIR-27` therefore reports `A3` as *"not
claimable — no baseline"* at every review held before `BM-002` exists.

> **The damage is permanent, not deferred.** A baseline cannot be captured retrospectively once the
> system that would change it is live. Every month `BM-002` slips forecloses a wave's benefit claim
> irrecoverably, and `06-02` §3.2's realisation curve — 45 → 310 → 645 → 876 BDT lac — becomes
> unverifiable from the bottom up.

**Remediation `R-04`:** `BM-002` before W1 begins. Owner: Programme Director with benefit owners
(`RL-005` `Q-01`). Escalate to `GV-005` as a **Critical** dependency.
**Status: OPEN.**

---

#### `RLA-22` — `PE-002` predicted a divergence, and it happened, in this category, the same day

**Raised by** this audit · **Against** the repository's concurrent-authoring practice ·
**Severity HIGH**

`PE-002` `PE-002-F-01`, issued 2026-08-19, states:

> *"`QA-001` and `QA-005` planned against list B; `PE-004`'s promotion path and **`RL-002`'s release
> process will plan against list A**. The divergence is invisible until two teams discover they
> built for different ladders."*

**`RL-002` v1.0 was at that moment doing exactly that.** It reconciled TSS §18.3's five deployment
targets with `QA-001` §7.1's seven test environments into **ten**; `PE-002` reconciled `02-05` §9 /
`AR-001` §8.5's six with `TS-001` §4.7's six into **twelve**. Two documents, same day, same
programme, two different environment inventories — differing by `local` and `migration-staging`.

The prediction was correct, it was published, and it was invisible to the session it described,
because **no mechanism in this repository notifies an author that a document they depend on has just
been written.**

**Remediation `R-05`:** corrected in `RL-002` v1.1 (`RLA-13`). The structural fix is `RG-08` —
proposed, recommended for the **eighth** time in this audit, never ratified — plus `RR-006`'s
cross-reference index. **Status: instance CLOSED; class OPEN.**

---

#### `RLA-23` — Three go-live-critical roles have a company-wide establishment of two or fewer

**Raised by** `RL-004` §8 `RLO-30` · **Against** `05-04` §5 · **Severity HIGH**

| Role | `05-04` §5 establishment | Go-live-critical at |
|---|:--:|:--:|
| `R30` HR Manager | **1–2** | W5 — payroll, zero-tolerance |
| `R26` Finance Manager | **2–4** | W3, W5 |
| `R32` Quality Manager / ISO Coordinator | **2–4** | W5 — ISO audit |

`RL-003` `RD-6` `P-4` requires *"at least two trained people"* per go-live-critical role. **For these
three that is not a redundancy target; it is the entire establishment**, and a single absence at W5
is a programme-wide `RD-6` veto under `GLR-11`.

**Remediation `R-06`:** `RL-004` `Q-03` — HR Director with the Programme Director, by **W5 minus 6
months**. **Status: OPEN.**

---

### 3.3 MEDIUM

---

#### `RLA-01` — `BE-003` §9 step 6 mis-cites `RL-003` for emergency change

**Raised by** `RL-001` §9.4 · **Against** `BE-003` · **Severity MEDIUM**

`BE-003` §9 step 6 reads *"deploy under **`RL-003`** emergency change."* `RL-003` is the Go-Live
Readiness Assessment and has no emergency change route. The route is `RL-001` §9 (authority) and
`RL-002` §13 (execution). `BE-003` §14 repeats the mis-citation in its traceability table.

**Remediation `R-07`:** `BE-003` v1.1 to read *"deploy under `RL-001` §9 emergency change, executed
per `RL-002` §13."* Owner: Engineering Lead (`RL-001` `Q-07`). Until then `RL-001` §9.4 is the
authority and says so explicitly, so a reader reaching `RL-003` does not conclude the route is
undefined. **Status: OPEN, mitigated.**

---

#### `RLA-08` — Two workforce denominators coexist estate-wide

**Raised by** `RL-004` §3.3 · **Against** the whole estate · **Severity MEDIUM**

Counted at 2026-08-19 02:25 (+06) across all 777 markdown files:

| Figure | Occurrences |
|---|---:|
| *"500+ employees"* / *"500+ staff"* | **90** |
| *"800+ employees"* / *"800+ staff"* / *"800+ people"* | **35** |

No document reconciles them. This is the `GA-04` defect class — *a percentage carries its
denominator* — applied to a headcount, and the same class as `AUDIT-014` `TS-01`'s five coverage
denominators. It matters because **floor-walker demand, training volume and licence count are all
computed from headcount**, and a 60% difference in the denominator propagates into all three.

`RL-004` §7.2 avoids both figures and computes from `05-04` §5's per-role headcounts directly, which
is the only source that can be counted rather than quoted.

**Remediation `R-08`:** one figure, ruled and dated, routed to `RR-005` and `GV-005`
(`RL-004` `Q-07`). **Status: OPEN.**

---

#### `RLA-10` — `GV-001` §12.1's programme-closure criterion cannot be met as written

**Raised by** `RL-006` §4.3 · **Against** `GV-001` §12.1 · **Severity MEDIUM**

`GV-001` §12.1: *"All 48 legacy systems decommissioned."* Counted from `DM-002` §2.2 by script at
2026-08-19 02:25 (+06):

| Disposition | Count |
|---|---:|
| **`R` Retire** — carries a decommission wave | **32** |
| **`K` Keep by design** — `SRC-020`, `SRC-021`, `SRC-022`, `SRC-031` marked *"Retained"* | **4** |
| **`P` Purge only** — `SRC-023`, destroyed not retired | **1** |
| **`N` Not a system** — 3 `PEOPLE`, 4 `PUB`, 4 `CFG` | **11** |
| | **48** ✓ |

Reporting a retained payment-gateway portal as *"decommissioned"* would be a false statement inside
a closure criterion. `DCM-04` restates it as four criteria, three of which previously had no owner.

**Remediation `R-09`:** `GV-001` v1.1 §12.1 to adopt `DCM-04` (`RL-006` `Q-03`).
**Status: OPEN.**

---

#### `RLA-11` — `DM-002` and RFP §4.3 are two unreconciled enumerations of "legacy"

**Raised by** `RL-006` §4.2 · **Severity MEDIUM**

`DM-002` registers **32 retirable sources**; RFP §4.3 commits contractually to **21 practices**.
Counted per wave at 2026-08-19 02:25 (+06):

| Wave | `DM-002` sources | RFP practices |
|:--:|---:|---:|
| W2 | 10 | 7 |
| W3 | 6 | 3 |
| W4 | 3 | 2 |
| W5 | 9 | 4 |
| W6 | 3 | 3 |
| W7 | 1 | 1 |
| W8 | **0** | **1** |
| | **32** | **21** |

`DCM-02` establishes that a source and a practice are different objects and 48 ≠ 21 is not an
error. The finding is that **nine sources carry a retirement wave and no contractual
accountability**: `SRC-011`, `SRC-012`, `SRC-018`, `SRC-017`, `SRC-030`, `SRC-033`, `SRC-035`,
`SRC-034`, `SRC-028`.

**Remediation `R-10`:** `DCM-08` marks all nine in the decommission register so a vendor scope
discussion can see them. **Status: CLOSED in specification.**

---

#### `RLA-13` — `RL-002` v1.0 ruled ten environments against `PE-002`'s twelve

**Self-audit finding.** See `RLA-22` for the cause. `RL-002` §3.1 v1.0 ruled *"the programme has ten
environments"* and stated the table stood *"until `PE-002` issues and supersedes it"* — `PE-002`
issued the same day. **Corrected in `RL-002` v1.1**: `PE-002` §4.2's twelve are adopted whole and
`RL-002` retains only the promotion path, which `PE-002` §4.1 delegates to it.
**Status: CLOSED.**

---

#### `RLA-14` — `RL-002` v1.0 ruled `Recreate`-only and `NFR-008` unachievable

**Self-audit finding.** `RL-002` `DPY-09` v1.0 stated `Recreate` was the only executable deployment
model, and `DPY-13` v1.0 stated *"`NFR-008` is not achievable … and no document has said so."*
`PE-004`, issued the same day, assigns a strategy per component (rolling for Odoo nodes, blue/green
for portals) and states `NFR-008` **is** achievable under four conditions.

**Corrected in `RL-002` v1.1**: `PE-004` §8.1 adopted; `NFR-008` restated as **specified, not
demonstrated**, with `PE-004-F-02`'s condition 3 — the readiness-check contract — named as the gap
and checklist item `E-07` added to measure it. **Status: CLOSED.**

---

#### `RLA-19` — Three-way `RB-` rule-prefix collision

**Raised by** this audit · **Against** `CM-012`, `OP-002`, `PE-004` · **Severity MEDIUM**

| Document | Rules | Meaning |
|---|---|---|
| `CM-012` §4 | `RB-01` … `RB-12` | **R**eadiness **B**ranch |
| `OP-002` §4.7 | `RB-01` … `RB-04` | **R**oll**B**ack |
| **`PE-004` §8.4** *(issued 2026-08-19)* | `RB-01` … `RB-05` | **R**oll**B**ack |

Three documents, three meanings, overlapping numbers. `CM-012` `RB-01` is *"readiness is eight
domains"*; `OP-002` `RB-01` is *"rollback is a business decision"*; `PE-004` `RB-01` is *"rollback is
redeploying the previous artefact digest"*. All three are cited across the estate, and Category 12
cites `CM-012`'s and `OP-002`'s in the same documents.

This is the defect class behind `H-03` (48 colliding `CD` identifiers), `H2-04` (22 colliding `KPI`
identifiers) and `PGD-A1-01`, and it is the reason Category 12 verified all six of its own prefixes
against every `[A-Z]{2,6}-[0-9]{1,3}` token in the workspace before allocating any of them.

**Remediation `R-11`:** `RR-002` (Identifier Convention Standard) — ⛔, recommended for the **eighth**
time. Interim: every Category 12 citation of an `RB-` rule names its document
(`CM-012` `RB-08`, never bare `RB-08`), which all six documents already do.
**Status: OPEN; Category 12 mitigated.**

---

#### `RLA-21` — `M66` §4 and `SP-031` §3 contradict each other on the CAB

**Raised by** `RL-001` §4.6 · **Severity MEDIUM**

`SP-031` §3/§5.3/§7 requires a Change Advisory Board with membership, quorum and an approval record;
`M66` §4 lists *"a formal Change Advisory Board meeting cadence"* under **what is not adopted**,
because *"a weekly meeting would delay more than it protects at our change volume"*. Both are
current, approved documents.

**Ruled in `RL-001` `RL-001-D-01`:** the word doing the damage is *"meeting"*. §8.2 constitutes the
CAB as a named body with an **asynchronous default** and a **convened exception** for High-risk
changes, satisfying `SP-031`'s control and `M66`'s throughput objection together — and discharging
`SP-031`'s open Definition-of-Done item in the process.
**Status: CLOSED by ruling; `SP-031` and `M66` should cross-reference §8.2 at their next revision.**

---

#### `RLA-24` — `PGD-000` §3's repository file count is stale by 20

**Raised by** this audit · **Against** `PGD-000` §3 Register Control · **Severity MEDIUM**

`PGD-000` §3 reads *"`project-guide-doc` is **136**, not 115 (`MGA-15`)."* Counted at
2026-08-19 02:25 (+06): **156 markdown files, 167 files in total**.

The figure was correct when written and is not now. `PG-M10` requires a figure appearing in more
than one place to be regenerated in every place; §3 is the fourth place the repository count
appears, and it is the one that drifts.

**Remediation `R-12`:** §3 updated at this issue with the counted figure and a timestamp.
**Status: CLOSED at this issue; recurrence prevented only by `RR-006`, which is ⬜.**

---

### 3.4 LOW

| # | Finding | Against | Status |
|---|---|---|---|
| `RLA-02` | **`PGD-000`'s `RL-003` row justification is stale.** It reads *"`06-02` §4 … does not define readiness assessment — who checks, against what evidence, with what authority to stop a go-live."* `GV-009` §4 and §5 have since defined evidence classes and assessors. `RL-003` §2.4 states the residual gap precisely rather than inheriting a superseded framing | `PGD-000` | **CLOSED** — the row is rewritten at this issue |
| `RLA-03` | **`06-01` §5 cites "all 15 criteria" for the Definition of Done; `02-02` §8 and RFP §12.5 both carry 17** (`DoD-01`…`DoD-17`, the last added after audit finding `C-04`) | `06-01` §5 | **OPEN** — already handled authoritatively by `RQ-010`; recorded here because Category 12 consumes `DoD-16` |
| `RLA-04` | **`OP-002`'s per-wave hypercare durations (8/6/8/6/8/4/6/4/6 weeks) contradict `06-01` §5 and RFP §12.6, which both state a flat "four weeks of elevated support after every wave go-live"** | `06-01`, RFP | **OPEN** — `OP-002` is the later and more derived document and is treated as authoritative by `RL-001` `F6` and `RL-005` §4.4 |
| `RLA-05` | **`CH-002` §4.2 converts `05-04` §5's `"51+"` for `R06`, `R18` and `R29` into `"51–60"`** — a reasonable working assumption presented in a source-figure column | `CH-002` | **OPEN** — `RL-004` `RLO-21` uses the floor instead and says so |
| `RLA-12` | **RFP §4.3 commits to retiring *"Excel management reporting packs"* at W8; `DM-002` registers no such source and no W8 decommission at all** | RFP §4.3, `DM-002` | **OPEN** — `DCM-07` registers it as an unmapped contractual commitment with an owner (`RL-006` `Q-04`) |
| `RLA-15` | **Self-audit.** `RL-002` §8.3 read *"58 items across **8** sections"* while §1.2 read *"nine sections"* and the checklist carried nine section headings — a correct total beside a wrong component, the `PGD-A2-24`/`QAA-12` class, **inside a document that cites that class twice** | `RL-002` | **CLOSED** — recounted to 59 items across 9 sections at v1.1 |
| `RLA-16` | **Self-audit.** `RL-001` §12.3 attributed six unmeasurable release metrics to `PE-004` and `PE-008` **being absent**; both issued the same day and the blockage is **implementation** | `RL-001` | **CLOSED** at v1.1; `Q-08` added because neither `PE-004` nor `PE-008` cites `RMP-M1`…`RMP-M5` as a telemetry consumer |
| `RLA-17` | **Self-audit.** Six `RL-003` evidence items were written against absent documents; all six corrected, **none changed status**, because each was blocked by a missing capability rather than a missing document | `RL-003` | **CLOSED** at v1.1; §11.4 and `GLR-31` added |
| `RLA-20` | **`PGD-000` §3's audit-identifier note is now understated.** It records the numeric space at `001`–`008` and the category-keyed space at `CAT-07`/`CAT-09`. Counted at 2026-08-19 02:25: numeric `001`–**`009`**, category-keyed `CAT-07`, `CAT-08`, `CAT-09`, **`CAT-13`** and now `CAT-12` | `PGD-000` §3 | **CLOSED** at this issue |

---

## 4. `T3` — Section-Set Conformance

Each document was audited against the section set its governing standard requires, counted section
by section.

| Document | Governing standard | Required sections | Present | % |
|---|---|:--:|:--:|:--:|
| `RL-001` | ITIL 4 Release Management + ISO/IEC 20000-1 §8.5.1/§8.5.3 | Scope · types · authority · cadence · versioning · notes · records · measurement | 8 / 8 | **100%** |
| `RL-002` | ITIL 4 Deployment Management + ISO/IEC 20000-1 §8.5.3 | Plan · environments · verify · record success/failure · back-out · communication | 6 / 6 | **100%** |
| `RL-003` | IPA Gateway 4 + ISO 21502 §6.4 | Dimensions · evidence · assessors · decision input · timeline · re-assessment · instrument | 7 / 7 | **100%** |
| `RL-004` | ITIL 4 phased deployment + ISO 21502 §7.7 | Population · sequence · pilot · readiness bar · rate · support model · exception | 7 / 7 | **100%** |
| `RL-005` | ISO 21502 §7.10/§6.6 + PRINCE2 7 Lessons | Timing · measures · lessons identify/record/analyse/apply · report · closure | 6 / 6 | **100%** |
| `RL-006` | NIST SP 800-88r2 + ISO/IEC 27001 A.8.10 + ISO 15489-1 | Inventory · disposition · states · archive · sanitisation · revocation · termination · proof | 8 / 8 | **100%** |

All six also carry the `TPL_Guiding_Document.md` skeleton: Purpose · Scope · Basis · Body · Rules ·
Open Questions · Decisions · Acceptance Criteria · Traceability · References · Revision History.

**T3: PASS for all six.**

---

## 5. `T4` — The Approval Record

**FAIL, for all six, and for the same reason as the other 119 ✅ documents in this register.**

`PGD-000` §0.3 test (d) requires *"a named owner and an approval record."* All six carry a named
owner and a named approver role. **None carries an approval record**, because `GV-001` condition
`CC-01` — the ERP Steering Committee's first minuted meeting — has not occurred, and no constituted
body can approve anything (`PGD-A1-09`, `PGD-A2-25`).

Category 12's ✅ is qualified on exactly the same basis as Categories 00–11 and 13. This audit does
not treat it as a category-specific defect, and does not invent a sixth status — which no body could
approve either.

---

## 6. `T5` — Identifier Integrity

### 6.1 Rule prefixes

All six were verified against every `[A-Z]{2,6}-[0-9]{1,3}` token in the workspace **before**
allocation, and re-verified at audit after Category 10, 11 and 13 documents were written
concurrently.

| Document | Prefix | Occurrences outside Category 12 | Verdict |
|---|:--:|:--:|:--:|
| `RL-001` | `RMP` | 0 | ✅ |
| `RL-002` | `DPY` | 0 | ✅ |
| `RL-003` | `GLR` | 0 | ✅ |
| `RL-004` | `RLO` | 0 | ✅ |
| `RL-005` | `PIR` | 0 | ✅ |
| `RL-006` | `DCM` | 0 | ✅ |

> **The category code `RL` was deliberately *not* used as a rule prefix.** `RL-01` … `RL-12` is
> already the rule space of `TR-024_Release_Training_and_Refresher_Standard.md`, which uses it **36
> times**. Had Category 12 followed the naive convention of prefix-equals-code, it would have
> created a 36-way collision across two documents describing the same event from different sides.
> This is the second time this register has avoided that specific trap by checking first — `GV-009`
> §9.1 records the first, where `SC-G*` collided with the Security category code and was corrected
> before issue.

### 6.2 Rule numbering

| Document | Range | Gaps | Duplicates | Declared count | Actual |
|---|---|:--:|:--:|:--:|:--:|
| `RL-001` | `RMP-01`…`RMP-47` | 0 | 0 | 47 | **47** ✅ |
| `RL-002` | `DPY-01`…`DPY-48` + `DPY-09a` | 0 | 0 | 49 | **49** ✅ |
| `RL-003` | `GLR-01`…`GLR-31` | 0 | 0 | 31 | **31** ✅ |
| `RL-004` | `RLO-01`…`RLO-43` | 0 | 0 | 43 | **43** ✅ |
| `RL-005` | `PIR-01`…`PIR-45` | 0 | 0 | 45 | **45** ✅ |
| `RL-006` | `DCM-01`…`DCM-57` | 0 | 0 | 57 | **57** ✅ |

`DPY-09a` uses a sub-numbered form rather than renumbering `DPY-10`…`DPY-48`, because five other
documents already cite those identifiers. `GW-36`'s principle — *a wrong tag is superseded by a new
one, never moved* — applied to rule identifiers.

### 6.3 Decision identifiers

All six use the `<DOCUMENT-ID>-D-nn` form required by `DL-06` — `RL-001-D-01`, `RL-006-D-06` — and
**none uses the bare `D-nn` form**, which is `GV-003`'s programme decision space.

### 6.4 Cross-references

All relative links in all six documents resolve to a file on disk, verified at 2026-08-19 02:25 (+06).
**0 broken links.**

**T5: PASS.**

---

## 7. `T6` — Reproducibility of Quantitative Claims

Every figure asserted by the category was re-derived from its cited source at audit.

| Claim | Document | Source | Re-derived | Verdict |
|---|---|---|---|:--:|
| 8 release types | `RL-001` §4.1 | `OP-006` §4.1 | 8 rows counted | ✅ |
| 3 change classes | `RL-001` §4.1 | `SP-031` §3 | 3 | ✅ |
| 5 tag forms | `RL-001` §4.1 | `BE-003` §8.2 | 5 | ✅ |
| 12 environments | `RL-002` §3.1 | `PE-002` §4.2 | 12 rows counted | ✅ |
| 59 checklist items across 9 sections | `RL-002` §8.3 | This document | P9·Q7·S5·D6·E7·R5·O7·C6·X7 = **59** | ✅ *(corrected — see `RLA-15`)* |
| 19 standing smoke cases | `RL-002` §7.2 | This document | 19 | ✅ |
| 70 gate criteria across 9 gates | `RL-003` §2.2 | `06-02` §4 | 12+10+9+10+7+6+6+5+5 = **70** | ✅ |
| 39 evidence items across 7 dimensions | `RL-003` §5 | This document | 5+6+6+6+6+5+5 = **39** | ✅ |
| 8 divisions | `RL-004` §4.2 | `MD-006` §2.1 | 8 | ✅ |
| Branch-resident population 538 – ≥873 | `RL-004` §7.2 | `05-04` §5 | 51+150+20+80+120+15+51+51 = **538**; high with "51+" as floor = **873** | ✅ |
| Per-site 10.5 – 17.1 users | `RL-004` §7.2 | Derived | 538/51 = 10.5; 873/51 = 17.1 | ✅ |
| Rollout rate 2–3 sites/week | `RL-004` §7.5 | `OP-002` §4.4 ratios × `06-01` §4 team | 5T ≤ 15 → T=3; 10T ≤ 15 → T=1.5 | ✅ |
| 4 effort figures, widest ratio 4.7× | `RL-005` §5.1 | `GV-007` §4, §8 | 834 / 1,513 / 1,842 / 3,022; band high 3,931 ÷ 834 = **4.7×** | ✅ |
| 48 sources → 32/4/1/11 | `RL-006` §3.2 | `DM-002` §2.2 | Script-counted; 32+4+1+11 = **48** ✓ | ✅ |
| 32 retirements by wave | `RL-006` §3.3 | `DM-002` §2.2 | 10+6+3+9+3+1 = **32** ✓ | ✅ |
| 21 RFP practices | `RL-006` §4.1 | RFP §4.3 | 7+3+2+4+3+1+1 = **21** ✓ | ✅ |
| 16 declared `_BN` counterparts, 0 on disk | `RL-004` §12.2 | `project_content` | 16 declared / 0 present | ✅ |
| 90 × "500+", 35 × "800+" | `RL-004` §3.3 | Workspace | 76+14 = 90; 24+5+6 = 35 | ✅ |

**T6: PASS. Eighteen of eighteen claims reproduce.** One (`RLA-15`) was wrong at v1.0 and is
corrected; it is counted here as it now stands and is recorded as a finding rather than smoothed
over.

---

## 8. `T7` — Operational Executability

`PGD-AUDIT-CAT-09` added this test because a category specifying an operation can be a complete
specification and an unperformable one. Category 12 is in the same position.

> **The question: if Wave 1 went live next month, which of these six documents could actually be
> followed?**

| Document | Executable today? | What blocks it |
|---|:--:|---|
| `RL-001` | **Partly** | The freeze calendar and release taxonomy are executable now. The CAB (§8.2) **cannot be quorate** — Change Manager, Security Lead and Service Manager are unappointed (`RMP-37`). Six of seven metrics need a built pipeline |
| `RL-002` | **Partly** | The runsheet, smoke set and abort criteria are executable. **Six of 59 checklist items cannot be evidenced** (`DPY-29`): none of the twelve environments is provisioned, no rollback rehearsed, no restore tested, no rota staffed, no paging tested, no rolling deployment measured for downtime. **As of the fifth enumeration every one is a missing capability, not a missing document** |
| `RL-003` | **No** | **Three of seven dimensions have no appointed assessor** (`GLR-26`). Under `GLR-07` an unassessed dimension is RED, and a RED on `RD-4` stops `C7`. Read literally, **Wave 1 cannot go live** |
| `RL-004` | **No** | `MD-003` is class `P3` — **the site list does not exist** (`RLO-01`). Sixteen Bengali counterpart files do not exist (`RLA-18`). The floor-walker resource is unfunded (`RLA-07`) |
| `RL-005` | **Partly** | The review is holdable. **No benefit may be claimed** until `BM-002` issues (`RLA-09`), and `BM-005` does not exist, so lessons go to an interim register |
| `RL-006` | **Partly** | The register is buildable. **`DEP-35` does not exist**, so no sanitisation standard governs the ten W2 retirements (`DCM-27`); **no legacy licence inventory exists**, so `D6` cannot complete for any source (`DCM-41`) |

### 8.1 The position, stated plainly

**Category 12 is a complete specification of an operation the programme cannot yet perform.** That
is the same verdict `PGD-AUDIT-CAT-09` reached about migration, in the same words: *"a complete
specification is not a performed migration."*

What is different here is **where** the blockage sits. Category 09's inexecutable rule classes
waited on tooling and data. Category 12's wait on **five appointments, one dataset, sixteen
translations, one baseline report and two registers** — none of which is a technical problem and
every one of which has a named owner and a date in the six documents' open questions.

| Blocker | Kind | Owner | Needed by |
|---|---|---|:--:|
| Security Lead, Service Manager, Financial Controller, Change Manager, Legal Counsel | **Appointment** | Programme Director | W1 − 5 months |
| `MD-003` populated and confirmed | **Dataset** | Operations MDM analyst | W1 − 3 months |
| 16 Bengali counterpart files | **Translation** | Content Design | W1 − 2 months |
| `BM-002` KPI baselines | **Document, irrecoverable if late** | Programme Director | Before W1 |
| `DEP-35` sanitisation programme | **Document** | Quality Manager | W2 − 2 months |
| Legacy licence inventory | **Document** | CFO with CTO | W2 − 2 months |
| Twelve environments provisioned | **Build** | Platform Lead | W1 − 3 months |
| On-call rota staffed and paging tested end to end | **Build** — `SV-004` issued 2026-08-19 | Service Manager | W1 |
| Floor-walker funding **or** schedule extension | **Steering decision** | Steering Committee | W1 |

**T7: the category specifies correctly and cannot be executed. Nine blockers, all named, all
owned, all dated — and not one of them is a technical problem.**

---

## 9. The Process Finding

### 9.1 What happened

Three of this category's six documents made status assertions about Category 10 that were true when
written and false within three hours. The corrections consumed a material share of the audit and
produced four findings — `RLA-13`, `RLA-14`, `RLA-16`, `RLA-17` — of which two (`RLA-13`, `RLA-14`)
required **withdrawing a ruling**, not merely refreshing a symbol.

### 9.2 What made it worse than a stale count

Previous instances of this class (`AP-17`, `PGD-A1-03`, `MGA-15`, `RLA-24`) produced **wrong
numbers**. This one produced **wrong rulings**:

| v1.0 said | Truth by issue | Consequence had it not been caught |
|---|---|---|
| *"The programme has ten environments"* | `PE-002` rules **twelve** | Two environment inventories in one repository, differing by `local` and `migration-staging` — the exact divergence `PE-002-F-01` predicted |
| *"`Recreate` is the only executable deployment model"* | `PE-004` §8.1 assigns rolling and blue/green per component | A deployment runsheet written for a model the pipeline does not use |
| *"`NFR-008` is not achievable … and no document has said so"* | `PE-004` §8.2 says it **is**, under four conditions | A P1 non-functional requirement reported as unachievable at every gate when it is specified as achievable |

### 9.3 The recommendation, for the eighth time

> **`RG-08`** — every status assertion carries an **enumeration timestamp**, not a date — remains
> *proposed and unratified*. `PGD-000` records it as *"pending ratification throughout"* and
> *"recommended for the seventh time."* **This audit is the eighth.**
>
> Category 12 complied with `RG-08` voluntarily: all six documents carry an
> `enumeration_timestamp` in front matter, and every count in this audit carries the instant it was
> taken. **That compliance is what made the four corrections findable.** A document with only a date
> would have been silently wrong.

**Additional recommendation, new at this audit:**

> **`RG-09` — a document that asserts another document is absent must name the enumeration instant
> of that assertion, in the sentence making it.** Not in front matter, in the sentence. `RL-003`
> §11.4's corrected table does this, and it is the difference between *"`PE-002` is ⛔"* — which
> rots — and *"`PE-002` was ⛔ at 2026-08-18 23:27 (+06)"* — which stays true forever and prompts a
> re-check.
>
> `RR-002` and `RR-006` remain the durable fixes and remain unwritten.
>
> **The recommendation count is itself now contested, which is a small demonstration of the
> problem.** `PGD-000` v1.5 recorded `RG-08` and `RR-002` *"recommended for the seventh time"*;
> v1.6, issued the same night by Category 13, recorded *"the eighth and ninth time"*; this audit is
> at least the tenth. **Nobody can say which, because no register counts recommendations** — which
> is precisely what `RR-006`'s cross-reference index would do.

---

## 10. Remediation Register

| # | Action | Owner | By | Finding | Status |
|:--:|---|---|:--:|---|:--:|
| `R-01` | Choose between funded floor-walkers and an extended wave schedule | **Steering Committee** | **W1** | `RLA-07` | OPEN |
| `R-02` | Translate the 16 declared `_BN` counterparts; `CM-012` and `OP-014` first; re-prioritise `CM-012` to `P0` | Content Design with Change Lead | **W1 − 2 mo** | `RLA-18` | OPEN |
| `R-03` | Recompute the rollout rate from measured walker-hours after the W1 pilot | Branch Operations Lead | W1 pilot exit | `RLA-06` | OPEN |
| `R-04` | Issue `BM-002` KPI baselines before W1 begins | Programme Director | **Before W1** | `RLA-09` | OPEN |
| `R-05` | Ratify `RG-08`; adopt `RG-09`; write `RR-002` and `RR-006` | PMO | W1 | `RLA-22` | OPEN |
| `R-06` | Cover the three go-live-critical roles with establishment ≤ 2 | HR Director | W5 − 6 mo | `RLA-23` | OPEN |
| `R-07` | `BE-003` v1.1 — correct the `RL-003` emergency-change mis-citation | Engineering Lead | W1 | `RLA-01` | OPEN |
| `R-08` | Rule one workforce denominator, dated | Programme Director | W1 | `RLA-08` | OPEN |
| `R-09` | `GV-001` v1.1 §12.1 — adopt `DCM-04`'s four criteria | Programme Director | W1 | `RLA-10` | OPEN |
| `R-10` | Mark the nine sources with no contractual accountability in the decommission register | CTO | W2 | `RLA-11` | CLOSED in spec |
| `R-11` | Interim: never cite a bare `RB-nn`; always name its document | All authors | Now | `RLA-19` | Cat 12 CLOSED |
| `R-12` | `PGD-000` §3 — regenerate the repository count and the audit-identifier note | PMO | This issue | `RLA-24`, `RLA-20` | **CLOSED** |
| `R-13` | Appoint Security Lead, Service Manager, Financial Controller, Change Manager | Programme Director | **W1 − 5 mo** | `GLR-26`, `RMP-37` | OPEN |
| `R-14` | Populate `MD-003` and convert it from class `P3` to `P1` | Operations MDM analyst | W1 − 3 mo | `RLO-01` | OPEN |
| `R-15` | Move `DEP-35` from W6 − 2 mo to W2 − 2 mo | Quality Manager | W2 − 2 mo | `DCM-27` | OPEN |
| `R-16` | Produce the legacy licence, hosting and support inventory | CFO with CTO | W2 − 2 mo | `DCM-41` | OPEN |
| `R-17` | Confirm `PE-004`/`PE-008` telemetry emits what `RMP-M1`…`RMP-M5` consume | Platform Lead | W1 | `RLA-16` | OPEN |

---

## 11. Verdict

| Test | Result |
|---|---|
| **T1** file exists | **PASS** — 6 / 6 |
| **T2** front matter | **PASS** — 6 / 6, all carrying `enumeration_timestamp` and `rule_prefix` beyond the template minimum |
| **T3** section-set conformance | **PASS** — 100% for all six |
| **T4** approval record | **FAIL** — as for all 119 ✅ documents; `GV-001` `CC-01` |
| **T5** identifier integrity | **PASS** — 6 verified-unused prefixes, 272 rules, 0 gaps, 0 duplicates, 0 broken links |
| **T6** reproducibility | **PASS** — 18 / 18 claims re-derived |
| **T7** operational executability | **SPECIFIED, NOT EXECUTABLE** — 8 named blockers |

> **Category 12 moves from `0 ✅ / 2 ◐ / 1 ⬜ / 3 ⛔` to `6 ✅`, qualified exactly as the 119 before
> it: tests (a), (b) and (c) met and verified; test (d)'s approval record absent and unobtainable
> until `GV-001` `CC-01` completes.**
>
> **Read the ✅ narrowly.** `RL-003` §8 states, and this audit confirms, that **read literally the
> category makes Wave 1 unable to go live** — three of seven readiness dimensions have no appointed
> assessor, the site list does not exist, and the branch instructions are not in Bengali. That is
> not a defect in the documents. It is the documents doing their job, which is to make an
> unperformable operation visible before it is attempted rather than after.

---

## 12. Independence

**This audit is not independent.** It was produced by the same function that authored the six
documents it audits, in the same session.

`PGD-AUDIT-001` §12 declares itself *"Not independent"*; `GV-009` §5.2 records that four repository
audits and nineteen category audits have been produced by the function that authored the material;
`AUDIT-019` recorded a critical finding *"against the auditor's own authoring."*

What this audit did to compensate, stated so it can be judged:

| Compensation | Applied |
|---|---|
| Every quantitative claim **re-derived from source**, not read back from the document | §7 — 18 claims |
| Findings raised **against the category's own work**, not only against its inputs | 5 of 24 — `RLA-13`…`RLA-17` |
| Two of those required **withdrawing a ruling**, not refreshing a status | `RLA-13`, `RLA-14` |
| The category's own ✅ read narrowly, with `T7` stating it cannot be executed | §8, §11 |
| The estate re-enumerated **four times** and every count timestamped | §1.3 |

`GV-009` `GA-09` provides independence from **Gate 4** onward. Until then the cross-assessment rule
is the only control available, and it does not apply to an audit of one's own authoring. **This
audit should be re-performed by `GV-010`'s independent reviewer when one is engaged.**

---

## 13. Revision History

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0 | 2026-08-19 | Enterprise Architecture | Initial issue. Six documents, 272 rules, 24 findings — 2 CRITICAL, 4 HIGH, 9 MEDIUM, 9 LOW — and 9 closures including `MG-006` `Q-01`, `MG-007` `Q-04` and `SP-031`'s open Definition-of-Done item. Five findings against the category's own work, all corrected at v1.1 before issue. Records the concurrent-authoring collision `PE-002-F-01` predicted and that occurred the same day (`RLA-22`), and recommends `RG-08` for the eighth time and `RR-002` for the eighth |

---

*`PGD-AUDIT-CAT-12` · Category 12 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
