# Flutter / Dart layer runbook (structural mode — no SDK on this box)

## Hard constraint

No Dart SDK / Flutter toolchain on this dev machine. Therefore:
- NEVER claim a mobile fix is "verified" — say "structurally validated".
- Structural gates are BLOCKING and run in the fitness battery:
  - `python tooling/fitness/check-dart-offline.py` (FF-41) — AR-010
    mandates in the engine source.
  - `python tooling/fitness/check-dart-apps.py` (FF-42) — all 4 apps
    consume fix_ui tokens (zero hand-hex), consume THE one engine
    (fix_offline, FL-03), customer app Bengali-first (DE-17).
- First SDK-equipped machine must run `flutter analyze` over
  `libs/dart/fix_offline` + all 4 `apps/mobile/*` before closing any
  mobile work (also `flutter test` once a test harness exists).

## Map

| Piece | Path | Gate |
|---|---|---|
| Offline engine | `libs/dart/fix_offline/lib/src/*.dart` | FF-41 |
| Shared UI kit | `libs/dart/fix_ui/lib/` (fixColor bridge, theme/tokens.dart generated) | FF-42 |
| P02 technician | `apps/mobile/technician/lib/main.dart` | FF-42 |
| P09 rider | `apps/mobile/rider/lib/main.dart` | FF-42 |
| P11 auditor | `apps/mobile/auditor/lib/main.dart` | FF-42 |
| APP-04 customer | `apps/mobile/customer/lib/main.dart` (Bengali-first) | FF-42 |

## Engine invariants (break one = break offline guarantees)

- **SP-07 upload-first**: sync() uploads BEFORE download — code order
  enforces it; keep it.
- **DI-05 idempotency**: journal acknowledge/reject/markInFlight must
  tolerate double-calls — **never `firstWhere` without a null-safe loop**
  (PP4 scar: `Bad state: No element` on retry).
- **AR-010 §6 two-state disclosure**: `notYetSynced` ≠ `syncedAndRejected`;
  ConflictDisclosure must render both distinctly.
- **SP-09 deferred evidence**: EvidenceChannel stays non-blocking/resumable.
- Command model: client-UUID idempotency key; 4-state lifecycle; non-null
  `createdAt` (PP4 scar: passing `createdAt: null` to non-nullable
  DateTime was a compile error unseen until structural review).
- Engine is PURE LOGIC: no fix_ui/Flutter dependency in fix_offline.

## Colors / theme

Generated tokens at `libs/dart/fix_ui/lib/theme/tokens.dart` (from the
DTCG source via tooling/generators/generate-design-tokens.py). Apps use
`fixColor("token-hex")` — a literal Color(0x…) in a main.dart fails FF-42.

## Typical structural-debug session

1. Reproduce logically from the report (e.g., "double-tap sync crashes").
2. Read the exact method in fix_offline; check invariants above.
3. Patch with safe-loop/StateError pattern; keep contracts.
4. `check-dart-offline.py` + `check-dart-apps.py` + battery.
5. Mark "pending flutter analyze" in the record.
