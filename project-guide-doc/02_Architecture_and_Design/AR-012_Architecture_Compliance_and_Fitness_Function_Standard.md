---
id: AR-012
title: Architecture Compliance & Fitness Function Standard
category: 02 — Architecture & Design
code: AR
project: 1000FiX ERP System v2.0
version: 1.1
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Chief Architect
approver: Design Authority (constituted under GV-002)
standards_basis: >
  Evolutionary architecture / fitness functions (Ford, Parsons, Kua) · ATAM (architecture evaluation) ·
  ISO/IEC/IEEE 42010:2022 · ISO/IEC 25010:2023
traces_to: >
  PGD-000 AR-012 · AS-01…AS-15 · 02-01 §10 ("non-negotiable architecture standards" with no
  detection mechanism) · AR-001 §6.5, §8.1, §10 · AR-005…AR-011
depends_on: AR-001 · AR-007 · PE-004 (CI/CD pipeline)
verified_on: 2026-08-18
priority: P2
needed_by: W2
enumeration_timestamp: 2026-08-18 02:05 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# AR-012 — Architecture Compliance & Fitness Function Standard

### Category 02 · Code `AR` · Evolutionary architecture · Fitness functions

---

## 1. Purpose

`02-01` §10 lists fifteen **"non-negotiable architecture standards"** — AS-01 through AS-15. They are
correct, they are well chosen, and **nothing detects a violation of any of them.**

Over 36 months, nine waves, 232 custom modules and a changing team, undetected architectural drift is
not a risk — it is a certainty. This document converts every architectural claim in Category 02 into
a **fitness function**: an automated or scheduled check with a pass/fail threshold and a named
consequence.

It also states the thing a compliance standard usually omits: **what happens when a check fails**, and
**what happens when a check is wrong**.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | The fitness-function taxonomy and the classification rule |
| 2 | **The complete fitness-function register** — 37 checks derived from `AR-001`…`AR-011` and `DA-001`…`DA-009` |
| 3 | Enforcement levels — blocking, warning, reporting — and how a check is promoted between them |
| 4 | The exemption procedure, with expiry |
| 5 | Wave-gate architecture review, and the manual checks that cannot be automated |
| 6 | Drift metrics and the architecture health report |
| 7 | Governance — who may add, change or retire a fitness function |

**Explicitly out of scope**

| Topic | Owned by | Why |
|---|---|---|
| The pipeline that runs the checks | `PE-004` | This document defines *what*; `PE-004` builds *how* |
| Code style and formatting | `BE-002` | Style is not architecture |
| Test strategy and coverage | `QA-001`, `QA-005` | A fitness function is not a unit test |
| Security scanning tooling | `SC-005`, `SC-009` | `FF-30` names the gate; SSDLC owns the tooling |
| The standards themselves | `AR-001`, `AR-005`…`AR-011`, `AR-007` | This document enforces; it does not legislate |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| Platform engineers (`PE-004`) | §4 is the implementation backlog |
| Every developer | §5 is what fails your build, and §6 is how to get an exemption honestly |
| Chief Architect | §7 wave-gate review and §8 drift metrics |
| Design Authority | §9 governance — a fitness function is an architectural commitment |
| Implementation vendor | The objective, automated acceptance standard |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Conformance | Departure |
|---|---|---|
| **Evolutionary Architecture** (Ford, Parsons, Kua) | Fitness functions as the mechanism for guided architectural change | Adopted in full, including the atomic/holistic and triggered/continual distinctions |
| **ATAM** | §7 wave-gate review evaluates against `AR-001` §10 quality-attribute scenarios | **Departure:** no full ATAM workshop is scheduled. Rationale: `AR-001` §10's scenarios already carry response measures; a workshop to elicit them again would be ceremony. A full ATAM is proposed only if the architecture is materially rebaselined |
| ISO/IEC/IEEE 42010:2022 | §5.6 correspondence rules; `AR-001` §14.1 CR-01…CR-06 are fitness functions here | |
| ISO/IEC 25010:2023 | Drift metrics grouped by quality characteristic | |

### 2.2 Source material

| Source | Contribution |
|---|---|
| `../../1000fix_ERP_Module/02_Architecture/02-01_*.md` §10 | AS-01…AS-15 — the standards with no mechanism |
| `.../05_Cross_Cutting_Specifications/05-06_*.md` §12 | AS-01…AS-15 **restated as testable rules with a verification column** — the closest the estate came to this document |
| `../../primary-doc/…Technology_Stack_Specification.md` §18.2 | The CI stage list, including model-registry and architecture stages |
| `AR-001` §6.5, §8.1, §10, §14.1 · `AR-005`…`AR-011` | The 37 checks |

### 2.3 What `05-06` §12 already achieved, and what was missing

`05-06` §12 restates AS-01…AS-15 with a *"How It Is Verified"* column — *"Static analysis in CI"*,
*"Model registry check in CI"*, *"Code review checklist"*. **That is genuinely most of the way there,
and it should be credited.**

Three things were missing, and they are what this document adds:

| Missing | Consequence |
|---|---|
| **A threshold** | *"Static analysis in CI"* does not say what fails |
| **A consequence** | Nothing states whether a violation blocks a merge, warns, or is reported |
| **An owner and an exemption path** | With no honest exemption route, a blocking check that is wrong gets disabled globally rather than exempted narrowly |

---

## 3. Taxonomy

| Axis | Kinds | Rule |
|---|---|---|
| **Scope** | **Atomic** — one artefact in isolation (a model has `company_id`) · **Holistic** — an emergent property across artefacts (no dependency cycle) | Holistic functions run less often and are usually the more valuable |
| **Timing** | **Continual** — every commit or build · **Triggered** — at a wave gate or on a schedule | Prefer continual. A triggered check finds a defect after it has been built on |
| **Enforcement** | **Blocking** — fails the build · **Warning** — reported, does not fail · **Reporting** — trend only | §5 |
| **Automation** | **Automated** · **Manual** — a checklist item at review | A manual check is a fitness function only if it has a named assessor and a recorded outcome |

---

## 4. The Fitness-Function Register

**37 functions.** Each states its source claim, scope, timing, enforcement, threshold and owner.

### 4.1 Boundary and structure

| ID | Check | Source | Scope | Timing | Enforce | Threshold |
|---|---|---|:--:|:--:|:--:|---|
| **FF-01** | No module reads another module's tables directly | AS-01, `AR-001` LB-01 | Holistic | Continual | **Block** | Zero cross-module table references outside the shared kernel |
| **FF-05** | Only Category G writes to `account.move` / ledger tables | `AR-001` LB-04 | Holistic | Continual | **Block** | Zero writes from a non-G module |
| **FF-07** | Category J writes no transactional aggregate; ML outputs are advisory records only | `AR-001` LB-06, `AR-011` §7.3 | Holistic | Continual | **Block** | Zero state mutations from J modules |
| **FF-08** | Party is one `res.partner` with `fix.party.role` records; no parallel party master | `AR-001` §6.3 | Holistic | Triggered (gate) | **Block** | Zero models with a duplicate party identity |
| **FF-10** | No business logic in views, controllers or portal code | AS-09 | Atomic | Continual | **Block** | Zero validations or rule evaluations in `controllers/` or `views/` |
| **FF-14** | Dependency reciprocity — every declared dependency is reciprocated | `RG-04`, `AR-006` §7 | Holistic | Continual | **Warn → Block at W1 gate** | Zero unreciprocated declarations (**currently 55**) |
| **FF-15** | Every §3.3 shared-concept row names an owner that defines the entity in its §10.1; every §3.2 owner appears in the dependency declaration | `AR-005` SC-05, SC-06 | Holistic | Continual | **Block** | Zero mismatches (**currently 0** — verified) |
| **FF-17** | Dependency layering — platform modules do not depend on domain modules | `AR-007` DL-01, DL-02 | Holistic | Continual | **Block** | Zero inversions |
| **FF-27** | Entity-name uniqueness — no entity declared owned by two modules | `AR-008` §7 | Holistic | Continual | **Warn → Block at W1 gate** | Zero multi-owned (**currently 34**) |
| **FF-29** | No dependency cycle outside the six approved co-design pairs | `AR-006` §4.1 | Holistic | Triggered (gate) | **Block** | Zero unapproved cycles (**currently 11 to break**) |

### 4.2 Odoo module conformance

| ID | Check | Source | Scope | Timing | Enforce | Threshold |
|---|---|---|:--:|:--:|:--:|---|
| **FF-02** | Naming — `cd_*` module, `fix.*` model, `fix_*` table, snake_case columns | AS-04, `AR-007` N-01…N-03 | Atomic | Continual | **Block** | 100% conformance |
| **FF-03** | **No modification to `odoo/` or an OCA subtree; no unregistered fork** | AS-05, `AR-007` OV-05, OCA-04 | Holistic | Continual | **Block** | Zero unregistered forks. **Diff against the pinned tree must be empty** |
| **FF-06** | No `state` assignment outside `_do_transition` | AS-06, `AR-007` SM-05 | Atomic | Continual | **Block** | Zero direct assignments |
| **FF-16** | `x_cd_id` present and **issued by `BE-005`** | `AR-007` §3.2 | Atomic | Continual | **Block** | 100%. ⚠ **Unsatisfiable until `BE-005` exists** |
| **FF-18** | Stored computed fields declare complete `depends` | `AR-007` N-06 | Atomic | Continual | **Block** | Zero incomplete |
| **FF-19** | Every model has `_description` | `AR-007` N-09 | Atomic | Continual | **Block** | 100% |
| **FF-20** | Every business model inherits `mail.thread` + `mail.activity.mixin` | AS-02, DM-04 | Atomic | Continual | **Block** | 100% |
| **FF-21** | Every transactional model carries `company_id` + `operating_unit_id` | AS-03, DM-03 | Atomic | Continual | **Block** | 100% |
| **FF-22** | No `Float` in a money path; `Monetary` with explicit `currency_id` | AS-10, DI-01 | Atomic | Continual | **Block** | Zero float money fields |
| **FF-23** | Datetimes stored UTC | AS-11, DM-08 | Atomic | Continual | **Block** | 100% |
| **FF-24** | Translation completeness — `bn_BD.po` at 100% | AS-12, DoD-08 | Atomic | Continual | **Block** | 100% of user-facing strings |
| **FF-25** | `ondelete` declared explicitly on every many2one | `AR-007` N-16 | Atomic | Continual | **Block** | 100% |
| **FF-26** | Every security group maps to a registered role `R01`…`R46` | `AR-007` §6 | Atomic | Continual | **Block** | 100%. ⚠ **Unsatisfiable until the role register is completed** |

### 4.3 Events and messaging

| ID | Check | Source | Scope | Timing | Enforce | Threshold |
|---|---|---|:--:|:--:|:--:|---|
| **FF-04** | **Outbox coverage** — every declared state transition emits its event through `emit_event()`, and the emitted set matches the SDD §9 table | AS-08, `AR-009` §5.5, `TR-12` | Holistic | Continual | **Block** | 100% of transitions |
| **FF-13** | Every emitted event is registered in `IN-003`; every consumed event has a registered producer | `AR-009` G-03, G-04 | Holistic | Continual | **Block** | Zero unregistered (**currently 953 declared-unregistered**) |
| **FF-28** | No module uses a bus client directly; all consumption via the shared library | `AR-009` §6.2 | Atomic | Continual | **Block** | Zero direct client uses |
| **FF-31** | Event schema backward compatibility within a `schema_version` | `AR-009` §8.1 | Holistic | Continual | **Block** | Additive changes only |

### 4.4 Security, privacy and residency

| ID | Check | Source | Scope | Timing | Enforce | Threshold |
|---|---|---|:--:|:--:|:--:|---|
| **FF-09** | **No residency-classified value outside CD-233** — not in a column, cache, log, index, report, prompt or event payload | NFR-086a, `AR-001` LB-08, `AR-009` P-03, `AR-011` LLM-03 | Holistic | Continual | **Block** | **Zero. No exemption is available for this check** |
| **FF-12** | Portal contract test PS-11 — an invalid payload posted directly to the API is rejected | `AR-002` EP-01, PS-11 | Atomic | Continual | **Block** | 100% of state-changing endpoints |
| **FF-30** | SAST, dependency, container, IaC and licence scans | `SC-005`, `AR-007` §3.3 | Atomic | Continual | **Block on high/critical** | Zero open high or critical (DoD-15) |
| **FF-32** | No personal data in logs or traces | OPS-04, `TR-16` | Holistic | Continual | **Block** | Zero matches against the classified-field pattern set |

### 4.5 Performance and quality attributes

| ID | Check | Source | Scope | Timing | Enforce | Threshold |
|---|---|---|:--:|:--:|:--:|---|
| **FF-11** | Bundle budget — critical customer paths | NFR-081, PS-07, `AR-001` QAS-10 | Atomic | Continual | **Block** | **< 400 KB first load** |
| **FF-33** | NFR performance targets at 1.5× expected peak | DoD-14, `AR-001` §10 | Holistic | Triggered (gate) | **Block** | Every applicable NFR met |
| **FF-34** | Offline harness — all six scenario classes | `AR-010` §10 | Holistic | Triggered (release) | **Block** | Zero data loss, zero double-application |
| **FF-35** | Accessibility — axe-core on portal builds | NFR-073, `UX-005` | Atomic | Continual | **Block on violations** | Zero WCAG 2.2 AA violations |

### 4.6 Data and metadata *(added at v1.1 — Category 03)*

| ID | Check | Source | Scope | Timing | Enforce | Threshold |
|---|---|---|:--:|:--:|:--:|---|
| **FF-36** | **Citation ↔ data dictionary.** Every `<file>.<field>` reference in any `DT-*`, `MD-*`, `LG-*`, `RP-*`, `TS-*` or module file resolves to a registered `DA-002` element | `DA-002` `RC-2`; audit `F3` / `LG-01` | Holistic | Continual | **Block** — on the **content** repository | Zero unresolvable field citations. **This is the check that catches the `F3` class** |
| **FF-37** | **Code-list drift.** Every enumerated column's permitted values match its `CL-nnn` members; every model with a `state` has a registered state set; the declared transition map matches `_TRANSITIONS` in code | `DA-009` DR-01…DR-04; `MD-027` `STA-01` | Holistic | Continual | **Block** | Zero drift. **348 models must have a registered state set** |

---

## 5. Enforcement Levels

### 5.1 The three levels

| Level | Behaviour | Use when |
|---|---|---|
| **Block** | The build fails. The change cannot merge | The claim is architectural and a violation is a defect |
| **Warning** | Reported in the build and on the architecture dashboard; does not fail | The check is new, or the existing violation count is non-zero and being burnt down |
| **Reporting** | Trend only | The metric informs judgement rather than defining pass/fail (coupling, module size) |

### 5.2 The promotion rule

> **A new fitness function starts as a Warning, with a burn-down target and a date, and is promoted to
> Blocking on that date.**

This exists because three checks in §4 currently have non-zero violation counts against a
specification set that predates them:

| Check | Current violations | Burn-down |
|---|---:|---|
| `FF-14` reciprocity | **55** | `AR-006` §7.3 R-01/R-02 → Block at the **W1 gate** |
| `FF-27` entity uniqueness | **34** | `AR-008` §7.5 rulings → Block at the **W1 gate** |
| `FF-13` event registration | **953** | `AR-009` §10.6 RM-01…RM-05 → Block at the **W1 gate** |
| `FF-29` cycles | **11 to break** | `AR-006` §4.1 → Block at the **W2 gate** |

**Turning these on as Blocking today would fail every build**, which is why a promotion rule exists
rather than a pretence that the estate is already clean.

### 5.3 Two checks that are unsatisfiable, and must not be quietly relaxed

| Check | Why | Position |
|---|---|---|
| **`FF-16`** `x_cd_id` issued | **`BE-005` does not exist.** Two incompatible CD registers exist, 48 identifiers collide | Build the check in W1; enable when `BE-005` issues. **Do not weaken it to "any identifier"** — that defeats its purpose |
| **`FF-26`** registered roles | `05-04` registers R01–R38; **R39–R46 in use and unregistered; R60 duplicates R32; R54/R57 undefined** | Build against **46 roles with R60 eliminated**. Enable when the register completes (Wave 0, `TR-13`). **Do not build against 38** |

---

## 6. Exemptions

**A blocking check with no honest exemption route gets disabled globally.** That is the failure mode
this section prevents.

| # | Rule |
|---|---|
| **EX-01** | An exemption is **per artefact and per check**. Never global, never per check alone |
| **EX-02** | An exemption is declared **in the repository, next to the code**, with the check id, the reason and an expiry date |
| **EX-03** | An exemption **has an expiry**. Maximum one wave. On expiry the build fails |
| **EX-04** | An exemption requires **Design Authority approval**, recorded with a named approver |
| **EX-05** | Every exemption is listed in the wave-gate architecture review (§7) |
| **EX-06** | **`FF-09` (residency) admits no exemption.** A residency violation is a statutory exposure, not a technical trade-off |
| **EX-07** | An exemption count above **10 open at any wave gate** is itself a gate finding — it means either the standard or the codebase is wrong, and the review must say which |

---

## 7. Wave-Gate Architecture Review

Automated checks cannot evaluate judgement. Six manual reviews run at every wave gate, each with a
named assessor and a recorded outcome.

| # | Review | Assessor | Evidence |
|---|---|---|---|
| **WG-01** | **Quality-attribute scenario re-evaluation.** Do `AR-001` §10's eleven scenarios still hold at this wave's volume and scope? | Chief Architect | Measured response per scenario |
| **WG-02** | **Fork register review.** Every fork's divergence measured in lines changed against upstream; exit condition still valid | Solution Architect | `AR-007` §5.4 register |
| **WG-03** | **Exemption review.** Every open exemption re-justified or closed | Design Authority | §6 register |
| **WG-04** | **Dependency graph regeneration.** `AR-006` §2.1 extraction re-run; new cycles and wave violations dispositioned | Solution Architect | Regenerated graph + diff |
| **WG-05** | **Event catalogue diff.** `AR-009` G-06 — an undeclared change is a gate failure | Chief Architect | Generated catalogue diff |
| **WG-06** | **ADR revisit triggers.** Has any `Revisit if` condition become true? | Chief Architect | `AR-004` §5 triggers |

> **WG-06 is the one most likely to be skipped and the one that keeps `AR-004` alive.** An ADR
> library nobody revisits is a history, not a control. Two triggers are already live and dated:
> ADR-001's OCA v19 migration exposure, and ADR-027's Odoo 20 release window (September–October 2026).

---

## 8. Drift Metrics

Reported, not enforced. These inform the wave-gate review; a threshold breach opens a conversation,
not a build failure.

| Metric | Definition | Watch |
|---|---|---|
| **Cross-module coupling** | Distinct modules a module calls or consumes events from | A module rising above 12 (current max out-degree: 11) |
| **In-degree concentration** | Modules with in-degree > 30 | Currently M29 (53), M33 (41), M28 (37). **Rising further concentrates risk** |
| **Fork divergence** | Lines changed vs upstream, per forked OCA module | Any fork exceeding a stated line budget |
| **Exemption count** | Open exemptions | > 10 at a gate is a finding (EX-07) |
| **Event surface growth** | Registered events per wave | Currently 988 declared. Growth without consumers is a smell |
| **Outbox coverage** | Transitions emitting / total transitions | Must be 100%; a falling trend precedes an `FF-04` failure |
| **Test coverage** | Custom code / financial paths | ≥ 80% / 100% |
| **Bengali translation completeness** | Translated / total strings | Must be 100% at acceptance |
| **Module size** | Models per module; lines per model | A module exceeding its peers by 3× warrants a boundary review (`AR-005`) |

**Published as an architecture health report at every wave gate**, alongside the six manual reviews.

---

## 9. Governance

| # | Rule |
|---|---|
| **GV-01** | A new fitness function requires **Design Authority approval** — it is an architectural commitment binding every team |
| **GV-02** | A fitness function names the **claim it enforces** and the document that claim comes from. A check with no source claim is a style rule and belongs in `BE-002` |
| **GV-03** | **A blocking check that fires frequently and is usually exempted is a defective check.** Fix the check or retire it. Do not normalise the exemption |
| **GV-04** | Retiring a fitness function requires the **same approval as adding one**, and a statement of what now prevents the drift it prevented |
| **GV-05** | The register is reviewed at every wave gate for coverage: **has a new architectural claim been made with no check?** |
| **GV-06** | A check may be **temporarily downgraded** to Warning by the Chief Architect for a maximum of one wave, recorded, and reported at the gate |

> **GV-03 is the rule that keeps the register credible.** A check that fires on legitimate code
> teaches developers that the architecture standards are noise, and that lesson generalises to the
> checks that matter.

---

## 10. Implementation Sequence

Not all 37 checks are built at once. The order follows what is most expensive to retrofit.

| Wave | Checks | Rationale |
|:--:|---|---|
| **W1** | `FF-02`, `FF-03`, `FF-04`, `FF-06`, `FF-09`, `FF-19`, `FF-20`, `FF-21`, `FF-22`, `FF-23`, `FF-25`, `FF-30`, `FF-32` | **A gate added later does not retro-check what shipped before it.** `FF-03` (fork) and `FF-09` (residency) are the two that must exist before the first line of code |
| W1 (Warning) | `FF-13`, `FF-14`, `FF-27` | Non-zero violation counts; burn down to Blocking at the W1 gate |
| W1 (built, disabled) | `FF-16`, `FF-26` | Unsatisfiable until `BE-005` and the role register exist (§5.3) |
| W2 | `FF-01`, `FF-05`, `FF-07`, `FF-10`, `FF-11`, `FF-12`, `FF-17`, `FF-18`, `FF-24`, `FF-28`, `FF-29`, `FF-31`, `FF-35` | Require multiple modules or a portal to exist |
| W2 | `FF-34` offline harness | With APP-01 |
| W3 | `FF-33` performance at 1.5× peak | Requires representative volume |
| **W1** | **`FF-37`** code-list drift | 348 state sets must be registered before the first module ships a `state` |
| **W2** | **`FF-36`** citation ↔ dictionary | Runs on the content repository; needs `DA-002` populated for W0–W1 modules |
| Ongoing | `FF-08`, `FF-15` | Triggered at gates |

> **The `FF-09` and `FF-03` priority is not negotiable.** Both are checks whose violations are
> effectively unrecoverable: a residency leak is a notifiable event, and a fork discovered at the
> Odoo 20 upgrade is a rewrite.

---

## 11. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| Q-01 | Who builds the checks — `PE-004` platform team, or a dedicated architecture-tooling owner? | CTO | W1 | §10 sequence |
| Q-02 | Are the four W1-gate burn-down targets (`FF-13` 953, `FF-14` 55, `FF-27` 34, `FF-29` 11) accepted as Wave 1 scope? | Design Authority | **W0** | W1 gate criteria |
| Q-03 | What is the fork line-budget for `FF-03` divergence reporting? | Solution Architect | W2 | WG-02 |
| Q-04 | Does the Design Authority exist in time to approve exemptions in Wave 1? (`PGD-A1-09`) | CTO | **W1** | EX-04; the whole exemption route |
| Q-05 | Should drift metrics have thresholds that trigger a mandatory review, or remain purely informational? | Chief Architect | W3 | §8 |

---

## 12. Decisions Recorded

| # | Decision | Options | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| D-A12-01 | Enforcement default | Warning; **Blocking** | **Blocking**, with the §5.2 promotion rule | A warning that never becomes blocking is a report | New checks start as Warning with a dated promotion |
| D-A12-02 | Exemptions | None; global disable; **per artefact with expiry** | **Per artefact with expiry** | A blocking check with no honest route gets disabled globally | EX-01…EX-07; `FF-09` exempt from exemption |
| D-A12-03 | Manual reviews | Automate everything; **six manual gate reviews** | **Six manual** | Judgement cannot be automated, and pretending otherwise leaves it undone | Named assessors at every gate |
| D-A12-04 | Unsatisfiable checks | Relax to make them pass; **build and disable** | **Build and disable (§5.3)** | Relaxing `FF-26` to 38 roles would let eight unregistered roles into production unchecked | Two checks built and dormant |
| D-A12-05 | Drift metrics | Enforce; **report** | **Report** | A coupling threshold enforced mechanically produces perverse decomposition | Feeds the gate review |

---

## 13. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | Every AS-01…AS-15 standard has at least one fitness function | §4 — all 15 covered |
| AC-02 | Every architectural claim in `AR-001`…`AR-011` has a check or a stated reason it cannot have one | §4 — 37 functions |
| AC-03 | Every check states scope, timing, enforcement, threshold and source claim | §4 tables |
| AC-04 | Checks with non-zero current violations have a burn-down target and a promotion date | §5.2 — four checks |
| AC-05 | Unsatisfiable checks are stated as such, not silently relaxed | §5.3 — `FF-16`, `FF-26` |
| AC-06 | An exemption procedure exists with expiry and approval | §6 |
| AC-07 | Manual reviews have named assessors and recorded evidence | §7 — six reviews |
| AC-08 | The implementation sequence prioritises checks that cannot be retrofitted | §10 |

**Definition of done.** Complete when every criterion is met, `PE-004` has implemented the Wave 1
set, and `PGD-000`'s `AR-012` row is updated with a fresh enumeration timestamp.

---

## 14. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `AR-001` §6.5, §8.1, §10, §14.1 | The claims enforced |
| Upstream | `AR-005`…`AR-011` | Source claims for 24 of the 37 checks |
| Upstream | `AR-007` §11 | 16 checks defined there, registered here |
| Downstream | **`PE-004`** | Implements the checks in the pipeline |
| Downstream | `QA-001`, `QA-005` | Test strategy consumes `FF-33`, `FF-34` |
| Downstream | `GV-009` | Wave-gate criteria include the §7 reviews |
| Downstream | `BE-002`, `BE-003` | Style and review standards reference, do not duplicate |
| Lateral | `../../1000fix_ERP_Module/02_Architecture/02-01` §10, `.../05-06` §12 | AS-01…AS-15 and their verification column |

---

## 15. References

**Within this repository**
`../PGD-000_*.md` · `./_CATEGORY_OVERVIEW.md` · `./AR-001` through `./AR-011` ·
`../_AUDIT/PGD-AUDIT-003_*.md`

**Workspace**
`../../1000fix_ERP_Module/02_Architecture/02-01` §10 · `.../05_Cross_Cutting_Specifications/05-06` §12 ·
`../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §18.2, §23

**External sources**

| Source | Verified |
|---|---|
| Ford, Parsons & Kua, *Building Evolutionary Architectures* — fitness functions | 2026-08-18 |
| SEI ATAM — Architecture Tradeoff Analysis Method | 2026-08-18 |
| ISO/IEC/IEEE 42010:2022 §5.6 correspondence rules | 2026-08-18 |

---

## 16. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.1 | 2026-08-18 | Enterprise Architecture | **`FF-36` and `FF-37` added** for Category 03 — citation-to-dictionary reconciliation (closes the `F3` class) and code-list drift. Register grows 35 → 37. Raised as `PGD-A5-17` in `PGD-AUDIT-005`: Category 03 cited both before they existed |
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. 35 fitness functions derived from `AR-001`…`AR-011`. States current violation counts (`FF-13` 953, `FF-14` 55, `FF-27` 34, `FF-29` 11) with burn-down targets, and records `FF-16`/`FF-26` as unsatisfiable rather than relaxing them | *Pending — Design Authority not constituted* |

---

*`AR-012` · Category 02 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
