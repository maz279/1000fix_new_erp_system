# Operational Runbook: 1000FiX Payroll BD (cd_payroll_bd)

**Document**: `addons/domain/h_people/cd_payroll_bd/runbook.md`  
**Standard**: DoD-11 (Per-Module Operational Runbook), AR-007 §3.1  
**Module ID**: `M56` | **CD ID**: `CD-M56-01` | **Wave**: `W5`  
**Category**: `Human Resources/Payroll` | **Layer**: `L3 Domain Extension`  
**Owner Squad**: `People`  
**Version**: `19.0.0.1.0` | **License**: `LGPL-3`  
**Compliance Status**: VERIFIED (DoD-11 Compliant)  

---

## 1. Operational Overview & Core Responsibilities

The `cd_payroll_bd` module (1000FiX Payroll BD) is an integral component of the 1000FiX ERP platform.

### 1.1 Business Scope
M56: payroll engine (FY2026-27 slabs), PF/gratuity Act-2026, BEFTN batch calendar, Bengali payslips, GL posting (CD-M56-nn)

CD-M56-01 (P08-M03) — the only P0 module in Category H:

- fix.payroll.period — journey 13's spine: draft -> attendance_locked ->
  calculated -> approved -> paid -> posted. Calculation is REFUSED until
  the month's attendance lock is locked (P08-M02-T05)
- fix.payslip — every line computed by libs/py/payroll_engine (the ONLY
  calculation authority, DoD-03 100% covered): FY 2026-27 income-tax
  slabs (375k threshold; 10/15/20/25/30), provident fund wings,
  2x overtime; gratuity + resignation compensation per the Labour
  (Amendment) Act 2026 on separation
- fix.beftn.batch — INT-005 with the batch model: settlement date from
  the engine's cut-off calendar (16:00, Fri/Sat/holiday -> next working
  day, Sunday-Thursday week). A run that misses the cut-off pays late —
  modelled, not hoped away
- payslip.pdf — the Bengali payslip (TR-07's named failure mode)
- GL posting to M19 on approval; approval SoD negative-tested

### 1.2 Critical Business Journeys Served
This module participates in and provides operational support for the following core enterprise journeys:
- **Primary Domain**: Human Resources > Payroll
- **Service Tier**: T8
- **Transactional Support**: Provides backend data processing, business logic validation, state machine transitions, and audit trail enforcement for after-sales service operations across all 51 nationwide branch locations.

---

## 2. Module Topology & Dependencies

### 2.1 Upstream Dependencies (Declared in Manifest)
The module depends on the following prerequisite modules:
- `base`
- `mail`
- `cd_entity_config`
- `cd_hr_core`
- `cd_attendance`
- `cd_gl_ext`
- `cd_event_outbox`

### 2.2 Event Bus Pub/Sub Contracts
- **Emitted Events**: Domain lifecycle state changes are published to `cd_event_outbox` for asynchronous consumption by downstream portals and streaming analytics.
- **Subscribed Events**: Subscribes to party/customer status updates, device verification tokens, and tenant configuration broadcast signals.

---

## 3. Data Models & Database Schemas

### 3.1 Primary Models Declared
- **Model**: `fix.payroll.period` (Table: `fix_payroll_period`)
  - *Description*: Payroll Period
  - *Source File*: `models/fix_payroll.py`
- **Model**: `fix.payslip` (Table: `fix_payslip`)
  - *Description*: Payslip
  - *Source File*: `models/fix_payroll.py`
- **Model**: `fix.beftn.batch` (Table: `fix_beftn_batch`)
  - *Description*: BEFTN Batch
  - *Source File*: `models/fix_payroll.py`

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
   python3 -m odoo -u cd_payroll_bd -d 1000fix_prod --stop-after-init
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
SELECT count(*) FROM fix_payroll_period WHERE active = true;

-- Inspect recent state transitions (last 24 hours)
SELECT id, create_date, write_date, state 
FROM fix_payroll_period 
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
py -3.12 -m pytest addons/domain/h_people/cd_payroll_bd -q -o 'addopts='
```

---

*Last Updated: 2026-10-20 · Approved by: 1000FiX Architecture Review Board (ARB)*
