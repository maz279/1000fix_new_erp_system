# P02-M01 Implementation Audit — 2026-09-30 (second pass)

> **Subject:** the implemented `P02-M01 — Workstation baseline` (native
> Windows, decision [`D-WS-001`](../decisions/D-WS-001-windows-native-workstation-baseline.md))
> — scripts, pins, docs, evidence — plus its source roadmap sections.
> **Method:** full read of every artefact; live execution of self-test,
> verify, inventory and setup dry-run; PowerShell language-parser check of
> all five PS files; cross-check of every task row against IR-002 `P02-M01`,
> `D-WS-001`, the guide and the traceability record; spot-verification of the
> roadmap audit's claimed remediations.
> **Verdict:** 19 findings — 3 factual tooling errors, 2 logic/consistency
> defects, 4 robustness (DE-18/DE-19) gaps, 1 dry-run fidelity gap, 2
> precondition gaps, 4 documentation/traceability discrepancies, 1 junk-artefact
> class, 2 roadmap-residual classes (11 corrupted rows in total).
> **All fixed and re-verified; register below.** A follow-up audit of these
> fixes themselves (iteration 2, 2026-10-01) found 9 more defects — see
> §Iteration 2 at the end.

## Findings register

### A — Junk artefacts

| # | Finding | Fix | Verified by |
|---|---|---|---|
| **A-1** | Four junk `nul` files (repo root of the workspace, `1000_fix_codebase/`, `tooling/`, `tooling/workstation/`) — output of failed `findstr`/`dir` commands run in Git Bash, polluting the tree | Deleted all four | `ls` returns "No such file" |

### B — Factual errors in tooling output

| # | Finding | Fix | Verified by |
|---|---|---|---|
| **B-1** | **Every report misnamed the OS.** The registry `ProductName` still reads "Windows 10 Pro" on Windows 11 (a known Microsoft quirk); `Get-PlatformInfo` copied it verbatim, so the inventory and verify T02 reported "Windows 10 Pro build 26300 (26H2)" — factually wrong (26300 is Windows 11) | `Get-PlatformInfo` derives the marketing name from the build (client ≥ 22000 ⇒ "Windows 11"), keeps the raw value as `ProductNameRaw` | Live run: "Windows 11 build 26300 (26H2)" |
| **B-2** | `machine-inventory.ps1` probed bare `python` (whatever wins PATH) — the recorded evidence showed `python: 3.14.7` against a 3.12.10 pin, misleading the inventory consumer | Inventory now probes the pinned line first (`py -3.12`) as `python312` and records PATH python separately as `pythonOnPath` | Live run: `python312: Python 3.12.10` |
| **B-3** | The Nirmala-UI remedy cited a nonexistent AppxManifest package (`Microsoft.Windows.FontExtrator_cw5n1h2txyewy`) — a command that cannot work | Replaced with the real repair: `sfc /scannow` (elevated) + Settings → Fonts check | Code inspection (remedy path not triggered on this machine) |

### C — Logic / consistency defects

| # | Finding | Fix | Verified by |
|---|---|---|---|
| **C-1** | **T01 display logic diverged between the two scripts**: `machine-inventory` required width ≥ 2560 **and** height ≥ 1440; `verify` checked width ≥ 2560 only. Same task, two answers | Single shared implementation `Get-HardwareClassification` in `Common.psm1` (2560×1440 **or** dual display, per roadmap T01 wording); both scripts consume it | Both live runs classify identically; self-test green |
| **C-2** | `machine-inventory.ps1` header comment invented a "4c/**8t**" minimum — the roadmap minimum is 4 cores / 16 GB / 256 GB SSD (no thread floor) | Comment corrected; code (cores ≥ 4, no thread floor) was already right | Code inspection |

### D — DE-18 / DE-19 robustness gaps

| # | Finding | Fix | Verified by |
|---|---|---|---|
| **D-1** | An unexpected `throw` (e.g. winget install failure) aborted `setup`/`install-wkhtmltopdf` mid-flight with a raw error and **no remedy line** — violating the DE-18 "remedy, not only the symptom" discipline | Top-level `trap` in both scripts: prints FAIL + remedy ("re-run — every step is idempotent") and exits 1 | Parser check + code inspection |
| **D-2** | **T06 passed on a machine whose Docker engine has never been started** (CLI + `--version` work offline; "installed but Docker Desktop never launched" was indistinguishable from a working baseline) | T06 now probes engine reachability (`docker info`): unreachable ⇒ WARN with the launch/licence remedy; the roadmap's literal verify text (engine ≥ 24, compose v2) remains the PASS gate | Live run: "engine reachable" in the PASS detail |
| **D-3** | The roadmap's T06 "add the user to the `docker` group" had **no Windows analogue check** (docker-users membership) | `Test-UserInDockerUsersGroup` added; definitively-not-a-member ⇒ WARN with `net localgroup docker-users` remedy; group absent (this backend) ⇒ informational, engine reachability being the functional proof | Live run: info note, PASS |
| **D-4** | `-Deep` Bengali render probe left both probe files in `%TEMP%` forever | Cleanup after the probe (PDF kept only on success — the success message tells the user to inspect it) | Code inspection |

### E — Dry-run fidelity

| # | Finding | Fix | Verified by |
|---|---|---|---|
| **E-1** | `-DryRun` skipped the **read-only** installed-version probe, so the dry-run plan listed "Installing Git.Git/Docker/Python/Chrome/Firefox" on a fully-provisioned machine — a misleading plan | Read-only probes now run in dry-run; only mutations are skipped. The dry-run plan shows real no-ops | Live dry-run: 4× "already installed", Docker info no-op |

### F — Precondition gaps

| # | Finding | Fix | Verified by |
|---|---|---|---|
| **F-1** | `install-wkhtmltopdf.ps1` non-elevated without `-UserScope` only WARNed, then proceeded into a machine-scope NSIS install that cannot succeed unattended — failing later without a remedy | Hard precondition: exit 2 + remedy (documented exit-code semantics now real) | Live test: exits 2 with FAIL + remedy |
| **F-2** | `setup-workstation.ps1` always invoked the installer machine-scope, so a `-AllowUserContext` (non-elevated) setup run hit F-1 | Setup passes `-UserScope` through when it is itself non-elevated | Code inspection + parse check |

### G — Documentation / traceability discrepancies

| # | Finding | Fix | Verified by |
|---|---|---|---|
| **G-1** | **The traceability record contradicted itself and overstated completion**: headline "8 PASS · 2 WARN · 0 FAIL · exit 0" next to "T03 is a genuine open FAIL"; README claimed "Implemented & executed". Per DE-12/SC-009/DE-19 the baseline is **RED** until BitLocker is on | Final-state section rewritten: precise T03 status (definitive elevated query = Protection Off ⇒ elevated verify would FAIL ⇒ baseline RED until operator enables), T10 WARN explained; README status table re-worded ("all ten mechanisms verified live; T03 open operator action") | Doc read-through |
| **G-2** | Guide §2 step 4 said wkhtmltopdf "adds `C:\Program Files\wkhtmltopdf` to the machine PATH" — stale: `-UserScope` exists and is what the machine actually runs | Guide documents both scopes | Doc read-through |
| **G-3** | `tooling/workstation/README.md` table said "+ machine PATH" for the installer and omitted the new T06 legs | Table updated (user/machine scope; T06 reachability + docker-users; inventory python probes; OS-name derivation) | Doc read-through |
| **G-4** | Evidence JSONs recorded the pre-fix tooling's output (wrong OS name, PATH-python 3.14.7, stale port state) | Both evidence files regenerated with the fixed tooling; traceability evidence table updated | New evidence files |

### H — Roadmap residual corruptions (registered in `roadmap/AUDIT_REPORT.md` §Follow-up)

| # | Finding | Fix |
|---|---|---|
| **H-1** | IR-002 Appendix I (historical 2026-08-19 record) still carried the programmatic minio→Ceph / Metabase→Superset / n8n→Airflow / Redpanda→Kafka replacements in 9 rows — including "P02-M05-T02 no longer pins Ceph Object Storage", which **directly contradicts** live §0.7.3, and licence/URL pairs that are factually false (e.g. "Apache Kafka BSL" over redpanda.com URLs; a broken `docs.Apache Airflow.io` URL) | All 9 rows restored to their as-verified 2026-08-19 subjects with italic replacement clarifiers — see FU-01…FU-09 |
| **H-2** | Two PG16-era arithmetic slips survived: "`PostgreSQL 17` reaches EOL 8 Nov 2029 … roughly **month 25**, inside this wave" (month 25 = Nov 2028 = PG16's date; 8 Nov 2029 = month 37) in live `P09-M02-T01` and Appendix I `IRB-04` | Both corrected to month 37 with the Wave-6 / Month-42-benefits framing |

## What was checked and found CORRECT (no action)

- **Pins**: every version in `versions.lock` is exact, `:latest` appears in no
  pin (self-test enforces DE-06); wkhtmltox and Noto Sans Bengali SHA256s
  were genuinely verified during the original implementation; fail-closed
  hash gates precede every install.
- **All five PS files** parse clean (language parser, 0 errors) and are pure
  ASCII (self-test enforces the PS 5.1 BOM/ANSI hazard).
- **Task coverage**: all ten roadmap tasks have an implemented mechanism, a
  Windows adaptation consistent with `D-WS-001`, and a live-executed
  verification (T03 = verify-and-instruct by design; enabling BitLocker is
  deliberately an operator action).
- **Credentials**: none read, stored or emitted anywhere in the tree.
- **The earlier roadmap audit's live-section remediations** (F-01…F-28) were
  spot-verified as genuinely applied — only the appendix residuals (H-1)
  remained, now fixed.

## Post-fix verification (all executed 2026-09-30, this machine)

| Check | Result |
|---|---|
| `verify-workstation.ps1 -SelfTest` | exit 0 |
| Language parser, 5 PS files | 0 errors |
| `machine-inventory.ps1 -OutFile …` | RECOMMENDED; correct OS name; pinned-python probe |
| `verify-workstation.ps1 -Json …` | **8 PASS · 2 WARN · 0 FAIL · exit 0** (T03 in-shell indeterminate, T10 sibling Docker stacks) |
| `setup-workstation.ps1 -DryRun` | exit 0; honest plan (no phantom installs) |
| `install-wkhtmltopdf.ps1` (non-elevated, no `-UserScope`) | exit 2 + remedy (precondition) |

**Open item (operator, not tooling): enable BitLocker** —
`manage-bde -on C:` from an elevated shell, recovery key saved first. Until
then the baseline is RED on T03 (DE-12/SC-009/DE-19), exactly as the record
now states.

---

## Iteration 2 — audit of the fixes themselves (2026-10-01)

> Re-audit of everything iteration 1 produced: every edited file re-read,
> every script re-executed, independent ASCII scan (not just the self-test),
> parser re-run, roadmap table-integrity checks, and a consistency sweep of
> the records iteration 1 wrote. **9 findings — 4 defects in the fixes, 3
> pre-existing gaps the first audit missed, 2 record inaccuracies. All
> fixed; re-verified below.**

| # | Class | Finding | Fix | Verified by |
|---|---|---|---|---|
| **K-1** | Record inaccuracy | Iteration-1 records claimed "20 findings" in three documents (README, P02-M01.md, this file's verdict line); the register contains **19**. The verdict also said "4 logic/consistency defects" — category C has 2 | Counts corrected everywhere; verdict line rewritten with the true breakdown | `grep -rn "20 findings\|20 defects"` → no hits outside this row's own quotation |
| **K-2** | Missed gap (pre-existing) | The self-test's ASCII-purity loop checked only 4 files — `verify-workstation.ps1` was never checked for the PS 5.1 ANSI-parse hazard, despite being the most-edited file | `verify-workstation.ps1` added to its own self-test list | Self-test output lists all 5 files |
| **K-3** | Defect in fix | The DE-18 traps called `Log-Fail`, which does not exist if the failure **is** the module load — the trap itself would then error | Traps fall back to `Write-Host` when `Log-*` is unavailable (setup, installer) | Code inspection; parse clean |
| **K-4** | Missed gap (pre-existing) | `machine-inventory.ps1` header promised exit code "2 preconditions" but no exit-2 path existed, and an unexpected throw exited without any remedy (violating DE-18 like D-1 did) | Trap added (exit 1 + remedy, with Write-Host fallback); exit-code comment now matches reality | Parse clean; live inventory run |
| **K-5** | Defect in fix (edge) | If the registry probe failed, `Get-PlatformInfo` left `ProductName` undefined → blank OS name in every report | Default `"Windows (registry probe failed)"` in the ordered dict before the try block | Code inspection (probe failure path not triggerable on this machine) |
| **K-6** | Weakness (research) | T02 accepted Windows 10 22H2 — past end of support (Oct 2025, ESU excepted) — silently, on a baseline whose encryption controls cite DE-12/SC-009 | T02 now **WARNs** on Windows 10-range builds (build < 22000) with a migration remedy; note added to `versions.lock`; revisit trigger added to D-WS-001 §5 (raise floor to 22000 under a new decision, not a silent edit) | Code + docs; this machine (Win11) still PASSes |
| **K-7** | Weakness (documentation) | Pin-floor semantics were implicit: packages that self-update (git went 2.55→2.56 within a day) drift above their pin, which looked like a DE-06 violation to any future reader | "PIN SEMANTICS" block added to `versions.lock`: pin = install version + verify floor; DE-06 governs container image digests, not workstation package updaters | File content |
| **K-8** | Defect in fix | The inventory JSON renamed a field (`python` → `python312`, added `pythonOnPath`) but kept `schema: …/machine-inventory/1` — a breaking rename inside an unchanged schema version | Schema bumped to `/2` with an inline change note | New evidence JSON shows `/2` |
| **K-9** | Record inaccuracy | The AUDIT_REPORT follow-up verdict claimed `grep ceph/ceph` "returns only the correct live-section uses" — it actually returns **zero** matches after remediation | Wording corrected; noted that the 2026-10-01 re-audit found no further roadmap defects | `grep -n "ceph/ceph"` → 0 hits |

### Iteration-2 verification (all executed 2026-10-01)

| Check | Result |
|---|---|
| Language parser, 5 PS files | 0 errors |
| `verify-workstation.ps1 -SelfTest` (now 5-file ASCII check) | exit 0 |
| `machine-inventory.ps1 -OutFile …-2026-10-01.json` | RECOMMENDED; schema v2 |
| `verify-workstation.ps1 -Json …-2026-10-01.json` | **8 PASS · 2 WARN · 0 FAIL · exit 0** |
| `setup-workstation.ps1 -DryRun` | exit 0, honest plan |
| `install-wkhtmltopdf.ps1` (non-elevated, no `-UserScope`) | exit 2 + remedy |
| Independent `grep -P '[^\x00-\x7F]'` over all 5 PS files | ASCII clean |
| `grep ceph/ceph` over the roadmap | 0 matches |

### Assessed and deliberately NOT changed

- **The 2026-09-30 evidence files were kept** next to the 2026-10-01 ones —
  point-in-time records, not overwritten (iteration 1 had overwritten the
  same-day originals; the audit trail now preserves both dates).
- **T03 wording across documents**: already honest after G-1; re-read and
  confirmed consistent (baseline RED until BitLocker enabled — operator
  action with reboot/recovery-key implications, never done silently).
- **winget exit-code constant** `-1978335189` = `0x8A15002B`
  ("already installed") — recomputed and confirmed correct.
- **The trap-on-module-load edge** in `verify-workstation.ps1` — not
  applicable: it sets `ErrorActionPreference = 'Continue'` and its checks
  handle their own failures; no trap needed.
