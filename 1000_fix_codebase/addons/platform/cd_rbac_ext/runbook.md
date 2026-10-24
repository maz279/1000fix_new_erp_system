# Operational Runbook: 1000FiX RBAC Extension (cd_rbac_ext)

**Document**: `addons/platform/cd_rbac_ext/runbook.md`  
**Standard**: DoD-11 (Per-Module Operational Runbook), AR-007 §3.1  
**Module ID**: `M29` | **CD ID**: `CD-M29-01` | **Wave**: `W1`  
**Category**: `Platform/Security` | **Layer**: `L2 Core Platform`  
**Owner Squad**: `Platform`  
**Version**: `19.0.1.0.0` | **License**: `LGPL-3`  
**Compliance Status**: VERIFIED (DoD-11 Compliant)  

---

## 1. Operational Overview & Core Responsibilities

The `cd_rbac_ext` module (1000FiX RBAC Extension) is an integral component of the 1000FiX ERP platform.

### 1.1 Business Scope
Field-level permissions, six isolation tiers (T0-T5), 53 roles, 61 SoD controls, OIDC federation

CD-M29-nn: the M29 RBAC extension.

Owns:
- fix.role (53 roles per the reconciled register, mapped to Keycloak realm roles)
- fix.isolation.tier (T0 public ... T5 residency-classified, as record rules)
- fix.sod.control (61 segregation-of-duties controls from SP-006)
- fix.field.rule (the field-level permission engine — security/<module>_field_rules.xml)
- fix.access.log (privileged session recording, NFR-070/SC-010)

### 1.2 Critical Business Journeys Served
This module participates in and provides operational support for the following core enterprise journeys:
- **Primary Domain**: Platform > Security
- **Service Tier**: T0
- **Transactional Support**: Provides backend data processing, business logic validation, state machine transitions, and audit trail enforcement for after-sales service operations across all 51 nationwide branch locations.

---

## 2. Module Topology & Dependencies

### 2.1 Upstream Dependencies (Declared in Manifest)
The module depends on the following prerequisite modules:
- `base`
- `mail`
- `cd_entity_config`

### 2.2 Event Bus Pub/Sub Contracts
- **Emitted Events**: Domain lifecycle state changes are published to `cd_event_outbox` for asynchronous consumption by downstream portals and streaming analytics.
- **Subscribed Events**: Subscribes to party/customer status updates, device verification tokens, and tenant configuration broadcast signals.

---

## 3. Data Models & Database Schemas

### 3.1 Primary Models Declared
- **Model**: `fix.field.rule` (Table: `fix_field_rule`)
  - *Description*: Field-Level Permission Rule
  - *Source File*: `models/fix_field_rule.py`
- **Model**: `fix.isolation.tier` (Table: `fix_isolation_tier`)
  - *Description*: Data Isolation Tier
  - *Source File*: `models/fix_isolation_tier.py`
- **Model**: `fix.role` (Table: `fix_role`)
  - *Description*: Business Role
  - *Source File*: `models/fix_role.py`
- **Model**: `fix.sod.control` (Table: `fix_sod_control`)
  - *Description*: Segregation of Duties Control
  - *Source File*: `models/fix_sod_control.py`
- **Model**: `fix.identity.document` (Table: `fix_identity_document`)
  - *Description*: Residency Enforcement Mixin
  - *Source File*: `models/residency_mixin.py`
- **Model**: `residency.mixin` (Table: `residency_mixin`)
  - *Description*: residency.mixin
  - *Source File*: `models/residency_mixin.py`

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
   python3 -m odoo -u cd_rbac_ext -d 1000fix_prod --stop-after-init
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
SELECT count(*) FROM fix_field_rule WHERE active = true;

-- Inspect recent state transitions (last 24 hours)
SELECT id, create_date, write_date, state 
FROM fix_field_rule 
WHERE write_date >= NOW() - INTERVAL '24 hours' 
ORDER BY write_date DESC LIMIT 50;
```

### 5.3 Incident Severity & Escalation Paths
- **Severity 1 (Critical Outage)**: System unable to process records or database locks. Escalate to Lead Systems Architect and On-Call Operations Lead.
- **Severity 2 (Degraded Performance)**: Specific actions exceeding 200ms latency budget. File ticket with Squad `Platform`.
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
py -3.12 -m pytest addons/platform/cd_rbac_ext -q -o 'addopts='
```

---

*Last Updated: 2026-10-20 · Approved by: 1000FiX Architecture Review Board (ARB)*
