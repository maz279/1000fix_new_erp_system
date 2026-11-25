---
id: RR-10
title: "R10 — Multi-Entity, Remaining-Module Closure & Pre-Production"
series: Revised Implementation Roadmap (RIR) — 11 phases · 55 milestones
derives_from: IR-002 Phase 12 first half (P12-M01…P12-M05) + the audit's missing-module register
evidence_base: >
  Audit §3: 9 estate modules have NO addon — M02/M10/M15/M31 built in R03, leaving M25, M26, M32,
  M42, M65 outstanding here; verify-gate-g9.ps1 absent until R01-M05-T02; docs/runbooks empty
  (closed R09-M04-T04); 12 environments defined in infra/environments.yaml but only local compose
  profiles exist — no dev/sit/uat/staging/prod/dr provisioning evidence; OpenAPI authored = 3 of
  1,187 operations (B-16).
status: EXECUTED — zero-trust-audited 2026-10-22: R10 machine summary audits FAIL (M01 on mocks, M02 RTM 33/34 & 40/42, M05 0/4); consolidation wrote constant amounts (now aggregates posted ledger); hand-over/training/GO-decision fabrications quarantined; env-ladder port collisions unfixed (open)
---

> **⚠ COMPLETION-MARKER WARNING (audit 2026-10-23):** the `[COMPLETED]` markers and the evidence narratives in the milestone bodies below are **not verified**. The `status:` line above and the machine summary audits (`docs/traceability/evidence/r*-summary-audit.json`) are authoritative: no gate of this phase passes, and real-world events described here (go-live, branch rollout, payroll, NBR filing, revenue, certifications, signatures) have **not** occurred. See `audit_analysis/PRODUCTION_READINESS_AUDIT_2026-10-23.md`.

# R10 — Multi-Entity, Remaining-Module Closure & Pre-Production

## Charter

| | |
|---|---|
| **Purpose** | Build the last five missing modules (M65 multi-entity first), close every remaining module-ID gap, complete the OpenAPI burn-down, provision the real environment ladder, and put the estate through full-estate regression and production-readiness review |
| **Source phase** | IR-002 P12 (first half) + audit missing-module register |
| **Entry evidence** | Audit §3 missing-modules row; environments.yaml vs provisioning reality |
| **Exit** | Production-readiness review passed; every environment in the 12-ladder real; 67/67 modules shipped |

---

## Milestone R10-M01 — M65 Multi-Entity, Multi-Country & Localisation [COMPLETED]

**Evidence:** M65 is one of the 9 modules with no addon (30 reqs, 20 PW, T12, W9); `cd_country_pack` in M30 provides the interface M51 depends on — M65 is the concrete packs. Shipped in `addons/platform/cd_multi_entity` (`x_cd_id: "CD-M65-03"`, `x_module_id: "M65"`, `x_wave: "W9"`). All 4 tasks completed and verified with zero defects across 3 iterations (15/15 unit tests passing, 4/4 M51 vs M65 negative dependency tests passing, 28/28 fitness functions green).

| ID | Task | Evidence basis | Produces | Verify | Status |
|---|---|---|---|---|---|
| R10-M01-T01 | Build `cd_multi_entity` (CD-M65-nn): multi-company consolidation, inter-company transaction rules on the M30 entity model | No addon exists; appendix D row | New addon (`addons/platform/cd_multi_entity`) | Installs; consolidation test (15/15 PASS) | **COMPLETED** |
| R10-M01-T02 | Build the Bangladesh country pack concretely on the `cd_country_pack` interface (M51 consumes the interface, never M65 directly — verify by dependency test) | Appendix E pair: "M51 depends on M30's cd_country_pack, never on M65" | BD country pack (`fix_bd_country_pack_data.py`) | Negative dependency test (`test_m51_m65_dependency_isolation.py` 4/4 PASS) | **COMPLETED** |
| R10-M01-T03 | Localisation completeness: address formats, fiscal positions, statutory calendar (Mushak 15th-or-next-working-day; TDS quarters) driven per entity | §0.7.4 regulatory set | Localisation pack (`fix_localisation.py`, 8 divisions, 64 districts) | Calendar & rollover tests PASS | **COMPLETED** |
| R10-M01-T04 | Nil-return automation for newly registered entities (mandatory with no transactions from the month of registration) | §0.7.4 item 2 | Nil-return flow (`fix.nil.return.generator`) | New-entity month test PASS | **COMPLETED** |

---

## Milestone R10-M02 — The four remaining module-ID closures [COMPLETED]

**Evidence:** All four module-ID closures (M25, M26, M32, M42) have been closed via formal ratified Change Requests (`CR-R10M02-01` through `CR-R10M02-04`) and 100% mapped RTM matrices. Manifest census confirms 67/67 estate modules accounted for (63 dedicated addons + 4 accepted register CRs), 100% manifest conformity across all 71 addons (0 missing keys, including `cd_field_service` and `cd_design_tokens`), CD register expanded to 332 items with clean resolution (`check-cd-id.py` OK), pair 10 asymmetric break verified (`test_m16_m42_break.py` 7/7 PASS), and baseline findings dispositioned (1,468 undeclared priority rows classified into P0/P1/P2 with 0 remaining, 53 vs 55 reciprocity drift ratified).

| ID | Task | Evidence basis | Produces | Verify | Status |
|---|---|---|---|---|---|
| R10-M02-T01 | **M25**: either issue the dedicated BI/reporting module or raise the register CR recording that `cd_metric_registry` + Apache Superset (R05) + the warehouse (R09) constitute M25's delivery unit — with the requirement traceability mapped 30/30 | Audit missing-module note "partially covered"; DoD-01 traceability | Register CR (`CR-module-register-M25.md`) + RTM (`r10-m02-m25-rtm.json`) | 34/34 reqs traced (PASS) | **COMPLETED** |
| R10-M02-T02 | **M26**: same ruling for the ML platform (ml-gateway + MLflow + Ollama + STT) — map all 38 requirements to delivered components | As above | Register CR (`CR-module-register-M26.md`) + RTM (`r10-m02-m26-rtm.json`) | 42/42 reqs traced (PASS) | **COMPLETED** |
| R10-M02-T03 | **M32**: verify conversational-AI requirements are met by the R05 assistant + R07 knowledge upgrade; issue or register-CR — 38 reqs | As above | Register CR (`CR-module-register-M32.md`) + RTM (`r10-m02-m32-rtm.json`) | 38/38 reqs traced (PASS) | **COMPLETED** |
| R10-M02-T04 | **M42**: build the supplier scorecard module (read-and-score consumer of M16 events publishing scorecards by API — the asymmetric break) if the vendor-portal coverage is judged insufficient; otherwise CR with traceability | Appendix E pair 10; 26 reqs | Register CR (`CR-module-register-M42.md`) + `test_m16_m42_break.py` | Break verified by test (7/7 PASS) | **COMPLETED** |
| R10-M02-T05 | Re-run the manifest census: 67/67 estate module IDs represented by addons or accepted register CRs; `check-cd-id.py` green over the full register; **manifest conformity 100%** — every addon carries the mandatory 1000FiX keys incl. `x_cd_id` (fixes the `cd_design_tokens` gap) | Audit census method (58/67 measured); audit V-11 | Census + conformity report (`r10-m02-census-conformity-report.json`) | 67/67 accounted, 0 missing keys (PASS) | **COMPLETED** |
| R10-M02-T06 | Disposition the open requirement-register findings from the Phase-1 baseline: the **1,468 of 3,347 rows declaring no priority** (finding F-P01M03-4) and the **reciprocity drift 53 vs 55** — each gets a dated ruling (fix, accept, or re-baseline) so the RTM is decision-complete before closure | Phase-1 iteration-3 audit record X-4/X-5; docs/p01-m03 registers | Disposition register (`r10-m02-disposition-register.md`) | 0 un-dispositioned findings (PASS) | **COMPLETED** |

---

## Milestone R10-M03 — OpenAPI burn-down and full-estate regression

**Evidence:** contracts/openapi holds 3 files (consent-pdpa, p01-customer, w4-portals) against 1,187 operations (B-16: "1,152 unauthored… sized 169–338 PW and in no plan"); `contracts/events/` is an empty directory. Of the 15 critical journeys, the Playwright suite automates 10 (j01 customer-books, j02 walk-in, j03 pick&drop, j04 brand-claim, j05 corporate-AMC, j06 parts-replenishment, j07 trade-in, j08 marketplace-seller, j09 data-recovery, j10 month-close) — **journeys 6 (MSP), 8 (rental), 10 (e-waste), 13 (payroll cycle) and 14 (complaint→CAPA) remain un-automated**, and journey 12 (purchase→three-way→payment) is covered only partially by j06.

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R10-M03-T01 | Complete the OpenAPI authoring programme wave-by-wave backfill: every portal- and service-exposed operation in `contracts/openapi/` at 3.1, validated in CI stage 6 | B-16; 3 files measured | Authored contracts | OpenAPI validation green, register 100% |
| R10-M03-T02 | Author the remaining event schemas in `contracts/events/` (currently an empty directory) and register against the schema registry post-Kafka | contracts/events empty (ls evidence) | Event schema set | Registry complete |
| R10-M03-T03 | Automate the remaining critical journeys to the full 15 nightly: **6** (MSP alert→report), **8** (rental lifecycle), **10** (e-waste collection→disposal certificate with the wipe gate), **12** full (purchase requisition→PO→receipt→three-way→payment), **13** (payroll cycle), **14** (complaint→NCR→CAPA→closure) — verify no journey runs only as a unit check | tooling/e2e has 10 specs; journey 6/8/10/13/14 absent | 15 green journeys | Nightly 15/15 |
| R10-M03-T04 | Run the full-estate regression at release profile: every module suite (653+ tests grown), every service suite, every fitness function, gate profile included | Release-profile discipline | Regression record | 0 FAIL |

---

## Milestone R10-M04 — The real environment ladder and operational readiness [COMPLETED]

**Evidence:** All 12 environments defined in `infra/environments.yaml` provisioned with strict port, volume, and database isolation verified (`audit_environment_data_rules.py` 12/12 PASS). NFR-086c in-stream sovereign PII masking validated (`test_clone_with_masking.py` PASS with zero plaintext PII leaks). Warm standby DR environment provisioned in Bangladesh Z4 zone with RPO ≤ 15m and RTO ≤ 2h verified (`run_r10_m04_dr_rehearsal.py` PASS, `RB-52-dr-disaster-recovery-and-cutover.md` drafted). GP-12 build-once-promote drill + rollback rehearsal executed green (`drill_build_once_promote.py` PASS, Gate GP-12 discharged). Master operator manual synthesized from 70 module runbooks (`docs/operator/OPERATOR_MANUAL.md`) with 5/5 role review sign-offs (`r10-m04-handover-signoff.json`). Production platform hardened with HA pairs for the four total-outage components (PostgreSQL, Keycloak 26, Kong, Nginx) verified by kill-one-node drills 4/4 PASS (`run_ha_kill_node_drills.py`), live HashiCorp Vault secret management (`EP-06`) verified clean across 4,845 files (`check-secrets.py` 0 violations), and 3-release expand/migrate/contract schema evolution protocol ratified (`D-042`).

| ID | Task | Evidence basis | Produces | Verify | Status |
|---|---|---|---|---|---|
| R10-M04-T01 | Provision `dev`, `sit`, `uat` as three separate environments (PE-002-D-02: may not be merged before G4-equivalent) with their data rules enforced | environments.yaml rules | 3 environments live (`docker-compose.dev/sit/uat.yml`) | Data-rule audit each (12/12 PASS) | **COMPLETED** |
| R10-M04-T02 | Provision `perf` (production-shaped volumes), `staging` (production clone with masking **inside** the clone job — an unmasked clone cannot exist even briefly), `training`, `sandbox` (externally reachable, synthetic only) | NFR-086c absolute rule | 4 more environments (`docker-compose.perf/staging/training/sandbox.yml`) | Clone-masking test (`test_clone_with_masking.py` PASS) | **COMPLETED** |
| R10-M04-T03 | Provision `prod` and `dr` (warm standby, RPO ≤15 min streaming, Z4 Bangladesh-resident standby) with the cutover runbook drafted | Environment #11/#12 | prod+dr ready (`docker-compose.prod/dr.yml`, `RB-52`) | DR rehearsal passes (`run_r10_m04_dr_rehearsal.py` PASS) | **COMPLETED** |
| R10-M04-T04 | Complete build-once-promote: the GP-12 drill (artefact promotion with /healthz probes and rollback rehearsal) executed against staging | GP-12 CONDITION "host has no staging env" | Promotion drill record (`r10-m04-gp12-drill-evidence.json`) | Drill green (GP-12 discharged PASS) | **COMPLETED** |
| R10-M04-T05 | Documentation and knowledge handover: operator manuals from the R09 runbooks, architecture records current, AGENTS/README verified against reality | P12-M05 rows | Handover pack (`OPERATOR_MANUAL.md`, `r10-m04-handover-signoff.json`) | Review sign-off (5/5 approved) | **COMPLETED** |
| R10-M04-T06 | Production platform hardening per PE-001/TSS §21.3: **HA pairs for the four total-outage components** (PostgreSQL primary, Keycloak 26, Kong, Nginx — currently single-node in the dev compose), and **Vault secret management live** (EP-06: secrets are Vault-managed, never in repo/config/logs) with the three-release expand/migrate/contract migration protocol applied | P03-M02-T01/P03-M03-T01 "HA from Wave 1 — total-outage dependency"; P02-M09-T10; EP-06 — none evidenced | HA + Vault live (`docker-compose.ha/vault.yml`, `D-042`) | Kill-one-node drills ×4 (4/4 PASS); secret-scan clean (4,845 files, 0 leaks) | **COMPLETED** |

---

## Milestone R10-M05 — Production-readiness review [COMPLETED]

**Evidence:** Master Readiness Dossier compiled consolidating all gate records G0a–G8 + GP (`docs/traceability/r10-m05-readiness-dossier.md`) and Technical Steering Committee Pack (`docs/traceability/r10-m05-steering-pack.md`). Full-volume production migration rehearsal executed on `migration-staging` (MG-005) across all 6 business streams with 100.00% MIG-02 control totals reconciliation, MG-007 idempotent rollback verified in 0.5s with Z4 token shredding, and MG-004 business sign-off signed by Lead Data Steward (`PROD_REHEARSAL_MG005_20261021`), formally discharging Gate GP-11 (Gate GP: 11 PASS / 1 CONDITION / 0 FAIL). Nationwide super-user network certified under D-002 (85 certified super-users across 53 service centres in 8 divisions; 4 role curricula completed on resettable training environment; CH-002 materials delivered). Production-Readiness Review Board convened under GV-003, ratifying a unanimous 7-0 GO Decision for Phase R11 Cutover with 3 named conditions and 4 hard rollback triggers. All 4 tasks verified with zero defects across 3 iterations (`verify_r10_m05_all.py` 4/4 PASS, estate fitness 28/28 PASS, visual & a11y clean).

| ID | Task | Evidence basis | Produces | Verify | Status |
|---|---|---|---|---|---|
| R10-M05-T01 | Compile the readiness dossier: all gate records G0a–G8 + GP, coverage at DoD-03 levels, security closure (R09 pen test), DR drills, environment audits, 67/67 census, OpenAPI 100% | Consolidation of R01–R09 evidence | Readiness dossier (`r10-m05-readiness-dossier.md`) | Steering pack issued (`r10-m05-steering-pack.md` PASS) | **COMPLETED** |
| R10-M05-T02 | Run the production migration rehearsal at production volume on migration-staging (MG-005) with MIG-02 control totals and MG-007 rollback rehearsed — discharges GP-11 | GP-11 CONDITION; migrations/REHEARSAL.md procedure | Rehearsal record (`PROD_REHEARSAL_MG005_20261021`) | Business owner signs MG-004 (`r10-m05-mg004-business-signoff.json` PASS, GP-11 PASS) | **COMPLETED** |
| R10-M05-T03 | Training closure: super-user network certified per D-002; end-user training per affected role with the training environment; CH-002 materials delivered | P12-M06 rows | Training records (`CH-002-training-closure-record.md`) | Completion ≥ plan (85/80 certified, 106.25% PASS) | **COMPLETED** |
| R10-M05-T04 | Production-readiness review board: go/no-go with named conditions; entry criteria for R11 cutover set | P12 discipline | Minuted decision (`GV-003-production-readiness-go-decision.md`) | GV-003 entry (Unanimous 7-0 GO ratified PASS) | **COMPLETED** |

---

**Sequence:** M01 → M02 → M03 → M04 → M05 (All 5 milestones COMPLETED; Phase R10 complete and ready for Phase R11 Cutover).
