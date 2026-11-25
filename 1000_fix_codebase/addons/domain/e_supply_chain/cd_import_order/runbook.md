# Operational Runbook: 1000FiX Import, Trade Compliance & Landed Cost (cd_import_order)

**Document**: `addons/domain/e_supply_chain/cd_import_order/runbook.md`  
**Standard**: DoD-11 (Per-Module Operational Runbook), AR-007 §3.1  
**Module ID**: `M44` | **CD ID**: `CD-M44-01` | **Wave**: `W6`  
**Category**: `Import, Trade Compliance & Landed Cost` | **Layer**: `L3 Domain Extension`  
**Owner Squad**: `Import, Trade Compliance & Landed Cost`  
**Version**: `19.0.0.1.0` | **License**: `LGPL-3`  
**Compliance Status**: VERIFIED (DoD-11 Compliant)  

---

## 1. Operational Overview & Core Responsibilities

The `cd_import_order` module (1000FiX Import, Trade Compliance & Landed Cost) is an integral component of the 1000FiX ERP platform.

### 1.1 Business Scope
M44: Import, Trade Compliance & Landed Cost (CD-M44-01)

CD-M44-01 (P09) — Import, Trade Compliance & Landed Cost.

Built on the existing estate (the layered model: compose, never
duplicate). AS-02 chatter + AS-03 company/OU on every transactional
model; AS-10 Monetary on every money field; events registered (AS-08).

### 1.2 Critical Business Journeys Served
This module participates in and provides operational support for the following core enterprise journeys:
- **Primary Domain**: Import, Trade Compliance & Landed Cost
- **Service Tier**: T9
- **Transactional Support**: Provides backend data processing, business logic validation, state machine transitions, and audit trail enforcement for after-sales service operations across all 51 nationwide branch locations.

---

## 2. Module Topology & Dependencies

### 2.1 Upstream Dependencies (Declared in Manifest)
The module depends on the following prerequisite modules:
- `base`
- `mail`
- `cd_entity_config`
- `cd_requisition`
- `cd_gl_ext`
- `cd_event_outbox`

### 2.2 Event Bus Pub/Sub Contracts
- **Emitted Events**: Domain lifecycle state changes are published to `cd_event_outbox` for asynchronous consumption by downstream portals and streaming analytics.
- **Subscribed Events**: Subscribes to party/customer status updates, device verification tokens, and tenant configuration broadcast signals.

---

## 3. Data Models & Database Schemas

### 3.1 Primary Models Declared
- **Model**: `fix.import.order` (Table: `fix_import_order`)
  - *Description*: Import Order
  - *Source File*: `models/fix_import_order.py`

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
   python3 -m odoo -u cd_import_order -d 1000fix_prod --stop-after-init
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
SELECT count(*) FROM fix_import_order WHERE active = true;

-- Inspect recent state transitions (last 24 hours)
SELECT id, create_date, write_date, state 
FROM fix_import_order 
WHERE write_date >= NOW() - INTERVAL '24 hours' 
ORDER BY write_date DESC LIMIT 50;
```

### 5.3 Incident Severity & Escalation Paths
- **Severity 1 (Critical Outage)**: System unable to process records or database locks. Escalate to Lead Systems Architect and On-Call Operations Lead.
- **Severity 2 (Degraded Performance)**: Specific actions exceeding 200ms latency budget. File ticket with Squad `Import, Trade Compliance & Landed Cost`.
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
py -3.12 -m pytest addons/domain/e_supply_chain/cd_import_order -q -o 'addopts='
```

---

*Last Updated: 2026-10-20 · Approved by: 1000FiX Architecture Review Board (ARB)*

---

## 8. Controls and configuration (A06 remediation, November 2026)

### 8.1 Roles
| Role | Group | Does |
|---|---|---|
| Import Officer | `cd_import_order.group_fix_import_officer` (admin member) | Records orders and lines, proformas, LCs, LCAs, amendments, tariff rows, HS classifications, shipping documents, arrivals, Bills of Entry; applies for and opens LCs; requests LC approval; receives the consignment; posts the landed-cost estimate |
| Import Approver | `cd_import_order.group_fix_import_approver` (ships EMPTY) | Approves proformas, LCAs, HS rulings, tariff rows, IRC suspension/reinstatement, the final landed cost; with a DOFA tier group, decides LC opening and amendments in the M63 inbox. Never on a record they recorded or changed |
| Finance | `account.group_account_user` | Pays a Bill of Entry (posts the duty), reverses a paid one, records LC payments |

A plain internal user reads everything and writes nothing.

### 8.2 Business decisions left configurable (`ir.config_parameter`)
| Key | Default | Meaning |
|---|---|---|
| `cd_import_order.lc_dofa_ladder` | `inf:tier_4` | LC and LC-amendment authority ladder on the BDT value (`<bound>:<tier>,...,inf:<tier>`). Default: every LC needs Tier 4 (CFO/CCO/COO) |
| `cd_import_order.lc_value_tolerance_pct` | `0` | How far an LC may exceed the order invoice value without an amendment |
| `cd_import_order.proforma_tolerance_pct` | `0` | Proforma vs order invoice value |
| `cd_import_order.lc_requires_lca` | `1` | Require an approved LCA before LC application (Finance may set `0`: the LCAF was repealed in 2022) |
| `cd_import_order.boe_required_documents` | `bl,invoice,packing` | Documents received before a Bill of Entry is assessed (BRU-ITC-05) |
| `cd_import_order.duty_variance_tolerance` | `0` | BDT difference allowed between customs' assessed total and the computed duty (BRU-ITC-07) |
| `cd_import_order.landing_charge_pct` | `1.0` | Landing charge in AV = CIF x FX x (1 + %), from spec FR-ITC-033; Finance to confirm |
| `cd_import_order.journal_code` | company's first general journal | Journal for landed-cost postings |
| `cd_import_order.payment_journal_code` | none (REQUIRED) | Bank/cash journal customs duty is paid from |
| (stock line, not configurable) | M15 valuation suspense account (`110999`) | The stock line posts to the account M15 books every stock-valuation movement against; the M19 cutover journal moves it to Inventory, so the landed cost reaches the GL once. It must exist in the chart, or posting is refused. |
| `cd_import_order.account_code.duty_clearing` | none (REQUIRED) | CD + RD + SD paid, awaiting capitalisation |
| `cd_import_order.account_code.landed_accrual` | none (REQUIRED) | Freight, insurance, clearing owed; landed-cost estimates |
| `cd_import_order.account_code.vat_input` | none (REQUIRED) | Import VAT input tax |
| `cd_import_order.account_code.at_input` | none (REQUIRED) | Advance Tax recoverable |
| `cd_import_order.account_code.ait_advance` | none (REQUIRED) | AIT paid at import (income-tax advance) |
| `cd_import_order.account_code.variance` | none (REQUIRED when used) | Landed cost of stock consumed before the final cost (cost-of-sales adjustment); also an accepted duty variance on a Bill of Entry |
| `cd_import_order.account_code.lc_clearing` | none (REQUIRED) | LC payments, at the commitment rate, until the supplier's bill settles them. An LC payment is refused until it is set |
| `cd_import_order.account_code.fx_difference` | none (REQUIRED when used) | Settlement rate against commitment rate on a foreign-currency LC payment |
| `cd_import_order.advance_cap_pct` | `0` | Share of the invoice value advances may reach before an approval needs a stated reason. 0 = every advance approval states one. Advances never exceed the invoice value |
| `cd_import_order.irc_expiry_warning_days` | `30` | Days before an IRC lapses that the Import Approvers get a to-do |
| `cd_import_order.boe_remittance_match_days` | `120` | Days before an unmatched Bill of Entry or LC payment is flagged. Stands for Bangladesh Bank's 4-month guideline; Finance confirms it |

A posting whose account or journal is not configured is refused with the key to set; nothing is posted to a guessed account.

Tariff rates are data: enter each heading's rates and SRO reference on the HS Tariff Master (`fix.import.tariff`) with an effective date; an Import Approver who did not enter the row activates it.

### 8.3 Postings
- **Bill of Entry paid**: Dr duty clearing (CD+RD+SD), Dr import VAT, Dr AT, Dr AIT advance / Cr duty bank.
- **Receipt with a posted estimate**: stock enters M15 at goods (FOB x commitment FX) + estimate; Dr inventory / Cr landed-cost accrual (estimate).
- **Final landed cost**: Dr landed-cost accrual (reverse estimate), Cr duty clearing (CD+RD+SD), Cr landed-cost accrual (freight+insurance+clearing), Dr inventory (true-up on stock still on hand, revalued through `fix.stock.onhand._fix_revalue`), Dr variance (true-up on stock already consumed).

### 8.4 Scheduled job
`M44: expire lapsed Import Registration Certificates` (`ir_cron_import_irc_expire`, daily).
