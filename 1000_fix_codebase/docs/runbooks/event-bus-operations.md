# Event Bus Operations & Disaster Recovery Runbook (P09-M01 / R07-M01)

**System:** 1000FiX ERP Platform v2.0  
**Component:** Apache Kafka HA Event Bus & Outbox Infrastructure  
**Governing Documents:** AR-009, IN-003, ADR-017, D-037  
**Classification:** Internal Operations Runbook  

---

## 1. Overview & Architecture

The 1000FiX event messaging backbone has migrated from single-node Redis Streams (W1–W5) to a high-availability 3-node Apache Kafka cluster (W6+) deployed with native KRaft consensus (no ZooKeeper dependency).

### Cluster Topography
- **Nodes:** `kafka-1` (Node 1), `kafka-2` (Node 2), `kafka-3` (Node 3)
- **Quorum:** KRaft voters `1@kafka-1:9093,2@kafka-2:9093,3@kafka-3:9093`
- **Replication Factor:** 3 (every partition replicated on all 3 brokers)
- **Min In-Sync Replicas (min.insync.replicas):** 2
- **Ports (Internal / Loopback):** `127.0.0.1:9092` (Node 1), `127.0.0.1:9094` (Node 2), `127.0.0.1:9095` (Node 3)
- **Outbox Publisher:** Transactional Outbox pattern (`fix.event.outbox` via `libs.py.fix_events.publish`)

---

## 2. Standard Operating Procedures (SOP)

### 2.1 Cluster Health & Quorum Check
To verify KRaft quorum and broker health:
```bash
docker compose -f infra/compose/docker-compose.asset-ml.yml ps kafka-1 kafka-2 kafka-3
python tooling/events/verify_kafka_cluster.py
```

### 2.2 Broker Loss & Failure Recovery Drill
The cluster survives the loss of any single broker with zero data loss (`min.insync.replicas=2`, `acks=all`).
- **Simulating loss:**
  ```bash
  docker compose -f infra/compose/docker-compose.asset-ml.yml stop kafka-2
  ```
- **Confirming remaining quorum:**
  Brokers `kafka-1` and `kafka-3` maintain active quorum and continue processing incoming outbox transactions.
- **Recovering broker:**
  ```bash
  docker compose -f infra/compose/docker-compose.asset-ml.yml start kafka-2
  ```
  Broker 2 catches up to current high watermark from ISR peers automatically.

---

## 3. Consumer Group Cutover & Rollback (EP-05)

### Canonical Consumer Groups:
1. `notification-dispatcher` (P08)
2. `inventory-syncer` (P04)
3. `audit-logger` (P02)
4. `bi-streaming` (P07)
5. `sla-calculator` (P01)
6. `evat-reporter` (P05)

### Per-Group Emergency Rollback
If consumer lag exceeds 500 messages or an unhandled exception rate spikes:
```python
from libs.py.fix_events.migration import get_migration_manager
mgr = get_migration_manager()
# Instantly roll back target group to Redis Streams in < 5 seconds
mgr.rollback_group("inventory-syncer", reason="Lag spike > 500 msgs")
```
- Remaining 5 consumer groups continue uninterrupted on Kafka (zero blast radius propagation).

---

## 4. Dead-Letter Queue (DLQ) Remediation & Re-Drive

### DLQ Topics
Every domain topic `<topic>` is provisioned with a corresponding `<topic>.dlq` dead-letter queue.

### Poison Pill Handling
When a consumer fails after retries:
1. Message is intercepted and written to `<topic>.dlq`.
2. Diagnostic headers attached: `dlq_reason`, `original_topic`, `original_offset`, `failed_at_utc`.
3. Consumer offset advances, preventing head-of-line blocking.

### Re-Drive Procedure
To remediate and re-inject dead-lettered events:
```python
from libs.py.fix_events.replay import get_replay_engine
engine = get_replay_engine()

def remediate_payload(payload: dict) -> dict:
    payload["schema_fixed"] = True
    return payload

engine.replay_dlq(
    dlq_topic="fix.events.vat.dlq",
    target_topic="fix.events.vat",
    remediator=remediate_payload,
)
```

---

## 5. Time-Travel Replay (EP-06 / M51 Compliance)

For statutory audit audits (NBR VAT Mushak 6.3 / 9.1) or disaster state reconstruction:
```python
from libs.py.fix_events.replay import get_replay_engine
engine = get_replay_engine()

# Replay all tax events from beginning of tax period
engine.replay_from_timestamp(
    topic="fix.events.vat",
    timestamp="2026-10-01T00:00:00Z",
    target_handler=my_vat_register_builder,
)
```

---

## 6. Redis Streams Retirement

Redis 7.2 (`compose-redis-1`, port 6380) is formally retired as the message bus:
- Outbox emitter targets Kafka as primary bus.
- Redis remains exclusively reserved for:
  - Ephemeral cache (FastAPI and Next.js ISR)
  - User session tokens
  - Distributed redlocks (`libs.py.fix_lock`)
