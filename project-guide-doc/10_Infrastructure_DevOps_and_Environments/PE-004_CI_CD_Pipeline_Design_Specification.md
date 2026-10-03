---
id: PE-004
title: CI/CD Pipeline Design Specification
category: 10 — Infrastructure, DevOps & Environments
code: PE
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-19
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Platform Engineering Lead
approver: CTO with QA Lead and Design Authority (constituted under GV-002)
standards_basis: >
  Continuous Delivery (Humble & Farley) deployment pipeline · SLSA build levels ·
  Semantic Versioning 2.0.0 · Twelve-Factor App §5 build/release/run ·
  ISO/IEC/IEEE 29119-2:2021 · NIST SSDF (SP 800-218)
traces_to: >
  PGD-000 PE-004 · QA-005 §11.1 TAF-52…TAF-59, §11.2 profiles · QA-001 · AR-012 fitness functions ·
  BE-002 §10 · BE-003 · BE-004 §12 · BE-007 §5 · SC-005 G-01…G-10 · IN-002 FF-56 ·
  Technology Stack §18.2, §18.3 · 02-05 §9 · DoD-03…DoD-17 · NFR-008 · OPS-07
depends_on: PE-002 · PE-003 · BE-003 · BE-004 · QA-005 · SC-005
verified_on: 2026-08-19
priority: P0
needed_by: W1
enumeration_timestamp: 2026-08-19 01:15 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# PE-004 — CI/CD Pipeline Design Specification

### Category 10 · Code `PE` · Deployment pipeline (Humble & Farley) · SLSA · NIST SSDF

---

> **`PGD-000`'s `PE-004` row states why this document is not optional:**
>
> *"`02-05` §9 describes CI/CD in two table rows. Seven files mention 'CI/CD' across the estate.
> **The pipeline is the mechanism by which every quality gate in this register is actually
> enforced.**"*
>
> **Counted at 2026-08-19 01:15 (+06), the gates now waiting on it:**
>
> | Source | Gates |
> |---|---:|
> | `AR-012` v1.1 fitness functions | **37** |
> | Category 04 `IN-001`…`IN-008` | **63** (`FF-38`…`FF-100`) |
> | Category 10 `PE-001`…`PE-003` | **27** (`FF-101`…`FF-127`) |
> | `SC-005` secure-development gates | `G-01`…`G-10` |
> | `QA-005` requirements on this document | `TAF-52`…`TAF-59` — **8**, plus 5 execution profiles |
> | Technology Stack §18.2 CI stages | 13 |
> | Definition of Done items with a technology gate | `DoD-03`…`DoD-17` |
> | **Fitness functions defined estate-wide, awaiting a pipeline** | **127** |
>
> **One hundred and twenty-seven automated checks have been specified across nine categories, and
> not one of them can run.** Every category wrote its gates against a pipeline that does not exist.

---

## 1. Purpose

This document specifies the deployment pipeline: its stages and their order, what blocks and what
reports, how an artefact is built once and promoted, how Odoo modules and database migrations are
packaged and executed, the deployment strategy per component, rollback, and the runner and
credential model that makes all of it safe.

It is written to satisfy **requirements that already exist**. `QA-005` §11.1 states eight
requirements *on this document* and says so explicitly: *"`PE-004` does not exist. This section
states the requirement it must satisfy, so that when `PE-004` is written the framework's needs are
already specified rather than negotiated."* This document answers all eight.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | The **pipeline model** — build once, promote the artefact, never rebuild per environment |
| 2 | **Five execution profiles** (`QA-005` §11.2), and what runs in each |
| 3 | The **stage set**, with what blocks and what reports |
| 4 | **The 20-minute pre-merge budget**, and how it is held as the estate grows |
| 5 | Artefact identity, provenance and the registry |
| 6 | **Odoo module packaging** — the case no generic pipeline handles |
| 7 | **Database migration execution**, and the forward-only rule that makes `NFR-008` possible |
| 8 | Deployment strategy per component; **rollback, and what cannot be rolled back** |
| 9 | Promotion across `PE-002`'s twelve environments |
| 10 | Runners, credentials and pipeline security |
| 11 | **Where the 127 fitness functions execute**, and the gate-classification rule |
| 12 | Fitness functions `FF-128`…`FF-136` |

**Explicitly out of scope**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| Which tests exist and what they assert | `QA-001`, `QA-003`, `QA-005` | This document runs them |
| Branching, commit convention, review | `BE-003` | Inherited unchanged |
| Repository layout | `BE-004` | Inherited |
| Dependency pinning, SBOM, licence checks | `BE-007` | This document executes them as stages |
| Infrastructure apply mechanics, plan review, policy | **`PE-003`** §7, §11 | This document **triggers** the apply |
| Environment inventory and data | **`PE-002`** | The promotion targets |
| Image content, base images, orchestration | **`PE-005`** | This document builds and deploys them |
| Secret storage and rotation | **`PE-009`** | §11.2 states only what the pipeline may hold |
| Release scheduling, comms, wave gates | `RL-*`, `GV-009` | This document deploys; `RL-*` decides when |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| Platform engineers | The whole document |
| Every developer | §4's profiles and §5's stages are their feedback loop |
| **QA Lead** | §3.3 answers `QA-005` `TAF-52`…`TAF-59` requirement by requirement |
| Release Manager | §8, §9 |
| Security Lead | §5.4, §11 |
| Architects | §10 — where `AR-012`'s fitness functions execute |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Concept | Conformance | Departure and rationale |
|---|---|---|---|
| **Continuous Delivery** (Humble & Farley) | Deployment pipeline; build once, promote | §3.1, §6 | **Departure on continuous deployment**: production is a **manual gate** (`02-05` §9, `DoD-16`), not automatic. §8.5 |
| **Twelve-Factor App §5** | Strict build / release / run separation | §6.1 — the artefact is immutable; the release is artefact + config | None |
| **SLSA** | Build provenance | §6.4, at the level `BE-007` sets for application artefacts | Aligned, not exceeded |
| **NIST SSDF (SP 800-218)** | Secure software development practices | §5.4's security stages; `SC-005` owns the practice set | Boundary, not departure |
| **Semantic Versioning 2.0.0** | Artefact versioning | §6.2 | None |
| **ISO/IEC/IEEE 29119-2:2021** | Test execution within a defined process | §4's profiles | None |

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| **`QA-005` §11.1, §11.2** | `../08_Quality_Engineering_and_Test/QA-005_*.md` | **`TAF-52`…`TAF-59` — eight explicit requirements on this document** — and five profiles with a **hard 20-minute pre-merge budget** |
| `QA-001` | Ibid. | Thirteen test levels and the ratio |
| **`AR-012`** v1.1 | `../02_Architecture_and_Design/AR-012_*.md` | 37 fitness functions with scope, timing and enforcement |
| `SC-005` | `../05_Security_Privacy_and_Compliance/SC-005_*.md` | `G-01`…`G-10` secure-development gates |
| `BE-002` §10, `BE-003`, `BE-004` §12, `BE-007` §5 | `../07_Build_Engineering_and_Development_Standards/` | Lint and style gates; branching and review; repository gates; dependency and licence gates |
| `IN-002`, `IN-003`, `IN-008` | `../04_Integration_and_API_Engineering/` | `FF-46`…`FF-100`; pact broker and schema registry reachability (`TAF-57`) |
| Technology Stack §18.2, §18.3 | `../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` | The 13-stage CI table; deployment triggers and gates per environment; **forward-only migrations (`OPS-07`)** |
| `02-05` §9 | `../../1000fix_ERP_Module/02_Architecture/02-05_*.md` | CD triggers; the manual gate to staging and production |
| `PE-002`, `PE-003` | `./` | Twelve environments; the apply path and policy gates |

### 2.3 Audit findings this document closes or contributes to

| Finding | Source | Disposition |
|---|---|---|
| `QA-001` §10.5, `QA-005` §11 — *"`PE-002` and `PE-004` as **Wave 0**. Nine of thirteen test levels rest on them and 0 of 7 environments exist"* | Category 08 | **Contributes decisively.** §12 sequences this document's build as Wave 0 |
| `QA-005` `TAF-52`…`TAF-59` | `QA-005` §11.1 | **All eight answered** — §3.3 |
| `AR-012` — 37 fitness functions with no execution point | `AR-012` | §10 places every one |
| `DoD-16` — *"rollback plan documented and rehearsed"* | `02-02` §8 | §8.6 makes rehearsal a pipeline artefact, not a claim |
| `NFR-008` — zero-downtime deployment | `05-06` | §7.3, §8.2 — achievable **only** with forward-only migrations |
| `OPS-07` — forward-only, backward-compatible migrations | Technology Stack §18.3 | §7.2 makes it a gate, not a convention |

---

## 3. The Pipeline Model

### 3.1 Build once, promote the artefact

> **`PE-004-D-01`. An artefact is built exactly once, from one commit, and the same bytes are
> promoted through every environment to production.**

| Rejected | Why |
|---|---|
| Rebuild per environment | The thing tested is not the thing deployed. Every rebuild is an opportunity for a different dependency resolution |
| Build from a branch per environment | Makes `staging` and `prod` different code paths by construction |

**The consequence, which is the point:** an artefact that passed `staging` **is** the artefact that
reaches production. Configuration differs (`PE-009`); bytes do not (`PE-002` `PA-01`).

### 3.2 The shape

```
commit ─► pre-commit (local, <30s)
   │
   ▼ pull request ─────────────────────────────────► PRE-MERGE  (<20 min, BLOCKS)
   │      lint · types · unit · contract · schema · security · architecture
   │
   ▼ merge to develop ─► BUILD ONCE ─► artefact + SBOM + provenance ─► registry
   │                          │
   │                          ▼ auto-deploy: ci, dev
   │
   ▼ nightly (<3h) ─────────────────────────────────► full suite, randomised
   │
   ▼ release candidate ─────────────────────────────► RELEASE (<4h, BLOCKS)
   │      auto: sit → manual: uat, staging, migration-staging, sandbox
   │
   ▼ wave gate (T−4 weeks) ─────────────────────────► GATE (days, BLOCKS)
   │
   ▼ production ─── manual gate ── change approval ── rehearsed rollback (DoD-16)
```

### 3.3 `QA-005`'s eight requirements, answered

`QA-005` §11.1 states them and asks that they be *"already specified rather than negotiated."*

| # | Requirement | How this document satisfies it |
|---|---|---|
| **`TAF-52`** | Ephemeral PostgreSQL 16 per run, seeded from a `QA-004` generator snapshot | §5.2 — `ci` is ephemeral per run (`PE-002` §5.2); the seed is a **versioned snapshot artefact**, restored not generated, so seeding is seconds |
| **`TAF-53`** | Parallel execution across components, results aggregated into one report | §4.3 — the `pre-merge` profile shards by component; §5.7 normalises results |
| **`TAF-54`** | Artefact retention — traces, videos, coverage, results — **for at least the gate window (T−6 to T+2)** | §6.5 — **retention is set to the gate window, not to a default** |
| **`TAF-55`** | A nightly trigger and a pre-merge trigger with different profiles | §4.2 — five profiles |
| **`TAF-56`** | Secret injection for role-account credentials, never in the repository | §11.2 — Vault-issued, short-lived, per-job |
| **`TAF-57`** | Pact broker and schema registry reachable from every build | §5.3 — both are pipeline services with an availability expectation, because **a build cannot verify a pact against an unreachable broker** |
| **`TAF-58`** | Device access for `A4` mobile — a lab or a farm | §5.6 — **and `Q-04` records that this is unfunded** |
| **`TAF-59`** | Results emitted in **one normalised shape** that `QA-011` consumes without per-tool parsing | §5.7 — one schema, every stage emits it |

---

## 4. Execution Profiles

### 4.1 The principle

Not every check runs on every trigger. **The profile is chosen by what the trigger can afford to
wait for**, and the budget is a design constraint.

### 4.2 The five profiles

Adopted from `QA-005` §11.2 unchanged, with the pipeline's own stages added:

| Profile | Trigger | Budget | Blocks | Adds beyond `QA-005` |
|---|---|---|:--:|---|
| **`pre-commit`** | Local hook | **< 30 s** | Locally | Format, lint, **secret scan** (`SC-005` `G-01`) |
| **`pre-merge`** | Pull request | **< 20 min** | **Yes** | + `BE-007` licence and vulnerability gate · `PE-003` plan and policy for `infrastructure/` changes · **blocking** `AR-012` fitness functions |
| **`nightly`** | Schedule | < 3 h | Reports; blocks the next release | + full fitness-function set · drift check (`PE-003` §8) |
| **`release`** | Release candidate | < 4 h | **Yes** | + artefact build, SBOM, provenance · migration dry run against a production-sized clone |
| **`gate`** | T−4 weeks | Days | **Yes** | + `PE-006` performance at 1.5× · DR drill evidence (`PE-007`) · full policy sweep |

### 4.3 Holding the 20-minute budget

`QA-005` `TAF-60`: *"The `pre-merge` budget is 20 minutes and is a design constraint, not an
aspiration. A pull-request suite slower than that gets bypassed, and a bypassed gate is not a gate."*

**The mechanisms that hold it as 67 modules and 12 portals accumulate:**

| # | Mechanism |
|---|---|
| **BG-01** | **Affected-component selection.** A change to one module runs that module's tests and its dependents — computed from `AR-006`'s dependency graph, not guessed |
| **BG-02** | **Sharding.** Independent components run in parallel across runners (`TAF-53`) |
| **BG-03** | **Layer placement.** When the budget is exceeded, the response is to **move tests down a layer** (`TAF-02`) or into `nightly` — **never to reduce what is checked before merge** |
| **BG-04** | **Caching** of dependencies and build layers, keyed on lock files |
| **BG-05** | **The budget is measured and reported per wave gate.** A profile trending toward the limit is a finding before it is a problem |

> **`PE-004-F-01`. `AR-006` measures 447 dependency edges and 18 cycles.** `BG-01`'s
> affected-component selection depends on that graph being acyclic enough to compute a dependent
> set. **With 18 cycles, a change inside a cycle marks every member as affected** — and the largest
> cycles will therefore be the slowest to merge into. This is a further, previously unstated cost of
> `AR-006`'s cycles, and it is felt on **every pull request**, not only at build time.

---

## 5. Stages

### 5.1 The stage set

Extending Technology Stack §18.2's thirteen with what the estate has specified since:

| # | Stage | Checks | Profile | Blocks |
|---|---|---|---|:--:|
| 1 | **Pre-commit** | Format, lint, Odoo checks, **secret scan** | `pre-commit` | Local |
| 2 | **Lint & type** | Python, TypeScript, Dart; naming (`AS-04`); `BE-002` §10 | `pre-merge` | ✔ |
| 3 | **Model registry** | `AS-02` chatter mixins · `AS-03` company/OU fields · **`AS-14` field-level residency and S3 classification** | `pre-merge` | ✔ |
| 4 | **Unit** | ≥ 80% coverage; **100% financial and tax** (`DoD-03`) | `pre-merge` | ✔ |
| 5 | **Integration** | Module-to-module; external against **sandboxes** | `pre-merge` (affected), `nightly` (full) | ✔ |
| 6 | **Contract** | OpenAPI 3.1 validation; **pact verification** (`FF-95`); `PS-11` portal contract test | `pre-merge` | ✔ |
| 7 | **Event** | Producer/consumer schema compatibility; **`AS-08` outbox coverage** (`FF-06`); idempotency | `pre-merge` | ✔ |
| 8 | **Security** | SAST, dependency scan, container scan, **IaC scan**; `SC-005` `G-01`…`G-10` | `pre-merge` | ✔ on high/critical |
| 9 | **Architecture** | `AR-012` blocking fitness functions — `AS-01`, `AS-05`, `AS-09`, `AS-10` and the rest | `pre-merge` | ✔ |
| 10 | **Localisation** | **Translation completeness at 100%** (`DoD-08`) | `pre-merge` | ✔ |
| 11 | **Bundle budget** | Critical customer paths **< 400 KB** | `pre-merge` | ✔ |
| 12 | **Accessibility** | axe-core on portal builds | `pre-merge` | ✔ on violations |
| 13 | **Licence & SBOM** | `BE-007` register check; SBOM generation | `release` | ✔ |
| 14 | **Build verification** | Container build; **migration dry run against a production-sized clone** | `release` | ✔ |
| 15 | **Infrastructure** | `PE-003` plan + §11 policy, when `infrastructure/` changed | `pre-merge` | ✔ |
| 16 | **Performance** | `PE-006` at 1.5× peak (`DoD-14`) | `gate` | ✔ |
| 17 | **DR evidence** | `PE-007` drill record within the wave (`FF-98`) | `gate` | ✔ |

### 5.2 The database per run — `TAF-52`

| # | Rule |
|---|---|
| **DB-01** | Every run gets **its own PostgreSQL 16 instance**, torn down after. Never a shared database |
| **DB-02** | It is seeded by **restoring a versioned snapshot artefact**, not by running a generator. Generation is minutes; restore is seconds, and the snapshot is **identical for every run** |
| **DB-03** | The snapshot is produced by `QA-004`'s generator on a schedule, **versioned, and pinned by the test suite** — so a generator change does not silently change every test's fixture |
| **DB-04** | **The major version matches production** (`PE-002` `PA-03`, `FF-115`) |

> **`DB-02` is the difference between a 20-minute budget and a 40-minute one.** It also removes the
> commonest source of order-dependent test failure, which is a shared database mutated by a previous
> run.

### 5.3 Pipeline services — `TAF-57`

Two services must be reachable from **every** build, and they are therefore infrastructure with an
availability expectation, not developer conveniences:

| Service | Consumed by | If unavailable |
|---|---|---|
| **Pact broker** | Contract stage (`FF-95`, `IN-008` `CT-02`) | **The build fails closed.** A pact that cannot be verified is not a pact that passed |
| **Schema registry** | Event stage (`IN-003` `FF-59`) | As above |

> **`PS-01`. Both fail closed, never open.** A pipeline that treats an unreachable verifier as a
> pass converts the two controls the estate relies on most into decoration.

### 5.4 Security stages

| # | Rule |
|---|---|
| **SE-01** | **Secret scanning runs pre-commit and in CI** — `SC-005` `G-01`. Pre-commit alone is bypassable |
| **SE-02** | SAST, dependency scan, container scan and **IaC scan** all run pre-merge |
| **SE-03** | **High and critical findings block.** `DoD-15` requires zero open high or critical at acceptance |
| **SE-04** | A vulnerability with **no fix available** follows `BE-007`'s VEX position — recorded, justified, time-boxed — never silently suppressed |
| **SE-05** | **The pipeline scans itself**: its own configuration is code and passes the same gates |

### 5.5 Odoo-specific stages

The case a generic pipeline does not handle:

| # | Rule |
|---|---|
| **OD-01** | **Module manifest validation** — dependencies declared, version present, licence stated |
| **OD-02** | **Installability**: every `cd_*` module installs into a clean database in dependency order. **A module that cannot install alone is not a module** |
| **OD-03** | **Upgradability**: every module upgrades from the previously released version, tested on the migration clone |
| **OD-04** | **`AR-007` conformance** — the mandatory `cd_*` anatomy, the inheritance rules, and the **fork register check (`FF-16`)** |
| **OD-05** | **No OCA fork without a `FORKS.yaml` entry** (`AS-05`, `BE-004`) |
| **OD-06** | **The Odoo submodule pin and OCA subtree commits are verified** against `versions.lock` (`BE-007`) |

### 5.6 Mobile — `TAF-58`

| # | Position |
|---|---|
| `A4` mobile tests need **real devices**: Flutter on Android primary, iOS secondary |
| A device lab or a hosted farm is required |
| **`Q-04`: neither is funded, and `TAF-58` records the requirement against nothing** |
| Interim: emulator coverage pre-merge, **real-device coverage at `gate` only** — and the reduction is **declared**, not silent |

### 5.7 Result normalisation — `TAF-59`

| # | Rule |
|---|---|
| **RN-01** | **Every stage emits results in one schema** — suite, case, status, duration, artefact links, and the identifier of the requirement or fitness function it verifies |
| **RN-02** | `QA-011` consumes that schema **without per-tool parsing** |
| **RN-03** | A stage whose tool cannot emit it is **wrapped by an adapter**; the adapter is code, reviewed and tested |
| **RN-04** | The **fitness-function identifier is in the result**, so `AR-012` coverage is measurable from pipeline output rather than by assertion |

> **`RN-04` is what turns 127 specified fitness functions into a measurable estate property.**
> Without it, "the gates are enabled" is a claim nobody can verify.

---

## 6. Artefacts

### 6.1 What an artefact is

| Property | Rule |
|---|---|
| Immutable | Built once, never modified. A change is a new artefact |
| Identified | By **content digest**, not only by tag |
| Traceable | To one commit, one build, one pipeline run |
| Accompanied | By an **SBOM** (`BE-007`) and **provenance** (§6.4) |
| Configuration-free | Configuration is injected at release (`PE-009`), never baked in |

### 6.2 Versioning

| Artefact | Version |
|---|---|
| Container image | `<component>:<semver>-<short-sha>`, plus the immutable digest |
| Odoo module bundle | Module version per `OD-01`, bundled per release |
| IaC module | SemVer (`PE-003` `MD-03`) |
| Database migration | Ordered, immutable, never renumbered |

### 6.3 The registry

| # | Rule |
|---|---|
| **RG-01** | One registry, **private**, with per-environment pull credentials |
| **RG-02** | **Production pulls by digest, never by tag.** A tag can be moved; a digest cannot |
| **RG-03** | **Only the pipeline pushes.** No human has push rights |
| **RG-04** | Images are **scanned on push** and **re-scanned on a schedule** — a clean image at build time is not clean six months later |
| **RG-05** | Retention: production digests **indefinitely**; others per §6.5 |

### 6.4 Provenance

| # | Rule |
|---|---|
| **PR-01** | Every artefact carries **signed provenance** naming the source commit, the builder and the inputs, at the SLSA level `BE-007` sets |
| **PR-02** | **Production verifies provenance before deploying.** An artefact without valid provenance does not deploy |
| **PR-03** | Signing keys live in the secret manager and are **never available to a pull-request build** — §11.3 |

### 6.5 Retention — `TAF-54`

| Artefact class | Retention | Basis |
|---|---|---|
| **Test evidence** — traces, videos, coverage, results | **The gate window, T−6 to T+2 weeks, minimum** | **`TAF-54`** |
| Production images | Indefinite | Rollback and forensics |
| Non-production images | 90 days | |
| SBOM and provenance | **With the artefact**, indefinitely for production | `BE-007` |
| Pipeline logs | **1 year**; longer where they evidence a `DoD` item | Audit |

> **`TAF-54` is a wave-gate requirement, not a storage default.** A gate assessor at T+2 asking for
> the evidence behind a T−6 result must find it. **A 30-day default retention silently voids the
> gate window**, and that failure appears only at the gate.

---

## 7. Database Migrations

### 7.1 Why this is the hardest part of the pipeline

Code rolls back by redeploying the previous artefact. **Data does not.** A migration that drops a
column has destroyed information that no rollback restores, and `AR-006` records **447 dependency
edges** across 67 modules whose schemas evolve independently.

### 7.2 Forward-only, backward-compatible

> **`PE-004-D-02`. Migrations are forward-only and backward-compatible. A release adds a column
> before code uses it, and removes a column only after no code references it — two releases, never
> one.**

This is `OPS-07` (Technology Stack §18.3), and it is what makes `NFR-008` zero-downtime achievable.

| Change | Release *n* | Release *n+1* | Release *n+2* |
|---|---|---|---|
| Add a column | Add nullable; code ignores it | Code writes and reads it | — |
| Remove a column | Code stops referencing it | — | Drop it |
| Rename a column | Add the new; **write both**; read the old | Read the new; backfill | Drop the old |
| Change a type | Add the new column; dual-write | Migrate and read the new | Drop the old |
| Add a constraint | Add as `NOT VALID`; fix data | Validate | — |

| # | Rule |
|---|---|
| **MG-01** | **No migration in a single release both adds and removes.** `FF-131` |
| **MG-02** | Migrations are **idempotent and re-runnable** |
| **MG-03** | Every migration is tested **forward on a production-sized clone** — stage 14 |
| **MG-04** | A migration's **duration is measured** on that clone. **A migration exceeding the deployment window is a release blocker**, not a surprise at 02:00 |
| **MG-05** | **Destructive migrations require a second approver** and an explicit acknowledgement, as `PE-003` `CP-03` requires of destructive infrastructure plans |
| **MG-06** | A **backup verified restorable** precedes every production migration (`PE-007`) |

### 7.3 Execution

| # | Rule |
|---|---|
| **ME-01** | Migrations run **as a distinct pipeline step**, before the new code is routed traffic |
| **ME-02** | They run **once**, from one runner, with an advisory lock. Two nodes migrating concurrently is a corrupted schema |
| **ME-03** | **Odoo module upgrades** are migrations and follow the same rules (`OD-03`) |
| **ME-04** | Failure **halts the deployment** and leaves the previous version serving — which is possible **only** because of `PE-004-D-02` |
| **ME-05** | Migration output is captured as a **release artefact**, retained per §6.5 |

---

## 8. Deployment and Rollback

### 8.1 Strategy per component

| Component | Strategy | Why |
|---|---|---|
| Odoo application nodes | **Rolling**, one node at a time, health-gated | `NFR-008`; ≥ 2 nodes from W1 (`PE-001` §9.2) |
| Next.js portals | **Blue/green** | Static assets and a fast cutover make it cheap |
| Domain services (16) | Rolling | Stateless |
| **Odoo cron nodes** | **Stop, migrate, start** | **Two schedulers running one job is a duplicate job.** §8.3 |
| Event consumers | Rolling, **with schema compatibility already verified** (stage 7) | `IN-003` §6 |
| Kong / Nginx | Rolling across AZs | `PE-001` §6.2 |
| Database | Migration only (§7) | — |
| Infrastructure | `PE-003` §7 | — |

### 8.2 Zero downtime, precisely

`NFR-008` is achievable **only** when all four hold:

| # | Condition |
|---|---|
| 1 | **Forward-only, backward-compatible migrations** (`PE-004-D-02`) |
| 2 | **≥ 2 instances** of every component being rolled (`PE-001` `HA-01`) |
| 3 | **Health checks that mean it** — a node is in service when it can serve, not when the process started |
| 4 | **Connection draining** — in-flight requests complete before a node stops |

> **`PE-004-F-02`. Condition 3 is where zero-downtime deployments usually fail**, and it is a
> per-component design obligation nobody has yet assigned. A readiness check that returns healthy
> before database connections and caches are warm produces a rolling deployment that serves errors
> from every node in turn. **Assigned to `PE-005` §6 as a container requirement.**

### 8.3 The cron exception, stated

Odoo cron nodes are **stopped, migrated and started** — a brief scheduler gap. **This is deliberate:**
two schedulers running concurrently during a rolling deployment means one job runs twice, and
`AR-009` `C-01`'s consumer idempotency does not cover **scheduled** jobs. A duplicate payroll
posting or a duplicate reminder batch is worse than a two-minute scheduler gap.

> **`PE-004-F-03`. Scheduled-job idempotency is unspecified estate-wide.** `AR-009` establishes
> idempotency for **event consumers**; `OPS-05` requires every scheduled job to report success,
> failure and duration; **no document requires a scheduled job to be safe to run twice.** With 60
> automations catalogued (Technology Stack §12.8), this is a real gap. Referred to `AR-003` and
> `RQ-009`.

### 8.4 Rollback

| # | Rule |
|---|---|
| **RB-01** | Rollback is **redeploying the previous artefact digest** — not rebuilding, not reverting commits |
| **RB-02** | The previous digest is **known and retained** (§6.3, §6.5) |
| **RB-03** | **Rollback is rehearsed in `staging` before every production release** — `DoD-16`, and the rehearsal produces an artefact (§8.6) |
| **RB-04** | **Data is not rolled back.** `PE-004-D-02` means the previous code runs against the new schema, which is why forward-only compatibility is the whole design |
| **RB-05** | A **rollback window** is declared per release: after it, rolling forward is the only route |

### 8.5 Why production is a manual gate

`02-05` §9 and `DoD-16` require it, and the reason is worth stating rather than inheriting:

| Consideration | Position |
|---|---|
| Wave-gate acceptance | A release may be technically green and **not yet accepted** (`GV-009`) |
| Change approval | `GV-003` requires a recorded decision |
| Business timing | `NFR-049`'s window, branch operating hours, cutover freezes (`MG-006`) |
| Migration duration | `MG-04` may make a release a windowed operation |

> **The gate is a *business* gate, not a technical one.** Everything technical has already been
> decided by the pipeline; what remains is *when*, and that is `RL-*`'s.

### 8.6 The rehearsal artefact

`DoD-16` requires a *"rollback plan documented and rehearsed."* **A rehearsal that leaves no evidence
did not happen.**

| # | Rule |
|---|---|
| **RH-01** | Each release candidate's `staging` deployment is followed by a **rollback to the previous digest and a re-deployment forward** |
| **RH-02** | The rehearsal emits: digests, durations, health-check outcomes, and any manual step required |
| **RH-03** | **A manual step in a rollback is a finding**, not a procedure — it is what fails at 02:00 |
| **RH-04** | The rehearsal artefact is a **release gate input** (`FF-133`) |

---

## 9. Promotion

| Environment | Trigger | Gate | Source |
|---|---|---|---|
| `ci` | Every push | — | Build |
| `dev` | Merge to `develop` | CI green | Same artefact |
| `sit` | Release candidate | CI green + integration | Same artefact |
| `uat` | **Manual** | QA Lead; **cycle freeze respected** (`PE-002` §5.5) | Same artefact |
| `staging` | **Manual** | Release Manager; **rollback rehearsal follows** | Same artefact |
| `perf` | **On gate provisioning** | `PE-002` §5.6 | Same artefact |
| `migration-staging` | **Per rehearsal** | Migration Lead | Same artefact |
| `training` | Per cohort | Change & Adoption Lead | Same artefact |
| `sandbox` | **Release candidate**, ahead of production | Integration Architect | Same artefact |
| **`prod`** | **Manual gate** | Wave-gate acceptance + change approval + **rehearsed rollback** | **Same artefact, pulled by digest** |
| **`dr`** | **Follows `prod` within the same release** | Replication + `PE-003` scale-from-code | Same artefact |

| # | Rule |
|---|---|
| **PM-01** | **No environment is skipped on the path to production.** A hotfix takes the same path, faster |
| **PM-02** | **`sandbox` receives a release candidate *before* production**, so partners meet a change before customers do (`IN-005` §10.3's notice obligations) |
| **PM-03** | **`dr` must not drift behind `prod`.** A standby running last month's artefact is a failover into an untested state. `FF-134` |

---

## 10. Where the 127 Fitness Functions Execute

### 10.1 The classification

| Class | Runs at | Enforcement | Example |
|---|---|---|---|
| **Static** | `pre-merge`, on code | **Fail** | `FF-01` no cross-module table access; `FF-122` no secret literal |
| **Contract** | `pre-merge`, against registries | **Fail** | `FF-95` pact; `FF-59` event reciprocity |
| **Plan-time** | `pre-merge`, on the IaC plan | **Fail** | `FF-101` no `0.0.0.0/0`; `FF-114` no `Z4` in non-production |
| **Runtime** | Continuous, in each environment | **Alert** → gate blocker | `FF-105` HA instance counts; `FF-118` replication lag |
| **Periodic** | Scheduled | **Fail** the next gate | `FF-120` drift; `FF-126` state restore |
| **Gate** | `gate` profile | **Block** | `FF-98` DR drill; `FF-133` rollback rehearsal |

### 10.2 The rule that keeps them meaningful

| # | Rule |
|---|---|
| **FG-01** | **Every fitness function has exactly one execution point** and one enforcement class. A check that runs in two places with two behaviours is two checks |
| **FG-02** | **A blocking check must be fast enough for its profile.** A check that cannot run in 20 minutes is not a `pre-merge` check — move it, do not weaken it (`BG-03`) |
| **FG-03** | **A reporting check that has never failed is reviewed** — either it is redundant or it is not actually running (`RN-04` makes this measurable) |
| **FG-04** | **A new fitness function is not enabled as blocking on the day it is written.** One wave in reporting mode, then blocking — otherwise the first run blocks the whole estate on a pre-existing condition |

> **`FG-04` matters immediately.** `FF-60` (event naming) cannot be enabled until `RM-03`'s 242
> renames land; `FF-53` will report M40 and M42 as having zero business-rule coverage because
> `05-05` registers no rules for them; `FF-119` will fail on day one against an estate with **no
> IaC-managed resources at all**. **Every one of those is a true finding, and none of them should
> block a developer's pull request on the day the gate is switched on.**

---

## 11. Runners, Credentials and Pipeline Security

### 11.1 Runners

| # | Rule |
|---|---|
| **RU-01** | Runners are **ephemeral** — created per job, destroyed after. A persistent runner accumulates state and secrets |
| **RU-02** | Runners live in **`Z5`** (`PE-001` §4.1) and reach `Z2`/`Z3` under `Z5`'s rules |
| **RU-03** | **A runner never has production data.** `TAF-52`'s database is synthetic |
| **RU-04** | Runners are built from a **pinned image** rebuilt on the `BE-007` cadence |

### 11.2 Credentials — `TAF-56`

| # | Rule |
|---|---|
| **CR-01** | **No long-lived credential exists in the pipeline.** Identity is federated; tokens are short-lived |
| **CR-02** | Credentials are **injected per job from Vault** (`PE-009`), scoped to that job |
| **CR-03** | **A pull-request build from a fork receives no credentials at all** — §11.3 |
| **CR-04** | Deployment credentials are **per environment**; a `staging` deploy identity cannot reach `prod` |
| **CR-05** | **`25-resident` apply credentials are separate** and separately approved (`PE-003` `RS-02`) |

### 11.3 The pull-request trust boundary

> **`PE-004-D-03`. A pull-request build runs with no deployment credentials, no signing keys and no
> registry push rights.**

A pull request is **untrusted code proposing to run inside the pipeline**. A build with push rights
lets a contributor publish an artefact; a build with signing keys lets them sign one.

| Build | May |
|---|---|
| Pull request | Read source, resolve pinned dependencies, run tests against ephemeral resources |
| Merge to `develop` | The above, **plus** build, sign, push |
| Release | The above, **plus** promote |
| Production deploy | **Pull by digest and deploy.** It cannot build |

### 11.4 Pipeline configuration as code

| # | Rule |
|---|---|
| **PC-01** | Pipeline definitions are **in the monorepo**, reviewed like code (`BE-003`) |
| **PC-02** | A change to a **blocking gate** requires the gate owner's approval — Security Lead for `SC-005` gates, Design Authority for `AR-012`, QA Lead for `QA-*` |
| **PC-03** | **Disabling a gate is a recorded decision with an expiry** (`PE-003` §11.2 parity). `FF-136` |
| **PC-04** | The pipeline **scans itself** (`SE-05`) |

> **`PC-03` is the control that protects the other 126.** The realistic failure mode is not a gate
> being wrong; it is a gate being disabled during a delivery crunch and never re-enabled.

---

## 12. Build Sequence

**This document's own delivery**, sequenced as Wave 0 — which `QA-001` and `QA-005` both asked for.

| # | Deliverable | Wave | Enables |
|---|---|:--:|---|
| **P-01** | Repository, branching, pre-commit, secret scan | **W0** | Any commit |
| **P-02** | `pre-merge`: lint, type, unit, coverage | **W0** | First merge |
| **P-03** | **Ephemeral database + `QA-004` snapshot** (`TAF-52`) | **W0** | Integration and contract stages |
| **P-04** | Build-once, registry, SBOM, provenance | **W0** | Promotion |
| **P-05** | Deploy to `ci`, `dev` | **W0** | Feedback |
| **P-06** | **Pact broker + schema registry** (`TAF-57`) | **W0** | `IN-008` `CT-02`, `IN-003` |
| **P-07** | `PE-003` plan + policy stage | **W0** | Infrastructure changes |
| **P-08** | Migration dry run on a production-sized clone | **W1** | `MG-03`, `MG-04` |
| **P-09** | Promotion to `sit`, `uat`, `staging` + **rollback rehearsal** | **W1** | `DoD-16` |
| **P-10** | Security stages: SAST, dependency, container, IaC | **W1** | `SC-005` `G-01`…`G-10` |
| **P-11** | **Result normalisation** (`TAF-59`) + fitness-function reporting | **W1** | `RN-04`, `QA-011` |
| **P-12** | Production deploy with manual gate + provenance verification | **W1** | Go-live |
| **P-13** | `nightly` profile, drift check | **W1** | `FF-120` |
| **P-14** | `gate` profile: performance, DR evidence | **W2** | `GV-009` |
| **P-15** | Device lab or farm (`TAF-58`) | **W2** | `A4` — **unfunded, `Q-04`** |

> **Thirteen of fifteen are Wave 0 or Wave 1**, into a wave `GV-004` already measures at **5.33×
> over-commitment**. `AR-001` §11.3: *"Wave 1 is an infrastructure wave, and must be resourced as
> one."* **Four documents have now said this** — `AR-001`, `QA-001`, `QA-005` and `PE-002`.

---

## 13. Fitness Functions

Allocation confirmed by enumerating every `FF-nn` definition across all authored categories at
**2026-08-19 01:15 (+06)**, per `PGD-AUDIT-007` `PGD-A7-01`.

| # | Check | Scope | Timing | Enforcement |
|---|---|---|---|---|
| **FF-128** | The artefact deployed to `prod` is **byte-identical** to the one that passed `staging` | Per release | Deploy | **Fail** |
| **FF-129** | Production deploys **by digest**, never by tag | Per deploy | Deploy | **Fail** |
| **FF-130** | Every deployed artefact has **valid signed provenance** | Per deploy | Deploy | **Fail** |
| **FF-131** | **No migration in one release both adds and removes** a schema object | Per release | `release` | **Fail** |
| **FF-132** | Migration duration on the production-sized clone is within the deployment window | Per release | `release` | **Fail** |
| **FF-133** | **A rollback rehearsal artefact exists** for the release candidate | Per release | `release` | **Fail** |
| **FF-134** | **`dr` runs the same artefact digest as `prod`** | Continuous | Runtime | **Alert** → gate blocker |
| **FF-135** | The `pre-merge` profile's **p95 duration is under 20 minutes** | Continuous | Weekly | **Alert**; wave-gate finding |
| **FF-136** | **No blocking gate is disabled without a recorded, unexpired exemption** | All gates | Daily | **Fail** |

---

## 14. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `PE-004-D-01` | Build model | Rebuild per environment · branch per environment · **build once, promote the artefact** | **Build once** | The thing tested must be the thing deployed | `FF-128`; configuration injected at release |
| `PE-004-D-02` | Migrations | Reversible with down-migrations · **forward-only, backward-compatible** | **Forward-only** | Down-migrations that restore dropped data do not exist; two-release compatibility is what makes `NFR-008` real | `MG-01`, `FF-131`; a rename takes three releases |
| `PE-004-D-03` | Pull-request trust | Full credentials · **no deployment credentials, no signing keys, no push** | **None** | A PR is untrusted code proposing to run inside the pipeline | §11.3 |
| `PE-004-D-04` | Production trigger | Continuous deployment · **manual gate** | **Manual gate** | The remaining decision is *when*, and it is a business decision — acceptance, change approval, `NFR-049`'s window | §8.5; a departure from Humble & Farley, stated |
| `PE-004-D-05` | Odoo cron deployment | Rolling · **stop, migrate, start** | **Stop/start** | Two schedulers means one job runs twice, and scheduled-job idempotency is unspecified estate-wide (`PE-004-F-03`) | §8.3; a brief scheduler gap, accepted |
| `PE-004-D-06` | Test database | Shared per environment · **ephemeral per run, restored from a versioned snapshot** | **Ephemeral, restored** | `TAF-52`; removes order-dependent failure and holds the 20-minute budget | `DB-01`…`DB-04` |
| `PE-004-D-07` | New fitness functions | Blocking immediately · **one wave reporting, then blocking** | **Reporting first** | Several will legitimately fail on day one against pre-existing conditions | `FG-04` |
| `PE-004-D-08` | `sandbox` promotion | After production · **before production** | **Before** | Partners must meet a change before customers do, and `IN-005` §10.3 obliges notice | `PM-02` |

---

## 15. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| **Q-01** | **Is Wave 0 pipeline build funded and staffed?** Thirteen of fifteen deliverables are W0/W1, into a 5.33× over-committed wave | **Programme Director** | **W0 — blocking** | Everything |
| **Q-02** | **Which CI/CD platform?** §5's stages and §11's trust boundary are platform-independent by design; runners, federation and the fork policy are not | CTO + Platform Engineering Lead | **W0 — blocking** | §11, `P-01` |
| **Q-03** | Who owns the **production-sized clone** the migration dry run needs, and how long does producing it take? (`MG-03`) | Platform + `PE-002` owner | **W1** | Stage 14, `P-08` |
| **Q-04** | **Is a device lab or farm funded?** `TAF-58` states the requirement against nothing | QA Lead + Programme Director | **W2** | `A4` mobile coverage, `P-15` |
| **Q-05** | **Who owns scheduled-job idempotency?** (`PE-004-F-03`) 60 automations, no requirement that any is safe to run twice | Chief Architect with `RQ-009` | **W1** | §8.3, cron safety |
| **Q-06** | Which component owns the **readiness-check contract** that `NFR-008` depends on? (`PE-004-F-02`) | `PE-005` owner | **W1** | Zero-downtime deployment |
| Q-07 | Does the pact broker (`TAF-57`) run as pipeline infrastructure or as a hosted service, and what is its availability expectation? | Integration Architect + Platform | W1 | §5.3, `PS-01` |

---

## 16. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | The gate backlog waiting on a pipeline is **counted** | Opening table — **127 fitness functions**, none executable |
| AC-02 | **All eight `QA-005` requirements are answered** individually | §3.3 |
| AC-03 | The five profiles are adopted with the **20-minute budget as a design constraint**, and the mechanisms that hold it are stated | §4.2, §4.3 |
| AC-04 | Build-once-and-promote is ruled, and enforced | `PE-004-D-01`, `FF-128` |
| AC-05 | **Odoo-specific stages** exist — installability, upgradability, fork register | §5.5 |
| AC-06 | Forward-only migrations are specified **with the multi-release patterns** | §7.2 |
| AC-07 | Zero downtime is stated as **four conditions**, and the one nobody owns is assigned | §8.2, `PE-004-F-02` |
| AC-08 | Rollback is redeployment, **rehearsed with an artefact** | §8.4, §8.6 |
| AC-09 | Every fitness function has **one execution point and one enforcement class** | §10 |
| AC-10 | The pull-request trust boundary is explicit | §11.3 |
| AC-11 | Gate disabling requires a **recorded, expiring** exemption | `PC-03`, `FF-136` |
| AC-12 | The build is sequenced as **Wave 0** | §12 |

**Definition of done.** Complete when every criterion is met, **Q-01 and Q-02 are decided**,
`P-01`…`P-14` are delivered, `FF-128`…`FF-136` are enabled, and `PGD-000`'s `PE-004` row carries a
fresh enumeration timestamp. **The 127 fitness functions specified across nine categories are not
"enabled" until `RN-04` reports them** — an assertion is not evidence.

---

## 17. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | **`QA-005`** §11.1, §11.2 | **Eight explicit requirements on this document**, and the profiles |
| Upstream | **`AR-012`** v1.1 | 37 fitness functions this pipeline executes |
| Upstream | `SC-005` `G-01`…`G-10` | Security stages |
| Upstream | `BE-002`, `BE-003`, `BE-004`, `BE-007` | Lint, branching, repository and dependency gates |
| Upstream | **`PE-002`**, **`PE-003`** | Promotion targets; the apply path and policy gates |
| Downstream | **`PE-005`** | Image build, readiness contract (`PE-004-F-02`) |
| Downstream | **`PE-006`** | The `gate` profile's performance stage |
| Downstream | **`PE-007`** | `FF-98` DR-drill evidence at the gate; `MG-06` pre-migration backup |
| Downstream | **`PE-009`** | Configuration injection at release; `CR-02` |
| Downstream | `RL-*` | Release scheduling consumes the promotion path |
| Downstream | `QA-011` | Consumes `RN-01`'s normalised results |
| Lateral | `../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §18.2, §18.3 | The 13-stage CI table, extended to 17; `OPS-07` |
| Lateral | `../../1000fix_ERP_Module/02_Architecture/02-05_*.md` §9 | Deployment triggers and gates |

---

## 18. References

**Within this repository**
[`../PGD-000_Master_Register_of_Project_Guiding_Documents.md`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md) ·
[`./_CATEGORY_OVERVIEW.md`](./_CATEGORY_OVERVIEW.md) ·
[`./PE-002_Environment_Strategy_and_Specification.md`](./PE-002_Environment_Strategy_and_Specification.md) ·
[`./PE-003_Infrastructure_as_Code_Standard.md`](./PE-003_Infrastructure_as_Code_Standard.md) ·
[`./PE-005_Containerisation_and_Orchestration_Design.md`](./PE-005_Containerisation_and_Orchestration_Design.md) ·
[`./PE-007_Backup_Disaster_Recovery_and_Business_Continuity_Design.md`](./PE-007_Backup_Disaster_Recovery_and_Business_Continuity_Design.md) ·
[`./PE-009_Configuration_and_Secrets_Management_Standard.md`](./PE-009_Configuration_and_Secrets_Management_Standard.md) ·
[`../02_Architecture_and_Design/AR-012_Architecture_Compliance_and_Fitness_Function_Standard.md`](../02_Architecture_and_Design/AR-012_Architecture_Compliance_and_Fitness_Function_Standard.md) ·
[`../08_Quality_Engineering_and_Test/QA-005_Test_Automation_Framework_Specification.md`](../08_Quality_Engineering_and_Test/QA-005_Test_Automation_Framework_Specification.md) ·
[`../04_Integration_and_API_Engineering/IN-008_Integration_Test_Sandbox_and_Certification_Specification.md`](../04_Integration_and_API_Engineering/IN-008_Integration_Test_Sandbox_and_Certification_Specification.md)

**Workspace**
`../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §18.2, §18.3, §18.6 ·
`../../1000fix_ERP_Module/02_Architecture/02-05_*.md` §9 ·
`../../1000fix_ERP_Module/02_Architecture/02-02_*.md` §8 (`DoD-03`…`DoD-17`)

**External sources**

| Source | Verified |
|---|---|
| Humble & Farley, *Continuous Delivery* — the deployment pipeline, build once and promote | 2026-08-19 |
| Twelve-Factor App §5 — build, release, run | 2026-08-19 |
| SLSA — build provenance levels | 2026-08-19 |
| NIST SP 800-218 (SSDF) — secure software development practices | 2026-08-19 |
| Semantic Versioning 2.0.0 | 2026-08-19 |

---

## 19. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-19 | Platform Engineering | Initial issue. Counts the backlog waiting on a pipeline: **127 fitness functions specified across nine categories, none executable**. **Answers all eight `QA-005` `TAF-52`…`TAF-59` requirements** individually and adopts the five profiles with the 20-minute pre-merge budget, stating the four mechanisms that hold it. Rules build-once-and-promote and **forward-only migrations** with the multi-release patterns. States zero downtime as four conditions and **assigns the readiness-check obligation nobody owned** (`PE-004-F-02`). Records that **scheduled-job idempotency is unspecified estate-wide across 60 automations** (`PE-004-F-03`), and that `AR-006`'s 18 dependency cycles impose a cost on **every pull request** through affected-component selection (`PE-004-F-01`) | *Pending — CTO, QA Lead; `GV-002` not constituted* |

---

*`PE-004` · Category 10 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
