---
id: RQ-003
title: Fit-Gap Analysis & Functional Design Specification
category: 01 — Requirements Engineering
code: RQ
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: ERP Solution Architect
approver: ERP Design Authority, endorsed by the CFO for the cost consequence
standards_basis: ISO/IEC/IEEE 29148:2018 §5.2.5 (Appropriate — implementation independence) · ERP fit-gap practice · ISO/IEC 25010:2023 (functional suitability)
traces_to: PGD-000 §2.1 item 2 · audit H-02 (implementation cost understated 70–80%) · audit AF-08 (1,513 PW measured vs 834 PW approved) · 02-05 §1 layer coverage · 05-01 §2.3
depends_on: RQ-001 (the requirement set and its denominator), RQ-004 (traceability), BE-005 (CD register — blocked)
verified_on: 2026-08-18
priority: P0
needed_by: Now
enumerated_on: 2026-08-18 02:15 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# RQ-003 — Fit-Gap Analysis & Functional Design Specification

### Category 01 · Code `RQ` · ERP fit-gap practice · ISO/IEC/IEEE 29148:2018 §5.2.5

---

> **The finding that produced this document.** The programme's cost model rests on a single
> claim: that Odoo 19 CE covers **28%** of requirements natively, OCA a further **24%**, and that
> custom development accounts for **25%**. Those figures appear in `02-05` §1, `02-05` §2 and
> `05-01` §2.3, and every effort and budget number in the programme descends from them.
>
> Two measurements taken from the filesystem at **2026-08-18 02:15 (+06)** show they cannot be
> relied on.
>
> **First**, the layer distribution in `05-01` §2.3 sums to **1,180** — the superseded 30-module
> baseline that `05-01` itself declares superseded on its own title page. It has never been
> recomputed against the 67-module estate.
>
> **Second**, and more seriously: the `Layer` column of the requirement rows themselves — the
> only requirement-level layer statement that exists anywhere — marks **3,078 of 3,347 rows
> (92%) as involving L5 custom development**, against a stack summary claiming 25%.
>
> Those two numbers cannot both be true. Until one is retired, **no cost figure in this programme
> is supportable**, which is precisely what audit `H-02` concluded by a different route.

---

## 1. Purpose

An ERP implementation is priced on one question asked 3,347 times: *does the product already do
this?* If it does, the requirement costs configuration time. If it does not, it costs design,
build, test, documentation and thirty-six months of maintenance. The difference between those two
answers, multiplied across a requirement set of this size, is the difference between the
$455K–780K the Board is holding and the number audit `H-02` says is 70–80% higher.

Nobody in this programme can currently answer that question for any individual requirement. This
document creates the instrument that answers it: a **disposition per requirement**, made against
a stated evidence standard by a named assessor, recorded as an attribute of the requirement, and
aggregated into the coverage figures the budget is allowed to use. For every requirement that
turns out to be a gap, it specifies the **Functional Design Specification** that states how the
built or configured behaviour will work — the artefact that stands between `FR-SRM-014` and a
developer opening `cd_service_order/models/service_order.py`.

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | The **disposition taxonomy** — fit / configure / extend / build / buy — and its mapping to delivery layers `L1`–`L6` (§3) |
| 2 | The **determination procedure**: who assesses, against what evidence, with what recording (§4) |
| 3 | The **evidence standard** per disposition — what proves "Odoo already does this" (§4.3) |
| 4 | The **measured baseline** and the reconciliation of three incompatible coverage positions (§5) |
| 5 | The **FDS content standard** — what a functional design for a gap shall contain (§6) |
| 6 | The **effort model inputs** the determination produces for `GV-007` and `CO-005` (§7) |
| 7 | The **execution plan** — sequence, assessors, throughput, and the wave-gate re-verification (§8) |

**Explicitly out of scope:**

| Topic | Owned by | Why |
|---|---|---|
| The requirement statements | `RQ-001` | A disposition is a judgement *about* a requirement |
| Person-week estimates and the resource plan | `GV-007` | This document supplies measured inputs; it does not publish a fourth uncontrolled estimate (`PGD-A1-05`) |
| The total cost of ownership | `CO-005` | As above |
| Technical design — classes, methods, schema deltas, algorithms | `AR-003` SDD | An FDS states *what the configured or built behaviour does*; the SDD states *how it is constructed* |
| The custom-development register | `BE-005` | `CD` identifiers are **not** allocated here. 31 already collide (`RQ-001` §3.10.7, `RQA-10`) |
| Build-vs-buy at platform level | `AR-013` | `02-05` §7 holds 20 platform decisions; this document dispositions requirements, not platforms |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| CFO and Board | The only defensible basis for a cost baseline (`GV-008`) |
| Implementation vendor | The scope of build, distinguished from the scope of configuration |
| Solution architects | The determination they own and must evidence |
| Odoo and OCA developers | The gap set they will design against |
| PMO | The coverage figures that may be quoted, and the ones that may not |
| Auditors | The evidence trail behind every "Odoo already does this" claim |

---

## 2. Basis and Inputs

### 2.1 Standards and method basis

| Basis | How applied | Departure |
|---|---|---|
| ISO/IEC/IEEE 29148:2018 §5.2.5 *Appropriate* | A disposition is recorded as a requirement **attribute**, never written into the requirement statement — a requirement that names its implementation is not implementation-independent | None |
| ISO/IEC/IEEE 29148:2018 §5.2.8 | `fit_gap` and `layer` are the two disposition attributes defined in `RQ-001` §3.10.3 | None |
| ISO/IEC 25010:2023 *Functional suitability* — completeness, correctness, appropriateness | A "fit" claim is a claim about functional suitability and is tested as one | None |
| ERP fit-gap practice (SAP, Oracle, Dynamics, IFS implementation method) | Five dispositions; evidence-based determination; gap-first design | This programme adds a **sixth** state, `undetermined`, and counts it, rather than defaulting unassessed requirements to "fit" |

**Verified 2026-08-18.**

### 2.2 Source material relied on

| Source | What it establishes | Measured |
|---|---|---|
| `RQ-001` §3.10.5, Appendix A | The requirement set and the single denominator | 3,347 adopted + 42 `SWR` |
| `../../1000fix_ERP_Module/02_Architecture/02-05` §1 | The six-layer stack and its coverage percentages | L1 28 · L2 24 · L3 4 · L4 17 · L5 25 · L6 2 |
| `.../02-05` §2 | Odoo 19 CE modules deployed, by wave | 16 module groups |
| `.../02-05` §3 | OCA — 140+ modules across 18 repositories, with v19 migration status | 18 repositories |
| `.../02-05` §4 | 24 standalone open-source systems with licence obligations | 24 systems |
| `.../02-05` §5.1–5.4 | 80 custom deliverables: 58 Odoo modules, 12 services, 4 mobile apps, 6 web apps; 834 PW | `CD-001…138` |
| `.../02-05` §6 | Four L6 commercial components, each CFO-approved | 4 |
| `.../05-01` §2.3 | Requirement distribution by layer | **Sums to 1,180 — superseded basis** |
| 67 module files §5 `Layer` column | The only requirement-level layer statement in existence | 3,347 rows |
| 67 module files §16.1 | Module-level layer coverage percentages | Contradicts §5 in every module sampled |

### 2.3 Audit findings this document addresses

| Finding | Source | Treatment |
|---|---|---|
| `H-02` (high) | `00-06` | Implementation cost understated 70–80%. §5 measures the contradiction that makes any current figure unsupportable; §7 supplies the inputs `GV-007` needs to restate it | Closes with `GV-007` + `CO-005` |
| `AF-08` | `00-06` | 1,513 PW measured against 834 PW approved. §5.3 shows the 834 PW figure descends from the 1,180-requirement basis | Closes with `GV-007` |
| **`RQA-14`** *(raised here)* | This document | **The layer coverage percentages that carry the cost model are computed on a superseded 1,180-requirement baseline** | Open — §5.2 |
| **`RQA-15`** *(raised here)* | This document | **The requirement-level `Layer` column and the module-level §16.1 coverage table contradict each other in every module measured** | Open — §5.3 |
| **`RQA-16`** *(raised here)* | This document | **40 requirement rows carry a wave value in the `Layer` column**, from the six tables that use `Wave` as the fifth column | Open — data defect, §5.4 |

---

# 3. The Disposition Taxonomy

## 3.1 The five dispositions, plus one

Every requirement in the set carries exactly one `fit_gap` value.

| Disposition | Definition | Delivery layer | Cost profile | Upgrade exposure |
|---|---|---|---|---|
| **`fit`** | The unmodified product satisfies the requirement. No configuration beyond routine setup | `L1` Odoo 19 CE · `L2` OCA · `L3` free third-party · `L4` standalone OSS | Setup and test only | None |
| **`configure`** | The product satisfies it through supported configuration — fields, views, workflow states, rules, reports — using no custom code | `L1`/`L2` configured | Configuration, test, documentation | Low; configuration migrates |
| **`extend`** | The product's model is inherited and extended in a separate module; core is not modified | `L5` extension | Design, build, test, documentation, upgrade regression | **Medium — the layer that decides whether the Odoo 20 upgrade is a project or a rewrite** |
| **`build`** | No product capability exists; the behaviour is constructed from nothing, as a custom Odoo module, a standalone service or an application | `L5` new | Full lifecycle cost | High |
| **`buy`** | A commercial component satisfies it, and no open-source equivalent was assessed as viable | `L6` | Subscription, integration, exit risk | Vendor-dependent |
| **`undetermined`** | **Not yet assessed.** A counted state, never a default | — | Unknown | Unknown |

> **Why `undetermined` is a first-class state.** The commonest failure in ERP fit-gap is that
> unassessed requirements are quietly presumed to be fits, because a fit costs nothing and
> therefore disturbs no plan. Counting them makes the size of what is not yet known visible.
> **At issue, all 3,389 requirements are `undetermined`** — that is the true starting position.

## 3.2 Disposition versus layer — they are not the same attribute

`layer` says **which technology delivers** the requirement. `fit_gap` says **how much work it
is**. They are correlated and not equivalent, which is exactly why the estate's layer column
cannot be read as a fit-gap result:

| Layer | Can be `fit` | Can be `configure` | Can be `extend` | Can be `build` |
|---|:--:|:--:|:--:|:--:|
| `L1` Odoo 19 CE | ✔ | ✔ | ✔ (as `L1`+`L5`) | ✗ |
| `L2` OCA | ✔ | ✔ | ✔ (as `L2`+`L5`) | ✗ |
| `L3` free third-party Odoo | ✔ | ✔ | ✔ | ✗ |
| `L4` standalone open source | ✔ | ✔ | ✔ (adapter in `L5`) | ✗ |
| `L5` custom | ✗ | ✗ | ✔ | ✔ |
| `L6` commercial | ✔ (`buy`) | ✔ | ✗ | ✗ |

**Rule `FG-01`.** A requirement marked `L5` is either `extend` or `build`. The distinction between
those two carries the entire upgrade-survivability risk of the programme (`CN-02`, `AS-05`), and
the estate does not currently record it for any requirement.

## 3.3 Disposition attribute schema

| Field | Rule |
|---|---|
| `fit_gap` | One of `fit` / `configure` / `extend` / `build` / `buy` / `undetermined` |
| `layer` | `L1`…`L6`, or a pair where two layers combine |
| `component` | The Odoo module, OCA module, OSS system, `cd_*` module, service or commercial product that delivers it. **Mandatory** for every disposition other than `undetermined` |
| `evidence` | The evidence reference required by §4.3. **Mandatory** for `fit` and `configure` |
| `assessor` | The role that made the determination. Never a personal name |
| `assessed_on` | Date; re-verified at each wave gate |
| `confidence` | `verified` (evidence executed) / `asserted` (evidence cited, not executed) / `assumed` |
| `gap_id` | `FG-nnn` where the disposition is `extend` or `build`; links to the FDS in §6 |
| `risk` | Upgrade, licence, or vendor risk carried by the disposition |

**Rule `FG-02`.** A `fit` or `configure` disposition with `confidence: assumed` **may not be used
in a cost figure**. It is counted as `undetermined` for costing purposes until evidence is
executed. This is the single control that prevents the optimism that produces `H-02`.

---

# 4. The Determination Procedure

## 4.1 Who determines

| Role | Determines | Cannot determine |
|---|---|---|
| **ERP Solution Architect** | Final disposition for every requirement; owns the register | — |
| **Odoo functional consultant** | `fit` and `configure` against `L1`/`L2`/`L3`, with executed evidence | `build` scope, which is an architecture decision |
| **Integration architect** | `L4` dispositions and adapter scope | Functional fits |
| **Business owner** (per module) | Whether a `fit` is *acceptable to the business* — a capability that exists but does not meet the business need is a gap, not a fit | The technical determination |
| **Enterprise Architect** | `extend` vs `build`, and the upgrade risk each carries | — |
| **CFO** | `buy` — every `L6` disposition requires CFO approval (`02-05` §6) | — |

**Rule `FG-03` — two signatures.** A `fit` disposition requires both the functional consultant's
technical evidence and the business owner's acceptance. A technical fit the business rejects is a
gap. This rule exists because the cheapest possible answer is always "it fits", and one signature
is not enough resistance against a budget.

## 4.2 The determination sequence

```
  For each requirement (RQ-001 baseline, 3,389)
      │
      ├─ 1. Is the requirement well-formed (RQ-001 §3.10.4)?
      │     └─ No → return to module author. A disposition on an ambiguous
      │              requirement is a disposition on an unknown.
      │
      ├─ 2. Does an L1 Odoo 19 CE capability address it?
      │     ├─ Yes, unmodified            → fit        [evidence: E-01]
      │     ├─ Yes, by configuration      → configure  [evidence: E-02]
      │     └─ No → 3
      │
      ├─ 3. Does an L2 OCA module address it, at v19 or with a v19 migration path?
      │     ├─ Yes, unmodified            → fit        [E-01 + E-05 migration status]
      │     ├─ Yes, by configuration      → configure  [E-02 + E-05]
      │     └─ No → 4
      │
      ├─ 4. Does an L3 free module or an L4 standalone system address it?
      │     ├─ Yes                        → fit / configure  [E-01, E-03 licence]
      │     └─ No → 5
      │
      ├─ 5. Can an existing model be inherited and extended without touching core?
      │     ├─ Yes                        → extend     [E-04 extension point named]
      │     └─ No → 6
      │
      ├─ 6. Is there a commercial component and no viable OSS equivalent?
      │     ├─ Yes                        → buy        [E-06 CFO approval + OSS assessment]
      │     └─ No → 7
      │
      └─ 7.                                → build     [FG-nnn raised, FDS required]
```

**Rule `FG-04` — the order is binding.** A requirement may not be dispositioned `build` without
the preceding six steps being recorded. The commonest cause of ERP over-build is that step 2 was
never attempted, because building is more interesting than configuring.

## 4.3 The evidence standard

*What actually proves each disposition. Without this table, "Odoo does that" is an opinion.*

| # | Evidence | Required for | What it is |
|---|---|---|---|
| **E-01** | **Executed demonstration** | `fit` | The capability demonstrated in a running Odoo 19 CE instance with representative 1000FiX data, recorded with the module name, version, screen and date. **Not** a documentation citation |
| **E-02** | **Configuration record** | `configure` | The specific configuration — fields, views, states, rules, reports — named, and demonstrated in a running instance |
| **E-03** | **Licence assessment** | any `L2`/`L3`/`L4` | The component's licence and the obligation it imposes, per `02-05` §4 and `CO-004` |
| **E-04** | **Extension point** | `extend` | The Odoo or OCA model inherited, the inheritance mechanism, and a statement that core is not modified (`AS-05`) |
| **E-05** | **v19 migration status** | any `L2` | The OCA module's current v19 status, with the date checked. `02-05` §3 records 8 of 33 `field-service` modules and 8 of 28 `helpdesk` modules unmigrated |
| **E-06** | **CFO approval + OSS assessment** | `buy` | The approval record and the assessment of why no open-source equivalent is viable |
| **E-07** | **Business acceptance** | `fit`, `configure` | The business owner's recorded acceptance that the capability meets the need, per `FG-03` |
| **E-08** | **Gap statement** | `extend`, `build` | The `FG-nnn` record and its FDS (§6) |

**Rule `FG-05`.** Evidence is recorded against the requirement, not against the module. A module
"90% covered by OCA" tells a costing exercise nothing about the ten requirements that are not.

---

# 5. The Measured Baseline

*Every figure in this section was counted at 2026-08-18 02:15 (+06). This section makes no
estimate.*

## 5.1 Three incompatible coverage positions

| Position | Source | L1 | L2 | L3 | L4 | L5 | L6 | Denominator |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| **A — Stack summary** | `02-05` §1 | 28% | 24% | 4% | 17% | 25% | 2% | *unstated* |
| **B — Requirement distribution** | `05-01` §2.3 | 330 (28.0%) | 283 (24.0%) | 47 (4.0%) | 201 (17.0%) | 295 (25.0%) | 24 (2.0%) | **1,180** |
| **C — Requirement rows, counted** | 67 modules + 12 portals, §5 `Layer` column | 110 (3.3%) | 107 (3.2%) | 33 (1.0%) | 100 (3.0%) | **3,078 (92.0%)** | 13 (0.4%) | **3,347** |

*Position C counts every row whose `Layer` cell **mentions** that layer, so combination cells such
as `L1/L5` are counted in both; the row percentages therefore exceed 100% in total. 40 rows
(1.2%) carry no layer value at all.*

## 5.2 Finding `RQA-14` — position B rests on a superseded baseline

`05-01` §2.3's six layer counts sum to **330 + 283 + 47 + 201 + 295 + 24 = 1,180**.

1,180 is the **30-module** requirement total that `05-01` §1.3 marks *"(30-module basis —
superseded)"* on its own page. The layer distribution beneath it was never recomputed when the
architecture went to 67 modules.

**Consequence.** Position A's percentages are position B's percentages, and position B's
percentages describe a system that has 30 modules and 1,180 requirements — a system this
programme is no longer building. The **834 PW** effort figure in `02-05` §5.1, the **$455K–780K**
cost band, and every derived Board figure descend from it.

## 5.3 Finding `RQA-15` — positions B and C contradict each other, and so does every module

Position C says 92% of requirement rows involve custom development. Position B says 25%.

This is not a rounding difference; it is a factor of **3.7**. It is also visible **inside single
modules**, between a module's own §5 requirement rows and its own §16.1 coverage table:

| Module | §5 rows marked `L5` | §16.1 claims `L5` | Divergence |
|---|---:|---:|---:|
| M01 Service Request & Order Management | 63 of 70 = **90%** | 54% | +36 pts |
| M15 Spare Parts & Inventory Management | 47 of 54 = **87%** | 42% | +45 pts |
| M19 Financial Accounting & General Ledger | 40 of 46 = **87%** | 43% | +44 pts |
| M29 Identity, Access & Information Security | 45 of 52 = **87%** | 50% | +37 pts |

**Two readings are possible, and they have opposite cost consequences:**

| Reading | If true | Cost consequence |
|---|---|---|
| **R-1.** `L5` was used as the default value in the `Layer` column when authors did not know | Position C is a data-entry artefact and tells us nothing | Coverage is genuinely unknown; the baseline must be built from zero, not corrected |
| **R-2.** The module authors, closest to the requirements, judged them to need custom work | Position B is wrong and the cost model understates build by ~3.7× | Consistent with audit `H-02`'s independent 70–80% understatement |

**Neither reading permits a cost figure to be published today.** Determining which is true is the
first task of the execution plan (§8.1) and is the single highest-value analysis available to
this programme.

## 5.4 Finding `RQA-16` — 40 rows carry a wave in the layer column

Six requirement tables use `Wave` as their fifth column instead of `Layer` (`RQ-001` Appendix B).
The 40 rows in them therefore record `W2`, `W4` or `W6` where a layer belongs. This is a schema
defect, not a judgement error, and is corrected by the conversion in `RQ-001` §3.10.7.

## 5.5 The honest starting position

| `fit_gap` state | Requirements | % |
|---|---:|---:|
| `fit` — with executed evidence | **0** | 0.0% |
| `configure` — with a configuration record | **0** | 0.0% |
| `extend` — with a named extension point | **0** | 0.0% |
| `build` — with an `FG-nnn` and an FDS | **0** | 0.0% |
| `buy` — with CFO approval | **0** | 0.0% |
| **`undetermined`** | **3,389** | **100.0%** |

**Not one requirement in this programme carries an evidenced fit-gap determination.** Position A
and position B are inferences at layer granularity; position C is an unvalidated column. That is
the position this document exists to change, and stating it plainly is more useful than restating
a percentage nobody can defend.

---

# 6. Functional Design Specification

Every requirement dispositioned `extend` or `build` raises a gap `FG-nnn` and requires an FDS.
The FDS is the artefact the register describes as missing between `FR-SRM-014` and
`cd_service_order/models/service_order.py`.

## 6.1 FDS content standard

| § | Section | Content | Mandatory |
|---|---|---|---|
| 1 | Gap identity | `FG-nnn`; the requirements it satisfies; module; wave; priority | ✔ |
| 2 | Why it is a gap | The determination trail from §4.2: which of steps 2–6 were attempted and what each returned | ✔ |
| 3 | Business behaviour | What the configured or built capability does, in business language, sufficient for the business owner to accept it | ✔ |
| 4 | Actors and roles | The `Rnn` roles that exercise it, with the scope each has | ✔ |
| 5 | Trigger and preconditions | What starts it; what must be true first | ✔ |
| 6 | Main flow | The normal path, step by step | ✔ |
| 7 | Alternate and exception flows | Every branch, including the one nobody models — no response, timeout, partial failure | ✔ |
| 8 | Business rules applied | The `BRU-` identifiers enforced, with classification (`RQ-009`) | ✔ |
| 9 | Data created, read, updated | Entities touched, with the owning module for each (`05-02`, `DA-001`) | ✔ |
| 10 | Events published and consumed | Domain events, with producer/consumer (`IN-003`) | ✔ |
| 11 | Interfaces | Screens affected, APIs called, external systems involved | ✔ |
| 12 | State model impact | New states or transitions introduced into an existing lifecycle | Where applicable |
| 13 | Extension mechanism | For `extend`: the model inherited, the inheritance type, and the statement that core is untouched | `extend` only |
| 14 | Configuration inventory | For `configure`: every configuration object with its value | `configure` only |
| 15 | Non-functional constraints | The `NFR` identifiers this capability must meet (`RQ-006`) | ✔ |
| 16 | Acceptance criteria | Given/When/Then per `RQ-008`, with a verification method per `RQ-001` §3.19 | ✔ |
| 17 | Localisation | Bengali strings, formats, and any layout consequence (`UX-007`) | ✔ |
| 18 | Migration impact | Legacy data that must land in the new structures (`MG-003`) | Where applicable |
| 19 | Open questions | With owner and needed-by | ✔ |

**Rule `FG-06`.** An FDS states **what the behaviour is**, never how it is constructed. Class
structure, method contracts, algorithms and schema deltas belong to `AR-003` (SDD, IEEE
1016-2009). An FDS a business owner cannot read has failed.

**Rule `FG-07`.** One FDS may satisfy several requirements; a requirement may not be satisfied by
several FDS documents. Where it appears to need two, the requirement is not singular (`RQ-001`
characteristic W-05) and is split.

## 6.2 Gap identifier space

| Space | Scope | Authority | Status |
|---|---|---|---|
| `FG-nnn` | Programme-wide gap identifier | This document | **Reserved.** Sweep across all four repositories at 02:15 (+06) returns **0** prior occurrences. To be ratified by `RR-002` |

**Rule `FG-08` — no `CD` identifiers are allocated here.** `CD-059`…`CD-090` already collide
across 31 identifiers, the highest in use is `CD-214` against a register of `CD-001…138`, and
`_MODULE_TEMPLATE` §16.2 forbids creating a build ticket from a provisional `CD`. A gap carries an
`FG-nnn`; `BE-005` maps `FG-nnn` to a `CD-nnn` when the CD register is re-based.

## 6.3 FDS production sequence

| Step | Who | Output |
|---|---|---|
| 1 | Solution Architect | Gap raised, `FG-nnn` allocated, requirements linked |
| 2 | Functional consultant + business owner | §3–§8 drafted; business behaviour agreed |
| 3 | Data architect | §9 entities reconciled against `DA-001`/`DA-002` |
| 4 | Integration architect | §10, §11 reconciled against `IN-002`/`IN-003` |
| 5 | Enterprise Architect | §13 extension mechanism approved; upgrade risk recorded |
| 6 | QA | §16 acceptance criteria and verification method agreed |
| 7 | Business owner | Sign-off. **The FDS is accepted by the business, not by IT** |
| 8 | PMO | `fit_gap`, `gap_id` and `component` written back to the requirement attributes |

---

# 7. Effort Model Inputs

This document **does not estimate**. Publishing a fourth uncontrolled estimate is finding
`PGD-A1-05`. It supplies the measured inputs `GV-007` needs.

## 7.1 What `GV-007` receives from a completed determination

| Input | Unit | Why it matters |
|---|---|---|
| Count of `fit` with executed evidence | requirements | The only requirements that cost setup and test alone |
| Count of `configure` with a configuration record | requirements | Configuration effort scales with configuration-object count, not requirement count |
| Count of `extend`, with the number of distinct extension points | requirements + models | Extension effort scales with model count; regression cost scales with it at every Odoo upgrade |
| Count of `build`, by deliverable type (Odoo module / service / mobile app / web app) | requirements + deliverables | The four types have different unit costs; `02-05` §5.1 already distinguishes them |
| Count of `buy`, with subscription exposure | components | `L6` is opex, not capex, and requires CFO approval each |
| Count of `undetermined` | requirements | **The size of what is not yet known** — the number a Board should be shown alongside any estimate |
| Distinct `component` count | modules/systems | Test surface, licence obligations (`CO-004`), upgrade regression scope |
| `extend` requirements per OCA module with incomplete v19 migration | requirements | Migration effort `02-05` §3 records but does not size |

## 7.2 The three figures that must be restated once determination completes

| Figure | Current value | Basis | Restated by |
|---|---|---|---|
| Layer coverage percentages | L1 28 / L2 24 / L5 25 | 1,180-requirement superseded baseline | This document §5 |
| Custom development effort | 834 PW | 80 deliverables, derived from the same baseline | `GV-007` |
| Programme cost | $455K–780K | Derived from 834 PW; disowned by audit `H-02` | `CO-005`, then `GV-008` |

**Rule `FG-09`.** Until the determination is complete for a wave's requirement set, **no cost
figure may be quoted for that wave** other than as a range with the `undetermined` count
displayed beside it.

---

# 8. Execution Plan

## 8.1 Sequence

| Step | Activity | Output | Gate |
|---|---|---|---|
| **0** | **Resolve `RQA-15`.** Sample 200 requirements stratified across all 11 categories; determine independently whether reading R-1 or R-2 in §5.3 holds | A stated finding: is the `Layer` column evidence or noise? | **Before any other determination work.** Everything downstream depends on the answer |
| **1** | Stand up a reference Odoo 19 CE + OCA instance with representative 1000FiX data | The instance against which `E-01` evidence is executed | Cannot determine `fit` without it |
| **2** | Determine Wave 1 requirements (13 modules + P03, ~600 rows) | `fit_gap` populated with evidence | Wave 1 gate |
| **3** | Raise `FG-nnn` and write the FDS for every Wave 1 `extend`/`build` | Wave 1 gap set | Before Wave 1 build starts |
| **4** | Publish the restated coverage position to `GV-007` and `CO-005` | Measured inputs | Before `GV-008` goes to the Board |
| **5** | Repeat per wave, one wave ahead of its build | Rolling determination | Each wave gate |
| **6** | Re-verify at every wave gate: OCA v19 status changes, Odoo releases, licences change | Re-dated determinations | `PG-M4` |

**Rule `FG-10` — determination runs one wave ahead of build, never in the same wave.** A
determination made during the wave it affects is made under schedule pressure, and schedule
pressure has exactly one effect on a fit-gap: it produces fits.

## 8.2 Throughput and its constraint

The binding constraint is not analyst time; it is **step 1**. Without a running reference instance
holding representative data, `E-01` cannot be executed, every `fit` claim falls to
`confidence: asserted`, and rule `FG-02` excludes it from costing. Standing up that instance is
therefore the first dependency of the programme's cost baseline, and it is `BE-001`'s
responsibility.

## 8.3 Re-verification triggers

| Trigger | Effect |
|---|---|
| An OCA module reaches or loses v19 status | Re-determine every requirement citing it |
| Odoo 20 is released | Re-determine every `extend`; `CN-02` exposure is realised here |
| A licence changes (BSL conversion, AGPL obligation) | Re-determine every affected `L4` |
| A commercial component's terms change | Re-determine the `buy`, per `02-05` §6 annual review |
| A requirement changes under `RQ-005` | Its determination is invalidated and re-made |

---

# 9. Decisions Recorded

| # | Decision | Options | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| D-01 | Determination granularity | (a) Per module; (b) per requirement | **(b) Per requirement** | A module "90% covered" says nothing about the ten requirements that are not, and those ten carry the cost | 3,389 determinations, not 79 |
| D-02 | Whether the `Layer` column may be read as a fit-gap result | (a) Adopt it; (b) treat it as unvalidated until tested | **(b)** | It contradicts the module's own §16.1 in every case measured. Adopting either side without testing would be choosing a cost answer before doing the analysis | §8.1 step 0 |
| D-03 | Default disposition for unassessed requirements | (a) `fit`; (b) `undetermined`, counted | **(b)** | A default of `fit` makes the unknown invisible and always understates cost | `undetermined` appears in every published figure |
| D-04 | Evidence standard for `fit` | (a) Documentation citation; (b) executed demonstration | **(b)** | Odoo documentation describes capability, not this business's requirement. `E-01` is the control that keeps `H-02` from recurring | Requires a reference instance (`BE-001`) before determination can start |
| D-05 | Whether `extend` and `build` are one disposition or two | (a) One (`L5`); (b) two | **(b)** | They carry entirely different upgrade exposure. `CN-02` is the programme's largest silent risk | `extend` requires `E-04` naming the extension point |
| D-06 | Where `CD` identifiers are allocated | (a) Here; (b) `BE-005` | **(b)** | 31 `CD` identifiers already collide; allocating more would compound `RQA-10` | Gaps carry `FG-nnn`; `BE-005` maps them |
| D-07 | Whether to publish an effort estimate here | (a) Yes; (b) No — supply inputs | **(b)** | `PGD-A1-05` records that the programme already carries three uncontrolled estimates | §7 supplies inputs to `GV-007` |

---

# 10. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| Q-01 | Is the `Layer` column evidence or a default? | Solution Architect | **Now** | Every downstream cost figure |
| Q-02 | Who funds and stands up the reference Odoo 19 CE + OCA instance, and when? | CTO | **Now** | `E-01`; therefore all `fit` determinations |
| Q-03 | Which register governs the OCA v19 migration status, and who re-checks it? | Enterprise Architect | W1 | `E-05`; `02-05` §3 records status with no date |
| Q-04 | Does the CFO accept `FG-09` — that no wave cost may be quoted without its `undetermined` count displayed? | CFO | W1 | `GV-008` |
| Q-05 | Are the business owners named in `FG-03` released to give `E-07` acceptance at the required rate? | Programme Director | W1 | Determination throughput |
| Q-06 | Does the RFP's evaluation methodology (§17) need restating once the true build proportion is known? | Procurement | W1 | `CO-002`, `CO-003` |

---

# 11. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | Six dispositions defined, mutually exclusive, with `undetermined` counted | §3.1 |
| AC-02 | Disposition and layer distinguished as separate attributes with a stated relationship | §3.2 |
| AC-03 | An evidence standard published per disposition, with `fit` requiring executed demonstration | §4.3 |
| AC-04 | The determination sequence is binding and ordered | §4.2, `FG-04` |
| AC-05 | Every coverage figure in circulation is reconciled or shown to be unsupportable, with its arithmetic reproduced | §5.1–§5.4 |
| AC-06 | The honest starting position is stated: 3,389 `undetermined` | §5.5 |
| AC-07 | The FDS content standard is complete enough for a business owner to accept against | §6.1 |
| AC-08 | `FG-nnn` swept for collisions before reservation | §6.2, 02:15 (+06) |
| AC-09 | No effort or cost estimate is published; measured inputs are supplied to `GV-007` | §7 |
| AC-10 | Roll-ups regenerated from source rows before issue | `PG-M10` |

---

# 12. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `RQ-001` | The requirement set, the denominator and the `fit_gap`/`layer` attributes |
| Upstream | `02-05` §1–§7 | The layer model, the components, the build-vs-buy positions |
| Upstream | `05-01` §2.3 | The superseded layer distribution this document supersedes |
| Downstream | `GV-007` | Estimation model consuming §7 inputs |
| Downstream | `GV-008`, `CO-005` | Budget baseline and TCO, which may not be set before §7 is supplied |
| Downstream | `AR-003` | SDD, written from the FDS for every `extend`/`build` |
| Downstream | `BE-005` | CD register, mapping `FG-nnn` → `CD-nnn` |
| Downstream | `AR-007` | Odoo module architecture standard, which governs every `extend` |
| Downstream | `QA-003` | Test cases derived per disposition; a `fit` is tested differently from a `build` |
| Lateral | `RQ-004` | Trace: requirement → disposition → gap → design → code → test |
| Lateral | `RQ-006` | The NFRs each gap must satisfy |

---

# 13. References

**Within this repository**
[`RQ-001`](RQ-001_Software_Requirements_Specification.md) ·
[`RQ-004`](RQ-004_Requirements_Traceability_Matrix.md) ·
[`RQ-006`](RQ-006_Non_Functional_Requirements_Specification.md) ·
[`RQ-008`](RQ-008_Use_Case_and_User_Story_Specification.md) ·
[`RQ-009`](RQ-009_Business_Rules_Specification.md) ·
[`../PGD-000_Master_Register_of_Project_Guiding_Documents.md`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md)

**Workspace**
`../../1000fix_ERP_Module/02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md` §1–§7 ·
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-01` §1.3, §2.3 ·
`../../1000fix_ERP_Module/03_Modules/` §5 and §16.1 of all 79 specifications ·
`../../1000fix_ERP_Module/00_Governance_and_Charter/00-06_Documentation_Audit_Report.md`

**External**

| Reference | Verified on |
|---|---|
| ISO/IEC/IEEE 29148:2018 §5.2.5, §5.2.8 | 2026-08-18 |
| ISO/IEC 25010:2023 — functional suitability | 2026-08-18 |
| IEEE 1016-2009 — cited for the FDS/SDD boundary | 2026-08-18 |
| Odoo 19 Community Edition, LGPL-3 | 2026-08-12 (`02-05`) |
| OCA repository v19 migration status | **Undated in source** — open question `Q-03` |

---

# 14. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. Disposition taxonomy and evidence standard published; three coverage positions reconciled and shown unsupportable; findings `RQA-14`, `RQA-15`, `RQA-16` raised; starting position stated as 3,389 `undetermined` | *Pending — `GV-002`* |

---

*`RQ-003` · Category 01 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
