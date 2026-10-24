# Operational Runbook: 1000FiX Time & Attendance (cd_attendance)

**Document**: `addons/domain/h_people/cd_attendance/runbook.md`  
**Standard**: DoD-11 (Per-Module Operational Runbook), AR-007 §3.1  
**Module ID**: `M55` | **CD ID**: `CD-M55-01` | **Wave**: `W5`  
**Category**: `Human Resources/Attendance` | **Layer**: `L3 Domain Extension`  
**Owner Squad**: `People`  
**Version**: `19.0.0.1.0` | **License**: `LGPL-3`  
**Compliance Status**: VERIFIED (DoD-11 Compliant)  

---

## 1. Operational Overview & Core Responsibilities

The `cd_attendance` module (1000FiX Time & Attendance) is an integral component of the 1000FiX ERP platform.

### 1.1 Business Scope
M55: attendance records, shifts/rosters, working-time compliance, the attendance lock payroll depends on (CD-M55-nn)

CD-M55-01 (P08-M02) — Wave 5 attendance:

- fix.attendance.record — check-in/out with source (biometric INT-041,
  mobile geofenced P02 flow, manual); worked-hours compute; records are
  IMMUTABLE once their period is locked
- fix.shift.template / fix.roster.slot — shift and roster management;
  the roster CLOSES the M02 -> M55 availability stub (P05-M03-T05): the
  W2 seam returned "available within working calendar"; dispatch now asks
  the ROSTER
- fix.attendance.lock — the monthly lock that payroll depends on
  (P08-M02-T05): journey 13 runs attendance lock -> calculation ->
  approval -> BEFTN -> payslips -> posting
- working-time compliance (SC-008): daily 8h standard, OT hours flagged
  beyond it, weekly rest-day verification
- biometric templates are S3 residency data: only the device reference
  lands here; the template itself routes through fix.identity.document

### 1.2 Critical Business Journeys Served
This module participates in and provides operational support for the following core enterprise journeys:
- **Primary Domain**: Human Resources > Attendance
- **Service Tier**: T8
- **Transactional Support**: Provides backend data processing, business logic validation, state machine transitions, and audit trail enforcement for after-sales service operations across all 51 nationwide branch locations.

---

## 2. Module Topology & Dependencies

### 2.1 Upstream Dependencies (Declared in Manifest)
The module depends on the following prerequisite modules:
- `base`
- `mail`
- `hr_attendance`
- `cd_entity_config`
- `cd_hr_core`
- `cd_employee_core`
- `cd_event_outbox`
- `cd_service_order`

### 2.2 Event Bus Pub/Sub Contracts
- **Emitted Events**: Domain lifecycle state changes are published to `cd_event_outbox` for asynchronous consumption by downstream portals and streaming analytics.
- **Subscribed Events**: Subscribes to party/customer status updates, device verification tokens, and tenant configuration broadcast signals.

---

## 3. Data Models & Database Schemas

### 3.1 Primary Models Declared
- **Model**: `fix.shift.template` (Table: `fix_shift_template`)
  - *Description*: Shift Template
  - *Source File*: `models/fix_attendance.py`
- **Model**: `fix.roster.slot` (Table: `fix_roster_slot`)
  - *Description*: Roster Slot
  - *Source File*: `models/fix_attendance.py`
- **Model**: `display_label` (Table: `display_label`)
  - *Description*: INT-041 Biometric Attendance Device
  - *Source File*: `models/fix_attendance.py`
- **Model**: `fix.biometric.device` (Table: `fix_biometric_device`)
  - *Description*: Attendance Record
  - *Source File*: `models/fix_attendance.py`
- **Model**: `fix.attendance.record` (Table: `fix_attendance_record`)
  - *Description*: Attendance Lock
  - *Source File*: `models/fix_attendance.py`
- **Model**: `display_label` (Table: `display_label`)
  - *Description*: display_label
  - *Source File*: `models/fix_attendance.py`
- **Model**: `fix.attendance.lock` (Table: `fix_attendance_lock`)
  - *Description*: fix.attendance.lock
  - *Source File*: `models/fix_attendance.py`

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
   python3 -m odoo -u cd_attendance -d 1000fix_prod --stop-after-init
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
SELECT count(*) FROM fix_shift_template WHERE active = true;

-- Inspect recent state transitions (last 24 hours)
SELECT id, create_date, write_date, state 
FROM fix_shift_template 
WHERE write_date >= NOW() - INTERVAL '24 hours' 
ORDER BY write_date DESC LIMIT 50;
```

### 5.3 Incident Severity & Escalation Paths
- **Severity 1 (Critical Outage)**: System unable to process records or database locks. Escalate to Lead Systems Architect and On-Call Operations Lead.
- **Severity 2 (Degraded Performance)**: Specific actions exceeding 200ms latency budget. File ticket with Squad `People`.
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
py -3.12 -m pytest addons/domain/h_people/cd_attendance -q -o 'addopts='
```

---

*Last Updated: 2026-10-20 · Approved by: 1000FiX Architecture Review Board (ARB)*
