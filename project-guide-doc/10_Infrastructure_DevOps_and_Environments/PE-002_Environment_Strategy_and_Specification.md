---
id: PE-002
title: Environment Strategy & Specification
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
  ISO/IEC/IEEE 42010:2022 deployment viewpoint (via AR-001 §8.5) ·
  ISO/IEC/IEEE 29119-2:2021 test environment requirements · ITIL 4 service environments ·
  Twelve-Factor App §10 dev/prod parity · PDPA 2026 (Ordinance 23 of 2026) non-production constraints
traces_to: >
  PGD-000 PE-002 · AR-001 §8.5 · 02-05 §9 · TS-001 §4.7 · QA-001 · QA-005 §11 ·
  MG-005 · IN-008 §6 · SC-007 §9 · audit OP-02, AP-12 ·
  NFR-007, NFR-049, NFR-051, NFR-071, NFR-086c, OPS-02
depends_on: PE-001 · AR-001 · SC-007 · QA-001 · MG-005 · IN-008
verified_on: 2026-08-19
priority: P0
needed_by: W1
enumeration_timestamp: 2026-08-19 01:15 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# PE-002 — Environment Strategy & Specification

### Category 10 · Code `PE` · ISO/IEC/IEEE 29119-2:2021 · Twelve-Factor §10

---

> **The measurement this document exists for, taken 2026-08-19 01:15 (+06):**
>
> | Source | Environments named | The names |
> |---|---:|---|
> | `02-05` §9 and `AR-001` §8.5 | **6** | `local` · `dev` · `staging` · `training` · `prod` · `dr` |
> | **`TS-001` §4.7** | **6** | `DEV` · `CI` · `SIT` · `UAT` · `PERF` · `TRAIN` |
> | **Members common to both** | **2** | `dev` · `training`/`TRAIN` |
> | Added later by `AP-12` / `IN-008` §6 | 1 | `sandbox` |
> | Added later by `MG-005` | 1 | `migration-staging` |
> | **Distinct environments the estate actually requires** | **12** | |
> | **Provisioned** | **0** | `TS-001` `O-03` |
>
> **Two documents each say the estate has six environments, and they agree on two of them.**
> Neither is wrong: `02-05` lists a *deployment* ladder and `TS-001` lists a *test* ladder. Nobody
> reconciled them, and every downstream document has been planning against whichever it read first.

---

## 1. Purpose

An environment is not a copy of production with a different name. It is a **contract**: a stated
purpose, a data class, a refresh policy, an access model, a lifetime and an owner. Without that
contract, environments multiply, diverge, hold data they should not, and become the reason a release
behaves differently in production than in test.

This document publishes the **single environment inventory** for the programme, reconciling the two
six-environment lists that currently coexist; specifies each environment against ten attributes;
fixes the **data class rules** that `NFR-071` and `NFR-086c` make non-negotiable; sequences
provisioning against the waves that need each; and states the cost the register does not carry.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | **The reconciliation** — one inventory replacing three partial ones |
| 2 | The **twelve environments**, specified against ten attributes each |
| 3 | **Data class per environment**, and the two absolute rules |
| 4 | Refresh, reset and freeze policy — including **who may freeze what** |
| 5 | Access model and account boundaries |
| 6 | **Lifetime** — which environments are permanent, which are ephemeral, which are per-cycle |
| 7 | Environment parity, and the parity that is deliberately **not** maintained |
| 8 | **Provisioning sequence**, against the wave that first consumes each |
| 9 | **Cost**, including the two lines `GV-008` explicitly excludes |
| 10 | Decommissioning |
| 11 | Fitness functions `FF-111`…`FF-118` |

**Explicitly out of scope**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| Network topology, addressing, placement | **`PE-001`** §5, §10 | This document says *which* environments exist; `PE-001` says *where* they may sit |
| The IaC that builds them | **`PE-003`** | One module set, parameterised per environment |
| Promotion between them | **`PE-004`** | A pipeline concern |
| Sizing arithmetic and growth | **`PE-006`** | This document states the *shape* of each environment; `PE-006` publishes the numbers |
| DR procedure, drills, failover | **`PE-007`** | `dr` is specified here; **operating it is `PE-007`** |
| Test data generation | `QA-004` | This document states the data *class*; `QA-004` produces the data |
| Test levels and what runs where | `QA-001`, `QA-005` | Consumed here as the requirement |
| Local developer workstation setup | `BE-001` | `local` is specified here as an environment; `BE-001` sets it up |
| Migration rehearsal procedure | `MG-005` | `migration-staging` is specified here; `MG-005` runs the rehearsal |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| **`PE-003`, `PE-004`, `PE-006` authors** | The inventory is their parameter set, promotion path and sizing denominator |
| Platform engineers | §5's specifications are the build list |
| **QA Lead** | §4's reconciliation is the answer to `TS-001` `O-03`, and §5 gives every test level a home |
| Migration lead | `migration-staging` (§5.11) finally has an owning design |
| CFO | §9 — two environment classes are outside `GV-008`'s infrastructure line |
| DPO and Legal Counsel | §6 — the two absolute data rules and how they are enforced |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Concept | Conformance | Departure and rationale |
|---|---|---|---|
| **ISO/IEC/IEEE 42010:2022** | Deployment viewpoint | Inherits `AR-001` §8.5's ladder and **extends it from six to twelve**, with the extension justified per environment | The extension is a correction, not a departure — §4 shows the ladder was incomplete |
| **ISO/IEC/IEEE 29119-2:2021** | Test environment requirements | §5 specifies each test environment against the attributes the standard requires: purpose, data, configuration, access, availability | None |
| **Twelve-Factor App §10** | Dev/prod parity | §7 — same images, configuration-only differences | **Deliberate departure on *scale*.** Parity of *shape* is maintained; parity of *size* is not, and §7.2 says why |
| **ITIL 4** | Service environments | Environment as a managed configuration item with an owner and a lifecycle | None |
| **PDPA 2026** (Ordinance 23 of 2026) | Non-production data | §6's two absolute rules | **Statutory currency:** the instrument is the Personal Data Protection Ordinance 2025 as amended by Ordinance No. 23 of 2026 — see `PE-001` §17 and `PGD-AUDIT-007` `PGD-A7-07` |

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| `AR-001` §8.5 | `../02_Architecture_and_Design/AR-001_*.md` | The six-name deployment ladder with data and refresh per environment |
| `02-05` §9 | `../../1000fix_ERP_Module/02_Architecture/02-05_*.md` | The same six names; CD triggers and gates per environment |
| **`TS-001` §4.7** | `../../project_content/13_Test_and_Acceptance_Content/TS-001_*.md` | **A different six**, with the `SIT`/`UAT`/`TRAIN` separation argument — and `O-03`: *"none is specified or provisioned"* |
| `QA-001`, `QA-005` §11.2 | `../08_Quality_Engineering_and_Test/` | Thirteen test levels; five execution profiles; `TAF-52`…`TAF-59` |
| **`MG-005`** | `../09_Data_Migration_and_Cutover/MG-005_*.md` | `migration-staging` as a **production-class** environment, distinct from `staging` |
| **`IN-008` §6** | `../04_Integration_and_API_Engineering/IN-008_*.md` | `SANDBOX` as a seventh environment with a **synthetic-only** data rule |
| `SC-007` §9 | `../05_Security_Privacy_and_Compliance/SC-007_*.md` | The `Z4` DR options; the `dr` environment's residency constraint |
| `PE-001` §10 | `./PE-001_*.md` | Placement, account boundaries and address blocks per environment |
| `AUDIT-017` `OP-02` | `../../project_content/_AUDIT/AUDIT-017_*.md` | **`dr` is named in the architecture and sized nowhere** |
| `AUDIT-016` `AP-12` | Ibid. | The partner sandbox is a seventh environment `TS-001` §4.7 does not have |

**Reproducible extraction**, run at **2026-08-19 01:15 (+06)**:

```bash
# Every backticked environment token across the four repositories
grep -rhoiE '`(local|dev|ci|sit|uat|perf|staging|training|train|prod|production|dr|sandbox|migration-staging)`' \
  --include=*.md . | tr 'A-Z' 'a-z' | sed 's/`//g' | sort | uniq -c | sort -rn
#   → 14 tokens; normalising train/training and prod/production → 12 distinct environments
```

### 2.3 Audit findings this document closes or contributes to

| Finding | Source | Disposition |
|---|---|---|
| **`OP-02` (high)** — the `dr` environment is *"named in the architecture and provisioned nowhere"*; `02-05` §9 lists six and §8.1 sizes five | `AUDIT-017` | **Contributes decisively.** §5.12 specifies `dr`; §9 costs it. Closes with `PE-001` §3 (the site) and `PE-007` (the procedure) |
| **`AP-12` (medium)** — the partner sandbox is a seventh environment `TS-001` §4.7 does not have | `AUDIT-016` | **Closed.** `sandbox` is §5.10 of a **twelve**-environment inventory. `TS-001` §4.7 is superseded by §4.4's ruling — the amendment `AP-010` `O-03` asks for |
| **`TS-001` `O-03`** — *"none of the six is specified or provisioned"* | `TS-001` | **The specification half is closed** by §5. Provisioning is `Q-01` |
| `QA-001` §10.5, `QA-006` — nine of thirteen test levels rest on environments that do not exist | Category 08 | §5 gives every level a home; §8 sequences provisioning ahead of the wave that needs it |
| `MG-005` — *"`migration-staging` must be sized by `PE-002`"* | Category 09 | §5.11 |
| `GV-008` `Q-03` — what does a Bangladesh-resident store cost? | `GV-008` | §9.2 gives the shape; `PE-006` the figure |

---

## 3. What an Environment Is

### 3.1 The ten attributes

Every environment in §5 is specified against all ten. **A missing attribute is a defect**, and an
attribute that reads "as production" is a defect too — it is the sentence that produces an unmasked
clone.

| # | Attribute | Why it must be stated |
|---|---|---|
| 1 | **Purpose** | One sentence. An environment with two purposes gets neither right — the `SIT`/`UAT` argument in §4.3 |
| 2 | **Data class** | §6. The single most consequential attribute |
| 3 | **Refresh policy** | What replaces the data, how often, and from where |
| 4 | **Freeze policy** | Who may stop it changing, and for how long |
| 5 | **Access model** | Who reaches it, with what authentication |
| 6 | **Lifetime** | Permanent · per-cycle · ephemeral |
| 7 | **Scale** | Relative to production, with the reason |
| 8 | **Availability expectation** | And explicitly whether it is covered by any SLO |
| 9 | **Owner** | A **role**, accountable for its state |
| 10 | **First consumed at** | The wave that makes it necessary — which sets provisioning order |

### 3.2 The three classes

| Class | Environments | Governed as |
|---|---|---|
| **Production-class** | `prod` · `dr` · **`migration-staging`** | Production access control, change control, audit logging and monitoring. **Regardless of whether they hold live data** |
| **Controlled** | `staging` · `uat` · `perf` · `training` · `sit` | Managed configuration, promoted changes, masked data, no ad-hoc access |
| **Open** | `local` · `dev` · `ci` · **`sandbox`** | Fast, resettable, synthetic data only. **`sandbox` is open internally and externally exposed**, which is why its data rule is the strictest of all |

> **`migration-staging` is production-class and that is not intuitive.** It holds masked production
> data at production volume, and `MG-005` classifies it so. **The reason is that a migration
> rehearsal that runs under weaker controls than the real cutover has not rehearsed the cutover.**

---

## 4. The Reconciliation

### 4.1 The problem, precisely

| List | Source | Names | Character |
|---|---|---|---|
| **A** | `02-05` §9, `AR-001` §8.5 | `local` · `dev` · `staging` · `training` · `prod` · `dr` | A **deployment** ladder — where code goes |
| **B** | `TS-001` §4.7 | `DEV` · `CI` · `SIT` · `UAT` · `PERF` · `TRAIN` | A **test** ladder — where levels execute |

**They intersect in two members.** List A has no `ci`, `sit`, `uat` or `perf`; list B has no `local`,
`staging`, `prod` or `dr`.

> **`PE-002-F-01`. Neither list is wrong and their coexistence is.** An engineer reading `02-05` §9
> builds a pipeline that promotes `dev → staging → prod` and has nowhere to run `TS-006`…`TS-012`.
> An engineer reading `TS-001` §4.7 provisions `SIT` and `UAT` and has nowhere to run a release
> candidate. **`QA-001` and `QA-005` planned against list B; `PE-004`'s promotion path and
> `RL-002`'s release process will plan against list A.** The divergence is invisible until two teams
> discover they built for different ladders.

### 4.2 The ruling

> **Ruling `PE-002-D-01`. One inventory of twelve environments. Lists A and B are both superseded,
> and `staging` is retained as a distinct environment from `sit` and `uat`.**

| # | Environment | From | Rationale for inclusion |
|---|---|---|---|
| 1 | `local` | A | Developer workstation. `BE-001` |
| 2 | `dev` | **A ∩ B** | Shared integration target for `develop` |
| 3 | `ci` | B | **Ephemeral per run.** `TAF-52` requires an ephemeral PostgreSQL per run — this is not `dev` |
| 4 | `sit` | B | System integration test across real modules. `QA-001` `TS-003`–`TS-005` |
| 5 | `uat` | B | **Frozen** during a cycle. `TX-08` voids a script whose expected results were not written first |
| 6 | `perf` | B | **Production-shaped volumes.** `NFR-053`, `NFR-054`; `DoD-14` requires 1.5× peak |
| 7 | `staging` | A | **Release candidate rehearsal**, production-shaped configuration. §4.3 |
| 8 | `training` | **A ∩ B** | Trainees destroy data by design. Resettable per cohort |
| 9 | **`sandbox`** | `AP-12`, `IN-008` §6 | **Externally reachable, externally credentialled, synthetic only** |
| 10 | **`migration-staging`** | `MG-005` | **Production-class** migration rehearsal at production volume |
| 11 | `prod` | A | Live |
| 12 | `dr` | A | Warm standby. `NFR-007` |

### 4.3 Why `staging`, `sit` and `uat` are three environments and not one

The costliest decision in this document, so the argument is stated rather than assumed.

| | `sit` | `uat` | `staging` |
|---|---|---|---|
| Answers | *"Do the modules work together?"* | *"Does the business accept it?"* | *"Will this release deploy cleanly?"* |
| Data | Full `TS-002` set, **moving** | Full `TS-002` set, **frozen for the cycle** | **Production clone, masked** |
| Configuration | Test-shaped | Test-shaped | **Production-shaped** |
| Changes | Continuously | **Frozen** | Per release candidate |
| Who drives | Engineering | **Business super-users** | Release management |

**`TS-001` §4.7 already argued two of the three separations** — *"`SIT` and `UAT` cannot be the same
environment… `TRAIN` cannot be `UAT` either"* — and this document adds the third: **`staging` cannot
be `uat`**, because a release rehearsal needs production-shaped configuration and a production-shaped
data clone, and a UAT cycle needs neither and is voided by both.

> **The compression that will be proposed, and the answer.** Under budget pressure the natural
> proposal is to merge `sit` and `staging`. **`PE-002-D-02`: they may be merged only after the W4
> gate, and only if UAT cycles have never contended with SIT.** Merging them at W1 means the first
> release rehearsal happens on an environment that is mid-integration-test, and the first time that
> matters is the first production deployment.

### 4.4 What must change upstream

| # | Document | Change | Owner |
|---|---|---|---|
| **RC-01** | `TS-001` §4.7 | Replace the six-environment table with a reference to this inventory. **This is `AP-010` `O-03` and `AP-12`'s remediation** | QA Lead (Category 13) |
| **RC-02** | `02-05` §9 | Correct the `Environments` row from six names to twelve, or reference this document | Enterprise Architecture |
| **RC-03** | `AR-001` §8.5 | Extend the ladder table to twelve rows | Enterprise Architecture |
| **RC-04** | `02-05` §8.1 | Add the environment dimension the sizing table lacks, and the **resident store line** (`PGD-A3-05`) | Enterprise Architecture with `PE-006` |

---

## 5. The Twelve Environments

### 5.1 `local`

| Attribute | Value |
|---|---|
| **Purpose** | Developer workstation — write and run code without shared infrastructure |
| **Data class** | **Synthetic fixtures only** |
| Refresh | On demand, by the developer |
| Freeze | n/a |
| Access | The developer. **No shared credential exists** |
| Lifetime | Ephemeral, per developer |
| Scale | Single-node Docker Compose (`BE-001`) |
| Availability | None |
| **Owner** | The developer |
| **First consumed** | **W0** |

**Placement:** `172.20.0.0/16`, deliberately outside the programme reservation, so a laptop cannot
route to a real environment (`PE-001` `AP-02`).

### 5.2 `ci`

| Attribute | Value |
|---|---|
| **Purpose** | Automated verification per commit and per pull request |
| **Data class** | **Fixtures, generated** — `QA-004` generator snapshot (`TAF-52`) |
| Refresh | **Per run.** Ephemeral PostgreSQL 16 per run, torn down after |
| Freeze | n/a |
| Access | The pipeline's service identity only. **No human logs in** |
| Lifetime | **Ephemeral — minutes** |
| Scale | Small, **parallel** (`TAF-53`) |
| Availability | Pipeline availability, not a service SLO |
| **Owner** | Platform Engineering |
| **First consumed** | **W0** — before the first feature merge |

> **`ci` is not `dev`.** `TAF-52` requires an ephemeral database seeded per run; a shared `dev`
> database makes test results order-dependent and is the most common cause of a suite that passes
> alone and fails in CI.

### 5.3 `dev`

| Attribute | Value |
|---|---|
| **Purpose** | Shared integration target for `develop`; the first place code from several developers meets |
| **Data class** | **Synthetic + anonymised sample** |
| Refresh | On every merge to `develop` (`02-05` §9) |
| Freeze | Never |
| Access | Engineering; SSO, no production credentials |
| Lifetime | Permanent |
| Scale | Minimal — **one node per component**, no HA |
| Availability | Best effort; **no SLO**, and engineering is told so |
| **Owner** | Engineering Lead |
| **First consumed** | **W0** |

### 5.4 `sit`

| Attribute | Value |
|---|---|
| **Purpose** | System integration test across real modules and real external sandboxes — `QA-001` `TS-003`–`TS-005`, `IN-008` L4 |
| **Data class** | **Full `TS-002` set**, masked |
| Refresh | Per release; **data moves continuously** |
| Freeze | Never — that is what `uat` is for |
| Access | Engineering + QA |
| Lifetime | Permanent |
| Scale | **Shape parity, not size parity** — every component present, minimum instances |
| Availability | Working hours; no SLO |
| **Owner** | QA Lead |
| **First consumed** | **W1** |

**External counterparties:** `sit` calls **counterparty sandboxes**, never production (`IN-008` §6.4).

### 5.5 `uat`

| Attribute | Value |
|---|---|
| **Purpose** | Business acceptance — `TS-006`–`TS-012`, `TS-016` |
| **Data class** | Full `TS-002` set, masked |
| Refresh | Per wave |
| **Freeze** | **Frozen for the duration of a UAT cycle.** Only the QA Lead may lift it |
| Access | **Business super-users** + QA |
| Lifetime | Permanent |
| Scale | Shape parity |
| Availability | Business hours during a cycle; **a `uat` outage during a cycle is an incident**, because super-user time is the scarcest resource in the programme (`GV-007`: 134–201 super-users) |
| **Owner** | QA Lead with the Business Owners Forum |
| **First consumed** | **W1** |

> **The freeze is the whole point.** `TX-08` voids a script whose expected results were not written
> before execution. **A partner or an engineer changing `uat` mid-cycle voids the cycle**, which is
> exactly why `AP-12` ruled that partners cannot use `uat` as a sandbox.

### 5.6 `perf`

| Attribute | Value |
|---|---|
| **Purpose** | Performance and load testing — `TS-014`, `DoD-14`'s **1.5× expected peak** |
| **Data class** | **Production-shaped volumes**, masked — `NFR-053` 5 M orders/year, `NFR-054` 5 M assets |
| Refresh | Per wave gate |
| Freeze | During a test run |
| Access | QA + Platform Engineering |
| Lifetime | **Per wave gate — provisioned, used, destroyed** |
| **Scale** | **The only non-production environment sized at production scale**, and only for the components under test |
| Availability | On demand |
| **Owner** | QA Lead with Platform Engineering |
| **First consumed** | **W2** |

> **`perf` is ephemeral by design and that is the cost decision.** A permanently-running
> production-scale environment roughly doubles the infrastructure bill. **Provisioned per gate from
> IaC** (`PE-003`), it costs its run time — which is only possible because `PE-003` exists. §9.3.

### 5.7 `staging`

| Attribute | Value |
|---|---|
| **Purpose** | **Release-candidate rehearsal** — the last stop before `prod`, with production-shaped configuration |
| **Data class** | **Production clone, PII-masked** — masked **inside the clone job** (`NFR-086c`) |
| Refresh | **Weekly** (`AR-001` §8.5) |
| Freeze | During a release candidate |
| Access | Engineering + Release Management; **production-class change control** |
| Lifetime | Permanent |
| Scale | **Configuration parity with production; reduced instance counts** |
| Availability | Working hours + release windows |
| **Owner** | Release Manager |
| **First consumed** | **W1** |

**Deployment rehearsal happens here or it does not happen.** `DoD-16` requires a **rehearsed**
rollback, and `staging` is where it is rehearsed.

### 5.8 `training`

| Attribute | Value |
|---|---|
| **Purpose** | Super-user and end-user training; `TR-003` `DS-14` screenshots |
| **Data class** | **Curated scenario data** — not a production clone. Scenarios must be *teachable*, which real data is not |
| Refresh | **Per cohort**, resettable |
| Freeze | During a cohort |
| Access | Trainers + trainees; throwaway accounts |
| Lifetime | Permanent, reset frequently |
| Scale | Minimal |
| Availability | Training-hours only |
| **Owner** | Change & Adoption Lead |
| **First consumed** | **W2** |

> **Trainees destroy data by design** (`TS-001` §4.7). Reset must be a **one-click, ten-minute**
> operation or trainers will avoid it and cohort *n+1* will train on cohort *n*'s wreckage.

### 5.9 `migration-staging`

| Attribute | Value |
|---|---|
| **Purpose** | **Migration rehearsal and dress rehearsal at production volume** — `MG-005` |
| **Data class** | **Masked production-volume legacy extracts.** Encrypted and access-logged under `SC-010` |
| Refresh | Per rehearsal cycle |
| Freeze | During a rehearsal |
| Access | **Production-class** — production access control, audit logging, change control (`MG-005`) |
| Lifetime | **Per migration wave** |
| **Scale** | **Production volume** — a rehearsal at 10% volume rehearses nothing about duration |
| Availability | On demand, during rehearsal windows |
| **Owner** | Migration Lead with Platform Engineering |
| **First consumed** | **W2** |

> **`migration-staging` is never `staging`** (`MG-005`). A migration rehearsal takes hours to days,
> holds a full legacy extract, and must not block the release path for its duration.

### 5.10 `sandbox`

| Attribute | Value |
|---|---|
| **Purpose** | **External partner integration development and certification** — `FR-IPF-019`, `IN-008` §6 |
| **Data class** | **Synthetic only.** Not masked, not pseudonymised, not a subset — `IN-008` `SB-01` |
| Refresh | Base set per wave; **per-partner reset on demand** |
| Freeze | Never |
| **Access** | **External**: 17+ brand partners, 500–2,000 sellers, corporate and courier developers. Partner-held credentials, `sandbox` rate-limit class |
| Lifetime | Permanent |
| Scale | Minimal; **partner-tenant isolated** |
| Availability | **Best effort, explicitly outside production SLOs — and partners are told so** |
| **Owner** | Integration Architect with Platform Engineering |
| **First consumed** | **W3** — the courier integrations (`IN-008` §12 `T-02`) |

**Placement:** its **own cloud account**, externally reachable, with **no network path to any other
environment** (`PE-001` `EP-02`).

> **The data rule is stricter than `NFR-071` and the reason is the access population.** Masked data
> is re-identifiable given auxiliary information, and thousands of external developers are precisely
> that condition. **Synthetic-only removes the question** (`IN-008` §6.3).

### 5.11 `prod`

| Attribute | Value |
|---|---|
| **Purpose** | Live service |
| **Data class** | **Live.** Residency-classified data **in `Z4` only** |
| Refresh | n/a |
| Freeze | **Change freeze at wave cutover** and during declared blackout windows (`MG-006`) |
| Access | **No standing administrative access** (`PE-001` `MA-01`); break-glass per `PE-009` |
| Lifetime | Permanent |
| Scale | `PE-006` |
| **Availability** | `NFR-006` ≥ 99.9% business hours · `NFR-045` ≥ 99.7% 24×7 · `NFR-046` portal ≥ 99.9% · `NFR-048` payment ≥ 99.95% (`PE-001` §9.1) |
| **Owner** | Head of Service with Platform Engineering |
| **First consumed** | **W1** |

**Placement:** `RGN-P` **and** `BD-R` — production is **two sites**, because `Z4` is not in `RGN-P`.

### 5.12 `dr`

| Attribute | Value |
|---|---|
| **Purpose** | **Warm standby** for site loss — `NFR-007` RPO ≤ 15 min, RTO ≤ 2 h |
| **Data class** | **Live, replicated.** Regional tier → `RGN-S`; **`Z4` → a Bangladesh-resident standby, never regionally** (`SC-007-DR-1`) |
| Refresh | **Continuous replication** |
| Freeze | n/a |
| Access | Break-glass and drills only |
| Lifetime | Permanent |
| **Scale** | **Minimal standing compute, data fully replicated, scaled on failover.** §5.12.1 |
| Availability | Measured as **replication lag** and **drill outcome**, not uptime |
| **Owner** | Platform Engineering Lead |
| **First consumed** | **W2** — the first drill must precede the W2 gate (`OP-02`) |

#### 5.12.1 What "warm" means, quantified

`OP-02` records that `dr` *"appears in no sizing table, no cost progression and no infrastructure
line."* Here is its shape — the numbers are `PE-006`'s:

| Element | Standing state | On failover |
|---|---|---|
| Data — regional | **Fully replicated, continuously.** Streaming replication, RPO ≤ 15 min | Promoted |
| Data — `Z4` | **Fully replicated to the in-country standby** | Promoted |
| Compute | **Minimal** — enough to run replication and health checks | **Scaled from IaC** (`PE-003`) to production shape |
| Network | Provisioned and addressed (`PE-001` §5.2, `10.65.0.0/16`) | Routed |
| **Backups** | **`BKP-3` immutable copy outside the primary account** | Restore source of last resort |

> **This is why `PE-003` is a `dr` dependency and not merely good practice.** A warm standby whose
> compute is scaled *from code* at failover costs a fraction of a hot standby. **A warm standby whose
> compute must be built by hand at 02:00 has an RTO measured in days**, and `NFR-007` says two hours.

#### 5.12.2 The `Z4` DR position, restated because it is unresolved

`SC-007` §9.4 sets out options A (provision an in-country DR target), B (obtain the Authority's
written position) and C (accept that `NFR-007` does not apply to residency-classified data), and
records that **C is the current position by default, not by decision**.

`PE-001` §3.3 names **three certified in-country facilities**, so option A is procurable.

> **`PE-002-F-02`. Until `Q-01` is decided, `dr` is specifiable but not provisionable for `Z4`, and
> the estate's DR RAG status is red** — which `OP-012` §3 `HC-01` already requires to be reported
> monthly to the Steering Committee. **Availability reporting must state the `Z4` RTO separately**
> (`SC-007` §9.5), because a green estate-level RTO conceals an unbounded one.

---

## 6. Data Class Rules

### 6.1 The two absolute rules

| # | Rule | Source | Enforcement |
|---|---|---|---|
| **DC-01** | **No non-production environment contains unmasked personal data.** Ever | `NFR-071` | `FF-113` |
| **DC-02** | **No non-production environment contains residency-classified data, masked or not, in any region.** Masking runs **inside** the clone job, so an unmasked clone cannot exist even briefly | **`NFR-086c` — absolute** | `FF-114` |

> **`DC-02` is stronger than `DC-01` and the difference matters.** `DC-01` permits masked personal
> data in `staging`. `DC-02` permits **nothing** from `Z4` anywhere outside `Z4` — not masked, not
> hashed, not a subset. A masked NID is still an NID that was copied.

### 6.2 The class per environment

| Environment | Live | Masked production | Synthetic | Curated | Legacy extract |
|---|:--:|:--:|:--:|:--:|:--:|
| `local` | | | ✔ | | |
| `ci` | | | ✔ | | |
| `dev` | | | ✔ | | |
| `sit` | | ✔ | ✔ | | |
| `uat` | | ✔ | | | |
| `perf` | | ✔ | ✔ | | |
| `staging` | | ✔ | | | |
| `training` | | | | ✔ | |
| `migration-staging` | | ✔ | | | **✔** |
| **`sandbox`** | | | **✔ only** | | |
| `prod` | ✔ | | | | |
| `dr` | ✔ | | | | |

### 6.3 The clone job

The single most dangerous scheduled job in the estate: it reads production and writes elsewhere.

| # | Rule |
|---|---|
| **CJ-01** | It runs in **`Z5`** and writes only to the target environment's account |
| **CJ-02** | **Masking happens inside the job**, between read and write. There is **no intermediate unmasked artefact** — not a file, not a table, not a snapshot |
| **CJ-03** | It **cannot read `Z4`**. `Z4` is not in its source set, and `PE-001` `NR-02` prevents it structurally |
| **CJ-04** | Its output is **verified**: a post-clone scan asserts zero unmasked personal-data patterns before the environment is released for use (`FF-113`) |
| **CJ-05** | A failed verification **destroys the target**, it does not quarantine it |
| **CJ-06** | Every run is logged with source, target, row counts and verification outcome |

---

## 7. Parity

### 7.1 What is held identical

| # | Rule |
|---|---|
| **PA-01** | **The same container images** run in every environment. Only configuration differs (`02-05` §9, Twelve-Factor §10) |
| **PA-02** | The same **IaC modules** build every environment, parameterised (`PE-003`) |
| **PA-03** | The same **PostgreSQL major version** everywhere. A version difference between `staging` and `prod` invalidates the rehearsal |
| **PA-04** | The same **migration path**: every environment reaches its schema by running the same forward-only migrations |
| **PA-05** | `staging`, `migration-staging` and `prod` hold **configuration parity** — same feature-flag defaults, same integration mode |

### 7.2 What is deliberately not held identical

| Difference | Environments | Why |
|---|---|---|
| **Instance counts and sizes** | All non-production except `perf` | Size parity across eleven environments multiplies the bill by an order of magnitude for no defect-finding value |
| **HA topology** | All non-production except `staging` | A single node is adequate to find functional defects |
| **External counterparties** | All non-production | **Counterparty sandboxes, never production** — `IN-008` §6.4 |
| **Data volume** | All except `perf` and `migration-staging` | Volume matters for performance and migration duration, and for little else |
| **`Z4`** | All non-production | `DC-02` |

> **`PA-06`. Where parity is not held, the difference is *declared*, not discovered.** Each
> environment's specification in §5 states its scale explicitly. **A defect that reproduces only in
> production is investigated against this list first**, because the list is the complete set of ways
> the environments differ.

---

## 8. Provisioning Sequence

### 8.1 The rule

> **`PE-002-D-03`. An environment is provisioned one wave before the wave that first consumes it.**

This is deliberate. `AUDIT-016` `AP-03` found **eight of twelve `AP` content files registered after
the wave that first consumed them, six of them needed at W1**, and called it *"the sixth consecutive
category with the same defect."* The same discipline `IN-008` §12 applied is applied here.

### 8.2 The sequence

| Wave | Provisioned | First consumed at | Driver |
|:--:|---|:--:|---|
| **W0** | `local`, `ci`, `dev` | W0 | Nothing can be built without them |
| **W0** | **`staging`** | W1 | The first release rehearsal is the W1 deployment |
| **W0** | **`prod` (`RGN-P` + `BD-R`)** | W1 | `HA-01` requires the four total-outage components HA **from W1** |
| **W1** | `sit`, `uat` | W1 | `QA-001` levels; UAT cycles begin in W1 |
| **W1** | **`dr` (`RGN-S` + `BD-R` standby + `BKP-3`)** | **W2** | **First drill must precede the W2 gate** (`OP-02`, `NFR-051`) |
| **W1** | `sandbox` | W3 | Courier partner onboarding (`IN-008` `T-02`) |
| **W1** | `migration-staging` | W2 | `MG-005` rehearsal |
| **W1** | `training` | W2 | First super-user cohort |
| **W2** | `perf` (first instantiation) | W2 | `DoD-14` at the W2 gate |

### 8.3 What this means in practice

**Eight of twelve environments must exist by the end of Wave 1**, and `GV-004` records Wave 1 as
already over-committed at **5.33×**.

> **`PE-002-F-03`. Environment provisioning is Wave 0 work that appears in no plan.** `QA-001` and
> `QA-005` reached the same conclusion from the test side and asked for **`PE-002` and `PE-004` as
> Wave 0**. `AR-001` §11.3 says *"Wave 1 is an infrastructure wave, and must be resourced as one."*
> **Three documents have now said this independently.** Referred to `GV-004` and `GV-007`; `Q-02`.

---

## 9. Cost

### 9.1 What the register carries, and what it excludes

`GV-008` §4.3 carries infrastructure at **$52K–$96K over three years**, from `02-05` §8.2, with a
recorded caveat: *"sized for the `SB-2` scope and for a single region. `CON-13` split residency adds
a Bangladesh-resident store that is not in this figure."* `GV-008-D-03` records that re-deriving it
requires `PE-001`–`PE-006`.

**Three lines are outside that figure:**

| # | Line | Why it is absent | Owner |
|---|---|---|---|
| **1** | **`BD-R`** — the Bangladesh-resident store, production **and** standby, plus in-country key custody | `02-05` §8.2 predates the split-residency decision. `GV-008` `Q-03` asks for it | `PE-006` |
| **2** | **`dr`** — `RGN-S` standing compute, replication egress, and **`BKP-3`** | **`OP-02`: `dr` appears in no cost progression** | `PE-006` |
| **3** | **Non-production environments** — eleven of them | `02-05` §8.2 is a **production** progression. It carries no environment dimension at all | `PE-006` |

> **`PE-002-F-04`. `02-05` §8.2's cost progression is a production-only figure being read as a total
> infrastructure figure.** `GV-008` inherited it with caveats pointing upward, and this document is
> the first to state that **eleven of the twelve environments are absent from it entirely**.

### 9.2 The shape of the three lines

Numbers are `PE-006`'s; the drivers are fixed here:

| Line | Driver | Relative scale |
|---|---|---|
| `BD-R` production + standby | **Availability and key custody, not volume** (`AR-001` §8.6) | Small compute, **disproportionate key-custody cost** |
| `dr` regional | **Data replication is continuous; compute is minimal** and scaled on failover (§5.12.1) | Storage-dominated |
| `BKP-3` | Object storage with **retention lock**, outside the primary account | Storage + egress |
| Non-production, eleven | Mostly small; **`perf` and `migration-staging` are the exceptions** | §9.3 |

### 9.3 The two expensive non-production environments, and how they are made cheap

| Environment | Why it is expensive | The mechanism |
|---|---|---|
| **`perf`** | **Production-scale by definition** — `DoD-14` requires 1.5× expected peak | **Ephemeral.** Provisioned from IaC per wave gate, destroyed after. Costs its run time, not its calendar |
| **`migration-staging`** | **Production-volume legacy extracts** | **Per migration wave**, not permanent. Destroyed between waves |

> **Both mechanisms depend entirely on `PE-003`.** An environment that can be rebuilt from code in
> an hour can be destroyed; an environment built by hand cannot, and will run permanently because
> nobody dares delete it. **This is the strongest cost argument for IaC in the programme**, and it is
> the argument `PE-003` §3.2 makes from the other direction.

---

## 10. Lifecycle and Decommissioning

| # | Rule |
|---|---|
| **LC-01** | Every environment has a **named owner role** (§5) and appears in a register with its state |
| **LC-02** | An environment is created **only** from IaC (`PE-003`). **A hand-built environment is not an environment; it is a liability with a hostname** |
| **LC-03** | **Ephemeral environments have a maximum lifetime enforced by automation** — `ci` minutes, `perf` per gate, `migration-staging` per wave. **Expiry destroys, it does not warn** |
| **LC-04** | Decommissioning **destroys data before releasing infrastructure**, and the destruction is evidenced (`DA-006`) |
| **LC-05** | An environment nobody has used for **one wave** is reviewed for decommissioning at the wave gate |
| **LC-06** | **Every environment carries a visible banner naming itself** in the UI. The `PE-009` configuration hierarchy supplies it |

> **`LC-06` is not cosmetic.** The estate has twelve environments, eleven holding masked or synthetic
> data and one live. **A super-user who cannot tell which one they are in will eventually enter real
> customer data into `training` or test data into `prod`**, and both failures are discovered late.

---

## 11. Fitness Functions

Allocation confirmed by enumerating every `FF-nn` definition across all authored categories at
**2026-08-19 01:15 (+06)**, per `PGD-AUDIT-007` `PGD-A7-01`.

| # | Check | Scope | Timing | Enforcement |
|---|---|---|---|---|
| **FF-111** | Every environment in the register exists in IaC state, and every IaC-managed environment is in the register | 12 | CI | **Fail** |
| **FF-112** | No environment is running an image tag that differs from the one promoted to it (`PA-01`) | 12 | Runtime | **Fail** |
| **FF-113** | **Post-clone verification finds zero unmasked personal-data patterns** before a target is released for use | Every clone | Per clone job | **Fail — destroys the target** |
| **FF-114** | **No non-production environment holds any residency-classified field**, and no clone job's source set includes `Z4` | All non-prod | CI + runtime | **Fail** |
| **FF-115** | Every environment runs the same PostgreSQL major version as `prod` (`PA-03`) | 12 | Weekly | **Fail** |
| **FF-116** | Every ephemeral environment older than its maximum lifetime is destroyed | `ci`, `perf`, `migration-staging` | Hourly | **Destroy** |
| **FF-117** | Every environment renders its identifying banner (`LC-06`) | 12 | Smoke test | **Fail** |
| **FF-118** | `dr` replication lag is within `NFR-007`'s RPO for **both** the regional tier and `Z4` | `dr` | Continuous | **Alert**, and a gate blocker if sustained |

---

## 12. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `PE-002-D-01` | The inventory | `02-05`'s six · `TS-001`'s six · **one reconciled twelve** | **Twelve** | The two lists share two members and neither supports the other's consumers | `TS-001` §4.7, `02-05` §9 and `AR-001` §8.5 all require correction (§4.4) |
| `PE-002-D-02` | `sit` and `staging` | Merge · **separate, mergeable after W4** | **Separate** | A release rehearsal on a mid-integration-test environment first matters at the first production deployment | §4.3; reviewed at the W4 gate |
| `PE-002-D-03` | Provisioning timing | With the wave that needs it · **one wave ahead** | **One wave ahead** | `AP-03`'s defect, six consecutive categories | §8.2; **eight environments by end of W1** |
| `PE-002-D-04` | `perf` lifetime | Permanent · **ephemeral per wave gate** | **Ephemeral** | Production-scale and permanent is the single largest avoidable infrastructure cost | Depends on `PE-003`; §9.3 |
| `PE-002-D-05` | `sandbox` data | `NFR-071` masking · **synthetic only** | **Synthetic only** | Masked data is re-identifiable, and the access population is thousands of external developers | `IN-008` `SB-01`; `FF-113` |
| `PE-002-D-06` | `migration-staging` class | Controlled · **production-class** | **Production-class** | A rehearsal under weaker controls than the cutover has not rehearsed the cutover | `MG-005`; §3.2 |
| `PE-002-D-07` | `dr` standing compute | Hot · **warm, scaled from IaC on failover** · cold | **Warm** | Meets RTO ≤ 2 h at a fraction of hot cost — **but only because the compute is code** | §5.12.1; a hard `PE-003` dependency |
| `PE-002-D-08` | Environment banners | Optional · **mandatory in every environment** | **Mandatory** | Twelve environments, eleven non-live; a super-user who cannot tell will eventually confuse them | `LC-06`; `FF-117` |

---

## 13. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| **Q-01** | **Is `BD-R` procured, closing `SC-007` §9.4 option A?** Until it is, `dr` is not provisionable for `Z4` and DR RAG is red | **CTO + CFO** | **W1** | `OP-01`, `OP-02`, `NFR-007` for `Z4`, `PE-007` |
| **Q-02** | **Is Wave 0 environment provisioning funded and staffed?** Eight of twelve by end of W1, into a wave already 5.33× over-committed | **Programme Director** | **W0 — blocking** | Everything |
| **Q-03** | Does the QA Lead accept the `TS-001` §4.7 supersession (`RC-01`)? It is a Category 13 change this document cannot make | QA Lead | **W1** | `AP-12`, `AP-010` `O-03` |
| **Q-04** | How many **cloud accounts** does `EP-01` imply, and what does the account structure cost to operate? | Platform Engineering Lead | W1 | `PE-001` `Q-05`, §9 |
| **Q-05** | Who owns the **clone job** operationally — Platform, QA, or Data? It reads production and writes elsewhere | CTO | **W1** | §6.3 |
| **Q-06** | Is `perf` genuinely destroyable between gates, or does test-data build time make it permanent in practice? | QA Lead + Platform | W2 | §9.3, `PE-002-D-04` |
| Q-07 | Does `training` need **cohort-parallel** instances, or does serial reset suffice at the planned cohort rate? | Change & Adoption Lead | W2 | §5.8 |

---

## 14. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | The environment inventory is **measured across the estate**, not taken from one document | §2.2 extraction; the opening table — 12 distinct, 0 provisioned |
| AC-02 | The two six-environment lists are **reconciled**, with the overlap counted | §4.1, §4.2 — **2 members in common** |
| AC-03 | Every environment is specified against **all ten attributes** | §5.1–§5.12 |
| AC-04 | The `sit`/`uat`/`staging` separation is **argued**, and the compression that will be proposed is answered in advance | §4.3, `PE-002-D-02` |
| AC-05 | Data class rules are stated as **two absolute rules** with the difference between them explained | §6.1 |
| AC-06 | The clone job — the estate's most dangerous scheduled job — is designed | §6.3 |
| AC-07 | Parity is stated **both ways**: what is identical and what deliberately is not | §7 |
| AC-08 | **`dr` is specified and shaped**, closing the specification half of `OP-02` | §5.12, §5.12.1 |
| AC-09 | Provisioning is sequenced **one wave ahead**, avoiding `AP-03` | §8.2, `PE-002-D-03` |
| AC-10 | The **three cost lines the register excludes** are named | §9.1; `PE-002-F-04` |
| AC-11 | The upstream corrections this reconciliation requires are listed with owners | §4.4 `RC-01`…`RC-04` |
| AC-12 | Fitness-function allocation was enumerated before allocation | §11 |

**Definition of done.** Complete when every criterion is met, **Q-01 and Q-02 are answered**,
`RC-01`…`RC-04` are applied upstream, `FF-111`…`FF-118` are enabled, the twelve environments are
provisioned per §8.2, and `PGD-000`'s `PE-002` row carries a fresh enumeration timestamp.
**`OP-02` closes only when `dr` is provisioned and drilled — not on issue of this document.**

---

## 15. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | **`PE-001`** §5, §10 | Address blocks and placement per environment |
| Upstream | **`AR-001`** §8.5 | The six-name ladder this extends to twelve |
| Upstream | **`SC-007`** §9 | The `Z4` DR options constraining `dr` |
| Upstream | `QA-001`, `QA-005` §11.2 | Test levels and profiles each environment must host |
| Upstream | `MG-005` | `migration-staging`'s production-class classification |
| Upstream | `IN-008` §6 | `sandbox`'s synthetic-only rule |
| Downstream | **`PE-003`** | Twelve environments = one module set, twelve parameter files |
| Downstream | **`PE-004`** | The promotion path runs across this inventory |
| Downstream | **`PE-006`** | §9's three cost lines are its to quantify |
| Downstream | **`PE-007`** | `dr`, `BKP-3` and the drill |
| Downstream | **`PE-009`** | Configuration hierarchy is keyed on environment; `LC-06`'s banner |
| Downstream | `QA-006`, `RL-002`, `SV-*` | All plan against this inventory |
| Lateral | `../../project_content/13_Test_and_Acceptance_Content/TS-001_*.md` §4.7 | **Superseded by §4.2** — `RC-01` |
| Lateral | `../../1000fix_ERP_Module/02_Architecture/02-05_*.md` §8.2, §9 | Cost progression and the six-name row — `RC-02`, `RC-04` |

---

## 16. References

**Within this repository**
[`../PGD-000_Master_Register_of_Project_Guiding_Documents.md`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md) ·
[`./_CATEGORY_OVERVIEW.md`](./_CATEGORY_OVERVIEW.md) ·
[`./PE-001_Infrastructure_and_Network_Architecture_Design.md`](./PE-001_Infrastructure_and_Network_Architecture_Design.md) ·
[`./PE-003_Infrastructure_as_Code_Standard.md`](./PE-003_Infrastructure_as_Code_Standard.md) ·
[`./PE-004_CI_CD_Pipeline_Design_Specification.md`](./PE-004_CI_CD_Pipeline_Design_Specification.md) ·
[`./PE-006_Capacity_Plan_and_Performance_Engineering_Baseline.md`](./PE-006_Capacity_Plan_and_Performance_Engineering_Baseline.md) ·
[`./PE-007_Backup_Disaster_Recovery_and_Business_Continuity_Design.md`](./PE-007_Backup_Disaster_Recovery_and_Business_Continuity_Design.md) ·
[`./PE-009_Configuration_and_Secrets_Management_Standard.md`](./PE-009_Configuration_and_Secrets_Management_Standard.md) ·
[`../02_Architecture_and_Design/AR-001_Software_Architecture_Document.md`](../02_Architecture_and_Design/AR-001_Software_Architecture_Document.md) ·
[`../05_Security_Privacy_and_Compliance/SC-007_Data_Residency_and_Cross_Border_Transfer_Design.md`](../05_Security_Privacy_and_Compliance/SC-007_Data_Residency_and_Cross_Border_Transfer_Design.md) ·
[`../04_Integration_and_API_Engineering/IN-008_Integration_Test_Sandbox_and_Certification_Specification.md`](../04_Integration_and_API_Engineering/IN-008_Integration_Test_Sandbox_and_Certification_Specification.md) ·
[`../09_Data_Migration_and_Cutover/MG-005_Mock_Migration_and_Dress_Rehearsal_Plan.md`](../09_Data_Migration_and_Cutover/MG-005_Mock_Migration_and_Dress_Rehearsal_Plan.md)

**Workspace**
`../../1000fix_ERP_Module/02_Architecture/02-05_*.md` §8.2, §9 ·
`../../project_content/13_Test_and_Acceptance_Content/TS-001_*.md` §4.7 ·
`../../project_content/_AUDIT/AUDIT-017_*.md` `OP-02` ·
`../../project_content/_AUDIT/AUDIT-016_*.md` `AP-03`, `AP-12` ·
`../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §18.3

**External sources**

| Source | Verified |
|---|---|
| ISO/IEC/IEEE 29119-2:2021 — test environment requirements | 2026-08-19 |
| Twelve-Factor App §10 — dev/prod parity | 2026-08-19 |
| ITIL 4 — service environments as managed configuration items | 2026-08-19 |
| Personal Data Protection Ordinance 2025, as amended by Ordinance No. 23 of 2026 | 2026-08-19 |

---

## 17. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-19 | Platform Engineering | Initial issue. **Reconciles two six-environment inventories that share two members** into a single inventory of **twelve environments, of which zero are provisioned** (`PE-002-F-01`). Specifies each against ten attributes, argues the `sit`/`uat`/`staging` separation and answers the compression that will be proposed under budget pressure. States the two absolute data rules and designs the clone job. **Specifies and shapes `dr`, closing the specification half of `OP-02`**, and records that `Z4` DR remains unprovisionable until `SC-007` §9.4 option A is chosen. Sequences provisioning **one wave ahead**, and names the **three cost lines `02-05` §8.2 excludes** — including all eleven non-production environments (`PE-002-F-04`) | *Pending — CTO, QA Lead; `GV-002` not constituted* |

---

*`PE-002` · Category 10 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
