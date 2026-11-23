# Operational Runbook: 1000FiX Accounts Payable (cd_ap_ext)

**Document**: `addons/domain/g_finance/cd_ap_ext/runbook.md`  
**Standard**: DoD-11 (Per-Module Operational Runbook), AR-007 §3.1  
**Module ID**: `M52` | **CD ID**: `CD-M52-01` | **Wave**: `W3`  
**Category**: `Finance/Payables` | **Layer**: `L3 Domain Extension`  
**Owner Squad**: `Commercial & Finance`  
**Version**: `19.0.1.0.0` | **License**: `LGPL-3`  
**Compliance Status**: VERIFIED (DoD-11 Compliant)  

---

## 1. Operational Overview & Core Responsibilities

The `cd_ap_ext` module (1000FiX Accounts Payable) is an integral component of the 1000FiX ERP platform.

### 1.1 Business Scope
M52 core: vendor invoices with blocking three-way match, TDS, expense claims, payment-request events (CD-M52-01)

CD-M52-01: the accounts-payable core.

- fix.vendor.invoice (+line) — the THREE-WAY MATCH (AR-006 section 4.1
  pair 11: the seam belongs in M52, consuming M16/M15 events, NOT in M16).
  G3-06: an unmatched invoice is BLOCKED, never warned about — payment is
  refused unless match_state == matched
- TDS determination is a SYNCHRONOUS call into M51 (pair 8); M51 consumes
  AP events, never the reverse
- fix.expense.claim — employee expense on the M21-core master (MV-01)
- T06: payment requests go to M50 as EVENTS (payment.requested) — no
  synchronous back-call (pair 9)

### 1.2 Critical Business Journeys Served
This module participates in and provides operational support for the following core enterprise journeys:
- **Primary Domain**: Finance > Payables
- **Service Tier**: T5
- **Transactional Support**: Provides backend data processing, business logic validation, state machine transitions, and audit trail enforcement for after-sales service operations across all 51 nationwide branch locations.

---

## 2. Module Topology & Dependencies

### 2.1 Upstream Dependencies (Declared in Manifest)
The module depends on the following prerequisite modules:
- `base`
- `mail`
- `account`
- `product`
- `hr`
- `cd_entity_config`
- `cd_employee_core`
- `cd_event_outbox`
- `cd_tax_engine_bd`
- `cd_requisition`
- `cd_gl_ext`

### 2.2 Event Bus Pub/Sub Contracts
- **Emitted Events**: Domain lifecycle state changes are published to `cd_event_outbox` for asynchronous consumption by downstream portals and streaming analytics.
- **Subscribed Events**: Subscribes to party/customer status updates, device verification tokens, and tenant configuration broadcast signals.

---

## 3. Data Models & Database Schemas

### 3.1 Primary Models Declared
- **Model**: `fix.vendor.invoice` (Table: `fix_vendor_invoice`)
  - *Description*: Vendor Invoice (three-way match)
  - *Source File*: `models/fix_ap_ext.py`
- **Model**: `fix.vendor.invoice.line` (Table: `fix_vendor_invoice_line`)
  - *Description*: Vendor Invoice Line
  - *Source File*: `models/fix_ap_ext.py`
- **Model**: `fix.expense.claim` (Table: `fix_expense_claim`)
  - *Description*: Expense Claim
  - *Source File*: `models/fix_ap_ext.py`

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
   python3 -m odoo -u cd_ap_ext -d 1000fix_prod --stop-after-init
   ```
2. **Configuration Verification**:
   - Verify access control rights in `security/ir.model.access.csv`.
   - Ensure company and operating unit isolation policies (`res.company`, `fix.operating.unit`) are active.

### 4.3 A08 controls: configuration keys (system parameters)
| Key | Default | Meaning |
|---|---|---|
| `cd_ap_ext.bank_cooling_off_hours` | `0` | Hours after a payee account is confirmed before it can be paid (BRU-APE-09; business decision B4). |
| `cd_ap_ext.claim_manager_threshold` | `25000` | Expense claims above this (with the employee's other live claims in the split window) need an Accounting Administrator. |
| `cd_ap_ext.claim_split_window_days` | `30` | Rolling window for split-claim detection (`0` = off). |
| `cd_ap_ext.claim_line_manager_step` | on | The claimant's line manager (employee manager with a login) approves before finance (spec §8.2). `0` = off. |
| `cd_ap_ext.higher_level_may_approve_lower` | on | An approver of a higher AP-matrix level may sign a lower level (managers sign level 1); one user still signs one level. |
| `cd_ap_ext.account_code.salary_payable` | none | GL account for advances recovered through payroll; unset = the recovery is refused. |
| `cd_ap_ext.account_code.retention_payable` | none | GL account for retention withheld from sub-contractor bills (FR-APE-027). **Unset = a bill with a retention percentage is refused, naming this key**; a bill without retention never needs it. |
| `cd_ap_ext.retention_max_percent` | none | Optional ceiling on a bill's retention percentage (FR-APE-027). Unset = no ceiling beyond 100 %. |
| `cd_ap_ext.retention_release_days` | `90` | Default days from entry to the scheduled retention release date (BRU-APE-20); the person may move the date on the bill. |

Consignment settlements (FR-APE-030) use the existing AP roles
(`cd_ap_ext.account_code.expense`, `cd_ap_ext.account_code.ap`, and M51's
`cd_tax_engine_bd.vat_input_account_code` when the brand's tax profile is
VAT-registered) and the configured purchase journal. They read M15's
`fix.stock.consumption` ledger; each consumption is settled once, and a
cancelled settlement releases its lines.

Payee bank accounts are paid only once confirmed by a second person
(`fix.payee.bank.change`, or `fix.supplier.bank.change` for M42 suppliers).
AP approval-matrix rows change only through `fix.ap.approval.rule.change`
(proposed by one Accounting Administrator, applied by another).

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
SELECT count(*) FROM fix_vendor_invoice WHERE active = true;

-- Inspect recent state transitions (last 24 hours)
SELECT id, create_date, write_date, state 
FROM fix_vendor_invoice 
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
py -3.12 -m pytest addons/domain/g_finance/cd_ap_ext -q -o 'addopts='
```

---

*Last Updated: 2026-10-20 · Approved by: 1000FiX Architecture Review Board (ARB)*
