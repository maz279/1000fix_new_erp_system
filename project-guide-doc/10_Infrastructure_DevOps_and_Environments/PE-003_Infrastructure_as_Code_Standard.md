---
id: PE-003
title: Infrastructure-as-Code Standard
category: 10 — Infrastructure, DevOps & Environments
code: PE
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-19
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Platform Engineering Lead
approver: CTO with Design Authority (constituted under GV-002)
standards_basis: >
  HashiCorp Configuration Language (HCL2) · OpenTofu 1.12 · Semantic Versioning 2.0.0 ·
  CIS Benchmarks · NIST SP 800-190 container security · SLSA build provenance ·
  AR-013 licence-currency rules LW-01…LW-05
traces_to: >
  PGD-000 PE-003 · PE-001 · PE-002 · AR-013 §6 LW-01…LW-05 · BE-004 · BE-007 ·
  Technology Stack §18.4, §18.5 · 02-05 §9 · OPS-02 · NFR-062 · audit OP-02
depends_on: PE-001 · PE-002 · AR-013 · BE-003 · BE-004
verified_on: 2026-08-19
priority: P0
needed_by: W1
enumeration_timestamp: 2026-08-19 01:15 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# PE-003 — Infrastructure-as-Code Standard

### Category 10 · Code `PE` · HCL2 · OpenTofu 1.12 · `AR-013` `LW-01`…`LW-05`

---

> **`PGD-000`'s `PE-003` row states the measurement: "Zero occurrences of 'Terraform' in 601 files."**
> Re-run at **2026-08-19 01:15 (+06)** across 621 files, the count is still **0** — for both
> `terraform` and `opentofu`.
>
> **The register's row also names Terraform, and that naming does not survive the estate's own
> licence policy.** Terraform has been **BUSL 1.1 since v1.6.0**; `AR-013` `LW-01` requires every
> BSL component to carry a **named fallback** and `LW-02` requires architecture approval for a BSL
> addition. **OpenTofu** — the MPL-2.0 fork, Linux Foundation-governed and CNCF-accepted — passes
> `AR-013` `A-01` without an exception at all. §4 rules on it.

---

## 1. Purpose

Six environments built by hand over 36 months will diverge, and **the divergence will be discovered
during an incident** — which is `PGD-000`'s own statement of why this document exists. The estate
now requires **twelve** (`PE-002`), across **three sites** (`PE-001`), and two of the twelve
(`perf`, `migration-staging`) are only affordable because they can be destroyed and rebuilt from
code (`PE-002` §9.3).

This document specifies how infrastructure is expressed as code: the engine and its licence
position, repository and module structure, state management and its blast radius, environment
parameterisation, the review and promotion path, drift detection and what happens when drift is
found, secret handling in IaC, and the policy checks that run before an apply.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | **The engine ruling** — Terraform, OpenTofu, or neither, decided against `AR-013` |
| 2 | Repository placement, and its relationship to `BE-004`'s monorepo |
| 3 | **Module structure** — composition, granularity, versioning, the module registry |
| 4 | **State** — where it lives, how it is locked, how it is split, and why splitting is a safety property |
| 5 | Environment parameterisation for `PE-002`'s twelve |
| 6 | The **plan → review → apply** path, and who may apply what |
| 7 | **Drift detection**, and the rule that makes drift actionable rather than reported |
| 8 | Secrets in IaC — what may and may not appear |
| 9 | **Policy-as-code** gates before apply |
| 10 | Configuration management (Ansible) and the boundary with image building |
| 11 | Bootstrapping — the chicken-and-egg problem nobody writes down |
| 12 | Fitness functions `FF-119`…`FF-127` |

**Explicitly out of scope**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| What infrastructure exists | **`PE-001`**, **`PE-002`** | This document encodes; they design |
| Container image content and orchestration manifests | **`PE-005`** | An image is a build artefact, not an infrastructure resource |
| The pipeline that runs the apply | **`PE-004`** | `PE-004` triggers; this document says what a correct apply is |
| Sizing values | `PE-006` | Inputs to a module, not the module |
| Application configuration and feature flags | **`PE-009`** | Infrastructure config vs application config — §10.3 draws the line |
| Application source repository structure, branching, review | `BE-004`, `BE-003` | §5.1 inherits them |
| Dependency pinning and licence register mechanics | `BE-007` | §4.4 uses its register |
| Secret storage and rotation | `PE-009` | §9 states only what IaC may reference |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| Platform engineers | The whole document |
| **`PE-004` author** | §7's apply path and §11's policy gates are pipeline stages |
| **CTO and Design Authority** | §4 is a licence decision with a four-year horizon |
| `PE-002`, `PE-006` | §6's parameterisation is how twelve environments share one module set |
| Security Lead | §9, §11 |
| Auditors | §7.4 — who applied what, when, and against which plan |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Concept | Conformance | Departure and rationale |
|---|---|---|---|
| **HCL2** | Declarative configuration language | §5's modules | None |
| **OpenTofu 1.12** | IaC engine | §4's ruling; `.tofu`-compatible HCL2 | **The engine choice is the departure from the register's wording** — §4.2 |
| **Semantic Versioning 2.0.0** | Module versioning | §5.4 | None |
| **CIS Benchmarks** | Host and network hardening | Encoded in modules (`PE-001` `HB-01`), checked by §11 policy | None |
| **NIST SP 800-190** | Container security | Referenced; `PE-005` owns it | Boundary, not departure |
| **SLSA** | Build provenance | §12 — provenance for IaC modules, aligning with `BE-007`'s position for application artefacts | Adopted at the level `BE-007` sets |
| **`AR-013` `LW-01`…`LW-05`** | Licence-currency rules | §4 applies them to the engine itself | None — this is the first document to apply them to a **tool** rather than a runtime component |

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| **`AR-013`** §6, `LW-01`…`LW-05`, `A-01` | `../02_Architecture_and_Design/AR-013_*.md` | Every AGPL/BSL/TSL/fair-code component needs a **named fallback**; additions need architecture approval; a component with no fallback may not be `Adopt` |
| `PE-001` | `./PE-001_*.md` | Every resource this standard encodes |
| `PE-002` | `./PE-002_*.md` | Twelve environments; `perf` and `migration-staging` **ephemeral by design** |
| `BE-004` | `../07_Build_Engineering_and_Development_Standards/BE-004_*.md` | Monorepo structure, `FORKS.yaml`, placement rules |
| `BE-003` | Ibid. | Branching, review, merge gates |
| `BE-007` | Ibid. | Pinning, licence register, SBOM, SLSA position |
| Technology Stack §18.4, §18.5 | `../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` | `OPS-02` configuration promoted never hand-edited; pinning; monthly update cadence |
| `02-05` §9 | `../../1000fix_ERP_Module/02_Architecture/02-05_*.md` | Environment triggers and gates |

**Reproducible extraction**, run at **2026-08-19 01:15 (+06)**:

```bash
grep -ril 'terraform'  --include=*.md . | wc -l     # → 0
grep -ril 'opentofu'   --include=*.md . | wc -l     # → 0
grep -ril 'ansible\|pulumi\|cloudformation' --include=*.md . | wc -l   # → 0
find . -type f \( -name '*.tf' -o -name '*.tofu' -o -name '*.yaml' \) \
     -not -path './project-guide-doc/*' | wc -l     # → 0
```

### 2.3 Audit findings this document closes or contributes to

| Finding | Source | Disposition |
|---|---|---|
| `PGD-000` `PE-003` — *"Zero occurrences of Terraform in 601 files. Six environments over 36 months built by hand will diverge"* | `PGD-000` | **Closed as a standard.** The estate now needs twelve environments; §3.2 restates the argument at the true scale |
| **`OP-02` (high)** — `dr` provisioned nowhere | `AUDIT-017` | **Contributes.** `PE-002` `PE-002-D-07`'s warm standby is affordable **only** because compute is scaled from code (§3.2) |
| `AR-013` `LW-01`, `LW-02` | `AR-013` | **Applied to the IaC engine** — §4. First application of the rule to a tool |
| `OPS-02` — configuration promoted, never hand-edited in production | Technology Stack §18.4 | §7, §8 make it mechanical |
| `AR-013` `LW-01` **violation in `AR-013` itself** — Grafana is `Adopt` with no named fallback | `AR-013` §6 | **Raised as `PE-A-02`**; `PE-008` §3.4 supplies the fallback |

---

## 3. Why This Document Exists

### 3.1 The stated argument

`PGD-000`: *"Six environments over 36 months built by hand will diverge, and the divergence will be
discovered during an incident."*

### 3.2 The argument at the real scale

`PE-002` establishes **twelve** environments across **three sites**, and two of them are affordable
only if they are disposable:

| Environment | Why it must be code |
|---|---|
| **`perf`** | Production-scale. **Permanent, it roughly doubles the infrastructure bill**; ephemeral per wave gate, it costs its run time (`PE-002` §9.3) |
| **`migration-staging`** | Production-volume legacy extracts, per migration wave. Same argument |
| **`dr`** | **Warm standby whose compute is scaled at failover.** Built by hand at 02:00, its RTO is days; `NFR-007` says **two hours** (`PE-002` §5.12.1) |
| **`ci`** | Ephemeral per run (`TAF-52`). There is no other way to create one |
| The other eight | Divergence |

> **`PE-003-F-01`. Three of `PE-002`'s twelve environments are not merely easier with IaC — they are
> impossible without it.** `dr` in particular: `NFR-007`'s two-hour RTO is unachievable if the
> standby's compute must be constructed manually. **The IaC standard is therefore a dependency of
> `NFR-007`**, which no document has previously stated.

### 3.3 What this document does not claim

IaC does not prevent misconfiguration; it makes misconfiguration **reviewable, reproducible and
revertible**. A wrong security group in code is still wrong — but it is visible in a diff, applied
identically everywhere, and removable in one change. **That is the whole claim.**

---

## 4. The Engine

### 4.1 The licence position, verified

| Fact | Verified 2026-08-19 |
|---|---|
| **Terraform** | **BUSL 1.1 for v1.6.0 and later.** Source-available, **not** open source. Each release carries a Change Date four years after publication, converting to MPL-2.0. Community-edition commercial use is restricted for those offering competitive services |
| **OpenTofu** | **MPL-2.0.** Forked from Terraform 1.5.7, the last MPL release, in August 2023. Governed by the **Linux Foundation**; accepted into the **CNCF in April 2025**; current stable **v1.12.2** as of June 2026. 140+ corporate backers |

### 4.2 Applying `AR-013` to the engine

`AR-013` `A-01`: *"Licence — permissive, or copyleft with a named fallback. AGPL/BSL/fair-code with
no fallback → **fail**."*

| Candidate | `A-01` | `LW-01` named fallback | `LW-02` architecture approval | Result |
|---|:--:|---|:--:|---|
| **Terraform ≥ 1.6** | **BSL → conditional** | Would have to be **OpenTofu** — the fallback for Terraform is the fork of Terraform | **Required** | Permitted **only** with an approved exception and a named fallback |
| **OpenTofu** | **MPL-2.0 → pass** | Not required. *(Terraform is nonetheless available as a fallback, which is unusual and useful)* | Not required | **Passes cleanly** |
| Pulumi | Apache-2.0 core | Pass | — | Viable, but a general-purpose-language IaC tool raises the review bar for a team of this size |
| CloudFormation / provider-native | Provider-specific | Pass | — | **Fails on portability** — `PE-001` `Q-01` has not chosen a provider, and `BD-R` is a colocation facility, not a hyperscaler |

> **Ruling `PE-003-D-01`. OpenTofu is the IaC engine. Terraform is the named fallback.**
>
> The reasoning is not preference. **`PE-001` `Q-01` has not selected a regional provider, and `BD-R`
> is a Bangladeshi colocation facility that no hyperscaler-native tool addresses.** A provider-neutral
> engine is therefore required on architectural grounds alone. Among provider-neutral engines,
> OpenTofu is the only one that passes `AR-013` `A-01` without an exception, and its configuration
> language is **compatible with the Terraform ecosystem's providers and modules**, so the ecosystem
> argument for Terraform survives the choice.
>
> **`PGD-000`'s `PE-003` row names Terraform.** That row is a description of a gap written before the
> licence position was examined, not a technology decision — and `PE-003` is where the decision was
> always going to be taken. **The register row is corrected at this issue.**

### 4.3 What the ruling costs, stated

| Consideration | Position |
|---|---|
| Provider ecosystem | **Unaffected.** OpenTofu consumes the same provider protocol |
| Module ecosystem | **Largely unaffected**; registry sources are configurable |
| Vendor tooling | Some commercial platforms assume Terraform. **A tool that cannot target OpenTofu is a tool the estate does not adopt** — the same test `AR-013` applies to everything else |
| Hiring | Engineers with Terraform experience are productive immediately; the languages are compatible |
| **Reversibility** | **High.** If OpenTofu were abandoned, Terraform is the fallback and the configuration largely transfers — which is exactly what `LW-01` asks a fallback to mean |

### 4.4 Pinning and currency

| # | Rule |
|---|---|
| **EN-01** | The engine version is **pinned exactly** in `versions.lock` (`BE-007`) and in the `required_version` constraint |
| **EN-02** | **Providers are pinned exactly**, with a lock file committed |
| **EN-03** | Engine and provider updates follow `BE-007`'s **monthly** cadence, applied first to `dev`/`ci` |
| **EN-04** | The engine and every provider appear in the **`BE-007` licence register** and the SBOM |
| **EN-05** | **Licence terms are re-verified at every wave gate** (`AR-013` `LW-04` parity). BUSL Change Dates and MPL status are not permanent facts |

---

## 5. Repository and Module Structure

### 5.1 Placement

> **`PE-003-D-02`. Infrastructure code lives in the monorepo, in a top-level `infrastructure/`
> directory, under `BE-004`'s rules.**

| Option | Assessment |
|---|---|
| A separate infrastructure repository | Makes *"this application change needs this infrastructure change"* a two-repository coordination problem — the exact argument `BE-004` `TD-15` rejects for application code |
| **Monorepo, top-level directory** | ✅ **Chosen.** One review path, one branching model (`BE-003`), atomic cross-cutting changes |
| Inside each module's directory | Infrastructure is estate-wide; scattering it makes the estate un-plannable |

**`infrastructure/` is `CODEOWNERS`-restricted to Platform Engineering** (`BE-003`), because the
review bar differs from application code: an application defect is a bug, an infrastructure defect
is an outage or an exposure.

### 5.2 Layout

```
infrastructure/
├── modules/                     reusable, versioned, no environment knowledge
│   ├── network/                 PE-001 §4–§5: zones, subnets, security groups, egress
│   ├── data/                    PE-001 §4.1 Z3: PostgreSQL, Redis, object storage
│   ├── resident-store/          PE-001 §4.1 Z4 — SEPARATE MODULE, see §5.3
│   ├── ingress/                 PE-001 §6: load balancer, Kong, Nginx, WAF
│   ├── egress/                  PE-001 §6.3: Z6 proxy and allow-list
│   ├── cluster/                 PE-005's orchestration substrate
│   ├── observability/           PE-008's collectors, stores and dashboards
│   ├── secrets/                 PE-009's Vault and its policies
│   └── environment/             composes the above; the only module an env file calls
├── environments/                one directory per PE-002 environment — TWELVE
│   ├── prod/ dr/ staging/ uat/ sit/ perf/ training/
│   ├── migration-staging/ sandbox/ dev/ ci/
│   └── local/                   Docker Compose, not OpenTofu (BE-001)
├── policy/                      §11 policy-as-code
├── bootstrap/                   §13 — state backend, identity, the first apply
└── ansible/                     §10 configuration management
```

### 5.3 Why `resident-store` is its own module

| # | Reason |
|---|---|
| It is deployed to a **different site, in a different jurisdiction**, under a different provider (`PE-001` §3.1) |
| Its state is **separately backed and separately access-controlled** (§6.4) |
| **`FF-114` requires that no non-production environment instantiate it at all** — a separate module makes that a structural check, not a review comment |
| Its key material is separate (`SC-006`), so its provider credentials are separate |

> **The composition rule follows: `environment/` instantiates `resident-store` only for `prod` and
> `dr`.** An environment file that references it is rejected by policy (§11).

### 5.4 Module rules

| # | Rule |
|---|---|
| **MD-01** | A module takes **inputs and returns outputs**. It contains **no environment name and no conditional on one** |
| **MD-02** | Every input has a **type, a description and — where safe — a default**. An input with no description fails review |
| **MD-03** | Modules are **versioned with SemVer** and consumed by version, never by branch |
| **MD-04** | A **breaking module change** (removing an input, changing a default that alters an existing resource, renaming a resource address) is a **major** bump and requires a migration note |
| **MD-05** | **No module creates a resource in more than one logical zone** (`PE-001` §4). A module spanning `Z2` and `Z3` hides the boundary the zone model exists to make visible |
| **MD-06** | Modules are **composable and shallow** — nesting deeper than two levels makes a plan unreadable, and an unreadable plan is an unreviewed plan |
| **MD-07** | Every module ships a `README` stating what it creates, its inputs, its outputs and **its blast radius** |

### 5.5 Naming and tagging

| # | Rule |
|---|---|
| **NT-01** | Every resource is named `1000fix-<environment>-<component>-<n>`. **The environment is in the name of every resource**, so a console view is unambiguous |
| **NT-02** | Every resource carries mandatory tags: `environment`, `owner-role`, `cost-centre`, `data-class`, `managed-by=opentofu`, `module-version` |
| **NT-03** | **`data-class` is mandatory and drives `FF-114`** — a resource tagged `residency-classified` outside `BD-R` fails |
| **NT-04** | **An untagged resource fails policy** (§11) and is reported as drift if it appears at runtime |

> **`NT-02`'s `cost-centre` tag is what makes `PE-006`'s cost model measurable**, and `NT-04` is what
> stops the estate accumulating resources nobody can attribute — the condition in which infrastructure
> spend becomes unauditable.

---

## 6. State

### 6.1 Why state is a safety topic

The state file is **an inventory of the estate and a map of its structure**, and in some providers it
contains resource attributes that are sensitive. Corrupting it can orphan production resources;
losing it can make production unmanageable without a rebuild.

### 6.2 Where it lives

| # | Rule |
|---|---|
| **ST-01** | **Remote backend only.** Local state is forbidden outside `bootstrap/` |
| **ST-02** | **Encrypted at rest**, with versioning enabled on the backing store |
| **ST-03** | **Locking is mandatory.** Two concurrent applies against one state is how resources are destroyed |
| **ST-04** | The backend is **in a separate account from the resources it describes**, so an account compromise does not yield both the estate and its map |
| **ST-05** | State is **backed up on every write**, retained 90 days, and **restore is tested quarterly** — `PE-007` §6 treats it as a first-class recovery object |

### 6.3 Splitting state — a blast-radius decision

> **`PE-003-D-03`. One state per environment per layer, not one state per environment.**

| Layer | Contents | Changes | Blast radius |
|---|---|---|---|
| `00-bootstrap` | State backend, identity, base accounts | Almost never | Total |
| `10-network` | `PE-001` §4–§5 | Rarely | High |
| `20-data` | `Z3` stores | Rarely | **High — destroys data** |
| `25-resident` | **`Z4`, `prod` and `dr` only** | Rarely | **High and regulated** |
| `30-platform` | Cluster, ingress, egress, observability, secrets | Regularly | Medium |
| `40-services` | Application-adjacent resources | Frequently | Low |

**Why split:** a single state means a routine change to `40-services` produces a plan that *could*
destroy the database if a module refactor went wrong. **Splitting makes the dangerous layers rarely
touched and separately permissioned**, and it lets `PE-002`'s ephemeral environments destroy
`40-services` without approaching `20-data`.

**Why not split further:** every split adds a cross-state dependency, and cross-state dependencies
are read at plan time from outputs. **Six layers is the point where the dependency graph is still
readable.**

### 6.4 `25-resident` is special

| # | Rule |
|---|---|
| **RS-01** | Its state lives **in Bangladesh**, with the resources it describes |
| **RS-02** | It is **separately access-controlled**; holding `prod` apply rights grants nothing here (`PE-001` `MA-04`) |
| **RS-03** | It is **instantiated only for `prod` and `dr`**. `FF-114` |
| **RS-04** | Its plans are reviewed by **two approvers**, one of whom is the Security Lead or the DPO |

---

## 7. The Change Path

### 7.1 Plan, review, apply

```
feature branch → automated plan on PR (no credentials that can apply)
      │
      ├─ §11 policy gates       ─── fail → blocked
      ├─ cost estimate           ─── material increase → CFO visibility
      ├─ drift check vs current  ─── drifted → §8
      │
      ▼ human review of THE PLAN, not the diff
   merge → apply to dev → sit → uat/staging → prod (PE-004 promotes)
```

| # | Rule |
|---|---|
| **CP-01** | **The plan is the review artefact, not the code diff.** A three-line variable change can destroy a database; only the plan shows it |
| **CP-02** | The **plan is posted to the pull request** automatically, with resource counts to add, change and **destroy** highlighted |
| **CP-03** | **Any plan that destroys or replaces a resource in `20-data` or `25-resident` requires a second approver** and an explicit acknowledgement |
| **CP-04** | **Apply happens only from the pipeline** (`PE-004`), never from a workstation. `FF-121` |
| **CP-05** | **Apply uses the plan that was reviewed** — a saved plan file, not a re-plan at apply time. A re-plan can differ from what was approved |
| **CP-06** | Production apply requires the change-approval gate (`02-05` §9, `DoD-16`) |
| **CP-07** | **No human holds standing apply credentials for `prod` or `25-resident`** (`PE-001` `MA-01`) |

### 7.2 Who may apply what

| Environment | Apply authority | Approvals |
|---|---|---|
| `local` | The developer | — |
| `ci`, `dev` | Pipeline, automatic on merge | CI green |
| `sit`, `training`, `sandbox` | Pipeline, automatic on merge | CI green + policy |
| `uat`, `staging`, `perf`, `migration-staging` | Pipeline, **manual promotion** | Platform Engineering |
| **`prod`** | Pipeline, **manual gate** | **Platform Engineering + change approval** |
| **`prod` `25-resident`** | Pipeline, **manual gate** | **Two approvers, one Security Lead or DPO** (`RS-04`) |
| **`dr`** | As `prod` | Plus a drill record for a failover-affecting change |

### 7.3 Emergency changes

| # | Rule |
|---|---|
| **EM-01** | An emergency infrastructure change is still **applied from the pipeline**, on a `hotfix/*` branch (`BE-003`) |
| **EM-02** | If the pipeline itself is the outage, **break-glass applies** (`PE-009`), and it is the **only** path that bypasses `CP-04` |
| **EM-03** | **Every break-glass apply is reconciled into code within one working day.** An emergency change that stays out of code is permanent drift with an alibi |
| **EM-04** | Break-glass use triggers a mandatory post-incident review (`OP-016`) |

### 7.4 The audit trail

| Recorded | Where |
|---|---|
| Who approved which plan | Pull request |
| Which plan was applied, and its hash | Pipeline record |
| What changed | State version history |
| Why | The linked change record (`GV-003`) or incident |
| **Every `25-resident` apply** | Additionally in the residency access log (`SC-007`) |

---

## 8. Drift

### 8.1 Detection

| # | Rule |
|---|---|
| **DR-01** | A **scheduled plan runs against every environment daily**, and reports any difference between code and reality |
| **DR-02** | Drift is **an alert with an owner**, not a dashboard number |
| **DR-03** | The drift check runs with **read-only credentials**. A detector that can apply is a scheduled unattended apply |

### 8.2 What happens when drift is found

> **`PE-003-D-04`. Drift is reverted, not adopted — except in `prod` `20-data` and `25-resident`,
> where it is investigated first.**

| Environment / layer | Response |
|---|---|
| `local`, `ci`, `dev`, `sit`, `training`, `sandbox` | **Automatically reverted** on the next scheduled apply |
| `uat`, `staging`, `perf`, `migration-staging` | Alert; reverted within one working day |
| **`prod` `30`/`40`** | Alert; reverted within one working day, or codified through §7 if it was correct |
| **`prod` `20-data`, `25-resident`** | **Alert and investigate before acting.** An automatic revert here could destroy data or breach the residency rule |

> **The exception exists because the safe default is not universally safe.** Reverting drift is
> right almost everywhere; automatically reverting an unexplained change to the production database
> or the resident store is how a recovery action taken during an incident gets undone at 03:00.

### 8.3 Drift is a signal about process

| Drift source | What it means |
|---|---|
| Console change by an engineer | Access is too broad, or the code path is too slow. **Both are process defects** (`OPS-02`) |
| Provider-side change | The provider changed a default. **Pin it explicitly** |
| Another tool | Two systems manage one resource. **Decide which** |
| Break-glass | Expected — and `EM-03` requires reconciliation within one working day |

> **`DR-04`. Recurring drift in one place is a finding, not a chore.** Three occurrences in one
> quarter on the same resource is raised as a process defect at the wave gate.

---

## 9. Secrets in IaC

| # | Rule |
|---|---|
| **SI-01** | **No secret value appears in IaC source, ever.** `NFR-062`, `IP-07`. `FF-122` |
| **SI-02** | IaC references secrets **by vault path**, and the value is injected at apply time (`PE-009`) |
| **SI-03** | **Secrets are not generated by IaC and stored in state.** Generation happens in the secret manager |
| **SI-04** | Where a provider forces a secret through state, the resource is **quarantined into its own state** with tightened access, and it is recorded as a known exposure |
| **SI-05** | **State is treated as sensitive regardless** (§6.2) |
| **SI-06** | Secret scanning runs **pre-commit and in CI** on `infrastructure/` as on all code (`BE-002`, `SC-005` `G-01`) |

> **`SI-04` is stated because `SI-01` alone is not achievable in every provider.** Some resources
> return generated credentials into state. **Pretending otherwise produces a standard nobody can
> follow; naming the exception produces one they can.**

---

## 10. Configuration Management and the Image Boundary

### 10.1 Three mechanisms, three jobs

| Mechanism | Owns | Owned by |
|---|---|---|
| **OpenTofu** | Resources — networks, instances, databases, DNS, policies | This document |
| **Image build** | What is *inside* a container or machine image | `PE-005` |
| **Ansible** | Configuration of things that are **neither** — colocation hardware, appliance-like services, `BD-R` hosts | §10.2 |

### 10.2 Where Ansible is genuinely needed

Most of the estate is containerised (`PE-005`), and configuration management is largely unnecessary
where images are immutable (`PE-001` `HB-02`). **Ansible is retained for a narrow, real case:**

| Case | Why |
|---|---|
| **`BD-R` colocation hosts** | A colocation facility is not an API-driven cloud. Hosts there are provisioned physically and configured, not instantiated |
| Network appliances | Same |
| Bootstrap of the first host in a new site | §13 |

> **`PE-003-D-05`. Ansible is scoped to non-API-driven infrastructure only.** Using it to configure
> containerised workloads would put configuration in two places, which is the condition
> `OPS-02` exists to prevent.

### 10.3 The infrastructure/application configuration boundary

| Concern | Owned by |
|---|---|
| A subnet's CIDR, an instance type, a security-group rule | **`PE-003`** |
| A database's existence, size, backup schedule | **`PE-003`** |
| Which feature flags are on, what a rate limit is, an integration endpoint | **`PE-009`** |
| A secret's **existence and policy** | `PE-003` |
| A secret's **value** | **`PE-009`** |

> **The test: if changing it requires a resource to change, it is `PE-003`'s. If it can change while
> everything keeps running, it is `PE-009`'s.**

---

## 11. Policy as Code

### 11.1 Gates before apply

Policy runs **on the plan**, before apply, in the pipeline (`PE-004`). Failures block.

| # | Policy | Basis |
|---|---|---|
| **PL-01** | No security group permits `0.0.0.0/0` ingress outside `Z0` | `PE-001` `FF-101`, `SG-03` |
| **PL-02** | No resource in `Z2`/`Z3`/`Z5` has a public IP | `PE-001` `HB-03` |
| **PL-03** | Every resource carries the mandatory tag set | `NT-02`, `NT-04` |
| **PL-04** | **No non-`prod`/`dr` environment instantiates `resident-store`** | `RS-03`, `FF-114` |
| **PL-05** | Storage and databases are **encrypted at rest**; `Z4` with separate key material | `NFR-061`, `SC-006` |
| **PL-06** | No secret literal appears in the plan | `SI-01`, `FF-122` |
| **PL-07** | Environment CIDRs do not overlap | `PE-001` `FF-102` |
| **PL-08** | No non-production environment has a route to `Z3`/`Z4` production | `PE-001` `EP-03` |
| **PL-09** | Backup retention meets `PE-007`'s minimum for the resource's data class | `PE-007` |
| **PL-10** | **A plan that destroys a `20-data` or `25-resident` resource carries the second-approver acknowledgement** | `CP-03` |
| **PL-11** | Engine and provider versions match `versions.lock` | `EN-01`, `EN-02` |
| **PL-12** | Cost delta above a threshold requires CFO visibility | `PE-006`, `GV-008` |

### 11.2 Exemptions

| Rule | Detail |
|---|---|
| Who grants | **Design Authority**, for policy; Security Lead for `PL-01`, `PL-02`, `PL-05`, `PL-06` |
| Recorded | Rule, reason, compensating control and **expiry date** |
| Maximum | **One wave** |
| On expiry | **Lapses.** No automatic renewal — the same rule `IN-005` §12.2 sets |

---

## 12. Provenance and Supply Chain

| # | Rule |
|---|---|
| **PV-01** | Modules are consumed **by version from an internal registry**, not from public sources at apply time |
| **PV-02** | A third-party module is **vendored and reviewed** before use, under `BE-004`'s fork rules and `BE-007`'s licence register |
| **PV-03** | Providers are verified against **published checksums**; the lock file is committed |
| **PV-04** | IaC build provenance follows `BE-007`'s SLSA position — **the same level as application artefacts, not a lower one** |
| **PV-05** | The `infrastructure/` tree is in scope for `BE-007`'s SBOM |

> **`PV-01` matters more than it looks.** A public module resolved at apply time means **the estate's
> production topology is defined partly by a third party's latest commit.** Vendoring is not
> conservatism; it is the difference between a reproducible apply and a hopeful one.

---

## 13. Bootstrapping

**The problem nobody writes down:** state lives in a remote backend, the backend is infrastructure,
and infrastructure is built from state.

| # | Rule |
|---|---|
| **BS-01** | `bootstrap/` creates **only**: the state backend, its encryption key, the pipeline's identity and the base account structure |
| **BS-02** | It is the **only** place a local state file is permitted, and that file is **committed encrypted** with a documented recovery path |
| **BS-03** | It is applied **once per site**, by a named engineer, with a recorded session (`NFR-070`) |
| **BS-04** | Immediately after, its state is **migrated into the backend it created**, and the local copy is destroyed |
| **BS-05** | **Bootstrap is rehearsed** in a scratch account before it is run against a real site — including for `BD-R`, where the provider differs |
| **BS-06** | The bootstrap procedure is part of **`PE-007`'s recovery documentation**: rebuilding the estate from nothing starts here |

> **`BS-06` is the reason bootstrap is specified rather than improvised.** `PE-007`'s worst-case
> scenario — account compromise, `BKP-3` restore — begins with an empty account and no state backend.
> **If nobody has written down how the first apply works, the recovery has no first step.**

---

## 14. Fitness Functions

Allocation confirmed by enumerating every `FF-nn` definition across all authored categories at
**2026-08-19 01:15 (+06)**, per `PGD-AUDIT-007` `PGD-A7-01`.

| # | Check | Scope | Timing | Enforcement |
|---|---|---|---|---|
| **FF-119** | Every resource in every environment is managed by IaC — **no unmanaged resource exists** | All | Daily reconciliation | **Fail** |
| **FF-120** | Daily drift check reports zero unexplained drift outside the §8.2 exception layers | All | Daily | **Alert**; gate blocker if sustained |
| **FF-121** | **No apply originates outside the pipeline**, except a recorded break-glass | All | Audit log | **Fail** |
| **FF-122** | No secret literal appears in `infrastructure/` source or in a plan | All | Pre-commit + CI | **Fail** |
| **FF-123** | Engine and provider versions match `versions.lock` in every environment | 12 | CI | **Fail** |
| **FF-124** | Every module consumed is a **pinned version from the internal registry** | All | CI | **Fail** |
| **FF-125** | Every resource carries the mandatory tag set, including `data-class` | All | CI + runtime | **Fail** |
| **FF-126** | **State backup restore is verified quarterly** | 6 layers × sites | Quarterly | **Fail** |
| **FF-127** | Every break-glass apply is reconciled into code **within one working day** | Per event | Weekly | **Fail** |

---

## 15. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `PE-003-D-01` | **The IaC engine** | Terraform (BUSL) · **OpenTofu (MPL-2.0)** · Pulumi · provider-native | **OpenTofu** | `PE-001` `Q-01` has not chosen a provider and `BD-R` is colocation, so provider-neutrality is architectural. Among neutral engines, only OpenTofu passes `AR-013` `A-01` without an exception; the provider and module ecosystem transfers | **`PGD-000`'s `PE-003` row is corrected.** Terraform is the named fallback (`LW-01`) |
| `PE-003-D-02` | Repository placement | Separate repo · **monorepo `infrastructure/`** · per-module | **Monorepo** | Application and infrastructure changes are routinely one change; `BE-004` `TD-15`'s argument applies unchanged | `CODEOWNERS`-restricted to Platform Engineering |
| `PE-003-D-03` | State granularity | One per environment · **one per environment per layer (6)** · one per resource group | **Six layers** | Makes dangerous layers rarely touched and separately permissioned, and lets ephemeral environments destroy `40-services` without approaching `20-data` | §6.3; `25-resident` separately controlled |
| `PE-003-D-04` | Drift response | Always revert · always investigate · **revert, except `prod` `20-data`/`25-resident`** | **Revert with an exception** | Auto-reverting an unexplained production database change could undo an incident action at 03:00 | §8.2 |
| `PE-003-D-05` | Ansible scope | Everything · none · **non-API-driven infrastructure only** | **Narrow** | Configuring containerised workloads with Ansible puts configuration in two places — what `OPS-02` forbids | `BD-R` hosts, appliances, bootstrap |
| `PE-003-D-06` | Apply origin | Workstation permitted · **pipeline only, with break-glass** | **Pipeline only** | An apply from a laptop has no reviewed plan, no audit trail and no policy gate | `CP-04`, `FF-121`, `EM-02` |
| `PE-003-D-07` | Third-party modules | Resolve at apply · **vendor and review** | **Vendor** | A public module resolved at apply time makes the production topology partly a third party's latest commit | `PV-01`, `PV-02` |
| `PE-003-D-08` | Review artefact | The code diff · **the plan** | **The plan** | A three-line variable change can destroy a database, and only the plan shows it | `CP-01`, `CP-02`, `CP-05` |

---

## 16. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| **Q-01** | **Is `PE-003-D-01` ratified?** Every module in §5.2 is written against an engine, and rewriting later is a full-estate change | **Design Authority + CTO** | **W0 — blocking** | All of §5, `PE-004` |
| **Q-02** | **Which regional provider?** (`PE-001` `Q-01`) Modules are provider-neutral in structure but not in resource types | CTO | **W0 — blocking** | §5.2 |
| **Q-03** | Does `BD-R`'s facility offer an **API** for provisioning, or is it Ansible-and-hands? (§10.2) | Platform Engineering Lead | **W1** | `resident-store` module, `BS-05` |
| **Q-04** | Which **policy engine** implements §11, and does it target OpenTofu plans? | Platform Engineering Lead | **W1** | §11, `PE-004` |
| **Q-05** | Is there an **internal module registry**, or is vendoring into the monorepo the mechanism? (`PV-01`) | Platform Engineering Lead | W1 | §12 |
| Q-06 | Who holds **break-glass apply** authority, and how many people? (`EM-02`, `PE-009`) | CTO + Security Lead | W1 | §7.3, `PE-009` |
| Q-07 | Does the estate's IaC fall in scope for `BE-007`'s SBOM tooling as written, or does it need a second toolchain? | Platform Engineering with `BE-007` owner | W2 | `PV-05` |

---

## 17. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | The pre-existing state is **measured** | §2.2 — 0 occurrences of any IaC tool in 621 files |
| AC-02 | The engine is chosen **against the estate's own licence rules**, not by preference | §4.2, `PE-003-D-01` |
| AC-03 | The cost of the choice is stated, including reversibility | §4.3 |
| AC-04 | Module structure prevents cross-zone and cross-residency composition **structurally** | §5.3, `MD-05`, `PL-04` |
| AC-05 | State granularity is a **blast-radius** decision with the reasoning shown | §6.3 |
| AC-06 | The review artefact is the **plan**, and destructive plans need a second approver | `CP-01`, `CP-03` |
| AC-07 | Drift has a response **per environment and layer**, including where the safe default is unsafe | §8.2 |
| AC-08 | Secrets in IaC are ruled, **including the case the rule cannot cover** | §9, `SI-04` |
| AC-09 | The infrastructure/application configuration boundary has a **one-sentence test** | §10.3 |
| AC-10 | **Bootstrapping is specified**, and tied to `PE-007`'s recovery | §13, `BS-06` |
| AC-11 | Every licence and version claim carries a verification date | §4.1, §19 — all 2026-08-19 |
| AC-12 | Fitness-function allocation was enumerated before allocation | §14 |

**Definition of done.** Complete when every criterion is met, **Q-01 and Q-02 are decided**,
`bootstrap/` has been applied and rehearsed for both sites, `FF-119`…`FF-127` are enabled, and
`PGD-000`'s `PE-003` row carries a fresh enumeration timestamp **and its Terraform wording is
corrected**.

---

## 18. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | **`PE-001`** | Every resource this standard encodes |
| Upstream | **`PE-002`** | Twelve environments = twelve parameter sets; three of them **impossible without IaC** |
| Upstream | **`AR-013`** `LW-01`…`LW-05`, `A-01` | The licence rules §4 applies to the engine |
| Upstream | `BE-003`, `BE-004`, `BE-007` | Branching and review; monorepo placement; pinning, licence register, SBOM, SLSA |
| Downstream | **`PE-004`** | §7's apply path and §11's policy gates are pipeline stages |
| Downstream | **`PE-005`** | The cluster module; the image boundary in §10.1 |
| Downstream | **`PE-006`** | `NT-02`'s `cost-centre` tag makes the cost model measurable |
| Downstream | **`PE-007`** | `dr` scale-on-failover; state backup as a recovery object; `BS-06` |
| Downstream | **`PE-009`** | §10.3's boundary; `SI-02`'s vault references |
| Downstream | `SC-005` | IaC scanning is one of its CI gates |
| Lateral | `../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §18.4, §18.5 | `OPS-02`, pinning, monthly cadence |
| Lateral | `../../1000fix_ERP_Module/02_Architecture/02-05_*.md` §9 | Environment triggers and gates |

---

## 19. References

**Within this repository**
[`../PGD-000_Master_Register_of_Project_Guiding_Documents.md`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md) ·
[`./_CATEGORY_OVERVIEW.md`](./_CATEGORY_OVERVIEW.md) ·
[`./PE-001_Infrastructure_and_Network_Architecture_Design.md`](./PE-001_Infrastructure_and_Network_Architecture_Design.md) ·
[`./PE-002_Environment_Strategy_and_Specification.md`](./PE-002_Environment_Strategy_and_Specification.md) ·
[`./PE-004_CI_CD_Pipeline_Design_Specification.md`](./PE-004_CI_CD_Pipeline_Design_Specification.md) ·
[`./PE-005_Containerisation_and_Orchestration_Design.md`](./PE-005_Containerisation_and_Orchestration_Design.md) ·
[`./PE-007_Backup_Disaster_Recovery_and_Business_Continuity_Design.md`](./PE-007_Backup_Disaster_Recovery_and_Business_Continuity_Design.md) ·
[`./PE-009_Configuration_and_Secrets_Management_Standard.md`](./PE-009_Configuration_and_Secrets_Management_Standard.md) ·
[`../02_Architecture_and_Design/AR-013_Technology_Radar_and_Build_vs_Buy_Register.md`](../02_Architecture_and_Design/AR-013_Technology_Radar_and_Build_vs_Buy_Register.md) ·
[`../07_Build_Engineering_and_Development_Standards/BE-004_Repository_and_Monorepo_Structure_Standard.md`](../07_Build_Engineering_and_Development_Standards/BE-004_Repository_and_Monorepo_Structure_Standard.md) ·
[`../07_Build_Engineering_and_Development_Standards/BE-007_Dependency_Licence_and_SBOM_Management_Standard.md`](../07_Build_Engineering_and_Development_Standards/BE-007_Dependency_Licence_and_SBOM_Management_Standard.md)

**Workspace**
`../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §18.4, §18.5 ·
`../../1000fix_ERP_Module/02_Architecture/02-05_*.md` §9 ·
`../../project_content/_AUDIT/AUDIT-017_*.md` `OP-02`

**External sources**

| Source | What it establishes | Verified |
|---|---|---|
| **HashiCorp Terraform LICENSE** | **BUSL 1.1 scoped to v1.6.0 and later**; Change Date four years per release; Change Licence MPL-2.0; community-edition commercial restrictions for competitive services | 2026-08-19 |
| **OpenTofu** | **MPL-2.0**; forked from Terraform 1.5.7 in August 2023; **Linux Foundation** governance; **accepted into the CNCF April 2025**; current stable **v1.12.2** (June 2026); 140+ corporate backers | 2026-08-19 |
| HashiCorp Configuration Language (HCL2) | The configuration language both engines consume | 2026-08-19 |
| Semantic Versioning 2.0.0 | Module versioning | 2026-08-19 |
| CIS Benchmarks | Host and network hardening baselines | 2026-08-19 |
| NIST SP 800-190 | Container security (referenced; `PE-005` owns) | 2026-08-19 |
| SLSA | Build provenance levels | 2026-08-19 |

---

## 20. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-19 | Platform Engineering | Initial issue against **0 occurrences of any IaC tool in 621 files**. **Rules the engine as OpenTofu with Terraform as the named fallback** (`PE-003-D-01`), applying `AR-013` `LW-01`/`A-01` to a tool for the first time — Terraform has been **BUSL 1.1 since v1.6.0** and would require an exception the estate's own policy makes avoidable. **Corrects `PGD-000`'s `PE-003` row**, which names Terraform. Establishes six state layers as a blast-radius decision, a drift response with a stated exception where the safe default is unsafe, and **specifies bootstrapping** — the first step of `PE-007`'s worst-case recovery, previously written down nowhere. Records that **three of `PE-002`'s twelve environments are impossible without IaC**, making this standard a dependency of `NFR-007` (`PE-003-F-01`) | *Pending — CTO; `GV-002` not constituted* |

---

*`PE-003` · Category 10 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
