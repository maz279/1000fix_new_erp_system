# Definition of "100% Deployable" — verification matrix

A claim of 100% requires every row green, machine-checked where possible. Gate GP
(`tooling/gate/verify-gate-gp.ps1`, created in PP7) aggregates these alongside G0b–G8.

## The matrix

| # | Criterion | Check | Target |
|---|---|---|---|
| D1 | Asset coverage — navigation registry fully resolved | Registry screen keys → Odoo menu/action (back office) or portal route (external); function register (5,100) → backend capability | 100% resolved; every exception documented with owner+date |
| D2 | Report coverage | 346 registry reports → QWeb/Superset realisations | 100% |
| D3 | Journey coverage | 10 journeys → E2E suites (web + mobile as applicable) | 100% pass |
| D4 | Fixture-free artifacts | `check-no-fixtures.py` over apps/libs/shipped bundles | 0 findings |
| D5 | No hard-coded data | grep sweeps: literals in render paths, PRNG in components, demo branches | 0 findings |
| D6 | Same-code-path data | Screen renders from API in seed and prod modes; only API base URL differs by env | Verified per portal via staging UAT on migration-staging |
| D7 | Tokens | One DTCG source; all runtimes generated; CFM-01…05 green on R1/R2/R4 (+R3/R5 where shipped) | Green ×5 realisations |
| D8 | i18n | `counterpart_pending == 0`; bn_BD.po 100%; bn UI parity spot-suites; BN-007 formatters used for ৳/dates/numerals | 0 pending; parity pass |
| D9 | Accessibility | axe + manual per QA-008: WCAG 2.2 AA on all portals; keyboard paths; focus rings; 390px responsive | 0 critical/serious |
| D10 | Performance | P01 critical path < 400 KB gzip on 3G; Lighthouse budgets on all portals; OWL bundle budgets (Odoo asset bundle size guard) | Budgets met |
| D11 | Security | No credential literals; SSRF guard on server fetches; OIDC flows correct; portal ACL negative tests (portal user cannot reach back office — pattern exists in smoke) | Clean review + tests |
| D12 | Offline (mobile) | L-suite (33 scripts) green; conflict disclosure states implemented; evidence channel non-blocking | Green |
| D13 | Contracts | Every API path in `contracts/openapi/` has PS-11 contract tests; zero undocumented paths used by apps | Green |
| D14 | Build & deploy | `build once, promote`: same artefact promotes dev → test → staging → prod; health checks; DB migrations run; rollback rehearsed | Drill record |
| D15 | Estate non-regression | Full battery (tests, fitness, comodel-deps, G0b–G8, smoke, seed double-run) green at every phase tag | Green at pp0…pp7 |
| D16 | Data readiness | Migration rehearsal at production volume with MIG-02 control totals reconciled; business sign-off recorded before any legacy decommission | Signed record |
| D17 | Security headers (audit addition) | CSP with per-portal nonces; HSTS; `frame-ancestors` scoped for embedded BI; CORS pinned at Kong; header assertions in E2E | Automated header checks green |
| D18 | Observability (audit addition) | OTel traces browser→Kong→Odoo on customer-critical paths; RUM metrics flowing to the existing TimescaleDB/Grafana stack; portal health dashboards live | Trace sampled end-to-end in staging; alerts wired |
| D19 | External-fact currency | Every technology claim in this plan carries a verified-on date ≤ 90 days at execution time (version-currency ritual); `06-EXTERNAL-FACTS.md` updated at each phase gate | Ritual record at PP1/PP3/PP5/PP7 |

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
