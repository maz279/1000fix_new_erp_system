# D-037: Kafka Event Bus Migration & Redis Streams Retirement (P09-M01 / R07-M01)

**Status:** APPROVED  
**Date:** 2026-10-18  
**Deciders:** Enterprise Architecture, Integration Lead, Platform Lead  
**Governing Documents:** AR-009, IN-003, PGD-000, ADR-017  

---

## 1. Context & Problem Statement

In Waves W1–W5, 1000FiX ERP utilized Redis 7.2 Streams (`fix:events:*`) on port 6380 as the primary event bus. While Redis Streams was sufficient for early stage delivery, scaling to 988 domain events across 67 modules, 12 portals, strict statutory audit requirements (M51 VAT Mushak 6.3/9.1 compliance), high-throughput analytics, and partition-level horizontal scalability required migrating to a high-availability event streaming backbone.

---

## 2. Decision

We have adopted a **3-Node Apache Kafka HA Cluster with native KRaft consensus** as the enterprise event bus, retiring Redis Streams from messaging while retaining Redis for caching, sessions, and distributed locks.

### Key Architectural Decisions:
1. **3-Node KRaft HA Cluster (No ZooKeeper):**
   - Nodes `kafka-1`, `kafka-2`, `kafka-3` form a KRaft quorum with replication factor 3 and `min.insync.replicas=2`.
   - Single-broker loss drill verified 100% zero data loss and automated catch-up parity upon rejoin.
2. **Expand-Contract Dual-Write Outbox (EP-05):**
   - `fix.event.outbox` extended with dual-write tracking (`bus_target`, `kafka_published_at`, `kafka_partition`, `kafka_offset`, `payload_sha256`).
   - Dual-write publisher validated 100% parity across Redis Streams and Kafka cluster without performance degradation.
3. **Phased Consumer Group Cutover with Per-Group Rollback:**
   - 6 canonical consumer groups cut over through `BUS_REDIS` -> `BUS_DUAL` -> `BUS_KAFKA`.
   - Rollback drill demonstrated instant reversion to Redis Streams in < 5 seconds with zero blast radius on other consumer groups.
4. **Time-Travel Replay & DLQ Isolation (EP-06):**
   - Partition offset seek by timestamp enables statutory re-construction of VAT registers.
   - Poison-pill failures route to `<topic>.dlq` with diagnostic headers, preventing consumer stall and enabling re-drive.
5. **Schema Registry 988-Event Catalogue (IN-003):**
   - Full audit of all 988 catalogued events with 0 schema diff and 100% ADR-017 compliance.

---

## 3. Consequences

### Positive
- Strict horizontal scalability and partition-level parallelism.
- High availability: system remains fully operable during single broker failure or maintenance.
- Full statutory audit capability via offset seek and event replay.
- Isolation of failing events through DLQs.

### Negative / Trade-offs
- Increased infrastructure footprint (3 Kafka broker containers vs 1 Redis container).
- Operational complexity of partition management and consumer group offset management, mitigated by `libs.py.fix_events` centralized client and operational runbooks.
