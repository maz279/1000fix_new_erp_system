# CR-P01M02-05 — Mobile framework reallocation under `D-027` (P07 / APP-09)

| | |
|---|---|
| **CR ID** | `CR-P01M02-05` |
| **Date** | 2026-10-01 |
| **Raised against** | `04-00` §2 ("Next.js 15 + React Native"); `BE-005` §9.1 mobile CD rows; resolves TSS open decision `D-17` (TSA-06) by recorded position |
| **Allocating authority** (`DL-08`) | `D-027` (ACCEPTED, `docs/decisions/D-027-mobile-framework.md`) allocates the mobile framework; CD-item rows are `BE-005` §6's to re-issue |
| **Owner** | Chief Architect (`CA`); CTO confirms the `D-17` surface position at its W6 checkpoint |

## 1. What changes

| Item | Was (per source documents) | Now (per `D-027` + TSS §11.9 position) |
|---|---|---|
| **`APP-09` / `P07` Marketplace Seller Portal & App** (W7) mobile surface | `04-00` §2: "React Native"; `02-05` §5.4: Next.js only; RFP §7.2: "mobile" unqualified — **three documents, three answers (TSA-06)** | **Progressive Web App on the Next.js 16.3 codebase in Wave 7** (per `D-026`). A native seller app is a **separately approved** W8+ item, **built in Flutter if approved** — so the estate carries one mobile framework |
| The four field applications (technician, rider, auditor, customer) + `fix_ui` | 3 CD rows Flutter, others unstated | **All Flutter** (`D-027`) — no row changes needed beyond the register annotation |
| React Native anywhere in the estate | Declared by `04-00` | **Removed.** React Native never enters `versions.lock` or any workstation |

## 2. Why (the recorded reasoning)

1. **`AR-010`'s offline engine is Dart; `UX-001` §3.3 rejects React Native** — the
   estate's own architecture documents decide this (`D-027` §1).
2. A second mobile framework costs **two toolchains, two offline engines, two
   CI pipelines and two skill sets for one additional application** (TSS §11.9).
3. **Upstream fact (verified via TSS §25.2.5 currency note, 2026):** React
   Native's legacy architecture has been **removed as of 0.83** — the New
   Architecture is mandatory. Adopting React Native now means adopting its
   newest architecture with no compatibility bridge; the migration risk lands
   on a single W7 application.

## 3. `D-017` disposition

TSS open decision `D-17` ("P07 mobile surface — PWA now, Flutter later, or
React Native", CTO, Wave 6) is **resolved by this CR's recorded position**:
PWA in W7; native-in-Flutter only if separately approved. The CTO's W6
confirmation converts "recorded position" to "closed" — tracked as a RAID row
so it cannot be silently forgotten.

## 4. Verification

- `BE-005` §9.1 re-issued with the annotation: every mobile CD row names
  Flutter (four apps) or PWA-on-Next (APP-09 mobile surface).
- `D-027` ADR §3.2 already carries the reallocation ruling; this CR is its
  item-level execution.
