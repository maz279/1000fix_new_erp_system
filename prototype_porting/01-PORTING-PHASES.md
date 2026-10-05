# Porting Phases PP0–PP7 — Task Tables

Task ID convention: `PPn-Mxx-Tyy`. Verify column states the machine check wherever one
exists. Roles reuse the roadmap's (FE frontend, MB mobile, OD Odoo dev, DA data, QA, SL
security, UX design lead, PM). Every phase ends with: full battery green (tests, fitness,
G0b–G8), commit, and no regression to the Phases 2–11 estate.

---

## PP0 — Foundation Reconciliation (everything else depends on this)

**Objective**: make the prototype's design truth the production source of truth, and
freeze the prototype as reference.

| ID | Task | Detail | Verify | Role | Dep |
|---|---|---|---|---|---|
| PP0-M01-T01 | **Reconcile the token source to Service-Teal** | Port `Front_end/css/tokens.css` (16-step teal ramp, `--primary #0E7A6E`, AA status triplets, dark theme, 3 densities, focus rings) into `libs/ts/ui/src/tokens/tokens.json` (DTCG). The blue `#2563eb` set is retired. Generator re-run → SCSS/CSS/TS/flat | CFM suite green (CFM-01…05 incl. WCAG contrast) on the new values; `cd_design_tokens` partials re-verified | UX | — |
| PP0-M01-T02 | **Regenerate all runtime token outputs** | `generate-design-tokens.py` emits R1 SCSS, R3 CSS, R2 TS, R4 Dart (`libs/dart/fix_ui/theme/`), R5 map | Build green in Odoo (asset bundle compiles); diff reviewed by UX | UX/FE | T01 |
| PP0-M02-T01 | **Merge the i18n catalogues** | Prototype `js/i18n.js` (74 keys per locale, EN↔বাংলা parity — recount-verified) + its bilingual nav labels + **the landing marketing dictionary `LAND_I18N` (40 keys, inline in `index.html`: 34 durable ported, 5 prototype-meta excluded, 1 locale-neutral excluded — verified in baseline execution)** are authored as new copy-pack files in **`project_content/03_UI_Copy_and_Microcopy/`** (the extractor's only source — verified in `tooling/scripts/extract-ui-copy.py`) and the registry regenerated; **close the 110 counterpart-pending keys** (translate, review, mark `inline` — 493 total keys in production registry) | `counterpart_pending == 0`; FF-25 still enforcing 100%; parity checker (prototype meta-audit logic ported to CI) | LL/UX | — |
| PP0-M03-T01 | **Generate the navigation registry** | `tooling/generators/generate-nav-registry.py` parses the prototype payloads — **every source syntax-verified by audit, counts recomputed programmatically (iteration 5)**: modules in **two declaration styles** (object-literal keys in `nav_data.js` = 14; `window.FX_MODULES.Mxx = {...}` assignments in `nav_data2/3.js` = 53; total **67**); screens `{id:'…', t:'w|g|f|r|c|d|x|s'}` nested in `groups:[{en, screens:[]}]` (**278 groups · 823 unique screen ids**); **the 346-report library and 266-form register are per-module plain-string arrays — `reports:['…','…']` and `forms:['…','…']` — NOT screen entries (only 80 report-viewer screens exist), and the registry must carry them or the Report Center loses its catalogue**; `freg` carries `src` + `sub` as array triples `[id, name, function-count]` (**600 triples · 5,100 functions — sums verified**); **structural arrays live in `demo_data.js`** — `FX_DEMO.PORTALS` (12 card entries), `FX_DEMO.JOURNEYS` (10, each with linked steps), `FX_DEMO.PERSONAS` (4) — EXTRACTED into the registry while every fabricated metric is dropped (labels/ids/step-links kept; values return via API in production) → `contracts/nav/registry.json` | Meta-audit port (`tooling/fitness/check-nav-registry.py` — the prototype's `_audit_meta.js` logic as CI): recomputes every headline from the registry (67/278/823/346/266/600/5,100), `freg.src == sum(sub counts)` per module, no dup screen ids, no orphan area→module refs, no module without an area, EN↔bn i18n parity | FE | — |
| PP0-M03-T02 | **Bind the registry to Odoo menus (design)** | Mapping spec: registry screen keys → Odoo menu/action XML ids per module; NVR-23 section limits honoured (max 6/7) where the prototype exceeds them — recorded exceptions, not silent drops | Spec review; `check_portal_contract.py` extended to accept the registry as the expected menu universe | OD | T01 |
| PP0-M04-T01 | **Extend the component contract to all 13 archetypes** | Role Center, Workspace, Function Explorer, Grid, Record Details (BPF+FactBox), Data-entry Form, Process Console, Dashboard, 360°, Report Viewer, Report Center, Report Writer, Search Results — each specified (props/slots/states/a11y/copy/tokens) like the 5 W1 components | Contract doc review; conformance inventory (CFM-04) updated with the 13 | UX | T01 |
| PP0-M04-T02 | **Chart primitive contracts** | Prototype's SVG charts (spark/line/bar/donut/gauge/heatmap/waterfall/funnel, token-aware, dark-safe) specified as components for R1/R2/R4 | Contract entries; visual reference screenshots from `_shots/` attached | UX | T01 |
| PP0-M05-T01 | **Freeze the prototype** | `Front_end/` marked read-only reference (note in README); its audits re-run once and archived into this folder as the porting baseline evidence | Baseline record in `ITERATIONS.md` | PM | — |

**PP0 exit**: tokens teal everywhere, i18n 0 pending, nav registry generated + checked,
contract covers 13 archetypes, prototype frozen. Battery green.

---

## PP1 — Platform Scaffolding

| ID | Task | Detail | Verify | Role | Dep |
|---|---|---|---|---|---|
| PP1-M01-T01 | Scaffold `apps/web/` — 7 Next.js 16.3 apps | `customer/ corporate/ analytics/ seller/ brand/ agent-console/ partner/` per the roadmap tree; Turbopack; Node 22; Payload 3.73 only where CMS is used (customer/marketing) | Each app builds and serves a token-driven hello-screen on 127.0.0.1:30xx | FE | PP0 |
| PP1-M01-T02 | Scaffold `apps/mobile/` — 4 Flutter apps | `technician/ rider/ auditor/ customer/` via fvm-pinned Flutter (3.44 migration notes honoured); consume `libs/dart/fix_ui` (R4 tokens) | `flutter analyze` clean; hello-screen renders tokens | MB | PP0 |
| PP1-M01-T03 | **Next-16 breaking-changes checklist + Payload re-verification** | Scaffold against the web-verified Next 16 realities (audit iteration 4): Turbopack default for dev+build; `middleware.ts`→`proxy.ts`; Cache Components (`'use cache'`) explicit — document each in the app template. **Payload "3.73 = full Next-16 support" could not be verified online (newest indexed release 3.61.1) — run the version-currency ritual against payloadcms.com at scaffold time and record the verified version** | Checklist in the portal template README; verification record appended to `tooling/version-currency/evidence/` | FE | T01 |
| PP1-M02-T01 | Build `libs/ts/api-client` | Typed client generated from `contracts/openapi/*.json`; auth (Keycloak OIDC per DE-09), retry, error mapping; no `fetch` outside the lib (CFM-style check). **All calls route through Kong 3.9 (in the local compose stack) — never direct-to-Odoo; CORS, rate limits and header policy configured at the gateway** | Contract tests against a stub; lint rule forbidding raw fetch in apps; Kong route smoke | FE | T01, T03 |
| PP1-M03-T01 | Populate `contracts/openapi/` | Move/extend `openapi-w4-portals.json`; author specs for P01, P05, P07, P12 surfaces from the existing Odoo controllers (service order tracking, vendor, marketplace, partner) — each spec paired with PS-11 contract tests like the W4 slice. **Add the PDPA consent endpoints (audit gap): consent status/grant/withdraw + DSR request submission — the `fix.consent` backend exists but has no portal API today** | `contracts/openapi/` one file per API-exposing CD item; tests green | OD/FE | — |
| PP1-M03-T02 | `contracts/portal/` — the CON-03 portal contract | Shared session/header/locale/tenant conventions for all portals | Spec signed off; a11y + locale headers testable | FE | T01 |
| PP1-M04-T01 | **Anti-fixture CI gate** | New check `check-no-fixtures.py`: fails any fixture/demo/mock data file under `apps/*/src`, `addons/**/static`, or shipped bundles; fixtures allowed only under `**/tests/`, `**/stories/`, `db/seeds/` | Check runs in pre-merge stage; seeded with deliberately-failing sample then removed | QA | — |
| PP1-M04-T02 | Wire CI stages for the new apps | Lint/type/test/build per app; bundle budget check (P01 < 400 KB gzip critical path); Lighthouse CI on customer paths | CI green on skeleton apps | DE | T01/T02 |

**PP1 exit**: all 11 apps scaffolded and building; api-client + contracts in place;
anti-fixture gate live.

---

## PP2 — Admin Operations Portal P03 (R1 OWL) — the 823-screen surface

The back office lives in Odoo. The port is **not** a rewrite of Odoo views; it is
completing them to the prototype's information architecture.

| ID | Task | Detail | Verify | Role | Dep |
|---|---|---|---|---|---|
| PP2-M01-T01 | Menu structure from the registry | Generate/extend module menus so the 12 areas × 67 modules match the registry (PP0-M03-T02 mapping); workspace menus per module | `check_portal_contract.py` against registry: every module reachable, no orphans; NVR-23 exceptions recorded | OD | PP0 |
| PP2-M01-T02 | Workspace screens (archetype 2) | Each module gets the contract-A2 workspace pattern: KPI strip, quick actions, per-group list previews, built-in reports panel — KPI **labels** from the registry, **values from `read_group`/API only, never literals**. *(Realisation guidance, non-normative: tabular numerals for BDT amounts; delta badges via `color.status.*`; C1 sparkline where the prototype shows one)* | Spot-check 12 modules, one per area; grep proves zero hard-coded KPI values; a11y scan | OD/UX | T01 |
| PP2-M02-T01 | Grid/list conformance (archetype 4) | Contract-A4 on every transactional list: filter chips, sortable columns, row actions, `status_badge` pills, selection with a floating bulk-action bar. *(Performance option, non-normative: DOM windowing + sticky key columns IF a real list exceeds ~1k rows in UAT — benchmark before adopting; 10k-row/60 FPS figures in the earlier draft were unsourced)* | Visual + a11y scan on 20 representative lists; bulk flow E2E | OD/UX | T01 |
| PP2-M02-T02 | Record details pattern (archetype 5) | Tabs + BPF stepper (labels under circles — defect-#2 lesson) + FactBox rail on the flagship records (service order, work order, claim, invoice…). *(Design option: a contextual slide-over drawer for cross-record context — a11y focus-trapped if built)* | Screenshots vs prototype side-by-side; partials reuse `cd_design_tokens` | OD/UX | T01 |
| PP2-M03-T01 | Process consoles (archetype 7) | Dispatch, close-day, triage consoles: steppers × checklists × gauges on live state; live status pills; action rails | Console actions mutate real records; smoke covers each console | OD | T02 |
| PP2-M04-T01 | Report Center (R3 QWeb) | The 346-report library: registry entries link to QWeb reports; financial reports carry bold totals footers (Mushak 9.1 VAT calculations); Bengali report path honoured | Report renders both locales; totals verified against seed | OD | T01 |
| PP2-M05-T01 | Tell-ME search in Odoo (archetype 13) | Global command palette (`Ctrl+K`) across modules/screens/records (EN+বাংলা) with sub-50ms fuzzy search and keyboard arrow navigation | Search E2E; bn queries return hits; keyboard-first navigation | OD | T01 |
| PP2-M06-T01 | Role centers (archetype 1) | 4 persona role centers (from the prototype) as Odoo home actions per role group | Each persona lands on its center; KPIs from real reads | OD | T02 |
| PP2-M07-T01 | Tab rail port (prototype shell) | The prototype's accumulating closable tab rail, ported to R1: open pages persist as tabs, closable, deep-link-restorable. *(Non-normative options if measured need appears: dirty-state guard on close; LRU eviction of >8 tabs via sessionStorage snapshots — the 50 ms rehydration figure is an aspiration to benchmark; BroadcastChannel sync is NOT a requirement)* | Tab open/close/restore E2E; dirty-guard modal if implemented | FE/OD | T01 |

**PP2 exit**: every registry back-office screen key resolves in Odoo; virtualized grids & MDI engine verified; battery green.

---

## PP3 — First Vertical Slice: P04 Corporate B2B Portal (R2)

| ID | Task | Detail | Verify | Role | Dep |
|---|---|---|---|---|---|
| PP3-M01-T01 | Shell + auth | Next.js 16.3 shell (top bar, area nav per the prototype shell), Keycloak OIDC corporate login, locale switch EN/বাংলা, Tell-ME search entry. *(The ARCHITECTURE_STATE §2 "6-point omni-nav" is one organising lens for this shell — its specific widgets are options, not requirements)* | Login E2E against the local Keycloak realm (synthetic users) | FE | PP1 |
| PP3-M01-T02 | Estate screen | `/estate` from the `/corporate/estate` API; contract-A4 grid; status badges; zero local data | Contract test + E2E on seeded data | FE | T01 |
| PP3-M02-T01 | Consolidated invoices | `/invoices` grouped multi-job invoices (the 400-devices-1-invoice case), BDT rendering via BN-007 formatters — **display only; every total and the balanced/unbalanced verdict comes from the backend** (AS-09/AS-10; 03 §8). *(UX options, non-normative: Lakhs/Crores grouping display; keyboard amount multipliers)* | Totals equal backend sums; a lint/review rule forbids client-side monetary arithmetic | FE | T01 |
| PP3-M02-T02 | Service requests at scale | `/service-requests` create/track with the prototype's grid+record patterns | E2E create → appears in Odoo (event/audit trail) | FE | T01 |
| PP3-M03-T01 | Dark mode, densities, a11y | Token-driven theme/density toggles (compact 32px, cozy 40px, relaxed 48px) ported from prototype shell | axe scan clean; WCAG 2.2 AA compliant; keyboard nav | FE/UX | T01 |
| PP3-M04-T01 | **Slice template extraction** | Everything reusable (omni-nav shell, MDI tab engine, virtualized grid, 4-zone KPI card, smart currency input, record+BPF, drawer, badges, charts, i18n wiring, api-client) promoted into `libs/ts/ui` as the R2 component set per the 13-archetype contract | Components used unchanged by the next portal (PP5 proof) | FE | all |

**PP3 exit**: P04 fully usable against seed data; the R2 component library exists.

---

## PP4 — Flutter Applications (R4)

| ID | Task | Detail | Verify | Role | Dep |
|---|---|---|---|---|---|
| PP4-M01-T01 | `libs/dart/fix_offline` — offline engine | Per AR-010: command journal (SQLCipher), SP-07 upload-first sync, client side of the server idempotency ledger, deferred evidence channel (SP-09). *(Table/key designs in ARCHITECTURE_STATE §7 are the PP4 design, to be ratified against AR-010 §4–§8 before coding)* | L-suite (33 scripts) green; field half scheduled (TS-015) | MB | PP1 |
| PP4-M01-T02 | Conflict resolution per AR-010 | Server-authoritative resolution with the two-state conflict disclosure (not-yet-synced vs synced-and-rejected — AR-010 §6). *(Design option to ratify: field-level 3-way merge — server-wins on financial fields, additive merge on evidence/notes — proposed in ARCHITECTURE_STATE §7, pending AR-010 authority-matrix sign-off)* | L-suite conflict scenarios; disclosure states never conflated | MB | T01 |
| PP4-M02-T01 | P02 Technician app | Day view, job execution (diagnostic tree, fault coding, time tracking), parts (van stock, scan-to-consume), evidence capture (photos GPS+time, Bengali voice notes) — the prototype's screens as Flutter per R4 tokens | Device lab E2E on emulator; offline scenarios pass | MB | T01 |
| PP4-M03-T01 | P09 Rider app | Pickup, custody scan chain, delivery confirmation, route view — offline-first | Chain-of-custody unbroken in E2E | MB | T01 |
| PP4-M04-T01 | P11 Auditor app | Audit checklists, branch audit capture, photo evidence | Offline capture → sync verified | MB | T01 |
| PP4-M05-T01 | APP-04 Customer mobile | Customer portal core flows as the mobile app (book/track/devices), corporate SSO | Store-build pipeline produces signed artefact (sandbox) | MB | PP5-P01 APIs |

**PP4 exit**: 4 apps building, offline engine shared, no duplicated sync code (FL-03 review).

---

## PP5 — Next.js Portal Batch (P01, P05, P07, P08, P10, P12) + P06 embed

Each portal follows the PP3 template. Distinct work beyond template application:

| Portal | Prototype screens to port | Backend surface (exists) | Special requirements |
|---|---|---|---|
| P01 Customer | Booking, live tracking (webhook + polling fallback), device history, ownership transfer, estimates approval, PWA offline shell, **PDPA consent dashboard (grant/withdraw per channel, status visible — audit gap closed via PP1 consent endpoints)** | M01 tracking controllers, M17 registry, fix.consent | **< 400 KB critical path on 3G** (CI gate); 250k users/month |
| P05 Vendor | RFQ response, PO acknowledgement, delivery confirm, invoice submission (3-way match gate) | M16 vendor controllers | Odoo Portal (QWeb/R3) + Next.js hybrid per spec |
| P06 Analytics | Executive/branch/technician/finance/warranty dashboards | M25 + Superset/Grafana | Embedded BI, no data in the portal layer |
| P07 Seller | Seller onboarding, quotes, jobs, settlement statements, scorecards | M12 marketplace + settlement | Seller app + portal pair |
| P08 Brand | Claim submission/status/reconciliation | M09 + `/brand/*` OpenAPI | Per-brand branding isolation |
| P10 Agent | Unified queue, customer 360, call control, handoff | M27 + `/contact/*` OpenAPI | 30–80 agents; softphone integration seam |
| P12 Partner | Referral submission, tracking, commission statements | M53 partner/commission | Referral link attribution |

Plus: the landing/login experience (12 portal cards, 10 journey strips, bilingual) ports
to the shared marketing shell used by every portal's public face.

**PP5 exit**: all 12 portals live on seed data; each has E2E + a11y + budget green.

---

## PP6 — Data Strategy Execution (details in 03-DATA-STRATEGY.md)

| ID | Task | Verify |
|---|---|---|
| PP6-M01-T01 | Delete/retire every fabrication from production paths: demo_data.js logic never ported; grep sweep for generators in shipped code | `check-no-fixtures.py` green |
| PP6-M02-T01 | Seed as the single test-data source for every portal E2E (portals read via API exactly as production) | E2E suites run green against seeded DB |
| PP6-M03-T01 | Real-data migration wiring: staging env profiles; MIG-02 control totals; MIG-03 legacy refs; MG-005 mock at production volume; reconciliation sign-off gates | Migration rehearsal record |
| PP6-M04-T01 | Data-shape parity check: for each grid/report screen, a test asserting the API returns the *fields the prototype's columns declare* (no missing columns, no dead columns) | Parity suite green per portal |

---

## PP7 — Hardening & 100%-Deployable Verification (details in 05-DOD-100-PERCENT.md)

| ID | Task | Detail | Verify | Role | Dep |
|---|---|---|---|---|---|
| PP7-M01-T01 | **Automated Journey E2E Execution Suite (J01–J10)** | Automated Playwright (Web R1/R2) and Flutter Patrol (Mobile R4) suites covering all 10 prototype journeys across their 54 discrete steps mapped in `ARCHITECTURE_STATE.md` §8 | All 10 journeys pass 100% in CI against seeded backend; zero test flakiness | QA | PP3–PP5 |
| PP7-M02-T01 | **Automated WCAG 2.2 AA Accessibility Gatekeeper** | CI crawler running `@axe-core/playwright` across registry-generated routes and all portals: 0 critical/serious violations; touch targets at the house floor `dimension.target.minimum = 44px`; modal/drawer focus traps; visible focus rings | Axe clean across all routes; manual half per QA-008; per-portal audit trail | UX/QA | all |
| PP7-M03-T01 | **Security Headers & Gateway Ingress Hardening** | Enforce per-portal CSP nonces, HSTS (`max-age=63072000; includeSubDomains; preload`), `frame-ancestors` scoped for P06 embedded BI, CORS strictly pinned at Kong 3.9 per `ARCHITECTURE_STATE.md` §6 | Automated security header scanner in CI; SSL Labs A+ rating; SSRF guard active | SL/DE | PP1 |
| PP7-M04-T01 | **Distributed Observability & Performance Budgets** | OTel distributed traces (Browser → Kong → Odoo) on customer-critical paths; RUM telemetry to the prod TimescaleDB/Grafana stack; the contractual budget is **P01 < 400 KB gzip on 3G** — propose and benchmark INP/LCP thresholds here before adopting them as criteria | Trace sampling verified end-to-end in staging; contracted budget met; proposed thresholds ratified-or-dropped | DE/FE | all |
| PP7-M05-T01 | **Gate GP (Porting) Verifier Execution** | Run `tooling/gate/verify-gate-gp.ps1` aggregating: registry coverage 100%, fixture-free codebase, i18n 0-pending, token conformance green, performance & a11y budgets met, E2E journey suite green | Gate GP reports 0 FAIL; added to standing battery alongside G0b–G8 | PM/DE | all |

