# External Facts — Evidence Table (zero-trust verification)

Every technology claim the plan depends on was re-verified on **2026-10-05** (iteration
4): internal numbers against the live systems, external claims against the open web,
and framework claims against the **vendored source** where one exists (the vendored
source wins over both memory and blog posts). Status legend: ✅ verified · ⚠️
unverifiable online — basis is local evidence only, re-verify at execution · 🔎
partially corroborated.

| # | Claim (as used in the plan) | Evidence | Status | Consequence |
|---|---|---|---|---|
| F1 | Next.js 15 reaches EOL **21 Oct 2026**; 16.3 is the current supported line (**16.3.8 LTS** at check; security release 16.3.3 moved to 25 Aug 2026) | Web: endoflife.date, eosl.date, nextjs.org, releasebot.io (searched 2026-10-05) | ✅ | D-026 baseline unchanged; the old platform's deadline is real and ~2 weeks away |
| F2 | **Turbopack is the default bundler** for `next dev` + `next build` in Next 16 | Web: multiple release coverages (Nov 2025–2026) | ✅ | No webpack in portal builds unless the documented escape hatch is needed (R-14) |
| F3 | Next 16 breaking changes: **`middleware.ts` → `proxy.ts`**, Cache Components (`'use cache'`) explicit, React 19 generation | Web: Next 16 migration coverage | ✅ | PP1-M01-T03 checklist |
| F4 | **Payload CMS "3.73.0 (23 Jan 2026) = full Next.js 16 support"; 15.5–16.1.x permanently unsupported** | Web: **could not verify — newest indexed release is 3.61.1 (Oct 2025)**. Local: `tooling/version-currency/evidence/verification-record-2026-10-01.json` records only "repo active" for Payload; the 3.73/23-Jan specifics rest on the roadmap's 2026-08-19 verification note, whose upstream snapshot is not in the evidence pack | ⚠️ | R-13 + PP1-M01-T03: re-run the version-currency ritual against payloadcms.com **before any Payload code**; restrict Payload to P01/marketing surfaces only |
| F5 | **Node 20 EOL 30 Apr 2026**; Node 22 is the LTS line (Active→Maintenance 20 Oct 2026; support into 2027–28) | Web: Node release schedule coverage | ✅ | Node 22 floor confirmed for all portal tooling |
| F6 | **Flutter 3.44 / Dart 3.12**: Impeller (Vulkan) default on Android; SwiftPM default on stable | Web: Flutter 3.44 coverage (Jun 2026), GitHub issues | ✅ | PP1 fvm pin; iOS secondary target uses SwiftPM |
| F7 | Flutter 3.44 "moves Material and Cupertino out of the core SDK; Skia removed from Android" (roadmap P02-M02-T03 warning) | Web: **only partially corroborated** — Impeller-default confirmed; the package-extraction detail did not surface in search results | 🔎 | Treat the roadmap's warning as plausible-but-unconfirmed; verify in the fvm pin step (PP1) before relying either way |
| F8 | **Keycloak 26** line is current and actively patched (26.x since Sep 2024; later minors security-focused) | Web: Keycloak release coverage; local: compose pins `keycloak:26.3.0` | ✅ | OIDC auth for portals as planned (PP3) |
| F9 | **Odoo 19 ships OWL 2**, specifically **2.8.4** | **Vendored source**: `vendor/odoo/addons/web/static/lib/owl/owl.js` contains `"2.8.4"`; `odoo/release.py` = 19.0.0 FINAL. Web claims of "OWL 3 in Odoo 19" refer to the upstream `odoo/owl` **3.0.0 Alpha**, which is not what ships | ✅ (vendored source wins) | R1 realisation targets OWL 2.8.x APIs; do not adopt OWL 3 alpha APIs |
| F10 | **Kong 3.9** is the local API gateway | Local: `infra/compose/docker-compose.yml` pins `kong:3.9` | ✅ | Portals route through Kong (PP1-M02-T01); gateway config as code (R-16) |
| F11 | WCAG **2.2 AA** is the programme standard; the prototype landing self-describes **2.1 AA** | Local: prototype `index.html` says "WCAG 2.1 AA"; roadmap UX-005/QA-008 mandate 2.2 | ✅ (discrepancy recorded) | R-15: 2.2 superset priced into PP7 |
| F12 | i18n prototype catalogue = **74 keys per locale with full EN↔বাংলা parity**; landing dictionary `LAND_I18N` = **17 keys** | Local: block-level recount of `js/i18n.js` (74/74) and `index.html` `LAND_I18N` (17) — the prototype README's 74/74 claim held; an earlier quick regex undercounted (44), corrected in iteration 4; LAND_I18N estimate (~30) corrected to the exact 17 in iteration 5 | ✅ | PP0-M02 merge volume known |
| F13 | Prototype scope numbers: 823 screens · 67 modules · **278 groups** · 346 reports (per-module `reports:[…]` string arrays) · 266 forms (per-module `forms:[…]`) · 600 sub-module triples · 5,100 functions · 10 journeys · 4 personas · 12 portal cards | Local: payload recount + `_audit_meta.js` logic replicated in Python — every headline now independently recomputed (iteration 5) | ✅ | Registry generator spec (PP0-M03-T01) is syntax- and count-accurate, including the report/form array sources iteration 4's spec missed |
| F14 | Estate battery at plan time: **531 addons + 194 service = 725 tests**; 64 installed cd_* modules; 123 AS-02/03 models; i18n registry 294 keys/110 pending; W4 OpenAPI 11 paths; token source still `#2563eb` (diverged) | Local: all re-run/re-read 2026-10-05 (pytest, psql, registry JSON, OpenAPI JSON) | ✅ | Plan header corrected (an earlier draft said "715+"); gap list G1–G9 confirmed current |
| F15 | The legacy `1000fix-portal-platform` (Next 15 + Payload 3) codebase | Local: **not present in this workspace** — only documentation folders exist under `1000_fix_corporate_website/` | ✅ (absence verified) | W0-05 migration happens elsewhere (CON-03 team); ERP portals are greenfield in our monorepo (D-026 rollback rule) |

## Rules carried forward from this verification

1. **The vendored source beats the web** for anything shipped in `vendor/` (F9).
2. **A claim with no online verification and no local snapshot is treated as
   unverified** (F4) and gets a re-verification task at the moment of first use — never
   a silent pass-through.
3. Every row here carries its checked date; DoD D19 requires re-verification ≤ 90 days
   at each phase gate where the claim is load-bearing.

## Search sources (2026-10-05)

- Next.js: endoflife.date · eosl.date · nextjs.org (security-release notice) ·
  releasebot.io · JavaScript-in-Plain-English (Next 16/Turbopack coverage)
- Node.js: release-schedule coverage (hysenlabs summary of the official schedule)
- Flutter 3.44: goldeninfosystems.com release breakdown · zenn.dev roadmap review ·
  GitHub issue tracker
- Keycloak: idptrust security-release blog · Red Hat docs · heise online
- Payload: newreleases.io (3.61.1 as newest indexed) · payloadcms.com docs (checked,
  no 3.73 found in indexed content)
