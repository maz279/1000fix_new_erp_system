---
id: RR-04
title: "R04 — Money, Tax & Document Depth"
series: Revised Implementation Roadmap (RIR) — 11 phases · 55 milestones
derives_from: IR-002 Phase 6 (P06-M01…P06-M10)
evidence_base: >
  G3 re-run 2026-10-15: 5 PASS · 7 CONDITION (auto-invoice NFR-040, ≥90% auto-match, NBR
  acceptance, 5-day close, custody chain, live three-way negative test, L6 journeys 1/2/3/12);
  finance modules are scaffold-to-mid depth (cd_gl_ext 214 LOC; cd_tax_engine_bd 933 LOC is the
  deepest); 4 vendored OCA finance repos (mis-builder, account-financial-×2, reporting-engine)
  unconsumed; M15→M19 suspense stub opened in R03 must close here.
status: PLANNED — evidence-derived
---

# R04 — Money, Tax & Document Depth

## Charter

| | |
|---|---|
| **Purpose** | Take the finance estate from conformant scaffolds to the money-moving, statutory-filing capability G3 demands: auto-invoicing, payment rails, three-way match, VAT returns, and the full observability stack |
| **Source phase** | IR-002 P06 |
| **Entry evidence** | G3-01…G3-07 CONDITION (2026-10-15 run); audit §2 Phase 6 row |
| **Exit** | G3 re-run 0 FAIL; Mushak 9.1 filed online for one full month without NBR exception |

---

## Milestone R04-M01 — M19 General Ledger at full depth

**Evidence:** `cd_gl_ext` is 214 LOC; OCA finance repos vendored-unconsumed (V-2); the M15 suspense stub (R03-M01-T04) is open with expiry targeting this phase.

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R04-M01-T01 | Install the vendored OCA finance layer (`account-financial-tools`, `account-financial-reporting`, `mis-builder`, `reporting-engine`) and build `cd_gl_ext` on it — extend, never fork | V-2; P06-M01-T01 | Installed + extended GL | Installs clean; FF-03 green |
| R04-M01-T02 | Load the Bangladesh chart of accounts from the `MD-*` finance content set (master data, not code) | P06-M01-T02; B-14 content dependency | Loaded CoA | CoA import reconciled |
| R04-M01-T03 | Build the period-close process targeting **month-end close within 5 days** and instrument it (G3-04) | G3-04 CONDITION | Close process + KPI | First timed close ≤5 days |
| R04-M01-T04 | **Reconcile the W2 inventory suspense account and close the M15→M19 stub** — an unreconciled balance across a wave boundary is a named finance risk | Appendix E; stub opened R03-M01-T04 | Reconciled suspense; GV-005 closure | Zero suspense balance; stub closed |
| R04-M01-T05 | Achieve 100% coverage on every financial calculation path (the R01-M04 harness now measures it) | DoD-03; ci.yml financial job never ran | Coverage ≥100% financial marker | CI financial job green |

---

## Milestone R04-M02 — M20/M52/M50: AR, AP and Treasury to gate depth

**Evidence:** G3-01 (auto-invoice 5 s), G3-06b (live negative-tested three-way match) CONDITION; interface breaks M20↔M50/M51, M50↔M52 designed in Appendix E but unproven live.

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R04-M02-T01 | Implement **automatic invoice generation from a closed job within 5 seconds** (NFR-040) with the G3-01 evidence run | G3-01 CONDITION | Auto-invoice path | Timed demo 100% of closed jobs |
| R04-M02-T02 | Implement the synchronous M20→M51 determination call and the event-only M20↔M50 break; prove no synchronous back-call exists via a dependency test | Appendix E pair 6/7 | Interface conformance tests | Tests green |
| R04-M02-T03 | Build dunning/ageing, credit notes with approval authority (SoD control), and consolidated billing hooks (full B2B consolidation lands R05) | P06-M03-T05/T06 | Collections + adjustments | Negative tests per role |
| R04-M02-T04 | Implement employee expense on `hr_expense` (closes the M52→M21 consequence of MV-01) and treasury bank reconciliation consuming M04's cash drawer | P06-M04-T02/T07 | Expense + reconciliation | Reconciles to M04 shift data |
| R04-M02-T05 | Live negative-test three-way match: an unmatched vendor invoice is **rejected**, not warned (G3-06b) | G3-06b CONDITION; P06-M04-T03 | Blocking demonstration | Signed negative-test record |
| R04-M02-T06 | Complete the P05 vendor portal (RFQ response, PO acknowledgement, delivery confirmation, onboarding from the EO-* set) and the P09 rider app (custody pickup/scan/delivery on `fix_offline`, coordinator view in OWL) — both are W3 portal deliverables shipping as skeletons | P06-M09 rows; audit: "vendor portal… rider app skeleton" | 2 portals at depth | WCAG + Bengali 100% |
| R04-M02-T07 | Take M03/M16/M41 to depth: consignments with **unbroken chain of custody** (G3-05's evidence), pick-and-drop + reverse logistics flows, requisition→PO→receipt on Odoo `purchase` + OCA `purchase-workflow`, WMS operations on OCA `stock-logistics-warehouse` (vendored, unconsumed); M42 scorecard seam verified asymmetric | P06-M07 rows; audit scaffolds register (cd_consignment/cd_requisition/cd_wms_structure); V-2 | 3 modules at depth + custody demo | Journey 3 green; G3-05 PASS |
| R04-M02-T08 | Take M11 W3 pricing and M36 quotation to depth: price books/rate cards on the catalogue kernel, **discount governance as a SoD control**, tender management, quotation unified with the M01 estimate — and **close the M10→M11/M20 redemption stub** (points become spendable) | P06-M06 rows; stub register (opened R03-M05-T01 with expiry here) | M11/M36 depth; stub closed | Redemption e2e test; GV-005 closure |

---

## Milestone R04-M03 — Payment integrations certified

**Evidence:** `services/payment-connectors` exists (4 py, bKash/Nagad/SSLCOMMERZ adapters) with tests but dry-run defaults; gateway sandbox certification and bank feeds are ahead.

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R04-M03-T01 | Obtain sandbox credentials for bKash/Nagad/SSLCOMMERZ (DEP-16-class external leads — start in R01) and certify each connector against its sandbox | P06-M05-T02..T04 | 3 certified connectors | Sandbox certification records |
| R04-M03-T02 | Implement idempotent payment confirmation (a retried confirmation must not double-credit) with tests | DI-04; P06-M05-T06 | Idempotency proofs | Double-submit test green |
| R04-M03-T03 | Integrate INT-004 bank statement feed and INT-006; build auto-reconciliation to **≥90% match** (G3-02) | G3-02 CONDITION | Feed + rules | Measured match rate ≥90% |
| R04-M03-T04 | Implement and test the P0 payment fallback register (gateway outage degrades, never stops trading) | §05-03 §7; P06-M05-T08 | Fallback behaviours | Outage simulation test |
| R04-M03-T05 | Author and verify pacts for every W3 integration in the sandbox; Pact broker fail-closed wired into CI | PS-01; ci.yml contract stage never ran | Verified pacts | Broker shows green verifications |

---

## Milestone R04-M04 — M51 tax completion and NBR engagement

**Evidence:** `cd_tax_engine_bd` already carries determination, Mushak 6.3, event-driven register, 9.1 logic with holiday rollover and nil returns (933 LOC — verified deepest finance module); NBR e-VAT (INT-038) unstarted; DEP-24 external.

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R04-M04-T01 | Obtain the NBR e-VAT specification (DEP-24 external lead — escalate if not started in R01) and integrate INT-038 | P07-M04-T03 note "start it in Phase 1" | e-VAT integration | Spec obtained; adapter tests |
| R04-M04-T02 | Build VAT sub-ledgers reconciled to the GL and TDS quarterly returns (statutory dates 25 Oct/Jan/Apr/Jul) | P07-M04-T02/T04 | Sub-ledgers + TDS | Journey 15 dry run |
| R04-M04-T03 | File one full month's Mushak 9.1 online via the NBR portal (online-only since 1 Jul 2026) and record acceptance **without NBR exception** (G3-03) | G3-03 CONDITION; §0.7.4 item 2 | Filed return evidence | NBR acceptance record |
| R04-M04-T04 | Withholding-tax certificate issuance flow; 100% coverage on every return-calculation path | DoD-03; P07-M04-T05/T08 | Certificates + coverage | CI tax job 100% |

---

## Milestone R04-M05 — Observability wiring, journey automation, and G3

**Evidence:** GP-10 CONDITION — "OTel trace round-trip… otel-collector image fails exec on this host"; compose observability profile fully pinned but the correlation-id chain unproven; L6 journeys must be "fully automated by W3".

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R04-M05-T01 | Wire OpenTelemetry instrumentation across services and Odoo with a **single correlation id across every hop**; verify the trace round-trip in Tempo/Grafana (discharges GP-10) | GP-10 CONDITION; NFR-092 | Instrumented estate | Trace visible end-to-end |
| R04-M05-T02 | Build the operational dashboards and alerting per PE-008 (dispatch, GPS health, payment, close) with anti-fatigue review | P06-M08-T06/T07 | Dashboards + alerts | Alert review recorded |
| R04-M05-T03 | Automate journeys 1, 2, 3 and 12 into the nightly L6 run (extend the existing 10-journey Playwright suite) | G3-07 CONDITION; tooling/e2e has 10 specs | 4 new journey specs | Nightly green ×3 runs |
| R04-M05-T04 | Enable FF-33 (performance at 1.5× peak) now that representative volume exists; run the first measured perf pass | P06-M08-T09 | FF-33 live + report | Fitness register updated |
| R04-M05-T05 | Run `verify-gate-g3.ps1` end-to-end; publish the gate report with residual conditions | G3 discipline | Signed G3 record | G3 JSON 0 FAIL |
| R04-M05-T06 | Take M63 process automation to depth: each of the **60 business automations (AUT-001…060)** assigned its named engine (Odoo automated action / Airflow workflow / domain service) and implemented — G3-e passes the register at artefact level only; the engines must exist | P06-M08-T03/T04; G3-e PASS-on-artefacts | 60 automations live | Automation register 60/60 implemented |

---

**Sequence:** M01 → M02 → M03 → M04 → M05 (M03 parallelisable after M02-T02; M05 requires all).
