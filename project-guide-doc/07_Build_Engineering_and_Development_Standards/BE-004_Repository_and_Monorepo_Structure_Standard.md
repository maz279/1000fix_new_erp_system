---
id: BE-004
title: Repository & Monorepo Structure Standard
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
  ISO 10007:2017 §6 · Odoo 19.0 addons-path model · OCA repository conventions ·
  Git submodule and subtree semantics · Turborepo / pnpm workspace model (inherited from AGENTS.md)
traces_to: >
  PGD-000 BE-004 · TD-15 (monorepo, no structure) · 02-05 §9 · Technology Stack Specification §18.1 ·
  AR-001 development view · AR-007 §3 (module internals) · PG-M12 / PGD-A2-15 (nothing under version control)
depends_on: BE-005 (issued CD identifiers) · AR-006 (build sequence) · AR-007 (module anatomy)
verified_on: 2026-08-18
enumeration_timestamp: 2026-08-18 13:06 (+06)
priority: P0
needed_by: Now
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# BE-004 — Repository & Monorepo Structure Standard

### Category 07 · Code `BE` · Odoo 19.0 addons model · OCA conventions · Git subtree/submodule semantics

---

## 1. Purpose

`TD-15` decides *"Monorepo"* against *"Polyrepo"*, with the rationale *"cross-cutting changes across
80 deliverables are common."* That is the entire published structural decision for the repository
that will hold **331 custom-development items across eight declared deliverable types and five
language stacks**, alongside **23 Odoo core modules, 140+ OCA modules across 18 repositories**, and a
**699-file documentation estate**.

A monorepo without a layout is not a decision; it is a deferral. The first developer to commit
decides where `cd_service_order` lives, and every subsequent decision is constrained by it. Moving a
directory after 200 modules depend on its import path is a migration, and `AS-05` — extend, never
fork — depends structurally on third-party code living somewhere a developer *cannot* casually edit.

This document is that layout: the tree, the third-party vendoring rules, the addons-path composition
per environment, the build tooling per stack, and the ownership boundaries that make code review
route to the right people.

> **The repository does not exist yet.** Verified 2026-08-18 13:06 (+06): **no `.git`, `.hg` or
> `.svn` directory exists anywhere under the workspace root**, across 699 files (`PG-M12`,
> `PGD-A2-15`). §13 is therefore not a migration plan but an initialisation plan, and it is Wave 0
> work.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | The repository decision — one repository, its boundary, and what stays outside it |
| 2 | The **top-level tree**, to the depth at which a developer can place any new file without asking |
| 3 | Third-party code: the **Odoo submodule pin**, the **OCA subtree strategy**, and the fork register's physical form |
| 4 | `addons_path` composition, per environment, and the layer order it encodes |
| 5 | Build tooling and workspace configuration per language stack |
| 6 | Ownership — `CODEOWNERS`, generated from `BE-005` |
| 7 | What may never enter the repository, and the mechanisms that keep it out |
| 8 | Repository size, clone-time and CI path-filtering budgets |
| 9 | Documentation-in-repository: where the 699-file estate lives |
| 10 | Day-0 initialisation sequence |

**Explicitly out of scope**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| The inside of a `cd_*` Odoo module | `AR-007` §3 | That standard governs module anatomy; this one governs everything above the module directory |
| Branching, commits, review, tagging | `BE-003` | Structure vs process |
| Language style and linter rules | `BE-002` | This document says where a config file lives; `BE-002` says what is in it |
| Dependency pinning, licences, SBOM | `BE-007` | This document places the lockfiles; `BE-007` governs their content |
| CI pipeline stages and runners | `PE-004` | §11 states the **path-filtering requirement**; `PE-004` builds it |
| Environment provisioning and IaC | `PE-002`, `PE-003` | `infra/` is placed here; its content is theirs |
| Secret storage | `PE-006` / `SC-007` | §10 states the prohibition; Vault is theirs |
| The identifiers used in directory names | `BE-005` | Consumed, not allocated |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| **Every developer** | Where does this file go? Answered by §4 without asking anyone |
| Platform Engineering | The paths CI filters on; the artefacts each pipeline builds |
| Solution Architect | The physical enforcement of `AS-05` and the dependency layering `DL-01`…`DL-04` |
| Implementation vendor | The repository they are given on day one and must deliver into continuously (RFP §5.10) |
| Security | The paths that must never contain a secret, a key or residency-classified data |
| Release Manager | What a release artefact is composed of, and from which paths |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | How this document conforms | Departure and rationale |
|---|---|---|
| **Odoo 19.0 addons model** | §6 composes `addons_path` in strict layer order; custom code never shadows core | Full |
| **OCA repository conventions** | OCA repositories are vendored **whole**, at repository granularity, retaining their own structure and `README.rst` | **Departure:** OCA repositories are consumed as **subtrees**, not as submodules or pip packages. §5.3 gives the reasoning |
| **Git submodule semantics** | Odoo core is a submodule pinned to an exact commit | Full |
| **Git subtree semantics** | OCA repositories are subtrees so that a local v19 migration is a normal commit, reviewable and contributable upstream | Full |
| **pnpm workspace + Turborepo** | Inherited from `AGENTS.md`; retained for the TypeScript estate | Full |
| `ISO 10007:2017` §6.2 | Every directory maps to an identified configuration item (`BE-005`) or to a named shared concern | Full |

### 2.2 Source material relied on

| Source | What it establishes |
|---|---|
| `02-05` §10 `TD-15` | The monorepo decision, and its rationale |
| `02-05` §9 | *"Monorepo with Odoo as a pinned submodule, OCA as subtrees, custom modules and services as first-class directories"* — the four-clause seed this document expands |
| TSS §18.1 | Restates the same four clauses, and adds the continuous-delivery-of-source obligation |
| **`../../../AGENTS.md`** | The in-house engineering conventions of the sibling portal programme: pnpm, Turborepo, Docker Compose, GitHub Actions, ESLint + Prettier, Husky + lint-staged |
| `../../../Intergrated_web_portal/Technical_documentation_roadmap/Architecture & Infrastructure/IMPL-18_Monorepo_Migration_Architecture_Evolution_Turborepo.md` | An in-house monorepo migration architecture already exists for the portal estate |
| `AR-007` §3.1, §3.4 | The module directory anatomy and the four-layer dependency order this tree must make physical |
| `AR-006` | Build sequence and the tier model that `CODEOWNERS` follows |
| `BE-005` §6, §9.1 | 331 items; 270 of them Odoo work; 14 portal deliverables |
| TSS §3.5 | The six-environment ladder that `addons_path` and configuration must serve |

### 2.3 The inherited conventions are real, and they cover one stack of four

`02-05` §9 opens: *"Inherits the conventions already established in the repository (`AGENTS.md`)."*
That inheritance is genuine and useful — `AGENTS.md` carries a complete TypeScript standard, a branch
model, a commit convention, a PR process and a test strategy, all already agreed in-house.

Measured against the ERP estate at 2026-08-18 13:06 (+06):

| Test on `AGENTS.md` | Result |
|---|---:|
| Mentions of **Odoo** | **0** |
| Mentions of **Flutter** | **0** |
| Mentions of **Dart** | **0** |
| Mentions of **Python** | **1** |
| `BE-005` items in stacks `AGENTS.md` does not cover | **270 of 331 — 82%** |

It also names **Rasa 3.6** and **Timefold** in its technology table, both of which the ERP rejected
by name in `TD-06` and `TD-05`; and it lists **Drizzle ORM** in the stack table while the build
commands and the security section reference **Prisma**.

> **The inheritance is retained where it applies and must not be assumed where it does not.** §7
> adopts `AGENTS.md`'s pnpm/Turborepo tooling for the TypeScript estate and `BE-002` adopts its
> TypeScript rules. Neither this document nor `BE-002` inherits its technology table. Raised as
> finding `BEA-09`.

---

## 3. The Repository Decision

### 3.1 One repository, and what it contains

`TD-15` is confirmed. The reasoning is stronger than `02-05` states it, because the coupling is not
only "cross-cutting changes are common" — it is that **a single change routinely spans three
languages**. Adding a field to `fix.service.order` touches the Odoo module, the OpenAPI contract, the
Next.js portal type, the Flutter offline schema and the migration script. In a polyrepo that is five
pull requests across five repositories with no atomic point, and `FF-12`'s portal contract test has
nothing to run against.

| Repository | Contents | Rationale |
|---|---|---|
| **`1000fix-erp`** *(this standard)* | All 331 CD items, vendored Odoo and OCA, infrastructure code, tooling, and the guiding-document estate | One atomic change across stacks; one CI; one version of the truth |
| `1000fix-portal-platform` *(pre-existing, `CON-03`)* | The Next.js + Payload CMS platform the portal programme already operates | **Cannot be replaced** (`CON-03`). The ERP integrates with it across a versioned contract (`IN-002`), it does not absorb it |
| `1000fix-erp-secrets` | **Does not exist.** Secrets live in Vault | §10 |

> **`REPO-01`.** There is exactly one ERP repository. A second ERP repository requires an ADR in
> `AR-004` and a `D-nnn` decision in `GV-003`.

### 3.2 The boundary with the portal platform

`CON-03` fixes the portal platform as unreplaceable. The six Next.js portals in `BE-005` (`CD-P01-01`,
`CD-P04-01`, `CD-P06-01`, `CD-P07-01`, `CD-P08-01`, `CD-P10-01`, `CD-P12-01`) are therefore ambiguous
in ownership until `UX-001` and `IN-002` rule.

| Position | Consequence |
|---|---|
| Portals built **inside** `1000fix-erp` | Atomic changes with the ERP; duplicates the portal platform's component library and deployment pipeline |
| Portals built **inside the portal platform** | Reuses `CON-03`'s platform; every ERP change touching a portal becomes a two-repository change |

**Ruling deferred, not assumed.** §4's tree reserves `apps/web/` for portals so that either ruling
can be executed without moving Odoo or service code. Recorded as `Q-01` and referred to `IN-002` and
`AR-002` `EP-01`. Until it is ruled, portal code is developed in `apps/web/` and the contract test
`PS-11` runs in this repository.

---

## 4. The Tree

Depth shown is the depth at which placement is unambiguous. Directories marked **generated** are
produced by tooling and are not hand-edited.

```
1000fix-erp/
│
├── README.md                       ← how to get running in one page; points at BE-001
├── AGENTS.md                       ← agent/contributor conventions for THIS repository
├── CODEOWNERS                      ← generated from BE-005 (§8)
├── LICENSE                         ← LGPL-3, per AR-007 §3.3
├── .gitattributes                  ← line endings, LFS patterns, linguist overrides
├── .gitignore
├── .pre-commit-config.yaml         ← BE-002 §9
├── .editorconfig
│
├── vendor/                         ← THIRD-PARTY CODE. Read-only to product developers (§5)
│   ├── odoo/                       ← git submodule, pinned commit on branch 19.0
│   └── oca/                        ← git subtrees, one directory per OCA repository
│       ├── field-service/
│       ├── helpdesk/
│       ├── management-system/
│       ├── operating-unit/
│       ├── hr/  payroll/  dms/  server-tools/  web/
│       ├── account-financial-tools/  account-financial-reporting/
│       ├── reporting-engine/  mis-builder/
│       ├── stock-logistics-workflow/  stock-logistics-barcode/  stock-logistics-warehouse/
│       ├── purchase-workflow/  partner-contact/  contract/
│       └── l10n-bangladesh/
│
├── addons/                         ← ALL custom Odoo modules — 270 of 331 CD items
│   ├── platform/                   ← AR-007 layer 3. Depended on, never depending on layer 4
│   │   ├── cd_event_outbox/        ← CD-M28-01
│   │   ├── cd_rbac_ext/            ← CD-M29-01
│   │   ├── cd_entity_config/       ← CD-M30-01
│   │   ├── cd_party_master/        ← CD-M33-01
│   │   └── …
│   └── domain/                     ← AR-007 layer 4, one subdirectory per module category
│       ├── a_service_delivery/
│       │   ├── cd_service_order/   ← CD-M01-01
│       │   ├── cd_diagnostic/      ← CD-M01-02
│       │   └── …
│       ├── b_customer_engagement/  c_commercial/  d_circular/  e_supply_chain/
│       ├── f_asset_facilities/     g_finance/     h_people/    i_governance/
│       └── j_data_analytics/       k_platform/
│
├── services/                       ← standalone services — 33 CD items + the service half of 90
│   ├── dispatch-scoring/           ← Python / FastAPI
│   ├── pricing-engine/
│   ├── ml-gateway/
│   ├── telemetry-collector/        ← Go
│   ├── notification-dispatcher/    ← Node.js
│   └── <one directory per service, named for its CD item>
│
├── apps/                           ← end-user applications — 14 portal CD items
│   ├── mobile/
│   │   ├── technician/             ← CD-P02-01, Flutter
│   │   ├── rider/                  ← CD-P09-01, Flutter
│   │   ├── auditor/                ← CD-P11-01, Flutter
│   │   └── customer/               ← CD-P01-02, framework pending D-027
│   └── web/
│       ├── customer/               ← CD-P01-01, Next.js
│       ├── corporate/  analytics/  seller/  brand/  agent-console/  partner/
│       └── admin/                  ← CD-P03-01 is an Odoo OWL module; see §4.2
│
├── libs/                           ← shared, versioned, cross-stack libraries
│   ├── py/
│   │   ├── fix_events/             ← the event client; FF-28 forbids direct bus clients
│   │   ├── fix_residency/          ← the ONLY client of the residency service; FF-09
│   │   └── fix_testing/            ← fixtures, factories, offline harness helpers
│   ├── ts/
│   │   ├── api-client/             ← generated from OpenAPI; see contracts/
│   │   ├── ui/                     ← shared components across the six Next.js portals
│   │   └── i18n/                   ← BN-005 key loading and pluralisation
│   └── dart/
│       ├── fix_offline/            ← the ONE offline engine (ADR-024) shared by three apps
│       └── fix_ui/
│
├── contracts/                      ← the interface surface, versioned independently of code
│   ├── openapi/                    ← one file per API-exposing CD item (AR-007 L5-01)
│   ├── events/                     ← event schemas; the IN-003 catalogue's machine form
│   └── portal/                     ← the CON-03 contract; PS-11 tests run against it
│
├── db/
│   ├── migrations/                 ← non-Odoo schema (TimescaleDB, ClickHouse)
│   └── seeds/                      ← synthetic fixtures only (§10)
│
├── infra/                          ← PE-002, PE-003 own the content
│   ├── compose/                    ← local development stack (BE-001)
│   ├── k3s/                        ← manifests / Helm
│   ├── terraform/
│   └── odoo-conf/                  ← per-environment odoo.conf templates (§6)
│
├── tooling/
│   ├── cd-register.yaml            ← generated from BE-005 §11.4
│   ├── fitness/                    ← AR-012 FF-* check implementations
│   ├── generators/                 ← module scaffold (BE-006 CBS-09), API client generation
│   └── scripts/
│
├── docs/                           ← in-repository engineering documentation (§12)
│   ├── adr/                        ← AR-004 records, one file per ADR
│   ├── runbooks/                   ← per CD item, per BE-006
│   └── guides/
│
└── .github/
    ├── workflows/                  ← PE-004 owns the content
    ├── PULL_REQUEST_TEMPLATE.md    ← BE-003 §7
    └── ISSUE_TEMPLATE/
```

### 4.1 Placement rules

| # | Rule |
|---|---|
| **`REPO-02`** | Every directory under `addons/`, `services/` and `apps/` maps to **exactly one issued CD identifier** from `BE-005` §6. A directory with no CD item, or a CD item with no directory, is a defect |
| **`REPO-03`** | `addons/platform/` holds `AR-007` layer-3 modules; `addons/domain/<category>/` holds layer-4. **The directory encodes the layer**, so `FF-17` can be checked by path before it is checked by import |
| **`REPO-04`** | Category subdirectories under `addons/domain/` use the lowercase letter and name from `02-02` §5 — `a_service_delivery`, `g_finance`. A module that is re-categorised **moves directory and keeps its CD identifier** (`CDR-02`) |
| **`REPO-05`** | `libs/` holds code with **more than one consumer**. A library with one consumer belongs inside that consumer. This is checked at review, not by tooling |
| **`REPO-06`** | `contracts/` is the only place an OpenAPI or event schema is authoritative. A schema inside a module directory is a copy and is generated, never edited |
| **`REPO-07`** | No product code lives at the repository root. The root holds configuration and entry-point documentation only |
| **`REPO-08`** | A file's path never encodes a wave, a sprint, a person or a vendor. Those change; the structure does not |
| **`REPO-09`** | `CODEOWNERS` is **generated** from `BE-005` and `AR-006`, never hand-edited (§8) |

### 4.2 Three placements that will be got wrong

| Case | Ruling |
|---|---|
| **`CD-P03-01` Admin Operations Portal, 30 PW** | It is declared *"Odoo module (OWL 2)"* in `P03` §16.2, not a Next.js application. It therefore lives in **`addons/platform/cd_workspace_framework/`**, not in `apps/web/admin/`. The `apps/web/admin/` entry in §4's tree is a **placeholder that must not be created** — recorded here because the portal name invites the wrong placement |
| **An "Odoo module + service" item** (90 of 331) | It is **one CD item and two directories**: the module under `addons/`, the service under `services/`, both named for the same identifier. `component.yaml` (`BE-006`) carries the identifier in both, and the register row is not duplicated |
| **`cd_offline_sync` and the three Flutter apps** | `ADR-024` mandates **one** offline engine across the three field applications. The engine is `libs/dart/fix_offline/`; the Odoo-side journal and idempotency ledger is `addons/platform/cd_offline_sync/`. Neither app carries its own copy — this is the single most likely structural defect in the programme, because three teams will each want their own |

---

## 5. Third-Party Code

### 5.1 The rule the structure exists to enforce

`AS-05` — *"Extensions are separate modules, not modifications to core"* — is the programme's
load-bearing upgrade-safety rule (`AR-007` §5, risk `TR-04`). `FF-03` blocks any build that modifies
`vendor/`.

**A rule enforced only in CI is enforced late.** The tree makes the rule visible before CI runs:
third-party code is in `vendor/`, product code is not, and no product directory sits inside
`vendor/`. A developer who finds themselves editing a path beginning `vendor/` knows immediately.

### 5.2 Odoo core — submodule

| Aspect | Standard |
|---|---|
| Mechanism | **Git submodule**, `vendor/odoo`, tracking branch `19.0` |
| Pin | An **exact commit SHA**, recorded in `.gitmodules` and in `tooling/versions.lock` |
| Update | A deliberate commit that moves the pin, raised as its own PR, with the upstream changelog in the description and the full regression suite green |
| Cadence | **Monthly**, per TSS §18.5; security patches out of cycle |
| Never | A local commit inside `vendor/odoo`. `FF-03` compares the working tree against the pinned tree and requires an empty diff |

> **Why a submodule and not a subtree, for Odoo alone.** Odoo core is never modified locally, so
> subtree's only advantage — making local commits natural — is a disadvantage here. A submodule makes
> a local modification *awkward*, which is exactly the ergonomics `AS-05` wants.

### 5.3 OCA — subtrees

| Aspect | Standard |
|---|---|
| Mechanism | **Git subtree**, one directory per OCA repository under `vendor/oca/` |
| Granularity | **Whole repository**, not per module. OCA repositories move as units and their CI assumes it |
| Pin | Recorded in `tooling/versions.lock` as repository + commit; `BE-007` `LX-03` governs the lock |
| Local change | Permitted **only** to migrate a module to v19, and **only** with a fork-register entry (§5.4) |
| Upstream | Every local migration is contributed back, per `02-05` §3's standing commitment. Subtree makes `git subtree push` the natural route |

> **Why subtrees and not submodules for OCA.** `02-05` §3 records that eight `field-service` modules
> and eight `helpdesk` modules are **not yet migrated to v19**, and `A-03` assumes the gap is closable
> in 12–20 PW. That migration work is done *by this programme*, in this repository, and must be
> reviewable in a normal PR and pushable upstream. A submodule would require a fork repository per
> OCA repository — eighteen extra repositories to authenticate, track and review across.

### 5.4 The fork register

`AR-007` §5.4 requires a fork register and `FF-03` enforces it. Its physical form is a single file so
that the check has one input:

```yaml
# vendor/FORKS.yaml — every deviation from upstream, or the build fails
- repository: OCA/field-service
  module: fieldservice_stock
  reason: "v19 migration; upstream PR OCA/field-service#1842 open"
  approved_by: Chief Architect
  approved_on: 2026-09-14
  upstream_pr: https://github.com/OCA/field-service/pull/1842
  review_at: W2-gate
  removal_condition: "upstream merges and the subtree is updated past the merge commit"
```

| # | Rule |
|---|---|
| **`REPO-10`** | Any diff between `vendor/` and its pinned upstream **must** have a `FORKS.yaml` entry. `FF-03` fails otherwise |
| **`REPO-11`** | Every entry carries an approver, a date, a **removal condition** and a **review gate**. An entry without a removal condition is a permanent fork disguised as a temporary one |
| **`REPO-12`** | The register is reviewed at every wave gate under `GV-009`. Entries whose upstream PR has been merged are removed by updating the subtree, not by deleting the row |

### 5.5 What `vendor/` costs

| Concern | Position |
|---|---|
| Repository size | 18 OCA repositories plus Odoo core is a large checkout. §11 sets the budget and the mitigation (partial clone, sparse checkout for non-Odoo developers) |
| Reviewing vendored code in PRs | `.gitattributes` marks `vendor/**` as `linguist-vendored` so it is collapsed in diffs; `CODEOWNERS` routes any `vendor/` change to the Chief Architect |
| Confusing "our code" with "their code" | The single-directory rule and the `FORKS.yaml` requirement. There is no third category |

---

## 6. `addons_path` Composition

`addons_path` is where the four-layer dependency order of `AR-007` §3.4 becomes executable. Order
matters: Odoo resolves a module name against the first matching path, so a custom module that shares
a name with a core module **silently shadows it**.

```ini
# infra/odoo-conf/base.conf — the order is normative, not cosmetic
addons_path =
    vendor/odoo/addons,
    vendor/odoo/odoo/addons,
    vendor/oca/field-service,
    vendor/oca/helpdesk,
    …                            ; all 18 OCA repositories, alphabetical
    addons/platform,
    addons/domain/a_service_delivery,
    …                            ; all 11 category directories, alphabetical
```

| # | Rule |
|---|---|
| **`REPO-13`** | Order is **Odoo core → OCA → 1000FiX platform → 1000FiX domain**, always. A custom path before an OCA path is a defect, not a preference |
| **`REPO-14`** | A `cd_*` module may **never** share a technical name with an Odoo or OCA module. `FF-02` checks the `cd_` prefix, which makes collision impossible by construction — this rule states *why* the prefix exists |
| **`REPO-15`** | `addons_path` is **generated** from the tree by `tooling/scripts/gen-addons-path.py`, never hand-maintained. A hand-maintained list drifts the day a category is added |
| **`REPO-16`** | Every environment uses the **same** `addons_path`. Environments differ by configuration and data, never by which code is loadable (TSS §18.4 environment parity) |

**Per-environment configuration**, all in `infra/odoo-conf/`, all layered over `base.conf`:

| File | Environment | Differs by |
|---|---|---|
| `local.conf` | Developer workstation | `--dev=all`, 2 workers, demo data enabled, verbose logging |
| `dev.conf` | CI target | Demo data enabled, test database templates |
| `staging.conf` | UAT / performance | Production worker counts, demo data **off**, masked data (NFR-086c) |
| `training.conf` | Training | Curated data load, demo data off |
| `prod.conf` | Live | Full workers, `list_db = False`, proxy mode, residency service endpoint |
| `dr.conf` | Warm standby | As production, read-only until promotion |

---

## 7. Build Tooling

One tool per stack, chosen for reproducibility, and all four driven from one task runner so that a
developer runs one command regardless of what they changed.

| Stack | Package/dep manager | Lockfile | Task entry point |
|---|---|---|---|
| **Python / Odoo & services** | `uv` | `uv.lock` | `make py.test`, `make py.lint` |
| **TypeScript / Next.js** | `pnpm` workspaces + **Turborepo** *(inherited from `AGENTS.md`)* | `pnpm-lock.yaml` | `pnpm turbo run test` |
| **Dart / Flutter** | `melos` + `fvm` (pinned SDK) | `pubspec.lock` per package, `.fvmrc` | `melos run test` |
| **Go** *(telemetry collector only)* | Go modules | `go.sum` | `go test ./...` |
| **Everything** | — | — | **`make`** — the single entry point |

| # | Rule |
|---|---|
| **`REPO-17`** | Every stack pins its **toolchain version** in-repository — `.python-version`, `.nvmrc`, `.fvmrc`, `go.mod`. "Works on my machine" is a version-pin defect |
| **`REPO-18`** | Lockfiles are committed and are **never** regenerated as a side effect of an unrelated change. A lockfile change is its own commit with its own review (`BE-007` `LX-04`) |
| **`REPO-19`** | `make <target>` works from a clean clone after `make bootstrap`, on every supported platform, for every stack. `BE-001` §7 verifies it |
| **`REPO-20`** | No task exists only in CI. If CI runs it, `make` runs it locally with the same arguments — otherwise the first time a developer sees a failure is after they push |

> **Why `uv` rather than `pip` + `venv`.** 331 CD items across two Python surfaces (Odoo addons and
> standalone services) with a shared library layer need a resolver that is deterministic and a lock
> that is complete. Odoo's own `requirements.txt` is consumed as an input constraint, not as the
> dependency source of truth.

---

## 8. Ownership

`CODEOWNERS` is the mechanism that puts the right reviewer on the right change. With 331 items and
eleven module categories it cannot be hand-maintained.

```
# CODEOWNERS — GENERATED from tooling/cd-register.yaml + AR-006. Do not edit.
/vendor/                                   @chief-architect
/vendor/FORKS.yaml                         @chief-architect @solution-architect
/contracts/                                @solution-architect @integration-lead
/libs/py/fix_residency/                    @security-lead @chief-architect
/libs/dart/fix_offline/                    @mobile-lead @solution-architect
/addons/platform/                          @platform-squad @solution-architect
/addons/domain/a_service_delivery/         @squad-service-delivery
/addons/domain/g_finance/                  @squad-finance @finance-controller
/infra/                                    @platform-engineering
/tooling/fitness/                          @solution-architect
/docs/adr/                                 @chief-architect
```

| # | Rule |
|---|---|
| **`REPO-21`** | `CODEOWNERS` is generated. A hand edit is reverted by the next generation, so the fix is to the register or to `AR-006`, never to the file |
| **`REPO-22`** | Four paths carry a **second, mandatory** reviewer beyond the owning squad: `vendor/`, `contracts/`, `libs/py/fix_residency/` and `addons/domain/g_finance/`. Each is a place where a single-reviewer mistake is expensive and hard to detect later |
| **`REPO-23`** | Every path in the repository resolves to at least one owner. An unowned path fails the ownership check at the wave gate |

> **`libs/py/fix_residency/` deserves the second reviewer on its own.** `FF-09` is the one fitness
> function `AR-012` declares to have **no exemption route**: no residency-classified value may exist
> outside `CD-233`'s successor. A change to the residency client that widens what it returns is a
> statutory breach that looks like a refactor.

---

## 9. Documentation in the Repository

| Content | Location | Rationale |
|---|---|---|
| **Guiding documents** — the 140-document `PGD` estate | `docs/guiding/` *(mirror of `project-guide-doc/`)* | Under version control at last (`PG-M12`). The mirror direction is one-way at initialisation and becomes authoritative afterwards |
| Module and portal specifications | `docs/specs/` *(mirror of `1000fix_ERP_Module/`)* | ibid. |
| ADRs | `docs/adr/` | `AR-004` records, one file per ADR, so a decision is diffable |
| Component READMEs and runbooks | Beside the code, inside the CD item's directory | `BE-006` `CBS-02`; documentation that lives away from code goes stale |
| OpenAPI and event schemas | `contracts/` | `REPO-06` |
| Operational content — SOPs, UI copy, training | **Not in this repository** | `project_content/` is authored and governed by the Content Council under `CG-002`; it is consumed as data, not built as code |

| # | Rule |
|---|---|
| **`REPO-24`** | Engineering documentation is version-controlled in this repository. The current position — 699 files, none under version control — has produced four of the estate's five recurring defect classes (`PG-M12`) |
| **`REPO-25`** | A specification and the code that implements it move in the **same** pull request where the change affects both. This is what a monorepo is for |

---

## 10. What May Never Enter the Repository

| # | Prohibited | Mechanism |
|---|---|---|
| **`REPO-26`** | **Secrets** — credentials, API keys, certificates, connection strings with passwords | `gitleaks` in pre-commit **and** in CI; Vault holds the real values (TSS §18.4, `SC-007`) |
| **`REPO-27`** | **Residency-classified data**, in any form, including in a fixture, a test snapshot or a screenshot | `FF-09`; `NFR-086c`; `db/seeds/` is synthetic-only and generated |
| **`REPO-28`** | **Any personal data**, real or copied from production | `TR-16`; masking runs as part of the clone job, not after it |
| **`REPO-29`** | Build outputs, `node_modules`, `.pyc`, `dist/`, compiled Flutter artefacts | `.gitignore`; CI fails on tracked ignored paths |
| **`REPO-30`** | Large binaries — media, fonts, sample PDFs, database dumps | Git LFS for the small set that is genuinely required (Bengali fonts, `TR-07`); everything else is an artefact-store reference |
| **`REPO-31`** | Generated code that can be regenerated deterministically — API clients, translations `.pot`, `addons_path` | Generated at build; `REPO-06`, `REPO-15` |
| **`REPO-32`** | A second copy of anything in `contracts/` | `REPO-06` |

> **`REPO-27` is not a hygiene rule.** A single NID in a test fixture places residency-classified data
> in every developer's clone, in every CI runner's cache and in every backup of the git host —
> including hosts outside Bangladesh. That is the failure mode TSS §25.5 item 3 names, and a
> repository is the most efficient possible way to reproduce it.

---

## 11. Size, Clone Time and CI Path Filtering

A monorepo's cost is paid at clone and at build. Both are budgeted, and both are measured rather than
assumed.

| Budget | Target | Mitigation when exceeded |
|---|---|---|
| Full clone, cold | **< 10 minutes** on a 20 Mbps connection | Partial clone (`--filter=blob:none`); shallow clone for CI |
| Working-tree size | **< 4 GB** including `vendor/` | LFS for binaries; sparse checkout profiles per role (§11.1) |
| `make bootstrap` on a clean clone | **< 30 minutes** | `BE-001` §7 measures it; container image caching |
| CI feedback on a single-module change | **< 12 minutes** to first failure | Path filtering (§11.2) |

### 11.1 Sparse-checkout profiles

Not every developer needs all 331 items. Profiles are committed in `tooling/sparse/`:

| Profile | Includes |
|---|---|
| `odoo` | `vendor/`, `addons/`, `libs/py/`, `contracts/`, `db/`, `tooling/` |
| `services` | `services/`, `libs/py/`, `contracts/`, `tooling/` |
| `web` | `apps/web/`, `libs/ts/`, `contracts/`, `tooling/` |
| `mobile` | `apps/mobile/`, `libs/dart/`, `contracts/`, `tooling/` |
| `full` | Everything — required for release engineering and for architecture review |

### 11.2 Path filtering

| # | Rule |
|---|---|
| **`REPO-33`** | CI computes the **affected set** from changed paths and the `BE-005` dependency graph, and runs only what is affected — plus the **always-run** set |
| **`REPO-34`** | The always-run set is: `contracts/**`, `libs/**`, `vendor/**`, `tooling/fitness/**`, `CODEOWNERS`, and every lockfile. A change in any of these runs the full suite |
| **`REPO-35`** | Path filtering **never** skips a fitness function that is declared Holistic in `AR-012` §4 — `FF-01`, `FF-03`, `FF-04`, `FF-09`, `FF-13`, `FF-14`, `FF-27`, `FF-29` and the rest. A holistic check that only runs on changed paths is not a holistic check |

> **`REPO-35` is the rule that gets broken first.** Holistic checks are the slow ones, and skipping
> them on "small" changes is the obvious optimisation. `FF-09` — no residency data outside the
> residency service — is holistic precisely because a violation is introduced somewhere other than
> where it is detected.

---

## 12. Enforcement

| Check | What it validates | Where | Blocks |
|---|---|---|:--:|
| `REPO-CHK-01` | Every directory under `addons/`, `services/`, `apps/` has a `component.yaml` naming an issued CD identifier | CI, from `cd-register.yaml` | ✔ |
| `REPO-CHK-02` | Every issued CD identifier has exactly one directory (or two, for "module + service") | CI | ✔ |
| `REPO-CHK-03` | No product code under `vendor/`; no `vendor/` diff without a `FORKS.yaml` entry — `FF-03` | CI | ✔ |
| `REPO-CHK-04` | `addons_path` regenerates identically to the committed file — `REPO-15` | CI | ✔ |
| `REPO-CHK-05` | `CODEOWNERS` regenerates identically; every path has an owner | CI | ✔ |
| `REPO-CHK-06` | Layer placement: no `addons/platform/**` manifest declares a dependency on `addons/domain/**` — `FF-17`, by path | CI | ✔ |
| `REPO-CHK-07` | Secret scan across the full history, not only the diff | Pre-commit + CI | ✔ |
| `REPO-CHK-08` | No tracked file matches an ignore pattern; no file over the LFS threshold outside LFS | CI | ✔ |
| `REPO-CHK-09` | Clone and bootstrap budgets (§11) measured weekly and reported | Scheduled CI | Report |

---

## 13. Day-0 Initialisation

The repository does not exist. Nothing below is a migration; it is a first commit. This is Wave 0
work and it blocks Wave 1.

| Step | Action | Owner | Gate |
|:--:|---|---|---|
| 1 | Create `1000fix-erp`; protect `main` and `develop` per `BE-003` `GW-08` | Engineering Lead | — |
| 2 | Commit the skeleton tree of §4 with `.gitkeep` and a `README.md` per top-level directory | Engineering Lead | — |
| 3 | **Commit the documentation estate first** — `docs/guiding/`, `docs/specs/`. 699 files enter version control before any code does | Enterprise Architecture | Closes `PGD-A2-15` |
| 4 | Add `vendor/odoo` as a submodule pinned to the current 19.0 commit | Platform Engineering | — |
| 5 | Add all 18 OCA repositories as subtrees at their current v19 heads; record every pin in `tooling/versions.lock` | Platform Engineering | `BE-007` `LX-03` |
| 6 | Generate `cd-register.yaml`, `addons_path`, `CODEOWNERS` from `BE-005` | Chief Architect | `BE-005` §11.4 |
| 7 | Commit `.pre-commit-config.yaml`, linter configuration and `Makefile` per `BE-002` | Engineering Lead | `BE-002` §9 |
| 8 | Enable `REPO-CHK-01`…`09` as **Warning**; promote to Blocking at the W1 gate | Platform Engineering | `AR-012` §5.2 |
| 9 | Scaffold the six Wave 1 platform modules from `tooling/generators/` and prove `make bootstrap` end to end | Platform squad | `BE-001` §7 |

> **Step 3 before step 4 is deliberate.** The documentation estate is where four of the five recurring
> defect classes live — stale roll-ups, registers denying work that exists, baseline movement, broken
> links — and all four are mechanically detectable by a pre-commit hook and by nothing else
> (`PG-M12`). It is also the cheapest step, and it is the one that stops the estate moving underneath
> the people counting it. The estate moved from 610 files at 02:06 to 681 at 12:46 to **699 at 13:06
> (+06)** on this single day.

---

## 14. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `BE-004-D-01` | Repository count | (a) Monorepo; (b) polyrepo; (c) monorepo + separate mobile repo | **(a)**, confirming `TD-15` | A single functional change routinely spans three languages and the portal contract | Clone and CI cost, budgeted in §11 |
| `BE-004-D-02` | Odoo core vendoring | (a) submodule; (b) subtree; (c) pip/OCB image | **(a) submodule** | Core is never modified; submodule makes modification awkward, which is the desired ergonomics | Submodule init is a `make bootstrap` step, not optional |
| `BE-004-D-03` | OCA vendoring | (a) submodules ×18; (b) subtrees; (c) pip packages | **(b) subtrees** | 16+ modules need local v19 migration and must be contributable upstream | Larger checkout; `FORKS.yaml` becomes the control |
| `BE-004-D-04` | Addons layout | (a) flat `addons/`; (b) `platform/` + `domain/<category>/` | **(b)** | The path encodes the `AR-007` layer, making `FF-17` checkable before import analysis | Re-categorising a module moves its directory |
| `BE-004-D-05` | Portal placement | (a) here; (b) portal platform repo; (c) deferred | **(c) deferred, with `apps/web/` reserved** | `CON-03` and `IN-002` have not ruled; reserving the path costs nothing and pre-empts nothing | `Q-01`; contract test `PS-11` runs here meanwhile |
| `BE-004-D-06` | Task runner | (a) per-stack native only; (b) `make` over native tools | **(b)** | Four stacks, one command; `REPO-20` keeps CI and local identical | A thin `Makefile` must be maintained |
| `BE-004-D-07` | Documentation location | (a) stays outside VCS; (b) mirrored into the repository | **(b)** | `PG-M12`; the estate has moved five times during authoring | One-way mirror at initialisation, authoritative afterwards |

---

## 15. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | Do the six Next.js portals live here or in the `CON-03` portal platform repository? | Chief Architect / `IN-002` | **W0** | `apps/web/` population; CI ownership; 118 PW of portal build |
| `Q-02` | Which git host, and is it Bangladesh-resident? A repository containing masked-but-derived data has a residency question of its own | CTO / DPO | **W0 — blocking** | `REPO-27`; step 1 of §13 |
| `Q-03` | Which mobile framework (`D-027`)? `apps/mobile/customer/` and `apps/mobile/seller/` cannot be scaffolded until it is answered | CTO | **W0** | `BE-001` toolchain; `libs/dart/` reuse |
| `Q-04` | Is the guiding-document mirror one-way or does `project-guide-doc/` retire at initialisation? | Enterprise Architecture | W1 | `REPO-24`; two sources of truth otherwise |
| `Q-05` | Who owns `libs/ts/ui/` when the portal platform already has a component library? | UX Lead / Engineering Lead | W2 | Duplication across six portals |

---

## 16. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | Every one of the 331 `BE-005` items has an unambiguous directory under §4 | `REPO-02`, `REPO-CHK-01/02` |
| `AC-02` | The four-layer dependency order is expressible as a path predicate | §4, `REPO-03`, `REPO-CHK-06` |
| `AC-03` | `AS-05` is enforceable structurally, not only in CI | §5.1, `vendor/` isolation, `FORKS.yaml` |
| `AC-04` | Every generated artefact is named, with its generator and its check | `addons_path`, `CODEOWNERS`, `cd-register.yaml`, API clients |
| `AC-05` | Budgets exist for clone, bootstrap and CI feedback | §11 |
| `AC-06` | Initialisation is a sequenced, owned plan with a gate per step | §13 |
| `AC-07` | Every prohibition has a mechanism, not only a rule | §10 |

**Definition of done.** Complete when every criterion is met, §13 step 3 has executed (the estate is
under version control), `PGD-000`'s `BE-004` row moves to ✅ with a fresh timestamped enumeration, and
the approver has signed.

---

## 17. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `02-05` `TD-15`, §9 | The monorepo decision this document implements |
| Upstream | `AR-007` §3.1, §3.4 | Module anatomy and layer order the tree makes physical |
| Upstream | `AR-006` | Build sequence and tiering, consumed by `CODEOWNERS` generation |
| Upstream | `BE-005` | Every directory maps to an issued identifier |
| Upstream | `../../../AGENTS.md` | pnpm/Turborepo tooling inherited for the TypeScript estate |
| Downstream | `BE-001` | Bootstraps the tree this document defines |
| Downstream | `BE-002` | Its configuration files live at the paths fixed here |
| Downstream | `BE-003` | Protected branches, `CODEOWNERS`-driven review |
| Downstream | `BE-006` | `component.yaml` at every directory named here |
| Downstream | `BE-007` | Lockfiles and `versions.lock` placed here |
| Downstream | `PE-004` | Path filtering, affected-set computation, pipeline stages |
| Downstream | `AR-012` `FF-03`, `FF-17` | Checked by path before being checked by analysis |
| Lateral | `../../1000fix_ERP_Module/03_Modules/**` | Mirrored into `docs/specs/` |
| Lateral | `../../../Intergrated_web_portal/Technical_documentation_roadmap/Architecture & Infrastructure/IMPL-18_Monorepo_Migration_Architecture_Evolution_Turborepo.md` | In-house monorepo precedent for the TypeScript estate |

---

## 18. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` ·
[`_CATEGORY_OVERVIEW.md`](_CATEGORY_OVERVIEW.md) ·
[`BE-001`](BE-001_Development_Environment_Setup_Guide.md) ·
[`BE-002`](BE-002_Coding_Standards_and_Style_Guide.md) ·
[`BE-003`](BE-003_Git_Workflow_Branching_and_Code_Review_Standard.md) ·
[`BE-005`](BE-005_Custom_Development_CD_Master_Register.md) ·
[`BE-006`](BE-006_Component_Build_Specification_Standard.md) ·
[`BE-007`](BE-007_Dependency_Licence_and_SBOM_Management_Standard.md) ·
`../02_Architecture_and_Design/AR-006_Module_Dependency_Map_and_Build_Sequence.md` ·
`../02_Architecture_and_Design/AR-007_Odoo_Module_Architecture_and_Code_Structure_Standard.md` ·
`../02_Architecture_and_Design/AR-012_Architecture_Compliance_and_Fitness_Function_Standard.md`

**Workspace**
`../../1000fix_ERP_Module/02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md` §9, §10 ·
`../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §3.5, §8.2, §18.1 ·
`../../../AGENTS.md` ·
`../../../Intergrated_web_portal/Technical_documentation_roadmap/Architecture & Infrastructure/IMPL-18_Monorepo_Migration_Architecture_Evolution_Turborepo.md`

**External standards and sources**
ISO 10007:2017 *Configuration management* — verified 2026-08-18 ·
Odoo 19.0 administration documentation, addons path and configuration — verified 2026-08-18 ·
OCA contributing conventions, `OCA/odoo-community.org` `CONTRIBUTING.rst` — verified 2026-08-18 ·
Git subtree and submodule documentation — verified 2026-08-18

---

## 19. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. Tree, vendoring model, addons-path composition, ownership generation, prohibitions, budgets and day-0 initialisation | *(unsigned — no constituted body, `PGD-A1-09`)* |

---

*`BE-004` · Category 07 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
