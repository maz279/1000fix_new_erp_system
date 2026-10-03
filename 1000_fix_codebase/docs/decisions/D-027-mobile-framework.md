# D-027 — Mobile framework: Flutter

| | |
|---|---|
| **Decision ID** | `D-027` |
| **Date** | 2026-10-01 |
| **Status** | ACCEPTED |
| **Deciders** | Chief Architect (`CA`) on the authority of the ARB, with the Mobile lead (`MB`) |
| **Allocating authority** (`DL-08`) | `GV-002`; recorded in `AR-004`, cross-referenced from `GV-003` (`P01-M02-T09`) |
| **Closes** | `BE-001` `Q-01` (mobile toolchain ambiguity); reconciles 3 Flutter vs 5 React-Native/unstated CD items (`BE-005` §9.1) |
| **Raise under** | `GV-003`; `AR-013`; `AR-010` |

## 1. Context

`BE-005` §9.1 records 3 CD items declaring Flutter and 5 declaring React
Native or leaving the framework unstated. Three estate facts decide this,
not preference:

1. **`AR-010`'s offline engine is specified in Dart** — the technician app's
   offline-first sync engine (the single hardest mobile component) is already
   designed for Flutter's runtime.
2. **`UX-001` §3.3 rejects React Native** on interaction-fidelity grounds for
   the technician PWA/app split.
3. **One toolchain per workstation** (`BE-001` `Q-01`): leaving both in the
   estate keeps two mobile toolchains, two widget systems and two upgrade
   calendars on every developer machine.

**Version-currency verification, 2026-10-01** — Flutter **3.44** is confirmed
upstream (flutter.dev blog *What's new in Flutter 3.44*; tracking issue
flutter/flutter#184093): **Material and Cupertino are frozen in the core
framework and move to standalone `material_ui` / `cupertino_ui` packages;
Impeller is the default renderer on Android; Dart 3.12 ships alongside.**
Four applications (technician, rider, auditor, customer) and the shared
`fix_ui` package are affected — the pin must be deliberate, not "newest".

## 2. Options considered

| Option | Assessment |
|---|---|
| **Flutter (via fvm, pinned)** | Matches `AR-010` (Dart offline engine), `UX-001`; one toolchain; single-skilled squad |
| React Native | Contradicts `UX-001` §3.3; forces a Dart→TS rewrite of the offline engine design; splits the toolchain |
| "Leave per-app" | Rejected — `Q-01` exists because ambiguity already cost a toolchain on every workstation |

## 3. Decision

1. **All four mobile applications and the `fix_ui` shared package are
   Flutter**, managed through **fvm** with the version pinned in `.fvmrc`
   (install path: `P02-M02-T03`).
2. **The five React-Native/unstated CD items are reallocated to Flutter** and
   their specifications annotated — executed item-level by
   **`CR-P01M02-05`** (`docs/p01-m02/CR-mobile-reallocation-D027.md`: APP-09 /
   P07 mobile surface → PWA on Next 16.3 in W7, native-in-Flutter only if
   separately approved, resolving TSS `D-17`/`TSA-06`); `DL-08` — the
   allocating authority for `CD-` items is `BE-005` §6.
3. **Pinning guidance:** pin the Flutter line deliberately **after** reading
   the 3.44 migration notes (Material/Cupertino extraction, Impeller default).
   `fix_ui` adopts `material_ui`/`cupertino_ui` at a named migration task, not
   opportunistically.

## 4. Consequences

- `Q-01` closed: one mobile toolchain on the workstation baseline; React
  Native never enters `versions.lock`.
- `P02-M02-T03` executes (it was conditional on this decision).
- The 3.44 structural change is a Wave-0 migration cost carried by `fix_ui`
  first, applications second.

## 5. Revisit triggers

- Flutter reversing the Material/Cupertino extraction, or Impeller regression
  on the target Android floor → re-pin under a new ADR.
- A fifth application with a hard RN-only dependency (e.g. an existing client
  app that must be absorbed) → new decision; this one does not bend silently.
