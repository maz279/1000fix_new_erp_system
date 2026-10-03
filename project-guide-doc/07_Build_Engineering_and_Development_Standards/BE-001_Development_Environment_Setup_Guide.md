---
id: BE-001
title: Development Environment Setup Guide
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
  Odoo 19.0 installation and configuration documentation · OCA development setup ·
  Docker Compose specification · TSS §3.5 environment ladder · NFR-086c (non-production residency)
traces_to: >
  PGD-000 BE-001 · old-primary-doc Missing-Documents checklist Document 1 (Priority 1, Document 1) ·
  Technology Stack Specification §4.1, §3.5, §20.1 W0-06, §20.3 · AGENTS.md §"Development Environment" ·
  02-05 §9
depends_on: BE-004 (the repository) · BE-002 (tool configuration) · BE-007 (pinned versions)
verified_on: 2026-08-18
enumeration_timestamp: 2026-08-18 13:06 (+06)
priority: P0
needed_by: Now
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# BE-001 — Development Environment Setup Guide

### Category 07 · Code `BE` · Odoo 19.0 · PostgreSQL 16 · Python 3.12 · Docker Compose

---

## 1. Purpose

The workspace's own March 2026 checklist put this document at **Priority 1, Document 1** — the first
of five identified as *"MUST-HAVE BEFORE DAY 1"*. Five months later it has not been written, and
`GV-004` §5.2 gives Wave 1 **40.7 effective build person-weeks against 217 person-weeks of demand**.
Against that ratio, a developer-week lost to environment archaeology is not an inconvenience; it is
2.5% of the wave's entire build capacity.

This document takes a developer from a clean machine to a verified, running 1000FiX ERP development
environment, and states what "verified" means as a checklist a machine runs rather than a feeling.

### 1.1 What changed since the March checklist

The March checklist scoped setup at *"4–6 hours per developer"* for **five** supporting services —
Keycloak, n8n, Redis, Traccar, Novu — for a two-person team.

TSS §20.3 states the Wave 1 technology load as **fifteen distinct infrastructure components plus the
entire engineering pipeline**, and `BE-005` counts **331 CD items across five language stacks**. A
single developer does not need all fifteen running to write an Odoo module, and this document is
built around that fact: §5's Compose **profiles** mean a new developer starts fifteen minutes of
services, not fifteen services.

| | March 2026 checklist | This document |
|---|---|---|
| Supporting services scoped | 5 | **15** (W1), started selectively by profile |
| Language stacks | Python/Odoo implied | 4 — Python, TypeScript, Dart, Go |
| Team size assumed | 2 | 3 → 12 build FTE across nine waves (`GV-004` §5.2) |
| Stated setup time | 4–6 hours | **§7.3** — measured, by profile, and treated as a budget |

### 1.2 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | Hardware and operating-system baseline |
| 2 | Toolchain installation for all four language stacks, at pinned versions |
| 3 | Repository clone, submodule and subtree initialisation, `make bootstrap` |
| 4 | The Docker Compose supporting stack, by profile |
| 5 | Odoo 19 CE source installation, `odoo.conf`, first run, database creation |
| 6 | Seed and demo data — and the absolute prohibition on production-derived data |
| 7 | IDE configuration, debugging and hot reload |
| 8 | The **verification checklist** — a script, not a list of feelings |
| 9 | Time budget, measured, with the failure modes that consume it |
| 10 | Troubleshooting for the failures that will actually occur |

**Explicitly out of scope**

| Topic | Owned by | Why |
|---|---|---|
| `dev`, `staging`, `training`, `prod`, `dr` environments | `PE-002`, `PE-003` | This document covers `local` only |
| Container images and registry | `PE-005` | Consumed here, built there |
| Secret management in shared environments | `PE-006`, `SC-007` | §6.4 covers local placeholders only |
| Repository layout | `BE-004` | Consumed |
| Linter and formatter rules | `BE-002` | Installed here, specified there |
| Dependency version policy | `BE-007` | This document installs what `versions.lock` pins |
| What to build once running | `BE-006`, the module specifications | — |

### 1.3 Intended audience

| Audience | Use |
|---|---|
| **A developer on day one** | Follow §3 → §8 in order. Stop at §7's checklist and do not proceed until it passes |
| Engineering Lead | §7.3's budget is an onboarding SLA, measured per joiner |
| Platform Engineering | §5's Compose file is the local expression of the `PE-002` environment ladder |
| Implementation vendor | The environment their engineers must reproduce before their first sprint |
| Security | §6.5 — why no real data ever reaches a workstation |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Conformance | Departure and rationale |
|---|---|---|
| **Odoo 19.0 installation documentation** | Source installation from the pinned submodule, not a package or a pip install | **Departure from Odoo's packaged install.** Rationale: `AS-05` requires reading and stepping into core code during development; a packaged install makes that awkward and invites the local edits `FF-03` blocks |
| **OCA development setup** | `pre-commit`, `pylint-odoo`, addons-path composition across repositories | Full |
| **Docker Compose specification** | Profiles, health checks, named volumes, explicit networks | Full |
| **TSS §3.5 environment ladder** | `local` is *"Developer workstation, Docker Compose. Synthetic fixtures. **Never** residency-classified data — synthetic only"* | Full, and §6.5 makes it a mechanism rather than an instruction |
| **NFR-086c** | Non-production environments never contain unmasked residency-classified data in any region | Full — enforced by never generating it locally, not by masking it |

### 2.2 Source material relied on

| Source | Contribution |
|---|---|
| `old-primary-doc/…Missing_Implementation_Documents.md` §3 Document 1 | The original eight-part specification for this document: base system, Odoo source install, OCA cloning, Docker services, VS Code, dev server and HMR, environment variables, verification checklist |
| **`../../../AGENTS.md`** §"Development Environment" | The in-house hardware baseline (16 GB minimum / 32 GB recommended, Ubuntu 22.04 LTS or Fedora 39+), and the pnpm/Docker/NVM setup sequence |
| TSS §4.1 | Odoo 19.0, released 18 September 2025; Python 3.12+; PostgreSQL 16; OWL 2; JSON-2 API |
| TSS §7.1, §20.2, §20.3 | The L4 systems and the fifteen-component Wave 1 load |
| TSS §3.5 | The six-environment ladder and `local`'s data rule |
| TSS §20.1 `W0-06` | *"Environment ladder, CI pipeline, Vault, monorepo, container registry"* — the Wave 0 activity this document discharges for `local` |
| `02-05` §3 | The 18 OCA repositories and their v19 migration status |
| `BE-004` §4, §6, §7 | The tree, `addons_path` composition, and the build tooling installed here |

### 2.3 Version currency

Every version below was verified against upstream release data on **2026-08-18**. Two carry findings
that affect this document.

| Component | Pinned | Verified position | Note |
|---|---|---|---|
| **Odoo** | 19.0 | Released **18 September 2025**; standard support for major versions is **three years**, so 19.0 to approximately **September 2028** | Odoo's own support documentation **does not classify 19.0 as "LTS"**, and extended support beyond the three years is a paid Enterprise offering. TSS §4.1 records the release class as *"Long-Term Support (LTS)"*. **A Community Edition deployment has no extended-support path.** Raised as `BEA-13`; see `BE-007` §7.2 |
| **Python** | 3.12 | Odoo 19.0's supported runtime | Pinned in `.python-version` |
| **PostgreSQL** | 16 | Supported to November 2029 | TSS §25.2.3's reasoning retained |
| **Node.js** | 20 LTS | Inherited from `AGENTS.md`; pinned in `.nvmrc` | |
| **Flutter** | Pinned via `fvm` in `.fvmrc` | | Subject to `D-027` (`BE-002` §6.2) |

---

## 3. Machine Baseline

### 3.1 Hardware

Inherited from `AGENTS.md` and revised upward for the Odoo estate, which the portal programme did not
carry.

| | Minimum | Recommended | Why |
|---|---|---|---|
| CPU | 4 cores / 8 threads | 8 cores / 16 threads | Odoo workers, 15 containers, and a Flutter or Next.js build concurrently |
| RAM | **16 GB** | **32 GB** | The `full` Compose profile plus Odoo plus an IDE exceeds 16 GB comfortably; 16 GB works on the `core` profile |
| Storage | 256 GB SSD | **512 GB NVMe** | `vendor/` alone is a large checkout (`BE-004` §11); container images and a production-sized database clone are not small |
| Display | 1080p | 2560×1440 or dual | Stated in `AGENTS.md`; retained |

> **The 16 GB minimum is real but tight.** A developer on 16 GB runs the `core` profile (§5.2) and
> starts additional services only when their work needs them. This is a supported configuration, not
> a degraded one.

### 3.2 Operating system

| OS | Status | Note |
|---|---|---|
| **Ubuntu 22.04 LTS or 24.04 LTS** | **Supported, recommended** | The `AGENTS.md` baseline; matches the container base images |
| Fedora 39+ | Supported | `AGENTS.md` baseline |
| macOS 14+ (Apple silicon) | Supported | `wkhtmltopdf` and some OCA C extensions need attention; §9 covers it |
| **Windows, natively** | **Not supported** | |
| Windows + WSL2 (Ubuntu 22.04) | **Supported** | With the caveats in §3.3 |

### 3.3 WSL2 caveats, stated because they will otherwise cost a day each

| Issue | Mitigation |
|---|---|
| File I/O across the Windows/Linux boundary is slow enough to make Odoo module loading painful | **The repository is cloned inside the WSL2 filesystem** (`~/src/1000fix-erp`), never under `/mnt/c/` |
| Docker Desktop's default memory allocation starves the Compose stack | `.wslconfig` sets `memory=12GB` minimum; `make doctor` checks it |
| Line endings | `XS-01` plus `.gitattributes`; `core.autocrlf` is `false`, not `true` |
| `localhost` port binding differs between Docker Desktop backends | The Compose file binds `127.0.0.1` explicitly, never `0.0.0.0` |

### 3.4 System packages

```bash
# Ubuntu 22.04 / 24.04
sudo apt update && sudo apt install -y \
  build-essential git curl \
  python3.12 python3.12-dev python3.12-venv \
  libpq-dev libxml2-dev libxslt1-dev libjpeg-dev libldap2-dev libsasl2-dev \
  libssl-dev libffi-dev zlib1g-dev \
  postgresql-client-16 \
  wkhtmltopdf \
  fonts-noto fonts-noto-bengali fonts-lohit-beng-bengali
```

| Package group | Why it is here |
|---|---|
| `libxml2`, `libxslt1`, `libsasl2`, `libldap2` | Odoo's `lxml` and `python-ldap` build dependencies. Missing these is the single most common first-hour failure |
| `wkhtmltopdf` | Odoo's PDF renderer. §9.2 covers the patched-Qt requirement |
| **Bengali fonts** | `TR-07` — *"Bengali treated as a font setting"* is a named programme failure mode. A developer whose machine cannot render Bengali will not see a shaping defect that reaches a Mushak 6.3 invoice |

---

## 4. Toolchain

All versions come from `tooling/versions.lock` (`BE-007` `LX-03`). Nothing is installed at "latest".

| Stack | Tool | Installed by | Pin file |
|---|---|---|---|
| Python | `uv` | `curl -LsSf https://astral.sh/uv/install.sh \| sh` | `.python-version`, `uv.lock` |
| Node | `nvm` → Node 20 LTS → `pnpm` | `nvm install` reads the pin | `.nvmrc`, `pnpm-lock.yaml` |
| Dart | `fvm` → Flutter | `fvm install` reads the pin | `.fvmrc`, `pubspec.lock` |
| Go | `go` toolchain | `go.mod` toolchain directive | `go.mod`, `go.sum` |
| Containers | Docker Engine 24+ / Docker Desktop, Compose v2 | Distribution package | — |
| Git | 2.40+ | Distribution package | — |

> **`git` 2.40 or later is required, not preferred.** `BE-004` uses subtrees for eighteen OCA
> repositories and partial clone for the size budget; older versions handle both poorly.

---

## 5. The Supporting Stack

### 5.1 Design

Fifteen Wave 1 infrastructure components is too many to start on a laptop by default, and starting
none of them means a developer discovers integration failures late. The resolution is **Compose
profiles**: a developer starts the profile their work needs.

| # | Rule |
|---|---|
| **`DE-01`** | Supporting services run in containers. **Nothing except Odoo itself and the language toolchains is installed on the host** |
| **`DE-02`** | Odoo runs **on the host**, from source, against containerised PostgreSQL. Debugging, breakpoints and `--dev=all` reload are all worse through a container |
| **`DE-03`** | Every service declares a **health check**. `make up` does not return until every service in the profile is healthy |
| **`DE-04`** | Every port is bound to `127.0.0.1`. A development stack is never reachable from the network |
| **`DE-05`** | Named volumes only. A `docker compose down -v` is a complete, intentional reset and nothing else destroys data |
| **`DE-06`** | Image tags are **pinned by digest** in `versions.lock`. `:latest` appears nowhere |

### 5.2 Profiles

| Profile | Services | Approx. RAM | When |
|---|---|---:|---|
| **`core`** | PostgreSQL 16, Redis, MinIO, Mailpit | ~2 GB | **The default.** Enough to build and test any Odoo module |
| `auth` | + Keycloak, PgBouncer | ~3.5 GB | Working on `cd_rbac_ext`, SSO, roles or record rules |
| `integration` | + Kong, n8n, Novu | ~5 GB | Working on M28, webhooks, orchestration or notifications |
| `field` | + Traccar, OSRM, VROOM | ~7 GB | Working on M02, M03 dispatch, routing or geofencing |
| `observability` | + Prometheus, Grafana, Loki, Tempo | ~8 GB | Working on instrumentation or performance |
| `full` | Everything | **~10–12 GB** | Integration testing; not a daily working configuration |

```bash
make up                      # core
make up PROFILE=auth         # core + auth
make up PROFILE=full
make down                    # stop, keep data
make reset                   # down -v, recreate, reseed  (DE-05)
```

### 5.3 The Compose file, abridged

```yaml
# infra/compose/docker-compose.yml — full file in the repository
name: fix-erp-local

services:
  postgres:
    image: postgres:16.9@sha256:<pinned>          # DE-06
    profiles: [core]
    environment:
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD: odoo                      # local only — DE-08
      POSTGRES_DB: postgres
      # en_US.UTF-8 with ICU: Bengali collation is a presentation concern (XS-05),
      # but the database must not be created in a C locale or ordering breaks.
      POSTGRES_INITDB_ARGS: "--encoding=UTF8 --locale=en_US.UTF-8"
    ports: ["127.0.0.1:5432:5432"]                 # DE-04
    volumes: [pgdata:/var/lib/postgresql/data]     # DE-05
    healthcheck:                                   # DE-03
      test: ["CMD-SHELL", "pg_isready -U odoo"]
      interval: 5s
      retries: 20

  redis:
    image: redis:7.4@sha256:<pinned>
    profiles: [core]
    command: ["redis-server", "--appendonly", "yes"]
    ports: ["127.0.0.1:6379:6379"]
    healthcheck: { test: ["CMD", "redis-cli", "ping"], interval: 5s, retries: 10 }

  minio:
    image: minio/minio@sha256:<pinned>
    profiles: [core]
    command: server /data --console-address ":9001"
    ports: ["127.0.0.1:9000:9000", "127.0.0.1:9001:9001"]
    volumes: [miniodata:/data]

  mailpit:                    # catches every outbound mail; nothing leaves the machine
    image: axllent/mailpit@sha256:<pinned>
    profiles: [core]
    ports: ["127.0.0.1:8025:8025", "127.0.0.1:1025:1025"]

  keycloak:
    image: quay.io/keycloak/keycloak:26.7@sha256:<pinned>
    profiles: [auth]
    command: ["start-dev", "--import-realm"]
    volumes: ["./keycloak/realm-1000fix-dev.json:/opt/keycloak/data/import/realm.json:ro"]
    ports: ["127.0.0.1:8080:8080"]
    depends_on: { postgres: { condition: service_healthy } }

  # kong, n8n, novu            → profile: integration
  # traccar, osrm, vroom       → profile: field
  # prometheus, grafana, loki, tempo → profile: observability

volumes: { pgdata: {}, miniodata: {} }
```

| # | Rule |
|---|---|
| **`DE-07`** | **All outbound mail goes to Mailpit.** No development environment sends real mail. `1000fix` operates a customer hotline and a notification estate; one misdirected batch is a reputational incident |
| **`DE-08`** | Local credentials are trivial and identical for everyone (`odoo`/`odoo`). They are **not secrets**, they never leave `local`, and they must never be reused in any other environment (`XS-06`) |
| **`DE-09`** | The Keycloak realm export is committed as a **synthetic** development realm with synthetic users. It is generated from the role register, never exported from a real environment |

---

## 6. Odoo

### 6.1 Source and addons

The Odoo source is already present after `BE-004`'s clone — `vendor/odoo` (submodule) and
`vendor/oca/*` (subtrees). There is no separate clone step, and cloning Odoo elsewhere is a defect:
the pinned commit is the version this repository builds against.

```bash
git clone --recurse-submodules <host>/1000fix-erp
cd 1000fix-erp
make bootstrap        # toolchains, uv sync, pnpm install, pre-commit install, addons_path generation
```

### 6.2 Configuration

`odoo.conf` is **generated**, never hand-written — `addons_path` is 30+ entries and drifts the day a
category is added (`REPO-15`).

```bash
make odoo-conf        # renders infra/odoo-conf/local.conf from base.conf + the tree
```

```ini
# infra/odoo-conf/local.conf — generated
[options]
addons_path = <generated — BE-004 §6, layer order is normative>
db_host = 127.0.0.1
db_port = 5432
db_user = odoo
db_password = odoo
admin_passwd = admin              ; local only (DE-08)
http_port = 8069
workers = 0                       ; 0 = threaded mode; required for breakpoint debugging
limit_time_cpu = 3600             ; generous, so a breakpoint does not kill the request
limit_time_real = 3600
dev = all                         ; Python auto-reload + XML/asset reload
log_level = info
log_handler = odoo.addons.cd_:DEBUG
list_db = True                    ; local only; False everywhere else
without_demo = False              ; local and dev only
```

> **`workers = 0` is not a performance setting.** With workers > 0 Odoo forks, and a debugger
> attached to the parent never stops in the child. Every developer who has spent an afternoon on a
> breakpoint that never fires has met this.

### 6.3 First run

```bash
make db-create                    # createdb fix_dev, correct locale
make odoo-init                    # -d fix_dev -i base,web,mail --stop-after-init
make odoo-install-wave1           # the W1 module set: Odoo core + OCA + cd_* platform
make run                          # http://127.0.0.1:8069
```

### 6.4 Environment variables

```bash
# .env.example — committed. .env is git-ignored and never committed (XS-06)
ODOO_DB=fix_dev
ODOO_CONF=infra/odoo-conf/local.conf
PGHOST=127.0.0.1
PGPORT=5432
REDIS_URL=redis://127.0.0.1:6379/0
MINIO_ENDPOINT=http://127.0.0.1:9000
KEYCLOAK_URL=http://127.0.0.1:8080
SMTP_HOST=127.0.0.1
SMTP_PORT=1025
RESIDENCY_SERVICE_URL=http://127.0.0.1:8100      # §6.5
FIX_ENV=local                                     # asserted by DE-11
```

| # | Rule |
|---|---|
| **`DE-10`** | `.env.example` is committed and complete; `.env` is ignored. A new variable added to code and not to the example is a broken onboarding for the next joiner |
| **`DE-11`** | Every service asserts `FIX_ENV=local` at startup and **refuses to start** if a non-local endpoint is configured alongside it. A local process must not be able to reach a production database because someone pasted a connection string |

### 6.5 Data — the rule with no exceptions

| # | Rule |
|---|---|
| **`DE-12`** | **A developer workstation never holds production data, masked or otherwise.** `local` sits below `staging` on the ladder and `staging` is already masked; the rule here is not "mask it", it is **"never bring it"** |
| **`DE-13`** | Seed data is **generated** by `make seed` from `db/seeds/`, deterministically from a fixed random seed, in Bengali and English |
| **`DE-14`** | The local residency service returns **synthetic values only** and is incapable of connecting to a real resident store. `FF-09` is satisfied locally by the impossibility of a real value existing, not by a check |
| **`DE-15`** | A production or staging database dump on a developer machine is a **security incident**, reported under `SC-009`, not a shortcut |

> **`DE-12` deserves its bluntness.** TSS §25.5 item 3 names *"residency enforcement built as
> convention rather than mechanism"* as a stack-failure mode, and NFR-086c is absolute. A developer
> machine is unencrypted at rest more often than anyone admits, is carried between offices, and is
> backed up to consumer cloud services. It is the least controlled environment in the estate and the
> easiest one to put real data on.

### 6.6 Seed data content

`make seed` produces a small, realistic, entirely synthetic estate:

| Entity | Volume | Notes |
|---|---:|---|
| Branches (operating units) | 5 | Mirrors the multi-branch isolation model |
| Users across the role register | ~25 | One per major role, so record rules can be exercised |
| Customers, individual and corporate | 200 | Bengali and English names; synthetic NIDs that are structurally valid and belong to nobody |
| Devices / customer assets | 500 | |
| Service orders across every state | 300 | Including the states that are hard to reach by clicking |
| Products and spare parts | 400 | |
| Open, closed and breached SLAs | 60 | So SLA logic has something to fail against |

| # | Rule |
|---|---|
| **`DE-16`** | Seed data covers **every state of every state machine**, not only the happy path. A state that seed data cannot reach is a state nobody tests |
| **`DE-17`** | Seed data is **Bengali-first**. An interface that has only ever been seen with English data hides its layout defects until UAT |

---

## 7. Verification

### 7.1 The checklist is a script

The March checklist asked for *"a 10-step checklist: run these commands to confirm your environment
is fully working."* A checklist a human reads is a checklist a human skips.

```bash
make doctor
```

| # | Check | Pass condition |
|:--:|---|---|
| 1 | Host prerequisites | Python 3.12.x, Node 20.x, `uv`, `fvm`, Docker Compose v2, git ≥ 2.40 — all at the pinned versions |
| 2 | Repository integrity | Submodule at the pinned commit; all 18 subtrees present; `git status` clean under `vendor/` (`FF-03`) |
| 3 | Compose health | Every service in the active profile reporting healthy |
| 4 | Database | `fix_dev` exists, UTF-8, reachable |
| 5 | `addons_path` | Regenerates identically to the committed file (`REPO-15`) |
| 6 | Odoo boot | Starts, serves `/web/login`, logs no ERROR |
| 7 | Module install | A scaffolded `cd_` module installs and uninstalls cleanly |
| 8 | Test run | `make test-smoke` green |
| 9 | Quality gates | `pre-commit run -a` green on a clean tree (`BE-002` §9) |
| 10 | Bengali rendering | A QWeb report renders Bengali with correct conjunct shaping — **compared against a committed reference image**, not judged by eye |
| 11 | Mail capture | A test mail arrives in Mailpit, and **no outbound SMTP connection is attempted** (`DE-07`) |
| 12 | Data safety | No table contains a value matching the residency-classified pattern set (`DE-12`, `FF-09`) |
| 13 | Debugger | A breakpoint in a `cd_` model is hit from an HTTP request |
| 14 | Hot reload | Editing a Python file and an XML view both take effect without restart |

| # | Rule |
|---|---|
| **`DE-18`** | `make doctor` exits non-zero on any failure and prints the remedy, not only the symptom |
| **`DE-19`** | **A developer does not begin work until `make doctor` is green.** Half a working environment produces defects that look like code defects and cost far more than the setup would have |
| **`DE-20`** | `make doctor` runs in CI on a clean runner, nightly. **The setup guide is tested, not trusted** — this is what keeps this document from going stale, and it is the reason it can be short |

> **Check 10 is the one that is usually skipped and is specific to this programme.** `TR-07` —
> *"Bengali treated as a font setting"* — describes invoices and payslips rendering wrongly to
> readers while passing automated tests. Comparing against a committed reference image is the only
> way an automated check catches a conjunct-shaping regression.

### 7.2 Smoke test

`make test-smoke` runs in under three minutes and exercises one path end to end: create a customer,
create a service order, transition it through its state machine, assert the outbox emitted the
declared events, assert the record rules deny a user without the role.

> If the smoke test passes, the environment is genuinely working. If only check 6 passes, Odoo is
> running and nothing has been proven.

### 7.3 Time budget

| Phase | `core` profile | `full` profile | Dominant cost |
|---|---:|---:|---|
| System packages and toolchains | 30–45 min | 30–45 min | Downloads |
| Clone with submodule and subtrees | **20–40 min** | 20–40 min | `vendor/` size (`BE-004` §11) |
| `make bootstrap` | 15–25 min | 15–25 min | `uv sync`, `pnpm install` |
| Image pulls | 5–10 min | **20–35 min** | Fifteen images |
| `make db-create` + `odoo-init` + `install-wave1` | 15–30 min | 15–30 min | OCA module installation |
| `make seed` | 3–5 min | 3–5 min | |
| `make doctor` | 5 min | 8 min | |
| **Total** | **1.6–2.7 hours** | **1.9–3.1 hours** | |

| # | Rule |
|---|---|
| **`DE-21`** | The budget is an **onboarding SLA**, measured per joiner and reported at the wave gate. A joiner exceeding 4 hours on `core` triggers a defect against this document, not against the joiner |
| **`DE-22`** | Any step that regularly exceeds its budget is automated or cached. The nightly `make doctor` run (`DE-20`) provides the measurement |

> **The March checklist's 4–6 hours was right for its scope and would be wrong here.** This estimate
> is lower for a larger stack because everything except Odoo is containerised and pinned, and because
> `make bootstrap` does in one command what the March document described as eight manual sections.

---

## 8. IDE and Debugging

### 8.1 VS Code

Committed at `.vscode/` so that configuration is shared rather than rediscovered.

| Extension | Purpose |
|---|---|
| `ms-python.python`, `ms-python.vscode-pylance` | Python language support |
| `charliermarsh.ruff` | `BE-002` `PYS-01` formatting and linting in-editor |
| `ms-azuretools.vscode-docker` | Compose stack management |
| `redhat.vscode-xml` | Odoo view XML with schema validation |
| `dart-code.flutter` | `apps/mobile/**` |
| `dbaeumer.vscode-eslint`, `esbenp.prettier-vscode` | `apps/web/**`, `libs/ts/**` |
| `eamodio.gitlens` | Review and blame |
| `humao.rest-client` | `contracts/openapi` exercised from `.http` files in-repo |

```jsonc
// .vscode/launch.json
{ "version": "0.2.0", "configurations": [
  { "name": "Odoo (local)",
    "type": "debugpy", "request": "launch",
    "program": "${workspaceFolder}/vendor/odoo/odoo-bin",
    "args": ["-c", "infra/odoo-conf/local.conf", "-d", "fix_dev"],
    "console": "integratedTerminal", "justMyCode": false },
  { "name": "Odoo test — current file",
    "type": "debugpy", "request": "launch",
    "program": "${workspaceFolder}/vendor/odoo/odoo-bin",
    "args": ["-c", "infra/odoo-conf/local.conf", "-d", "fix_test",
             "--test-enable", "--test-tags", "${fileBasenameNoExtension}",
             "--stop-after-init"],
    "console": "integratedTerminal", "justMyCode": false } ]}
```

> **`justMyCode: false` matters here.** Most debugging in an Odoo programme happens inside
> `vendor/odoo` or an OCA module, understanding what the framework does before extending it — which
> is precisely the reading `AS-05` depends on.

### 8.2 Hot reload

| Layer | Mechanism | Restart needed? |
|---|---|---|
| Python (models, services) | `--dev=all` reload | No |
| XML views, QWeb templates | `--dev=all` asset reload | No |
| Manifest, new model, new field | Module upgrade | **Yes** — `make upgrade MODULE=cd_x` |
| OWL 2 / static assets | Asset bundle regeneration | No; hard-refresh the browser |
| Next.js | Turbopack HMR | No |
| Flutter | Hot reload / hot restart | No |

---

## 9. Troubleshooting

The failures that will actually occur, with their remedies. This section grows from real support
requests; entries are added by the person who solved the problem, not by the document's owner.

| Symptom | Cause | Remedy |
|---|---|---|
| `lxml` or `python-ldap` fails to build during `uv sync` | Missing `libxml2-dev` / `libxslt1-dev` / `libsasl2-dev` / `libldap2-dev` | §3.4. **The most common first-hour failure** |
| Odoo starts, but no `cd_*` module appears in Apps | `addons_path` stale, or the module list not updated | `make odoo-conf`, then Apps → Update Apps List |
| A breakpoint never fires | `workers > 0`; Odoo forked | §6.2 — `workers = 0` |
| PDF report renders blank or unstyled | Distribution `wkhtmltopdf` is unpatched Qt | Install Odoo's patched build; `make doctor` check 10 catches it |
| Bengali renders as boxes or wrong conjuncts | Missing Noto Bengali / Lohit Bengali on the host **or** in the report container | §3.4; `TR-07` |
| `port is already allocated` | Host PostgreSQL or Redis already running | Stop the host service. `DE-01` — nothing but Odoo on the host |
| Everything is slow on WSL2 | Repository under `/mnt/c/` | Clone inside the WSL2 filesystem (§3.3) |
| `docker compose up` OOM-kills containers | `full` profile on 16 GB | Use `core`; §5.2 |
| Odoo starts against the wrong database | `.env` and `local.conf` disagree | `make doctor` check 4; `DE-11` |
| Tests pass locally, fail in CI | Test residue or ordering dependence | `PYS-27`, `AR-007` `T-02`. Run `make test` on a fresh `make reset` |
| macOS: `psycopg2` build failure | Homebrew `libpq` not on the path | `export LDFLAGS="-L$(brew --prefix libpq)/lib"` |
| Pre-commit rejects an unrelated file | Formatter run for the first time on the tree | Commit the formatting separately (`GW-11`) |

---

## 10. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `BE-001-D-01` | Odoo runtime location | (a) Container; (b) **host, from source** | **(b)** | Breakpoint debugging, `--dev=all` reload, and stepping into `vendor/` are all materially worse containerised | Host needs Python 3.12 and the build dependencies (§3.4) |
| `BE-001-D-02` | Supporting services | (a) Host packages; (b) **containers** | **(b)** | Fifteen components at pinned versions cannot be reproduced by host installation across three operating systems | Docker is a hard prerequisite |
| `BE-001-D-03` | Service scope on day one | (a) All fifteen; (b) **profiles** | **(b)** | A 16 GB machine cannot run the full stack, and an Odoo developer does not need Traccar | Profile choice is an extra concept; §5.2 makes the default explicit |
| `BE-001-D-04` | Local data | (a) Masked production clone; (b) **generated synthetic** | **(b)** | NFR-086c; TSS §25.5 item 3; a workstation is the least controlled environment in the estate | Seed data must be deliberately built to cover every state (`DE-16`) |
| `BE-001-D-05` | Verification form | (a) Written checklist; (b) **`make doctor`, run nightly in CI** | **(b)** | A checklist a human reads is skipped; a document not executed goes stale | The script is maintained as code, and it is what makes this document short |
| `BE-001-D-06` | Windows | (a) Native; (b) **WSL2 only** | **(b)** | Odoo's build dependencies and path semantics under native Windows cost more than the whole team saves | §3.3's caveats must be followed exactly |

---

## 11. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | `D-027` — is a React Native toolchain also required locally? | CTO | **W0** | §4 toolchain table; the time budget |
| `Q-02` | Are workstations Company-issued and disk-encrypted, given `DE-12`? | CTO / Security Lead | **W0 — blocking** | Whether `DE-12` is enforceable or merely stated |
| `Q-03` | Do vendor engineers develop on their own machines or on Company-provided VDI? | CTO / Procurement | **W0** | `DE-12`, `DE-15`, and `BE-003` `Q-02` |
| `Q-04` | Which registry hosts the pinned images, and is it reachable from Bangladesh at usable speed? | Platform Engineering | W0 | §7.3's image-pull budget |
| `Q-05` | Who maintains the synthetic Keycloak realm as the role register completes to R46? | Security Lead | W1 | `DE-09`; `FF-26` |

---

## 12. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | A developer with no prior Odoo experience reaches a green `make doctor` unaided | Measured per joiner (`DE-21`) |
| `AC-02` | Every one of the eight areas the March checklist specified is covered | §3, §4, §6.1, §5, §8, §8.2, §6.4, §7 |
| `AC-03` | Verification is executable and runs in CI | `make doctor`; `DE-20` |
| `AC-04` | Bengali rendering is verified against a reference, not by eye | Check 10 |
| `AC-05` | No path exists by which real data reaches a workstation | `DE-12`…`DE-15`, check 12 |
| `AC-06` | Every version is pinned and carries a verification date | §2.3, `versions.lock` |
| `AC-07` | The time budget is measured, not asserted | §7.3, `DE-21`, `DE-22` |

**Definition of done.** Complete when every criterion is met, `make doctor` has passed on a clean
runner for all three supported operating systems, `PGD-000`'s `BE-001` row moves to ✅ with a fresh
timestamped enumeration, and the approver has signed.

---

## 13. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `BE-004` | The repository and `make bootstrap` this document runs |
| Upstream | `BE-002` §9 | Pre-commit installed here |
| Upstream | `BE-007` | `versions.lock` supplies every pin |
| Upstream | TSS §3.5, §4.1, §20.3 | Environment ladder, platform specification, Wave 1 load |
| Upstream | `../../../AGENTS.md` §"Development Environment" | Hardware baseline and setup sequence |
| Downstream | `PE-002`, `PE-003` | `local` is the bottom rung of the ladder they build |
| Downstream | `BE-006` | Scaffolded components must install in this environment |
| Downstream | `QA-005` | The test automation framework runs here first |
| Downstream | `CH-004` | Developer onboarding consumes §7.3's budget |
| Lateral | `../../project_content/11_Localisation_Bengali/BN-006_*` | The Bengali rendering reference for check 10 |

---

## 14. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` ·
[`_CATEGORY_OVERVIEW.md`](_CATEGORY_OVERVIEW.md) ·
[`BE-002`](BE-002_Coding_Standards_and_Style_Guide.md) ·
[`BE-004`](BE-004_Repository_and_Monorepo_Structure_Standard.md) ·
[`BE-006`](BE-006_Component_Build_Specification_Standard.md) ·
[`BE-007`](BE-007_Dependency_Licence_and_SBOM_Management_Standard.md)

**Workspace**
`../../old-primary-doc/1000FiX_ERP_Missing_Implementation_Documents.md` §3 Document 1 ·
`../../../AGENTS.md` §"Development Environment", §"Build and Development Commands" ·
`../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §3.5, §4.1, §7.1, §20.1, §20.3 ·
`../../1000fix_ERP_Module/02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md` §3, §4, §9

**External standards and sources** *(all verified 2026-08-18)*
Odoo 19.0 administration documentation — installation, configuration, standard and extended support ·
Odoo 19.0 released 18 September 2025; standard support three years, to approximately September 2028;
extended support is a paid Enterprise offering and **the documentation does not use the term "LTS"** ·
OCA development setup and `pre-commit` configuration ·
Docker Compose specification — profiles, health checks ·
PostgreSQL 16 release and support schedule — supported to November 2029

---

## 15. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. Machine baseline, four toolchains, six Compose profiles, generated Odoo configuration, synthetic-only data rules, a 14-check executable verification, a measured time budget and a troubleshooting register. Raises `BEA-13` | *(unsigned — no constituted body, `PGD-A1-09`)* |

---

*`BE-001` · Category 07 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
