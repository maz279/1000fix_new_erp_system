# Operational Runbook: 1000FiX Service Order (cd_service_order)

**Document**: `addons/domain/a_service_delivery/cd_service_order/runbook.md`  
**Standard**: DoD-11 (Per-Module Operational Runbook), AR-007 §3.1  
**Module ID**: `M01` | **CD ID**: `CD-M01-01` | **Wave**: `W1`  
**Category**: `Service Delivery/Orders` | **Layer**: `L3 Domain Extension`  
**Owner Squad**: `Service Delivery`  
**Version**: `19.0.1.0.0` | **License**: `LGPL-3`  
**Compliance Status**: VERIFIED (DoD-11 Compliant)  

---

## 1. Operational Overview & Core Responsibilities

The `cd_service_order` module (1000FiX Service Order) is an integral component of the 1000FiX ERP platform.

### 1.1 Business Scope
Service order/work order core with full state machine, SLA clocks, diagnostic tree, estimate/approval, QC checklist (M01-core)

CD-M01-nn: Service Request & Order Management core (M01, W1 slice).

The largest single module in the programme. AS-06: state transitions declared
in one place per model (DP-01). SLA computation lives in services/ so it is
unit-testable without a database (AR-007 section 3.1).

### 1.2 Critical Business Journeys Served
This module participates in and provides operational support for the following core enterprise journeys:
- **Primary Domain**: Service Delivery > Orders
- **Service Tier**: T3
- **Transactional Support**: Provides backend data processing, business logic validation, state machine transitions, and audit trail enforcement for after-sales service operations across all 51 nationwide branch locations.

---

## 2. Module Topology & Dependencies

### 2.1 Upstream Dependencies (Declared in Manifest)
The module depends on the following prerequisite modules:
- `base`
- `mail`
- `cd_entity_config`
- `cd_catalogue`
- `cd_party_master`
- `cd_device_registry`
- `cd_document_core`
- `cd_event_outbox`
- `cd_employee_core`

### 2.2 Event Bus Pub/Sub Contracts
- **Emitted Events**: Domain lifecycle state changes are published to `cd_event_outbox` for asynchronous consumption by downstream portals and streaming analytics.
- **Subscribed Events**: Subscribes to party/customer status updates, device verification tokens, and tenant configuration broadcast signals.

---

## 3. Data Models & Database Schemas

### 3.1 Primary Models Declared
- **Model**: `fix.estimate` (Table: `fix_estimate`)
  - *Description*: Repair Estimate
  - *Source File*: `models/fix_estimate.py`
- **Model**: `fix.estimate.line` (Table: `fix_estimate_line`)
  - *Description*: Estimate Line
  - *Source File*: `models/fix_estimate.py`
- **Model**: `fix.qc.checklist` (Table: `fix_qc_checklist`)
  - *Description*: QC Checklist
  - *Source File*: `models/fix_qc_checklist.py`
- **Model**: `fix.qc.item` (Table: `fix_qc_item`)
  - *Description*: QC Checklist Item
  - *Source File*: `models/fix_qc_checklist.py`
- **Model**: `fix.service.order` (Table: `fix_service_order`)
  - *Description*: Service Order
  - *Source File*: `models/fix_service_order.py`
- **Model**: `fix.service.order.fault` (Table: `fix_service_order_fault`)
  - *Description*: Service Order Fault Line
  - *Source File*: `models/fix_service_order_fault.py`
- **Model**: `fix.sla.policy` (Table: `fix_sla_policy`)
  - *Description*: SLA Policy
  - *Source File*: `models/fix_sla_policy.py`
- **Model**: `fix.diagnostic.node` (Table: `fix_diagnostic_node`)
  - *Description*: Diagnostic Tree Node
  - *Source File*: `models/fix_sla_policy.py`
- **Model**: `fix.work.order` (Table: `fix_work_order`)
  - *Description*: Work Order
  - *Source File*: `models/fix_work_order.py`
- **Model**: `fix.work.order.part` (Table: `fix_work_order_part`)
  - *Description*: Work Order Part
  - *Source File*: `models/fix_work_order.py`

### 3.2 Data Residency & Classification (PDPA / Statutory Compliance)
- **Classification**: All tables storing customer identifiers, device serial numbers, or financial transactions are governed under Bangladesh Personal Data Protection statutory residency requirements.
- **Storage Tier**: PostgreSQL Primary Relational Storage (Sovereign onshore datacenter).
- **Audit Logging**: Chatter mixins (`mail.thread`, `mail.activity.mixin`) track field mutations with user attribution, timestamps, and previous/new values.

---

## 4. Routine Operations & Administrative Tasks

### 4.1 Scheduled & Maintenance Actions
- **Nightly Reconciliation**: Automated integrity checks run via standard cron schedules to detect orphan records or stalled state transactions.
- **Data Retention & Pruning**: Outbox payloads and temporary staging buffers are pruned according to data governance retention windows (90-day hot retention).

### 4.2 Standard Operational Procedures
1. **Module Deployment**:
   ```bash
   python3 -m odoo -u cd_service_order -d 1000fix_prod --stop-after-init
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
SELECT count(*) FROM fix_estimate WHERE active = true;

-- Inspect recent state transitions (last 24 hours)
SELECT id, create_date, write_date, state 
FROM fix_estimate 
WHERE write_date >= NOW() - INTERVAL '24 hours' 
ORDER BY write_date DESC LIMIT 50;
```

### 5.3 Incident Severity & Escalation Paths
- **Severity 1 (Critical Outage)**: System unable to process records or database locks. Escalate to Lead Systems Architect and On-Call Operations Lead.
- **Severity 2 (Degraded Performance)**: Specific actions exceeding 200ms latency budget. File ticket with Squad `Service Delivery`.
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
py -3.12 -m pytest addons/domain/a_service_delivery/cd_service_order -q -o 'addopts='
```

---

*Last Updated: 2026-10-20 · Approved by: 1000FiX Architecture Review Board (ARB)*
