---
id: BE-003
title: Git Workflow, Branching & Code Review Standard
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
  Conventional Commits 1.0.0 · Semantic Versioning 2.0.0 · OCA commit conventions ·
  DORA / Accelerate delivery-performance findings · NIST SP 800-218 (SSDF) PO.3, PS.1, PW.7, PW.8
traces_to: >
  PGD-000 BE-003 · old-primary-doc Missing-Documents checklist Document 4 · 02-05 §9 ·
  Technology Stack Specification §18.1, §18.3 · AGENTS.md §"Git Workflow" ·
  PG-M12 / PGD-A2-15 (no version control anywhere) · RFP §5.10 (continuous source delivery)
depends_on: BE-004 (repository) · BE-005 (issued CD identifiers) · BE-002 (what review checks)
verified_on: 2026-08-18
enumeration_timestamp: 2026-08-18 13:06 (+06)
priority: P0
needed_by: Now
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# BE-003 — Git Workflow, Branching & Code Review Standard

### Category 07 · Code `BE` · Conventional Commits 1.0.0 · SemVer 2.0.0 · NIST SP 800-218

---

## 1. Purpose

`PGD-000` records this document as **◐ — partial, covered by `02-05` §9**. That coverage is three
table cells:

> | Branching | `main` (production) ← `release/*` ← `develop` ← `feature/*` and `fix/*`; `hotfix/*` from `main` |
> | Commit convention | `<type>(<scope>): <subject>` — feat, fix, docs, style, refactor, test, chore, perf |
> | Code review | Every change reviewed by a second developer; architecture changes reviewed by the architect |

Three cells are a summary of a procedure, not the procedure. They do not say how long a branch may
live, what a reviewer is accountable for, what blocks a merge, who may approve a change to the
finance ledger, how a release is tagged when two versioning schemes are in play, or what happens at
02:00 when production is down and the reviewer is asleep.

They also describe a workflow for a repository that **does not exist**. Verified 2026-08-18 13:06
(+06): there is no `.git`, `.hg` or `.svn` directory anywhere under the workspace root, across 699
files (`PG-M12`, `PGD-A2-15`).

This document is the procedure, and §3 is its first step.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | Repository initialisation, and what enters version control first |
| 2 | The **branch model** — types, sources, targets, lifetimes and protection |
| 3 | Branch **naming**, bound to `BE-005` issued identifiers |
| 4 | The **commit convention**, and the dual-convention rule for upstream OCA contributions |
| 5 | The **pull request** — template, size limits, and what must be true before review starts |
| 6 | **Code review** — reviewer count and identity by risk class, depth, turnaround, and what a reviewer is accountable for |
| 7 | **Merge criteria** and merge strategy per branch type |
| 8 | **Release, tagging and versioning** across two coexisting version schemes |
| 9 | **Hotfix** procedure, including the reduced-review path and its compensating controls |
| 10 | Delivery metrics and the review of this standard against them |

**Explicitly out of scope**

| Topic | Owned by | Why |
|---|---|---|
| Repository layout, `CODEOWNERS` generation | `BE-004` | This document consumes `CODEOWNERS`; `BE-004` generates it |
| What the reviewer looks *for* | `BE-002` §11 | Process vs content |
| CI stages, runners, deployment automation | `PE-004`, `RL-002` | §8 states what a tag means; the pipeline is theirs |
| Environment promotion gates | TSS §18.3, `GV-009` | Cited, not restated |
| Change approval for production | `GV-003`, `RL-003` | A merge is not a deployment |
| Dependency and lockfile update policy | `BE-007` | `GW-13` states the review rule only |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| **Every developer** | Branch, commit, open a PR, get it merged |
| Reviewers | §6 — what they are accountable for, and how long they have |
| Release Manager | §8 — what a tag means and how it is produced |
| Engineering Lead | §3 initialisation; §10 metrics |
| Implementation vendor | The workflow they deliver into continuously, per RFP §5.10 |
| Auditors | SSDF PO.3/PS.1/PW.7 evidence — who approved which change, and on what basis |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Conformance | Departure and rationale |
|---|---|---|
| **Conventional Commits 1.0.0** | `<type>(<scope>): <subject>`, `BREAKING CHANGE:` footer, types `feat` `fix` `docs` `style` `refactor` `perf` `test` `build` `ci` `chore` | **Extension:** `<scope>` must be an **issued** `BE-005` identifier or a reserved keyword (`GW-06`) |
| **Semantic Versioning 2.0.0** | Services, applications and shared libraries version `MAJOR.MINOR.PATCH` | **Departure:** Odoo addons use OCA's `{odoo_version}.{major}.{minor}.{patch}`. §8.2 governs the coexistence |
| **OCA commit conventions** | `[FIX]`, `[IMP]`, `[MIG]` tags; imperative present; ≤ 50-character summary | **Dual convention** — `GW-07`. House commits are Conventional; commits pushed upstream to OCA use OCA's form |
| **DORA / Accelerate** | Small batches, short-lived branches, trunk-adjacent flow, four key metrics | **Departure:** GitFlow with `release/*` is retained rather than trunk-based development. §4.1 gives the reasoning and §4.4 gives the compensating control |
| **NIST SP 800-218 (SSDF)** | PO.3 (supporting toolchains), PS.1 (protect code), PW.7 (review human-readable code), PW.8 (test), RV.1 (identify vulnerabilities) | Full; §6 and §7 are the PW.7 evidence, §3.3 the PS.1 evidence |

### 2.2 Source material relied on

| Source | Contribution |
|---|---|
| `02-05` §9 | The three cells this document expands; the branch model and commit convention |
| TSS §18.1, §18.3 | Restates the branch model; fixes the six-environment promotion ladder and its gates |
| **`../../../AGENTS.md`** §"Git Workflow" | The in-house branch table, commit types with worked examples, the seven-step PR process, PR naming, and *"Squash and merge"* |
| `old-primary-doc/…Missing_Implementation_Documents.md` §3 Document 4 | The original requirement, including the **4-hour review turnaround** target and the security/performance/Odoo/Bengali review checklist |
| `BE-005` §6 | The 331 issued identifiers that `GW-04` and `GW-06` bind to |
| `BE-004` §8 | `CODEOWNERS`, generated, and the four paths requiring a second reviewer |
| `GV-009` | Wave gates, which §8.3 maps releases onto |
| `GV-004` §5.2 | The team ramp — 3 build FTE in W1 rising to 12 — which §6.4 sizes review capacity against |

### 2.3 The inherited workflow, and its one internal inconsistency

`AGENTS.md` §"Git Workflow" is a complete and usable standard, and §4 adopts its structure. One
defect is carried forward and corrected here rather than inherited silently:

> `AGENTS.md`'s branch diagram shows `main ← develop ← feature/*`, with `hotfix/*` from `main`.
> **`release/*` does not appear in the diagram.** Its branch table, immediately below, states that
> `main`'s source is `release/*` and that `develop`'s merge target is `release/*`.
>
> The diagram and the table describe two different models. `02-05` §9 and TSS §18.1 both follow the
> table. **This document follows the table**, and §4.2 draws the diagram that matches it. Raised as
> finding `BEA-11`.

---

## 3. Initialisation

Nothing below is optional and nothing below is Wave 1. This is Wave 0, and Wave 1 cannot start
without it.

### 3.1 Sequence

| Step | Action | Owner |
|:--:|---|---|
| 1 | Create `1000fix-erp` on the approved host (`BE-004` `Q-02` must be answered first) | Engineering Lead |
| 2 | Create `main` and `develop`; make `develop` the default branch | Engineering Lead |
| 3 | **Commit the 699-file documentation estate** before any code — `docs/guiding/`, `docs/specs/` (`BE-004` §13 step 3) | Enterprise Architecture |
| 4 | Apply protection rules (§3.3) to `main`, `develop` and `release/*` | Engineering Lead |
| 5 | Commit `CODEOWNERS`, PR and issue templates, `.pre-commit-config.yaml` | Engineering Lead |
| 6 | Enable required status checks, signed commits and linear history where §3.3 requires them | Platform Engineering |
| 7 | Tag `v0.0.0-baseline` on the documentation-only commit | Release Manager |

> **Step 3 before step 4, and both before any code, is deliberate.** The estate has moved five times
> during authoring — 595 → 601 → 610 files, then 681 at 12:46 and **699 at 13:06 (+06)** on this
> single day. Every count in every register is a measurement of a moment because nothing records
> when a file arrived. A commit history records exactly that, and it is the only mechanism that does.

### 3.2 What the first tag means

`v0.0.0-baseline` marks the estate as it stood when version control began. It is the point every
later claim about "what the register said at the time" resolves against, and it closes the
reconstruct-from-memory problem that `GV-003` had to solve for `D-001`…`D-015`.

### 3.3 Branch protection

| Setting | `main` | `develop` | `release/*` | `feature/*`, `fix/*` |
|---|:--:|:--:|:--:|:--:|
| Direct push | ✘ blocked | ✘ blocked | ✘ blocked | ✔ |
| Pull request required | ✔ | ✔ | ✔ | — |
| Approvals required | **2** | 1 (2 for `CODEOWNERS` paths) | **2** | — |
| `CODEOWNERS` review required | ✔ | ✔ | ✔ | — |
| Status checks required | All | All | All | Pre-commit only |
| Dismiss stale approvals on new commits | ✔ | ✔ | ✔ | — |
| Force push | ✘ | ✘ | ✘ | ✔ (own branch only) |
| Branch deletion | ✘ | ✘ | ✘ | ✔ after merge |
| Signed commits | ✔ | ✔ | ✔ | recommended |
| Linear history | ✔ | ✔ | ✔ | — |
| Administrators exempt | **✘ — no exemption** | ✘ | ✘ | — |

> **"Administrators exempt: no" is the row that matters.** Every other protection is undone by an
> administrator who can bypass it under pressure, and the pressure always arrives at the worst
> moment. `GW-11`'s hotfix path exists so that there is a fast route that is still recorded.

---

## 4. The Branch Model

### 4.1 The decision, and the evidence against it

The programme's published model is GitFlow: `main ← release/* ← develop ← feature/*`, with
`hotfix/*` from `main`. The DORA research programme finds the opposite association — trunk-based
development with short-lived branches predicts elite delivery performance, and long-lived branches
are treated as a batch-size problem, with a branch living longer than roughly a day read as a smell.

The model is nevertheless **retained**, for reasons specific to this programme:

| Reason | Detail |
|---|---|
| **Nine wave gates with funded exits** | `GV-009` requires a wave's content to be assessable as a unit. `release/w<n>` is that unit; trunk-based delivery has no such object |
| **Six environments with manual promotion** | TSS §18.3 gates `staging` and `prod` manually. A release branch is what is promoted |
| **A distributed implementation vendor** | RFP §5.10 requires continuous delivery of source into a Company repository; an integration branch is the contractual handover point |
| **Odoo migrations are forward-only** | `MG-01`. A release object makes the migration set for a promotion enumerable |

**The cost of the choice is batch size, and batch size is controlled explicitly instead** (`GW-03`,
`GW-05`) rather than left to the branch model. That is the honest form of the trade: GitFlow does not
constrain batch size, so this standard does.

### 4.2 The model, drawn to match the table

```
main ────────────────────────────●───────────────●──────────  production, tagged, protected
                                ╱ merge          ╱ merge
                    release/w1 ●───●───●        ╱               stabilisation only
                              ╱ cut     ╲      ╱
develop ──●───●───●───●───●──●───────────●────●───────────────  integration, default branch
          ╱   ╱   ╱       ╲                    ╲
 feature/…   fix/…          ╲                   ╲
                             ╰── hotfix/… ───────╯  from main, merged to main AND develop
```

| Branch | Purpose | Cut from | Merges to | Max lifetime |
|---|---|---|---|---|
| `main` | Production. Every commit is deployed or deployable | — | — | permanent |
| `develop` | Integration. Default branch | — | `release/*` | permanent |
| `release/w<n>` | Wave stabilisation — fixes only, no new scope | `develop` | `main` **and** `develop` | until the wave gate closes |
| `feature/<CD-ID>-<slug>` | New scope | `develop` | `develop` | **3 working days** (`GW-03`) |
| `fix/<CD-ID>-<slug>` | Defect on unreleased work | `develop` | `develop` | 2 working days |
| `hotfix/<INC-ID>-<slug>` | Production defect | `main` | `main` **and** `develop` | 24 hours |
| `chore/<slug>` | Tooling, dependencies, documentation | `develop` | `develop` | 2 working days |
| `spike/<slug>` | Time-boxed investigation. **Never merged** | `develop` | — deleted | 5 working days |

### 4.3 Naming

| # | Rule |
|---|---|
| **`GW-01`** | Branch names are lower-case, hyphen-separated, ASCII. No spaces, no `#`, no Bengali |
| **`GW-02`** | `feature/*` and `fix/*` **must** carry an **issued** `BE-005` identifier: `feature/CD-M01-03-sla-escalation-matrix`. A provisional or legacy identifier fails the check (`CDR-08`, `FF-16`) |
| **`GW-03`** | A `feature/*` branch that has not merged within **3 working days** is reported daily to the Engineering Lead and appears on the sprint board as an impediment. It is not force-closed — it is made visible |
| **`GW-04`** | Branch names are validated in CI against `tooling/cd-register.yaml`; an identifier that is not in the register fails the check |
| **`GW-05`** | A branch changing more than **400 lines of non-generated, non-test code** is split, or carries an explicit written justification in the PR that the reviewer accepts before review starts |

> **`GW-03` and `GW-05` together are the compensating control for choosing GitFlow.** Three days and
> 400 lines are not arbitrary: the branch ceiling keeps integration frequent enough that `develop`
> stays merge-able, and 400 lines is around the point at which review defect-detection falls off
> sharply. `GW-05` is a **conversation trigger**, not a hard block — a generated migration or a
> scaffolded module legitimately exceeds it, which is why the justification is written and accepted
> rather than waived silently.

### 4.4 Batch-size measurement

`GW-03` and `GW-05` are only real if they are measured. §10 reports **branch age at merge** and
**changed lines per PR** as distributions, at every wave gate. A standard that sets a limit and never
looks at the distribution has set an aspiration.

---

## 5. Commits

### 5.1 Form

```
<type>(<scope>): <subject>

<body — why, not what; wrapped at 72>

<footer — BREAKING CHANGE:, Refs:, Co-authored-by:>
```

| # | Rule |
|---|---|
| **`GW-06`** | `<scope>` is an **issued** `BE-005` identifier, or one of the reserved scopes `repo`, `ci`, `deps`, `docs`, `contracts`, `infra`, `vendor` |
| **`GW-07`** | `<type>` is one of `feat` `fix` `docs` `style` `refactor` `perf` `test` `build` `ci` `chore` `revert` |
| **`GW-08`** | Subject: imperative present, ≤ 72 characters, no trailing period. *"add SLA escalation matrix"*, not *"added"* |
| **`GW-09`** | A breaking change carries a `BREAKING CHANGE:` footer stating what breaks and what a consumer must do. `!` after the scope is permitted in addition, never instead |
| **`GW-10`** | A commit touching `contracts/` states the version decision in the body — additive, or a new `schema_version` (`FF-31`, `LX-08`) |
| **`GW-11`** | Commits are **atomic**: one logical change. A commit that both refactors and changes behaviour is two commits |
| **`GW-12`** | `commitlint` enforces `GW-06`…`GW-09` in pre-commit and in CI |

Examples, all valid:

```
feat(CD-M01-03): add multi-clock SLA escalation matrix
fix(CD-M15-04): prevent negative on-hand after concurrent cycle count
refactor(CD-M28-01): extract outbox publisher from the model mixin
chore(deps): pin OCA/field-service subtree to 19.0 @ 4f2a91c
docs(CD-P02-01): record the offline conflict rules in the runbook

feat(CD-M53-02)!: settle commission in minor units

BREAKING CHANGE: settlement.amount changes from decimal string to
integer minor units. Consumers must divide by the currency exponent.
Refs: CR-0042
```

### 5.2 The upstream convention conflict

`02-05` §3 records a standing commitment: *"where 1000FiX migrates an OCA module to v19, the work is
contributed back upstream."* OCA's contributing conventions require a different commit form —
`[FIX]`, `[IMP]`, `[MIG]` tags, imperative present, summary under 50 characters, **no** Conventional
Commits prefix.

The two conventions cannot both apply to one commit, and the estate has not noticed the conflict.

| # | Rule |
|---|---|
| **`GW-13`** | **Dual convention, by destination.** Commits landing in `1000fix-erp` use Conventional Commits (§5.1). Commits pushed to an OCA repository use OCA's form |
| **`GW-14`** | Work destined for upstream is developed on a `feature/*` branch in the house convention, then **exported** via `git subtree push` and rewritten to OCA form at the boundary by `tooling/scripts/oca-export.sh`. The rewrite is scripted so it is consistent and reviewable, not done by hand |
| **`GW-15`** | Every upstream contribution is recorded in `vendor/FORKS.yaml` with its PR link before it is pushed (`REPO-10`, `REPO-11`) |

> This matters more than it looks. `02-05` §3 puts 16 unmigrated OCA modules and `A-03`'s 12–20 PW
> of migration work on the upstream path. Without `GW-14` that work either stops being contributed —
> losing the maintenance benefit the commitment exists for — or arrives upstream in a form OCA
> reviewers will ask to be rewritten.

---

## 6. Code Review

### 6.1 What a reviewer is accountable for

Stated because "reviewed by a second developer" does not say what the second developer is answerable
for, and a reviewer who is not answerable for anything approves everything.

> **A reviewer asserts three things by approving:** that they understand what the change does; that
> they have checked it against `BE-002` §11; and that they would be comfortable being called about it
> at 02:00. **Approval is a shared signature, not a courtesy.**

A reviewer is **not** accountable for finding every defect. That is what tests and fitness functions
are for, and a review process that pretends otherwise produces slow reviews that find nothing.

### 6.2 Review depth by risk class

| Class | Applies to | Approvals | Who | Depth |
|:--:|---|:--:|---|---|
| **R0** | Generated code, lockfile bumps with no version change, typo fixes in `docs/` | **1** | Any developer | Confirm it is what it claims to be |
| **R1** | Ordinary feature and fix work inside one CD item | **1** | A developer outside the author's pair | `BE-002` §11 in full |
| **R2** | Changes to `contracts/`, `libs/**`, `addons/platform/**`, any migration, any security artefact | **2** | Squad reviewer **plus** the `CODEOWNERS` owner | §11 plus contract-compatibility and migration-shape review |
| **R3** | `addons/domain/g_finance/**`, `libs/py/fix_residency/**`, `vendor/**`, anything touching money movement, tax or personal data | **2** | `CODEOWNERS` owner **plus** Chief Architect or Security Lead | §11 plus a written statement in the PR of what was verified |
| **R4** | Architectural change — a new dependency edge, a new bounded context, a new external integration | **2 + ADR** | Chief Architect, and an `AR-004` ADR merged first | The ADR is reviewed; the code is then checked against it |

| # | Rule |
|---|---|
| **`GW-16`** | Risk class is derived from changed paths by `tooling/scripts/risk-class.py` and posted as a PR label. **The author cannot lower it**; the Engineering Lead can raise it |
| **`GW-17`** | An author never approves their own change, in any class, including R0 |
| **`GW-18`** | An R3 approval carries a written statement of what was verified. *"LGTM"* on an R3 change is not an approval and is reverted at audit |
| **`GW-19`** | Pair-programmed work still requires an outside reviewer. Pairing improves the change; it does not provide independence |

### 6.3 Turnaround

The March 2026 checklist set a **4-hour** review target for a two-person team. That target does not
survive a team ramping from 3 to 12 build FTE across nine waves, so it is restated by class:

| Class | First response | Approval or explicit rejection |
|:--:|---|---|
| R0 | 4 working hours | 4 working hours |
| R1 | 4 working hours | 1 working day |
| R2 | 1 working day | 2 working days |
| R3 | 1 working day | 3 working days |
| R4 | ADR at the next Design Authority sitting | Per `GV-002` cadence |

| # | Rule |
|---|---|
| **`GW-20`** | Review is **the first work of the day**, before new development. A queue of unreviewed PRs is a queue of unintegrated work, and `GW-03` is unachievable if reviews wait |
| **`GW-21`** | A PR that breaches its turnaround is escalated automatically to the Engineering Lead, and appears in the sprint review |
| **`GW-22`** | A reviewer who cannot review within the window **declines explicitly and reassigns**. Silence is the failure mode this rule exists to remove |

### 6.4 Review capacity is a real constraint

`GV-004` §5.2 staffs W1 with **3 build FTE**. Every change needs an approver who is not the author, so
with three people the reviewer pool for any change is two — and for an R3 change in W1 it is the
Chief Architect or the Security Lead, who are not among the three.

| Wave | Build FTE | Reviewer pool for an R1 | R3 pool |
|:--:|---:|---:|---|
| W1 | 3 | 2 | Chief Architect / Security Lead — **outside the build team** |
| W2 | 7 | 6 | as above |
| W4 | 10 | 9 | as above |

> **In Wave 1 review is not a background activity; it is roughly a third of the team's throughput.**
> `GV-007`'s 0.78 delivery factor already discounts for overhead, but it was not derived from a review
> model. This is stated so that the W1 plan is not read as three developers each producing a full
> week of feature work. Raised as `BEA-12` and referred to `GV-004` §7.2.

### 6.5 Giving and receiving review

| # | Rule |
|---|---|
| **`GW-23`** | A review comment states the rule or the risk. *"`PYS-22`: this `sudo()` has no justification"* is actionable; *"I wouldn't do it this way"* is not |
| **`GW-24`** | A comment is marked **blocking** or **non-blocking**. A non-blocking comment never delays a merge |
| **`GW-25`** | Disagreement that survives one exchange goes to the Solution Architect. It does not go to a third exchange in the PR thread |
| **`GW-26`** | An author responds to every blocking comment, by change or by reasoned reply. Silently resolving a thread is not a response |

---

## 7. Pull Requests

### 7.1 Entry conditions

A PR is not ready for review until **all** are true. A reviewer returns it, unreviewed, otherwise —
this is not rudeness, it is what keeps review time going to review.

| # | Condition |
|---|---|
| 1 | All CI checks green, including every `BE-002` §10 gate |
| 2 | Branch rebased or merged up to date with `develop` |
| 3 | Description complete per §7.2 |
| 4 | Risk class label applied (`GW-16`) |
| 5 | Tests present for the behaviour changed, including the negative tests `XS-17` requires |
| 6 | No `TODO` without an issue reference (`XS-11`) |
| 7 | Under 400 changed lines, or carrying an accepted justification (`GW-05`) |

### 7.2 Template

```markdown
## What and why
<!-- One paragraph. Why is a person reading this, not what the diff already shows. -->

## CD item
<!-- Issued BE-005 identifier(s). Must match the branch name. -->

## Requirement / rule
<!-- FR-*, BRU-*, NFR-* or the audit finding this closes. -->

## How it was verified
- [ ] Unit tests added or updated
- [ ] Negative test per H-class rule, through UI **and** API (`XS-17`, DoD-04)
- [ ] Negative test per applicable role (DoD-07)
- [ ] Migration dry-run against a production-sized clone (`SQL-09`) — or N/A
- [ ] Bengali strings present and `bn_BD` at 100% (`XS-08`) — or N/A
- [ ] Manually exercised in: <environment>

## Risk
- Risk class: <!-- auto-labelled -->
- Rollback: <!-- how this is undone; DoD-16 -->
- Contract impact: <!-- none / additive / new schema_version (GW-10) -->
- Residency or personal data touched: <!-- no / yes + how FF-09 is satisfied -->

## Screenshots or output
<!-- Required for any user-facing change; both locales for a Bengali-visible change. -->
```

### 7.3 Merge

| Branch type | Strategy | Why |
|---|---|---|
| `feature/*`, `fix/*`, `chore/*` → `develop` | **Squash and merge** | One logical change, one commit; matches `AGENTS.md`; keeps `develop` bisectable |
| `release/*` → `main` | **Merge commit**, no fast-forward | The release is a distinguishable object in history |
| `release/*` → `develop` (back-merge) | **Merge commit** | Preserves the stabilisation commits |
| `hotfix/*` → `main`, then `main` → `develop` | **Merge commit** both times | The fix must be provably in both |

| # | Rule |
|---|---|
| **`GW-27`** | The squash commit message is the PR title in Conventional Commits form; the PR description becomes the body. `GW-06`…`GW-09` apply to it |
| **`GW-28`** | Merge is blocked until every entry condition and approval requirement is met. **No administrator override** (§3.3) |
| **`GW-29`** | The branch is deleted on merge. A merged branch left open is a claim on work that is finished |
| **`GW-30`** | A revert is a `revert:` commit through the normal flow, never a force push |

---

## 8. Release, Tagging and Versioning

### 8.1 Two version schemes, and why both are correct

| Artefact class | Scheme | Example | Authority |
|---|---|---|---|
| Odoo addons (`addons/**`) | `{odoo_series}.{major}.{minor}.{patch}` | `19.0.1.2.0` | OCA convention; Odoo's update mechanism reads it |
| Services, applications, shared libraries | **SemVer 2.0.0** | `2.4.1` | `LX-08` |
| **The release as a whole** | `v<MAJOR>.<MINOR>.<PATCH>` with a wave suffix | `v1.0.0-w1` | This document |

| # | Rule |
|---|---|
| **`GW-31`** | An addon's version is bumped in `__manifest__.py` in the same commit as the change, per `pylint-odoo`'s `manifest_version_format`. A behaviour change that does not bump is a defect |
| **`GW-32`** | A library's version bump follows SemVer against its **public** interface. A signature change in `libs/py/**` is a MAJOR bump (`PYS-11`) |
| **`GW-33`** | The two schemes are never mixed in one artefact, and no tooling attempts to derive one from the other |

> `AR-007` §3.2's manifest comment describes the addon scheme as five components including a
> *build* — `<odoo>.<major>.<minor>.<patch>.<build>`. OCA's convention has four, in which `19.0` is
> the two-part series. `BE-002` `BEA-10` raises it; `GW-31` implements the OCA reading pending
> `AR-007` v1.1.

### 8.2 Release tags

| Tag | Cut at | Meaning |
|---|---|---|
| `v0.0.0-baseline` | Documentation-only first commit | The estate as version control began (§3.2) |
| `v<n>.0.0-rc<k>` | On `release/w<n>` | Candidate promoted to `staging` for UAT |
| `v<n>.0.0-w<n>` | On `main` at wave go-live | Production release for wave *n*; the `GV-009` gate evidence anchor |
| `v<n>.<m>.<p>` | On `main` | Patch or minor production release inside a wave |
| `hotfix-<INC-ID>` | On `main` | Emergency production fix |

| # | Rule |
|---|---|
| **`GW-34`** | Tags are **annotated and signed**. A lightweight tag carries no author and no date of its own |
| **`GW-35`** | Every production tag has release notes generated from Conventional Commits, plus the migration set, the rollback procedure (`DoD-16`) and the `GV-009` gate reference |
| **`GW-36`** | A tag is never moved or deleted. A wrong tag is superseded by a new one and the error recorded in the notes |

### 8.3 Releases map to waves, not to sprints

Nine waves, nine major production releases, with patch releases inside each. `release/w<n>` is cut
when the wave's scope is complete on `develop` and closes when `GV-009`'s gate assessment concludes.
`BE-008` `SPR-14` governs what happens to work that does not make the cut.

| # | Rule |
|---|---|
| **`GW-37`** | Once `release/w<n>` is cut, **no new scope enters it**. Fixes only. New scope goes to `develop` for the next wave |
| **`GW-38`** | Every commit on a release branch is back-merged to `develop` before the branch closes. A fix that exists only on a release branch is a regression waiting for the next wave |

---

## 9. Hotfix

The path that exists so that the protections in §3.3 are never bypassed.

| Step | Action | Time |
|:--:|---|---|
| 1 | Incident raised in `SV-003`; an `INC-` identifier allocated | — |
| 2 | `hotfix/<INC-ID>-<slug>` cut **from `main`** | — |
| 3 | Minimum change written. Fix only — no refactoring, no cleanup, no adjacent improvement | — |
| 4 | CI runs in full. **No check is skipped** | — |
| 5 | **One** approval, from any developer with `CODEOWNERS` standing on the path, plus notification to the Engineering Lead | Target 1 hour, any hour |
| 6 | Merge to `main`; tag `hotfix-<INC-ID>`; deploy under `RL-003` emergency change | — |
| 7 | Merge `main` into `develop` **the same day** | Same day |
| 8 | Post-incident review within 5 working days; a regression test that reproduces the defect is merged before the review closes | 5 days |

| # | Rule |
|---|---|
| **`GW-39`** | A hotfix reduces the **approval count**, never the **checks**. `GW-40` is the compensating control |
| **`GW-40`** | Step 8's regression test is mandatory and is tracked as an open item until merged. A hotfix without a test is a defect that will return |
| **`GW-41`** | If a hotfix cannot be made safe within 24 hours, it is not a hotfix — it becomes a `fix/*` through the normal flow, and the incident is mitigated operationally meanwhile |

> **Step 3 is the one that gets broken.** The temptation to tidy adjacent code while in an unfamiliar
> file at 02:00 is strong, and a hotfix diff that touches more than the defect cannot be reviewed
> quickly by anyone — which removes the only compensating control the reduced-approval path has.

---

## 10. Metrics

Reported at every wave gate, per `GV-009`. Each is here because it tests a rule this document sets,
not because it is fashionable.

| Metric | Tests | Target |
|---|---|---|
| **Branch age at merge**, median and 90th percentile | `GW-03` | Median < 2 days; p90 < 3 days |
| **Changed lines per PR**, median and p90 | `GW-05` | Median < 200; p90 < 400 |
| **Time to first review response**, by class | `GW-20`, `GW-22` | Within §6.3 for 90% of PRs |
| **Deployment frequency** | DORA | Rising within a wave |
| **Lead time for change** — first commit to production | DORA | Falling wave over wave |
| **Change failure rate** — deployments needing a hotfix | DORA | < 15% |
| **Mean time to restore** | DORA | < 4 hours for P1 |
| **PRs merged with a single approval on an R2+ path** | `GW-16`, `GW-28` | **Zero.** Any instance is an audit finding |
| **Reverts within 48 hours of merge** | Review effectiveness | Trend; investigated above 5% |

> **The eighth is the control metric.** A non-zero count means either the risk classifier is wrong
> or the protection is being bypassed, and both are more serious than any delivery number on the
> list.

---

## 11. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `BE-003-D-01` | Branch model | (a) Trunk-based; (b) **GitFlow with `release/*`**; (c) GitHub Flow | **(b)**, confirming `02-05` §9 | Nine funded wave gates and six manually-promoted environments need a release object | Batch size is not constrained by the model, so `GW-03` and `GW-05` constrain it explicitly |
| `BE-003-D-02` | Feature-branch ceiling | (a) None; (b) 1 day (DORA); (c) **3 working days** | **(c)** | 1 day is unrealistic against 4-hour review turnarounds and a 3-FTE Wave 1; unbounded reproduces the integration problem GitFlow is criticised for | Measured as a distribution (§10), not asserted |
| `BE-003-D-03` | Commit convention | (a) Conventional; (b) OCA tags; (c) **both, by destination** | **(c)** | `02-05` §3's upstream commitment and TSS §18.1's house convention are both binding and incompatible | `GW-14`'s scripted rewrite at the subtree boundary |
| `BE-003-D-04` | Commit scope | (a) Free text; (b) module code; (c) **issued CD identifier** | **(c)** | Makes `FF-16`, release notes and `QA-004` traceability mechanical | Depends on `BE-005`; before it existed this was unenforceable |
| `BE-003-D-05` | Review model | (a) One reviewer always; (b) **risk-classed 1–2 plus ADR** | **(b)** | Uniform review under-reviews the ledger and over-reviews a typo | A path-based classifier must be built and maintained |
| `BE-003-D-06` | Administrator bypass | (a) Permitted for emergencies; (b) **none, with a defined hotfix path** | **(b)** | A bypass is used precisely when scrutiny matters most | §9 must be fast enough to be used, hence the 1-hour target |
| `BE-003-D-07` | Merge strategy into `develop` | (a) Merge commit; (b) rebase; (c) **squash** | **(c)** | Matches `AGENTS.md`; one logical change is one commit; keeps `develop` bisectable | Intermediate commits are lost, which is why `GW-11` requires atomic commits on the branch |

---

## 12. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | Which git host, and is it Bangladesh-resident? (`BE-004` `Q-02`) | CTO / DPO | **W0 — blocking** | §3 step 1; every subsequent step |
| `Q-02` | Does the implementation vendor push directly to `1000fix-erp`, or to a fork with PRs? RFP §5.10 requires continuous delivery but does not say by which mechanism | CTO / Procurement | **W0** | §3.3 protections; vendor onboarding |
| `Q-03` | Who holds `CODEOWNERS` standing for `addons/domain/g_finance/**` before a Finance squad exists in W3? | Engineering Lead / CFO | W1 | R3 reviews in W1–W2 |
| `Q-04` | Are signed commits mandatory for vendor contributors, and who runs the key infrastructure? | Security Lead | W1 | §3.3; SSDF PS.1 evidence |
| `Q-05` | Does `AGENTS.md` get corrected for `BEA-11`, or is it superseded by the ERP repository's own file? | Engineering Lead | W0 | Two branch models in circulation |

---

## 13. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | Every branch type has a source, a target, a lifetime and a protection profile | §4.2, §3.3 |
| `AC-02` | Branch and commit forms are machine-validated against issued identifiers | `GW-04`, `GW-12`, `tooling/cd-register.yaml` |
| `AC-03` | Review requirements vary by risk and the classifier cannot be lowered by the author | §6.2, `GW-16` |
| `AC-04` | There is a fast path for emergencies that bypasses no check | §9 |
| `AC-05` | Both versioning schemes are stated with their authority and their boundary | §8.1 |
| `AC-06` | The upstream-contribution conflict is resolved rather than left latent | `GW-13`…`GW-15` |
| `AC-07` | Every rule this document sets has a metric that tests it | §10 |
| `AC-08` | Initialisation is sequenced, owned and gated | §3.1 |

**Definition of done.** Complete when every criterion is met, §3 has executed, the first PR has passed
through the full flow, `PGD-000`'s `BE-003` row moves from ◐ to ✅ with a fresh timestamped
enumeration, and the approver has signed.

---

## 14. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `02-05` §9 | The three cells this document expands; ◐ → ✅ |
| Upstream | TSS §18.1, §18.3 | Branch model and promotion ladder |
| Upstream | `../../../AGENTS.md` §"Git Workflow" | Adopted structure; `BEA-11` corrected |
| Upstream | `BE-005` | Issued identifiers for `GW-02`, `GW-06` |
| Upstream | `BE-004` §8 | `CODEOWNERS` consumed by §6.2 |
| Downstream | `BE-002` §11 | The content of a review |
| Downstream | `BE-008` `SPR-14` | Work that misses a release cut |
| Downstream | `PE-004` | Required status checks; release automation |
| Downstream | `RL-002`, `RL-003` | Deployment and emergency change |
| Downstream | `SV-003` | `INC-` identifiers consumed by §9 |
| Lateral | `GV-003` | `CR-nnn` referenced in commit footers |
| Lateral | `GV-009` | Wave gates that release tags anchor to |

---

## 15. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` ·
[`_CATEGORY_OVERVIEW.md`](_CATEGORY_OVERVIEW.md) ·
[`BE-002`](BE-002_Coding_Standards_and_Style_Guide.md) ·
[`BE-004`](BE-004_Repository_and_Monorepo_Structure_Standard.md) ·
[`BE-005`](BE-005_Custom_Development_CD_Master_Register.md) ·
[`BE-007`](BE-007_Dependency_Licence_and_SBOM_Management_Standard.md) ·
[`BE-008`](BE-008_Sprint_Model_Estimation_and_Backlog_Management_Standard.md) ·
`../00_Programme_Governance_and_Control/GV-009_Wave_Gate_and_Phase_Exit_Criteria_Handbook.md` ·
`../02_Architecture_and_Design/AR-004_Architecture_Decision_Record_Library.md`

**Workspace**
`../../../AGENTS.md` §"Git Workflow" ·
`../../old-primary-doc/1000FiX_ERP_Missing_Implementation_Documents.md` §3 Document 4 ·
`../../1000fix_ERP_Module/02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md` §3, §9 ·
`../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §18.1, §18.3

**External standards and sources** *(all verified 2026-08-18)*
Conventional Commits 1.0.0 — `conventionalcommits.org` ·
Semantic Versioning 2.0.0 — `semver.org` ·
OCA contributing conventions — `OCA/odoo-community.org` `CONTRIBUTING.rst`, commit tags `[FIX]`/`[IMP]`/`[MIG]` ·
DORA / Accelerate — delivery-performance findings on trunk-based development, batch size and the four key metrics ·
NIST SP 800-218 *Secure Software Development Framework v1.1* — practices PO.3, PS.1, PW.7, PW.8, RV.1

---

## 16. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. Initialisation sequence, branch model with lifetimes, dual commit convention, five-class review model, merge and release rules, hotfix path, nine metrics. Raises `BEA-11`, `BEA-12` | *(unsigned — no constituted body, `PGD-A1-09`)* |

---

*`BE-003` · Category 07 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
