# Operational Runbook: 1000FiX General Ledger Extension (cd_gl_ext)

**Document**: `addons/domain/g_finance/cd_gl_ext/runbook.md`  
**Standard**: DoD-11 (Per-Module Operational Runbook), AR-007 §3.1  
**Module ID**: `M19` | **CD ID**: `CD-M19-01` | **Wave**: `W3`  
**Category**: `Finance/Accounting` | **Layer**: `L3 Domain Extension`  
**Owner Squad**: `Commercial & Finance`  
**Version**: `19.0.1.0.0` | **License**: `LGPL-3`  
**Compliance Status**: VERIFIED (DoD-11 Compliant)  

---

## 1. Operational Overview & Core Responsibilities

The `cd_gl_ext` module (1000FiX General Ledger Extension) is an integral component of the 1000FiX ERP platform.

### 1.1 Business Scope
M19 core: branch/OU posting dimensions, 5-day period close, fixed-asset seam, suspense reconciliation, journal events (CD-M19-01)

CD-M19-01: the M19 financial core on Odoo account + OCA account-financial-tools.

Owns:
- fix.journal.dimension — branch/cost-centre/OU on every posting (AS-03)
- fix.period.close (+line) — the 5-day month-end close process (CD-M19-05)
- fix.fixed.asset.seam — the capitalisation interface M49 extends (Phase 8)
- post_with_dimensions() — atomic post + dimensions + journal.posted event (AS-08)

The Bangladesh chart of accounts loads from the MD-* finance and statutory
content set (master data, AF-09-gated — loader lands with the content).
Suspense reconciliation (AR-006 §5.4) is enforced at close: the W2 inventory
suspense balance must be zero before a period can close.

### 1.2 Critical Business Journeys Served
This module participates in and provides operational support for the following core enterprise journeys:
- **Primary Domain**: Finance > Accounting
- **Service Tier**: T4
- **Transactional Support**: Provides backend data processing, business logic validation, state machine transitions, and audit trail enforcement for after-sales service operations across all 51 nationwide branch locations.

---

## 2. Module Topology & Dependencies

### 2.1 Upstream Dependencies (Declared in Manifest)
The module depends on the following prerequisite modules:
- `base`
- `mail`
- `account`
- `cd_entity_config`
- `cd_event_outbox`

### 2.2 Event Bus Pub/Sub Contracts
- **Emitted Events**: Domain lifecycle state changes are published to `cd_event_outbox` for asynchronous consumption by downstream portals and streaming analytics.
- **Subscribed Events**: Subscribes to party/customer status updates, device verification tokens, and tenant configuration broadcast signals.

---

## 3. Data Models & Database Schemas

### 3.1 Primary Models Declared
- **Model**: `fix.chart.account` (Table: `fix_chart_account`)
  - *Description*: Bangladesh Statutory Chart Account
  - *Source File*: `models/fix_chart_loader.py`
- **Model**: `fix.chart.loader` (Table: `fix_chart_loader`)
  - *Description*: Chart of Accounts Loader
  - *Source File*: `models/fix_chart_loader.py`
- **Model**: `fix.fiscal.period.bridge` (Table: `fix_fiscal_period_bridge`)
  - *Description*: Fiscal Year and Period Close Bridge
  - *Source File*: `models/fix_fiscal_year_ext.py`
- **Model**: `fix.financial.report.bridge` (Table: `fix_financial_report_bridge`)
  - *Description*: Financial Reporting Bridge
  - *Source File*: `models/fix_fiscal_year_ext.py`
- **Model**: `fix.journal.dimension` (Table: `fix_journal_dimension`)
  - *Description*: Journal Posting Dimension
  - *Source File*: `models/fix_gl_ext.py`
- **Model**: `fix.period.close` (Table: `fix_period_close`)
  - *Description*: Period Close Checklist
  - *Source File*: `models/fix_gl_ext.py`
- **Model**: `fix.period.close.line` (Table: `fix_period_close_line`)
  - *Description*: Period Close Step
  - *Source File*: `models/fix_gl_ext.py`
- **Model**: `fix.fixed.asset.seam` (Table: `fix_fixed_asset_seam`)
  - *Description*: Fixed Asset Seam (M49 interface)
  - *Source File*: `models/fix_gl_ext.py`

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
   python3 -m odoo -u cd_gl_ext -d 1000fix_prod --stop-after-init
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
SELECT count(*) FROM fix_chart_account WHERE active = true;

-- Inspect recent state transitions (last 24 hours)
SELECT id, create_date, write_date, state 
FROM fix_chart_account 
WHERE write_date >= NOW() - INTERVAL '24 hours' 
ORDER BY write_date DESC LIMIT 50;
```

### 5.3 Incident Severity & Escalation Paths
- **Severity 1 (Critical Outage)**: System unable to process records or database locks. Escalate to Lead Systems Architect and On-Call Operations Lead.
- **Severity 2 (Degraded Performance)**: Specific actions exceeding 200ms latency budget. File ticket with Squad `Commercial & Finance`.
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
py -3.12 -m pytest addons/domain/g_finance/cd_gl_ext -q -o 'addopts='
```

---

*Last Updated: 2026-10-20 · Approved by: 1000FiX Architecture Review Board (ARB)*
