# P01-M10 — Gate G0a · Evidence pack, residual register & gate record

**IR-002 Phase 1, Milestone M10** · Assessed 2026-10-01 by
[`tooling/gate/verify-gate-g0a.ps1`](../../tooling/gate/verify-gate-g0a.ps1)
(machine record: `gate-g0a-2026-10-01.json` — **10 PASS · 6 CONDITION · 2 OPEN(external) · 0 FAIL**, 18 criteria).

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
| B-06 legacy profiling | **E2** | 48-source register + rulings issued | CONDITION — ~4-week execution |
| B-10 FF register | **E2** | `fitness-function-register.md` (measured 88 vs 37/127/187) | CONDITION — DA ratification |
| B-11 SoW gap | **E1** | `SoW-F08-resolution.md` (baseline-citing clauses) | CONDITION — signature external |
| B-12 super-users | **E1** | `D-002-super-user-availability.md` | CONDITION — Board + named individuals |
| **B-01 governance** | **E1** | **OPEN** — Board/Steering/ARB/DP-Forum minutes (P01-M01) | **OPEN** |
| **B-02 DEP-31 → D-013** | **E1** | **OPEN** — external legal opinion (6–10 wk); D-013 PREPARED for same-day taking | **OPEN** |

## T09 — Residual open-item register (nothing closes by omission)

| # | Item | Owner | Date target | Consequence if missed |
|---|---|---|---|---|
| 1 | **B-01** charter minute, Steering/ARB/DP-Forum standing | PM | Day 1 | No approval of anything is valid (`PGD-A1-09`); G0a cannot convene |
| 2 | **B-02** DEP-31 opinion + `D-013` minute | SL | Day 1 +6–10 wk | **G0a fails; Phase 3 does not start**; every persistent-state task holds (P01-M06 interim ruling carries) |
| 3 | B-05b MV movements — Steering approval | CA | G0a | 25 of 32 wave violations unresolved; W1 buildable-order claim lapses |
| 4 | B-06 profiling execution (48 sources) | ML | ~4 wk | `G1-05` fails at the next gate |
| 5 | B-10 FF register DA ratification | CA | G0a | `FF-16` enablement (condition 1 of 5) unblocks without the register it checks |
| 6 | B-11 SoW amendment signature | PM | Before contract signature | Live commercial exposure carried into every subsequent gate |
| 7 | B-12 D-002 Board decision + names | PM | G0a | UAT acceptance model unevidenced — the binding programme constraint |
| 8 | Workstation T03 BitLocker (dev machine DESKTOP-CVE1HTI) | Operator | Before Phase 2 | Baseline RED per DE-12/SC-009/DE-19 (evidence on file, 2026-09-30/10-01) |

## T10 — Gate record (template, per GV-009 §6.3–6.4)

**Verdict available today: HOLD** — 2 external E1 blockers open. The Steering
outcomes and their consequences:

- **Proceed:** requires B-01 + B-02 closed with E1 minutes — not available today.
- **Proceed-with-conditions:** permissible only as a recorded Steering decision
  naming each condition, owner and date — the residual register above is the
  menu; conditions 3–8 are the shape of it.
- **Hold:** the default while B-01/B-02 are open; Phase 2 (G0b) entry requires
  "`G0a` passed, or a Steering-recorded override" — the override, if taken,
  lands in `GV-003`, never in silence.

*The gate verifier re-runs at Steering: `powershell -ExecutionPolicy Bypass
-File tooling\gate\verify-gate-g0a.ps1 -Json <record>` — the verdict is
recomputed from artefacts, not remembered.*
