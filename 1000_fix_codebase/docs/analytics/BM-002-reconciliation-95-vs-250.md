---
id: BM-002-REC
title: "M25 / BM-002 KPI Reconciliation Report: 95 Registered vs. 250 In-Use Metrics"
category: Data Governance & Analytics Architecture
status: RATIFIED
version: 1.0
date: 2026-10-17
author: Principal Enterprise Architect & Lead Data Architect
traces_to:
  - "06-02_KPI_Benefits_and_Acceptance_Criteria.md §2"
  - "BM-002_KPI_Baseline_Measurement_Report.md §9"
  - "RP-001_KPI_Dictionary_and_Metric_Definition_Standard.md"
  - "AUDIT-015 RP-01 (250 KPI identifiers against 95 registered)"
  - "R05_Agreements_ContactCentre_PDPA_Readiness.md (R05-M04-T03)"
---

# M25 / BM-002 KPI Reconciliation Report: 95 Registered vs. 250 In-Use Metrics

## 1. Executive Summary & Purpose

During early architecture phases, `AUDIT-015` (Finding `RP-01`) identified a major apparent discrepancy in the programme's metric governance: **250 distinct KPI identifiers** appeared across the 79 module and portal specifications, whereas the authoritative Board-level register in `06-02` §2 contained only **95 registered KPIs**.

This report, fulfilling milestone task **R05-M04-T03**, formalizes the reconciliation derived in `BM-002` §9, instruments all **95 registered KPIs** in the M25 Analytics engine (`services/bi-warehouse/kpi-register.json`), and provides the definitive data governance ledger explaining the architectural origin, classification, and lifecycle of every metric identifier.

---

## 2. Independent Count & Mathematical Proof

The counts performed on the module and portal specifications yield the exact reconciliation matrix:

```bash
# Reproduction command (from repository root)
grep -rho "KPI-[0-9]\{3\}" 1000fix_ERP_Module/03_Modules/ \
     1000fix_ERP_Module/04_Portals_and_Applications/ | sort -u | wc -l
```

### Table 1: Population Reconciliation Matrix

| Category | Count | Identifier Range | Status & Governance Handling |
|---|---:|---|---|
| **Authoritative Registered KPIs (`06-02` §2)** | **95** | `KPI-001` … `KPI-095` | Board-level benefit drivers. 100% instrumented in M25 (`kpi-register.json`). |
| **Distinct Identifiers in Specifications** | **250** | `KPI-001` … `KPI-305` | Complete metric footprint across all 79 specifications. |
| **Used but Unregistered Operational Metrics** | **196** | `KPI-110` … `KPI-305` | Module-level operational telemetry (M01–M67). Reserved under `RP-001` §4.3; do NOT dilute Board KPIs. |
| **Registered but Unused in Spec Narratives** | **41** | Mixed in `01`…`95` | Strategic platform/benefit metrics measured by dimensional facts, not narrative module text. |
| **Both Registered and Explicitly Cited in Specs** | **54** | Mixed in `01`…`95` | Core operational backbone metrics shared between Board register and module SOPs. |
| **Unallocated Reserved Gap** | **14** | `KPI-096` … `KPI-109` | Reserved buffer space between Board register (1–95) and operational register (110+). |

### Arithmetic Verification (`PG-M10`):
$$\text{Total Distinct Identifiers} = 95 (\text{Registered}) + 196 (\text{Used-but-Unregistered}) = 291 \quad \checkmark$$
$$\text{Cited in Specifications} = 54 (\text{Overlapping}) + 196 (\text{Operational}) = 250 \quad \checkmark$$
$$\text{Unused in Specification Text} = 95 - 54 = 41 \quad \checkmark$$
$$95 + 14 (\text{Gap}) = 109 \to \text{First Operational ID is } \text{KPI-110} \quad \checkmark$$

---

## 3. Structural Decomposition of the 95 Registered KPIs

The 95 registered KPIs are organized into 10 cohesive operational families within `services/bi-warehouse/kpi-register.json`:

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                  1000FiX M25 Authoritative 95-KPI Register                   │
├──────────────────────────┬───────┬───────────────────────────────────────────┤
│ Family                   │ Count │ Primary Source Fact / Owning Modules      │
├──────────────────────────┼───────┼───────────────────────────────────────────┤
│ 1. Service Delivery      │   10  │ fact_service_orders (M01, M04, M11)       │
│ 2. Field Operations      │    9  │ fact_service_orders (M02, M03, M26)       │
│ 3. Customer & CX         │    8  │ fact_nps, fact_conversations (M07, M27)   │
│ 4. Commercial & Revenue  │    9  │ fact_invoices, fact_orders (M08, M10, M11)│
│ 5. Warranty & Claims     │    5  │ fact_warranty_claims (M09 - AUT-018)      │
│ 6. Supply Chain & Parts  │    8  │ fact_service_orders, fact_invoices (M15)  │
│ 7. Financial & Statutory │    9  │ fact_invoices, Mushak-6.3 ledger (M19,20) │
│ 8. People & Quality      │   10  │ dim_technician, CAPA records (M21,22,23)  │
│ 9. New Business Lines    │   16  │ dim_device, MSP/Rental/Refurb facts       │
│ 10. Platform & SRE       │   11  │ Telemetry outbox, DQ logs (M25,28,29,30)  │
├──────────────────────────┼───────┼───────────────────────────────────────────┤
│ TOTAL                    │   95  │ 100% Covered in kpi-register.json         │
└──────────────────────────┴───────┴───────────────────────────────────────────┘
```

---

## 4. Architectural Analysis of the Discrepancy

### 4.1 Why Did the Count Grow from 95 to 250?
When `06-02` §2 was initially authored, the programme comprised 30 core modules. As the enterprise architecture expanded to 67 modules and 12 portals to address enterprise multi-site operations, brand warranty claims at scale, and Bangladesh statutory compliance (NBR VAT Act 2012, PDPA 2026), module authors required fine-grained engineering telemetry. 

Instead of waiting for quarterly Steering Committee updates to `06-02`, module authors followed the metric partitioning rule in `RP-001` §4.3:
- Range `KPI-001` to `KPI-095`: Reserved for the **Board-Level Business Objective (BO) Register**.
- Range `KPI-110` to `KPI-305`: Allocated for **Module-Level Operational Telemetry**.

### 4.2 Why Are 41 Registered KPIs Uncited in Module Text?
The 41 registered KPIs that do not appear verbatim in module specification bodies represent **cross-cutting platform and executive outcomes** (e.g., `KPI-085` System Uptime, `KPI-095` Overall Automation Rate, `KPI-058` Tax Compliance Findings, `KPI-031` Negative Margin Contracts). These are calculated by the M25 analytical dimensional warehouse by joining facts across multiple modules rather than by any single module's isolated workflow.

---

## 5. Governance Action & Resolution

1. **Board Register Protection (`BMR-17`)**:
   `06-02` §2 remains the exclusive source of truth for benefits realization and wave gate certification.
2. **Operational Telemetry Ratification**:
   The 196 module operational metrics (`KPI-110`…`KPI-305`) are classified as Tier-2 Telemetry in the M62 Data Catalogue (`fix.data.entity`), visible in Grafana/Superset diagnostic dashboards without burdening Board governance.
3. **M25 Analytics Surfacing (`DoD-09`)**:
   `services/bi-warehouse/kpi-register.json` and the `/analytics/kpis/register` API endpoint surface all 95 registered KPIs with explicit owner, baseline, W4/W8 target, source fact table, and calculation formula.
