# IR-002 IMPLEMENTATION STATUS AUDIT REPORT

> **Audit Date:** 2026-10-15 (first pass) · **2026-10-15 (second pass — self-audit and correction, §8)**
> **Auditor:** Independent full-stack implementation audit (codebase research + live verification execution)
> **Subject:** `IR-002_Final_Production_Implementation_Roadmap.md` (v2.0.1, 4,371 lines — 12 Phases · 120 Milestones · 1,200 Tasks) versus the actual build estate at `1000fix_new_erp_system/1000_fix_codebase/`
> **Verdict:** **The foundation layers (Phases 1–4) are genuinely built and verified green-on-artefacts. Phases 5–11 exist as breadth-first scaffolds of varying depth. Phase 5 is materially incomplete, Phase 12 has not started, and every gate to date passes only as "GREEN-on-artefacts" — 49 CONDITION items across the 11 executed gate verifiers await runtime, human, and production-scale evidence, plus 5 OPEN external items. Two external blockers keep the programme's own Wave 0a gate at HOLD.**

---

## 1. Executive summary

### 1.1 What was audited

| Input | Method |
|---|---|
| `IR-002_Final_Production_Implementation_Roadmap.md` (456 KB) | **Read end-to-end in the second pass** (first pass covered ~75% of lines; the missing Phase 6–11 task tables were read in full on correction): Part 0 (governance, 12 blockers, AS/DoD/EP rules), all 12 phase charters, all 120 milestone task tables, Appendices D–I |
| `roadmap/AUDIT_REPORT.md` (prior document audit) | **All 28 numbered findings (F-01…F-28) and all 9 follow-up findings (FU-01…FU-09) verified against the current roadmap text in the second pass** (first pass verified 8 of 28) — see §7 |
| `1000_fix_codebase/` (git repo, 98 commits, 15,995 tracked files) | Full structural sweep: 66 Odoo addons, 17 services, 8+4 web/mobile apps, 3 shared libs, vendored Odoo + 19 OCA repos, CI, infra, tooling, docs/traceability; git forensics with exact commit timestamps |
| Live verification | Executed on this machine, 2026-10-15: Python compile of every `.py`; the fitness suite; 653 addon tests; 202 service tests; 44 payroll/STT/residency tests; `test-smoke.py` (15/15); **all 11 gate verifiers re-run live** |

### 1.2 Headline results (all re-executed 2026-10-15, not quoted from records)

| Verification | Result |
|---|---|
| Python compile — addons + services + libs + tooling | **0 errors** |
| Manifest validation — 66 `__manifest__.py` | **0 parse errors**; 58 of the 67 estate M-modules covered + 4 portal-surface addons (P01/P03/P04/P05) + 1 design-system addon; 1 missing `x_cd_id` (`cd_design_tokens`, deliberately `DSY-01`) |
| Fitness suite (`tooling/fitness/run.py`) | **20 PASS · 7 SKIP · 0 FAIL** (27 checks; evidence JSON `fitness-20261015T134539Z.json`) |
| Addon test estate (`pytest addons`) | **653 passed** (2.9 s) |
| Service test estate (`pytest services`) | **202 passed** |
| Payroll / STT / residency-stub suites | **44 passed** |
| Smoke test (`test-smoke.py`) | **15/15 PASS** — including state-machine transitions, outbox event emission, ACL denial, seed idempotency |
| E2E journeys (Playwright, evidence dated 2026-10-13) | **10/10 expected · 0 flaky · 0 skipped** |
| Gate verifiers (11 files re-run live, this audit) | G0a **10P/6C/2 OPEN → HOLD** · G0b **8P/3 OPEN** · G1a **4P/6C** · G1 **2P/10C** · G3 **5P/7C** · G4 **6P/8C** · G5 **9P/1C** · G6 **7P/3C** · G7 **7P/3C** · G8 **6P/2C** · GP (portal, non-roadmap) **9P/3C** — **totals: 73 PASS · 49 CONDITION · 0 FAIL · 5 OPEN over 127 checks. Missing verifiers: G2 and G9** |
| Bengali localisation | 19 shipped `bn_BD.po` files, all **100% translated**; FF-25 enforces this in the fitness suite |

### 1.3 The one-paragraph truth

The codebase is a **credible, disciplined foundation estate**: the monorepo matches the roadmap's mandated tree almost exactly; the Phase 1–2 governance/tooling/pipeline apparatus is unusually complete (executable gate verifiers, a 331-item CD register, a requirements baseline of 3,347 rows, a regenerated dependency graph); the Phase 3–4 kernel (party master, event outbox, RBAC with 53 roles and 61 SoD controls, residency enforcement, entity config, service orders with a 14-state machine) is real, tested code. But **the entire Phase 1–11 module estate was produced between 2026-10-01 and 2026-10-04** — Phases 3–7 landed inside the initial git import (2026-10-03 16:38) and Phases 8–11 followed within roughly 21 hours (Oct 3 23:31 → Oct 4 19:34) — and the 55 domain modules built that way average ~5 Python files each (~325 LOC/module): conformant skeletons, not the 3,389-requirement functional build. Nine estate modules (including two P0 modules, **M02 Field Service and M15 Inventory**) have **no addon at all**, 18 of 19 vendored OCA repositories are **never referenced by any custom module's `depends`**, three standalone services are **empty directories**, and the programme's own G0a gate remains at **HOLD on two external blockers** (Board charter minutes, the DEP-31 legal opinion). Nothing has been demonstrated at runtime scale: no coverage measurement, no penetration test, no performance run at 1.5× peak, no DR drill, no migration rehearsal with real data.

---

## 2. Phase-by-phase implementation map

Legend: **A%** = artefact completeness (files/structures the roadmap's `Produces` column demands), **D** = functional depth judgement, ✅ implemented · 🟡 partial · ❌ absent.

### Phase 1 — Programme Mobilisation & Blocking-Decision Closure (W0a, Gate G0a) — **A ~95% codebase-side · external closure outstanding**

| Milestone | Status | Evidence |
|---|---|---|
| P01-M01 Charter & governance | 🟡 | Governance artefacts prepared; the E1 items (Board minute, Steering/ARB/DP Forum constitution, **CDO appointment — a statutory PDPA role no source document appoints**) are external and open |
| P01-M02 Four technology decisions | ✅ | 9 ADRs on disk (`docs/decisions/`): D-013 prepared (3-option table), D-025/026/027 accepted, D-028/029/030 recorded + completed, D-031 proposed; DEP-31 engagement letter drafted; version-currency ritual **42 OK · 1 WARN · 0 FAIL** |
| P01-M03 Requirements baseline & fit-gap | ✅ | Executable scan engine — **14 PASS · 3 findings · 0 FAIL**; fit-gap register 3,347 rows; `CR-01` denominator reproduced exactly (3,347 + 42 = 3,389); M66/M67 register correction CR raised |
| P01-M04 Architecture baseline | ✅ | Dependency-graph extractor regenerated: 67 nodes / 447 edges / 18 mutual / 32 violations — exact to `AR-006`; wave-violation register with dispositions (MOVE 9 matches AR-006) |
| P01-M05 Identifier discipline | ✅ | `tooling/cd-register.yaml` — **331 items / 1,850 PW / crosswalk 331**; `check-cd-id.py` live: all CD references resolve |
| P01-M06 Data architecture | ✅ | 1,335-entity baseline; Z4/ORM-residency/clone-mask/erasure-saga rulings on disk |
| P01-M07 Legacy profiling | 🟡 | 48-source register + migration rulings issued; the ~4-week profiling execution itself is open (B-06) |
| P01-M08 Commercial closure | 🟡 | SoW F-08 resolution prepared citing the measured baseline; **signature is external** |
| P01-M09 Team mobilisation | 🟡 | D-002 super-user decision record + squad charters; named individuals external |
| P01-M10 Gate G0a | ⚠️ | Executable verifier: **10 PASS · 6 CONDITION · 2 OPEN · 0 FAIL — verdict `RED-EXTERNAL-BLOCKERS-OPEN` (HOLD)** on B-01 and B-02 |

**Remaining:** B-01 Board minutes; **B-02 DEP-31 legal opinion → D-013 (6–10 week lead, the programme's longest external dependency — start it Day 1)**; SoW amendment signature; B-06 profiling execution; CDO appointment.

### Phase 2 — Engineering Foundation (W0b, Gate G0b) — **A ~95% · 🟢 strongest infrastructure phase**

| Milestone | Status | Evidence |
|---|---|---|
| P02-M01 Workstation | ✅ | Native Windows baseline (deviation `D-WS-001` formally recorded); recorded run 8 PASS · 2 WARN; BitLocker off is the one RED item |
| P02-M02 Toolchains | ✅ | `versions.lock` pins (Node 22, Python 3.12.10, Flutter 3.44, Go) with dated provenance |
| P02-M03 Repository init | ✅ | Monorepo tree matches the roadmap's mandated layout **exactly** (`addons/platform` + `addons/domain` ×10 categories, `services/`, `apps/`, `libs/{py,ts,dart}`, `contracts/`, `db/`, `infra/`, `tooling/`, `docs/`, `.github/`) |
| P02-M04 Vendoring | ✅ | Odoo submodule pinned `6436101` on 19.0; **19 OCA subtrees** committed with pinned squashed commits; `FORKS.yaml`; `versions.lock` pins. (Roadmap says 18 — `l10n-bangladesh` was dropped as a phantom repo, honestly recorded) |
| P02-M05 Supporting stack | ✅ | Compose with profiles (core/auth/integration/field/observability/full + intelligence/msp/asset-ml/migration-staging); images digest-pinned **except 8 placeholder occurrences** (§3); every port loopback-only (DE-04 verified by scan); Mailpit; synthetic residency stub at 8100 |
| P02-M06 Odoo runtime | ✅ | `make bootstrap/odoo-conf` (generated, REPO-15)/`db-create`/`run`/`seed` — deterministic, state-complete (DE-16), Bengali-first (DE-17, verified in seed source) seed: 5 branches, 25 users, 200 customers, 500 devices, 300 orders, 400 products, 60 SLAs |
| P02-M07 VS Code | ✅ | `.vscode/{extensions,launch,settings}.json` committed per spec |
| P02-M08 Quality gates | 🟡 | `.pre-commit-config.yaml`, gitleaks, licence gate (D-030) live; fitness runner **20 PASS · 7 SKIP · 0 FAIL** — the 7 SKIPs are mis-wired script paths (see V-3) |
| P02-M09 CI/CD | 🟡 | `ci.yml` implements 17 stages / 5 profiles / build-once / PS-01 fail-closed / ephemeral PG17; 12-environment ladder in `infra/environments.yaml`. **Never executed on a real runner** (no run evidence; repo has no remote CI history) |
| P02-M10 Doctor & G0b | ✅ | `doctor.ps1` — all 14 checks, Windows-native twin (D-WS-001); `test-smoke` 15/15; G0b verifier **8 PASS · 3 OPEN · 0 FAIL** |

**Remaining:** 3 OPEN G0b items; resolve the 7 fitness SKIPs; **8 placeholder digests** (1 `novu` in core compose, 1 `clickhouse` in intelligence, 3 in asset-ml incl. the Kafka brokers, 3 in msp); push the repo and get one real CI run; BitLocker.

### Phase 3 — Platform Bootstrap & Shared Kernel (W1a, G1a) — **A ~90% · real kernel code**

All eight kernel modules exist with conformant manifests (1000FiX keys, LGPL-3, layer order) and tests:

| Milestone | Status | Evidence |
|---|---|---|
| M29 Identity (`cd_rbac_ext`) | ✅ | `fix.role` — **53 reconciled R-nn roles**; isolation tiers T0–T5 as record rules; **61 SoD controls** (SP-006 register of record) with conflict actions; field-level permission engine; **`residency.mixin` — write-time ORM enforcement of NFR-086a** |
| M28 Integration (`cd_event_outbox` + `libs/py/fix_events`) | ✅ | Transactional outbox `emit()` same-transaction (AS-08), `drain_pending()`, idempotent UUID event IDs; `fix_events` the sole event client (FF-28) with idempotent consume + replay-from-timestamp |
| M30 Admin (`cd_entity_config`) | ✅ | `fix.entity`/`fix.branch`/`fix.cost.center` on OCA `operating_unit`; zone/geofence; working calendar; feature-flag service with `@flag_enabled`; BD address hierarchy; country pack; notification config — **the only custom module that consumes an OCA repo** |
| M33 Party (`cd_party_master`) | ✅ | The multi-role kernel rule enforced by constraint (`fix.party.role` — one `res.partner`, many roles); hierarchy; identity documents residency-routed (checksum from Z4 value, never in payloads); PDPA consent registry with proof requirement; dedup rules |
| M37 Catalogue (`cd_catalogue`) | ✅ | Catalogue item, service kits, rental SKUs, refurb grades, brand/model masters |
| M64-core + M24-core | ✅ | `cd_mdm_core` (change request + golden-record rules), `cd_document_core` (`fix.document` on `ir.attachment` + retention class) |
| M21-core (`cd_employee_core`) | ✅ | Employee master + JML events; M21↔M29 interface break documented in the T0 SDD |
| Residency/Z4 | ✅ | `libs/py/fix_residency` SSRF-hardened, sole Z4 client; `check_ff09_residency.py` **0 bypass paths — FF-09 blocking PASS live** |
| Gate G1a | ⚠️ | **4 PASS · 6 CONDITION · 0 FAIL** (conditions need Odoo runtime; the later 2026-10-03 commit "all 32 modules install live" partially discharges the clean-install condition, but that is not re-recorded against G1a) |

### Phase 4 — Service Core, Front Desk & Admin Portal (W1b, G1) — **A ~85%**

| Milestone | Status | Evidence |
|---|---|---|
| M17 Device registry | ✅ | Serial/IMEI uniqueness, warranty status, ownership transfer with history, attachments via kernel API |
| M04 Front desk | ✅ | Token queue (branch-daily sequence), walk-in intake with the 3-minute timing fields, cash shift with AS-10 monetary reconciliation |
| M01 Service order | ✅ | **AS-06 single-source 14-state machine** (`VALID_TRANSITIONS`), SLA clocks with pause/resume, idempotency key, legacy reference (MIG-03), estimates with 15% VAT, QC checklists, job-card QWeb report — 718 LOC, 653-test suite exercises it end to end |
| M07 CRM W1 slice | ✅ | `crm.lead` extension, party-kernel link, convert-to-service-order |
| Notification platform | ✅ | `services/notification-dispatcher`: NT-001 event→channel matrix, consent-aware policy (NT-002/003, quiet hours, frequency caps), INT-010/012/013 adapters SSRF-guarded and dry-run by default, retry/fallback/dead-letter, all **26 NT-* templates as a machine registry in Bengali and English**; 37 unit tests green |
| P03 Admin portal | ✅+ | Shell + 6 W1 workspaces role-gated via M29 groups; later **deepened beyond the W1 slice** in porting phase PP2 (Tell-ME, Report Center, dispatch console, BPF+FactBox, grid conformance, tab rail) |
| Design system | ✅ | DTCG token generator → SCSS/CSS/TS artefacts (no runtime authors a value); 5 W1 components; CFM-01…05 conformance suite — CFM-03 contrast check caught and fixed a 3.76:1 red |
| Bengali base | ✅ | Translation workflow + FF-25 enforcing 100%; BN-007 formatting; `libs/ts/i18n`; Bengali QWeb report path with committed conjunct-shaping reference PNG |
| Wave-1 migration | 🟡 | MIG-01…08 standards + 4 per-source ETL **specifications** (customer/device/branch/employee) — the loads themselves are ahead |
| Gate G1 | ⚠️ | **2 PASS · 10 CONDITION · 0 FAIL** — conditions honestly name the runtime demo, pen test, T−6 entry check, 3-minute intake by branch staff, business reconciliation sign-off |

### Phase 5 — Field Operations, Offline Engine & Inventory (W2, G2) — **A ~30% · ❌ the critical gap**

This is the audit's single most important finding. **There is no Phase 5 traceability record, no Phase 5 commit, and no G2 gate verifier.** Phase 5's portal deliverables were partially absorbed by the later porting programme (PP4 offline engine, PP5 customer portal), but the Wave-2 module build itself never ran.

| Milestone | Required | Actual |
|---|---|---|
| M15 Inventory | 48 reqs, P0 | ❌ **No addon.** Odoo `stock` and the 3 vendored OCA stock-logistics repos are depended on by nothing |
| M31 Workshop | 58 reqs | ❌ No addon (work orders exist inside `cd_service_order`, which is the W1 slice — the W2 workshop capability is not built) |
| M02 Field Service & Dispatch | 74 reqs, **P0, 40 PW** | 🟡 A dispatch-console **JS surface** exists in `cd_p03_portal`; `fix.work.order` carries technician assignment — but **no FSM module**, and the OCA `field-service` repo (33 modules) is vendored and unconsumed |
| M10 Loyalty | 44 reqs | ❌ No addon |
| Geospatial platform | TimescaleDB/Traccar/OSRM/VROOM | 🟡 Compose `field` profile defines all four services — no integration code |
| Dispatch scoring service | `services/dispatch-scoring` | ❌ **Empty directory** |
| Telemetry collector | Go service | ❌ **Empty directory** |
| Offline engine (ADR-024) | The programme's hardest requirement | 🟡 `libs/dart/fix_offline` — a well-shaped 758-LOC skeleton (command journal, sync engine, idempotency ledger, conflict disclosure, evidence channel) but **no SQLCipher encryption, no server sync endpoint, no L12 test suite** |
| P02 Technician app | Flutter | 🟡 **1 Dart file + pubspec** per app (4 apps) — shells consuming `fix_ui`/`fix_offline` |
| P01 Customer portal | Next.js | ✅ `apps/web/customer` — Next.js **16.3.8** (D-026 honoured), 14 TSX, booking/consent/devices/estimates/tracking/welcome routes, PWA landing — built later in porting phase PP5 with live-fire 45/45 |
| Gate G2 | 10 criteria | ❌ **`verify-gate-g2.ps1` does not exist** — one of only two missing gate verifiers (with G9) |

### Phase 6 — Money, Movement & Documents (W3, G3) — **A ~65% · scaffold-to-mid depth**

✅ Modules: `cd_gl_ext` (M19, 214 LOC), `cd_billing_engine` (M20), `cd_ap_ext` (M52), `cd_cash_position` (M50), **`cd_tax_engine_bd` (M51 — the deepest finance module at 933 LOC: VAT determination per the AR-006 worked example, Mushak 6.3 issuance, event-driven Mushak register, 9.1 return logic with holiday rollover and nil-return rules)**, `cd_rate_card`/`cd_quotation` (M11/M36), `cd_consignment`/`cd_requisition`/`cd_wms_structure` (M03/M16/M41 slices), `cd_esignature` (M24 ext).
✅ Services: payment-connectors (bKash/Nagad/SSLCOMMERZ), pricing-engine, reconciliation, document-generation, OCR — all with tests.
🟡 Portals: `cd_vendor_portal` (P05, with EA-05 record rules and the three-way-match invoice surface), rider app (P09) skeleton.
⚠️ Gate G3: **5 PASS · 7 CONDITION · 0 FAIL.** The four vendored OCA finance repos (mis-builder, account-financial-*, reporting-engine) are unconsumed; three-way match enforcement, BEFTN, gateway certification, NBR e-VAT (INT-038) and the production-clone migration dry run are ahead. Roadmap specifics confirmed unimplemented: auto-invoice within 5 s of job close (NFR-040), ≥90% payment auto-matching, month-end close in 5 days.

### Phase 7 — Agreements, Billing, Contact Centre & Analytics (W4, G4) — **A ~65%**

✅ `cd_contract_core` (M08), `cd_warranty_claims` (M09, with brand API), `cd_subscription` (M39), `cd_settlement_ext` (M53 W4), `cd_contact_centre` (M27), `cd_cx_feedback` (M34), `cd_metric_registry` (M62 — also carries the KPI/instrumentation surface M25 consumes), `cd_corporate_portal` (P04 — deepened in PP3 to a 10-TSX vertical slice with live-verified endpoints), agent-console (P10), brand portal (P08), analytics (P06 — 3 static TSX, Apache Superset not wired), consent OpenAPI contract, DSR orchestrator service (erasure-saga shape present).
⚠️ Gate G4 (the **v1.0 tranche boundary**): **6 PASS · 8 CONDITION · 0 FAIL.** PDPA consent infrastructure is live, but the ~13 May 2027 enforcement readiness condition, penetration test, AI-assistant 40% resolution, and Superset wiring for P06 remain.

### Phase 8 — People, Payroll, Quality & Managed Services (W5, G5) — **A ~75% · best gate result**

✅ `cd_hr_core` (M21 full), `cd_attendance` (M55), **`cd_payroll_bd` (M56 — Bangladesh Labour (Amendment) Act 2026 rates: 30/45-day gratuity bands, provident fund)**, `cd_performance` (M57, incl. incentive engine), `cd_competency` (M22 — the certification register that closes the M02→M22 stubs at model level), `cd_qms_process` (M23), `cd_msp_contract` (M05), `cd_equipment_register`/`cd_vehicle_ext`/`cd_fixed_asset_ext` (M45/M46/M49), auditor app (P11) skeleton, payroll-engine service.
⚠️ Gate G5: **9 PASS · 1 CONDITION · 0 FAIL.** The 100%-coverage-on-calculation-paths requirement (DoD-03) for payroll is **not evidenced** — no coverage measurement exists anywhere in the estate. BEFTN batch-window modelling and Bengali payslip reference images (TR-07) are ahead.

### Phase 9 — New Asset Businesses, Event Bus & AI/ML (W6, G6) — **A ~60%**

✅ `cd_rental_asset` (M13), `cd_tradein` (M14), `cd_data_case` (M06 — the Z4-residency journey-11 module), ml-gateway (M26), `cd_demand_plan`/`cd_import_order`/`cd_fpa` (M43/M44/M54), `cd_talent`/`cd_hse`/`cd_grc`/`cd_knowledge`/`cd_itsm` (M58–M61, M66), customer app (APP-04) skeleton.
⚠️ Gate G6: **7 PASS · 3 CONDITION.** The **Redis Streams → Apache Kafka migration is compose-only** — a 3-node Kafka cluster is defined in `docker-compose.asset-ml.yml` with placeholder digests, and `fix_events` documents the W6+ path in comments, but no Kafka client code exists; the dual-write/consumer-migration/replay programme (P09-M01) has not run. The Odoo major-version upgrade slot (D-025) is unexercised; MLflow/Ollama are placeholder-digested compose entries.

### Phase 10 — Marketplace, Settlement & Partner Channel (W7, G7) — **A ~60%**

✅ `cd_marketplace` (M12) with the M12↔M53 interface break correctly event-driven, `cd_storefront` (M38), `cd_partner` (M40), `cd_dynamic_pricing` (M11 W7), `cd_facility` (M47), `cd_ppm` (M67), seller/partner portals (P07/P12 — 6/5 TSX).
⚠️ Gate G7: **7 PASS · 3 CONDITION.** L6 KYC integration, the seller payout rail (INT-007), external-seller onboarding at 500–2,000 scale and the 51-branch rollout are operational conditions.

### Phase 11 — Intelligence, Warehouse, IoT & ESG (W8, G8) — **A ~60%**

✅ ClickHouse compose profile (placeholder digest); `cd_metric_registry` delivers the M62 data governance set (data catalogue with NFR-086c enforcement, lineage, DQ rules with alerting events); `cd_stream_registry` (M48: IoT device/telemetry/alert + predictive maintenance wired to dispatch); STT service with Bengali WER measurement and a **PDPA legal-basis gate that refuses transcription without a confirmed basis**; `cd_ewaste` (M18: journey 10 with the M06 wipe gate before destruction, ESG metrics).
⚠️ Gate G8: **6 PASS · 2 CONDITION.** The warehouse migration itself (dbt/ClickHouse load), steady-state performance hardening and technical-debt burn-down are ahead; `services/bi-warehouse` is a README + dbt stub only.

### Phase 12 — Expansion, Decommissioning & Closure (W9, G9) — **A 0% · ❌ not started**

No M65 addon (one of the nine missing module IDs), **no G9 verifier** (the second of the two missing gates), no decommissioning plan, no hypercare, no documentation handover, no training closure, no post-implementation review. Expected — the phase is months away in the plan — but it must be named in any honest status statement.

### Cross-phase: the portal porting programme (PP0–PP6, 2026-10-05 → 10-10)

A parallel workstream not in IR-002 that materially advanced the portal surfaces: PP0 foundation reconciliation, PP1 platform scaffolding, PP2 P03 admin portal deepening (R1/OWL), PP3 corporate B2B vertical slice, PP4 Flutter apps + offline-engine hardening, PP5 Next.js batch (**7 portals live**, landing shell, bilingual parity, live-fire 45/45), PP6 data strategy (real/test/forbidden enforced). Its **GP gate: 9 PASS · 3 CONDITION** (OTel round-trip, migration rehearsal, build-once drill — all workstation-blocked, correctly deferred to staging).

---

## 3. Quantified coverage

| Measure | Count | Note |
|---|---|---|
| Estate delivery units | 79 (67 M + 12 P) | Roadmap Appendix D |
| Custom Odoo addons shipped | **66** (11 platform + 55 domain) | **58 of 67 estate M-modules covered (87%)** + 4 portal-surface addons (P01/P03/P04/P05) + 1 design-system addon |
| Estate modules with **no addon** | **9**: M02, M10, M15, M25, M26, M31, M32, M42, M65 | Of which **M02 and M15 are P0**; M25/M26/M32/M42/M65 are partially covered inside other units (metric registry, ml-gateway/stt, contact centre, vendor portal, entity config) |
| Addon Python LOC | **21,400** (avg ~325/module) | Against 1,842 PW of specified build demand — a foundation, not the functional estate |
| Standalone services | **17 directories: 13 with code** (4,269 LOC), 4 empty/skeleton | dispatch-scoring, telemetry-collector, bi-warehouse empty; residency-stub intentionally 1 file |
| Web portals | **8 Next.js 16.3.8 apps** (~50 TSX components; customer portal deepest at 14 TSX) | GP gate confirms "8/8 portals verified live" |
| Mobile apps | 4 Flutter shells (1 Dart file each) + `fix_offline` 758 LOC | The 24-hour offline requirement is not yet met |
| OCA repos vendored / consumed | 19 / **1** (`operating_unit` via `cd_entity_config`) | 18 vendored-but-unconsumed — the L2 "extend, never fork" strategy is not yet exercised |
| OpenAPI contracts | 3 files (consent-pdpa, p01-customer, w4-portals) | Roadmap's B-16: 1,152 of 1,187 operations unauthored — the gap remains almost entirely open |
| Gate verifiers | **10 of the 12 roadmap gates exist (no G2, no G9) + 1 non-roadmap gate (GP) = 11 files** | 0 FAIL · **49 CONDITION · 5 OPEN · 73 PASS over 127 checks** |
| Placeholder image digests | **8 occurrences across 4 compose files** (novu, clickhouse, 3× asset-ml incl. Kafka brokers, 3× msp) | DE-06 requires exact pins; `resolve-digests.ps1` exists but hasn't completed |
| Traceability records | 16 files covering P01–P04, P06–P11 (+ audits) | **P05 record absent** |
| Requirement-level completion | **~15–25% at functional depth** | All 3,389 requirements have baseline rows; the built-out fraction is concentrated in Phases 3–4 |
| Build chronology (git-verified) | Phase 3–7 modules: initial import **2026-10-03 16:38** (built Oct 1–3 pre-git) · Phase 8: Oct 3 23:31 · Phase 9: Oct 4 16:29 · Phase 10: Oct 4 18:07 · Phase 11: Oct 4 19:34 · porting PP0–PP6: Oct 5–10 | **The whole Phase 1–11 estate was produced in 4 days; Phases 8–11 in the final ~21 hours** |

---

## 4. Findings register

### Document-level (the roadmap file itself)

| # | Finding | Severity | Status |
|---|---|:--:|---|
| D-1 | The v2.0.1 remediation of the `update_roadmap.py` corruptions **is confirmed in place — all 28 numbered findings (F-01…F-28) and all 9 follow-up findings (FU-01…FU-09) verified against the current text in this audit's second pass** (see §7 for the verification matrix) | — | ✅ Verified fixed |
| D-2 | `update_roadmap.py` remains in the roadmap folder alongside the source `IR-001` — re-running it would re-corrupt the remediated document | Medium | Open |
| D-3 | Internal count drift: "18 OCA subtrees" versus the 9+4+7=20 named in T03–T05 (19 vendored after the phantom `l10n-bangladesh` drop) | Low | Open (inherited) |
| D-4 | `AUDIT_REPORT.md`'s own header claims "35 findings (12 Critical, 14 High, 9 Medium)" but the register numbers only 28 findings (F-01…F-28) plus 9 follow-ups (FU-01…FU-09) — 12+14+9=35 does not reconcile with 28 numbered rows; the severity arithmetic or the numbering is off inside that document | Low | Open (in the prior audit report, not the roadmap) |

### Codebase-level

| # | Finding | Severity | Detail |
|---|---|:--:|---|
| V-1 | **Phase 5 is materially unbuilt** — no M15/M31/M02/M10 addons, no G2 verifier, empty dispatch-scoring and telemetry services, no traceability record | **Critical** | Wave 2 contains two P0 modules and the programme's hardest technical requirement (24-h offline). It is the plan's critical path and it is the weakest phase |
| V-2 | **18 of 19 OCA repositories vendored but consumed by nothing** | High | The estate's L2 strategy (extend `field-service`, `stock-logistics-*`, `dms`, `payroll`, `hr`, finance repos) is unexercised; custom modules re-implement thin versions where OCA provides battle-tested depth |
| V-3 | **7 fitness checks SKIP with "script missing"** while the FF-03 script actually exists in `tooling/scripts/` — the runner looks in the wrong path | Medium | The fitness suite's honesty is good, but a mis-wired path makes a live check invisible; CI's architecture stage calls the script correctly |
| V-4 | **CI has never executed on a real runner** | High | `ci.yml` is complete (17 stages) but there is no run evidence; pipeline budgets (pre-merge < 20 min) are unmeasured |
| V-5 | **No coverage measurement anywhere** — DoD-03 (≥80%, 100% financial/tax) is unverified; no `.coverage`/`coverage.xml`/`htmlcov` artefacts exist | High | The payroll and VAT paths explicitly require 100% |
| V-6 | **8 container-digest placeholders across 4 compose files** (`novu`, `clickhouse`, 3× asset-ml including the Kafka brokers, 3× msp) | Medium | DE-06 requires exact pins; `resolve-digests.ps1` exists but hasn't been run to completion |
| V-7 | **`docs/runbooks/` is an empty directory** — DoD-11 requires a runbook per module | Medium | 66 modules, zero runbooks |
| V-8 | OpenAPI surface is 3 contracts against 1,187 operations (B-16 gap unchanged) | High | Sized 169–338 PW in the estate's own analysis and still in no sprint plan |
| V-9 | `services/pytest` collection fails without `--import-mode=importlib` (8 packages) — root `pyproject` conftest gap | Low | Tests pass with the flag; the default invocation in CI would fail |
| V-10 | Bengali po coverage is 100% **of extracted strings**; several domain categories carry 1-entry po files (skeleton string sets) | Low | Honest at the artefact level; the string population itself grows with depth |
| V-11 | `cd_design_tokens` manifest lacks `x_cd_id` (carries `DSY-01` instead) | Low | Deliberate but breaks FF-16 uniformity |
| V-12 | One `ceph/daemon:latest@sha256:…` entry — tag+digest form is acceptable but the `:latest` tag is noise against the "no latest" rule | Low | Cosmetic |

### Programme-level

| # | Finding | Severity |
|---|---|:--:|
| P-1 | **G0a remains at HOLD** on B-01 (Board minutes) and B-02 (DEP-31 legal opinion → D-013). The roadmap is explicit: starting Phase 3 with these open is a Steering decision, never a team decision. Phase 3–11 code exists anyway | **Critical** (governance) |
| P-2 | **Every gate passes only "GREEN-on-artefacts"** — 49 CONDITION items plus 5 OPEN across the 11 executed verifiers need runtime execution, human demonstration, production volume, or external evidence. No gate has been passed on evidence in the GV-009 sense | High |
| P-3 | The build sequenced the whole Phase 1–11 estate in four calendar days (2026-10-01 → 10-04), with Phases 8–11 in the final ~21 hours. The tier-order discipline (§0.4.2) was respected in scaffolding order, but the capacity model (3 build FTE, 1,088 effective PW) cannot hold for functional depth — the 5.87× Wave-1 overcommitment is now a measured reality, not a projection | High |
| P-4 | The **G4 tranche boundary** (v1.0 scope-complete, re-authorisation of Waves 5–9 per D-017) has been crossed in scaffolding terms without the Steering re-authorisation the roadmap makes mandatory | High |
| P-5 | Workstation baseline deviation D-WS-001 (Windows-native) is well-documented but diverges from the roadmap's Ubuntu baseline; doctor check 13/14 semantics changed accordingly | Low |

---

## 5. Expert recommendations

### 5.1 Immediate (before any further feature work) — "stop, close the ring"

1. **Start the DEP-31 legal engagement this week.** It is the longest external lead (6–10 weeks), the G0a HOLD rests on it, and `D-013` gates the residency architecture that Phase 3 already encoded. The drafted engagement letter (`docs/p01-m02/DEP-31-engagement-scope.md`) needs only a signature. Convene the Board for B-01 in the same session.
2. **Write `verify-gate-g2.ps1` and the Phase 5 traceability record before building Phase 5.** The estate's own discipline — an executable gate per phase — has a hole exactly where the risk is highest. Defining the 10 G2 criteria first (from `P05-M10`) will define what "done" means for the hardest phase. Write the G9 verifier at the same time so no gate is ever missing again.
3. **Decide the OCA strategy explicitly, now.** Either (a) commit to extending OCA `field-service`/`stock`/`dms`/`payroll` as the roadmap's L2 layer demands — in which case the 18 unconsumed subtrees become the base of Phases 5–8's real build — or (b) raise a CR recording that custom-thin replaces L2 for named modules, with the maintenance-cost consequence written down. The current state (vendored, pinned, CI-verified, never imported) is the worst of both worlds: clone cost without the benefit.
4. **Run the CI pipeline once on a real runner and publish the budget measurements.** Until a pre-merge run exists, the 17-stage pipeline is a document. Fix V-3 (fitness FF-03 path) and V-9 (pytest import mode) in the same pass.

### 5.2 Structural (next 2–3 months)

5. **Re-plan Phase 5 as the next vertical, not Phase 12-style breadth.** The service-to-field flow (M15 inventory → M31 workshop → M02 dispatch → P02 technician app with the offline engine) is the business's revenue path and the source of three of the 15 critical journeys. Sequence: M15 on Odoo `stock` + OCA barcode → M31 on the existing work-order base → M02 on OCA `field-service` with the dispatch-scoring service → offline engine hardening (SQLCipher journal, server sync endpoint per AR-010 §4.3–4.4, the L12 suite). Staff it as the roadmap staffs it: the squad that will own two of the three offline consumers.
6. **Introduce coverage measurement as a gate, not an aspiration.** Wire `pytest --cov` into the addon suite with `--cov-fail-under=80` and a separate 100% job for the `financial`/`tax` markers (the CI stages already specify this — it has simply never run). Payroll (M56) and VAT (M51) are statutory; their calculation paths cannot ship unmeasured.
7. **Burn down the CONDITION ledger deliberately.** 49 items is trackable: convert each CONDITION into a named sprint story with its evidence class (runtime / human / production / external), and re-run the gate verifiers per sprint. The verifiers are already executable — this is the estate's best invention; use it as the drumbeat.
8. **Author the OpenAPI contracts wave-by-wave (B-16).** 1,152 unauthored operations sized at 169–338 PW sit in no plan. Fold contract authoring into each module's DoD-06 so the debt stops growing; schedule a 2-sprint contract catch-up per wave.
9. **Close the 8 placeholder digests by running `resolve-digests.ps1` to completion; delete `update_roadmap.py` (or move it to an archive folder with a warning header) so the remediated roadmap cannot be silently regenerated; reconcile the 35-vs-28 count inside `AUDIT_REPORT.md`.**

### 5.3 Risk posture (honest statements for Steering)

10. **Do not describe the estate as "Phases 1–11 complete."** The defensible statement is: *"Phases 1–4 are implemented and verified green-on-artefacts (with runtime conditions pending); Phases 5–11 are conformant scaffolds averaging 325 LOC/module awaiting functional build; Phase 12 not started; G0a formally at HOLD."* The traceability records themselves use exactly this honest register — keep it.
11. **The capacity arithmetic has not gone away.** 1,842 PW of specified demand against a ramping 3→12 FTE team is 1.69× over-committed on paper; the four-day scaffold sprint proves how much of the "implemented" surface is skeleton. At G4-equivalent re-authorisation, present the measured velocity (the working-agreement record already collects it) and re-scope Waves 5–9 against evidence, as D-017 requires.
12. **Protect the two genuinely strong assets.** The executable-gate + fitness + traceability apparatus and the Phase 3 kernel (party/outbox/RBAC/residency) are the parts of this build that would survive any re-plan. Any descoping decision should cut around them, not through them.

### 5.4 Suggested next three sprints (concrete)

| Sprint | Content |
|---|---|
| S1 | DEP-31 letter signed + Board minutes (B-01/B-02) · `verify-gate-g2.ps1` + `verify-gate-g9.ps1` written · fitness FF-03 path fixed · first real CI run with budget report · all 8 digests resolved |
| S2 | Phase 5 vertical slice 1: M15 inventory on Odoo stock + OCA stock-logistics/barcode, multi-location + van stock, events through the outbox; coverage harness live (80% gate + 100% financial/tax job) |
| S3 | Phase 5 vertical slice 2: M31 workshop bench/WIP board on the work-order base; dispatch-scoring service implemented (FastAPI, event-driven from the outbox); G2 verifier run and conditions burned down |

---

## 6. Verification appendix (commands executed by this audit, 2026-10-15)

```
python -m py_compile <every .py in addons, services, libs, tooling>   → 0 errors
python tooling/fitness/run.py                                        → 20 PASS · 7 SKIP · 0 FAIL (27 checks)
python -m pytest addons -q                                           → 653 passed
python -m pytest services -q --import-mode=importlib                 → 202 passed
python -m pytest services/{stt,payroll-engine,local-residency-stub}  → 44 passed
python tooling/scripts/test-smoke.py                                 → 15/15 PASS
python tooling/scripts/check-cd-id.py                                → OK (331 items)
powershell tooling/gate/verify-gate-{g0a,g0b,g1a,g1,g3,g4,g5,g6,g7,g8,gp}.ps1
   → G0a 10P/6C/2OPEN(HOLD) · G0b 8P/3OPEN · G1a 4P/6C · G1 2P/10C · G3 5P/7C
     G4 6P/8C · G5 9P/1C · G6 7P/3C · G7 7P/3C · G8 6P/2C · GP 9P/3C
   → totals: 73 PASS · 49 CONDITION · 5 OPEN · 0 FAIL over 127 checks (G2, G9 missing)
manifest ast-parse + key validation (66 manifests)                    → 0 errors, 58/67 M-modules
bn_BD.po coverage scan (19 files)                                    → 100% all files
compose scan                                                          → all ports 127.0.0.1; 8 digest placeholders
coverage-artefact scan                                                → none exist (DoD-03 unmeasured)
git log --diff-filter=A (module first-commit dates)                   → Phases 3–7: initial import Oct 3 16:38
                                                                        Phase 8: Oct 3 23:31 · P9: Oct 4 16:29
                                                                        P10: Oct 4 18:07 · P11: Oct 4 19:34
roadmap structural scan (python)                                      → 120 milestones (10/phase) · 1,200 task rows
                                                                        (100/phase, 0 duplicates) · 0 table defects
```

---

## 7. Document integrity & visual inspection of the roadmap (second pass)

The first pass verified 8 of the prior audit's findings by spot-check; the second pass verified **all of them** and added structural checks of the document itself.

### 7.1 Structural integrity — all PASS

| Check | Claimed | Measured | Verdict |
|---|---|---|---|
| Milestones | 120 | **120 distinct `## Pnn-Mnn` headings — exactly 10 per phase × 12 phases** | ✅ |
| Tasks | 1,200 | **1,200 distinct task rows (`\| Pnn-Mnn-Tnn \|`) — exactly 100 per phase** | ✅ |
| Duplicate identifiers | — | **0 duplicate milestone IDs · 0 duplicate task IDs** | ✅ |
| Task-table structure | 7 columns | **0 genuine defects** — 16 flagged rows are correctly-escaped pipes (`\|`) inside cells | ✅ |
| Frontmatter | — | `id: IR-002`, `version: 2.0`, `revised_on: 2026-09-30`, `verified_on: 2026-09-30`, well-formed status line | ✅ |
| Revision history | Required (F-28) | Present with 4 versions including the v2.0.1 remediation entry | ✅ |
| Phase symmetry | — | Every phase exactly 10 milestones / 100 tasks — unusually regular (template-generated, consistent with the `update_roadmap.py` provenance) but internally consistent | ✅ |

### 7.2 Prior-audit remediation verification matrix — all 37 confirmed

| Finding group | Representative checks performed on the current text | Verdict |
|---|---|---|
| F-01…F-07 (Critical text corruptions) | `minio/minio was archived 25 April 2026` narrative restored (line 469); RustFS "closest to the MinIO developer experience" (line 486); PG17 EOL 8 Nov 2029 stated once, correctly (line 496); D-030 licence table shows **original→replacement** shape (lines 515–521); Next.js 15-EOL fact restored in §0.7.2 (line 453); host-service grep names MinIO (line 967) | ✅ all restored |
| F-08…F-12 (blocker-table logic) | B-11 "0 requirements are unbought… gap closed by stakeholder confirmation"; B-19/B-21/B-22 all name the **original** components and their **replacements** correctly (lines 381–384) | ✅ |
| F-13…F-19 (identity/precedence/pins) | `id: IR-002`, title, precedence chain, `P02-M05-T02` reads "Do not pin MinIO… Pin the object store selected by D-028 (Ceph)" (line 1113) | ✅ |
| F-20…F-28 (consistency) | `postgres:17-alpine` (line 76); `revised_on`/`verified_on: 2026-09-30` present; D-029 options table carries the "Selected" marker and strikethrough; Revision History present | ✅ |
| FU-01…FU-09 (Appendix I residuals) | `grep -c "ceph/ceph"` = **0 matches**; month-**37** arithmetic consistent at lines 496, 2699 and 4198; Appendix I names MinIO/Metabase/n8n/Redpanda as the 2026-08-19 subjects with replacement clarifiers | ✅ |

**Conclusion:** the roadmap document itself is in remediated, internally-consistent condition. The one live risk is D-2 (the transformation script sitting beside it).

---

## 8. Second-pass audit record (self-audit of this report, 2026-10-15)

This section documents the audit of the audit, in the same register the codebase's own traceability records use. The first pass of this report contained **9 factual errors and 2 coverage gaps**, all found by re-deriving every numeric claim from raw evidence rather than from the first pass's own notes. All are corrected in this version.

| # | First-pass error | Correction (evidence) |
|---|---|---|
| E-1 | Fitness suite reported as "14 PASS · 8 SKIP" | **20 PASS · 7 SKIP · 0 FAIL** — recounted from the evidence JSON `fitness-20261015T134539Z.json` (27 results) |
| E-2 | "43 CONDITION items across 11 gate verifiers" | **49 CONDITION + 5 OPEN** (73 PASS, 0 FAIL, 127 checks) — summed from the per-gate run outputs |
| E-3 | "18 services directories" | **17** (13 coded + 4 empty/skeleton) |
| E-4 | "9 Next.js apps" | **8** — the 9th `apps/web` entry is `.mimosa`, a tool cache, not an app; the GP gate itself says "8/8 portals" |
| E-5 | "5 placeholder digests" | **8 placeholder occurrences across 4 compose files** (recounted) |
| E-6 | "Gate verifiers: 11 of 12 exist (no G2)" | **10 of the 12 roadmap gates exist — both G2 and G9 are missing**; the 11th file (GP) is a non-roadmap portal gate |
| E-7 | "Phases 5–11 compressed into four days of commits (Oct 3–6)" | **Phases 3–7 landed inside the initial import (2026-10-03 16:38, built Oct 1–3 pre-git); Phases 8–11 landed Oct 3 23:31 → Oct 4 19:34 (~21 hours)** — git `--diff-filter=A` first-commit dates per module |
| E-8 | "63 distinct estate module IDs covered" (ambiguous) | **58 of 67 estate M-modules (87%) + 4 portal addons + 1 design addon = 66 manifests** |
| E-9 | "8 fitness checks SKIP as script missing" (finding V-3) | **7 checks SKIP** (FF-03, 13, 19, 26, 30, 32, 37) |
| G-1 | Coverage gap: roadmap lines 2056–3250 (Phase 6–11 task tables) unread in pass one | **Read in full this pass** — enabled the Phase 6–9 gate-criterion specifics added to §2 (NFR-040 auto-invoice, ≥90% auto-matching, 5-day close, Kafka dual-write programme, BEFTN batch windows, Labour Act 2026 rates) |
| G-2 | Coverage gap: only 8 of the prior audit's findings spot-checked | **All 28 + 9 follow-up findings verified** (§7.2); plus new structural checks (§7.1) and one new finding (D-4: the prior audit's own 35-vs-28 count discrepancy) |

**Method note.** Every number in §1.2, §3 and §6 of this version was re-derived from a machine-readable source (evidence JSON, gate-run output, filesystem count, git metadata) during the second pass. No figure is carried forward from the first pass unverified.

---

## 9. Document control

| | |
|---|---|
| Report file | `roadmap/IMPLEMENTATION_STATUS_AUDIT_REPORT.md` |
| Audited roadmap | `IR-002_Final_Production_Implementation_Roadmap.md` v2.0.1 (2026-09-30) |
| Audited codebase | `1000fix_new_erp_system/1000_fix_codebase/` @ `cb6bf71e42` (2026-10-10) |
| Audit executed | 2026-10-15 — two passes: (1) research + live verification, (2) self-audit, full-document read, all-finding verification, numeric re-derivation |
| Overall status | **Foundation strong · breadth scaffolded · depth pending · Phase 5 critical · Phase 12 untouched · G0a at HOLD** |
