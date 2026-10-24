# Operational Runbook: 1000FiX Quality Management (cd_qms_process)

**Document**: `addons/domain/i_governance/cd_qms_process/runbook.md`  
**Standard**: DoD-11 (Per-Module Operational Runbook), AR-007 §3.1  
**Module ID**: `M23` | **CD ID**: `CD-M23-01` | **Wave**: `W5`  
**Category**: `Quality/Management System` | **Layer**: `L3 Domain Extension`  
**Owner Squad**: `Quality`  
**Version**: `19.0.0.1.0` | **License**: `LGPL-3`  
**Compliance Status**: VERIFIED (DoD-11 Compliant)  

---

## 1. Operational Overview & Core Responsibilities

The `cd_qms_process` module (1000FiX Quality Management) is an integral component of the 1000FiX ERP platform.

### 1.1 Business Scope
M23: NCR, root-cause/CAPA, internal audit programme (ISO 9001:2015), QC checklist takeover — closes the M31/M34/M42 -> M23 stubs (CD-M23-nn)

CD-M23-01 (P08-M06) — the quality estate completes on the OCA
management-system patterns:

- fix.ncr — non-conformance records from ANY source (service order, QC
  checklist, complaint (M34 -> M23 STUB CLOSED), supplier (M42),
  internal audit); journey 14's middle
- fix.capa — root cause and CORRECTIVE/PREVENTIVE action with
  verification and closure; a CRITICAL NCR closes only through verified
  CAPA
- fix.qc.checklist EXTENSION — QC ownership transfers from M01 to M23
  (P08-M06-T04, AR-005 exactly-one-owner): the failed checklist now
  RAISES an NCR instead of a string; the M31 -> M23 stub closes
- fix.internal.audit — the ISO 9001:2015 audit programme (CON-11: zero
  major non-conformances traced to systems at surveillance); consumed
  by the P11 field-auditor surface (audit execution with offline
  capture fields)
- fix.complaint EXTENSION — the M34 -> M23 stubs close: ncr_stub_ref /
  capa_stub_ref become real relations; action_raise_ncr creates the NCR

### 1.2 Critical Business Journeys Served
This module participates in and provides operational support for the following core enterprise journeys:
- **Primary Domain**: Quality > Management System
- **Service Tier**: T8
- **Transactional Support**: Provides backend data processing, business logic validation, state machine transitions, and audit trail enforcement for after-sales service operations across all 51 nationwide branch locations.

---

## 2. Module Topology & Dependencies

### 2.1 Upstream Dependencies (Declared in Manifest)
The module depends on the following prerequisite modules:
- `base`
- `mail`
- `cd_entity_config`
- `cd_event_outbox`
- `cd_service_order`
- `cd_cx_feedback`

### 2.2 Event Bus Pub/Sub Contracts
- **Emitted Events**: Domain lifecycle state changes are published to `cd_event_outbox` for asynchronous consumption by downstream portals and streaming analytics.
- **Subscribed Events**: Subscribes to party/customer status updates, device verification tokens, and tenant configuration broadcast signals.

---

## 3. Data Models & Database Schemas

### 3.1 Primary Models Declared
- **Model**: `fix.ncr` (Table: `fix_ncr`)
  - *Description*: Non-Conformance Record
  - *Source File*: `models/fix_qms.py`
- **Model**: `fix.capa` (Table: `fix_capa`)
  - *Description*: CAPA
  - *Source File*: `models/fix_qms.py`
- **Model**: `fix.internal.audit` (Table: `fix_internal_audit`)
  - *Description*: Internal Audit
  - *Source File*: `models/fix_qms.py`

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
   python3 -m odoo -u cd_qms_process -d 1000fix_prod --stop-after-init
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
SELECT count(*) FROM fix_ncr WHERE active = true;

-- Inspect recent state transitions (last 24 hours)
SELECT id, create_date, write_date, state 
FROM fix_ncr 
WHERE write_date >= NOW() - INTERVAL '24 hours' 
ORDER BY write_date DESC LIMIT 50;
```

### 5.3 Incident Severity & Escalation Paths
- **Severity 1 (Critical Outage)**: System unable to process records or database locks. Escalate to Lead Systems Architect and On-Call Operations Lead.
- **Severity 2 (Degraded Performance)**: Specific actions exceeding 200ms latency budget. File ticket with Squad `Quality`.
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
py -3.12 -m pytest addons/domain/i_governance/cd_qms_process -q -o 'addopts='
```

---

*Last Updated: 2026-10-20 · Approved by: 1000FiX Architecture Review Board (ARB)*
