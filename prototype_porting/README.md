# README — Prototype Porting Programme (PP)

**Purpose**: 100% port of the verified `Front_end/` prototype onto the production
stack (Odoo R1 + Next.js 16.3 R2 + QWeb R3 + Flutter R4), producing a real, deployable
system with real/test data discipline and zero damage to the built estate.

## ▶ START HERE — begin porting phase by phase

1. Read [`07-PORTING-PLAYBOOK.md`](07-PORTING-PLAYBOOK.md) — the execution runbook:
   environment pre-flight commands, then PP1→PP7 step-by-step with exact commands,
   entry/exit gates, and per-phase skill guidance.
2. Run the pre-flight (`doctor` + `verify-repo` + conformance + nav-registry + smoke).
3. Start **PP1 — Platform Scaffolding** (playbook §PP1). PP0 is complete; nothing
   blocks PP1.
4. Daily loop: task table ([`01`](01-PORTING-PHASES.md)) → implement via Write/Edit →
   run the task's Verify column → battery green → commit → one-line record in
   [`ITERATIONS.md`](ITERATIONS.md).

**Normative sources** (the only ones): the roadmap, `contracts/nav/registry.json`,
the DTCG token source, the component contract. Everything labelled *(non-normative)*
or **[TARGET]** is optional/unratified — see [`AUDIT_REPORT.md`](AUDIT_REPORT.md) §5.2.

## The document set

| # | File | Role |
|---|---|---|
| 1 | [`00-MASTER-PLAN.md`](00-MASTER-PLAN.md) | mandate, constraints, verified state, architecture mapping, phase graph |
| 2 | [`01-PORTING-PHASES.md`](01-PORTING-PHASES.md) | PP0–PP7 normative task tables (what & why) |
| 3 | [`07-PORTING-PLAYBOOK.md`](07-PORTING-PLAYBOOK.md) | **execution runbook (how & order) — start here** |
| 4 | [`02-ASSET-PORTING-MATRIX.md`](02-ASSET-PORTING-MATRIX.md) | every prototype asset → destination (the "100% ledger") |
| 5 | [`ARCHITECTURE_STATE.md`](ARCHITECTURE_STATE.md) | architecture state — sections labelled [FACT]/[TARGET]; journey→E2E matrix (54 steps), Kong ingress design, offline-sync design |
| 6 | [`03-DATA-STRATEGY.md`](03-DATA-STRATEGY.md) | real / test / forbidden data; demo-data elimination; statutory masking; money = backend-only |
| 7 | [`04-RISK-AND-PROTECTIONS.md`](04-RISK-AND-PROTECTIONS.md) | no-damage protocols + risk register (R-1…R-18) |
| 8 | [`05-DOD-100-PERCENT.md`](05-DOD-100-PERCENT.md) | the verification matrix (D1–D19) and Gate GP |
| 9 | [`06-EXTERNAL-FACTS.md`](06-EXTERNAL-FACTS.md) | evidence table for every external technology claim (web-verified 2026-10-05) |
| 10 | [`LEARNINGS.md`](LEARNINGS.md) | defect RCAs L-01…L-05 (real) + design cautions + conventions |
| 11 | [`ITERATIONS.md`](ITERATIONS.md) | the audit trail (planning iterations 1–5, PP0 execution + audits) |
| 12 | [`BASELINE-PP0.md`](BASELINE-PP0.md) | the frozen prototype, measured |
| 13 | [`AUDIT_REPORT.md`](AUDIT_REPORT.md) / [`CODEBASE_RISK_REGISTER.md`](CODEBASE_RISK_REGISTER.md) | forensic audit of this folder (2026-10-05) + live risk register |

## Headline numbers

- Prototype scope: 823 screens · 346 reports · 266 forms · 5,100 functions · 67 modules ·
  12 areas · 12 portals · 10 journeys · 4 personas · 8,566 verified routes
- Production state (audit-verified 2026-10-14): all 8 phases PP0–PP7 executed; 8 web
  portals live (202–250 KB gz vs the 400 KB contract) with nonce-CSP + HSTS; P03
  workspace wired to the live backend; 12 portal surfaces in place (4 Flutter apps
  structurally validated — device compile/E2E awaits an SDK machine); **Gate GP:
  9 PASS / 3 CONDITION / 0 FAIL** (the 3 conditions are deployment-side: staging
  OTel round-trip, migration rehearsal at volume, promote drill). The 754-screen
  per-action data burn-down continues phase-by-phase per the coverage ledger.
- Porting phases: 8 (PP0–PP7), dependency-ordered, each gated by the full existing
  battery + new GP criteria

## Status

| Phase | State | Next action |
|---|---|---|
| PP0 Foundation Reconciliation | **COMPLETE** (2026-10-05 — teal tokens ×5 realisations + live-bundle-verified bridge, i18n 493/0-pending, nav registry + FF-38, mapping 65/67, contract +13/+8, prototype frozen) | — |
| PP1 Platform Scaffolding | **COMPLETE** (2026-10-06 — 7 Next 16.3.8 apps scaffolded, corporate built green at 171 KB gz; 4 Flutter skeletons; api-client lib; contracts/openapi ×3 with FF-40; anti-fixture FF-39 blocking; Payload F4 closed live) | PP2 (P03 menus from the registry) |
| PP2 P03 Admin (OWL) | **COMPLETE** (2026-10-06 — cd_p03_portal with 301 menus; OWL workspace A2 + Tell-ME A13 (EN+বাংলা, Ctrl+K, keyboard nav) + Report Center A10/A11 (346 reports, area/query filter) + Dispatch Console A7 (live read_group) + BPF stepper + FactBox A5 on service order + grid conformance A4 (filter chips, sortable, status pills, focus ring) + tab rail; 34 tests; coverage ledger 0/754) | PP3 (P04 Corporate vertical slice) |
| PP3 P04 Corporate slice | **COMPLETE** (2026-10-06 — 7 routes built at 205 KB gz; estate/invoices/service-requests with backend-computed BDT; OIDC auth shell; dark mode + density; api-client callOdoo; Odoo controllers for the W4 contract) | PP4 (Flutter apps) or PP5 (portal batch) |
| PP4 Flutter apps | **COMPLETE** (2026-10-06 — `fix_offline` engine per AR-010: SP-07 upload-first sync, DI-05 idempotency, SP-09 deferred evidence, §6 two-state conflict disclosure; 4 apps: P02 technician (diagnostic tree/fault coding), P09 rider (custody chain), P11 auditor (8-item ISO checklist), APP-04 customer (Bengali-first); FF-41/FF-42 blocking; deep-audit fixes ee190f620d. Honest note: no Dart SDK on the build machine — structural validation only, first SDK run must `flutter analyze` + device-lab E2E) | PP5 (Next.js portal batch) |
| PP5 Next.js portal batch | **COMPLETE + LIVE-VERIFIED** (2026-10-06 — 7 portals: P01 customer (Bengali-first, 7 routes, ~154-177KB gz), P05 vendor (new app), P06 analytics (config-only BI embed), P07 seller, P08 brand (brand_id isolation), P10 agent console (queue+360+softphone seam), P12 partner; 7 API controllers + NEW cd_customer_portal; OpenAPI 29 paths; FF-43 blocking parity gate; shared landing shell. Deep audit: all 25 routes LIVE-FIRED on fix_dev (45/45 positive+negative), 4 bugs fixed (invoice OU, None-default trap, brand kwargs collision, Decimal model bug), SSR visual 38/38 + CFM-01 hex-proof; 646 tests) | PP6 (data strategy execution) |
| PP6 Data strategy execution | **COMPLETE** (2026-10-06 — the three data classes machine-enforced: FF-44 demo-literals gate (estate swept clean + Odoo demo-data policy), FF-45 data-shape parity (14 grids column-complete) + §7 statutory masks in libs (BIN/NID/e-TIN, no invented checksums) + bn007, FF-39 extended with a client money-arithmetic guard, seed double-run refusal in smoke (exit 2 verified), migration-staging profile + MIG-02 mig-totals verifier + MG-004 rehearsal record. 646 tests · fitness FF-38..45 green · smoke 15/15 · 7/7 builds) | PP7 (hardening + Gate GP) |
| PP7 Hardening + Gate GP | **COMPLETE** (2026-10-13 — nonce-CSP/HSTS on all 8 portals + Kong response policy; J01–J10 journey E2E 10/10 ×3 runs zero flakiness; WCAG 2.2 AA gatekeeper 25/25 routes 0 serious/critical; budgets 8/8 ≤250 KB gz; OTLP-shaped RUM seam (inert-by-default); Gate GP verifier 9 PASS / 3 CONDITION / 0 FAIL. Found+fixed en route: JSX-runtime void-0 hydration bug (7 apps), 63-of-67 registry title drift, parallel-session QC-forgery handler + fake GPS/Twilio remnants. See ITERATIONS.md PP7 record) | 3 deployment-side conditions (staging OTel round-trip; migration rehearsal; promote drill) + Flutter SDK compile pass |
