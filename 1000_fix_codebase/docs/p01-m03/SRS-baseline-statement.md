# SRS baseline statement — the single requirement denominator (T03)

**Task `P01-M03-T03`** · Measured 2026-10-01 by
[`tooling/requirements-baseline/scan-requirements.ps1`](../../tooling/requirements-baseline/scan-requirements.ps1)
(evidence: `requirements-baseline-2026-10-01.json`) · **CR-02: every figure
below carries the timestamp that made it true.**

## The baseline (RG-08-stamped)

| Figure | Value | Basis | Status |
|---|---:|---|---|
| Module requirement rows | **2,989** | `CR-01` command, 67 M-specs | ✅ measured = RQ-001 §3.10.5 |
| Portal requirement rows | **358** | `CR-01` command, 12 P-specs | ✅ measured = RQ-001 |
| **Adopted requirement rows** | **3,347** | 2,989 + 358, **0 duplicate ids** | ✅ measured = RQ-001 |
| `SWR` supplements | **42** | unique `SWR-001…042` in RQ-001 §9.6.12 | ✅ measured = RQ-001 |
| **Engineering population** | **3,389** | 3,347 + 42 | ✅ **baselined at this figure** |
| Contracted figure | 2,930 | `PGD-000`/README, provenance unstated | Non-authoritative (RQ-001 §3.10.5 table); retained for contract reconciliation — the 459-row difference is the historical scope gap **B-11 resolved around** (§0.7 of IR-002) |

**Counting rule in force:** `CR-01` — rows matching
`^\| *FR-[A-Z0-9]+-[0-9]+[a-z]?` in module/portal §5 tables; never the
highest allocated identifier, never range sums. **No coverage, effort or
completeness figure may be published against any other denominator** (`CR-02`).
The denominator moves only under `RQ-005` change control and is re-stamped at
every wave gate (`CR-03`) — the scan tool is that re-stamp, executable.

## Superseded figures (do not quote)

1,180 (superseded 30-module basis) · ~2,352 (mixed basis, `RG-05`-prohibited) ·
2,930 (provenance unstated) · 3,343 (audit figure, superseded by the
reproducible 3,347).

## Primary-document basis (T01, measured same run)

4 documents, **17,680 lines** (RFP 3,942 · BRD 4,525 · URD 4,815 · TSS 4,398)
— measured = the roadmap's reading basis exactly. 79 delivery-unit
specifications confirmed on disk (67 M + 12 P; 19 governance files counted
separately) — measured = the roadmap's T02 basis exactly.
