# AGENTS.md — contributor conventions for the `1000fix-erp` repository

This file states the conventions **of this repository** (BE-004 §2). The
programme-level conventions live in the workspace `AGENTS.md` and the
`project-guide-doc` set; where the two disagree, the programme set wins and a
CR fixes this file.

## The one rule above all others

**`DE-19` — a developer does not begin work until `make doctor` is green**
(Windows: `tooling/scripts/doctor.ps1`). Half a working environment produces
defects that look like code defects.

## Layout in one screen

```
vendor/    third-party (Odoo submodule + 20 OCA subtrees) — READ-ONLY (AS-05)
addons/    custom Odoo modules: platform/ (layer 3) + domain/a..k (layer 4)
services/  standalone services (FastAPI / Go / Node)
apps/      mobile (Flutter) + web (Next.js 16.3 portals)
libs/      py / ts / dart shared libraries
contracts/ openapi / events / portal — the versioned interface surface
db/        migrations + seeds (SYNTHETIC ONLY — DE-12/DE-13)
infra/     compose / k3s / terraform / odoo-conf
tooling/   cd-register.yaml, fitness/, generators/, scripts/, versions.lock
docs/      adr (= decisions/), runbooks/, guides/, traceability/
.github/   workflows + PR/issue templates
```

## Identifiers

- Work items are **`CD-<UNIT>-<nn>`** and come from
  `tooling/cd-register.yaml` (BE-005 §6, rule `CDR-11`: generated, never
  hand-edited). **`CDR-08`: an identifier may not appear in a manifest,
  branch, commit, backlog item or test case unless it is in the register.**
  Stories are `ST-<CD-ID>-<nn>`, derived, never centrally allocated.
- Full identifier discipline: `docs/p01-m05/identifier-discipline.md`.

## Commits — `<type>(<scope>): <subject>`

- `type` ∈ `feat fix docs style refactor test chore perf`
- `scope` = the CD unit the change belongs to: `CD-<UNIT>-<nn>` for a specific
  item (e.g. `feat(cd_service_order)`… no — see next line) — **scope is the
  CD identifier**, e.g. `feat(CD-M01-01): …`. Unit-level changes use the unit
  prefix scope `CD-M01` when no single item owns it.
- **Root/release exceptions** (recorded decision of this repository): commits
  that belong to no CD item — repository initialisation, version tags, lock
  re-pins — use scope `repo` or `release`. The commit-msg hook accepts exactly
  these two non-CD scopes; anything else must resolve in the register.
- Enforced by `.githooks/commit-msg` (installed by bootstrap via
  `git config core.hooksPath .githooks`). `--no-verify` is permitted **only**
  on `hotfix/*` branches and the next commit on that branch must pass (`XS-20`).

## Branches — `main` ← `release/*` ← `develop` ← `feature/*|fix/*`; `hotfix/*` from `main`

Protected from day 0 (P02-M03-T05): required reviews, required status checks,
signed commits, linear history, no force-push.

## Hard rules enforced by tooling, not review

| Rule | Enforced by |
|---|---|
| Never edit `vendor/` | `check-vendor-clean` (`FF-03`), pre-commit + CI |
| No secrets | gitleaks, pre-commit + CI over full history (`SE-01`) |
| No AGPL/BSL/TSL/fair-code additions without approval | licence gate (`D-030` register) |
| `cd_` identifiers must be register members | `check-cd-id.py` (`FF-16`, Warning→Blocking at `G1`) |
| `odoo.conf` is generated, never hand-written | `generate-odoo-conf` (`REPO-15`), doctor check 5 |
| Residency fields only via `libs/py/fix_residency` | `FF-09` (single-client rule) |
| Events only via `libs/py/fix_events` | `FF-28` (no direct bus clients) |
| Local env never reaches non-local endpoints | `DE-11` startup assertion |
| No production data on a workstation, ever | `DE-12`/`DE-15` — a dump here is a security incident |

## Environments

`local` is synthetic-only, below `staging` on the ladder. Twelve environments
and their data rules: `infra/environments.yaml` (`PE-002-D-01`).
