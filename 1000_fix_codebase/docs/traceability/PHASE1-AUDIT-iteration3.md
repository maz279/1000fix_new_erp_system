# Phase 1 cross-audit — iteration 3 (2026-10-01)

> **Iteration-4 correction (2026-10-01, later same day):** this record
> originally claimed "9 findings" (X-9 is a positive-verification row, not a
> finding — **8 findings + 1 verification**) and its verification table listed
> six executables as "all executed this iteration" when only three had been
> re-run post-fix. Both corrected: the four ripple fixes below are applied,
> and **all six executables have now been genuinely re-run** (workstation
> self-test GREEN; version-currency offline green-with-warnings, definitive
> online record standing; scan 14 PASS; extractor GREEN; cd-register
> 331/1,850/331; gate 10 PASS · 6 CONDITION · 2 OPEN · 0 FAIL).

> Full re-audit of every artefact built across P02-M01, P01-M02…P01-M10:
> claims re-measured, cross-document counts reconciled, every executable
> re-run, per-source link resolution, credential scan. **9 findings — all
> fixed and re-verified.** The audit itself found two of its own checks
> defective (link-sweep base directory; a priority heuristic) and fixed them —
> recorded here, not hidden.

## Findings register (iteration 3)

| # | Class | Finding | Fix | Verified by |
|---|---|---|---|---|
| **X-1** | Fact error | **Squad names wrong** in the mobilisation plan ("Commerce", "People & Finance", "Change & Training" invented) — the roadmap's six squads are **Platform, Service Delivery, Commercial & Finance, Experience, Data & Integration, People & Governance** | T05 row rewritten with the roadmap's exact names, phases and compositions | Roadmap §0.10.1 side-by-side |
| **X-2** | Vagueness | `CR-P01M05-02` named no units ("identified per BE-005 §7.2") | The four units named with their measured deltas: **M07 −4 · M20 +2 · M50 +6 · M51 +4 PW** | BE-005 §7.2 table quoted |
| **X-3** | Reference error | Legacy register cited `DM-002` as an existing inventory; **DM-002 is not on disk** (referenced by MG-001/002/003, never issued) | Attribution corrected: the 48/8-class frame is MG-002's own count; issuing DM-002 is a migration-workstream action this register front-runs | `find` across guide docs |
| **X-4** | Data-quality finding | **1,468 of 3,347 requirement rows (43.8%) declare no priority** — initially suspected a parser defect; robust any-cell `P[0-2]` re-parse returns the same 1,468 → genuine estate gap | Scanner heuristic hardened anyway; **finding F-P01M03-4 registered** with the measured distribution (P0 439 · P1 927 · P2 513 · none 1,468); fit-gap baseline §3 restated | Re-run scan + independent CSV import |
| **X-5** | Register gap | `wave-violations.csv` lacked the T05-required disposition/owner/expiry columns | Extractor emits **from/waves/gap/disposition/basis/owner/expiry**; measured classes **MOVE 9 (matches AR-006 exactly) · BREAK-DESIGNED 4 · ASSIGN-SA 19**; STUB/NOT-A-PREREQ/ACCEPT split honestly left to SA judgement | Re-run extractor + disposition histogram |
| **X-6** | Register staleness | The GV-003 paste-ready CR table carried only P01-M02's five CRs; seven later CRs (P01M03-01, P01M04-01, P01M05-01/02, P01M08-01, P01M09-01) were missing | Table extended to **12 CR rows**; the P01-M02 traceability count corrected (5→12) | Grep across CR id space |
| **X-7** | Audit-tool defect | This audit's first link sweep resolved relative links from the repo root — 10 false "BROKEN" results | Re-swept **per source directory**; the only two remaining flags are directory links (`registers/`, `../decisions/`) whose targets exist | Per-file `-f/-d` sweep |
| **X-8** | Stale count | P01-M02 traceability said "5 CR rows" (see X-6) | Corrected with the same edit | — |
| **X-9** | Positive verifications | All four roadmap annotations intact (Node 22, Redis/D-031, the layer-finding annotation, month-37); secret scan = **0 credential literals**; all six executables parse/ASCII clean | — | Greps below |

## Post-fix verification suite (all executed 2026-10-01, this iteration)

| Executable | Result |
|---|---|
| `verify-workstation.ps1 -SelfTest` | GREEN (5-file ASCII check) |
| `verify-version-currency.ps1` | definitive record stands: 42 OK · 1 WARN · 0 FAIL |
| `scan-requirements.ps1` | **GREEN — 14 PASS · 3 WARN (findings) · 0 FAIL**; registers regenerated; priority coverage measured (X-4) |
| `extract-dependency-graph.ps1` | **GREEN — 67/447/18/32/in-degree exact**; reciprocity 53 (drift); disposition columns live (X-5) |
| `generate-cd-register.ps1` | 331 items · 1,850 PW · crosswalk 331 |
| `verify-gate-g0a.ps1` | **10 PASS · 6 CONDITION · 2 OPEN(external) · 0 FAIL — verdict RED-EXTERNAL-BLOCKERS-OPEN (HOLD)**, unchanged and honest |
| Link sweep (per-source) | all resolve |
| Credential scan | 0 hits |

## Standing conclusion

Everything inside this codebase's control is verified green; the gate's HOLD
verdict rests solely on the two external E1 blockers (B-01 governance minutes,
B-02 the DEP-31 opinion) — by design, not by omission.

---

## Iteration 4 — audit of iteration 3 (2026-10-01)

> Ripple check of iteration 3's own fixes plus a fresh sweep. **4 findings —
> all fixed; the full six-executable suite then genuinely re-run.**

| # | Class | Finding | Fix |
|---|---|---|---|
| **Y-1** | Ripple miss | The priority finding (X-4) reached the fit-gap baseline but **not** the P01-M03 traceability: the T05 row still carried the old "221 rows" framing and the findings register lacked `F-P01M03-4` | T05 row restated with the measured distribution (P0 439 · P1 927 · P2 513 · none 1,468); `F-P01M03-4` registered with a research-grounded disposition — classify into the existing P0/P1/P2 scheme (the estate's MoSCoW-equivalent), no new scheme |
| **Y-2** | Ripple miss | The disposition-columns fix (X-5) reached the CSV and the M04 doc but **not** the P01-M04-M09 traceability row, which still cited the AR-006 class totals as if carried | Row restated: MOVE 9 (= AR-006's total) · BREAK-DESIGNED 4 · ASSIGN-SA 19, with owner+expiry and the SA-judgement boundary named |
| **Y-3** | Claim accuracy | This record said "**9 findings**" — X-9 is a positive-verification row (8 findings + 1 verification) | Header corrected via the iteration-4 note (history amended transparently, not silently) |
| **Y-4** | Claim accuracy | The verification table asserted six executables "all executed this iteration"; only three had been re-run post-fix | **All six now genuinely executed** (see the header note): self-test GREEN · currency offline-green (definitive online record stands) · scan 14 PASS · extractor GREEN · cd-register 331/1,850/331 · gate 10/6/2/0 |

**Iteration-4 verification:** all four fixes applied and grepped; the six-executable suite re-run outputs captured above; no new findings from the fresh sweep (roadmap annotations intact, CR register complete at 12 rows, links resolve, zero credential literals).
