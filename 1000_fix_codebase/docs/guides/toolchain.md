# Toolchain guide — reproducing the workstation exactly (P02-M02-T10)

**`DE-21`: the setup time budget is an onboarding SLA, measured per joiner and
reported at the wave gate.** A joiner exceeding **4 hours on `core`** triggers
a defect against `BE-001`, not against the joiner. Measure with
`docs/guides/onboarding-sla.md`'s form and file the result.

The single source of every version: [`tooling/versions.lock`](../../tooling/versions.lock)
(`BE-007 LX-03`). Nothing installs at "latest" (`DE-06`).
**Lock rule (recorded decision):** container images pin **bytes** (digest);
workstation toolchains pin **lines** with floors enforced by `doctor.ps1`
check 1 — toolchains self-update within their line, and a stale patch pin is a
worse failure mode than a line pin with a doctor floor.

## 1. The pinned set

| Tool | Line | Pin file / how it loads | Floor enforced by |
|---|---|---|---|
| Python | **3.12.10** | `.python-version` (uv reads it) | doctor check 1 |
| Node | **22 LTS** (20 went EOL 2026-04-30 — finding F-1) | `.nvmrc` | doctor check 1 |
| pnpm | 9 | workspace catalog | doctor check 1 |
| uv | 0.8 line | self-managed | doctor check 1 |
| Flutter | **3.44.0 via fvm** | `.fvmrc` | doctor check 1 |
| Go | 1.24 | `services/telemetry-collector/go.mod` toolchain directive | CI |
| git | ≥ 2.40 | — | doctor check 1 / verify-workstation T07 |

## 2. Install (Windows-native, `D-WS-001`)

```powershell
# from the repository root (elevated for winget steps)
powershell -ExecutionPolicy Bypass -File tooling\scripts\setup-toolchains.ps1
# check only:
powershell -ExecutionPolicy Bypass -File tooling\scripts\setup-toolchains.ps1 -VerifyOnly
```

## 3. Install (Ubuntu 22.04/24.04 — CI runners and any Linux developer)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh          # uv (reads .python-version)
uv python install 3.12.10
nvm install && nvm use                                     # reads .nvmrc -> Node 22
npm install -g pnpm@9
fvm install && fvm use                                     # reads .fvmrc -> Flutter 3.44.0
# Go: https://go.dev/dl/ (1.24 line); the go.mod toolchain directive governs
```

## 4. Post-install (both platforms)

```bash
make bootstrap        # Linux; Windows: powershell tooling\scripts\tasks.ps1 -Target bootstrap
make doctor           # Windows: powershell tooling\scripts\doctor.ps1
```

## 5. Flutter 3.44 — pin deliberately (`D-027`)

**Read the 3.44 migration notes before pinning.** 3.44 moves Material and
Cupertino out of the core SDK into standalone `material_ui`/`cupertino_ui`
packages and makes Impeller the default renderer on Android (Skia removed).
Four applications and `libs/dart/fix_ui` are affected; `fix_ui` adopts the
standalone packages as a named migration task, never opportunistically.

## 6. Git configuration (P02-M02-T07/T08/T09)

```bash
git config core.autocrlf false        # false, NOT true (XS-01; .gitattributes governs)
git config core.hooksPath .githooks   # commit convention hook (bootstrap does this)
git config commit.gpgsign true        # signed commits are a branch-protection precondition
gh auth status                        # PR flow + CI artefact inspection
```
