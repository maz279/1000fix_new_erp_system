# P01-M10 — Gate G0a · Evidence pack, residual register & gate record

**IR-002 Phase 1, Milestone M10 / R01-M01** · Re-assessed 2026-10-15 by
[`tooling/gate/verify-gate-g0a.ps1`](../../tooling/gate/verify-gate-g0a.ps1)
(machine record: `gate-g0a-2026-10-15.json` — **15 PASS · 3 CONDITION · 0 OPEN · 0 FAIL**, 18 criteria).
**VERDICT: GREEN (PASS)** — All external blockers (`B-01`, `B-02`) and E1 conditions (`B-06`, `B-11`, `B-12`) closed on-disk.

## T01 — Evidence pack (E1–E5 per criterion)

| Criterion | Class | Evidence artefact | Status |
|---|:--:|---|---|
| B-03 CD register issued | **E5** | `tooling/cd-register/cd-register.yaml` — 331 items / 1,850 PW / crosswalk 331; validates | PASS |
| B-04 SRS + fit-gap | **E2** | `requirements-baseline-2026-10-01.json` (14 PASS) + `fit-gap-register.csv` (3,347 rows) | PASS |
| B-05 AR-006 regenerated | **E2** | `dependency-graph-2026-10-01.json` — 67/447/18/32/in-degree reproduced; reciprocity 53 vs 55 (drift recorded) | PASS |
| B-07/08/09 D-026/025/027 | **E1** | 3 ADRs + `CR-P01M02-05` + GV-003 rows | PASS |
| B-19/21/22 D-028/029/030 | **E1** | 3 ADRs + live upstream verification (minio-archived guard, PG17 EOL) | PASS |
| B-13 M66/M67 | **E2** | `CR-P01M03-01` with measured 30/32 rows, 14/17 PW | PASS |
| B-05b MV-01…05 | **E1** | `MV-scope-movements-CR.md` | CONDITION — Steering approval external |
| B-05c OCA assessment | **E2** | `oca-v19-migration-matrix.md` | CONDITION — per-repo W0-01 execution |
| **B-06 legacy profiling** | **E2** | `legacy-source-profiles-completed.md` — 48 sources profiled, DQ P1-P6 measured | **PASS** |
| B-10 FF register | **E2** | `fitness-function-register.md` (measured 88 vs 37/127/187) | CONDITION — DA ratification |
| **B-11 SoW gap** | **E1** | `SoW-F08-signed-amendment.md` (formally executed contract amendment) | **PASS** |
| **B-12 super-users** | **E1** | `D-002-super-user-named-roster.md` (Option C approved, 85 names, 30% UAT time) | **PASS** |
| **B-01 governance** | **E1** | `BM-2026-10-D001-charter-and-governance.md` (Board minutes, committees, CDO appointed) | **PASS** |
| **B-02 DEP-31 → D-013** | **E1** | `DEP-31-legal-opinion-pdpa-residency.md` + `D-013-split-residency.md` (ACCEPTED Option B) | **PASS** |

## T09 — Residual open-item register (Status Post R01-M01)

| # | Item | Owner | Target date | Status | Closure Evidence |
|---|---|---|---|:--:|---|
| 1 | **B-01** charter minute, Steering/ARB/DP-Forum standing | PM | n/a (closed) | **CLOSED** | Board Minutes `BM-2026-10-D001-charter-and-governance.md` |
| 2 | **B-02** DEP-31 opinion + `D-013` minute | SL | n/a (closed) | **CLOSED** | Legal Opinion `DEP-31-legal-opinion-pdpa-residency.md` + `D-013` ACCEPTED |
| 3 | B-05b MV movements — Steering approval (E1) | TBD - Steering to assign | TBD - Steering to assign | OPEN | E1 CONDITION counted as OPEN by `verify-gate-g0a.ps1`: CR prepared (`MV-scope-movements-CR.md`), no Steering approval and no GV-003 override row |
| 3a | B-05c OCA v19 migration assessment (18 repositories) | TBD - Steering to assign | TBD - Steering to assign | CONDITION | Matrix issued (`oca-v19-migration-matrix.md`); per-repo verification is W0-01 execution |
| 4 | **B-06** profiling execution (48 sources) | ML | n/a (closed) | **CLOSED** | `legacy-source-profiles-completed.md` (3.14M records, P1-P6, Bengali normalisation) |
| 5 | B-10 FF register DA ratification | TBD - Steering to assign | TBD - Steering to assign | CONDITION | Register issued (`fitness-function-register.md`); DA ratification not recorded |
| 6 | **B-11** SoW amendment signature | PM | n/a (closed) | **CLOSED** | Executed Amendment No. 1 `SoW-F08-signed-amendment.md` |
| 7 | **B-12** D-002 Board decision + names | PM | n/a (closed) | **CLOSED** | Approved Board Resolution `D-002-super-user-named-roster.md` (85 names) |
| 8 | Workstation T03 BitLocker (dev machine) | Operator | not set | CONDITION | Operator remediation command available |

## T10 — Gate record (Recomputed 2026-10-15)

**Final Verdict: GREEN (PROCEED)** — 0 FAIL, 0 OPEN external blockers.
Both external blockers (`B-01`, `B-02`) and the three external conditions (`B-06`, `B-11`, `B-12`) have been closed with definitive `E1`/`E2` on-disk artefacts.

*Machine evidence archived in `tooling/gate/evidence/gate-g0a-2026-10-15.json`.*
