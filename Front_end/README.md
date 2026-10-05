# 1000 FiX ERP — Front-End Prototype (8-Portal Integrated Smart Service Platform)

> **FROZEN — READ-ONLY REFERENCE (PP0-M05, 2026-10-05).** This prototype is the
> porting baseline for the production programme (`prototype_porting/`). Its
> payloads are consumed by generators (`generate-nav-registry.py`,
> `generate-prototype-copy-pack.py`, the Service-Teal token port). Do not edit,
> extend or "improve" it — any change invalidates the baseline and the
> generated contracts. Production work happens in `1000_fix_codebase/`.

A **100% working, dependency-free front-end prototype** of the full 1000 FiX ERP: every
module, sub-module, function, screen, form, report, portal, journey, and navigation path
renders and responds in a plain browser — no build step, no server, no npm install.

Open `index.html` (landing) → any portal / journey / module entry → `login.html`
(TOTP `123456` or one-click demo personas) → `app.html` (the ERP shell).

---

## 1. What's inside

| Path | Role |
|------|------|
| `index.html` + `css/landing.css` | Marketing landing: 12 portal cards, 10 journey strips, 15 area cards, EN ⇄ বাংলা runtime toggle |
| `login.html` + `css/landing.css` | Split-screen sign-in: email/password, 6-box TOTP, one-click persona login (4 roles) |
| `app.html` + `js/shell.js` | ERP app shell: top command bar, mega menus, Tell-ME global search, tab rail, breadcrumbs, dark mode, 3 densities, EN/বাংলা |
| `js/nav_data*.js` | **The single source of navigation truth** — 12 areas (A–K), 67 modules (M01–M67), 600 sub-modules, 5,100 functions, 346 built-in reports |
| `js/app.js` | Hash router + the 13 screen archetypes (see §3) |
| `js/charts.js` | Dependency-free SVG charts: spark, line, bar, donut (true ring), gauge, heatmap, waterfall, funnel — token-aware, dark-mode safe |
| `js/demo_data.js` | Deterministic demo data (seed 20260927): Bangladesh-realistic — ৳ BDT amounts, Mushak 9.1 VAT, NBR tax, bKash/Nagad, Dhaka zones |
| `js/i18n.js` | Full app-shell bilingual dictionary |
| `css/tokens.css` | Design tokens — "Service-Teal Fluent": teal brand ramp, Fluent-2 greys, AA status triplets, dark theme, densities, focus rings |
| `css/app.css` | Archetype + component styles |
| `_shots/` | 19 verification screenshots incl. true-390px mobile captures (evidence from the final audit run) |
| `_audit*.js`, `_verify*.js` | Audit + verification harnesses: `_audit.js` (Node route walker), `_audit_click.js` (full-browser crawl), `_audit_final.js` (assets/deep/history/overflow/mobile/focus), `_audit_meta.js` (counts & i18n consistency), `_verify_fixes.js` / `_verify_mega.js` (targeted fix proofs) — see §5 |

## 2. Verified scope numbers

**823 screens · 346 built-in reports · 266 data-entry forms · 600 sub-modules ·
5,100 functions · 67 modules · 12 areas · 12 portals · 10 end-to-end journeys ·
4 personas.**

## 3. The 13 screen archetypes

1. **Role Center** (home) — KPI strip, activity lists, favourites, news flash
2. **Module workspace** (`#/workspace/Mxx`) — KPI + quick actions + lists per module
3. **Function explorer** (`#/f/Mxx/group`) — sub-modules → sub-sub-modules → 5,100 functions, cross-linked
4. **Grid / list page** (`#/g/Mxx/...`) — filter chips, sortable columns, row actions, status pills
5. **Record details** (`#/record/Mxx/ID`) — Business-Process-Flow stepper (labels under circles), tabs, FactBox rail
6. **Data-entry form** (modal) — required-field validation, red-on-empty, chip pickers, closes on valid
7. **Process console** (`#/x/close`, dispatch, …) — steppers × checklists × gauges, live pills
8. **Dashboard** (`#/d/...`) — KPI row + line/donut charts + split panel
9. **360° view** — party master with relationship map
10. **Report viewer** (`#/r/Mxx/i`) — table (with totals footers on financial reports), distribution bar, 7-week trend
11. **Report Center** (`#/reports`) — statutory shelf + full 346-report library, all open
12. **No-code report writer** (`#/writer`) — 7-step builder wizard with live preview
13. **Global search results** (`#/search/…`) — Tell-ME results page with scoped hits

## 4. Navigation model

- **Hash router**: `#/g|f|r|c|d|x|record|screen|workspace|…` — deep-linkable, back/forward safe
- **Five simultaneous entry paths to every module**: left nav tree · mega menu · Tell-ME
  search (EN + বাংলা) · Report Center · portal/journey/area pages
- **Multi-point & cross-navigation**: every grid row, KPI card, BPF step, FactBox, journey
  step, report line, and breadcrumb is a live hyperlink — 8,566 unique routes, all reachable
- **Tab rail**: open pages accumulate as closable tabs ( Dynamics-style multi-open )
- **Breadcrumbs + area rail** on every page for orientation

## 5. How it was verified (two-stage, fully automated + visual)

**Stage 1 — Interactive crawl (scripted, headless Chrome via CDP):**
`node _audit_click.js` drives a real browser through: landing anchor sweep →
login (TOTP + one-click) → all 11 mega menus → Tell-ME in EN and বাংলা →
form-modal validation → tab rail → theme/density/language toggles → then a **BFS
crawl of every `#/` link found on every page**, asserting each route renders with
zero console errors. Final result:

```
LANDING area-cards=15 journeys=10 portals=12 anchorsOk=true
LANDING lang-toggle-bn=true lang-restore-en=true
LOGIN totp=true after-submit-url=/app.html#/home
LOGIN one-click-demo=/app.html#/home
MEGA-MENUS opened=11 links=116/93/131/37/83/66/111/88/47/47/82
TELLME results=12 navigated=#/workspace/M02
TELLME bengali-results=5
FORM-MODAL {"chips":4,"redOnEmpty":3,"closedOnValid":true}
TAB-RAIL {"open":true,"items":3}
TOGGLES {"theme":"dark","density":"relaxed","bn":true,"navBn":"সার্ভিস অর্ডার"}
CRAWL unique-routes=8566 crawled=8566
RESULT ALL CLEAN ✓ routes=8566 screenshots=16
```

**8,566 / 8,566 routes rendered clean — no dead ends, no broken links, no console errors.**
(The count includes a 404 dead-link guard that fails the run if any crawled route
renders the 404 page; cache is disabled in the crawler so every run grades current code.)

**Stage 1b — Supplementary audit (`node _audit_final.js`):** cold deep-links with a
404 guard, network asset integrity, browser back/forward, 1600 px overflow, **true
390 px mobile viewport (verified applied)**, and focus-visible rings. Final result:

```
ASSETS loaded=14 failed-net=0 bad-status=0
DEEP-LINKS cold-start pass=20/20 (404-guard on)
HISTORY clicks=#/workspace/M01,#/screen/M01-all back1=#/workspace/M01 back2=#/directory fwd1=#/workspace/M01 fwd2=#/screen/M01-all ok=true
OVERFLOW 1600px pass=12/12
MOBILE 390px viewport=390 pass=3/3 shots=3
FOCUS control=BUTTON outline="none 3px" shadow="rgba(232, 89, 12, 0.35) 0px 4px 14px 0px" ring=true
RESULT ALL CLEAN ✓ assets+deep+history+overflow+mobile+focus
```

**Stage 2 — Visual inspection:** all archetype screenshots (in `_shots/`, including the
true-390px mobile captures 17–19) were reviewed with a vision model, plus a manual
click-through of login → shell → mega menu → Tell-ME → record → report viewer → dark
mode in a second (in-app) browser. Issues found **and fixed**:

| # | Defect | Fix |
|---|--------|-----|
| 1 | Landing EN→বাংলা→EN left page in Bengali | `FXLandLang()` now captures/restores `data-orig` per node |
| 2 | BPF connector lines struck through step labels | `.bpf-step i` is a centred block; label is a block under the circle |
| 3 | Duplicate WO ids on the dispatch board | `usedWO` dedupe map across all 5 zone columns |
| 4 | VAT/Mushak reports had no totals row | Dedicated Mushak-9.1 dataset with bold footer totals |
| 5 | Gauge caption clipped / collided with arc | Resized 150×96, caption moved below arc, clamped to 22 chars |
| 6 | Donut centre label sat on segment colours (weak in dark mode) | True annular ring — centre text now sits on card surface |
| 7 | Mega menu stayed open over the page after clicking one of its links | `hashchange` listener closes mega menu, Tell-ME dropdown and mobile nav overlay on every navigation |
| 8 | Unknown record families produced a dead `#/screen/generic` breadcrumb (404); report dimension labels masqueraded as record links | `recordPage` fallback anchors at the live `M01-all` screen; report tables render plain first columns |
| 9 | At phone width (390 px) the fixed nav rail and full topbar forced +192 px document scroll | Grid items get `min-width:0`, rail collapses, topbar compacts (≤760 px hides company pill/density/directory), open rail is an overlay, wide grids/charts scroll **inside** the page |
| 10 | Tell-ME had no keyboard navigation (mouse only) | ↑/↓ move an `.active` highlight, Enter follows the highlighted item (plain Enter still opens the full search page) |
| 11 | Function register internally inconsistent: 34 of 67 modules' `freg.src` summary disagreed with their own sub-module breakdown (headline said 5,012, breakdowns summed to 5,100) | `src` is now the derived summary of its `sub` ledger — reconciled across all 34 modules; headline corrected to 5,100 everywhere (landing, README, docs) |
| 12 | Asset links carried `?v=1` through multiple code edits — real browsers would serve stale files | All `<link>/<script>` references bumped to `?v=2` |

After every fix, the audits were **re-run end-to-end: ALL CLEAN again** (final run:
8,566 routes + all six supplementary phases + counts/i18n meta-audit), and each fix
was re-verified interactively (`node _verify_fixes.js` — breadcrumb, plain report
columns, keyboard Tell-ME, mobile overlay; all assertions true) plus visually.

A fourth pass (`node _audit_meta.js`) recomputes every headline number from the live
payload — modules 67 · areas 12 · groups 278 · screens 823 · reports 346 · forms 266 ·
sub-modules 600 · functions 5,100 · personas 4 · journeys 10 · portals 12 — checks for
duplicate screen ids, orphaned area→module references, modules without an area, and
EN↔বাংলা i18n catalogue parity (74/74 keys, no gaps).

Harness notes worth remembering (they invalidated earlier "passes"):
- `Emulation.setDeviceMetricsValue` **does not exist** — the correct call is
  `Emulation.setDeviceMetricsOverride`, and `mobile:true` makes Chrome fit-scale the
  viewport (390 → 583 observed). Use `mobile:false` + `deviceScaleFactor:2` and
  verify `window.innerWidth`.
- Python's `http.server` sends no cache headers — Chrome heuristically caches JS/CSS
  and grades stale code. The crawler disables cache (`Network.setCacheDisabled`) and
  cold-loads each page with a `?_cb=` stamp.
- Chrome's history-manipulation hardening treats programmatic `location.hash` changes
  without user activation as replacements — the history phase drives **trusted
  `Input.dispatchMouseEvent` clicks** on real app links, like a user would.

To reproduce the audit yourself:

```bash
# terminal 1 — static server
cd Front_end && python -m http.server 8471
# terminal 2 — headless Chrome with CDP (dedicated profile)
chrome --headless --remote-debugging-port=9333 --user-data-dir=./_chr-profile about:blank
# terminal 3 — run the audits (Node ≥ 18, no npm deps)
node _audit_click.js
node _audit_final.js
node _verify_fixes.js   # targeted re-verification of the fixes above
```

## 6. Known, intentional simplifications

- Demo data is **deterministic** (seeded PRNG) — every reload shows the same figures,
  which is what makes the 8,566-route audit reproducible.
- UI chrome is bilingual (EN/বাংলা); **data values** (names, ids, codes) stay in English,
  as in localized Dynamics/ODoo deployments.
- Auth is simulated (any password + TOTP `123456`); payments/SMS/Maps show realistic
  flows, not live gateway calls.
- One mega-menu shows 11 areas by design: A01 Home is nav-less (`mods:[]`).

## 7. Design language

**"Service-Teal Fluent"** — a Dynamics-365-inspired Fluent-2 system tuned to the
1000 FiX brand: teal ramp anchored on `#0E7A6E`, neutral greys for chrome, AA-contrast
status triplets (ok/warn/err), 4px baseline grid, double-ring keyboard focus, dark theme,
and three densities (compact / cozy / relaxed). All charts read design tokens at render
time, so theme flips restyle every SVG.

---
*Prototype generated September 2026 · verified 8,566 routes ALL CLEAN + 390px mobile pass · evidence in `_shots/`*
