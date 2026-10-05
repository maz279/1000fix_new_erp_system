# Planning Iterations — three-pass audit record

The user's instruction: *"do 3 iterations to make sure you got it correctly."*
Each iteration is recorded here with what was checked, what was found, and what changed.

---

## Iteration 1 — Research & Draft (2026-10-05)

**Method**: read the prototype, the built estate, and the governing documents directly;
measure, don't assume.

**Verified facts gathered**:
- Prototype anatomy: 5,462 lines (9 JS + 3 CSS + 3 HTML); globals `FX_AREAS` (12),
  `FX_PORTALS` (12), `FX_MODULES` (67, entries carry `kpis/groups/screens/freg`),
  `FX_I18N` (74 keys EN↔bn), `FX_DEMO` (deterministic PRNG, seed 20260927);
  13 archetypes; 8,566-route crawl verified ALL CLEAN; 19 screenshots in `_shots/`.
- Built estate: 64 modules installed, 123 models, 531 + 194 tests green, fitness 6/6,
  comodel-deps 0, Gates G0b–G8 0 FAIL, smoke 14/14, seed idempotent double-run.
- Frontend foundation: token generator + CFM conformance exist; token source is
  **blue `#2563eb`** vs prototype **Service-Teal `#0E7A6E`** (the divergence, G1);
  i18n registry 294 keys / **110 counterpart-pending**; W4 OpenAPI slice (11 endpoints,
  P04/P08/P10/P06); `apps/web` + `apps/mobile` EMPTY; `contracts/`, `libs/dart` empty.
- Governing docs: `D-026` (Next 16.3 + Payload 3.73+, Node 22; old platform EOL 21 Oct
  2026), `D-027` (Flutter), UX-001 (one token source, 5 realisations, component
  contract), W0-05 migration plan (ERP blocked-by, not owner), DE-12 (no prod data on
  workstations), MIG-01…08 + MG-004/005 (migration discipline), the twelve environments,
  Keycloak 26 + Kong in the local compose stack.

**Produced**: `README.md`, `00-MASTER-PLAN.md`, `01-PORTING-PHASES.md` (PP0–PP7),
`02-ASSET-PORTING-MATRIX.md` (20 asset rows), `03-DATA-STRATEGY.md`,
`04-RISK-AND-PROTECTIONS.md` (10 protections, 12 risks), `05-DOD-100-PERCENT.md`
(16-criterion matrix + Gate GP).

---

## Iteration 2 — Audit vs artifacts (2026-10-05)

**Checks and findings**:

| # | Check | Finding | Fix applied |
|---|---|---|---|
| A1 | Prototype numbers re-derived from payload | Structure differs from first-pass regex assumption (modules are `M01: {...}` literals; screens use `t:'g'` codes) | Parser spec made explicit in PP0-M03-T01 (globals, `t:` codes, `freg`) |
| A2 | Prototype KPI arrays (`kpis:[{l,v,d,spark}]`) contain fabricated values | Risk: porting them would smuggle demo data into production | PP0-M03-T01 now **drops fabricated values** — registry keeps labels/ids only; values return via API |
| A3 | Portal spec table (04-00) says P01 app = **React Native** | Superseded by `D-027` (Flutter) | Architecture mapping notes the supersession; APP-04 is Flutter in PP4 |
| A4 | Portal spec says P06 = **Metabase** + Grafana | L4 stack baseline is **Apache Superset** + Grafana | Mapping row corrected with the reconciliation note |
| A5 | Roadmap waves (P01 W2 first) vs porting order (P04 first) | Apparent contradiction | §5 reconciliation added: PP3 = P04 because its OpenAPI slice exists (fastest vertical slice); P01's budget enforced from PP1 |
| A6 | App counts: L5 line "8 Next.js · 3 Flutter" vs tree "7 web dirs · 4 mobile dirs" | The roadmap's own RG-08 identifier-discipline issue | Reconciliation recorded in 05-DOD §App-count; basis = monorepo directories; CD register to reconcile in PP1 |
| A7 | Environment ladder draft listed non-existent env names | Roadmap's twelve are `local ci dev sit uat perf staging training sandbox migration-staging prod dr` | 05-DOD corrected, names verbatim, NFR-086c masking rule attached |
| A8 | PP3 auth assumed a local IdP | Verified: **Keycloak 26.3.0 is in the compose stack** | Task stands as written; grounded |
| A9 | Anti-fixture / SSRF / no-credentials constraints vs the Mimosa standing rules | All present in 03-DATA-STRATEGY §6 + protection P-09 | Confirmed, no change |
| A10 | Seed as sole test-data source | Seed already covers anchors + config masters (idempotent double-run verified 2026-10-05) | PP6 builds on it; no parallel fixture channel introduced |

---

## Iteration 3 — Final consistency verification (2026-10-05)

**Checks run**:
1. File set complete: README, 00, 01, 02, 03, 04, 05, ITERATIONS — 8 files present.
2. Internal links resolve (README↔00↔01..05↔ITERATIONS) — 0 broken after ITERATIONS written.
3. Headline numbers consistent across files: 823 / 346 / 266 / 5,100 / 67 / 12 / 12 /
   10 / 4 (prototype), 294/110 (i18n), 11 endpoints (W4 OpenAPI), 64 modules / 123
   models / 531+194 tests / G0b–G8 (estate) — same figures everywhere they appear.
4. Phase graph consistency: PP0→{PP1→{PP2,PP3,PP5},PP4}, PP6 after surfaces, PP7 last —
   task-table dependency columns match the graph.
5. Every gap G1–G9 in the master plan maps to at least one task in 01-PORTING-PHASES
   (G1→PP0-M01, G2/G3→PP1-M01, G4→PP1-M02, G5→PP1-M03, G6→PP0-M03, G7→PP6-E1,
   G8→PP0-M02, G9→R-03/D-026 rollback rule).
6. Every DoD row D1–D16 maps to a phase task or an existing battery check.
7. Constraints table (master plan §2) traceable to their source docs (D-026, D-027,
   UX-001, DE-12, EP-12, PE-004, AS-08/09/10, FF-25, BN-007).

**Residual honesty items** (named, not hidden):
- The 8-vs-7 / 3-vs-4 app-count discrepancy in the roadmap (A6) is recorded, not
  silently resolved — CD register reconciliation is a PP1 task.
- The old `1000fix-portal-platform` migration is owned by the CON-03 platform team and
  is outside this programme's control; the D-026 rollback rule (standalone 16.3
  deployments) is the containment.
- Real production data enters only through the MIG pipeline with sign-off; no porting
  task may shortcut that.

**Verdict**: plan is consistent, grounded in measured artifacts, dependency-ordered,
and protectively gated. Ready to execute starting at PP0.

---

## Iteration 4 — Zero-trust evidence audit (2026-10-05, user-commissioned)

**Method**: nothing from iterations 1–3 was trusted. Every number was re-measured
against the live systems; every external claim was re-searched on the open web; every
framework claim was checked against the vendored source; structural claims about the
prototype were re-derived from its payload with corrected parsing.

### Errors found and fixed

| # | Defect | Evidence | Fix |
|---|---|---|---|
| E4-1 | Master plan header said "**715+ tests**" — internally inconsistent with its own "531 + 194" (correct sum: **725**) | Full pytest re-run 2026-10-05: 531 addons + 194 service | Header corrected to 725 with the breakdown and re-run date |
| E4-2 | PP0-M03-T01 parser spec implied journeys/personas come from `nav_data*.js` | Payload recount: they live in **`demo_data.js`** (`FX_DEMO.JOURNEYS` ×10, `FX_DEMO.PERSONAS` ×4) — the file slated for elimination | Parser spec rewritten: structural arrays **extracted from demo_data.js** into the registry; fabrications dropped |
| E4-3 | Parser spec assumed one module-declaration syntax | nav_data.js uses literal keys (14 modules); nav_data2/3 use `FX_MODULES.Mxx =` assignments (53) — 67 total ✓ | Both syntaxes documented in the spec; `freg.sub` triple shape `[id, name, count]` documented |
| E4-4 | The landing's marketing copy dictionary was unknown | `LAND_I18N` (~30 keys) found inline in `index.html` — a third i18n surface beyond `FX_I18N` (74/74) and nav labels | Added to PP0-M02-T01 and the asset matrix |
| E4-5 | WCAG level unstated in the porting delta | Prototype landing self-describes **WCAG 2.1 AA**; programme standard is **2.2 AA** | Recorded as matrix row 21 + risk R-15 (added scope, not relaxation) |
| E4-6 | Payload "3.73 = full Next-16 support" passed through from D-026 as settled | **Web-unverifiable**: newest indexed Payload release is 3.61.1 (Oct 2025); the local verification record says only "repo active" | Flagged ⚠️ in 06-EXTERNAL-FACTS F4; PP1-M01-T03 re-verification task + risk R-13; Payload restricted to CMS-true surfaces |

### Confirmed correct (re-verified, not assumed)

- i18n catalogue **74/74 parity** (an intermediate 44-count was a regex artifact,
  corrected by block-level parse — the README's claim held)
- 823 unique screen ids · 67 modules · 10 journeys · 4 personas · 12 portal cards
  (landing renders from `FX_DEMO.PORTALS`)
- Estate: 64 modules · 123 models · 531+194 tests · i18n 294/110 · OpenAPI 11 paths ·
  token source still `#2563eb` (divergence live)
- **OWL version resolved against the vendored source**: Odoo 19.0.0 ships **OWL 2.8.4**
  (`vendor/odoo/addons/web/static/lib/owl/owl.js`); web claims of "OWL 3 in Odoo 19"
  describe the upstream 3.0.0 **alpha** — the plan's R1 = OWL 2 stands, now with
  primary-source evidence
- Next 15 EOL 21 Oct 2026 / 16.3 line current (16.3.8 LTS); Turbopack default; Node 20
  EOL 30 Apr 2026 / Node 22 LTS; Flutter 3.44 Impeller+SwiftPM defaults; Keycloak 26
  line active (compose pins 26.3.0); Kong 3.9 in the stack

### Gaps found and closed (added scope)

| Gap | Fix |
|---|---|
| Kong 3.9 API gateway never mentioned although in the local stack | PP1-M02-T01 routes all portal traffic through Kong; risk R-16; constraint row |
| PDPA consent has a backend (`fix.consent`) but **no portal API** and no portal surface | PP1-M03 consent endpoints in `contracts/openapi/`; P01 consent dashboard task (PP5) |
| No CSP/security-header task | PP7 task + DoD **D17** (CSP nonces, HSTS, frame-ancestors for embedded BI, CORS at Kong) |
| No frontend observability task | PP7 task + DoD **D18** (OTel browser→Kong→Odoo, RUM to the existing stack) |
| No external-fact currency rule | DoD **D19** + `06-EXTERNAL-FACTS.md` with checked dates and links |
| Legacy platform code assumed present | Absence verified (docs-only folders); W0-05 scope explicitly marked external (F15) |
| Next-16 breaking changes not planned | PP1-M01-T03 checklist (`proxy.ts`, Cache Components, Turbopack) + risk R-14 |

### Files revised

All 8 existing files updated; **`06-EXTERNAL-FACTS.md` added** (15-row evidence table
F1–F15 with sources). Doc map and cross-links updated in README and 00.

**Verdict**: the plan now carries zero unverified external claims without a flag, zero
internally inconsistent numbers, and four previously missing scope items (Kong, consent,
CSP, observability) — each traceable to evidence.

---

## Iteration 5 — Audit of the audit (2026-10-05, user-commissioned)

**Method**: iteration 4's own outputs were treated with the same zero trust. The
prototype's authoritative recomputation harness (`_audit_meta.js`) was read in full and
replicated in Python; every count claim was re-derived from the payload syntax it
actually depends on; remaining feasibility assumptions were traced to the tooling
source.

### Defects found in iteration 4's work

| # | Defect | Evidence | Fix |
|---|---|---|---|
| E5-1 | **The parser spec would have silently dropped the 346-report library and 266-form register.** Iteration 4 verified "823 screens" via `t:` codes (80 report-viewer screens, 26 form screens) but never identified where 346/266 live | `_audit_meta.js` sums per-module arrays `m.reports` / `m.forms`; Python replication counts exactly **346 report strings and 266 form strings across 67 modules** | PP0-M03-T01 and asset-matrix row 2 now specify `reports:[…]`/`forms:[…]` arrays as registry sources; the CI meta-audit recomputes them |
| E5-2 | **LAND_I18N count was an estimate** ("~30 keys") | Block-level count: **17 keys** | Corrected to 17 in 00, 01, 02; F12 updated |
| E5-3 | Groups (278) absent from the parser spec although the landing itself cites "278 groups" and screens nest inside them | `screens:[` array count = 278 | Added to spec + matrix + F13 |
| E5-4 | "Merge into the registry" stated no concrete mechanism | `extract-ui-copy.py` reads ONLY `project_content/03_UI_Copy_and_Microcopy/**/*.md` | PP0-M02-T01 now names the copy-pack path as the authoring surface |

### Verified exactly (Python replication of `_audit_meta.js`)

278 groups · 823 unique screen ids · 600 `freg.sub` triples · 5,100 function sum ·
346 report strings · 266 form strings · 67 modules (14 literal + 53 assignment) ·
i18n 74/74 · LAND_I18N 17 · 4 static + 11 rendered = 15 landing area cards ·
`freg.src == sum(sub)` consistency is the prototype's own invariant and is now a CI
check in the ported meta-audit.

### Consistency checks re-run

- PP1 task numbering after the iteration-4 insert: T01–T03 sequential, no collision ✓
- "R1 OWL" vs "R1 OWL 2": consistent (constraints row carries the precise 2.8.4) ✓
- Cross-file number sweep: 346/266/278/600/5,100/17/74 identical everywhere cited ✓

**Verdict**: the plan's registry generator is now specified against the payload's real
syntax with independently recomputed counts — the single highest-risk artifact (the
navigation registry everything else consumes) is no longer specified from assumptions.

---

## PP0 execution record (2026-10-05) — three implementation iterations

**Iteration 1 — implement** (commit `cfd52fdf1b`): all five PP0 milestones built and
verified in-turn (details in the commit message and `BASELINE-PP0.md`). Mid-iteration
defects caught and fixed at the time: LAND_I18N recount (40 keys, not 17 — the same
line-anchored-regex artifact class), a no-Bengali counterpart that would have stayed
pending forever (`p03.list.bulk`, now guarded by a startup assert), journey-step parser
shape (`[['actor','desc','#route']]`, `]]` terminator), portal-row over-matching, the
style-1 module body running past `};` into the assignment files (double count), and one
en-cell mismatch caught by the applier's own verify step.

**Iteration 2 — audit of the implementation**: blue `#2563eb` eradicated from live
values (survives only in "replaced the interim blue" descriptions); teal present in all
realisations; **found and fixed a stale loader comment** claiming "266 BN counterparts
pending" (reality: 0 — note updated, commit `2ad8b047d8`); repo-formats initially red
only because it demands generated artifacts be committed with their source (clean after
commit — the check's contract working as designed); smoke 14/14; Odoo serving 200;
pack content spot-checked. The extended portal-contract checker also **surfaced a real
pre-existing regression**: `cd_party_master` had drifted to 10 second-level sections
across phases 5–11 (NVR-23 max 7) — fixed by nesting the four governance surfaces
under a Data Governance section; module upgraded on the live registry.

**Iteration 3 — final verification**: fitness 8/8 (including the two new checks —
`check-nav-registry` and the registry-coverage extension of `check_portal_contract`),
CFM 1–5 green, contract carries exactly 13 archetype sections and 8 chart rows,
nav-registry invariants all hold (counts, per-module ledger, unique ids, area
integrity, i18n parity, freshness), gates G0b–G8 all 0 FAIL, 531 addons tests green,
tree clean.

**Exit criteria — all met**: tokens Service-Teal everywhere (CFM-03 WCAG AA) ✓ ·
i18n 0 counterpart-pending (493 keys) ✓ · navigation registry generated + CI-checked ✓
· contract covers the 13 archetypes + 8 charts ✓ · prototype frozen read-only with the
baseline recorded ✓ · full battery green ✓.

**Carried forward (on the record, not hidden)**: M10 Loyalty has no production
realisation yet (mapping kind `pending`); M65 lands in Phase 12; the 5 prototype-meta
landing keys and 1 locale-neutral key are deliberately not ported (data strategy);
the PP2 exceptions register will record every module whose workspace sections nest
beyond the prototype's group order.

---

## PP0 audit of the implementation (2026-10-05, user-commissioned — iteration 4 of PP0)

Zero-trust re-verification of every PP0 artefact against the **running system**, not
the committed files. One critical, three material findings — all fixed in-turn.

| # | Finding | Evidence | Fix |
|---|---|---|---|
| P0-1 | **CRITICAL (pre-existing since Phase 4): the `:root` CSS-custom-property bridge was dead.** Sass preserves custom-property values verbatim, so `--fix-x: $ref` leaked 228 literal `$refs` into the compiled backend bundle — the design tokens were never reachable as CSS variables in Odoo; only the partials' inline `$var` use worked | Served `web.assets_web.min.css` carried `--fix-color-status-brand: $color-status-brand`; confirmed against the Sass spec (sass-lang.com, Custom Properties) | Generator now emits **values directly** in the `:root` block; module upgraded; live bundle re-verified: fresh hash, `--fix-color-status-brand: #0e7a6e`, **0 `$ref` leaks**, dark tokens present |
| P0-2 | **Token-fidelity gap: dark-mode shadows never ported** (the programmatic diff of all 94 prototype CSS variables vs the DTCG tree — everything else matched under renamed keys) | diff output: 3 dark shadow overrides missing | `shadow.dark.{sm,md,lg}` added (231 tokens now); regenerated; CFM green; module upgraded; live bundle carries `--fix-shadow-dark-*` |
| P0-3 | **UI-900 landing EN truncated where the prototype splits text across a sibling `<b>`**: `proto.land.s5` read ":2015 certified operations" | pack row | Generator composes the full string ("ISO 9001:2015 certified operations") and now **fails the run** on any EN cell that starts with punctuation or is empty; pack + registry regenerated |
| P0-4 | **The nav-registry checker wasn't in the official battery** (it ran standalone; `verify-repo` didn't know it) | `tooling/fitness/registry.yaml` had no entry | Added **FF-38 (blocking)**: "navigation registry integrity — counts, ledger, ids, areas, i18n parity, freshness"; `verify-repo` now runs it (PASS) |

Also verified and closed without changes: journeys are EN-only in the frozen payload
(0/10 carry `bn` — faithful freeze; production Bengali journey names are a PP5 item,
now recorded in the registry `$note`); the registry's portal `tech` strings are
prototype-era and now carry a `$note` marking them superseded by D-026/D-027/L4;
pack table integrity is proven by the extractor's clean regeneration (493 unique
keys); `s5`-style truncation cannot recur (generator assert).

**Battery after fixes**: 531 addons tests · fitness 0 failures (FF-38 now blocking) ·
CFM 1–5 · smoke 14/14 · gates G0b/G4/G8 0 FAIL.
