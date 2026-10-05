# Definition of "100% Deployable" — verification matrix

A claim of 100% requires every row green, machine-checked where possible. Gate GP
(`tooling/gate/verify-gate-gp.ps1`, created in PP7) aggregates these alongside G0b–G8.

## The matrix

| # | Criterion | Check | Target |
|---|---|---|---|
| D1 | Asset coverage — navigation registry fully resolved | Registry screen keys → Odoo menu/action (back office) or portal route (external); function register (5,100) → backend capability | 100% resolved; every exception documented with owner+date |
| D2 | Report coverage | 346 registry reports → QWeb/Superset realisations | 100% |
| D3 | Journey coverage | All 10 journeys (J01–J10) across 54 discrete steps mapped to automated Playwright (R1/R2) & Flutter Patrol (R4) test suites (`ARCHITECTURE_STATE.md` §8); 0 test flakiness | 100% pass |
| D4 | Fixture-free artifacts | `check-no-fixtures.py` over apps/libs/shipped bundles | 0 findings |
| D5 | No hard-coded data | grep sweeps: literals in render paths, PRNG in components, demo branches | 0 findings |
| D6 | Same-code-path data | Screen renders from API in seed and prod modes; only API base URL differs by env | Verified per portal via staging UAT on migration-staging |
| D7 | Tokens | One DTCG source; all runtimes generated; CFM-01…05 green on R1/R2/R4 (+R3/R5 where shipped) | Green ×5 realisations |
| D8 | i18n | `counterpart_pending == 0`; bn_BD.po 100%; bn UI parity spot-suites; BN-007 formatters used for ৳/dates/numerals | 0 pending; parity pass |
| D9 | Accessibility (WCAG 2.2 AA) | axe-core + manual per QA-008: 0 critical/serious violations; touch targets at the house floor **`dimension.target.minimum = 44px`** (the DTCG token — 48px is not the contract); body-text contrast ≥ 4.5:1 (AA — 7:1 is AAA, applied only where the tokens already choose it); visible `:focus-visible` rings; modal focus traps; sequential headings | 0 critical/serious violations; per-portal audit trail |
| D10 | Performance Budgets | P01 critical path < 400 KB gzip on 3G (the contractual budget — roadmap P02-M07-T07); Lighthouse budgets on all portals; OWL asset bundle budget guard. *(INP/LCP thresholds and 60 FPS on 10k-row grids: PROPOSED PP7 targets — benchmark and ratify before they become criteria; not current DoD)* | Contracted budgets met; proposed targets ratified-or-dropped with evidence |
| D11 | Security | No credential literals; SSRF guard on server fetches; OIDC flows correct; portal ACL negative tests (portal user cannot reach back office — pattern exists in smoke) | Clean review + tests |
| D12 | Offline (mobile) | `libs/dart/fix_offline` engine verified: SQLCipher encryption, SP-07 upload-first journal, AR-010 3-way conflict state machine (financial server-authoritative, operational union-merge), L-suite (33 scripts) green, background binary media isolate non-blocking (`ARCHITECTURE_STATE.md` §7) | Green; 0 data loss under network partitions |
| D13 | Contracts | Every API path in `contracts/openapi/` has PS-11 contract tests; zero undocumented paths used by apps | Green |
| D14 | Build & deploy | `build once, promote`: same artefact promotes dev → test → staging → prod; health checks (`/healthz`, `/readyz`); DB migrations run; rollback rehearsed | Drill record |
| D15 | Estate non-regression | Full battery (531 addons + 194 service = 725 tests, fitness 8/8, comodel-deps, G0b–G8, smoke 14/14, seed double-run) green at every phase tag | Green at pp0…pp7 |
| D16 | Data readiness | Migration rehearsal at production volume with MIG-02 control totals reconciled; business sign-off recorded before any legacy decommission | Signed record |
| D17 | Security headers & Gateway Policy | CSP with per-portal cryptographic nonces; HSTS (`max-age=63072000; includeSubDomains; preload`); `frame-ancestors` strictly scoped for embedded BI (P06); CORS strictly pinned at Kong 3.9; automated header checks in CI | Automated header checks green |
| D18 | Frontend Observability | OTel distributed traces (browser $\rightarrow$ Kong $\rightarrow$ Odoo) on all transactional workflows; RUM performance telemetry streaming to TimescaleDB/Grafana; error tracking & live alerts | End-to-end trace sampling verified; dashboards live |
| D19 | External-fact currency | Every technology claim carries a verified-on date $\le 90$ days at execution time (version-currency ritual); `06-EXTERNAL-FACTS.md` updated at each phase gate | Ritual record at PP1/PP3/PP5/PP7 |

## Environment ladder (the twelve environments — named per the roadmap)

`local` (synthetic only) → `ci` (ephemeral) → `dev` → `sit` → `uat` → `perf`
(1.5× peak) → `staging` (masked production clone) → `training` → `sandbox`
(partner certification, synthetic) → `migration-staging` (production-volume
rehearsal) → `prod` → `dr` (warm standby, RPO ≤ 15 min, RTO ≤ 2 h).

Portals deploy as artefacts through the same ladder; Odoo keeps its own upgrade
cadence (protection P-06 / freeze rules). NFR-086c is absolute: no unmasked
residency-classified data outside `prod`/`dr` Z4 — masking runs inside the clone job.

### App-count reconciliation (RG-08: every counted figure carries its basis)

The roadmap's L5 line says "8 Next.js apps · 3 Flutter apps" while its monorepo tree
shows **7 Next.js directories** (`customer, corporate, analytics, seller, brand,
agent-console, partner` — P05's Next.js half lives beside its Odoo-portal half, P06's
Next.js shell embeds BI rather than being a standalone portal) and **4 Flutter
directories** (`technician, rider, auditor, customer`). This programme counts by
**monorepo directory**: 7 web + 4 mobile = 11 apps, realising 12 portals + APP-04.
The discrepancy is recorded here, not silently resolved — it follows the roadmap's own
identifier-discipline rule (RG-08) and will be reconciled in the CD register during PP1.

## Sign-off

- Gate GP green → PM publishes the porting completeness statement (every gap named,
  owned, dated — the roadmap's "nothing closed by omission" rule).
- Residual register published with the statement; MS-11 closure in Phase 12 consumes it.
