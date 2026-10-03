# Fitness-function register baseline + identifier-space resolution (T09)

**Task `P01-M04-T09`** · Closes `B-10a` · Measured 2026-10-01.

## The discrepancy, quantified

| Figure | Source | Measured on disk (this baseline) |
|---|---|---|
| 37 | `AR-012` §4 register | — |
| 127 | `PE-004` §10 | — |
| 187 | "distinct in use" | — |
| **88** | **this run** — unique `FF-nnn` identifiers across `primary-doc`, `project-guide-doc`, `1000fix_ERP_Module` | **the only reproducible figure** |

**Finding F-P01M04-1 (MEDIUM):** the estate's fitness-function population has
three irreconcilable document figures and a measured fourth. Per `RG-08`, the
measured figure with its pattern (`\bFF-\d{3}\b`, whole-estate sweep) is the
baseline; the three document figures are superseded until each cites a
reproducible command.

## Resolution: one register, one allocating authority

- **Register:** `AR-012` is the single fitness-function register; this baseline
  seeds it from the measured 88. Every `FF-nnn` in build artifacts must resolve
  to a register row (the `FF-16` membership principle applied to `FF-` itself).
- **Allocating authority (`DL-08`):** the **Design Authority** allocates `FF-`
  identifiers (fitness functions are architecture-compliance checks — `GV-01`
  already requires Design Authority approval for each new one). The authority
  table in [`docs/p01-m05/identifier-discipline.md`](../p01-m05/identifier-discipline.md)
  names this allocation and every other shared space.
- **Promotion rule unchanged:** a check enters at Warning and promotes to
  Blocking at the named gate (`AR-012` §5.2) — the pipeline enforces what the
  register admits.

## Standing checks already executable in this codebase

| Check | Instrument | Status |
|---|---|---|
| `FF-09` (residency classification present) | `verify-version-currency` + P01-M06 enforcement spec | specified (P01-M06-T05) |
| `FF-14` (dependency reciprocity, `R-03`) | `extract-dependency-graph.ps1` | **executable — 53 failures measured, drift now impossible to miss** |
| `FF-16` (CD-register membership) | `generate-cd-register.ps1` + enablement plan (P01-M05-T08) | register validates at 331 |
| `FF-37` (code-list registration) | P01-M06-T08 code-list register | specified |
