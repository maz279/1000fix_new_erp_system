# D-WS-001 — Windows-Native Workstation Baseline for P02-M01

| | |
|---|---|
| **Decision ID** | `D-WS-001` |
| **Date** | 2026-09-30 |
| **Status** | ACCEPTED (product owner direction) |
| **Deciders** | Product owner (1000FiX) — direction; Engineering — adaptation design |
| **Supersedes (for this build)** | `BE-001-D-06` (native Windows not supported) and the Ubuntu/WSL2 baseline of IR-002 `P02-M01-T02` |
| **Raise under** | `GV-003` change control per `IR-01` / `IR-04` — deviations are recorded, never silently applied |

## 1. Context

IR-002 `P02-M01 — Workstation baseline` tasks every developer machine onto
**Ubuntu 22.04/24.04 LTS** (or WSL2 for Windows users, `BE-001 §3.2–§3.3`),
with LUKS full-disk encryption, an apt package set, Docker Engine from
Docker's apt repo, git ≥ 2.40, Odoo's patched-Qt wkhtmltopdf, and a two-browser
requirement.

The product owner directed (2026-09-30) that **the build runs on native
Windows machines with no Ubuntu installation and no WSL2** ("pure native
Windows"). This decision records that direction and its engineering
consequences so the deviation is auditable rather than implicit.

## 2. Decision

The P02-M01 workstation baseline is implemented **natively on Windows**:

| Roadmap task | Ubuntu original | Windows-native adaptation |
|---|---|---|
| T01 hardware | 8c/16t · 32 GB · 512 GB NVMe · 2560×1440 or dual | unchanged criteria, probed via CIM (`Get-HardwareSummary`) |
| T02 OS | Ubuntu 22.04/24.04 | Windows 10 22H2 (build 19045) or newer, client SKU |
| T03 encryption | LUKS at install time | **BitLocker** on the OS volume (same policy driver: `DE-12`/`SC-009`) |
| T04 packages | apt set incl. Odoo build deps | winget-pinned set (Git, Docker Desktop, Python 3.12, Chrome, Firefox); the libxml2/libxslt/… build-dependency group is **not needed on the host** — those builds happen inside the Linux containers |
| T05 Bengali fonts | `fonts-noto` + `fonts-noto-bengali`* + `fonts-lohit-beng-bengali` | **Noto Sans Bengali v3.011** (hash-pinned, per-user install) + **Nirmala UI** (Windows built-in). *`fonts-noto-bengali` does not exist in the Ubuntu archive — see §4 |
| T06 containers | Docker Engine apt repo | **Docker Desktop** pinned 4.93.0 (bundles Engine ≥ 24 + Compose v2) |
| T07 git ≥ 2.40 | distro/PPA | Git for Windows pinned 2.55.0.5 |
| T08 wkhtmltopdf | patched-Qt 0.12.6.1-3 `.deb` | **Split build**: patched 0.12.6.1-3 lives **inside the Odoo container image** (Linux artefact); host gets the last upstream Windows build **0.12.5-1 msvc2015 (patched)**, hash-pinned |
| T09 browsers | Chrome/Chromium + Firefox | Chrome 154 (primary) + Firefox 157 (second engine), pinned |
| T10 port hygiene | `ss -ltnp` on 5432/6379/9000 | `Get-NetTCPConnection` on the same ports, Docker-backend listeners classified distinctly |

Tooling form: **PowerShell 5.1+** scripts under `tooling/workstation/`
(`setup-workstation.ps1`, `verify-workstation.ps1`, `machine-inventory.ps1`,
`install-wkhtmltopdf.ps1`, shared `lib/Common.psm1`), pins in
`tooling/versions.lock` (KEY=VALUE, dual-runtime parseable).

## 3. Consequences accepted

1. **Odoo runs containerised** (deviation from `BE-001-D-01`/`D-02`, which
   run Odoo on the host from source for breakpoint fidelity and `--dev=all`).
   Consequence: day-to-day debugging of Odoo happens against the container;
   the P02-M06/P02-M07 host-run and IDE workflows will need Windows-specific
   re-design when those milestones arrive (they are **not** waived — they are
   re-scoped, and any further deviation will be recorded as its own decision).
2. **PowerShell, not Bash/Make**, is the workstation tooling runtime. The
   future `make doctor` (P02-M10) will get a `doctor.ps1` equivalent; the
   task list of M10 is unchanged, its harness changes.
3. **wkhtmltopdf host version stays at 0.12.5-1** because upstream has never
   shipped a Windows 0.12.6.x. Container-side rendering (what Odoo actually
   uses) is at the same patched 0.12.6.1-3 as the roadmap baseline.
4. **Lohit Bengali is absent on Windows** (no binary distribution; upstream
   publishes font sources). Nirmala UI (Microsoft, full Bengali conjunct
   support) fills the "second conjunct-capable family" role of `TR-07`.
5. Docker Desktop's backend (WSL2 or Hyper-V) is a machine-level property;
   the baseline requires only `docker` + `docker compose` ≥ v2 on PATH — it
   does not require the user to install an Ubuntu distribution.
6. `make doctor` checks 13/14 (host breakpoint, hot reload) will need
   Windows adaptations in P02-M10; tracked there, not silently dropped.

## 4. Corrections raised against source documents (per `IR-01`/`IR-04`)

| # | Source says | Reality (verified 2026-09-30) | Action |
|---|---|---|---|
| C-1 | BE-001 §3.4 / IR-002 package block list `fonts-noto-bengali` | **No such Ubuntu package exists** in jammy/noble; Noto Sans Bengali glyphs ship inside `fonts-noto-core` | Corrected in this baseline; raise `CR` against BE-001 §3.4 |
| C-2 | BE-001 §3.4 pins `postgresql-client-16` | IR-002's own package block (P02-M01) pins `postgresql-client-17` per `D-029` (PG 17 baseline) | Follow IR-002; on Windows the psql client ships inside containers, host client optional |
| C-3 | BE-001 §5.3 Compose carries `minio` images | `B-19` resolved MinIO→Ceph (`D-030`) | Port set for hygiene checks kept as-is; container images are P02-M05's pin problem |

## 5. Revisit triggers

- If breakpoints/`--dev=all` fidelity becomes a blocking complaint → evaluate
  WSL2 as a **developer-option** (not a baseline requirement) under a new ADR.
- When Odoo 20 upgrade planning starts (`B-08`), re-check whether a Windows
  host-run path is feasible at all; if not, document the permanent container
  workflow in the developer guide.
- `Q-02` (Company-issued, disk-encrypted machines) maps on Windows to
  BitLocker-on-OOBE policy; Security Lead to confirm fleet enforcement tooling.
- **Windows 10 end of support** (audit addendum 2026-10-01): the T02 floor
  still admits Windows 10 22H2 per this decision, but 22H2 passed end of
  support in October 2025 (ESU excepted). `verify-workstation.ps1` T02 now
  WARNs on Windows 10-range builds. When the fleet policy lands, raise the
  floor to build 22000 (Windows 11) under a new decision rather than editing
  this one silently.
