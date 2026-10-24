# Operational Runbook: 1000FiX Customer Self-Service Portal (P01) (cd_customer_portal)

**Document**: `addons/domain/b_customer_engagement/cd_customer_portal/runbook.md`  
**Standard**: DoD-11 (Per-Module Operational Runbook), AR-007 §3.1  
**Module ID**: `P01` | **CD ID**: `CD-P01-01` | **Wave**: `W4`  
**Category**: `Sales/Portal` | **Layer**: `L3 Domain Extension`  
**Owner Squad**: `Experience`  
**Version**: `19.0.1.0.0` | **License**: `LGPL-3`  
**Compliance Status**: VERIFIED (DoD-11 Compliant)  

---

## 1. Operational Overview & Core Responsibilities

The `cd_customer_portal` module (1000FiX Customer Self-Service Portal (P01)) is an integral component of the 1000FiX ERP platform.

### 1.1 Business Scope
P01 PP5 slice: booking, live tracking, device history, ownership transfer, estimate approval and the PDPA consent dashboard via the portal API (CD-P01-01)

P01 PP5 slice (roadmap PP5-M01):

- The API surface the Next.js (R2) customer portal consumes — the W4
  OpenAPI contract in contracts/openapi/w4-portals.json (PS-11 tests
  enforce; AS-09: no business rule lives in portal code)
- Booking: <=3-step service booking writing fix.service.order with the
  model's own validation (the portal passes through)
- Live tracking: order state, technician, SLA clocks — polling today,
  the websocket upgrade rides the same payload shape
- Device history: the M17 registry's own timeline (T07 history entries)
- Ownership transfer: fix.device.action_transfer_ownership — T05 said
  "portal P01 exposes this in Phase 5"; this IS that exposure
- Estimate approval: the customer records their documented approval
  (BRU-SRM-07), then the model's action_approve enforces the hard gates
- PDPA consent dashboard: grant/withdraw per channel on fix.consent
  with the state visible — closes the audit gap surfaced in PP0

### 1.2 Critical Business Journeys Served
This module participates in and provides operational support for the following core enterprise journeys:
- **Primary Domain**: Sales > Portal
- **Service Tier**: T7
- **Transactional Support**: Provides backend data processing, business logic validation, state machine transitions, and audit trail enforcement for after-sales service operations across all 51 nationwide branch locations.

---

## 2. Module Topology & Dependencies

### 2.1 Upstream Dependencies (Declared in Manifest)
The module depends on the following prerequisite modules:
- `base`
- `portal`
- `mail`
- `cd_entity_config`
- `cd_rbac_ext`
- `cd_service_order`
- `cd_device_registry`
- `cd_party_master`

### 2.2 Event Bus Pub/Sub Contracts
- **Emitted Events**: Domain lifecycle state changes are published to `cd_event_outbox` for asynchronous consumption by downstream portals and streaming analytics.
- **Subscribed Events**: Subscribes to party/customer status updates, device verification tokens, and tenant configuration broadcast signals.

---

## 3. Data Models & Database Schemas

### 3.1 Primary Models Declared
- Direct extension or configuration module (inherits and configures parent models).

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
   python3 -m odoo -u cd_customer_portal -d 1000fix_prod --stop-after-init
   ```
2. **Configuration Verification**:
   - Verify access control rights in `security/ir.model.access.csv`.
   - Ensure company and operating unit isolation policies (`res.company`, `fix.operating.unit`) are active.
3. **OTP SMS delivery** (`controllers/otp_delivery.py`):
   - `/customer/auth/otp/send` POSTs a `security.otp_requested` event (NT-007) straight to the
     notification dispatcher's `/consume/once`; the code never goes through `fix_events` /
     the outbox, so it is never persisted in PostgreSQL or on the bus. The dispatcher
     redacts it in its tracking and excludes it from KPIs.
   - `FIX_NOTIFICATION_DISPATCHER_URL` (default `http://127.0.0.1:8110`). Outside
     `FIX_ENV=production` only loopback / `notification-dispatcher` hosts are accepted (DE-11).
   - Delivery failure: production answers `otp_unavailable` (no code is kept); `FIX_ENV=local`
     logs a warning and still echoes `dev_code`. Without an SMS gateway the dispatcher is dry-run.
   - A session may request a new code for a phone once per 60 s (`otp_throttled`); cross-session
     volume is capped by the Kong `rate-limiting` plugin. CORS is terminated at Kong
     (explicit origin allow-list) - no route declares `cors`.

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
SELECT count(*) FROM cd_customer_portal WHERE active = true;

-- Inspect recent state transitions (last 24 hours)
SELECT id, create_date, write_date, state 
FROM cd_customer_portal 
WHERE write_date >= NOW() - INTERVAL '24 hours' 
ORDER BY write_date DESC LIMIT 50;
```

### 5.3 Incident Severity & Escalation Paths
- **Severity 1 (Critical Outage)**: System unable to process records or database locks. Escalate to Lead Systems Architect and On-Call Operations Lead.
- **Severity 2 (Degraded Performance)**: Specific actions exceeding 200ms latency budget. File ticket with Squad `Experience`.
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
py -3.12 -m pytest addons/domain/b_customer_engagement/cd_customer_portal -q -o 'addopts='
```

---

*Last Updated: 2026-10-20 · Approved by: 1000FiX Architecture Review Board (ARB)*
