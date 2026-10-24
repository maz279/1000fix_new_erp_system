# RB-53 — Master Production Cutover Runbook
## 1000FiX ERP System v2.0 · Category 12 (Release, Deployment & Transition) · PE-001 / TSS §21.3 Conformance

| Metadata | Details |
|---|---|
| **Runbook ID** | `RB-53-PRODUCTION-CUTOVER-MASTER` |
| **Document Version** | 1.0 (Production Go-Live Baseline) |
| **Governance Standard** | ISO 9001:2015 §8.5 · PE-001 §6.2 · TSS §21.3 · MIG-01..08 · GV-003 |
| **Scheduled Window** | Saturday 22:00 BST to Sunday 06:00 BST (8h Maintenance Window) |
| **Command Center** | 24/7 Operations War Room (HQ 5th Floor / Video Bridge / Telegram Incident Channel) |
| **Incident Commander** | Programme Delivery Director (Engr. Rafiqul Islam) |
| **Technical Lead** | Principal Systems Architect (Dr. A. K. M. Shamsuddin) |
| **Exit Criterion** | Milestone R11-M01 Task T01 — Completed dry-walkthrough, all checklists signed |

---

### 1. Command Structure & Roles

During the cutover execution window, operational hierarchy is governed by strict Incident Command System (ICS) protocols:

| Role | Primary Responsible | Authority / Responsibilities |
|---|---|---|
| **Incident Commander (IC)** | Engr. Rafiqul Islam | Overall cutover authority; declares Go/No-Go and Rollback. |
| **Technical Migration Lead** | Dr. A. K. M. Shamsuddin | Coordinates database migration pipeline, ETL execution, and service deployment. |
| **Lead Database SRE** | Kazi Moniruzzaman | Controls PostgreSQL primary, standby replication, WAL streaming, and backup snapshots. |
| **QA & Smoke Gate Lead** | Farhana Sultana | Executes and signs off 15/15 critical user journey smoke tests. |
| **Business Reconciliation Lead**| Mohammad Ali | Validates MIG-02 control totals and signs off source cutover. |
| **Security & Compliance Monitor**| Tariqul Hassan, CISSP | Monitors sovereign Z4 residency, Vault token leasing, and zero plaintext PII leaks. |
| **Regional Operations Coordinator**| Anisur Rahman | Coordinates 53 branch connectivity checks and super-user network across 8 divisions. |

---

### 2. Cutover Timeline & Phase Ladder

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          CUTOVER TIMELINE PHASES                                │
├───────────┬─────────────────────────────────────────────────────────────────────┤
│ T-48h     │ Legacy Source Schema Freeze (No master data changes in legacy DBs)  │
│ T-4h      │ Standby Replication Lag Check (WAL lag < 10s confirmed)             │
│ T-2h      │ Operations War Room Assembled & Communications Broadcast            │
│ T-0h      │ Maintenance Landing Page Activated; Legacy Read-Only Lock Engaged    │
│ T+0.5h    │ Final Incremental Delta Extract Captured (All 48 Sources)           │
│ T+1.5h    │ Production Database Ingestion & Transformation Sequence Executed    │
│ T+2.0h    │ MIG-02 Control Totals Reconciled (100.00% precision target)         │
│ T+2.5h    │ Automated Smoke Test Suite Executed (15/15 Prod-Shape Journeys)     │
│ T+3.0h    │ 53/53 Branch Heartbeat Handshake & Terminal Connectivity Verified   │
│ T+3.5h    │ Final Business Sign-off Executed by IC & Steering Committee         │
│ T+4.0h    │ DNS Records Cut Over; Maintenance Mode Disengaged; Live Traffic ON  │
│ T+4.0h+   │ Hypercare Phase SV-004 Formally Commences (24/7 Monitoring)         │
└───────────┴─────────────────────────────────────────────────────────────────────┘
```

---

### 3. Topological Source Load Ordering (48 Legacy Sources)

Migration follows a strict directed acyclic graph (DAG) to satisfy referential integrity:

1. **Tier 1: Master Geographies & Organizational Entities (ETL-3)**
   - Bangladesh 8 divisions, 64 districts, 495 upazilas, postal codes.
   - Operating units, 53 service centre branches, warehouses, technician bays.
2. **Tier 2: Customer & Partner Registry with M64 Deduplication (ETL-1)**
   - WooCommerce, WordPress store customer profiles, corporate client accounts.
   - NID/TIN tokens extracted, encrypted, and routed to Z4 sovereign vault.
3. **Tier 3: Device Master & Warranty Catalogs (ETL-2)**
   - 2,840 serialized device records, IMEI/Serial registry, brand warranty rules.
4. **Tier 4: Human Resources & Staff Credentials (ETL-4)**
   - 380 employee profiles, department mappings, role-based RBAC key assignments.
5. **Tier 5: Inventory Opening Balances & Stock Lots (ETL-5)**
   - Central Dhaka warehouse, Chattogram regional hub, and 53 branch stock lots.
   - Valuation: Strict FIFO / Moving Average Costing parity check.
6. **Tier 6: Active Workshop WIP & Repair Tickets (ETL-6)**
   - In-flight repair tickets, technician assignment history, parts consumption ledgers.
7. **Tier 7: Financial Subledgers & Trial Balances (ETL-7)**
   - Opening accounts receivable, accounts payable, VAT control accounts.

---

### 4. Automated Smoke Gates (15/15 Critical Journeys)

Before live traffic is unblocked, the automated smoke harness (`tooling/e2e`) runs against the production cluster:

| Journey | Description | Verification Criterion |
|---|---|---|
| `J01` | Customer Online Booking | Pickup request created, SMS tracking URL issued |
| `J02` | Front-Desk Walk-in Intake | Device triage logged, deposit invoice printed |
| `J03` | Pick & Drop Logistics | Rider custody OTP verified, transit stage logged |
| `J04` | Brand Warranty Claim | Vendor RMA ticket generated with serial trace |
| `J05` | Corporate AMC Bulk Service | Bulk repair batch accepted against active contract |
| `J06` | MSP SNMP Alert to Ticket | Automated telemetry creates high-priority job |
| `J07` | Rental / Loaner Device | Device loaned with deposit, agreement PDF stamped |
| `J08` | E-Waste DOD Wipe & Certificate| Storage sanitized, cryptographic certificate signed |
| `J09` | Trade-in Instant Valuation | Condition checklist generates credit voucher |
| `J10` | Marketplace Seller Order | Spare part order routed to verified merchant |
| `J11` | Cleanroom Data Recovery | Chain of custody signed, forensic scan logged |
| `J12` | Procure-to-Pay 3-Way Match | PO, goods receipt, and vendor bill match 100% |
| `J13` | Monthly Payroll Run | Gross-to-net calculated with statutory TDS |
| `J14` | Customer Grievance & CAPA | Quality non-conformance routed to root cause |
| `J15` | Month-End Trial Balance | Debit = Credit, Mushak 9.1 VAT report clean |

---

### 5. Hard Rollback Triggers & Abort Protocol (MG-007)

If any of the following four conditions occur, the Incident Commander orders an **immediate, irreversible abort**:

```
[TRIGGER 1] Outage duration > 4h 00m
[TRIGGER 2] Financial or inventory balance reconciliation variance > 0.00%
[TRIGGER 3] Workshop repair intake fails on 2 or more service centres
[TRIGGER 4] Any plaintext sovereign PII detected outside Z4 vault
```

#### Rollback Execution Steps (Target Duration ≤ 5 Minutes):
1. **Command**: `python migrations/rollback.py --profile prod`
2. **Database Reversal**: Deletes all records bearing legacy prefixes (`BR:PILOT:%`, `CUST:WP_STORE:%`, `DEV:ASSET_SHEET:%`, `EMP:PAYROLL_2026:%`, `INV:LOT:%`, `WIP:TICKET:%`).
3. **Z4 Shredding**: Cryptographic erasure of transient encryption keys for migrated PII.
4. **Traffic Re-routing**: Nginx reverse proxy reverts upstream DNS pointers to legacy servers.
5. **Post-Mortem**: War room remains convened to collect error diagnostics and log dumps.
