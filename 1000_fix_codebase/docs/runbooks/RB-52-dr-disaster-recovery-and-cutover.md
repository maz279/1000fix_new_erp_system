# RB-52 — Disaster Recovery & Production Cutover Runbook
## 1000FiX ERP System v2.0 · Category 12 (Release, Deployment & Transition) · PE-001 / TSS §21.3 Conformance

| Metadata | Details |
|---|---|
| **Runbook ID** | `RB-52-DISASTER-RECOVERY-CUTOVER` |
| **Document Version** | 1.0 (Production Operational Readiness) |
| **Governance Standard** | ISO/IEC 27031:2011 · BCM Policy · PE-001 §6.2 · TSS §21.3 · NFR-007 |
| **Target Architecture** | Primary DC (Z4 Sovereign Zone) to Warm Standby DR (Bangladesh Resident Standby) |
| **Recovery Metrics** | **RPO ≤ 15 minutes** (Continuous Streaming WAL) · **RTO ≤ 2 hours** |
| **Owning Lead** | Principal Infrastructure & SRE Lead with Database Administrator |
| **Approving Authority** | Chief Technology Officer (CTO) with Disaster Recovery Board |
| **Exit Criterion** | Milestone R10-M04 Task T03 — Successful failover, promotion, data consistency, and failback verification |

---

## 1. Executive Summary & Statutory Baseline

This runbook defines the authoritative operational protocol for handling catastrophic primary site loss, primary database failure, or scheduled disaster recovery drills for the 1000FiX Integrated Smart ERP System.

Under the sovereign split-residency architecture of Bangladesh (PDPA §4.5.4, Rule `SC-002`, and `PE-001` §6.2):
1. **Sovereign Residency Invariant (`Z4`)**: The DR warm standby is physically hosted inside an accredited Tier-III datacenter within the borders of Bangladesh. No sovereign data is ever replicated or diverted to cross-border zones during failover.
2. **Streaming Replication & Recovery Point Objective (`RPO`)**: The primary PostgreSQL 17 cluster streams write-ahead logs (WAL) continuously to the standby node via secure TLS replication slots (`postgres_dr_standby`). Maximum acceptable replication delay is **15 minutes**.
3. **Recovery Time Objective (`RTO`)**: The end-to-end failover sequence—from failure declaration to public portal traffic restoration—must complete in **under 2 hours** (typically $< 10\text{ minutes}$ automated).

---

## 2. DR Architecture & Topology

```
┌────────────────────────────────────────────────────────┐
│             PRIMARY DATACENTER (DHAKA DC-1)            │
│  PostgreSQL 17 Primary (Port 5442)                     │
│  wal_level = replica, archive_mode = on                │
└──────────────────────────┬─────────────────────────────┘
                           │ TLS Replication Stream
                           │ (RPO <= 15 minutes)
                           ▼
┌────────────────────────────────────────────────────────┐
│         WARM STANDBY DATACENTER (CHATTOGRAM DC-2)      │
│  PostgreSQL 17 Standby (Port 5443)                     │
│  hot_standby = on, recovery target = latest            │
│  Kong API Gateway Standby + Odoo Standby (Port 8079)   │
└────────────────────────────────────────────────────────┘
```

---

## 3. Seven-Step Disaster Recovery Cutover Procedure

### Step 1: Incident Assessment & Outage Declaration (T+0 min)
- **Condition**: Primary datacenter unreachable, hardware failure, unrecoverable corruption, or planned DR drill.
- **Action**: Incident Commander convenes the DR Emergency Response Team.
- **Notification**: Automated PagerDuty/Novu alert broadcasts to `#incident-sev1` Slack channel.

### Step 2: Replication Lag & RPO Assessment (T+2 min)
- Query standby replication status:
  ```bash
  psql -U fix_admin -d fix_production -c "SELECT pg_last_wal_receive_lsn(), pg_last_wal_replay_lsn(), now() - pg_last_xact_replay_timestamp() AS lag;"
  ```
- **Validation Gate**: If lag is $\le 15\text{ minutes}$, proceed with standard automated failover. If lag exceeds 15 minutes, notify CTO for manual loss-window sign-off.

### Step 3: Split-Brain Prevention & Primary Fencing (T+4 min)
- Prevent dual-master split-brain:
  1. Revoke network ingress to primary PostgreSQL (IP routing blackhole / shutdown).
  2. Stop primary container:
     ```bash
     docker compose -f infra/compose/docker-compose.prod.yml stop postgres-prod
     ```
  3. Validate primary port 5442 is completely unreachable.

### Step 4: Standby Promotion to Read-Write Primary (T+6 min)
- Issue PostgreSQL promotion command on DR node:
  ```bash
  psql -U fix_admin -d fix_production -c "SELECT pg_promote(wait => true, wait_seconds => 60);"
  ```
- Verify node has transitioned out of recovery mode:
  ```bash
  psql -U fix_admin -d fix_production -c "SELECT pg_is_in_recovery();" # Must return 'f'
  ```

### Step 5: Service Stack Promotion & Upstream Re-Routing (T+8 min)
- Update environment routing at Kong / Cloudflare Edge:
  1. Point Kong upstream `erp_backend_upstream` to `127.0.0.1:8079` (DR Odoo).
  2. Point Redis client connection pool to `redis-dr` (standby promoted to master via `REPLICAOF NO ONE`).
- Clear edge CDN cache:
  ```bash
  curl -X POST https://api.cloudflare.com/client/v4/zones/${CF_ZONE}/purge_cache -d '{"purge_everything":true}'
  ```

### Step 6: Post-Cutover Sanity Verification (T+10 min)
- Execute synthetic health probes:
  - Check portal endpoints: `/api/v1/healthz` returns HTTP 200.
  - Check payment webhooks: bKash / Nagad callback ingress is green.
  - Create synthetic test work order to confirm database read-write operation.
  - Verify zero database constraint violations or sequence stalls.

### Step 7: Failback & Re-Synchronization (Post-Incident)
- Once the primary site is restored:
  1. Take differential snapshot of DR database.
  2. Reconfigure primary host as replica tracking DR (`pg_rewind`).
  3. Resynchronize WAL streams.
  4. Schedule planned maintenance window (30-second connection pause) to return primary role to DC-1.

---

## 4. Automation & Rehearsal Verification

The operational validity of this runbook is automatically asserted via `tooling/dr/run_r10_m04_dr_rehearsal.py`, verifying:
1. Replication slot readiness and RPO $\le 15\text{ min}$.
2. Sub-minute promotion time ($< 60\text{ s}$, well inside the 2-hour RTO).
3. Data consistency across transactional tables (`res_partner`, `fix_work_order`, `account_move`).
4. Evidence output emitted to `docs/traceability/evidence/r10-m04-dr-rehearsal-evidence.json`.
