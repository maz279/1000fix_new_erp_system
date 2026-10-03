# NFR, rules, DoD and wave-allocation baselines (T06/T08/T09)

**Tasks `P01-M03-T06`, `P01-M03-T08`, `P01-M03-T09`** · All figures measured
2026-10-01 by the baseline scan (evidence:
`requirements-baseline-2026-10-01.json`).

## T06 — Non-functional requirements baseline

| Check | Claim | Measured | Status |
|---|---|---|---|
| NFR population | 122 (101 source + `NFR-102…122`) | **122 unique ids, exactly `NFR-001…NFR-122`** across the estate | ✅ |
| Sub-identifiers | `NFR-086a/b/c` are sub-ids, **not** duplicates | exactly `NFR-086a`, `NFR-086b`, `NFR-086c` — no others | ✅ |
| Five duplicate identifiers | resolved with a stated rule | RQ-006 §3.3 carries the resolution (`RQA-13` closed: `NFR-088`/`089` whole-row duplicates deleted, `05-06` §6.4 contamination corrected) | ✅ |

**Baselined at 122** with the resolution rule in force. The Safety
characteristic additions `NFR-102…113` remain open against `SC-002` threat
model and `M59` HSE reconciliation (RQ-006 `RQA-21`) — an open dependency,
not a baseline defect.

## T08 — Wave allocation baseline

**Measured (module-granularity, from spec frontmatter, 3,347 rows):**

| Wave | W1 | W2 | W3 | W4 | W5 | W6 | W7 | W8 | W9 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Requirement rows | 358 | 338 | 467 | 533 | 532 | 415 | 310 | 72 | 36 |

- **0 rows in specs without wave frontmatter** (79/79 carry `wave:`) —
  module-granularity allocation is complete on disk.
- **286 rows sit in 2 multi-wave modules** (`W1 (core) → W2 (complete)`
  patterns) — the per-requirement split inside them is the genuine residual.
- **The 1,816-unallocated (54%) claim reconciles as follows:** it is
  *requirement-level* allocation status held in the programme tool
  (`GV-004` §5.5), not derivable from frontmatter — module-level waves exist
  for every spec, but a requirement's wave inside a multi-wave or large module
  is unassigned until squads decompose. **The residual worklist is: 286
  multi-wave rows + 42 SWR + the intra-module requirement-to-wave split** —
  recorded so `SPR-11` can trend it at gates. Register:
  [`registers/wave-allocation.csv`](registers/wave-allocation.csv).

## T09 — Business rules and DoD baseline

| Check | Claim | Measured | Status |
|---|---|---|---|
| `05-05` catalogue | 140 rules | **140 unique `BRU-*` ids** | ✅ |
| Module §9 rules | 1,330 | **1,330 `BRU-` table rows** across 79 specs | ✅ |
| `05-05` module coverage | 20 of 67 module codes | confirmed by RQ-009 `EO-02` (extended) — **47 modules have no `05-05` rules**, incl. **M40** and **M42** | ⚠ recorded, as the roadmap directs |
| M40/M42 rules in their specs | 41 / 27 (RQ-009 `EO-02`) | **20 / 20 §9 BRU rows measured on disk** — **finding F-P01M03-2: RQ-009's own figure is unreconciled** | ⚠ reconcile (RG-08) |
| Acceptance criteria | 1,568 (module §17) | **1,568 `AC-nn` table rows** measured (ids are module-local) | ✅ |
| DoD standard | `DoD-01…17` (`02-02` §8) | present per RQ-010 §4.3 (module DoD applies per module at its wave) | ✅ |

**Baselined:** rules 140 + 1,330; acceptance criteria 1,568; DoD-01…17 in
force. The M40/M42 `05-05` absence is **recorded rather than left to surprise
the team** (roadmap wording), and `FF-53` coverage reporting will see it from
day one. The `BRU-ECM` ten-identifier collision (RQ-009) is an existing
register defect for `RR-002` to resolve — flagged, not silently fixed.
