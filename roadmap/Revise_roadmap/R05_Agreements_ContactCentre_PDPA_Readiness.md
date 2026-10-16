---
id: RR-05
title: "R05 — Agreements, Contact Centre & PDPA Readiness"
series: Revised Implementation Roadmap (RIR) — 11 phases · 55 milestones
derives_from: IR-002 Phase 7 (P07-M01…P07-M10)
evidence_base: >
  G4 re-run 2026-10-15: 6 PASS · 8 CONDITION (24h/72h claims live, ≥90% approval, 10+ corporate
  clients, hotline capture, ≥40% AI resolution, PDPA verified operational, journeys 4/5/15
  nightly, v1.0 scope statement). AUT-018 code exists (fix_warranty_claims.py:141) but the live
  24h/72h timing unproven; analytics portal P06 is 3 static TSX with Apache Superset unwired;
  OCA contract repo vendored-unconsumed.
status: PLANNED — evidence-derived
---

# R05 — Agreements, Contact Centre & PDPA Readiness

## Charter

| | |
|---|---|
| **Purpose** | Close the v1.0 commitment at functional depth — contracts, warranty claims at brand scale, subscription billing, the contact centre with a measured AI assistant, real analytics — and reach **verified** PDPA readiness before the ~13 May 2027 enforcement date, then take the D-017 tranche decision at G4 |
| **Source phase** | IR-002 P07 |
| **Entry evidence** | G4-01…G4-08 CONDITION (2026-10-15); audit §2 Phase 7 row |
| **Exit** | G4 re-run 0 FAIL **plus** the Steering tranche decision (re-authorise / re-scope / stop) recorded in GV-003 |

---

## Milestone R05-M01 — M08 Contracts and M09 Warranty at brand scale

**Evidence:** `cd_contract_core` carries entitlement fields (`entitlement_ids`, `entitlement_active()` referenced by M01) but OCA `contract` (12 modules) is vendored-unconsumed; AUT-018 auto-claim code exists (verified at fix_warranty_claims.py:141-145) without the live 24h/72h timing or the 17+ brand Airflow workflows.

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R05-M01-T01 | Install OCA `contract` (12 modules) and rebuild `cd_contract_core` on it: entitlement draw-down, contract-vs-service SLA reconciliation (one concept, two scopes), renewal/escalation/price-revision, PM schedule generator feeding dispatch | V-2; P07-M01 rows | Extended contract engine | Tests; PM orders appear in M02 |
| R05-M01-T02 | Prove AUT-018 live: claims auto-created within **24 h** of a completed warranty job and submitted within **72 h** (G4-01) — run the clock, don't assert it | G4-01 CONDITION; code exists unproven | Timing evidence | G4 verifier item PASS |
| R05-M01-T03 | Build the 17+ brand submission workflows in Apache Airflow (one per brand template — configuration, not code) and the completeness check that **blocks** incomplete packs | P07-M02-T05/T06; Airflow compose-pinned since R01 | Airflow DAGs | DAG runs green per template |
| R05-M01-T04 | Verify the "17+ brands" figure against real counterparties (H2-12) and measure first-submission approval rate to **≥90%** (G4-02) | G4-02; P07-M02-T07 | Verified brand register + rate | Monthly rate report |
| R05-M01-T05 | Claim-status webhooks and remittance reconciliation flagging unmatched; evidence pack assembly drawing on the R03-M02 workshop pack | P07-M02-T08 | Reconciliation live | Unmatched flagged = 0 aged |

---

## Milestone R05-M02 — M39 Subscription, M53 W4 revenue, M51 completion

**Evidence:** `cd_subscription`/`cd_settlement_ext` exist as scaffolds; consolidated B2B invoicing ("one invoice, many jobs, many sites") unimplemented; settlement engine service exists (4 py) with the M12↔M53 break noted in P10 traceability.

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R05-M02-T01 | Build consolidated B2B invoicing on OCA `contract` subscription recurrences; dunning/refund flows | P07-M03-T02/T03 | Consolidated billing | 400-device client → 1 invoice demo |
| R05-M02-T02 | Complete the M53 W4 slice: revenue recognition (non-marketplace half) with 100% coverage on revenue/commission calculation | DoD-03; P07-M03-T10 | Rev-rec engine | CI financial job 100% |
| R05-M02-T03 | Commission engine fed by events only (M12 earning is an event; M53 never called by M12 — verify by test) | Appendix E pair 12 | Event-driven commission | Dependency negative-test |
| R05-M02-T04 | Settlement-engine service to payout-run readiness with SoD approval authority (the rail itself lands R08) | P07-M03-T07 | Payout-run model | SoD negative tests |

---

## Milestone R05-M03 — M27 Contact Centre and M32 Conversational AI, measured

**Evidence:** `cd_contact_centre` scaffold (8 py); G4-04b hotline capture and G4-05b ≥40% AI resolution CONDITION; L6 CPaaS and qualified e-signature are the two undecided commercial components; Ollama is a compose placeholder (asset-ml).

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R05-M03-T01 | Take the L6 decisions formally: CPaaS telephony and qualified e-signature — CFO approval each, with the written OSS-alternative review (§L6 rule) | TSS §9; undecided commercial items | 2 minuted L6 decisions | GV-003 entries |
| R05-M03-T02 | Integrate INT-015 telephony and INT-018 chat; unify channels (voice/chat/email/WhatsApp/in-app) with conversation capture to the system of record (G4-04) | G4-04b CONDITION | Unified channel model | Hotline conversation in record |
| R05-M03-T03 | Deploy Ollama (resolve digest in R01) with the GPU latency measurement taken **before** purchase; transactional-intent assistant with Bengali/English NLU on real utterances | P07-M05-T05/T08; "GPU only if latency requires" | Live assistant | Intent test suite |
| R05-M03-T04 | Implement human handoff with full context transfer and measure **≥40% first-contact resolution** in production terms (G4-05) | G4-05b CONDITION | Handoff + measurement | Rate report vs handoffs |
| R05-M03-T05 | Confirm the DPIA legal basis for transcript mining **before** mining begins (SC-003 recorded no confirmed basis) | P07-M05-T04 warning | Basis confirmation | DP Forum minute |

---

## Milestone R05-M04 — M25/M62 analytics and the four portals at depth

**Evidence:** P06 analytics portal is 3 static TSX (audit §3 "Superset not wired"); `cd_metric_registry` provides the KPI/governance layer; mis-builder/reporting-engine vendored-unconsumed; 95 registered KPIs unmeasured; 69 of 102 portal-consumed events unpublished (B-17).

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R05-M04-T01 | Deploy Apache Superset on the read replica (never the primary); build the five dashboard sets (executive, branch, technician, finance, warranty) | P07-M07-T01/T05; audit "Superset not wired" | P06 live on Superset | Dashboards render from replica |
| R05-M04-T02 | Install OCA `mis-builder` + `reporting-engine`; build the M62 W4 dimensional model and the dbt ETL skeleton (full warehouse lands R09) | P07-M07-T02..T04 | Reporting layer + dbt seed | dbt build green on replica |
| R05-M04-T03 | Instrument and surface the **95 registered KPIs** in M25; reconcile the 250-in-use figure (BM-002) | DoD-09; P07-M07-T06 | KPI register live | Every delivered module's KPI visible |
| R05-M04-T04 | Deepen P04 corporate (tender/multi-site admin), P08 brand (claim submission/reconciliation), P10 agent console (queue + customer 360) — 10+ corporate clients transacting is G4-03 | G4-03 CONDITION | 3 portals at depth | Client transaction evidence |
| R05-M04-T05 | Address the **69 unpublished portal-consumed events** for these four portals: rename, project, or register each (three dispositions) | B-17: "67.6% is not a rounding error" | Event reconciliation register | Register complete |

---

## Milestone R05-M05 — PDPA verified operational, v1.0 statement, and the G4 tranche decision

**Evidence:** G4-06b "PDPA compliance VERIFIED operational" and G4-08 "v1.0 scope-completion statement" CONDITION; enforcement activates ~13 May 2027 (§0.7.4); consent registry and DSR orchestrator exist as code.

| ID | Task | Evidence basis | Produces | Verify |
|---|---|---|---|---|
| R05-M05-T01 | Complete the DSR orchestrator: portable machine-readable export assembling regional + Z4 data; **rehearse** the erasure saga with compensating actions across stores/replicas/warehouse/backups, preserving the 5-year processing record | P07-M08-T03..T05 | Rehearsed DSR + erasure | Saga drill record |
| R05-M05-T02 | Implement controller-side 30-day consumer notification and the NDMA breach-notification runbook — rehearsed, not documented | P07-M08-T06/T07 | Notification flows | Breach drill executed |
| R05-M05-T03 | Re-run and sign the SC-003 DPIA **against what was built**, then run the PDPA readiness assessment as a G4 gate item (G4-06) | G4-06b; P07-M08-T09/T10 | Signed DPIA + assessment | Filed under SC-003 |
| R05-M05-T04 | Automate journeys 4, 5 and 15 nightly (warranty-to-reimbursement, AMC lifecycle, month-close-to-VAT-return) | G4-07 CONDITION | 3 journey specs | Nightly green |
| R05-M05-T05 | Produce the v1.0 scope-completion statement (every v1.0 commitment mapped to delivered capability, gaps named) and convene Steering for the **D-017 tranche decision** — re-authorise Waves 5–9, re-scope, or stop | G4-08; §7.0 "the roadmap makes it an explicit stop" | Signed statement + decision | GV-003 tranche record |

---

**Sequence:** M01 → M02 → M03 → M04 → M05 (M02 parallel after M01-T01; M05 requires all).
