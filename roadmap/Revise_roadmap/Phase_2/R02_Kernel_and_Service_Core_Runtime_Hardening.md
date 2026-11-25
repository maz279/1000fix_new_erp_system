---
id: RR-02
title: "R02 — Kernel & Service-Core Runtime Hardening"
series: Revised Implementation Roadmap (RIR) — 11 phases · 55 milestones
derives_from: IR-002 Phases 3–4 residual items (P03-M01…P04-M10)
evidence_base: >
  Gate re-runs 2026-10-15: G1a 4 PASS · 6 CONDITION; G1 2 PASS · 10 CONDITION; migration specs
  exist (migration-mig-standards.md + migration-etl-specs.md) but no loads executed; 3 modules
  ship without .po files (cd_customer_portal, cd_p03_portal, cd_design_tokens); "all 32 modules
  install live" commit (c72633ae29) never recorded against G1a.
status: EXECUTED 2026-10-16/17 — zero-trust-audited 2026-10-22: G1a CONDITION (7P/3C), G1 CONDITION (6P/6C); permission suite was tautological (mock-raised AccessError) — live ir.rule isolation now proven separately; MG-004 sign-off PENDING; walk-in timing INCOMPLETE
---

# R02 — Kernel & Service-Core Runtime Hardening

## Charter

| | |
|---|---|
| **Purpose** | Convert the built-but-unproven Wave-1 kernel and service core from "GREEN-on-artefacts" to GREEN-on-evidence: runtime install proof, the 53-role permission suite, runtime Bengali completeness, the four Wave-1 migration loads, and the G1 evidence pack |
| **Source phases** | IR-002 P03 + P04 remainders |
| **Entry evidence** | G1a-1/2/5/6/7/9 CONDITION; G1-02…10/12 CONDITION; audit §2 Phase 3–4 rows |
| **Exit** | G1a and G1 re-run with 0 FAIL and all runtime CONDITIONs discharged or converted to named production conditions |

---

## Milestone R02-M01 — Clean-install and runtime proof of the 66-module estate

**Evidence:** G1a-1 "clean-install = Odoo runtime" and G1a-2 "six shared-kernel concepts" both CONDITION; commit c72633ae29 claims "all 32 modules install live" but predates 34 later modules and was never recorded as gate evidence.

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R02-M01-T01 | Extend `make odoo-install-wave1` to install **all 66 modules in AR-007 dependency order** into a clean `fix_dev` (currently installs only `base,cd_party_master` per Makefile fallback line) | Makefile: `odoo-install-wave1: … -i base,cd_party_master … || echo "extend the module list"` | Full-install target | Clean DB install log, 0 errors |
| R02-M01-T02 | Prove OD-02 installability per module: every `cd_*` installs **alone** into a clean database in dependency order; record results in the fitness evidence store | G1a-1 CONDITION; P03-M10-T01 "a module that cannot install alone is not a module" | Per-module install matrix | Matrix 66/66 green |
| R02-M01-T03 | Record the six shared-kernel concepts (party, product, location, legal entity, document, event) modelled once and consumed — re-run the FF-01/FF-17 checks against the installed runtime, not just source | G1a-2 CONDITION | Kernel conformance report | Report filed; FF-01 live |
| R02-M01-T04 | Boot Odoo with the full profile, serve `/web/login`, and capture the six P03 workspaces rendering (dispatch console, service intake, party master, device registry, catalogue, administration) | G0b doctor check 6 pattern; P04-M06 deliverables never runtime-verified | Runtime screenshots/logs in evidence | Login + 6 workspace routes HTTP 200 |

---

## Milestone R02-M02 — Permission negative tests: 53 roles × 6 isolation tiers

**Evidence:** G1a-5 "Permission negative tests (DoD-07)" CONDITION; `cd_rbac_ext` ships `fix.role` (53 roles), `fix.isolation.tier` (T0–T5) and 61 SoD controls — none negative-tested per role.

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R02-M02-T01 | Build the permission test harness: one Odoo tests class that iterates the 53 seeded `fix.role` records and asserts denial for users without each role on representative models per tier | DoD-07: "negative-tested for every applicable role"; G1a-5 | `cd_rbac_ext/tests/test_permissions_negative.py` | Suite runs green at runtime |
| R02-M02-T02 | Negative-test the six isolation tiers: a T2 branch user cannot read another operating unit's records; a T5 read requires step-up flags; record-rule domains assert | `05-04` §4; AS-03/FF-21 | Tier test suite | All 6 tiers covered |
| R02-M02-T03 | Negative-test the 61 SoD controls: assign each conflicting role pair and assert the declared block/warn/log action fires (`check_assignment()`) | `fix.sod.control` model exists with `check_assignment()` — never exercised | SoD test suite | 61 controls tested |
| R02-M02-T04 | Negative-test field-level rules on residency-classified fields: a user without the field rule sees the masked/absent value; Z4 reads logged | `residency.mixin` + `fix.field.rule` exist; NFR-086a mechanism untested at runtime | Field-rule tests | Suite green |
| R02-M02-T05 | Wire the permission suite into CI stage 3 (model-registry) or a dedicated stage so it runs pre-merge from now on | §0.8.4 pipeline discipline | CI wiring | First green CI run incl. suite |

---

## Milestone R02-M03 — Bengali completeness at runtime, including the three uncovered modules

**Evidence:** G1a-6 and G1-05 CONDITION; audit V-10 — 19 shipped `.po` files are 100% translated, but `cd_customer_portal`, `cd_p03_portal`, `cd_design_tokens` ship **no** `.po` (JS surfaces rely on the generated ui-copy registry with 110 keys marked counterpart-pending in the P04 record).

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R02-M03-T01 | Extract and translate the missing string population for the three no-po modules; burn the 110 counterpart-pending ui-copy keys to 0 | P04-M06 T09 record: "110 keys honestly marked counterpart-pending" | 3 new `.po` files; updated generated copy | `python -m i18n.check --completeness 100` green |
| R02-M03-T02 | Run the translation completeness check against the **installed** runtime (loaded terms, not just files) for all 66 modules | G1-05: "100% Bengali translation (FF-25 blocking)" | Runtime coverage report | Report 100% |
| R02-M03-T03 | Execute the Bengali rendering reference-image comparison at runtime (doctor check 10's pixel half) across job card, Mushak preview and payslip templates | Doctor check 10: "static validation now, pixel comparison at runtime" | Reference-image evidence | Check 10 fully PASS |
| R02-M03-T04 | Run the layout-under-text-expansion Playwright suite (bn vs en) against the live six workspaces; fix truncation findings | tooling/a11y exists with bn/en comparison; runtime-gated | A11y/expansion report | 0 serious/critical |

---

## Milestone R02-M04 — Execute the Wave-1 migration loads

**Evidence:** audit §2 Phase 4 migration row 🟡 — "MIG standards + 4 per-source ETL **specifications** … the loads themselves are ahead"; G1-03 CONDITION "Customer/device data migrated with reconciliation signed".

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R02-M04-T01 | Implement the four ETL loaders from the existing specs (customer with M64 golden-rule dedup, device with serial/IMEI gate, branch ×6 OU-mapped, employee with JML events) against the migration-staging profile | `migrations/REHEARSAL.md` + `migration-etl-specs.md` exist; no loader code | 4 loaders under `migrations/` | Each runs on staging with control totals |
| R02-M04-T02 | Enforce MIG-02 control totals **before** load acceptance (count, value, checksum per source) via `tooling/scripts/mig-totals.py` | MIG-02 binding standard; tool exists unexercised | Control-total manifests | `mig-totals.py` green per load |
| R02-M04-T03 | Enforce MIG-06 residency routing: migrated NID/TIN values pass through `fix_residency` to the stub Z4 — assert no raw value lands in the regional store | §0.7 "the compliance breach the architecture exists to prevent, at scale, on day one" | Routing assertions in loaders | FF-09 scan over loaded DB |
| R02-M04-T04 | Rehearse MG-007 rollback for each of the four loads and obtain MG-004 business reconciliation sign-off (this is G1-03's evidence) | G1-03 CONDITION; MIG-08 | Signed reconciliation | G1 verifier item PASS |
| R02-M04-T05 | Load the **48 `MD-*` master-data content set** (catalogue, BD address/zone reference, finance/statutory templates) — B-14 records it as unbudgeted and "Odoo cannot be configured without them"; escalate the content-approval dependency rather than working around it | B-14; P03-M06-T06/P04-M08-T06; audit content-readiness row | Loaded + approved MD set | Content register rows approved |

---

## Milestone R02-M05 — G1 evidence pack and gate re-run

**Evidence:** G1 currently 2 PASS · 10 CONDITION; G1a-7 (coverage) addressed by R01-M04 baseline; G1a-9/G1-12 (capacity) unreported.

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R02-M05-T01 | Demonstrate SLA clocks and escalation firing including breach/near-breach paths at runtime (G1-04) | G1-04 CONDITION; `fix.sla.policy` exists unproven at runtime | SLA demo evidence | Verifier item PASS |
| R02-M05-T02 | Run the T−6 standing-criteria check and the branch-staff 3-minute walk-in timing demonstration (G1-02, G1-08) — by branch staff, not developers | G1-02 "demonstrated by branch staff, not by developers" | Timed demonstration record | Signed timing sheet |
| R02-M05-T03 | Run the security scan pass (SAST + dependency + container) to zero high/critical on the Wave-1 estate (G1-06 first half; full pen test deferred to R09) | G1-06 CONDITION | Security report | 0 high/critical |
| R02-M05-T04 | Produce the honest capacity report: measured velocity vs the ~239 PW Wave-1 demand; state the 5.87× position as a measurement | G1a-9/G1-12; audit P-3 | Capacity report to Steering | Report filed |
| R02-M05-T05 | Re-run `verify-gate-g1a.ps1` and `verify-gate-g1.ps1`: target 0 FAIL with every runtime CONDITION discharged; remaining production-scale items converted to named R-phase conditions | Gate discipline | G1a/G1 evidence JSON | 2 gate records filed |

---

**Sequence:** M01 → M02 → M03 → M04 → M05 (M02/M03 parallel after M01; M05 requires all).
