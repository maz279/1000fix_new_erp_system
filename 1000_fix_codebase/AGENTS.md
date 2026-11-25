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

---

## Enterprise Multi-Tab Forms & Bangladesh Workforce Master Standard (October 2026)

### 1. Dynamics 365 In-Workspace Multi-Tab Forms Architecture
- **Tabbed Layout**: Complex data-entry forms (>15 fields) must NEVER be rendered as a single vertical scroll page. They must be partitioned into Microsoft Dynamics 365 multi-tab navigation (`tabs: [{id, label, bn, icon, badge}]`).
- **Engine Support**: `p03_workspace.js` handles active tab state (`formActiveTab`, `formSetTab(tabId)`), dynamic section filtering (`formSections`), and atomic full-form writes across all tabs (`/p03/model/write`).
- **Accessible ARIA Standards**: Tab navigation uses `.d365-formtabs` with `role="tablist"` and `aria-label="Form Tabs"`, tab buttons with `role="tab"`, `aria-selected`, roving `tabindex="0|-1"`, and panel container with `role="tabpanel"`. Minimum 44px tap target height and visible 2px focus ring satisfy WCAG 2.2 AA.
- **Photo & Avatar Field**: Support `image_1920` / binary image fields using dedicated `.d365-image-field` components with avatar preview, camera icon button, file picker, and clearing buttons. Automatically strip `data:image/...;base64,` prefixes before ORM commits.

### 2. Bangladesh Statutory Workforce Master Compliance
Under the Bangladesh Labour Act 2006 (BLA 2006), Labour Rules 2015, and Income Tax Act 2023, every employee master record must capture:
- **Statutory Identity**: English legal name, Bengali legal name (`name_bn`), employee code, Father's name, Mother's name, Date of Birth, Gender (`sex`), Blood Group, Religion, Marital Status.
- **Statutory & Tax Registrations**: 10-digit Smart / 17-digit National ID (`nid_number`), 12-digit e-TIN (`tin_number`), NBR Tax Zone (`tax_zone`), NBR Tax Circle (`tax_circle`), Form 7 Service Book Register No (`service_book_number`), Passport No.
- **Addresses & Contacts**: Present residential address (`private_street`, `private_city`), statutory permanent ancestral address (`permanent_address`, `permanent_district`, `permanent_division`), personal email/phone, and official work channels.
- **Scheduled Bank & MFS Accounts**: Scheduled bank name, branch, 9-digit BEFTN routing code (`routing_number`), bank account number, MFS wallet provider (`mfs_provider`: bKash/Nagad/Rocket), MFS account number, and BLA s.108 overtime eligibility (`overtime_eligible`).
- **Emergency Next-of-Kin**: Primary emergency contact person, relation, primary phone, alternative phone, full address, spouse name, and dependent children count.
