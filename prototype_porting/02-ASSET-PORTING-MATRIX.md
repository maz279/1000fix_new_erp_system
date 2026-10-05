# Asset Porting Matrix — every prototype asset to its production home

Measured from the prototype on 2026-10-05 (`Front_end/`, 5,462 lines total).
Rule: **nothing is hand-copied where a generator can emit it**; the prototype's data
becomes generator input or a registry, and runtimes consume the generated artifact.

| # | Prototype asset (measured) | Production destination | Mechanism | Phase |
|---|---|---|---|---|
| 1 | `css/tokens.css` — Service-Teal ramp (16 steps), `--primary #0E7A6E`, AA status triplets, surfaces, dark theme, 3 densities, focus rings, dark shadows (231 DTCG tokens) | `libs/ts/ui/src/tokens/tokens.json` (DTCG single source) | Ported in PP0 → generator emits SCSS/CSS/TS/Dart/flat; `:root` bridge verified (231 tokens); CFM 1–5 PASS | PP0 |
| 2 | `nav_data.js` + `nav_data2.js` + `nav_data3.js` — 12 areas, 67 modules (mixed declaration styles: literal keys in part 1, `FX_MODULES.Mxx =` assignments in parts 2–3), **278 screen groups**, 823 screens (`t:` codes), **per-module `reports:[…]` arrays = the 346-report library and `forms:[…]` arrays = the 266-form register (plain strings, not screens)**, `freg.sub` = `[id, name, count]` triples (600 · 5,100) (2,388 lines) | `contracts/nav/registry.json` | Generated in PP0 via `generate-nav-registry.py` (parse → JSON, bilingual labels kept) + CI meta-audit `check-nav-registry.py` (FF-38) | PP0 |
| 3 | `js/i18n.js` — 74-key-per-locale EN↔বাংলা app catalogue (53 lines; parity recount-verified) **+ `LAND_I18N` landing dictionary (40 keys, inline in `index.html`: 34 durable ported, 5 prototype-meta excluded, 1 locale-neutral excluded — baseline verified)** | merged into `libs/ts/i18n/src/ui-copy.generated.json` | Extracted via UI-900 copy pack in PP0; counterpart-pending closed (110 → 0; 493 keys total) | PP0 |
| 4 | 13 screen archetypes (`js/app.js`, 744 lines) — Role Center, Workspace, Function Explorer, Grid, Record Details (BPF+FactBox), Data Form, Process Console, Dashboard, 360°, Report Viewer, Report Center, Report Writer, Search | `docs/design-system/component-contract.md` (Parts 2–3, landed PP0) + R1/R2/R4 realisations | Contract-first, per the landed Part-2 specs; realisation guidance (tabular numerals, delta badges, optional windowing for huge lists) is non-normative — the client never computes money (AS-09) | PP0–PP5 |
| 5 | Charts: spark/line/bar/donut/gauge/heatmap/waterfall/funnel, token-aware (`js/charts.js`, 177 lines) | `libs/ts/ui` (R2 SVG components) + OWL partials (R1) + Flutter widgets (R4) | Component contract entries; token-driven, dark-safe | PP0/PP3 |
| 6 | Shell: command bar, mega menus, Tell-ME, tab rail, breadcrumbs, dark/density/lang toggles (`js/shell.js`, 431 lines) | R2 portal shell (PP3 template) + Odoo webClient adaptations (R1) + Flutter app bars (R4) | Faithful port of the prototype shell; ARCHITECTURE_STATE §2/§3 (omni-nav lens, LRU tab engine) are design options — the tab rail itself is the requirement | PP2/PP3/PP4 |
| 7 | Landing: 12 portal cards, 10 journey strips, 15 area cards, EN⇄বাংলা (`index.html`, 231 lines — **renders live from `FX_DEMO.PORTALS`, `FX_DEMO.JOURNEYS`, `FX_AREAS`/`FX_MODULES`; the copy lives in inline `LAND_I18N`**) | Shared marketing shell + per-portal public pages | Port as React components in the shared shell; data sources move to the registry (PP0-M03) | PP5 |
| 8 | Login: split-screen, TOTP, persona one-click (`login.html`, 101 lines) | Real auth: Keycloak OIDC (DE-09); personas become seeded realm users; TOTP becomes real TOTP enrolment | Auth integration, not UI copying | PP1/PP3 |
| 9 | `js/demo_data.js` (371 lines) — **split by audit into two halves**: (a) *structural* — `PORTALS` (12), `JOURNEYS` (10 with linked steps), `PERSONAS` (4) → extracted to the registry; (b) *fabrications* — PRNG grid rows, KPI values, console scripts, dashboard widgets → **NOT PORTED**. Replaced by: seed (test env) + real data (prod) via APIs | Anti-fixture CI gate | PP0 (extraction) / PP6 (elimination) |
| 10 | Grid schemas/columns per module (in demo_data) | Data-shape parity tests: API fields ≡ prototype columns | `check-data-parity` per portal | PP6 |
| 11 | Report library (346 entries, Mushak 9.1 with totals footers) | QWeb reports (R3) linked from registry; Superset for analytics | Report Center in P03 | PP2 |
| 12 | Report writer (7-step no-code wizard) | P03/R2 report-writer on M62 metrics + safe query surface | Later increment, contract from prototype | PP5+ |
| 13 | Journeys (10 end-to-end strips, 54 discrete steps) | E2E test specifications (Playwright R1/R2 + Flutter Patrol R4) + portal cross-links | **Journey-to-E2E Execution Matrix** (`ARCHITECTURE_STATE.md` §8) mapping all 54 steps to automated test suites; 100% pass required by DoD D3 | PP5/PP7 |
| 14 | Personas (4 role centers) | Odoo role-center home actions per group | PP2 |
| 15 | 360° party view with relationship map | P03 + P10 customer-360 (uses M33 party kernel) | PP2/PP5 |
| 16 | Bengali shaping/layout behaviour (expansion budgets, no truncation) | BN-007 rules + `check-expansion-static.py` + runtime bn scans | Existing harness reused | all |
| 17 | Audit harnesses (`_audit_click/_final/_meta/_verify*.js`, crawl of 8,566 routes) | CI: Playwright route-crawl per portal (routes generated from the registry), 404 guard, console-error guard, deep-link/history/mobile/focus checks | Port the crawler pattern; route universe comes from the real apps; integrated into **Automated A11y Gatekeeper** (`ARCHITECTURE_STATE.md` §9) | PP1/PP7 |
| 18 | Mobile 390px responsive behaviour | R2 responsive layouts; a11y mobile scans | PP7 |
| 19 | `login` simulated auth | Keycloak synthetic realm matching seed users (`seed.user%@1000fix.local`) | PP1 |
| 20 | Evidence `_shots/` (19 screenshots incl. true-390px mobile) | Visual-regression baselines for the conformance suite | PP7 |
| 21 | Accessibility posture — landing self-describes **WCAG 2.1 AA**; audit confirmed the suite target is **WCAG 2.2 AA** (UX-005/QA-008) | Port to the 2.2 superset; the delta (e.g. 2.2's focus-appearance, dragging, target-size criteria) is added scope, not a relaxation — recorded so the effort is priced | Automated `@axe-core/playwright` CI Gatekeeper (`ARCHITECTURE_STATE.md` §9); 0 critical/serious violations, Lighthouse a11y $\ge 98/100$ | PP7 |

## Coverage accounting (the "100%" ledger)

The registry (asset 2) is the denominator. Gate GP reports:
- `registry.screens` → resolved by P03 Odoo menu/action mapping (back office) or portal
  route (external) — target **100% resolved, exceptions documented**;
- `registry.reports` → QWeb/Superset realisations — **100%**;
- `registry.functions` (5,100) → traced to backend capabilities (model action, API
  endpoint, or report) — the function register stays machine-checkable, as in the
  prototype's own meta-audit;
- `registry.journeys` → E2E suites — **100%**.
