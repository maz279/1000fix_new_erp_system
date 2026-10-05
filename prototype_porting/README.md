# README — Prototype Porting Programme (PP)

**Purpose**: 100% port of the verified `Front_end/` prototype onto the production
stack (Odoo R1 + Next.js 16.3 R2 + QWeb R3 + Flutter R4), producing a real, deployable
system with real/test data discipline and zero damage to the built estate.

## Read in this order

1. [`00-MASTER-PLAN.md`](00-MASTER-PLAN.md) — mandate, constraints, verified current
   state, architecture mapping, phase graph
2. [`01-PORTING-PHASES.md`](01-PORTING-PHASES.md) — PP0–PP7 task tables
3. [`02-ASSET-PORTING-MATRIX.md`](02-ASSET-PORTING-MATRIX.md) — every prototype asset →
   destination (the "100% ledger")
4. [`03-DATA-STRATEGY.md`](03-DATA-STRATEGY.md) — real / test / forbidden data;
   demo-data elimination
5. [`04-RISK-AND-PROTECTIONS.md`](04-RISK-AND-PROTECTIONS.md) — no-damage protocols +
   risk register
6. [`05-DOD-100-PERCENT.md`](05-DOD-100-PERCENT.md) — the verification matrix (D1–D19) and Gate GP
7. [`06-EXTERNAL-FACTS.md`](06-EXTERNAL-FACTS.md) — evidence table for every external
   technology claim (web-verified 2026-10-05, zero-trust audit iteration 4)
8. [`ITERATIONS.md`](ITERATIONS.md) — the planning-audit iterations (1–4), recorded

## Headline numbers

- Prototype scope: 823 screens · 346 reports · 266 forms · 5,100 functions · 67 modules ·
  12 areas · 12 portals · 10 journeys · 4 personas · 8,566 verified routes
- Production today: backend 100% (64 modules, 123 models, all gates green); frontend
  portals 0% (empty `apps/`); foundation partial (tokens diverged, i18n 110 pending,
  W4 OpenAPI slice only)
- Porting phases: 8 (PP0–PP7), dependency-ordered, each gated by the full existing
  battery + new GP criteria

## Status

| Phase | State |
|---|---|
| PP0 Foundation Reconciliation | **COMPLETE** (2026-10-05 — teal tokens ×5 realisations, i18n 493/0-pending, nav registry + checker, mapping spec 65/67, contract +13 archetypes/+8 charts, prototype frozen; battery + gates green) |
| PP1 Platform Scaffolding | planned |
| PP2 P03 Admin (OWL) | planned |
| PP3 P04 Corporate slice | planned |
| PP4 Flutter apps | planned |
| PP5 Next.js portal batch | planned |
| PP6 Data strategy execution | planned |
| PP7 Hardening + Gate GP | planned |
