# Operational Runbook: 1000FiX Workflow Engine (cd_workflow_engine)

**Document**: `addons/domain/i_governance/cd_workflow_engine/runbook.md`  
**Standard**: DoD-11 (Per-Module Operational Runbook), AR-007 §3.1  
**Module ID**: `M63` | **CD ID**: `CD-M63-01` | **Wave**: `W3`  
**Category**: `Operations/Automation` | **Layer**: `L3 Domain Extension`  
**Owner Squad**: `People & Governance`  
**Version**: `19.0.1.2.0` | **License**: `LGPL-3`  
**Compliance Status**: VERIFIED (DoD-11 Compliant)  

---

## 1. Operational Overview & Core Responsibilities

The `cd_workflow_engine` module (1000FiX Workflow Engine) is an integral component of the 1000FiX ERP platform.

### 1.1 Business Scope
M63: the AUT-001..060 automation register with runtime-verified engine bindings, approval matrix seam (CD-M63-01/02/04).

CD-M63-01/02/04: process automation.

- fix.automation — the 60-automation register (data/aut_register.yaml,
  extracted from 05-05 section 12); every row names the mechanism that
  really executes it (odoo_cron | odoo_method | event_consumer | manual —
  P06-M08-T04) and the binding is verified at runtime by
  `_binding_resolver`; engine-gap reporting for G3 evidence (never
  assumed done)
- fix.approval.matrix — the 05-04 section 7 authority matrix in one place
- Notifying automations PUBLISH EVENTS consumed by the W1 notification
  dispatcher (closes the M63 -> M27 violation — no direct calls)

### 1.2 Critical Business Journeys Served
This module participates in and provides operational support for the following core enterprise journeys:
- **Primary Domain**: Operations > Automation
- **Service Tier**: T4
- **Transactional Support**: Provides backend data processing, business logic validation, state machine transitions, and audit trail enforcement for after-sales service operations across all 51 nationwide branch locations.

---

## 2. Module Topology & Dependencies

### 2.1 Upstream Dependencies (Declared in Manifest)
The module depends on the following prerequisite modules:
- `base`
- `mail`
- `hr`
- `cd_entity_config`
- `cd_event_outbox`
- `cd_rbac_ext`

### 2.2 Event Bus Pub/Sub Contracts
- **Emitted Events**: `automation.register.loaded` (a catalogue reload, with the
  loaded / refreshed / verified / unresolved counts), plus the approval and
  substitution lifecycle events. All are published to `cd_event_outbox` for
  asynchronous consumption.
- **Consumed by this module**: `automation.register.loaded` →
  `fix.automation.consume_register_loaded` (data/fix_aut_event_consumers.xml).
  When a reload leaves a row whose reference does not resolve, it raises a
  same-day to-do on every broken row for an active DoA Administrator.

### 2.3 Scheduled Actions Owned Here
Only two, both approval-engine jobs (`data/approval_engine_cron.xml`):

| ir.cron xmlid | What it does | Interval |
|---|---|---|
| `cd_workflow_engine.ir_cron_approval_escalate_overdue` | remind, then escalate, overdue approval tasks | 1 hour |
| `cd_workflow_engine.ir_cron_approval_substitution_expire` | expire ended approval substitutions and hand tasks back | 1 day |

There is **no nightly reconciliation cron** in this module. The automation
register's own executors are other modules' crons, methods and event
consumers — the Scheduled Jobs screen (`scheduled_jobs` pack) lists the real
`ir.cron` estate.

---

## 3. Data Models & Database Schemas

### 3.1 Primary Models Declared
- **Model**: `fix.automation` (Table: `fix_automation`)
  - *Description*: Business Automation — engine / engine_ref / implementation /
    executor_note; computed binding_state / executor_active / coverage_state
  - *Source File*: `models/fix_workflow_engine.py`
- **Model**: `fix.approval.matrix` (Table: `fix_approval_matrix`)
  - *Description*: Approval Authority Matrix
  - *Source File*: `models/fix_workflow_engine.py`

### 3.2 Data Residency & Classification (PDPA / Statutory Compliance)
- **Classification**: All tables storing customer identifiers, device serial numbers, or financial transactions are governed under Bangladesh Personal Data Protection statutory residency requirements.
- **Storage Tier**: PostgreSQL Primary Relational Storage (Sovereign onshore datacenter).
- **Audit Logging**: Chatter mixins (`mail.thread`, `mail.activity.mixin`) track field mutations with user attribution, timestamps, and previous/new values.

---

## 4. Routine Operations & Administrative Tasks

### 4.1 Scheduled & Maintenance Actions
- **Approval escalation**: `M63: remind and escalate overdue approvals` (hourly)
  and `M63: expire ended approval substitutions` (daily) — §2.3.
- **Register reload**: `fix.automation.action_load_register()` re-reads
  `data/aut_register.yaml` idempotently. Run it after a catalogue change
  (deploy or manual); it refreshes every catalogue row and deactivates the
  rows the estate does not implement. It never overwrites `trigger`/`action`.
- **Data Retention & Pruning**: Outbox payloads and temporary staging buffers are pruned according to data governance retention windows (90-day hot retention).

### 4.2 Standard Operational Procedures
1. **Module Deployment**:
   ```bash
   python3 -m odoo -u cd_workflow_engine -d 1000fix_prod --stop-after-init
   ```
   An upgrade to 19.0.1.2.0 runs `migrations/19.0.1.2.0/post-migrate.py`:
   it refreshes the register from the truthful catalogue and converts any
   non-catalogue row still carrying a retired engine value
   (`odoo_automated_action` / `airflow` / `domain_service`) to
   `engine='manual'`, `implementation='none'`, inactive, with a note. It is
   idempotent.
2. **Configuration Verification**:
   - Verify access control rights in `security/ir.model.access.csv`.
   - Ensure company and operating unit isolation policies (`res.company`, `fix.operating.unit`) are active.

### 4.3 Operator Guide — reading Binding / Coverage

Open **Data & Analytics → M63 Process Automation → Workflow Definitions**
(or **Scheduled Jobs** for the real `ir.cron` list). Each automation row
carries:

| Column | Meaning |
|---|---|
| **Engine** | `odoo_cron` = a scheduled action; `odoo_method` = a model method run on a document step; `event_consumer` = an outbox event consumer; `manual` = nothing executes it |
| **Engine Reference** | `cron:<module>.<xmlid>`, `method:<model>.<method>`, `consumer:<event_type>`; empty for `manual` |
| **Implementation** | how much of the described action the executor really performs: `full`, `partial` (the executor note says what is missing), `none` |
| **Binding** | *verified* / *unresolved* / *manual* — resolved live against the registry, not stored |
| **Coverage** | *implemented* (full + verified), *partial* (partial + verified), *planned* (nothing implements it), *broken* (claims an implementation its reference cannot back) |
| **Executor Active** | the cron is switched on / the method exists / the consumer row is active |

Rules to remember:
- An **active** row must have a **verified** binding (or be `manual` with
  implementation `none`). The server refuses to save an active row whose
  reference does not resolve, naming the reference in the error.
- `manual` may never carry an implementation; say `none` and record why in
  the executor note.
- Coverage **planned** rows are loaded **inactive** — an automation nobody
  runs automates nothing.

### 4.4 When `action_report_engine_gap` lists a row

The gap report (and the "broken" coverage state) lists every row that
**claims an implementation its reference cannot back**, plus any still-active
`planned` row. It resolves references against the live registry, so it is
the truth at the moment it runs. (A module **upgrade** reloads the register
while Odoo is still loading the other modules; that reload's
`automation.register.loaded` event can therefore report references as
unresolved that resolve as soon as every module is loaded. The consumer
recomputes from the database, so no false to-do is raised — re-open the
report after the upgrade finishes.)

For each reported row:

1. Read the row's **executor note** and the error text the
   `automation.register.loaded` consumer put in the to-do on the row.
2. Either **fix the reference** (correct `module.xmlid` / `model.method` /
   `event_type`, after checking the code or the `fix.event.consumer` row), or
3. **Correct the claim**: if only part of the behaviour exists, set
   `implementation = partial` and state what is missing; if nothing executes
   it, set `engine = manual`, `implementation = none`, **deactivate** the row
   and explain in the executor note.
4. Re-run `action_load_register()` only if you changed the YAML catalogue —
   it would overwrite manual edits to these fields with the catalogue's
   values by design.
5. Confirm the report is empty (`action_report_engine_gap()` returns `[]`)
   or lists exactly the rows you knowingly left broken.

---

## 5. Troubleshooting & Diagnostic Playbooks

### 5.1 Common Failure Modes & Symptoms
- **Stalled State Transitions**: Records remaining in processing/pending states without advancing.
- **Permission Denied / Access Errors**: Non-admin users unable to read or write specific records. Verify group membership and multi-company rules.
- **Constraint Violations**: Duplicate external IDs, missing required relational links (e.g. `partner_id`, `company_id`).
- **"AUT xxx is active but its engine reference does not resolve"**: the write
  guard refused an active row with a dead reference — see §4.4.
- **A known-good automation shows `unresolved`**: its executor's module may be
  uninstalled or its cron deleted; the resolver reads the live registry, so
  this is the truth, not a stale flag.

### 5.2 Diagnostic SQL Queries
```sql
-- The automation register by what really executes it (there is NO `state`
-- column on fix_automation: engine + implementation + active are the facts)
SELECT engine, implementation, count(*), count(*) FILTER (WHERE active) AS active_rows
FROM fix_automation
GROUP BY 1, 2
ORDER BY 1, 2;

-- Rows that claim an implementation but have no reference at all
SELECT code, engine, implementation
FROM fix_automation
WHERE implementation <> 'none' AND coalesce(engine_ref, '') = '';

-- The register's engine references against the real scheduled actions
SELECT a.code, a.engine_ref, c.active, c.nextcall
FROM fix_automation a
LEFT JOIN ir_model_data d
  ON d.model = 'ir.cron' AND 'cron:' || d.module || '.' || d.name = a.engine_ref
LEFT JOIN ir_cron c ON c.id = d.res_id
WHERE a.engine = 'odoo_cron'
ORDER BY a.code;

-- Recently changed rows (an edit is the event; there is no state machine)
SELECT code, engine, implementation, write_date
FROM fix_automation
WHERE write_date >= NOW() - INTERVAL '24 hours'
ORDER BY write_date DESC LIMIT 50;
```

### 5.3 Incident Severity & Escalation Paths
- **Severity 1 (Critical Outage)**: System unable to process records or database locks. Escalate to Lead Systems Architect and On-Call Operations Lead.
- **Severity 2 (Degraded Performance)**: Specific actions exceeding 200ms latency budget. File ticket with Squad `People & Governance`.
- **Severity 3 (Minor Defect / Cosmetic)**: Route to normal sprint backlog.

---

## 6. Disaster Recovery & Data Remediation

### 6.1 Idempotent Repair & Data Re-sync
In the event of network disruption or interrupted transactions:
1. Identify uncommitted or faulted IDs using the diagnostic query in §5.2.
2. Re-run `fix.automation.action_load_register()` (idempotent) to restore the
   catalogue's engine / reference / implementation facts, or re-run the module
   migration runner.
3. Verify event outbox relay queues are drained.

### 6.2 Module Downgrade & Rollback Precautions
- **Rollback Policy**: Schema migrations adding columns are non-destructive (backward-compatible). Never execute `DROP COLUMN` in production without prior ARB sign-off and complete database backup.
- **19.0.1.2.0 note**: the retired engine values are kept OUT of the selection.
  A downgrade to 19.0.1.1.0 would meet rows whose engine value the old
  selection does not know; re-run the old module's own migration or restore
  the pre-upgrade backup.

---

## 7. Telemetry, Observability & SLA Thresholds

### 7.1 Prometheus & Log Metric Probes
- **Latency Budget**: Transactional write latency p95 <= 200 ms; read queries p95 <= 50 ms.
- **Correlation ID Tracking**: All incoming portal or API calls propagate `X-Correlation-ID` header into PostgreSQL session variables and application log output.

### 7.2 Health Probes
```bash
# Verify module load and test execution clean
py -3.12 -m pytest addons/domain/i_governance/cd_workflow_engine -q -o 'addopts='
```

---

*Last Updated: 2026-11-23 · Approved by: 1000FiX Architecture Review Board (ARB)*
