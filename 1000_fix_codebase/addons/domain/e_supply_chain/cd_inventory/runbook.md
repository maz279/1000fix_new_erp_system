# Operational Runbook: 1000FiX Spare Parts & Inventory Management (cd_inventory)

**Document**: `addons/domain/e_supply_chain/cd_inventory/runbook.md`  
**Standard**: DoD-11 (Per-Module Operational Runbook), AR-007 §3.1  
**Module ID**: `M15` | **CD ID**: `CD-M15-01` | **Wave**: `W2`  
**Category**: `Inventory/Logistics` | **Layer**: `L3 Domain Extension`  
**Owner Squad**: `Supply Chain`  
**Version**: `19.0.1.0.0` | **License**: `LGPL-3`  
**Compliance Status**: VERIFIED (DoD-11 Compliant)  

---

## 1. Operational Overview & Core Responsibilities

The `cd_inventory` module (1000FiX Spare Parts & Inventory Management) is an integral component of the 1000FiX ERP platform.

### 1.1 Business Scope
M15 Wave-2 slice: multi-location on fix.branch, van stock, barcode/QR scan-to-consume, replenishment rules, M43 seam (CD-M15-01)

CD-M15-01: Spare Parts & Inventory Management.

Features:
- Multi-location inventory mapped to fix.branch / operating units
- Specialized Technician Van Stock location type
- Spare parts catalog with device compatibility and warranty tracking
- Barcode and QR code scan-to-consume engine on repair jobs
- Automated replenishment alerts and reorder rules with M43 forecasting seam
- GV-005 suspense valuation ledger pending Wave-3 GL cutover
- Transactional outbox events (stock.consumed, stock.returned, reorder.triggered, van.reconciled)

### 1.2 Critical Business Journeys Served
This module participates in and provides operational support for the following core enterprise journeys:
- **Primary Domain**: Inventory > Logistics
- **Service Tier**: T3
- **Transactional Support**: Provides backend data processing, business logic validation, state machine transitions, and audit trail enforcement for after-sales service operations across all 51 nationwide branch locations.

---

## 2. Module Topology & Dependencies

### 2.1 Upstream Dependencies (Declared in Manifest)
The module depends on the following prerequisite modules:
- `base`
- `mail`
- `stock`
- `cd_entity_config`
- `cd_wms_structure`
- `cd_device_registry`
- `cd_catalogue`
- `cd_event_outbox`

### 2.2 Event Bus Pub/Sub Contracts
- **Emitted Events**: Domain lifecycle state changes are published to `cd_event_outbox` for asynchronous consumption by downstream portals and streaming analytics.
- **Subscribed Events**: Subscribes to party/customer status updates, device verification tokens, and tenant configuration broadcast signals.

---

## 3. Data Models & Database Schemas

### 3.1 Primary Models Declared
- **Model**: `fix.graded.stock` (Table: `fix_graded_stock`)
  - *Description*: Graded & Refurbished Inventory
  - *Source File*: `models/fix_graded_stock.py`
- **Model**: `fix.reorder.rule` (Table: `fix_reorder_rule`)
  - *Description*: Spare Part Reorder Rule
  - *Source File*: `models/fix_reorder_rule.py`
- **Model**: `fix.spare.part` (Table: `fix_spare_part`)
  - *Description*: Spare Part & Component
  - *Source File*: `models/fix_spare_part.py`
- **Model**: `fix.stock.consumption` (Table: `fix_stock_consumption`)
  - *Description*: Job Parts Consumption
  - *Source File*: `models/fix_stock_consumption.py`
- **Model**: `fix.stock.location` (Table: `fix_stock_location`)
  - *Description*: Inventory Location & Van Stock
  - *Source File*: `models/fix_stock_location.py`
- **Model**: `fix.inventory.valuation.suspense` (Table: `fix_inventory_valuation_suspense`)
  - *Description*: Inventory Valuation Suspense Entry
  - *Source File*: `models/fix_valuation_suspense.py`

### 3.2 Data Residency & Classification (PDPA / Statutory Compliance)
- **Classification**: All tables storing customer identifiers, device serial numbers, or financial transactions are governed under Bangladesh Personal Data Protection statutory residency requirements.
- **Storage Tier**: PostgreSQL Primary Relational Storage (Sovereign onshore datacenter).
- **Audit Logging**: Chatter mixins (`mail.thread`, `mail.activity.mixin`) track field mutations with user attribution, timestamps, and previous/new values.

---

## 4. Routine Operations & Administrative Tasks

### 4.1 Scheduled & Maintenance Actions
- **Nightly Reconciliation**: Automated integrity checks run via standard cron schedules to detect orphan records or stalled state transactions.
- **Data Retention & Pruning**: Outbox payloads and temporary staging buffers are pruned according to data governance retention windows (90-day hot retention).

### 4.1a Inventory controls (A06 remediation, Nov 2026)
- **Roles** (`cd_wms_structure`): Storekeeper and Warehouse Operator (admin is a member);
  Inventory Controller ships EMPTY and is the second person on every inventory approval
  (count variances, write-offs, van discrepancies, transfers, class changes, RTV, bin unblock,
  part status / standard cost). A controller never approves what they raised, counted,
  quarantined or blocked.
- **Configuration** (`ir.config_parameter`, default `0` = every case needs approval):
  `cd_inventory.count_variance_tolerance_pct`, `cd_inventory.van_variance_tolerance_pct`,
  `cd_inventory.writeoff_approval_threshold` (BDT), `cd_inventory.transfer_approval_threshold` (BDT).
- **Cron**: `M15: replenishment sweep (reorder rules)` runs `check_replenishment_alerts()` hourly.
- **Valuation suspense**: system-written only; reconciled only by the M19 cutover
  (`cd_gl_ext` period close). `fix.inventory.valuation.suspense.get_baseline_integrity()` and the
  workspace report *Valuation Suspense Integrity* show a duplicated initial-count baseline and the
  gap to the on-hand value. They change nothing: removing duplicates is a Finance decision.
- **Ledger**: `fix.stock.onhand` is written only by movements; stock has a status
  (unrestricted / quarantine / in transit / staged) and only unrestricted stock is reserved or
  issued. Receipts value at weighted-average cost.

### 4.2 Standard Operational Procedures
1. **Module Deployment**:
   ```bash
   python3 -m odoo -u cd_inventory -d 1000fix_prod --stop-after-init
   ```
2. **Configuration Verification**:
   - Verify access control rights in `security/ir.model.access.csv`.
   - Ensure company and operating unit isolation policies (`res.company`, `fix.operating.unit`) are active.

---

## 5. Troubleshooting & Diagnostic Playbooks

### 5.1 Common Failure Modes & Symptoms
- **Stalled State Transitions**: Records remaining in processing/pending states without advancing.
- **Permission Denied / Access Errors**: Non-admin users unable to read or write specific records. Verify group membership and multi-company rules.
- **Constraint Violations**: Duplicate external IDs, missing required relational links (e.g. `partner_id`, `company_id`).

### 5.2 Diagnostic SQL Queries
Check for inconsistent or locked records:
```sql
-- Count total active records
SELECT count(*) FROM fix_graded_stock WHERE active = true;

-- Inspect recent state transitions (last 24 hours)
SELECT id, create_date, write_date, state 
FROM fix_graded_stock 
WHERE write_date >= NOW() - INTERVAL '24 hours' 
ORDER BY write_date DESC LIMIT 50;
```

### 5.3 Incident Severity & Escalation Paths
- **Severity 1 (Critical Outage)**: System unable to process records or database locks. Escalate to Lead Systems Architect and On-Call Operations Lead.
- **Severity 2 (Degraded Performance)**: Specific actions exceeding 200ms latency budget. File ticket with Squad `Supply Chain`.
- **Severity 3 (Minor Defect / Cosmetic)**: Route to normal sprint backlog.

---

## 6. Disaster Recovery & Data Remediation

### 6.1 Idempotent Repair & Data Re-sync
In the event of network disruption or interrupted transactions:
1. Identify uncommitted or faulted IDs using the diagnostic query in §5.2.
2. Trigger the idempotent re-sync routine or re-run the module migration runner.
3. Verify event outbox relay queues are drained.

### 6.2 Module Downgrade & Rollback Precautions
- **Rollback Policy**: Schema migrations adding columns are non-destructive (backward-compatible). Never execute `DROP COLUMN` in production without prior ARB sign-off and complete database backup.

---

## 7. Telemetry, Observability & SLA Thresholds

### 7.1 Prometheus & Log Metric Probes
- **Latency Budget**: Transactional write latency p95 <= 200 ms; read queries p95 <= 50 ms.
- **Correlation ID Tracking**: All incoming portal or API calls propagate `X-Correlation-ID` header into PostgreSQL session variables and application log output.

### 7.2 Health Probes
```bash
# Verify module load and test execution clean
py -3.12 -m pytest addons/domain/e_supply_chain/cd_inventory -q -o 'addopts='
```

---

*Last Updated: 2026-10-20 · Approved by: 1000FiX Architecture Review Board (ARB)*
