# Operational Runbook: 1000FiX Privilege Programme, Loyalty Points & Vouchers (cd_loyalty)

**Document**: `addons/domain/b_customer_engagement/cd_loyalty/runbook.md`  
**Standard**: DoD-11 (Per-Module Operational Runbook), AR-007 §3.1  
**Module ID**: `M10` | **CD ID**: `CD-M10-01` | **Wave**: `W2`  
**Category**: `Customer/Loyalty` | **Layer**: `L3 Domain Extension`  
**Owner Squad**: `Customer Engagement`  
**Version**: `19.0.1.0.0` | **License**: `LGPL-3`  
**Compliance Status**: VERIFIED (DoD-11 Compliant)  

---

## 1. Operational Overview & Core Responsibilities

The `cd_loyalty` module (1000FiX Privilege Programme, Loyalty Points & Vouchers) is an integral component of the 1000FiX ERP platform.

### 1.1 Business Scope
M10 privilege programme, tier management, points ledger, vouchers & campaign hooks (CD-M10-01)

CD-M10-01 (P05-M08-T01..T03):

- fix.loyalty.program — the privilege programme configuration, points earning rates,
  currency value, and expiration rules
- fix.loyalty.tier — membership tier definitions (Bronze, Silver, Gold, Platinum) with
  thresholds, bonus multipliers, and labour/part discount benefits
- fix.loyalty.account — customer loyalty account tracking balances and tier progression
- fix.loyalty.ledger — append-only points transaction ledger (earned, redeemed, adjusted, expired)
- fix.loyalty.voucher — privilege vouchers with single-use codes, discounts, and expiry
- fix.loyalty.campaign — campaign hooks integrating with cd_campaign for promo codes and bonus points
- STUB-M10-M11-001 — cross-wave redemption stub with registered expiry at R04-M02-T08

### 1.2 Critical Business Journeys Served
This module participates in and provides operational support for the following core enterprise journeys:
- **Primary Domain**: Customer > Loyalty
- **Service Tier**: T6
- **Transactional Support**: Provides backend data processing, business logic validation, state machine transitions, and audit trail enforcement for after-sales service operations across all 51 nationwide branch locations.

---

## 2. Module Topology & Dependencies

### 2.1 Upstream Dependencies (Declared in Manifest)
The module depends on the following prerequisite modules:
- `base`
- `mail`
- `operating_unit`
- `cd_entity_config`
- `cd_party_master`
- `cd_service_order`
- `cd_event_outbox`

### 2.2 Event Bus Pub/Sub Contracts
- **Emitted Events**: Domain lifecycle state changes are published to `cd_event_outbox` for asynchronous consumption by downstream portals and streaming analytics.
- **Subscribed Events**: Subscribes to party/customer status updates, device verification tokens, and tenant configuration broadcast signals.

---

## 3. Data Models & Database Schemas

### 3.1 Primary Models Declared
- **Model**: `fix.loyalty.account` (Table: `fix_loyalty_account`)
  - *Description*: Customer Loyalty Membership Account
  - *Source File*: `models/fix_loyalty_account.py`
- **Model**: `fix.loyalty.campaign.hook` (Table: `fix_loyalty_campaign_hook`)
  - *Description*: Loyalty Campaign Integration Hook
  - *Source File*: `models/fix_loyalty_campaign.py`
- **Model**: `fix.loyalty.ledger` (Table: `fix_loyalty_ledger`)
  - *Description*: Loyalty Points Audit Ledger
  - *Source File*: `models/fix_loyalty_ledger.py`
- **Model**: `loyalty.points_accrued` (Table: `loyalty_points_accrued`)
  - *Description*: loyalty.points_accrued
  - *Source File*: `models/fix_loyalty_ledger.py`
- **Model**: `fix.loyalty.program` (Table: `fix_loyalty_program`)
  - *Description*: Loyalty & Privilege Programme
  - *Source File*: `models/fix_loyalty_program.py`
- **Model**: `fix.loyalty.redemption.stub` (Table: `fix_loyalty_redemption_stub`)
  - *Description*: Cross-Wave Loyalty Redemption Stub (M10 -> M11/M20)
  - *Source File*: `models/fix_loyalty_stub.py`
- **Model**: `fix.loyalty.tier` (Table: `fix_loyalty_tier`)
  - *Description*: Loyalty Membership Tier
  - *Source File*: `models/fix_loyalty_tier.py`
- **Model**: `fix.loyalty.voucher` (Table: `fix_loyalty_voucher`)
  - *Description*: Loyalty Privilege Voucher
  - *Source File*: `models/fix_loyalty_voucher.py`

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
   python3 -m odoo -u cd_loyalty -d 1000fix_prod --stop-after-init
   ```
2. **Configuration Verification**:
   - Verify access control rights in `security/ir.model.access.csv`.
   - Ensure company and operating unit isolation policies (`res.company`, `fix.operating.unit`) are active.

### 4.3 Lifecycle controls added by the A03 P2 repair (November 2026)
- **Earning**: the R8 relay delivers `service_order.closed` to `fix.loyalty.account.consume_service_order_closed`. Each account earns once per order and programme (receipt key `earn:service_order:<order>:<programme>` in `fix.loyalty.event.receipt`), using the live scheme's earn rules or the programme rate. A frozen or suspended wallet keeps the earned line as a draft. The same event converts a pending referral whose referee it is.
- **Merges**: `party.merged` is consumed by `consume_party_merged`. A lone victim account is re-pointed; when both parties hold an account, the balance moves as posted `merge_transfer` lines and the victim account closes. A frozen victim's points are not moved (`loyalty.merge_transfer_blocked`).
- **Balance**: `points_balance` is derived from posted ledger lines. The daily cron *Loyalty: reconcile every balance with its posted ledger* (or the account's *Reconcile Balance* button) records any drift in `balance_drift`, publishes `loyalty.balance_drift` and re-derives the balance.
- **Fraud-lock release**: requested with *Request Fraud-Lock Release*; decided by a DOFA Tier 2 holder from the M63 inbox (`loyalty_release` decision domain). Pressing `action_unfreeze` directly is refused.
- **Expiry**: point expiry runs one account per savepoint (a frozen account is retried next day); *Loyalty: expire vouchers past their Valid Until date* runs daily.
- **Business switches on the programme (DOFA Tier 3 to change)**: `expected_breakage_pct` (IFRS 15, default 0 = gross liability), `referral_referrer_points` and `referral_referee_points` (default 0 = no award). Each awaits a business ruling.

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
SELECT count(*) FROM fix_loyalty_account WHERE active = true;

-- Inspect recent state transitions (last 24 hours)
SELECT id, create_date, write_date, state 
FROM fix_loyalty_account 
WHERE write_date >= NOW() - INTERVAL '24 hours' 
ORDER BY write_date DESC LIMIT 50;
```

### 5.3 Incident Severity & Escalation Paths
- **Severity 1 (Critical Outage)**: System unable to process records or database locks. Escalate to Lead Systems Architect and On-Call Operations Lead.
- **Severity 2 (Degraded Performance)**: Specific actions exceeding 200ms latency budget. File ticket with Squad `Customer Engagement`.
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
py -3.12 -m pytest addons/domain/b_customer_engagement/cd_loyalty -q -o 'addopts='
```

---

*Last Updated: 2026-10-20 · Approved by: 1000FiX Architecture Review Board (ARB)*
