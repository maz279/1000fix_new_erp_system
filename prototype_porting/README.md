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
- Production today: backend 100% (64 modules, 123 models, 725 tests, all gates green);
  foundation 100% (PP0 complete: Service-Teal 231 tokens, i18n 493 keys with 0 pending,
  nav registry active + FF-38 enforced, component contract +13 archetypes/+8 charts);
  frontend portals 0% (empty `apps/`) — **that is what PP1 starts**
- Porting phases: 8 (PP0–PP7), dependency-ordered, each gated by the full existing
  battery + new GP criteria

## Status

| Phase | State | Next action |
|---|---|---|
| PP0 Foundation Reconciliation | **COMPLETE** (2026-10-05 — teal tokens ×5 realisations + live-bundle-verified bridge, i18n 493/0-pending, nav registry + FF-38, mapping 65/67, contract +13/+8, prototype frozen) | — |
| PP1 Platform Scaffolding | **COMPLETE** (2026-10-06 — 7 Next 16.3.8 apps scaffolded, corporate built green at 171 KB gz; 4 Flutter skeletons; api-client lib; contracts/openapi ×3 with FF-40; anti-fixture FF-39 blocking; Payload F4 closed live) | PP2 (P03 menus from the registry) |
| PP2 P03 Admin (OWL) | **COMPLETE** (2026-10-06 — cd_p03_portal with 301 menus; OWL workspace A2 + Tell-ME A13 (EN+বাংলা, Ctrl+K, keyboard nav) + Report Center A10/A11 (346 reports, area/query filter) + Dispatch Console A7 (live read_group) + BPF stepper + FactBox A5 on service order + grid conformance A4 (filter chips, sortable, status pills, focus ring) + tab rail; 34 tests; coverage ledger 0/754) | PP3 (P04 Corporate vertical slice) |
| PP3 P04 Corporate slice | **NEXT — start here** | playbook §PP3: OIDC login → estate → invoices → service requests → template extraction |
| PP4 Flutter apps | planned | after PP1 (parallel with PP3) |
| PP5 Next.js portal batch | planned | after PP3 |
| PP6 Data strategy execution | planned | with PP5+ |
| PP7 Hardening + Gate GP | planned | last |
