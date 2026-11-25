# Operational Runbook: 1000FiX Fixed Assets (cd_fixed_asset_ext)

**Document**: `addons/domain/g_finance/cd_fixed_asset_ext/runbook.md`  
**Standard**: DoD-11 (Per-Module Operational Runbook), AR-007 §3.1  
**Module ID**: `M49` | **CD ID**: `CD-M49-01` | **Wave**: `W5`  
**Category**: `Accounting/Fixed Assets` | **Layer**: `L3 Domain Extension`  
**Owner Squad**: `Finance`  
**Version**: `19.0.0.1.0` | **License**: `LGPL-3`  
**Compliance Status**: VERIFIED (DoD-11 Compliant)  

---

## 1. Operational Overview & Core Responsibilities

The `cd_fixed_asset_ext` module (1000FiX Fixed Assets) is an integral component of the 1000FiX ERP platform.

### 1.1 Business Scope
M49: fixed assets on M19's seam, straight-line depreciation (100% covered), CWIP capitalisation; M54 budget link advisory (CD-M49-nn)

CD-M49-01 (P08-M08) — fixed assets on the seam M19 built (P06-M01-T07):

- fix.fixed.asset — gross (Monetary), life, salvage; straight-line
  monthly depreciation computed by a PURE function (100% coverage,
  DoD-03 — a financial path); capitalised FROM the M19 seam
  (fix.fixed.asset.seam): finance posts capitalisation events, M49
  consumes
- fix.cwip.entry — capital-work-in-progress: costs accumulate; the
  CAPITALISE action creates the fixed asset from the accumulated total
- THE M49 <-> M54 BREAK (AR-006 4.1 pair 14): M54 consumes
  depreciation EVENTS (depreciation.accrued, published per POSTED monthly charge); M49
  does NOT read budgets — budget_reference is an ADVISORY char (5.4
  NOT-A-PREREQ), never a foreign key into M54

### 1.2 Critical Business Journeys Served
This module participates in and provides operational support for the following core enterprise journeys:
- **Primary Domain**: Accounting > Fixed Assets
- **Service Tier**: T9
- **Transactional Support**: Provides backend data processing, business logic validation, state machine transitions, and audit trail enforcement for after-sales service operations across all 51 nationwide branch locations.

---

## 2. Module Topology & Dependencies

### 2.1 Upstream Dependencies (Declared in Manifest)
The module depends on the following prerequisite modules:
- `base`
- `mail`
- `cd_entity_config`
- `cd_gl_ext`
- `cd_event_outbox`

### 2.2 Event Bus Pub/Sub Contracts
- **Emitted Events**: Domain lifecycle state changes are published to `cd_event_outbox` for asynchronous consumption by downstream portals and streaming analytics.
- **Subscribed Events**: Subscribes to party/customer status updates, device verification tokens, and tenant configuration broadcast signals.

---

## 3. Data Models & Database Schemas

### 3.1 Primary Models Declared
- **Model**: `fix.fixed.asset` (Table: `fix_fixed_asset`)
  - *Description*: Fixed Asset
  - *Source File*: `models/fix_fixed_asset.py`
- **Model**: `fix.cwip.entry` (Table: `fix_cwip_entry`)
  - *Description*: CWIP Entry
  - *Source File*: `models/fix_fixed_asset.py`
- **Master data**: `fix.asset.category` (posting accounts, journal, default life, tax class) and
  `fix.asset.tax.rate` (ITA 2023 Third Schedule reducing-balance rates, effective-dated, seeded
  UNVERIFIED — the tax adviser ticks *Verified* or adds a corrected dated row) — `models/fix_asset_master.py`
- **Depreciation**: `fix.asset.depreciation.run` / `.line` — monthly dual-book run; one line per
  asset, book and month (DB constraint) — `models/fix_asset_depreciation.py`
- **Capex**: `fix.capex.budget`, `fix.capex.request` — `models/fix_capex.py`
- **Lifecycle**: `fix.asset.transfer`, `fix.asset.revaluation`, `fix.asset.disposal` — `models/fix_asset_lifecycle.py`
- **Verification**: `fix.asset.verification.campaign` / `.line` — `models/fix_asset_verification.py`
- **Leases (IFRS 16)**: `fix.lease`, `fix.lease.schedule.line` — `models/fix_lease.py`

### 3.2 Data Residency & Classification (PDPA / Statutory Compliance)
- **Classification**: All tables storing customer identifiers, device serial numbers, or financial transactions are governed under Bangladesh Personal Data Protection statutory residency requirements.
- **Storage Tier**: PostgreSQL Primary Relational Storage (Sovereign onshore datacenter).
- **Audit Logging**: Chatter mixins (`mail.thread`, `mail.activity.mixin`) track field mutations with user attribution, timestamps, and previous/new values.

---

## 4. Routine Operations & Administrative Tasks

### 4.1 Scheduled & Maintenance Actions
- **Nightly Reconciliation**: Automated integrity checks run via standard cron schedules to detect orphan records or stalled state transactions.
- **Data Retention & Pruning**: Outbox payloads and temporary staging buffers are pruned according to data governance retention windows (90-day hot retention).

### 4.2 Month-End Procedure (P03 workspace, M49)
1. Configure each asset category's journal and accounts once (postings fail closed without them).
2. *Leases*: Post Due Months on each active lease (interest + payment; the ROU depreciation is
   charged through the depreciation run for that month).
3. *Dual-Book Depreciation*: create a run per book for the month, Compute, check the notes, Post.
   The accounting book posts one entry per journal (Dr depreciation expense / Cr accumulated);
   the tax book is a memo book (no GL). Re-running a month never charges an asset twice.
4. Post approved disposals and revaluations dated in the month, then review *Schedules & Movements*.

### 4.3 Standard Operational Procedures
1. **Module Deployment**:
   ```bash
   python3 -m odoo -u cd_fixed_asset_ext -d 1000fix_prod --stop-after-init
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
SELECT count(*) FROM fix_fixed_asset WHERE active = true;

-- Inspect recent state transitions (last 24 hours)
SELECT id, create_date, write_date, state 
FROM fix_fixed_asset 
WHERE write_date >= NOW() - INTERVAL '24 hours' 
ORDER BY write_date DESC LIMIT 50;
```

### 5.3 Incident Severity & Escalation Paths
- **Severity 1 (Critical Outage)**: System unable to process records or database locks. Escalate to Lead Systems Architect and On-Call Operations Lead.
- **Severity 2 (Degraded Performance)**: Specific actions exceeding 200ms latency budget. File ticket with Squad `Finance`.
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
py -3.12 -m pytest addons/domain/g_finance/cd_fixed_asset_ext -q -o 'addopts='
```

---

*Last Updated: 2026-10-20 · Approved by: 1000FiX Architecture Review Board (ARB)*
