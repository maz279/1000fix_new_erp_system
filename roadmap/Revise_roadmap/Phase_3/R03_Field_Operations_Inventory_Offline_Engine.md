---
id: RR-03
title: "R03 — Field Operations, Inventory & the Offline Engine"
series: Revised Implementation Roadmap (RIR) — 11 phases · 55 milestones
derives_from: IR-002 Phase 5 (P05-M01…P05-M10) — the critical gap, plus P05 completion slices
evidence_base: >
  Audit V-1 (Critical): M02/M15/M31/M10 have NO addons (9 missing module IDs include these);
  services/dispatch-scoring and services/telemetry-collector are EMPTY directories;
  libs/dart/fix_offline is a 758-LOC skeleton (no SQLCipher, no sync server, no L12 suite);
  4 mobile apps are 1-file shells; OCA field-service (33 mods) and stock-logistics (3 repos)
  vendored but unconsumed by any cd_ manifest; no P05 traceability record; G2 verifier absent.
status: EXECUTED 2026-10-16/17 — zero-trust-audited 2026-10-22: G2 RED-OPEN; route optimiser was a hardcoded 0.813 factor (now real haversine/OSRM + 2-opt); SQLCipher offline store is an in-memory fake (open); telemetry flush is a no-op (open)
---

# R03 — Field Operations, Inventory & the Offline Engine

## Charter

| | |
|---|---|
| **Purpose** | Build the missing Wave-2 estate for real: inventory, workshop, field service and dispatch, the shared offline engine at production depth, the technician application, and loyalty — then close G2 |
| **Source phase** | IR-002 P05 in full (the audit's weakest phase) |
| **Entry evidence** | Audit §2 Phase 5 table: every row ❌/🟡; dependency histogram shows zero `stock`/`field_service` depends across 66 manifests |
| **Exit** | `verify-gate-g2.ps1` (written in R01-M05) run with 0 FAIL; M02/M15/M31/M10 shipped to DoD |
| **Strategy** | OCA-first per the estate's L2 rule (extend `stock-logistics-*` and `field-service`, never fork) — reversing the audit's V-2 finding for this wave |

---

## Milestone R03-M01 — M15 Spare Parts & Inventory on Odoo stock + OCA

**Evidence:** no `cd_` module declares `stock` in `depends` (dependency histogram, 2026-10-15); OCA `stock-logistics-workflow/barcode/warehouse` vendored with pinned commits, unconsumed.

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R03-M01-T01 | Install Odoo `stock` + the three vendored OCA stock repos' needed modules into the dev database, cross-checked against `docs/guides/oca-v19-status.md` | V-2: 18 OCA repos vendored-but-unconsumed | Installed stock layer | `make odoo-install-wave1` extended; install log |
| R03-M01-T02 | Build `cd_inventory` (CD-M15-nn): multi-location on `fix.branch`/operating units, van stock as a location type, barcode/QR scan-to-consume via OCA barcode | M15 48 reqs P0; appendix D T3 W2 | New addon + tests | Module installs; DoD checklist started |
| R03-M01-T03 | Build replenishment alerts and reorder rules with the M43 seam (Phase R07 will extend, not replace) | P05-M01-T05 | Reorder engine | Unit tests on reorder math |
| R03-M01-T04 | Register the M15→M19 suspense-account stub in GV-005 **with an expiry date targeting R04** — stock valuation posts to suspense until the GL cutover | Appendix E stub register: "posts to a suspense account… an unreconciled suspense balance across a wave boundary is a finance risk" | GV-005 stub row | Register entry with expiry |
| R03-M01-T05 | Emit M15 events (`stock.consumed`, `stock.returned`, `reorder.triggered`, `van.reconciled`) through `fix_events`; register them | AS-08; outbox exists | Registered events | Event coverage test green |
| R03-M01-T06 | Migrate branch inventory against a **physical count** (not a spreadsheet) with MIG-02 totals — target ≥95% accuracy (G2-04) | P05-M09-T01; G2 criterion | Inventory ETL + count evidence | Reconciliation signed |

---

## Milestone R03-M02 — M31 Workshop & Depot Repair

**Evidence:** work orders exist only as the W1 slice inside `cd_service_order` (`fix.work.order`, 70 LOC) — the W2 workshop capability (58 reqs) is absent.

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R03-M02-T01 | Build `cd_workshop` (CD-M31-nn): bench assignment, WIP board, repair-level routing L1/L2/L3, multi-job handling | M31 58 reqs; P05-M02 rows — no addon exists | New addon | Installs; state machine unified with M01 (AS-06) |
| R03-M02-T02 | Build the evidence pack on the `cd_document_core` attachment API (photos, diagnostic, parts, serial, certification) — consumed by warranty in R05 | P05-M02-T04; MV-02 rationale | Evidence-pack model | Attachment API used, not local impl (AS-01) |
| R03-M02-T03 | Register and expiry-date the two M31 stubs: →M22 certification (returns "eligible" until R06), →M23 QC (M01 owns checklists until R06) | Appendix E: "a stub that always returns 'eligible' is a control that does not work" | 2 GV-005 rows | Register entries |
| R03-M02-T04 | Migrate open workshop WIP from paper job cards (open WIP only; history not migrated per the P01-M07 ruling) | P05-M09-T03 | WIP capture record | Count reconciled |
| R03-M02-T05 | Emit M31 events; register; add the workshop surface to the P03 operations workspace | AS-08; UX-002 | Registered events + menu | Negative-tested menu visibility |

---

## Milestone R03-M03 — M02 Field Service, Dispatch & the geospatial platform

**Evidence:** only a 74-line dispatch-console JS exists in `cd_p03_portal/static/src/p03_dispatch_console.js`; `services/dispatch-scoring/` is an **empty directory**; M02 is 74 reqs, P0, 40 PW — the largest missing P0.

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R03-M03-T01 | Install OCA `field-service` (33 modules) verified against the v19 status matrix; build `cd_field_service` (CD-M02-nn) extensions: assignment flows, accept/decline with reason, zone/geofence enforcement on `fix.zone` | P05-M03; V-2 (vendored unconsumed); AS-05 | New addon on OCA base | Installs over field-service |
| R03-M03-T02 | Implement `services/dispatch-scoring` (Python/FastAPI, event-driven from the outbox): score on skill, certification (stub until R06), van stock, zone, SLA risk, route | **Empty directory** verified 2026-10-15; P05-M03-T03 | Working service + tests | Service tests in the 202+ set grow |
| R03-M03-T03 | Stand up the geospatial stack: TimescaleDB hypertables + compression, Traccar 6.7 (already digest-pinned in the `field` profile), OSRM + VROOM; implement the Go `services/telemetry-collector` to 50k events/minute design | Compose `field` profile defines all four — no integration code; **telemetry-collector empty** | Live local stack + collector | `make up PROFILE=field` healthy; ingest test |
| R03-M03-T04 | Implement the route orchestrator over VROOM/OSRM and measure the ≥15% travel-time reduction against a recorded baseline (G2-03) | P05-M03-T04; G2 criterion | Orchestrator + measurement | Baseline vs optimised report |
| R03-M03-T05 | Register the M02 stubs (→M22 certification, →M55 availability returning M30's working calendar) with expiries; emit the throttled M02 event set | Appendix E; NFR-056 throttle rule | GV-005 rows; registered events | Event throttle test |
| R03-M03-T06 | Integrate INT-011 redundant SMS, INT-014 push, INT-019–023 mapping/routing/traffic/GPS — each with a documented, tested fallback | P05-M09-T05..T07 | 5+2 integrations | Fallback register tests |

---

## Milestone R03-M04 — The offline engine at production depth + the technician app (P02)

**Evidence:** `libs/dart/fix_offline` = 758 LOC across 7 files — command/conflict/evidence/idempotency/journal/sync **models** only; no SQLCipher, no server-side sync endpoint service, no L12 suite; each of the 4 mobile apps is 1 Dart file + pubspec.

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R03-M04-T01 | Harden the journal: encrypted SQLite (SQLCipher), key from device credentials + server-issued key, wipe-on-revocation | AR-010 §3/4.1; audit: "no SQLCipher encryption" | Hardened `fix_offline` | Dart tests |
| R03-M04-T02 | Implement the **server sync endpoint** (upload-then-download per SP-07; one DB transaction per command per SP-01..03; per-command idempotency ledger returning original results) as an Odoo controller or dedicated service | AR-010 §4.2–§4.4; audit: "no server sync endpoint" | Sync endpoint + ledger | Contract tests incl. replay |
| R03-M04-T03 | Implement conflict detection/authority matrix (apply · reject · apply-with-conflict) and the two-state disclosure UI contract (not-yet-synced ≠ synced-and-rejected) | AR-010 §5–§6 | Conflict engine | Scripted-conflict tests |
| R03-M04-T04 | Implement the deferred evidence channel (resumable, never blocking state sync) for 40 MB photo backlogs | AR-010 §8 SP-09 | Evidence channel | Backlog test |
| R03-M04-T05 | Build the technician app (P02) for real on `fix_ui`: day view, geofenced clock-in, job execution with the diagnostic tree, parts scan-to-consume, evidence capture with Bengali voice notes, estimate approval + e-signature, navigation, panic alert (M59 early slice) | Audit: apps are 1-file shells; P05-M06 rows | Full Flutter app | Device-lab pass + field pilot |
| R03-M04-T06 | Build and run the **L12 offline suite** (33 scripts; 24-hour operation; scripted conflict scenarios) and schedule the TS-015 field half | QA-001 L12; G2-02 "the single hardest technical requirement" | L12 suite + 24-h zero-loss demo | G2-02 evidence |

---

## Milestone R03-M05 — M10 Loyalty, completion slices, customer portal hardening, and G2

**Evidence:** M10 has no addon; M01's W2 business-line slice (`FR-SRM-063…088` — rental intake, swap-out) absent from `fix_service_order.py` (grep found no rental/swap models); P01 portal exists (PP5) but booking-funnel conversion unmeasured.

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R03-M05-T01 | Build `cd_loyalty` (CD-M10-nn): privilege programme, points, vouchers, campaign hooks; register the M10→M11/M20 redemption stub with expiry (closes in R04) | M10 44 reqs, no addon; Appendix E | New addon + stub row | Tests green |
| R03-M05-T02 | Complete the M01 W2 slice: business-line extensions FR-SRM-063…088 (rental intake, swap-out, deferred block) and verify the 28 allocated-but-unused requirement IDs are closed or reallocated | P05-M08-T05; H2-03; grep: no rental/swap in fix_service_order.py | Extended service order | Requirement register rows closed |
| R03-M05-T03 | Complete the M17 W2 slice and M64 completion (rest of MDM beyond the W1 core) | P05-M08-T04/T06 | Completion code | DoD per slice |
| R03-M05-T04 | Harden P01 customer portal: measure the booking funnel (>72% design KPI), the <400 KB budget on 3G (already gated), the public no-auth tracking link surface review, and the ≥60% online-booking pilot metric | G2-05; PP5 delivered the surface but not the pilot metrics | Pilot evidence | Metrics recorded at pilot sites |
| R03-M05-T05 | Withdraw paper service forms in Dhaka and run `verify-gate-g2.ps1` end-to-end; publish the gate report with conditions | G2-06/G2-10; audit: G2 verifier now exists (R01-M05) | Signed G2 record | G2 JSON evidence filed |

---

**Sequence:** M01 → M02 → M03 → M04 → M05 (M01/M02 may interleave; M04 depends on M03's events; M05 closes the wave).
