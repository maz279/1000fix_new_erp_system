---
id: BE-009
title: Technical Debt Register & Refactoring Policy
category: 07 — Build Engineering & Development Standards
code: BE
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Chief Architect
approver: ERP Design Authority
standards_basis: >
  ISO/IEC 25010:2023 maintainability · ISO/IEC 5055:2021 (automated source code quality measures) ·
  Fowler technical-debt quadrant · SEI technical-debt management framework
traces_to: >
  PGD-000 BE-009 · AR-012 §5.2 (promotion rule, non-zero violation counts) · GV-009 (wave gates) ·
  GV-005 (RAID) · BE-008 SPR-29 (10% allowance) · BE-007 §7 (currency watch)
depends_on: BE-005 (component identity) · BE-006 (README deferred-work section) · AR-012 (drift metrics)
verified_on: 2026-08-18
enumeration_timestamp: 2026-08-18 13:06 (+06)
priority: P2
needed_by: W2
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# BE-009 — Technical Debt Register & Refactoring Policy

### Category 07 · Code `BE` · ISO/IEC 25010:2023 · ISO/IEC 5055:2021 · Fowler quadrant

---

## 1. Purpose

`PGD-000` states the case in one line: *"A 36-month, 9-wave programme with wave-gated funding will
accumulate debt structurally. Without a register it accumulates invisibly."*

Three properties of this programme make that structural rather than probable. **Funding is gated**,
so a wave under pressure trades quality for a gate date and the trade is invisible after the gate
closes. **Every wave before W8 is over capacity** (`BE-008` §6.1, 1.69× overall, 5.87× in Wave 1), and
overloaded waves shed exactly the work that has no immediate consumer — tests, documentation,
migration cleanliness. And **the team changes** across 36 months, so debt taken by one group is
inherited by another that does not know why.

This document establishes the register, the classification, the measurement, the repayment allocation
and the ceiling above which feature work stops.

> **Its most useful section is §4, and §4 was written before a line of code exists.** The programme
> already carries **15 identified debt items totalling 6,550 counted instances — 1,387 of them
> discrete, actionable pieces of work** (§4.1 explains the two figures). Every one is recorded
> somewhere in the estate, and none is in a register with an owner, a cost and a repayment date. Debt does not begin at the first commit. It began when the first specification
> declared an event that no catalogue registered.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | What counts as technical debt here, and what does not |
| 2 | The **classification** — deliberate/inadvertent × prudent/reckless, plus a severity |
| 3 | The `DBT-nnn` register — schema, allocation and lifecycle |
| 4 | The **inherited debt position**, counted at issue |
| 5 | How debt is recorded — the four routes by which an item enters the register |
| 6 | **Measurement** — principal, interest, and the metrics that are not proxies for it |
| 7 | The **repayment allocation** and the ceiling that stops feature work |
| 8 | Refactoring policy — when it is permitted, how it is made safe, and when it is not |
| 9 | Wave-gate review and reporting |

**Explicitly out of scope**

| Topic | Owned by | Why |
|---|---|---|
| Defects | `QA-007` defect management | A defect is behaviour that is wrong; debt is behaviour that is right and expensive to change |
| Risks | `GV-005` RAID | A risk may not happen. Debt has already happened. §5.4 covers escalation between the two |
| Architecture fitness functions and drift metrics | `AR-012` §4, §8 | This document **consumes** violation counts; `AR-012` defines the checks |
| Architecture exemptions | `AR-012` §6 | An exemption with an expiry is the mechanism; a `DBT-` entry is the record |
| Scope reduction | `GV-006` §7 | Descope removes work; debt repayment restores quality in work already done |
| Dependency currency and end-of-life | `BE-007` §7 | An out-of-date dependency is `BE-007`'s; the **cost of being behind** is recorded here |
| Coding standards | `BE-002` | A violation of a standard is prevented, not owed |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| **Every developer** | §5 — how to record debt in thirty seconds, so that it is recorded |
| Chief Architect | §4's inherited position; §7's ceiling; §8's refactoring approvals |
| Programme Director / Steering | §7.3 — the ceiling is a **funding** control, not a technical preference |
| Wave-gate assessors | §9's gate report |
| Implementation vendor | The standard by which delivered quality is assessed beyond the Definition of Done |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Conformance | Departure and rationale |
|---|---|---|
| **ISO/IEC 25010:2023** | Debt is expressed against maintainability sub-characteristics — modularity, reusability, analysability, modifiability, testability | Full |
| **ISO/IEC 5055:2021** | Automated source-code measures for reliability, security, performance efficiency and maintainability | **Partial.** §6.2 explains why the automated measure is a *supporting* signal here rather than the register's basis |
| **Fowler technical-debt quadrant** | Deliberate/inadvertent × prudent/reckless | Full, with a severity added — §3.2 |
| **SEI technical-debt management** | Identify, measure, prioritise, repay, monitor | Full; §5–§9 follow the sequence |

### 2.2 Source material relied on

| Source | Contribution |
|---|---|
| `AR-012` §5.2 | The four non-zero violation counts — `FF-13` 953, `FF-14` 55, `FF-27` 34, `FF-29` 11 — and the promotion rule that manages them |
| `AR-012` §5.3, §6, §8 | Unsatisfiable checks, the exemption mechanism, and the drift metrics §6.3 consumes |
| `PGD-AUDIT-001` … `PGD-AUDIT-004` | The finding populations §4 counts |
| `00-06`, `00-07` | `H-03`, `H2-04`, `H2-06`, `H2-07` and the register-completeness findings |
| TSS §25.1 | Ten inherited defects that affect the build |
| `02-05` §3 | The sixteen OCA modules not yet migrated to v19 |
| `BE-005` §12 | `BEA-01`…`BEA-08` |
| `BE-007` §7.1 | `BEA-16` — MinIO end of life |
| `BE-008` §7.2 | The 10% standing repayment allowance this document sets |
| `GV-005` | The RAID register debt escalates into |

### 2.3 Identifier space

| Space | Form | Allocating authority | Verified |
|---|---|---|---|
| `DBT-nnn` | `DBT-001`, `DBT-002`, … | **Chief Architect** | Swept across all 699 workspace files at 2026-08-18 13:06 (+06): **0 existing uses**. Free |

> **`TD-nn` was the obvious choice and is taken.** `02-05` §10 uses `TD-01`…`TD-15` for technology
> decisions, and the space carries **366 occurrences** across the estate. Choosing it would have
> created the 49th collision in a document whose purpose is partly to stop them. Swept before
> allocation, per `BE-005` §4.

---

## 3. What Counts, and How It Is Classified

### 3.1 The definition

> **Technical debt is a property of an artefact that makes future change more expensive, that the
> programme has accepted, and that has an identifiable cost to remove.**

Three tests, all of which must hold:

| Test | Excludes |
|---|---|
| It makes **future change** more expensive | A slow query that is fast enough forever is not debt; it is a design choice |
| It has been **accepted** — knowingly or not | Work in progress is not debt |
| It has an **identifiable removal cost** | *"The architecture could be nicer"* is not debt; it is an opinion |

| # | Rule |
|---|---|
| **`DBT-R01`** | Debt is recorded against an **artefact** — a `BE-005` component, a register, a document or a dependency — never against a person or a squad |
| **`DBT-R02`** | *"We should refactor this"* is not a register entry. An entry states **what is owed, why it costs, and what removing it costs** |
| **`DBT-R03`** | Debt is not a defect (`QA-007`) and not a risk (`GV-005`). §5.4 governs movement between them |

### 3.2 Classification

Fowler's quadrant, plus a severity, because a register with only a quadrant cannot be prioritised.

| | **Deliberate** | **Inadvertent** |
|---|---|---|
| **Prudent** | *"We ship the rule-based dispatcher in W2 and add ML in W6."* Recorded, owned, dated. **The only acceptable way to take debt** | *"Now we understand the party model, we would have modelled roles differently."* Learning. Recorded without blame |
| **Reckless** | *"No time for the negative tests."* **Not permitted.** `BE-006` §5 criterion 7 blocks it, and an override is an `AR-012` §6 exemption with an expiry | *"What is an outbox?"* Prevented by `BE-002`, `AR-007` and review — and where it happens, it is a training signal, not a debt-management one |

| Severity | Definition | Repayment |
|:--:|---|---|
| **S1** | Blocks a wave gate, a statutory obligation or a `P0` business path | Before the gate. Non-negotiable |
| **S2** | Materially raises the cost of the **next** wave's work | Within the next wave |
| **S3** | Raises cost locally; contained | Within two waves |
| **S4** | Cosmetic or speculative | Repaid opportunistically; reviewed annually for closure |

| # | Rule |
|---|---|
| **`DBT-R04`** | **Deliberate-reckless debt is not available.** Where the pressure is real, the route is an `AR-012` §6 exemption with a named owner and an expiry date — which is deliberate-prudent debt with paperwork |
| **`DBT-R05`** | Every entry carries a quadrant **and** a severity. The quadrant explains how it arrived; the severity decides when it leaves |

---

## 4. The Inherited Position

Counted at 2026-08-18 13:06 (+06), before any code exists. Each item is recorded elsewhere in the
estate; none was in a register with an owner, a cost and a date.

| `DBT` | Item | Instances | Quad | Sev | Source | Repayment |
|---|---|---:|:--:|:--:|---|---|
| `DBT-001` | **Declared events not registered in the event catalogue** | **953** | Inadv. | **S1** | `AR-012` `FF-13`; `AR-009` §10.6 | `FF-13` blocks at the W1 gate |
| `DBT-002` | **Unreciprocated module dependency declarations** | **55** | Inadv. | **S2** | `FF-14`; `AR-006` §7.3 | W1 gate |
| `DBT-003` | **Entities declared owned by more than one module** | **34** | Inadv. | **S2** | `FF-27`; `AR-008` §7.5 | W1 gate |
| `DBT-004` | **Dependency cycles outside the six approved co-design pairs** | **11** | Delib.-prudent | **S2** | `FF-29`; `AR-006` §4.1 | W2 gate |
| `DBT-005` | **Roles used and unregistered** (`R39`–`R46`), `R60` duplicating `R32`, `R54`/`R57` undefined | **11** | Inadv. | **S1** | `H2-07`; TSS §25.1.2; `FF-26` | **W0 — blocking** |
| `DBT-006` | **Segregation-of-duties controls used and unregistered** (`SOD-13`…`SOD-30`) | **18** | Inadv. | **S1** | `H2-06`; TSS §25.1.3 | **W0 — blocking** |
| `DBT-007` | **Colliding KPI identifiers** | **22** | Inadv. | **S2** | `H2-04`; TSS §25.1.4 | W0, before instrumentation |
| `DBT-008` | **`NFR-090`/`091`/`092` each carrying two requirements; `NFR-088`/`089` duplicated** | **5** | Inadv. | **S2** | `AP-02`; `RQA-13`; TSS §25.1.5 | W0 |
| `DBT-009` | **Acceptance criteria in run-on prose, not decomposable** | **237** | Inadv. | **S2** | `RQA-25` | W1, as refinement (`SPR-27`) |
| `DBT-010` | **Requirement rows containing no modal verb** | **3,347** | Inadv. | **S2** | `RQA-02` | Phased by wave, W1–W4 |
| `DBT-011` | **Requirements allocated to no wave** | **1,816** | Inadv. | **S1** | `PGD-A2-04` | **W0 — blocking** (`SPR-10`) |
| `DBT-012` | **OCA modules not migrated to v19** (`field-service` 8, `helpdesk` 8) | **16** | Delib.-prudent | **S2** | `02-05` §3; `A-03`, 12–20 PW | W0 assessment, W2 delivery |
| `DBT-013` | **Navigation footers that do not resolve** | **14** | Inadv. | S3 | `PGD-A2-16` | W1 |
| `DBT-014` | **Business-rule identifiers double-allocated** (`BRU-ECM-01`…`-10`) | **10** | Inadv. | **S1** | `RQA-27` | **W0** |
| `DBT-015` | **MinIO at end of life** — repository archived 25 April 2026, no named fallback | **1** | Inadv. | **S1** | `BE-007` §7.1 `BEA-16` | **W0 — blocking Wave 1** |
| | **Total** | **6,550** | | | | |

**Verification** *(`PG-M10`, regenerated from the rows above)*: 953 + 55 + 34 + 11 + 11 + 18 + 22 + 5
+ 237 + 3,347 + 1,816 + 16 + 14 + 10 + 1 = **6,550** ✓ across **15 items**, of which **6 are S1**.

### 4.1 How to read that total

The 6,550 is dominated by two rows — `DBT-010` (3,347 requirement rows) and `DBT-011` (1,816
unallocated requirements) — which are estate-wide properties rather than 5,163 separate pieces of
work. Removing those two leaves **1,387 discrete instances across 13 items**, which is the number a
repayment plan is built against.

> **Both numbers are reported.** 6,550 is the honest count of instances; 1,387 is the count of things
> a squad can pick up. Reporting only the smaller understates the estate's condition; reporting only
> the larger makes the register look unactionable and it will be ignored.

### 4.2 What the position means

| Observation | Consequence |
|---|---|
| **Six S1 items exist before the first commit.** Four are marked W0-blocking | Wave 1 cannot start cleanly. `GV-009` already assesses Gate 1 as carrying five blockers, four of them P0; these are the same class of item, now costed and owned |
| **Fourteen of fifteen items are `Inadvertent`** | This is not a team that cut corners. It is an estate written by many hands with **no register and no version control** — which is exactly what `PG-M12` and `BE-003` §3 address |
| **`DBT-001` is 953 instances against an event catalogue covering 6.5% of the surface** (`A2-04`) | The largest single item, and it is a *specification* debt that becomes a *code* debt the moment a module emits an unregistered event |
| **`DBT-015` is four months old and was found by writing this category** | `BE-007` `LX-29`…`LX-32`'s continuous currency watch exists because of it |
| **The 48 CD collisions are absent from this table** | Closed by `BE-005` §6 on the same date. Recorded here so the closure is visible: the estate's largest identifier debt was repaid by writing a register |

---

## 5. Recording

### 5.1 Entry schema

```yaml
# docs/debt/DBT-nnn.yaml — illustrative. This example allocates no identifier (DBT-R36).
id: DBT-nnn
title: "Rule-based dispatch scoring; ML deferred to W6"
artefact: CD-M02-01                # BE-005 identifier, register, document or dependency
quadrant: deliberate-prudent
severity: S2
raised_by: squad-field-operations
raised_on: 2026-11-04
owner: Solution Architect

principal: "8 PW to replace the rule engine with the ML gateway and retrain."
interest: "Every new dispatch constraint is coded twice — once in rules, once for the future model.
           ~0.5 PW per constraint; 6 constraints expected before W6 → ~3 PW carrying cost."
trigger: "ADR-014; M26 ML gateway not available until W6."
consequence_if_unpaid: "Rule engine calcifies; W6 ML adoption slips a wave."

repay_by: W6
repay_in: sprint            # sprint | wave | gate
linked:
  adr: ADR-014
  exemption: null           # AR-012 §6 exemption, if the debt is a live rule breach
  risk: null                # GV-005 identifier, if escalated (§5.4)
status: open                # open | scheduled | repaid | accepted-permanent | superseded
```

| # | Rule |
|---|---|
| **`DBT-R06`** | **`principal`, `interest` and `consequence_if_unpaid` are mandatory and quantified.** An entry with an unquantified interest cost cannot be prioritised against feature work, so it will lose every time |
| **`DBT-R07`** | Every entry names an **owner** and a **repay-by wave**. An entry without both is not managed; it is recorded |
| **`DBT-R08`** | The register lives in the repository at `docs/debt/`, under version control. It is not a spreadsheet and not a ticket-system label |
| **`DBT-R09`** | `status: accepted-permanent` requires **Design Authority approval** and an annual review. It is the honest way to close an item nobody will ever repay, and it is far better than an entry that stays `open` for three years |

### 5.2 The four entry routes

| Route | Trigger | Who |
|---|---|---|
| **Deliberate** | A decision to defer, taken at design or in a sprint | The squad, at the moment of the decision |
| **Discovered** | Found while working on something else | The developer who found it, in the same PR |
| **Automated** | A fitness function or scan reports a violation that is exempted rather than fixed | Generated from the `AR-012` §6 exemption |
| **Audit** | An audit finding whose remediation is not immediate | The auditor, at finding closure |

| # | Rule |
|---|---|
| **`DBT-R10`** | **Recording takes under two minutes or it will not happen.** `make debt` generates the skeleton from the current branch's CD identifier |
| **`DBT-R11`** | A `TODO` in code carries a `DBT-` identifier where it represents debt, not merely an issue (`XS-11`) |
| **`DBT-R12`** | `BE-006` §4.2's README section *"Known limitations and deferred work"* carries `DBT-` identifiers. **Every entry there must exist in the register**, checked in CI |
| **`DBT-R13`** | An `AR-012` §6 exemption **automatically** creates a `DBT-` entry with the exemption's expiry as its repay-by date. An exemption without a debt entry is a rule that has been quietly switched off |

### 5.3 What must never be recorded as debt

| Not debt | Why | Where it goes |
|---|---|---|
| A missing feature | Absence of scope, not degraded quality | Backlog (`BE-008`) |
| A defect | Wrong behaviour | `QA-007` |
| A coding-standard violation | Prevented by `BE-002` §10, not owed | Fix it |
| A disagreement about design | Not a cost | `AR-004` ADR, or drop it |
| A dependency being one version behind | Routine currency | `BE-007` §4.2 — becomes debt only when **`LX-12`**'s three-month deferral triggers |

### 5.4 Movement between registers

| From | To | Trigger |
|---|---|---|
| Debt → **Risk** (`GV-005`) | An S1 item that will not be repaid before it bites | Chief Architect, at gate review |
| Debt → **Change request** (`GV-003`) | Repayment changes scope, cost or schedule | Programme Director |
| Risk → Debt | A risk materialises and the response is a deferred fix | Risk owner |
| Defect → Debt | A defect is mitigated rather than fixed, and the mitigation has a carrying cost | QA Lead + Chief Architect |
| Debt → **Closed** | Repaid, superseded, or `accepted-permanent` | Owner, evidenced |

---

## 6. Measurement

### 6.1 Principal and interest

| Term | Definition | Unit |
|---|---|---|
| **Principal** | The effort to remove the debt | Person-weeks |
| **Interest** | The recurring extra effort caused by not removing it | Person-weeks **per wave** |
| **Payback** | Principal ÷ interest per wave | Waves |

| # | Rule |
|---|---|
| **`DBT-R14`** | An item whose **payback is shorter than the waves remaining** is repaid; the arithmetic decides, not advocacy |
| **`DBT-R15`** | Interest is **re-estimated at every wave gate**. Interest usually rises as more code depends on the compromise, and an interest figure fixed at raise-time understates the position by construction |
| **`DBT-R16`** | Both figures are estimate class 4 or 5 and are labelled as such (`GV-007` §3.2). A precise-looking debt estimate is the same unearned precision `AF-02` recorded |

### 6.2 Why the automated measure is a supporting signal, not the basis

ISO/IEC 5055:2021 defines automated source-code measures, and static-analysis platforms report a
"technical debt ratio" in hours. Both are used here — and neither is the register's basis.

| Reason | Detail |
|---|---|
| It cannot see the largest items | `DBT-001`'s 953 unregistered events, `DBT-005`'s role register and `DBT-011`'s unallocated requirements are all **specification** debt. No source-code measure detects any of them |
| It cannot see deliberate-prudent debt | A rule-based dispatcher deliberately shipped ahead of an ML model is clean, well-tested code. A scanner reports zero |
| Its hours are not this programme's hours | A generic remediation-cost model has no knowledge of Odoo, of Bengali content obligations, or of a 0.78 delivery factor |

| # | Rule |
|---|---|
| **`DBT-R17`** | Automated measures are reported as a **trend** alongside the register, never as a substitute. A falling scanner score with a growing register is the normal and correct picture during a build |

### 6.3 Metrics

| Metric | Purpose | Cadence |
|---|---|---|
| Open items by severity | The register's shape | Per sprint |
| **Total principal (PW)** | The size of the obligation | Per wave gate |
| **Total interest (PW/wave)** | What it costs to keep it | Per wave gate |
| **Debt ratio** — interest ÷ wave capacity | §7's ceiling input | Per wave gate |
| Age of open S1 and S2 items | Whether repayment actually happens | Per sprint |
| Items raised vs repaid | Whether the register is converging | Per wave |
| `AR-012` §8 drift metrics | Structural direction | Continuous |
| Exemptions in force and expiring | `DBT-R13` linkage | Per sprint |

---

## 7. Repayment

### 7.1 The standing allocation

| # | Rule |
|---|---|
| **`DBT-R18`** | **10% of every squad's sprint capacity is reserved for debt repayment**, removed before commitment (`BE-008` `SPR-29`) |
| **`DBT-R19`** | The allocation is **spent on register items**, prioritised by severity then payback — not on whatever the squad finds irritating |
| **`DBT-R20`** | Unspent debt capacity is **reported, not reallocated**. A squad that never spends it either has no debt (verifiable against the register) or is not repaying (also verifiable) |
| **`DBT-R21`** | S1 items are repaid **outside** the 10%, as gate-blocking work. Ten percent is the mechanism for S2 and S3 |

### 7.2 Sequencing

| Position | Repaid |
|---|---|
| **In the sprint that creates it** | Debt whose principal is under half a day. Recording and deferring costs more than fixing |
| **In the next sprint** | S1 items raised mid-wave |
| **In the wave's final two sprints** | S2 items whose repayment would otherwise destabilise mid-wave work |
| **Before the gate** | Every S1 item. `GV-009` gate criterion |
| **In a dedicated sprint** | **Only** where an item's principal exceeds 20% of a wave's capacity — a "hardening sprint" is otherwise a symptom of `DBT-R18` not being honoured |

### 7.3 The ceiling

The control `PGD-000` asks for: *"the ceiling above which feature work stops."*

| Debt ratio (interest ÷ effective wave capacity) | Position |
|---|---|
| **< 5%** | Healthy. Normal 10% allocation |
| **5–10%** | Watch. Allocation rises to 15%; reported at the gate |
| **10–15%** | **Concern.** Allocation rises to 25%; **no new S2 debt may be taken** without Design Authority approval |
| **> 15%** | **Ceiling breached. Feature work stops** until the ratio returns below 10% |

| # | Rule |
|---|---|
| **`DBT-R22`** | The ceiling is assessed at every wave gate by the Design Authority and reported to Steering. It is a **funding decision**, not a technical preference — stopping feature work costs money and is decided by the body that spends it |
| **`DBT-R23`** | The ceiling **cannot be waived by a delivery deadline**. It exists precisely for the moment a delivery deadline argues against it |
| **`DBT-R24`** | Statutory and compliance debt — `DBT-005`, `DBT-006`, and anything touching Mushak, TDS, PDPA, BEFTN or payroll — is outside the ratio. It is repaid regardless of the ceiling, because the consequence is a legal one and does not respond to prioritisation |

> **A ceiling nobody has ever hit is a ceiling set too high.** §4's position implies a starting ratio
> that must be computed at the Wave 1 gate before this scale can be calibrated. The thresholds above
> are a starting position, explicitly subject to revision at the W1 gate once `DBT-001`…`DBT-015`
> carry principal and interest figures. Recorded as `Q-02`.

---

## 8. Refactoring

### 8.1 When it is permitted

| Situation | Permitted? |
|---|---|
| Repaying a register item within the 10% allocation | **Yes** |
| Making a change possible — the code must move before the feature can be added | **Yes**, in the same PR, as a **separate commit** (`GW-11`) |
| Improving code you are already changing, within its blast radius | **Yes**, if the PR stays under `GW-05`'s 400 lines |
| Improving code you are not otherwise changing | **No.** Raise a `DBT-` entry |
| Refactoring during a hotfix | **Never** (`BE-003` §9 step 3) |
| Refactoring on a release branch | **Never** (`GW-37`) |
| Refactoring across a module boundary | **Only** with an `AR-004` ADR — it is an architecture change |

### 8.2 Making it safe

| # | Rule |
|---|---|
| **`DBT-R25`** | **Characterisation tests first.** Code without tests is not refactored; it is tested, then refactored. A refactor of untested code is a rewrite with optimism |
| **`DBT-R26`** | Refactoring commits **change no behaviour**. A commit that both refactors and changes behaviour cannot be reviewed or reverted independently (`GW-11`) |
| **`DBT-R27`** | Refactoring across a public interface — `libs/**`, `contracts/**` — follows `LX-08` versioning and `FF-31` compatibility. There is no such thing as an internal refactor of a published contract |
| **`DBT-R28`** | A refactor touching an Odoo model with stored data requires a **migration** and follows `SQL-05`'s two-release lifecycle. Renaming a column is not a refactor; it is a schema change |
| **`DBT-R29`** | Large refactors are **incremental and continuously shippable**. A six-week refactor branch breaches `GW-03` by a factor of ten and will not merge |

### 8.3 The Odoo-specific constraint

Refactoring in an Odoo estate has one property that does not exist in ordinary application code, and
it must be stated because it will otherwise be discovered expensively.

> **A model, field or table rename propagates into stored data, `ir.model.data` XML identifiers,
> record rules, access-control rows, views, reports, translations and — through `AS-05`'s inheritance
> chains — into every module that extends it.**

| # | Rule |
|---|---|
| **`DBT-R30`** | A rename of a model, field or table in a module that any other module `_inherit`s requires an ADR, a migration, and a **coordinated release across every dependent module** (`AR-006`). It is planned into a wave, never done opportunistically |
| **`DBT-R31`** | The cheapest moment to fix an Odoo naming or modelling decision is **before the first production record exists**. `AR-007` §4's naming rules and `FF-02` exist to make that moment unnecessary — and where a naming debt survives into production, its principal should be estimated at several times its pre-production cost |

---

## 9. Wave-Gate Review

`GV-009` requires evidence classes with named assessors. This document contributes one, generated:

```
# make debt-report WAVE=W1  → GV-009 evidence
Wave 1 debt position
  Open items                     31   (S1: 4 · S2: 12 · S3: 11 · S4: 4)
  Principal                      47 PW
  Interest                       6.2 PW / wave
  Debt ratio (interest ÷ 40.7)   15.2%   ⚠ CEILING BREACHED (DBT-R22)
  Raised this wave               22      Repaid this wave   9
  S1 items open at gate           4      ⛔ GATE BLOCKER
  Exemptions expiring next wave   3
  Inherited items still open      9 of 15
```

| # | Rule |
|---|---|
| **`DBT-R32`** | The report is **generated from the register**, not compiled by hand (`PG-M10`) |
| **`DBT-R33`** | **An open S1 item blocks the gate.** This is the mechanism that stops a wave being declared complete with known gate-blocking debt |
| **`DBT-R34`** | The report goes to Steering with the gate assessment, not only to the Design Authority. The ceiling is a funding decision (`DBT-R22`) |
| **`DBT-R35`** | The **inherited items** row stays in the report until all fifteen are closed. Fifteen items that predate the first commit will otherwise be forgotten within two waves |

---

## 10. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `BE-009-D-01` | Identifier space | (a) `TD-nn`; (b) `TDR-`; (c) **`DBT-nnn`** | **(c)** | `TD-nn` has 366 uses as the technology decision log; swept before allocation | A new space, but a verified-free one |
| `BE-009-D-02` | Register location | (a) Ticket system; (b) **files in the repository** | **(b)** | Debt must be diffable, reviewable and versioned with the code it describes; `PG-M12` is the estate's fourth-largest defect class | Requires `make debt` tooling so `DBT-R10` holds |
| `BE-009-D-03` | Debt measurement basis | (a) Automated ratio (ISO/IEC 5055); (b) **principal and interest, manually estimated**; (c) both | **(b) with (a) as a trend** | The largest items are specification debt no scanner can see | Estimates are class 4–5 and must be labelled |
| `BE-009-D-04` | Repayment funding | (a) Ad hoc; (b) **10% standing allocation**; (c) hardening sprints | **(b)** | Ad hoc means never at 1.69× capacity pressure; hardening sprints are a symptom of (b) not being honoured | `BE-008` `SPR-29` removes it before commitment |
| `BE-009-D-05` | The ceiling | (a) None; (b) Advisory; (c) **Hard, at a 15% debt ratio** | **(c)** | A ceiling that can be waived by a deadline is not a ceiling | Thresholds are provisional until W1 gate calibration (`Q-02`) |
| `BE-009-D-06` | Inherited debt | (a) Start the register at the first commit; (b) **count what already exists** | **(b)** | Six S1 items and 1,387 discrete instances exist before any code. A register that starts clean starts wrong | §4 becomes the largest section, and four W0-blocking items are exposed |

---

## 11. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | Who estimates principal and interest for `DBT-001`…`DBT-015`, and when? Without those figures §7.3's ratio cannot be computed | Chief Architect | **W0** | The ceiling; the W1 gate report |
| `Q-02` | Are §7.3's thresholds right for this programme, or does the W1 gate position require recalibration? | Design Authority | W1 gate | `DBT-R22` |
| `Q-03` | Do the four W0-blocking inherited items (`DBT-005`, `DBT-006`, `DBT-011`, `DBT-015`) stop Wave 1 starting, or are they carried? | Steering Committee | **W0 — blocking** | Wave 1 start |
| `Q-04` | Does the implementation vendor's contract oblige them to record and repay debt, and is the 10% allocation in their price (`CO-003`)? | CTO / Procurement | **W0** | `DBT-R18` against a vendor team |
| `Q-05` | Is `DBT-010` — 3,347 requirement rows with no modal verb — repaid, or accepted permanently with a compensating verification standard? | CTO / QA Lead | W1 | `RQA-02`; the size of the register |

---

## 12. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | The identifier space is verified free before allocation | §2.3, swept across 699 files |
| `AC-02` | Debt is defined by three tests, with explicit exclusions | §3.1, §5.3 |
| `AC-03` | The inherited position is counted, not asserted | §4, 15 items, 6,550 instances, verified |
| `AC-04` | Every entry carries principal, interest, owner and a repay-by wave | `DBT-R06`, `DBT-R07` |
| `AC-05` | Repayment has funded capacity, not only intent | `DBT-R18`, `BE-008` `SPR-29` |
| `AC-06` | The ceiling exists, is quantified, and cannot be waived by a deadline | §7.3, `DBT-R23` |
| `AC-07` | Refactoring rules address the Odoo-specific propagation constraint | §8.3 |
| `AC-08` | Gate reporting is generated and blocks on S1 | §9, `DBT-R32`, `DBT-R33` |

**Definition of done.** Complete when every criterion is met, `DBT-001`…`DBT-015` carry principal and
interest figures, the first `make debt-report` runs against a real wave, `PGD-000`'s `BE-009` row
moves to ✅ with a fresh timestamped enumeration, and the approver has signed.

---

## 13. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `AR-012` §5.2, §6, §8 | Violation counts, exemptions (`DBT-R13`) and drift metrics |
| Upstream | `PGD-AUDIT-001`…`004`, `00-06`, `00-07` | The finding populations §4 counts |
| Upstream | `BE-005` §12, `BE-007` §7.1 | `BEA-*` findings entering the register |
| Upstream | TSS §25.1 | Ten inherited defects |
| Downstream | `BE-008` `SPR-29` | The 10% allocation |
| Downstream | `GV-009` | §9's gate report; S1 items block |
| Downstream | `GV-005` | Escalation route (§5.4) |
| Downstream | `GV-003` | Repayment that changes scope becomes a `CR-nnn` |
| Downstream | `BE-006` §4.2 | README deferred-work entries carry `DBT-` identifiers |
| Lateral | `QA-007` | Defects, distinguished in §5.3 |
| Lateral | `AR-004` | ADRs for boundary-crossing refactors (`DBT-R30`) |

---

## 14. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` ·
[`_CATEGORY_OVERVIEW.md`](_CATEGORY_OVERVIEW.md) ·
[`BE-005`](BE-005_Custom_Development_CD_Master_Register.md) ·
[`BE-006`](BE-006_Component_Build_Specification_Standard.md) ·
[`BE-007`](BE-007_Dependency_Licence_and_SBOM_Management_Standard.md) ·
[`BE-008`](BE-008_Sprint_Model_Estimation_and_Backlog_Management_Standard.md) ·
`../02_Architecture_and_Design/AR-012_Architecture_Compliance_and_Fitness_Function_Standard.md` ·
`../00_Programme_Governance_and_Control/GV-005_RAID_Register.md` ·
`../00_Programme_Governance_and_Control/GV-009_Wave_Gate_and_Phase_Exit_Criteria_Handbook.md` ·
`../_AUDIT/PGD-AUDIT-004_Category_01_Requirements_Engineering_Audit.md`

**Workspace**
`../../1000fix_ERP_Module/00_Governance_and_Charter/00-06_Documentation_Audit_Report.md` ·
`../../1000fix_ERP_Module/00_Governance_and_Charter/00-07_Category_H_Audit_and_Repository_Integrity_Report.md` ·
`../../1000fix_ERP_Module/02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md` §3 ·
`../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §25.1

**External standards** *(all verified 2026-08-18)*
ISO/IEC 25010:2023 — maintainability characteristic ·
ISO/IEC 5055:2021 — automated source code quality measures ·
Fowler technical-debt quadrant · SEI technical-debt management framework

---

## 15. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. `DBT-nnn` space swept and allocated; three-test definition; quadrant plus severity; **the inherited position counted at 15 items and 6,550 instances, 6 of them S1**; principal/interest measurement; 10% funded allocation; a hard 15% ceiling; Odoo-specific refactoring constraints; generated gate reporting | *(unsigned — no constituted body, `PGD-A1-09`)* |

---

*`BE-009` · Category 07 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
