# Workstation Tooling — P02-M01 (Native Windows)

Executables that implement IR-002 milestone `P02-M01 — Workstation baseline`
under decision [`D-WS-001`](../../docs/decisions/D-WS-001-windows-native-workstation-baseline.md).
Full guide: [`docs/guides/workstation-baseline.md`](../../docs/guides/workstation-baseline.md).

| File | Purpose |
|---|---|
| `setup-workstation.ps1` | Automated baseline: OS floor (T02), BitLocker verify-and-instruct (T03), pinned winget set (T04/T06/T07/T09), patched wkhtmltopdf (T08 — passes `-UserScope` through when run non-elevated with `-AllowUserContext`), Bengali fonts (T05), port-hygiene report (T10). Idempotent; `-DryRun` shows the real plan (read-only probes still run) |
| `verify-workstation.ps1` | Executable verification of **all ten tasks** — PASS/WARN/FAIL with remedies (`DE-18`), exit non-zero on any FAIL (`DE-19`); `-Json`, `-Strict`, `-Deep`, `-SelfTest`. T06 also probes engine reachability (`docker info`) and `docker-users` group membership |
| `machine-inventory.ps1` | T01 hardware/OS/tool inventory + RECOMMENDED/MINIMUM classification (shared `Get-HardwareClassification`); `-OutFile` JSON. Reports the pinned Python line (`py -3.12`) separately from whatever `python` resolves to on PATH |
| `install-wkhtmltopdf.ps1` | T08: hash-verified silent install of the pinned patched-Qt host build; machine PATH by default, or **user PATH via `-UserScope`** (no elevation). Non-elevated machine-scope attempts exit 2 with the remedy |
| `packages.winget` | The pinned system package set (T04) |
| `lib/Common.psm1` | Shared helpers: pin loading (fails closed), logging + remedies, version maths, platform/hardware probes, **`Get-PlatformInfo` derives the true marketing OS name** (the registry `ProductName` still says "Windows 10" on Windows 11), font probes, port probes, hardware classification, docker-users probe |
| `lib/common.sh` · `install-wkhtmltopdf.sh` | Tombstones — superseded Ubuntu tooling (D-WS-001); do not execute |

Pins come **only** from [`tooling/versions.lock`](../versions.lock) — no
version is ever "latest" (`IR-07`/`DE-06`), and no credentials are handled
anywhere.

## Quick start (elevated PowerShell)

```powershell
powershell -ExecutionPolicy Bypass -File .\setup-workstation.ps1          # install
powershell -ExecutionPolicy Bypass -File .\verify-workstation.ps1        # must be green
powershell -ExecutionPolicy Bypass -File .\machine-inventory.ps1 -OutFile inventory.json
```

Runtime: Windows PowerShell 5.1 (inbox) or PowerShell 7+. Scripts are pure
ASCII by policy (PS 5.1 parses BOM-less files as ANSI) — the self-test
enforces it.
