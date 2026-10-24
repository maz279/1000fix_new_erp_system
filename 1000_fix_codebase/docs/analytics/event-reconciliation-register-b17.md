# Event Reconciliation Register (B-17 / R05-M04-T05)

**Status:** APPROVED — ADJUDICATED  
**Date:** 2026-10-17  
**Authority:** Enterprise Architecture & Integration Layer (IN-003 §7 / B-17 / R05-M04-T05)  
**Target Milestone:** R05-M04 — M25/M62 analytics and the four portals at depth  
**Evidence Baseline:** `project-guide-doc/04_Integration_and_API_Engineering/IN-003_artefacts/reconciliation/portal-consumed-unpublished.csv` (69 unpublished events, 67.6% consumer-side gap)

---

## 1. Executive Summary & Problem Statement

In the integration baseline analysis (IN-001 / IN-003 §7.1), the portal layer consumed **102 distinct events**, but only **33 events (32.4%)** were published by an estate backend module. The remaining **69 events (67.6%)** were consumed by portals without a declared publishing module. As noted in B-17: *"67.6% is not a rounding error"*.

Milestone **R05-M04-T05** mandates addressing these **69 unpublished portal-consumed events** across three normative dispositions:
1. **D1 — Same fact, two names (Rename):** The fact is already published under a different name. The consumer is corrected to the producer's canonical name.
2. **D2 — Coarse projection (Project):** The consumer requires a rolled-up view of finer-grained events (e.g. `.status_changed`, `.updated`, `_en_route`). A named stream projector is specified and documented.
3. **D3 — Genuinely absent (Register):** The fact was absent from the initial schema catalogue. The event is formally registered with an owning module, schema contract, and outbox publisher.

Every single one of the 69 events is now adjudicated, with **0 unadjudicated rows remaining (100% resolution)**.

---

## 2. Adjudication Totals

| Disposition Class | Meaning | Count | Percentage |
|---|---|---:|---:|
| **D1** | Rename (Consumer aligned to canonical producer event) | **25** | 36.2% |
| **D2** | Projection (Named stream projector over fine-grained events) | **11** | 15.9% |
| **D3** | Register (Formally registered in event catalogue with owning module) | **33** | 47.8% |
| **Unadjudicated** | Open items requiring decision | **0** | **0.0%** |
| **Total** | Full baseline surface | **69** | **100.0%** |

---

## 3. The Four Portals at Depth (R05-M04)

Milestone R05-M04 explicitly focuses on the four key operational and analytical portals:
- **P04 Corporate B2B Portal** (Tender & Multi-Site Admin)
- **P06 Analytics Portal** (Superset on Read Replica & Executive Dashboards)
- **P08 Brand Partner Portal** (Claim Submission & Counterparty SLA Tracking)
- **P10 Contact Centre / Agent Console** (Queue Management & Customer 360)

### 3.1 P04 Corporate B2B Portal (6 Events)

| Consumed Event | Disposition | Published / Projected Target | Owning Module | Adjudication Rationale |
|---|---|---|---|---|
| `credit_note.issued` | **D1** | `ar.credit_note_issued` | M53 (`cd_billing_engine`) | Convention-B namespace absorbed noun; M53 already publishes (IN-A-10) |
| `entitlement.threshold_crossed` | **D3** | `entitlement.threshold_crossed` | M08 (`cd_contract_core`) | Registered schema for corporate SLA 80%/100% draw-down threshold alerts |
| `invoice.issued` | **D1** | `ar.invoice_validated` | M20 (`cd_billing_engine`) | Corrected to canonical statutory Mushak 6.3 invoice validation event |
| `project.milestone_reached` | **D1** | `project.milestone_accepted` | M67 (`cd_msp_contract`) | Corrected to MSP contract acceptance transition event |
| `service_order.status_changed` | **D2** | `service_order.state_transition` | M01 (`cd_service_order`) | Stream projector aggregating fine-grained field transitions into high-level portal state |
| `sla.at_risk` | **D1** | `sla.warning` | M01 (`cd_service_order`) | Same namespace; canonical event is `sla.warning` (AP-01 class-1 pair) |

### 3.2 P06 Analytics Portal (5 Events)

| Consumed Event | Disposition | Published / Projected Target | Owning Module | Adjudication Rationale |
|---|---|---|---|---|
| `dataset.quality_failed` | **D1** | `data_quality.failing` | M62 (`cd_metric_registry`) | Corrected to canonical Data Quality rule failure event in M62 |
| `dataset.refreshed` | **D3** | `data_warehouse.dataset_refreshed` | M62 (`cd_metric_registry`) | Registered schema published upon completion of read-replica dbt ETL build |
| `model.published` | **D3** | `ai_model.published` | M26 (`ml-gateway`) | Registered schema for Ollama / Timefold optimization model deployments |
| `sla.at_risk` | **D1** | `sla.warning` | M01 (`cd_service_order`) | Corrected to canonical `sla.warning` for executive SLA breach forecasting |
| `user.scope_changed` | **D3** | `rbac.user_scope_changed` | M29 (`cd_rbac_ext`) | Registered schema for analytics row-level-security (RLS) cache invalidation |

### 3.3 P08 Brand Partner Portal (6 Events)

| Consumed Event | Disposition | Published / Projected Target | Owning Module | Adjudication Rationale |
|---|---|---|---|---|
| `capa.closed` | **D1** | `qms.capa_closed` | M23 (`cd_grc`) | Corrected to canonical ISO 9001:2015 CAPA resolution event in QMS |
| `certification.expiring` | **D2** | `technician.certification_status_changed` | M22 (`cd_competency`) | Time-windowed stream projection (30d/15d/7d prior to expiration) |
| `claim.evidence_incomplete` | **D3** | `warranty.claim_evidence_incomplete` | M09 (`cd_warranty_claims`) | Registered schema triggering brand automated photo/serial completeness check |
| `payment.received` | **D1** | `payment.transaction_settled` | M20 (`cd_settlement_ext`) | Corrected to canonical settlement ledger event |
| `recall.execution_updated` | **D3** | `warranty.recall_execution_updated` | M09 (`cd_warranty_claims`) | Registered schema for OEM hardware safety recall progress updates |
| `stock.consignment_reconciled` | **D1** | `stock.consignment_consumed` | M15 (`cd_wms_structure`) | Corrected to canonical consignment inventory consumption ledger event |

### 3.4 P10 Contact Centre / Agent Console (8 Events)

| Consumed Event | Disposition | Published / Projected Target | Owning Module | Adjudication Rationale |
|---|---|---|---|---|
| `assist.suggestion_available` | **D3** | `assist.suggestion_available` | M27 (`cd_contact_centre`) | Registered schema for Ollama real-time contextual intent suggestions |
| `complaint.reference_issued` | **D3** | `complaint.reference_issued` | M27 (`cd_contact_centre`) | Registered schema for customer complaint reference generation |
| `cpaas.degraded` | **D3** | `cpaas.telephony_degraded` | M27 (`cd_contact_centre`) | Registered schema under INT-015 for telephony carrier MOS jitter alerting |
| `interaction.routed` | **D3** | `contact.interaction_routed` | M27 (`cd_contact_centre`) | Registered schema for omnichannel queue routing to available agent |
| `interaction.transferred` | **D3** | `contact.interaction_transferred` | M27 (`cd_contact_centre`) | Registered schema for human handoff with full conversation context transfer |
| `payment.received` | **D1** | `payment.transaction_settled` | M20 (`cd_settlement_ext`) | Corrected to canonical customer payment settlement event |
| `queue.sla_breached` | **D2** | `service_order.sla_warning` | M27 (`cd_contact_centre`) | Stream projector over queue wait duration vs contractual SLA target |
| `service_order.status_changed` | **D2** | `service_order.state_transition` | M01 (`cd_service_order`) | Stream projector tracking active customer service order transitions |

---

## 4. Full Estate Event Register (69 Events)

The complete machine-readable mapping of all 69 events is published in:
`contracts/events/portal-event-reconciliation-register.json`

---

## 5. Verification

Automated suite `tests/test_r05_m04_event_reconciliation.py` asserts:
1. Total adjudicated count = 69 (matches baseline).
2. Unadjudicated count = 0 (100% adjudicated).
3. Every D1 event maps to a valid published event in the estate.
4. Every D2 event defines a valid stream projection rule.
5. Every D3 event defines an owning module and registered schema.
6. The four focus portals (P04, P06, P08, P10) have 100% coverage.
