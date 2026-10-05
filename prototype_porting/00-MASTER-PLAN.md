# Prototype Porting Programme — Master Plan

**Programme ID**: `PP` (Prototype Porting) · **Version**: 1.0 · **Date**: 2026-10-05
**Source of truth for scope**: `Front_end/` prototype (verified 8,566 routes ALL CLEAN)
**Mandate**: 100% port of the working prototype onto the production stack — a real,
deployable system — **without damaging what has already been built and verified** in the
Odoo backend estate (Phases 2–11: 64 modules, 123 models, **725 tests — 531 addons + 194 service, re-run 2026-10-05**, Gates G0b–G8 green).

> **Zero-trust audit note (iteration 4, 2026-10-05)**: every number in this folder was
> re-verified against the live systems on 2026-10-05, and every external technology
> claim was re-researched on the open web. The evidence table lives in
> [`06-EXTERNAL-FACTS.md`](06-EXTERNAL-FACTS.md); the audit record in
> [`ITERATIONS.md`](ITERATIONS.md). One claim (Payload 3.73) could not be
> independently verified online and is flagged for re-verification at PP1.

---

## 1. The mandate, stated precisely

The `Front_end/` prototype is a **100% working, dependency-free simulation** of the full
ERP: 823 screens · 346 reports · 266 forms · 600 sub-modules · 5,100 functions ·
67 modules · 12 areas · 12 portals · 10 journeys · 4 personas — bilingual EN/বাংলা,
dark mode, 3 densities, 8,566 deep-linkable routes verified with zero console errors.

"100% porting to production" means all of the following, and nothing less:

1. **Every prototype asset lands in production** — navigation truth, screen
   archetypes, design tokens, i18n catalogue, journeys, personas, report library
   structure — consumed by real runtimes, not copied as static files.
2. **Every screen renders from real data** — no `demo_data.js`, no fabricated rows,
   no hard-coded values in any production artifact. Test environments use the
   deterministic seed (DE-12); production uses migrated real data (MIG-01…MIG-08).
3. **The result deploys** — build once, promote the artefact (PE-004-D-01); health
   checks, migrations, and rollback work on a clean machine with no manual steps.

## 2. Non-negotiable constraints (from the governing documents)

| Constraint | Source | Consequence for porting |
|---|---|---|
| One token source, five runtime realisations (R1 OWL, R2 Next.js, R3 QWeb, R4 Flutter, R5 partial) | UX-001 §3 | The prototype's CSS tokens become the DTCG source; every runtime generates from it. **R1 precision (verified in vendor source): Odoo 19.0.0 bundles OWL `2.8.4` (`vendor/odoo/addons/web/static/lib/owl/owl.js`); "OWL 3" exists only as an upstream alpha and is not what ships** |
| **Next.js 16.3 + Payload 3.73+, Node 22** — never Next 15 | `D-026` (ACCEPTED) | All six Next.js portals scaffold on 16.3 from first commit. Web-verified 2026-10-05: 16.3 line current (16.3.8 LTS), **Next 15 EOL 21 Oct 2026**, Turbopack default for dev+build; Node 20 EOL 30 Apr 2026, Node 22 LTS (Active→Maintenance 20 Oct 2026). **Payload 3.73 = full Next-16 support is NOT independently verifiable online (newest indexed release: 3.61.1) — re-verify at PP1 scaffold time (version-currency ritual)** |
| Next 16 breaking changes: `middleware.ts`→`proxy.ts`, Cache Components (`'use cache`) explicit, some libs need webpack fallback | release notes (web-verified) | PP1 scaffolding task includes a Next-16 breaking-changes checklist |
| **Flutter** for all mobile apps; one offline engine (`libs/dart/fix_offline`) | `D-027`, ADR-024, FL-03 | P02/P09/P11/APP-04 consume the engine; never re-implement sync. Flutter 3.44/Dart 3.12 web-verified: Impeller (Vulkan) default on Android, SwiftPM default on stable — **the roadmap's "Material/Cupertino out of core" detail was only partially corroborated; verify at fvm pin time (PP1)** |
| No Vite, no fourth bundler | IR-002 §0.1 deviation 1 | Turbopack (Next), Odoo bundler (OWL), Flutter build only |
| **APIs route through Kong 3.9** (in the local compose stack) | infra baseline | Portals talk to Kong, never directly to Odoo; CORS/rate-limit/header policy at the gateway (PP1) |
| Bengali-first, `bn_BD.po` 100%, BN-007 formatting | DE-17, FF-25 | Prototype's 74-key app catalogue **+ its 17-key landing dictionary (`LAND_I18N`, inline in `index.html` — found by audit, count re-verified iteration 5)** merge into `libs/ts/i18n`; 110 counterpart-pending keys close |
| Accessibility: **WCAG 2.2 AA** is the programme standard | UX-005, QA-008 | The prototype's landing self-describes as WCAG **2.1** AA (audit finding) — porting targets 2.2 (a superset); no relaxation, recorded so nobody "discovers" the delta later |
| Monetary = currency-carrying (AS-10); events via outbox (AS-08); no business logic in views (AS-09) | 05-06 | Portal screens call the OpenAPI surface; they never compute money or write state directly |
| A developer workstation never holds production data | DE-12 | Seed stays synthetic-but-valid; real data only on migration staging/prod |
| Loopback-only local endpoints | EP-12, DE-11 | Dev servers bind 127.0.0.1; no outbound calls from ported UI |
| Build once, promote the artefact | PE-004-D-01 | Same image/bundle promotes dev → staging → prod |
| The legacy `1000fix-portal-platform` (Next 15 + Payload 3) **is not in this workspace** | audit finding (docs-only folders under `1000_fix_corporate_website`) | Its migration (W0-05) is owned by the CON-03 platform team elsewhere; the six ERP portals are greenfield apps in OUR monorepo and per D-026's rollback rule do not wait for it |

## 3. Verified current state (measured, not assumed — 2026-10-05)

### Built and green — DO NOT DAMAGE
- **Odoo backend estate**: 64 `cd_*` modules installed, 123 AS-02/03-conformant models,
  531 addons tests + 194 service tests, fitness 6/6, Gates G0b–G8 all 0 FAIL,
  E2E smoke 14/14, deterministic seed covering every anchor + config master.
- **Design-system foundation**: DTCG token generator (`tooling/generators/generate-design-tokens.py`)
  → SCSS/CSS/TS/flat map; component contract (5 W1 components); CFM conformance suite
  (`tooling/design-system/conformance.py`); `cd_design_tokens` OWL partials.
- **i18n**: `libs/ts/i18n` generated registry — 294 keys, **110 counterpart-pending**;
  bn_BD.po 100% on all modules; BN-007 formatters.
- **Portal API surface (W4 slice)**: `services/portal-contracts/openapi-w4-portals.json`
  — 11 endpoints for P04/P08/P10/P06 (corporate estate, consolidated invoices, brand
  claims, contact conversations, analytics).
- **Odoo-side portal slices**: admin portal shell + 6 W1 workspaces (P03 slice),
  `cd_corporate_portal` (P04 R3 slice), vendor/marketplace/partner backend surfaces.
- **A11y harness**: Playwright + axe-core (WCAG 2.2 AA) + static expansion checks.

### Gaps — this programme closes them
| # | Gap | Evidence |
|---|---|---|
| G1 | Brand-token divergence: prototype is **Service-Teal** (`#0E7A6E`, 16-step ramp); production token source says **blue `#2563eb`** | `Front_end/css/tokens.css` vs `libs/ts/ui/src/tokens/tokens.json` |
| G2 | `apps/web/` (7 Next.js portals) — **empty** | directory listing |
| G3 | `apps/mobile/` (4 Flutter apps) — **empty** | directory listing |
| G4 | `libs/ts/api-client/` — **does not exist** | roadmap tree vs codebase |
| G5 | `contracts/openapi/`, `contracts/portal/` — **empty**; only the W4 slice exists outside it | `contracts/` listing |
| G6 | Prototype navigation truth (nav_data 2,388 lines, 8,566 routes) — not ported to any registry | — |
| G7 | `demo_data.js` fabrications — must never reach production | file exists, by design prototype-only |
| G8 | 110 i18n keys counterpart-pending | registry counter |
| G9 | Old `1000fix-portal-platform` on Next 15 — EOL, unmigratied (owner: CON-03 platform team; ERP blocked-by) | `W0-05` plan |

## 4. Architecture: where each prototype surface lands

The prototype renders **one integrated shell**. Production deliberately splits it by
audience and runtime — this is the load-bearing mapping of the whole programme:

| Prototype surface | Production home | Runtime |
|---|---|---|
| Areas A01–A12, all 67 module workspaces, grids, records, consoles (the 823-screen back office) | **P03 Admin Operations Portal** — Odoo backend | R1 OWL 2 |
| P01 Customer Self-Service (web) | **P01 Customer Portal** | R2 Next.js |
| Customer mobile app (APP-04) | **APP-04 Customer Mobile** — Flutter per `D-027` (the portal-spec's "React Native" predates the decision and is superseded) | R4 Flutter |
| Corporate estate/invoices/service requests screens | **P04 Corporate B2B** | R2 Next.js |
| Vendor RFQ/PO/invoice screens | **P05 Vendor Portal** | R3 QWeb + R2 |
| Executive/branch/finance dashboards | **P06 Analytics** (Apache Superset + Grafana embedded — the L4 stack; the portal spec's "Metabase" is superseded by the architecture baseline) | embed + R2 |
| Marketplace seller screens | **P07 Seller Portal** | R2 Next.js |
| Brand claim/reconciliation screens | **P08 Brand Partner** | R2 Next.js |
| Contact-centre console + customer 360 | **P10 Agent Console** | R2 Next.js |
| Partner/referral screens | **P12 Partner Portal** | R2 Next.js |
| Technician day view / job execution / parts | **P02 Technician App** | R4 Flutter |
| Rider pickup/custody/route screens | **P09 Rider App** | R4 Flutter |
| Audit checklist / branch audit screens | **P11 Auditor App** | R4 Flutter |
| Landing + login (12 portal cards, 10 journeys) | Shared marketing shell in each portal + the corporate website | R2 |
| Report Center (346 reports) | Odoo QWeb reports (R3) + Superset for analytics | R3 / embed |
| Tell-ME global search | Odoo search (R1) + per-portal search (R2/R4) via API | all |

## 5. The eight porting phases (dependency-ordered)

```
PP0 Foundation Reconciliation ──┬──> PP1 Platform Scaffolding ──┬──> PP2 P03 Admin (OWL)
                                │                               ├──> PP3 P04 Corporate (1st Next.js slice)
                                │                               └──> PP5 Next.js Portal Batch
                                │                                        (P01,P05,P07,P08,P10,P12)
                                └──> PP4 Flutter Apps (P02,P09,P11,APP-04) — needs PP1 libs/dart
PP6 Data Strategy Execution (needs PP2..PP5 APIs; starts with PP0 rules)
PP7 Hardening & 100%-Deployable Verification (needs all)
```

| Phase | Name | Depends on | Delivers |
|---|---|---|---|
| **PP0** | Foundation Reconciliation | — | Service-Teal token source; merged i18n (0 pending); navigation registry generated from nav_data; archetypes added to component contract; prototype frozen as reference |
| **PP1** | Platform Scaffolding | PP0 | apps/web (7 Next.js 16.3 skeletons), apps/mobile (4 Flutter skeletons), `libs/ts/api-client`, `contracts/openapi+portal` populated, CI stages wired |
| **PP2** | Admin Portal P03 completion (R1) | PP0 | The 823-screen back-office surface in Odoo: menus from the navigation registry, workspace/grid/record patterns per module, consoles |
| **PP3** | First vertical slice: P04 Corporate | PP1 | One portal 100% (auth → estate → invoices → service requests) against the live OpenAPI; the template for all Next.js portals |
| **PP4** | Flutter apps | PP1 (+backend from P2–P11) | P02 technician (offline engine), P09 rider, P11 auditor, APP-04 customer |
| **PP5** | Next.js portal batch | PP3 | P01, P05, P07, P08, P10, P12 — each a full port of its prototype screens |
| **PP6** | Data strategy execution | PP0 rules; PP2–PP5 surfaces | demo_data eliminated everywhere; API-only rendering; seed = the only test data; real-data migration wired to MIG standards |
| **PP7** | Hardening & deployable verification | all | CFM conformance green ×5 runtimes, WCAG 2.2 AA, perf budgets (P01 < 400 KB 3G), E2E, gates, one-command deploy |

Each phase has a detailed task table in [`01-PORTING-PHASES.md`](01-PORTING-PHASES.md).

### Porting order vs the roadmap's wave order — reconciled

The roadmap builds portals by wave (P01 W2 · P05/P09 W3 · P04/P06/P08/P10 W4 ·
P11 W5 · P07/P12 W7). The porting programme re-sequences for engineering leverage:
**PP3 delivers P04 first** because its OpenAPI slice already exists
(`openapi-w4-portals.json`), making it the fastest complete vertical slice and the
template for every other Next.js portal. P01 (W2 in the roadmap, highest user volume,
tightest perf budget) follows immediately in PP5 on the matured template. Wave
*content* is unchanged — only build order inside the porting programme differs, and
P01's perf budget is enforced from the PP1 skeleton onward (not deferred to PP5).

## 6. Data strategy in one page (detail in `02-DATA-STRATEGY.md`)

Three data classes, never mixed (DE-12):

1. **Production (real) data** — enters only through migration (MIG-01…MIG-08: control
   totals, permanent legacy reference, dry runs, reconciliation sign-off) or through
   live user traffic. Never on a developer workstation.
2. **Test data** — the deterministic seed (`db/seeds/seed.py`, fixed seed `1000fix`),
   extended as portals need fixtures; idempotent double-run verified; consumed by
   portals **through the same APIs production uses**.
3. **Forbidden in production artifacts**: `demo_data.js`-style arrays, random value
   generators, hard-coded KPI numbers, sample names, mock statuses. A CI check
   (new, PP1) fails any PR that ships a fixture into `apps/` or `addons/` runtime code;
   fixtures live only in `apps/*/tests/` and Storybook.

## 7. Protections for what is already built (detail in `03-RISK-AND-PROTECTIONS.md`)

- The Odoo estate's gates (fitness, G0b–G8, smoke, seed idempotency) run before every
  PP merge — a porting change that reddens an existing gate is reverted, not excused.
- Token regeneration is additive: the DTCG source gains the Service-Teal ramp; the
  generator's outputs and CFM suite re-run; nothing overwrites Odoo assets in place
  without the conformance suite green.
- The running database is never schema-dropped for porting convenience; every change
  is an Odoo migration or an additive manifest upgrade.
- The prototype directory itself is **read-only reference** — never edited, never deleted.

## 8. Definition of done — "100% deployable" (detail in `04-DOD-100-PERCENT.md`)

Every prototype asset traceable to a production realisation; every screen renders from
API data in seed and production modes; zero fixture data in shipped bundles; CFM
conformance green on all five runtimes; WCAG 2.2 AA; perf budgets met; E2E suites per
portal; `make deploy-profile` promotes the same artefact through the twelve
environments; gates G0b–G8 (plus a new GP gate for porting) all green.

## 9. Document map

| File | Content |
|---|---|
| [`01-PORTING-PHASES.md`](01-PORTING-PHASES.md) | PP0–PP7 task tables with dependencies, per-phase DoD |
| [`02-ASSET-PORTING-MATRIX.md`](02-ASSET-PORTING-MATRIX.md) | Every prototype asset → production destination, line-counted |
| [`03-DATA-STRATEGY.md`](03-DATA-STRATEGY.md) | Real / test / forbidden data rules; demo_data elimination plan |
| [`04-RISK-AND-PROTECTIONS.md`](04-RISK-AND-PROTECTIONS.md) | Risk register; no-damage protocols |
| [`05-DOD-100-PERCENT.md`](05-DOD-100-PERCENT.md) | The 100% definition + verification matrix |
| [`06-EXTERNAL-FACTS.md`](06-EXTERNAL-FACTS.md) | Evidence table for every external technology claim (web-verified 2026-10-05, with links) |
| [`ITERATIONS.md`](ITERATIONS.md) | The plan-audit iterations (1–4), recorded |
