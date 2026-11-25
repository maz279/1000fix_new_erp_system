# Operational Runbook: 1000FiX Platform Administration & Configuration (cd_entity_config)

**Document**: `addons/platform/cd_entity_config/runbook.md`  
**Standard**: DoD-11 (Per-Module Operational Runbook), AR-007 §3.1  
**Module ID**: `M30` | **CD ID**: `CD-M30-01` | **Wave**: `W1`  
**Category**: `Platform/Administration` | **Layer**: `L2 Core Platform`  
**Owner Squad**: `Platform`  
**Version**: `19.0.1.0.0` | **License**: `LGPL-3`  
**Compliance Status**: VERIFIED (DoD-11 Compliant)  

---

## 1. Operational Overview & Core Responsibilities

The `cd_entity_config` module (1000FiX Platform Administration & Configuration) is an integral component of the 1000FiX ERP platform.

### 1.1 Business Scope
Entity, branch, cost centre, zone, working calendar, feature flags, BD address hierarchy, country-pack interface, notification routing

M30 Platform Administration — the T0 configuration module.

Owns:
- fix.entity (legal entity on res.company)
- fix.branch (51+ operational branches, the OU isolation unit)
- fix.cost.center (financial cost centre)
- fix.zone + fix.geofence (dispatch zones)
- fix.working.calendar (M02's availability stub calls this)
- fix.feature.flag (every capability ships behind a flag — OPS-06)
- fix.bd.address (8 divisions / 64 districts / upazilas / unions)
- fix.country.pack (interface M51 consumes instead of M65)
- fix.notification.config (Novu channel routing, ADR-022)

CD items: CD-M30-01..CD-M30-nn per tooling/cd-register.yaml.

### 1.2 Critical Business Journeys Served
This module participates in and provides operational support for the following core enterprise journeys:
- **Primary Domain**: Platform > Administration
- **Service Tier**: T0
- **Transactional Support**: Provides backend data processing, business logic validation, state machine transitions, and audit trail enforcement for after-sales service operations across all 51 nationwide branch locations.

---

## 2. Module Topology & Dependencies

### 2.1 Upstream Dependencies (Declared in Manifest)
The module depends on the following prerequisite modules:
- `base`
- `mail`
- `operating_unit`

### 2.2 Event Bus Pub/Sub Contracts
- **Emitted Events**: Domain lifecycle state changes are published to `cd_event_outbox` for asynchronous consumption by downstream portals and streaming analytics.
- **Subscribed Events**: Subscribes to party/customer status updates, device verification tokens, and tenant configuration broadcast signals.

---

## 3. Data Models & Database Schemas

### 3.1 Primary Models Declared
- **Model**: `fix.bd.address` (Table: `fix_bd_address`)
  - *Description*: Bangladesh Address
  - *Source File*: `models/fix_bd_address.py`
- **Model**: `fix.branch` (Table: `fix_branch`)
  - *Description*: Branch
  - *Source File*: `models/fix_branch.py`
- **Model**: `fix.country.pack` (Table: `fix_country_pack`)
  - *Description*: Country Data Pack
  - *Source File*: `models/fix_country_pack.py`
- **Model**: `fix.country.pack.line` (Table: `fix_country_pack_line`)
  - *Description*: Country Data Pack Line
  - *Source File*: `models/fix_country_pack.py`
- **Model**: `fix.entity` (Table: `fix_entity`)
  - *Description*: Legal Entity
  - *Source File*: `models/fix_entity.py`
- **Model**: `fix.feature.flag` (Table: `fix_feature_flag`)
  - *Description*: Feature Flag
  - *Source File*: `models/fix_feature_flag.py`
- **Model**: `fix.geofence` (Table: `fix_geofence`)
  - *Description*: Geofence
  - *Source File*: `models/fix_geofence.py`
- **Model**: `fix.notification.config` (Table: `fix_notification_config`)
  - *Description*: Notification Configuration
  - *Source File*: `models/fix_notification_config.py`
- **Model**: `fix.working.calendar` (Table: `fix_working_calendar`)
  - *Description*: Working Calendar
  - *Source File*: `models/fix_working_calendar.py`
- **Model**: `fix.working.calendar.line` (Table: `fix_working_calendar_line`)
  - *Description*: Working Calendar Line
  - *Source File*: `models/fix_working_calendar.py`
- **Model**: `fix.working.calendar.holiday` (Table: `fix_working_calendar_holiday`)
  - *Description*: Calendar Holiday
  - *Source File*: `models/fix_working_calendar.py`
- **Model**: `fix.zone` (Table: `fix_zone`)
  - *Description*: Dispatch Zone
  - *Source File*: `models/fix_zone.py`

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
   python3 -m odoo -u cd_entity_config -d 1000fix_prod --stop-after-init
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
SELECT count(*) FROM fix_bd_address WHERE active = true;

-- Inspect recent state transitions (last 24 hours)
SELECT id, create_date, write_date, state 
FROM fix_bd_address 
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
py -3.12 -m pytest addons/platform/cd_entity_config -q -o 'addopts='
```

---

*Last Updated: 2026-10-20 · Approved by: 1000FiX Architecture Review Board (ARB)*

---

## Taking a DOFA authority ruling (open as of 2 November 2026)

Two approval ladders have an unresolved conflict between the specification's
prose and the DOFA authority matrix. **Neither is a defect** — in both cases
the code implements the REQ text and says so — but both are unresolved
policy, and the A03 gap plan classifies them as a **Decision** owed "before
external audit".

| Model | Field | REQ text (what the code does) | DOFA matrix (the alternative) |
|---|---|---|---|
| `fix.loyalty.ledger` | point adjustments | ≤500 → **Tier 0, no approval**; >500 → T2; >2,000 → T3 | ≤500 → T1; ≤2,000 → T2; ≤10,000 → T3 |
| `fix.complaint` | service-recovery concessions | >৳1,000 → T2; >৳5,000 → T3 (≤৳1,000 → T1) | ≤৳500 → T1; ≤৳2,500 → T2; ≤৳10,000 → T3 |

Note the deliberate asymmetry worth ruling on as well: M10 allows a
no-approval band below its first bound while M34 requires a supervisor for
any concession.

### Current state

Both bases are loaded as `fix.dofa.ladder` records with **`in_force` false on
every one**, so each model keeps its own coded default and behaviour today is
exactly what it has always been. Nothing has been pre-decided.

### How to take the ruling

1. Open **M30 → Approval Authority (DOFA) → Open DOFA Rulings**. The report
   lists each unresolved model, both bases, their bands side by side, and a
   **"What The Code Does Today"** column. That column is *computed* by
   comparing each ladder's bands against the model's real
   `_dofa_thresholds()`, so it cannot drift from the code — it currently
   reads *REQ text* for both. Choosing REQ text therefore changes nothing;
   choosing the matrix changes the bands.
2. Open **Authority Ladders**, select the ladder you are ruling for, and run
   **Put In Force (ruling)**.
3. Supply the **authority reference** — the board minute, memo or approval
   that authorises it. The action refuses without one: a change to who may
   approve what, with nothing recorded about who authorised the change, is
   not an improvement on a hard-coded list.

Putting a ladder in force automatically stands the sibling ladder down, so
exactly one basis per model is ever live. `ruled_by` and `ruled_at` are
stamped from the acting user, and the change is posted to the ladder's
chatter.

### Required authority

`fix.dofa.ladder` is writable only by `cd_entity_config.group_dofa_tier_4`
(CFO / CCO / COO). Read access is open to internal users, deliberately: an
approver is entitled to see the ladder they are held to.

### Effect

The ladder in force is consulted by `fix.dofa.mixin._dofa_tier_for_amount()`,
which is the single chokepoint every tier derivation passes through. With no
ladder in force the call falls through to the model's own Python default, so
the fallback — not the table — is what guarantees that an unruled estate
behaves exactly as before.
