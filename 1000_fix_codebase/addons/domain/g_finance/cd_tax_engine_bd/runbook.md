# Operational Runbook: 1000FiX VAT Engine (M51-core) (cd_tax_engine_bd)

**Document**: `addons/domain/g_finance/cd_tax_engine_bd/runbook.md`  
**Standard**: DoD-11 (Per-Module Operational Runbook), AR-007 §3.1  
**Module ID**: `M51` | **CD ID**: `CD-M51-01` | **Wave**: `W3`  
**Category**: `Finance/Tax` | **Layer**: `L3 Domain Extension`  
**Owner Squad**: `Commercial & Finance`  
**Version**: `19.0.1.0.0` | **License**: `LGPL-3`  
**Compliance Status**: VERIFIED (DoD-11 Compliant)  

---

## 1. Operational Overview & Core Responsibilities

The `cd_tax_engine_bd` module (1000FiX VAT Engine (M51-core)) is an integral component of the 1000FiX ERP platform.

### 1.1 Business Scope
VAT determination, TDS, Mushak 6.3 issuance + register, VAT/TDS returns, withholding certificates (CD-M51-01, P07-M04 completion)

CD-M51-01..05 (W3 slice per MV-03) + the P07-M04 completion:
- fix.vat.return — Mushak 9.1 monthly preparation from the register, with
  the MANDATORY nil return, holiday-rolled due dates, online-only filing
  (confirmation reference mandatory — manual filing abolished 1 July 2026),
  and the sub-ledger reconciliation
- fix.tds.return — quarterly returns on the statutory deadlines (25
  Oct/Jan/Apr/Jul, holiday-rolled) against the BD fiscal year
- fix.withholding.certificate — the deductee certificate flow
- The CALCULATION is pure (return_logic.py — 21 tests, 100% of return paths)

- tax_logic.determine_tax() / determine_tds() — PURE determination functions
  (no Odoo imports); M20 and M52 call them SYNCHRONOUSLY (AR-006 section 4.1
  pairs 7/8); nothing calls M20 back
- fix.vat.treatment — tariff projection, data source M30's country pack
  (NOT M65 — T06 closes the +5-wave violation)
- fix.mushak.register — the VAT register, populated by CONSUMING
  invoice.created events (never calling M20); rebuilds from the event stream
  alone (T04); BIN-format constraints (13 digits); atomic-posted with the GL
  (T08)
- The statutory Mushak 6.3 QWeb invoice with Bengali rendering (TR-07)

VAT returns and filing (Mushak 9.1) are explicitly W4 (roadmap P06-M02-T09).

### 1.2 Critical Business Journeys Served
This module participates in and provides operational support for the following core enterprise journeys:
- **Primary Domain**: Finance > Tax
- **Service Tier**: T5
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
- `cd_gl_ext`

### 2.2 Event Bus Pub/Sub Contracts
- **Emitted Events**: Domain lifecycle state changes are published to `cd_event_outbox` for asynchronous consumption by downstream portals and streaming analytics.
- **Subscribed Events**: Subscribes to party/customer status updates, device verification tokens, and tenant configuration broadcast signals.

---

## 3. Data Models & Database Schemas

### 3.1 Primary Models Declared
- **Model**: `fix.vat.treatment` (Table: `fix_vat_treatment`)
  - *Description*: VAT Treatment
  - *Source File*: `models/fix_tax_engine.py`
- **Model**: `fix.mushak.register` (Table: `fix_mushak_register`)
  - *Description*: Mushak 6.3 VAT Register
  - *Source File*: `models/fix_tax_engine.py`
- **Model**: `fix.vat.return` (Table: `fix_vat_return`)
  - *Description*: VAT Return (Mushak 9.1)
  - *Source File*: `models/fix_tax_returns.py`
- **Model**: `vat_subledger.reconciled` (Table: `vat_subledger_reconciled`)
  - *Description*: TDS Return (quarterly)
  - *Source File*: `models/fix_tax_returns.py`
- **Model**: `fix.tds.return` (Table: `fix_tds_return`)
  - *Description*: TDS Return Detail Line
  - *Source File*: `models/fix_tax_returns.py`
- **Model**: `fix.tds.return.line` (Table: `fix_tds_return_line`)
  - *Description*: Withholding Tax Certificate
  - *Source File*: `models/fix_tax_returns.py`
- **Model**: `fix.withholding.certificate` (Table: `fix_withholding_certificate`)
  - *Description*: fix.withholding.certificate
  - *Source File*: `models/fix_tax_returns.py`

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
   python3 -m odoo -u cd_tax_engine_bd -d 1000fix_prod --stop-after-init
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
SELECT count(*) FROM fix_vat_treatment WHERE active = true;

-- Inspect recent state transitions (last 24 hours)
SELECT id, create_date, write_date, state 
FROM fix_vat_treatment 
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
py -3.12 -m pytest addons/domain/g_finance/cd_tax_engine_bd -q -o 'addopts='
```

---

*Last Updated: 2026-10-20 · Approved by: 1000FiX Architecture Review Board (ARB)*
