# Risk Register & No-Damage Protections

Prime directive: **the Phases 2–11 estate is verified and green — porting must not
regress it.** Every protection below is a standing rule for all PP phases.

## Protections (mechanical, not aspirational)

| # | Protection | Mechanism |
|---|---|---|
| P-01 | The existing battery gates every PP merge: 531 addons + 194 service tests, fitness 6/6, comodel-deps, G0b–G8 verifiers, smoke 14/14, seed double-run | Pre-merge CI; a red existing gate **blocks** the porting PR — no override |
| P-02 | Token changes are regenerative, not surgical: the DTCG source is edited, the generator re-runs, CFM conformance must be green before merge | `generate-design-tokens.py` + conformance.py in CI |
| P-03 | The Odoo DB is migrated, never dropped: porting needs schema changes only via module upgrade/migration files | No `reset` on any env above `dev`; dev reset allowed only with seed re-run |
| P-04 | The prototype is read-only reference | No edits under `Front_end/` (check in CI: path excluded from PR diffs) |
| P-05 | Vendor subtrees (`vendor/odoo`, OCA) untouched | `check-vendor-clean` (exists) |
| P-06 | New frontend code lives only in `apps/`, `libs/ts`, `libs/dart`, `contracts/`, `tooling/` — Odoo modules change only for menus/views/controllers the port requires | CODEOWNERS + review |
| P-07 | Every new OpenAPI path ships with PS-11 contract tests (like the W4 slice) before a portal consumes it | CI ordering |
| P-08 | Anti-fixture gate (PP1-M04-T01) runs from PP1 onward — failures fail the build | CI |
| P-09 | Secrets only from env; SSRF guard on all server-side fetches (Mimosa constraints) | Hook + code review |
| P-10 | Rollback: each PP phase ships behind its own feature flag (Odoo menu groups for R1; env flags per portal for R2/R4) so a portal can be disabled without a redeploy | Flags via `fix.feature.flag` (pipeline-managed) |
| P-11 | **Strict Portal-to-Gateway Isolation (Zero Direct Backend Coupling)**: Portals in `apps/web/` and mobile apps in `apps/mobile/` talk *strictly* through Kong 3.9 API Gateway to OpenAPI contracts; zero direct database queries, zero direct ORM model imports | Architecture enforcement + lint rules forbidding raw DB or direct Odoo controller bindings |
| P-12 | **Outbox Pattern Enforcement for State Mutations (AS-08)**: All portal mutations flow through domain events via `cd_event_outbox`; no cross-module synchronous writes from frontend controllers | Event outbox schema checks + unit tests |
| P-13 | **Zero-Damage Automated Regression Tripwire**: Pre-merge CI battery (531 addons + 194 service = 725 tests, fitness 8/8, G0b–G8 gates, smoke 14/14) runs against every PP branch; any failure immediately blocks merge — zero excuses | Pre-merge CI pipeline |

## Risk register

| ID | Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|---|
| R-01 | Token re-basing (blue→teal) breaks Odoo asset bundles or CFM contrast checks | M | M | Regenerate + CFM in CI before merge; fix contrast at source (as done before: error-red #c62222) | UX |
| R-02 | Navigation registry ↔ Odoo menus drift (NVR-23 section limits vs prototype density) | H | M | Recorded exceptions list; `check_portal_contract.py` extended to the registry as expected universe | OD |
| R-03 | `1000fix-portal-platform` (Next 15) migration slips — shared shell/CMS blocked | M | H | PP3/PP5 do not depend on the platform: standalone Next 16.3 deployments from first commit (D-026 rollback rule); corporate-website CMS work stays with CON-03 | FE |
| R-04 | Offline engine re-implementation pressure under schedule (FL-03 violation) | M | H | Engine built once (PP4-M01) before any app screen; reviewer is the control | MB |
| R-05 | Bengali layout breakage in React/Flutter (conjuncts, expansion) | M | M | BN-007 budgets + static expansion checks from PP3 onward; two-engine TR-07 checks | UX |
| R-06 | Perf budget blown on P01 (400 KB / 3G) | M | H | Bundle budget CI from PP1 skeleton; chart components tree-shaken | FE |
| R-07 | Seed cannot satisfy a portal's E2E shape → temptation for fixtures | H | M | Seed-extension policy (E4) with named owner per portal; parity tests catch shape gaps early | DA |
| R-08 | Real-data rehearsal exposes model gaps late | M | H | Parity suite + migration-staging UAT from PP6, before hardening | DA |
| R-09 | Scope creep: porting the report *writer* (no-code) before the 346 standard reports exist | M | M | Sequenced last (PP5+); registry marks writer screens separately | PM |
| R-10 | Parallel work damages the Odoo estate (menu XML conflicts, view breakage) | M | H | P-01 battery + P-06 scoping; weekly full-battery run on main regardless of PR status | PM |
| R-11 | Mimosa/hook findings block commits on new frontend code (path traversal patterns in tooling) | M | L | New generators read inputs via explicit args, no `..`; commit-msg format followed | FE |
| R-12 | 12-portal E2E runtime explodes in CI | M | M | Route-crawl generated from registry; shard per portal; only affected-app tests on PRs (affected-selection exists) | DE |
| R-13 | **Payload "3.73 = full Next-16 support" is web-unverifiable** (newest indexed release 3.61.1; audit iteration 4) — if wrong, the CMS choice for P01/marketing shifts | M | M | PP1-M01-T03 re-runs the version-currency ritual at scaffold time and records the verified version before any Payload code is written; Payload used ONLY where CMS is genuinely needed (customer/marketing), not in data-heavy portals | FE |
| R-14 | Next-16 breaking changes (`middleware.ts`→`proxy.ts`, Cache Components, Turbopack-only libs) surprise mid-build | M | M | PP1 breaking-changes checklist in the template; webpack-escape hatch documented but discouraged | FE |
| R-15 | WCAG delta: prototype built/audited to 2.1 AA; programme requires 2.2 AA (superset — focus-appearance, dragging, target-size) | H | M | Priced as added scope in PP7; axe 2.2 ruleset + manual suite; the 8,566-route crawl is re-run against 2.2 checks | QA |
| R-16 | Kong gateway misconfig (CORS/rate-limit) blocks all portals at once | L | H | Gateway config as code in the repo; contract tests run through Kong locally, not just direct-to-Odoo | DE |
| R-17 | **Statutory financial drift** (TDS 10/15/20%, Mushak 9.1 VAT 15%, 13-digit BIN) — portal displays diverging from the backend tax engine *(corrected 2026-10-05: the CDBL tariff reference was wrong-domain and removed)* | M | H | Backend-only computation (03 §8); statutory cases embedded in OpenAPI contract tests (PS-11); any UI-computed tax figure is a review-blocking AS-09 violation | DA/FE |
| R-18 | **PDPA identity/consent gaps at the portals** (SC-003/SC-008): consent captured without proof, NID mishandled, DSR requests unreachable *(reclassified 2026-10-05 — the earlier BFIU AML/CFT framing was wrong-domain; 1000FiX is not a BFIU reporting institution)* | M | H | PP1 consent endpoints (grant/withdraw + DSR submission); `fix.identity.document` verification states surfaced; per-portal ACL negative tests (smoke pattern) | SL/FE |

## Freeze & rollback

- Each phase tags the repo (`pp0 … pp7`); any regression is reverted to the tag, not
  patched forward under pressure.
- The Odoo estate keeps its own release cadence — portal deployments never force an
  Odoo upgrade in the same window (PE-004 promotes independently versioned artefacts).
