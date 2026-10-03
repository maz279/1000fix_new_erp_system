---
id: BE-006
title: Component Build Specification Standard
category: 07 — Build Engineering & Development Standards
code: BE
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Engineering Lead
approver: Chief Architect
standards_basis: >
  ISO/IEC/IEEE 42010:2022 §5 (documented architecture) · OpenAPI 3.1 · CycloneDX 1.7 ·
  Odoo 19.0 manifest conventions · OCA module documentation standards · Keep a Changelog 1.1
traces_to: >
  PGD-000 BE-006 · Technology Stack Specification §8.3 L5-01…L5-10 · 02-05 §9 (documentation as DoD) ·
  02-02 §8 DoD-01…DoD-17 · AR-007 §12 · AR-012 FF-16 · BE-005 (331 components)
depends_on: BE-004 (placement) · BE-005 (identifiers) · BE-002 (code inside the component)
verified_on: 2026-08-18
enumeration_timestamp: 2026-08-18 13:06 (+06)
priority: P1
needed_by: W1
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# BE-006 — Component Build Specification Standard

### Category 07 · Code `BE` · OpenAPI 3.1 · CycloneDX 1.7 · OCA documentation standards

---

## 1. Purpose

`02-05` §9 makes documentation a definition-of-done item:

> *"Every module ships with a README, a runbook and its OpenAPI specification; documentation is a
> definition-of-done item."*

It does not say what any of those three contain, which means "documentation complete" is asserted
rather than assessed. TSS §8.3 goes further with `L5-01`…`L5-10`, and `02-02` §8 further still with
`DoD-01`…`DoD-17`, but neither defines the **artefact set** — the actual files that must exist beside
the code, in a form a wave-gate assessor can check without reading the code.

This document is that definition. It fixes the artefact set per deliverable class, gives each
artefact a template, and introduces one machine-readable file — `component.yaml` — that turns the
definition of done from a checklist somebody ticks into a record a build validates.

> **Why one more file rather than more prose.** `GV-009` §4 needed *"eight evidence classes and named
> assessors"* because the programme could not previously say what evidence a completed thing
> produces. `component.yaml` is that evidence for a built component: it names the CD identifier, the
> requirements satisfied, the events emitted, the roles secured and the artefacts present, and CI
> checks every claim in it against reality.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | The **five deliverable classes** and the artefact set each must ship |
| 2 | `component.yaml` — schema, semantics and validation |
| 3 | Templates for README, runbook, CHANGELOG and the manifest |
| 4 | API and event contract obligations |
| 5 | Test artefact obligations |
| 6 | Localisation artefact obligations |
| 7 | The **component definition of done**, consolidating `DoD-01`…`DoD-17`, `L5-01`…`L5-10` and `AR-007` §12 into one assessable list |
| 8 | Scaffolding — the generator that makes conformance the default |
| 9 | The wave-gate evidence this standard produces |

**Explicitly out of scope**

| Topic | Owned by | Why |
|---|---|---|
| Odoo module internal anatomy | `AR-007` §3 | This document says *which files must exist*; `AR-007` says how the code inside them is organised |
| Code style | `BE-002` | |
| Directory placement | `BE-004` | |
| Identifier allocation | `BE-005` | Consumed |
| Test **strategy** and coverage policy | `QA-001`, `AR-007` §9 | This document requires the artefacts; the strategy sets the targets |
| Runbook operational content — escalation trees, on-call | `SV-002`, `SV-004` | This document fixes the runbook's **structure**; operations owns its content |
| Dependency and SBOM policy | `BE-007` | This document requires the SBOM artefact; `BE-007` governs its content |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| **Every developer** | What must exist beside the code before a component is done |
| Wave-gate assessors (`GV-009`) | The evidence a completed component produces, checkable without reading code |
| Implementation vendor | The delivery standard for each of 331 components |
| Service Operations | The runbook they inherit at handover, in a shape they can use at 02:00 |
| QA | The test artefacts that must exist for coverage to mean anything |
| Platform Engineering | The `component.yaml` schema CI validates against |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Conformance | Departure and rationale |
|---|---|---|
| **OpenAPI 3.1** | Every API-exposing component ships a specification, validated in CI | Full. Required by `L5-01`, `DoD-06` |
| **CycloneDX 1.7** | Every component contributes to the build-time SBOM | Delegated to `BE-007` §5; this document requires the artefact to exist |
| **Keep a Changelog 1.1** | `CHANGELOG.md` per component, generated from Conventional Commits | **Departure:** generated, not hand-written, so it cannot drift from history (`GW-35`) |
| **Odoo 19.0 manifest conventions** | Required keys, version format, licence | Deferred to `AR-007` §3.2 and `BE-002` §4.6 |
| **OCA module documentation standards** | `README` per module, with purpose, configuration, usage and known issues | **Departure:** Markdown, not `README.rst`. Rationale: the whole estate is Markdown, and a module contributed upstream is converted at the boundary by `GW-14`'s export script |
| **ISO/IEC/IEEE 42010:2022** §5 | Architecture-relevant decisions are recorded, not implicit | ADRs live in `AR-004`; a component records only the ones local to it |

### 2.2 Source material relied on

| Source | Contribution |
|---|---|
| TSS §8.3 | `L5-01`…`L5-10` — the ten custom-development standards this document makes concrete |
| `02-02` §8 | `DoD-01`…`DoD-17` — the programme definition of done this document consolidates |
| `02-05` §9 | *"Documentation is a definition-of-done item"* — the requirement with no artefact set |
| `AR-007` §3.1, §12 | Module anatomy, and the module definition of done this document extends beyond Odoo |
| `AR-012` `FF-16` | Requires `x_cd_id` **issued**; `component.yaml` is where the identifier is machine-readable |
| `BE-005` §9.1 | The type distribution that determines how many classes are needed |
| `GV-009` | The eight evidence classes a wave gate assesses |
| `project_content/00_Content_Governance…/CG-008` | The content estate's own definition of done — the precedent that a DoD is checkable |

### 2.3 The five classes, derived from the register

`BE-005` §9.1 counts eight declared types across 331 items. Eight artefact sets would be
unmaintainable; the types collapse to five classes with genuinely different obligations.

| Class | `BE-005` types included | Items | Distinguishing obligation |
|---|---|---:|---|
| **C1 — Odoo module** | Odoo module | 180 | Manifest, security artefacts, i18n, migrations |
| **C2 — Odoo module + service** | Odoo module + standalone service | 90 | Both C1 and C3, one identifier, two directories |
| **C3 — Standalone service** | Standalone service | 33 | OpenAPI, health and metrics endpoints, declared fallback |
| **C4 — Mobile application** | Flutter · React Native · mobile application | 8 | Offline behaviour, store metadata, device-permission register |
| **C5 — Web application / front-end** | Next.js application · front-end component | 20 | Bundle budget, accessibility evidence, portal contract test |
| | **Total** | **331** | |

**Verification** *(`PG-M10`)*: 180 + 90 + 33 + 8 + 20 = **331** ✓ against `BE-005` §6's count of 331.

---

## 3. `component.yaml`

One file per component directory. It is the component's self-description, and every claim in it is
validated against reality by CI.

```yaml
# addons/domain/a_service_delivery/cd_service_order/component.yaml
schema: 1
id: CD-M01-01                     # BE-005 issued identifier — FF-16
class: C1
name: cd_service_order
title: Service Order
owner_unit: M01
owner_role: Service Operations Director      # business owner, from 05-04
squad: squad-service-delivery                # matches CODEOWNERS
wave: W1
effort_pw: 16
legacy_ids: [CD-001]

satisfies:                        # RQ-004 traceability terminates here
  requirements: [FR-SRM-001, FR-SRM-002, "…"]
  business_rules: [BRU-SRM-01, BRU-SRM-04]
  nfrs: [NFR-012, NFR-090-M]

emits:                            # must equal the AR-003 §9 table — FF-04, FF-13
  - service_order.created
  - service_order.assigned
  - service_order.completed
consumes:
  - work_order.completed
  - entitlement.verified

roles:                            # every applicable role has a negative test — DoD-07
  [R03, R07, R12, R21]

data:
  residency_classified: false     # true requires a residency-service dependency — FF-09
  personal_data: true
  retention_policy: RET-004

interfaces:
  openapi: contracts/openapi/service-order-v1.yaml
  portal_contract: contracts/portal/service-order.json

dependencies:
  odoo: [base, mail, repair, project]
  oca: [field-service, helpdesk]
  fix_platform: [cd_event_outbox, cd_rbac_ext, cd_party_master]
  fix_domain: []                  # DL-02 — empty unless AR-006 §6.1 permits

artefacts:                        # presence validated; §4 defines the set per class
  readme: README.md
  runbook: runbook.md
  changelog: CHANGELOG.md
  adr: []                         # local ADRs; programme decisions live in AR-004

quality:
  coverage_target: 80             # 100 where financial: true
  financial: false
  offline_capable: false
  bundle_budget_kb: null          # C5 only
```

| # | Rule |
|---|---|
| **`CBS-01`** | Every component directory contains exactly one `component.yaml`, and no directory under `addons/`, `services/` or `apps/` exists without one (`REPO-CHK-01`) |
| **`CBS-02`** | Documentation lives **beside the code it documents**, inside the component directory. Documentation kept elsewhere goes stale and is not read at the moment it is needed |
| **`CBS-03`** | Every field is **validated**, not merely present: `id` against `cd-register.yaml`; `emits` against `contracts/events/` and the SDD table; `roles` against the role register; `requirements` against `RQ-004`; `dependencies` against the manifest |
| **`CBS-04`** | `id` is the single machine-readable binding between code, register, backlog, tests and CI. `FF-16` reads it |
| **`CBS-05`** | `component.yaml` is **hand-authored and machine-validated** — not generated. It is a set of claims the author makes, which is what makes CI's contradiction of them meaningful |
| **`CBS-06`** | A field that cannot yet be filled is set to `null` with a `# TODO(<CD-ID>, #issue)` comment (`XS-11`). It is never omitted, because an omitted field is indistinguishable from a forgotten one |

> **`CBS-03` is the whole value of the file.** A component that claims to emit
> `service_order.assigned` and does not is caught by `FF-04`; a component that emits it and does not
> claim it is caught by the same check from the other side. Before this file existed, the two sides
> were `AR-003` §9's prose table and the code, and nothing compared them — which is how `FF-13`
> arrived at **953 declared-unregistered events**.

---

## 4. The Artefact Set

### 4.1 By class

| Artefact | C1 Odoo | C2 Both | C3 Service | C4 Mobile | C5 Web |
|---|:--:|:--:|:--:|:--:|:--:|
| `component.yaml` | ● | ● | ● | ● | ● |
| `README.md` (§4.2) | ● | ● | ● | ● | ● |
| `runbook.md` (§4.3) | ● | ● | ● | ● | ● |
| `CHANGELOG.md` — generated | ● | ● | ● | ● | ● |
| `__manifest__.py` | ● | ● | — | — | — |
| `security/ir.model.access.csv` + rules | ● | ● | — | — | — |
| `i18n/<module>.pot` + `bn_BD.po` | ● | ● | — | — | — |
| `migrations/19.0.x.y.z/` | ● | ● | — | — | — |
| OpenAPI 3.1 specification | where API | ● | ● | — | — |
| Event schemas in `contracts/events/` | where emitting | ● | ● | — | — |
| `Dockerfile` + health and metrics endpoints | — | ● | ● | — | — |
| Declared fallback behaviour (`L5-09`) | — | ● | ● | ● | — |
| ARB translation files, `bn_BD` complete | — | — | — | ● | — |
| Store metadata and device-permission register | — | — | — | ● | — |
| Offline behaviour specification | — | — | — | ● | — |
| Bundle-budget report (`FF-11`) | — | — | — | — | ● |
| Accessibility report (axe-core, `FF-35`) | — | — | — | ● | ● |
| Portal contract test (`PS-11`, `FF-12`) | — | — | where portal-facing | — | ● |
| `tests/` per `AR-007` §9 | ● | ● | ● | ● | ● |

### 4.2 `README.md`

For a developer who has never seen this component. Fixed headings, so it is scannable across 331
components and so its absence is detectable.

```markdown
# <CD-ID> — <Title>

**Unit** M01 · **Class** C1 · **Wave** W1 · **Squad** squad-service-delivery

## What it does
<!-- Two paragraphs. Business capability, not implementation. -->

## What it does NOT do
<!-- The boundary, naming the owning component. AR-005's overlap control, made local. -->

## Key models and concepts
<!-- Aggregate roots, state machine in one line, the vocabulary a newcomer needs. -->

## Depends on
<!-- Per component.yaml, with one line each on why. -->

## Configuration
<!-- Every system parameter, feature flag and master-data prerequisite. -->

## Events
<!-- Emitted and consumed, with the trigger for each. Must match component.yaml. -->

## Business rules enforced here
<!-- BRU-* identifiers, classification, and where each is implemented. -->

## Known limitations and deferred work
<!-- Honest. Every entry carries a BE-009 DBT- identifier or an issue. -->
```

| # | Rule |
|---|---|
| **`CBS-07`** | Headings are fixed and none is omitted. A section that does not apply says so in one line (`_MODULE_TEMPLATE`'s convention, carried into code) |
| **`CBS-08`** | *"What it does NOT do"* is mandatory and names the owning component for each excluded capability. `AR-005`'s boundary control fails at the code level without it |

### 4.3 `runbook.md`

Written for a person who did not build the component, at 02:00, under pressure. That reader
constraint dictates the structure.

```markdown
# <CD-ID> — Operational Runbook

## Health
<!-- How to tell in 30 seconds whether this is working. Endpoint, dashboard, query. -->

## Dependencies and blast radius
<!-- What breaks if this is down. What this needs to be up. -->

## Common failures
| Symptom | Likely cause | Diagnosis | Remedy | Escalate to |

## Fallback behaviour (L5-09)
<!-- What degrades and what still works. No service failure blocks a P0 path (NFR-050). -->

## Restart, replay and recovery
<!-- Safe restart. Outbox replay. Idempotency guarantees. -->

## Data
<!-- Personal or residency-classified data touched, and the handling constraint. -->

## Rollback (DoD-16)
<!-- The rehearsed procedure. Migrations are forward-only (MG-01). -->

## Alerts owned
<!-- Each alert, its threshold, and what the on-call engineer should do. -->
```

| # | Rule |
|---|---|
| **`CBS-09`** | The runbook is written **before** the component enters staging, not before go-live. A runbook written at go-live is written by someone recalling the failure modes rather than someone who has just met them |
| **`CBS-10`** | *"Common failures"* has at least one row before acceptance. A component with no known failure modes has not been tested hard enough |
| **`CBS-11`** | The **rollback procedure is rehearsed**, and the rehearsal is dated in the runbook (`DoD-16`). An unrehearsed rollback is a plan, not a control |

### 4.4 Contracts

| # | Rule |
|---|---|
| **`CBS-12`** | The OpenAPI specification lives in `contracts/openapi/` (`REPO-06`); the component references it. **A specification inside a component directory is a copy and is a defect** |
| **`CBS-13`** | The specification is authored **before** the implementation, and the implementation is validated against it. Generating a specification from code documents what was built, not what was agreed |
| **`CBS-14`** | Every emitted event has a schema in `contracts/events/` registered in `IN-003` (`FF-13`) |
| **`CBS-15`** | A contract change is additive within a `schema_version` (`FF-31`); a breaking change is a new version with both served during a stated overlap |

### 4.5 Tests

Artefact obligations only; `QA-001` and `AR-007` §9 own the strategy.

| Artefact | Required for | Rule |
|---|---|---|
| `tests/test_<aggregate>.py` | C1, C2 | State machine and happy path |
| `tests/test_rules.py` | C1, C2 | **One negative test per H-class rule, through UI and API** (`DoD-04`, `XS-17`) |
| `tests/test_security.py` | C1, C2 | One negative test per role in `component.yaml` (`DoD-07`) |
| `tests/test_events.py` | Any emitting | Every declared transition emits (`DoD-05`, `FF-04`) |
| `tests/test_api.py` | Any API | Contract tests including `PS-11`'s invalid-payload rejection |
| `test/offline/` | C4 | All six offline scenario classes (`FF-34`, `AR-010` §10) |
| `e2e/` | C5 | The critical journeys this component participates in |

### 4.6 Localisation

| # | Rule |
|---|---|
| **`CBS-16`** | `bn_BD` is **100% complete before acceptance**, not before go-live (`AS-12`, `DoD-08`, `FF-24`) |
| **`CBS-17`** | Keys follow `BN-005`; terminology follows `BN-003`; do-not-translate terms follow `BN-004` |
| **`CBS-18`** | A component rendering a printed document ships a **Bengali rendering reference image** and a test comparing against it (`TR-07`, `BE-001` check 10) |

> **`CBS-18` exists because `TR-07` is a compliance failure mode, not a cosmetic one.** A Mushak 6.3
> invoice with broken conjunct shaping is a statutory document that is wrong, and it passes every
> test that does not look at pixels.

---

## 5. The Component Definition of Done

`02-02` §8 gives `DoD-01`…`DoD-17`, TSS §8.3 gives `L5-01`…`L5-10`, `AR-007` §12 gives eleven
structural items. A developer needing to know whether a component is finished currently reads three
lists in three documents. This is the consolidation — the **only** list a wave-gate assessor needs.

| # | Criterion | Source | Class | Evidence |
|:--:|---|---|:--:|---|
| 1 | `component.yaml` present, complete and validated | `CBS-01`…`CBS-03` | all | CI |
| 2 | Issued CD identifier in the manifest / metadata | `FF-16`, `AR-007` §3.2 | all | CI |
| 3 | Directory anatomy conforms | `AR-007` §3.1 | C1, C2 | CI |
| 4 | All 18 naming rules pass | `AR-007` §4 | C1, C2 | `FF-02` |
| 5 | Inheritance decision tree applied; **zero unregistered forks** | `AR-007` §5 | C1, C2 | `FF-03` |
| 6 | Unit coverage ≥ 80%; **100% financial and tax** | `DoD-03`, `L5-02` | all | Coverage gate |
| 7 | Negative test per H-class rule, UI **and** API | `DoD-04`, `L5-04` | C1, C2 | CI |
| 8 | Negative test per applicable role | `DoD-07`, `L5-05` | all | CI |
| 9 | Every transition emits through the outbox; events registered | `DoD-05`, `L5-03` | all | `FF-04`, `FF-13` |
| 10 | OpenAPI 3.1 published and validated; `PS-11` passes | `DoD-06`, `L5-01` | where API | `FF-12` |
| 11 | `bn_BD` at 100% | `DoD-08`, `L5-06`, `AS-12` | all | `FF-24` |
| 12 | KPIs instrumented with allocated identifiers | `DoD-09`, `L5-07` | all | Metric registry |
| 13 | README complete per §4.2 | `L5-01`, `02-05` §9 | all | Assessor |
| 14 | **Runbook written and rollback rehearsed** | `DoD-11`, `DoD-16` | all | `CBS-11`, dated |
| 15 | Migrations forward-only, dry-run on a production-sized clone | `MG-01`…`MG-03`, `SQL-09` | C1, C2 | CI |
| 16 | Performance tested at **1.5× expected peak** | `DoD-14` | all | `FF-33` |
| 17 | Security review, **zero open high or critical** | `DoD-15` | all | `FF-30` |
| 18 | Regulatory citations verified, with a `verified_on` date | `DoD-17` | where regulatory | Assessor |
| 19 | Fallback behaviour declared and tested | `L5-09` | C2, C3, C4 | CI |
| 20 | Bundle budget met | `FF-11`, NFR-081 | C5 | CI |
| 21 | Accessibility: zero WCAG 2.2 AA violations | `FF-35`, NFR-073 | C4, C5 | CI |
| 22 | Offline harness: all six scenario classes, zero loss, zero double-application | `FF-34` | C4 | CI |
| 23 | Source, configuration, migrations, tests and documentation delivered to the Company repository | `L5-10`, RFP §5.10 | all | Continuous |

| # | Rule |
|---|---|
| **`CBS-19`** | **Nineteen of twenty-three are machine-checked.** Four require an assessor: 13, 14, 18 and 23. `GV-009` names the assessor for each |
| **`CBS-20`** | A component is **not** done because it works. It is done when all applicable criteria pass |
| **`CBS-21`** | No criterion is waived at component level. A genuine exception is an `AR-012` §6 exemption with an owner and an expiry, or it is not an exception |

> **Criterion 14 is the one that will be argued about.** A rehearsed rollback costs a day per
> component and it is the difference between an incident and an outage. `GV-009` `Gate 1` already
> carries five blockers; a wave whose components cannot be rolled back adds a sixth that only appears
> after go-live.

---

## 6. Scaffolding

Conformance is achieved by making it the default. A developer creating a component runs one command
and receives a conforming skeleton.

```bash
make new-component ID=CD-M43-04 CLASS=C1 NAME=cd_safety_stock
```

Produces, from `tooling/generators/`:

| Generated | Content |
|---|---|
| Directory at the correct path | Per `BE-004` §4 and the unit's category |
| `component.yaml` | Pre-filled from `cd-register.yaml`; `satisfies` and `emits` left for the author |
| `__manifest__.py` | Required keys, correct version format, `x_cd_id` set, licence per `AR-007` §3.3 |
| Full `AR-007` §3.1 anatomy | Including empty `security/`, `i18n/`, `migrations/`, `tests/` |
| `README.md`, `runbook.md` | Templates with fixed headings and `TODO` markers |
| `tests/` | Failing placeholder tests per §4.5 — **failing, so they must be written** |
| `CODEOWNERS` entry | Regenerated |

| # | Rule |
|---|---|
| **`CBS-22`** | The scaffold **passes every CI gate that can pass on empty code**, and fails only on the tests that must be written. A scaffold that fails linting on day one teaches developers that gates are noise |
| **`CBS-23`** | The scaffold is versioned and updated whenever this standard changes. Existing components are **not** retro-fitted automatically; the change is tracked in `BE-009` as debt with a wave target |
| **`CBS-24`** | Creating a component by copying another is permitted but the result must pass `CBS-03` validation. Copy-and-forget is how a stale `component.yaml` enters the estate |

---

## 7. Wave-Gate Evidence

`GV-009` requires eight evidence classes with named assessors. This standard produces four of them
mechanically, per component, with no additional work at gate time.

| Evidence class | Produced by | Form |
|---|---|---|
| Conformance | §5 criteria 1–12, 15–17, 19–22 | CI report per component, aggregated per wave |
| Documentation | §4.2, §4.3 | README and runbook presence and completeness |
| Traceability | `component.yaml` `satisfies` | Requirement → component → test, machine-generated |
| Operational readiness | Runbook + rehearsed rollback date | Dated evidence in the runbook |

```
# make gate-report WAVE=W1  → GV-009 evidence pack
Wave 1 — 38 components
  DoD criteria passing:            21 / 23 aggregate
  Components fully conforming:     31 / 38
  Blocked on criterion 14:          5    (rollback not rehearsed)
  Blocked on criterion 11:          2    (bn_BD at 94%, 87%)
  Exemptions in force (AR-012 §6):  1    (expires W2 gate)
```

| # | Rule |
|---|---|
| **`CBS-25`** | The gate report is generated, not compiled by hand. `PG-M10`'s roll-up defect class — a correct total concealing wrong components — is prevented by generation, not by care |

---

## 8. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `BE-006-D-01` | Component metadata | (a) Prose in README; (b) **`component.yaml`**; (c) fields in the manifest | **(b)** | Only C1/C2 have a manifest; a machine-readable file serves all five classes and makes `FF-16` and traceability mechanical | One more file per component; `CBS-22`'s scaffold removes the cost |
| `BE-006-D-02` | Class count | (a) One set for all; (b) eight, one per declared type; (c) **five** | **(c)** | One set imposes mobile obligations on Odoo modules; eight is unmaintainable | The C2 hybrid must be stated explicitly (one identifier, two directories) |
| `BE-006-D-03` | `component.yaml` authorship | (a) Generated from code; (b) **hand-authored, machine-validated** | **(b)** | Generation from code cannot contradict code. The value is the contradiction | Authors must maintain it; `CBS-03` catches drift |
| `BE-006-D-04` | README format | (a) OCA `README.rst`; (b) **Markdown with fixed headings** | **(b)** | The whole estate is Markdown; conversion at the upstream boundary is scripted (`GW-14`) | A conversion step exists for OCA contributions |
| `BE-006-D-05` | Contract location | (a) Beside the component; (b) **central `contracts/`** | **(b)** | A contract has two or more parties; storing it with one of them makes that party its owner | Components reference rather than contain, and `CBS-12` must be enforced |
| `BE-006-D-06` | DoD form | (a) Cite three documents; (b) **consolidate into one 23-item list** | **(b)** | Three lists in three documents is how a criterion gets missed by everyone who assumes another list covered it | This list must be re-verified whenever any source changes |

---

## 9. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | Does `component.yaml` `satisfies.requirements` list every requirement, or only the primary ones? At 3,347 requirement rows across 331 components the full form is large | QA Lead / `RQ-004` | W1 | Traceability completeness; `RQA-26` |
| `Q-02` | Who assesses criteria 13, 14, 18 and 23 — the squad, QA or the gate assessor? | `GV-009` owner | W1 | Gate operability |
| `Q-03` | Is the runbook's operational content owned by the squad or by Service Operations at handover? | Service Manager | W2 | `SV-002` boundary |
| `Q-04` | Does criterion 16 (1.5× peak) apply per component or per journey? Per component is cheaper and weaker | QA Lead | W1 | `FF-33` scope |
| `Q-05` | How are the 331 `component.yaml` `emits` lists reconciled with the 953 declared-unregistered events (`FF-13`)? | Integration Lead | **W0** | `FF-13` burn-down |

---

## 10. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | Every one of the 331 components maps to exactly one class | §2.3, verified 180+90+33+8+20 = 331 |
| `AC-02` | Every artefact has a template or a schema, not only a name | §3, §4.2, §4.3 |
| `AC-03` | The definition of done is one list, consolidating all three sources | §5, 23 criteria |
| `AC-04` | The proportion of machine-checked criteria is stated | `CBS-19` — 19 of 23 |
| `AC-05` | Conformance is the default via scaffolding | §6 |
| `AC-06` | Wave-gate evidence is generated, not compiled | §7, `CBS-25` |
| `AC-07` | No criterion in `DoD-01`…`DoD-17` or `L5-01`…`L5-10` is dropped | §5 source column covers both sets |

**Definition of done.** Complete when every criterion is met, the scaffold produces a component that
passes `CBS-22`, a `make gate-report` runs against a real wave, `PGD-000`'s `BE-006` row moves to ✅
with a fresh timestamped enumeration, and the approver has signed.

---

## 11. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `02-02` §8 `DoD-01`…`DoD-17` | Consolidated in §5 |
| Upstream | TSS §8.3 `L5-01`…`L5-10` | Consolidated in §5 |
| Upstream | `AR-007` §3.1, §12 | Anatomy and Odoo DoD extended to five classes |
| Upstream | `BE-005` | `component.yaml` `id`; the 331-item population |
| Upstream | `BE-004` | Where a component directory lives |
| Downstream | `AR-012` `FF-16` | Reads `component.yaml` `id` |
| Downstream | `GV-009` | §7's evidence pack |
| Downstream | `QA-004` | Traceability terminates on `component.yaml` `satisfies` |
| Downstream | `SV-002` | Inherits the runbook at handover |
| Downstream | `BE-009` | Deferred work in README becomes `DBT-` entries |
| Lateral | `IN-003` | Event registration, checked against `emits` |
| Lateral | `../../project_content/11_Localisation_Bengali/BN-003`, `BN-004`, `BN-005` | Localisation obligations |

---

## 12. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` ·
[`_CATEGORY_OVERVIEW.md`](_CATEGORY_OVERVIEW.md) ·
[`BE-002`](BE-002_Coding_Standards_and_Style_Guide.md) ·
[`BE-004`](BE-004_Repository_and_Monorepo_Structure_Standard.md) ·
[`BE-005`](BE-005_Custom_Development_CD_Master_Register.md) ·
[`BE-007`](BE-007_Dependency_Licence_and_SBOM_Management_Standard.md) ·
[`BE-009`](BE-009_Technical_Debt_Register_and_Refactoring_Policy.md) ·
`../00_Programme_Governance_and_Control/GV-009_Wave_Gate_and_Phase_Exit_Criteria_Handbook.md` ·
`../02_Architecture_and_Design/AR-007_Odoo_Module_Architecture_and_Code_Structure_Standard.md` ·
`../02_Architecture_and_Design/AR-012_Architecture_Compliance_and_Fitness_Function_Standard.md`

**Workspace**
`../../1000fix_ERP_Module/02_Architecture/02-02_Module_Catalogue_Master_Register.md` §8 ·
`../../1000fix_ERP_Module/02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md` §9 ·
`../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §8.3 ·
`../../project_content/00_Content_Governance_and_Standards/CG-008_Content_Definition_of_Done_and_QA_Checklist.md`

**External standards** *(all verified 2026-08-18)*
OpenAPI Specification 3.1 · CycloneDX 1.7 (ECMA-424, 2nd edition) ·
Keep a Changelog 1.1 · OCA module documentation conventions ·
ISO/IEC/IEEE 42010:2022 §5 · WCAG 2.2 Level AA

---

## 13. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. Five deliverable classes, `component.yaml` schema, artefact templates, a consolidated 23-item definition of done, scaffolding and generated wave-gate evidence | *(unsigned — no constituted body, `PGD-A1-09`)* |

---

*`BE-006` · Category 07 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
