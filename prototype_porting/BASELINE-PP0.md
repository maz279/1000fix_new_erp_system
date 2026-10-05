# PP0 Baseline — the frozen prototype, measured (PP0-M05-T01)

**Frozen**: 2026-10-05 · **Method**: every headline number below was
recomputed programmatically from the payload (Python replication of the
prototype's own `_audit_meta.js` invariants) by
`tooling/generators/generate-nav-registry.py` — which FAILS if any number
drifts — and re-verified by `tooling/fitness/check-nav-registry.py` in CI.
The prototype's browser audits (`node _audit_click.js`, `_audit_final.js`,
`_audit_meta.js` — 8,566 routes ALL CLEAN + 390px mobile + focus + assets)
were last run by the prototype team before handover; their harness recipes
live in its README §5 and remain reproducible (static server :8471 +
headless Chrome CDP :9333). Re-running them against the FROZEN tree is
optional and must produce identical output — the tree cannot change.

## The frozen numbers (the porting denominator)

| Measure | Value | Enforced by |
|---|---|---|
| Areas | 12 | generator assert + checker |
| Portals | 12 | generator assert + checker |
| Modules | 67 (14 literal + 53 assignment declarations) | generator assert + checker |
| Screen groups | 278 | generator assert + checker |
| Screens | 823 unique ids (`t:` codes w g f r c d x s) | generator assert + checker |
| Report library | 346 (per-module `reports:[]` strings) | generator assert + checker |
| Form register | 266 (per-module `forms:[]` strings) | generator assert + checker |
| Sub-modules | 600 `freg.sub` triples | generator assert + checker |
| Functions | 5,100 (sum of triple counts; `src == sum(sub)` per module) | checker, per module |
| Journeys | 10, 54 steps, every step routed (`#/…`) | generator assert |
| Personas | 4 | generator assert |
| i18n catalogues | FX_I18N 74/74 EN↔বাংলা parity; LAND_I18N 40 keys (34 durable ported, 5 prototype-meta excluded, 1 locale-neutral excluded) | checker (parity) + copy pack |
| Design system | Service-Teal: 16-step ramp, primary `#0E7A6E`, WCAG-AA status triplets, dark theme, 3 densities | CFM-03 on the ported DTCG source |
| Prototype files | 5,462 lines (9 JS · 3 CSS · 3 HTML) | read-only reference |

## Where each asset landed at PP0

| Prototype asset | Production artefact (PP0 output) |
|---|---|
| `css/tokens.css` | `libs/ts/ui/src/tokens/tokens.json` (DTCG, 228 tokens) → generated SCSS/CSS/TS/Dart/flat; CFM 1–5 green |
| `nav_data*.js` + structural `demo_data` arrays | `contracts/nav/registry.json` (generated, checker-gated) |
| `js/i18n.js` + `LAND_I18N` + nav labels | copy pack `UI-900` (199 inline keys) in the registry → 493 keys, **0 counterpart-pending** |
| 13 archetypes + 8 chart primitives | `docs/design-system/component-contract.md` Parts 2–3 |
| Module universe M01–M67 | `docs/navigation/registry-to-production-mapping.md` (65/67 realised; M65 planned P12; M10 pending — on the record) |
