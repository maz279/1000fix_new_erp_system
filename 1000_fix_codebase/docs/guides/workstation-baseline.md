# Workstation Baseline — P02-M01 (Native Windows)

**IR-002 Phase 2 · Milestone M01 · Decision D-WS-001 (Windows-native).**
This guide takes a Windows PC to a green workstation baseline in one pass.
Everything the scripts do is pinned in [`tooling/versions.lock`](../../tooling/versions.lock);
nothing installs at "latest" (`IR-07`, `BE-007 LX-03`, `DE-06`).

> **A developer does not begin work until `verify-workstation.ps1` is green.**
> (`DE-19`) Half a working environment produces defects that look like code
> defects. The verifier prints the **remedy**, never just the symptom (`DE-18`).

---

## 1. The two baselines (T01)

| | Minimum | Recommended |
|---|---|---|
| CPU | 4 cores | 8 cores / 16 threads |
| RAM | 16 GB *(core Compose profile only)* | 32 GB |
| Disk | 256 GB SSD | 512 GB NVMe |
| Display | 1080p | 2560×1440 or dual |

The `full` Compose profile plus Odoo plus an IDE exceeds 16 GB — that is not
a degraded configuration, it is the documented `core`-profile mode.

## 2. One-command setup (T02–T09)

From an **elevated** PowerShell:

```powershell
cd <repo>\tooling\workstation
powershell -ExecutionPolicy Bypass -File setup-workstation.ps1
```

What it does, in order (all idempotent — safe to re-run):

1. **T02** — checks the OS floor (Windows 10 22H2 / build 19045+; native
   Windows is the sanctioned baseline under `D-WS-001`).
2. **T03** — checks BitLocker on the OS volume and instructs if off. Enabling
   BitLocker is deliberately **not** silent: it is a provisioning action with
   TPM/reboot implications (`DE-12`/`SC-009` make it non-negotiable, the
   operator runs `manage-bde -on C:` themselves).
3. **T04/T06/T07/T09** — installs the winget-pinned set: Git 2.55.0.5,
   Docker Desktop 4.93.0, Python 3.12.10, Chrome 154, Firefox 157.
   After Docker Desktop installs you must **launch it once** and accept the
   licence (interactive by design), then open a new shell.
4. **T08** — delegates to `install-wkhtmltopdf.ps1`: downloads the pinned
   `wkhtmltox 0.12.5-1 msvc2015-win64` installer, **verifies SHA256 before
   install**, installs silently, and wires the PATH — machine scope
   (`C:\Program Files\wkhtmltopdf\bin`, machine PATH) when elevated, or
   user scope (`%LOCALAPPDATA%\Programs\wkhtmltopdf\bin`, user PATH) with
   `-UserScope` / when setup itself runs non-elevated. (The Odoo container
   image carries the patched 0.12.6.1-3 Linux build — see the split-build
   ruling in D-WS-001.)
5. **T05** — downloads Noto Sans Bengali v3.011, verifies SHA256, installs
   the family per-user (no admin, no reboot). Nirmala UI ships with Windows
   and is verified present.
6. **T10** — reports any listener on ports 5432/6379/9000. Host
   PostgreSQL/Redis/object-store services are prohibited (`DE-01`): those
   run as containers only.

Dry-run first if you want to see the plan:

```powershell
powershell -ExecutionPolicy Bypass -File setup-workstation.ps1 -DryRun
```

Selective steps: `-SkipWinget`, `-SkipFonts`, `-SkipWkhtmltopdf`.

## 3. Verify (all ten tasks)

```powershell
# elevated recommended: T03 needs manage-bde
powershell -ExecutionPolicy Bypass -File verify-workstation.ps1
```

- Exit `0` = green (warnings allowed). Exit `1` = red, remedies printed.
- T06 checks the version floors **and** that the engine is actually
  reachable (`docker info`) — "installed but Docker Desktop never launched"
  is a WARN, not a pass. It also checks `docker-users` group membership
  (the Windows analogue of the roadmap's "add the user to the docker
  group"); if the group does not exist on your backend that leg is
  informational, engine reachability being the functional proof.
- `-Json out.json` — machine-readable results (feeds evidence packs).
- `-Strict` — warnings count as failures.
- `-Deep` — adds a Bengali HTML→PDF render probe (the reference-image
  conjunct comparison itself is `make doctor` check 10, P02-M10-T04).
- `-SelfTest` — validates the tool's own logic; no system access.

## 4. Machine inventory (T01)

```powershell
powershell -ExecutionPolicy Bypass -File machine-inventory.ps1 -OutFile inventory.json
```

Classifies the machine `RECOMMENDED` / `MINIMUM (core profile)` /
`BELOW MINIMUM` and records CPU, RAM, system disk (bus/media), displays,
BitLocker state, tool versions, Bengali-font presence and reserved-port
listeners.

## 5. Troubleshooting (seeded from BE-001 §9, Windows-adapted)

| Symptom | Cause | Remedy |
|---|---|---|
| `docker` not on PATH after setup | New shell needed after Docker Desktop install | Open a new PowerShell window |
| Docker engine unreachable | Docker Desktop launched but licence not accepted / engine still starting | Launch Docker Desktop, accept licence, wait for "Engine running" |
| T04 says a package "missing" though installed | winget console truncation or a non-standard install channel | The check falls back to binary probes (git/docker/py/chrome.exe/firefox.exe VersionInfo); if it still misses, install via the pinned winget id |
| T08 fails with SHA256 mismatch | Upstream artefact replaced or corrupted download | Do **not** install; re-download; if persistent, update the pin via a reviewed change |
| Bengali renders as boxes | Fonts not installed / stale browser session | Run the fonts step (`setup-workstation.ps1 -SkipWinget -SkipWkhtmltopdf`), restart the browser |
| PDF reports blank/unstyled | Unpatched wkhtmltopdf shadowing the pinned build | Re-run `install-wkhtmltopdf.ps1`; check `where.exe wkhtmltopdf` for strays |
| `port is already allocated` | A host service holds 5432/6379/9000 | Stop/uninstall the host service (`DE-01`); containers own those ports |
| T03 indeterminate | `manage-bde` needs elevation | Re-run `verify-workstation.ps1` from an elevated shell |
| Scripts fail to parse with odd characters | A non-ASCII character entered a `.ps1` (PS 5.1 reads BOM-less files as ANSI) | Keep scripts ASCII-only — the self-test enforces this; build non-ASCII strings from code points |

## 6. What is deliberately NOT on the host

Per `DE-01` (Windows adaptation): PostgreSQL, Redis, object storage, Odoo and
its build dependencies all run **in containers**. The host carries the
toolchain (Git, Python 3.12, Node/pnpm arrive with P02-M02), Docker Desktop,
two browsers, patched wkhtmltopdf and the Bengali fonts. Port hygiene (T10)
enforces the boundary.

## 7. Next milestone

`P02-M02 — Toolchain installation and pinning` installs uv/nvm/pnpm/fvm/Go
and extends `tooling/versions.lock`; `P02-M05` stands up the Compose stack.
This milestone's scripts are the harness those steps plug into.
