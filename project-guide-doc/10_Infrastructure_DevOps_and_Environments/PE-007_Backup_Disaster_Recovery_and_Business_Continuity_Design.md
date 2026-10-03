---
id: PE-007
title: Backup, Disaster Recovery & Business Continuity Design
category: 10 — Infrastructure, DevOps & Environments
code: PE
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-19
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Platform Engineering Lead
approver: CTO with CFO, Legal Counsel and Design Authority (constituted under GV-002)
standards_basis: >
  ISO 22301:2019 business continuity · ISO/IEC 27031:2011 ICT readiness ·
  NIST SP 800-34 Rev.1 contingency planning · 3-2-1-1-0 backup rule ·
  PostgreSQL PITR / WAL archiving · Uptime Institute Tier topology
traces_to: >
  PGD-000 PE-007 · PE-001 §3 sites, §8.2 link · PE-002 §5.12 dr · PE-003 §13 bootstrap ·
  PE-005 RC-05 · SC-007 §9 · AR-001 §8.4 DR-01…DR-04 · OP-012 · OP-014 ·
  audit OP-01 (critical), OP-02 (high) · NFR-007, NFR-051, NFR-052, NFR-050, NFR-086b
depends_on: PE-001 · PE-002 · PE-003 · PE-005 · SC-007 · DA-006
verified_on: 2026-08-19
priority: P0
needed_by: W1
enumeration_timestamp: 2026-08-19 01:45 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# PE-007 — Backup, Disaster Recovery & Business Continuity Design

### Category 10 · Code `PE` · ISO 22301:2019 · ISO/IEC 27031:2011 · NIST SP 800-34 Rev.1

---

> **This document exists to close the estate's oldest open critical finding.**
>
> **`AUDIT-017` `OP-01` (critical, open):** *"There is no lawful DR path for Bangladesh-resident
> personal data… In an outage affecting the resident store, an engineer at 02:00 has a choice
> between a two-hour RTO and a cross-border transfer of exactly the data category the Act singles
> out. **That leaves no route that both restores service and complies, and the constraint is
> invisible until the night it binds.**"*
>
> **`AUDIT-017` `OP-02` (high, open):** *"The `dr` environment is named in the architecture and
> provisioned nowhere… `NFR-007` is currently an aspiration with no infrastructure behind it, and
> `OP-012` is a design document rather than an executable playbook. The honest RAG status for DR
> readiness is **red**. **This is the largest unfunded operational obligation the content register
> has surfaced.**"*
>
> **State at 2026-08-19 01:45 (+06):**
>
> | `OP-02`'s three named preconditions of `NFR-007` | State |
> |---|---|
> | Continuous WAL archiving to a **separate failure domain** | **Not provisioned** |
> | An **immutable backup copy outside the primary provider account** | **Not provisioned** |
> | A **rehearsed failover** (`NFR-051`, twice yearly) | **No exercise scheduled anywhere** |
> | P0 integrations with a **tested** manual fallback (`NFR-050`) | **0 of 13** |

---

## 1. Purpose

`OP-012` writes the disaster-recovery **playbook**. It is a good playbook, and it runs on
infrastructure that does not exist — which is `OP-02`'s finding, stated by `OP-012`'s own author.

This document designs the infrastructure the playbook assumes: what is backed up, how often, where
it is held, how long it is kept, how restoration is **proven** rather than assumed, how failover
works for each tier including the one that cannot leave the country, what degraded operation looks
like, and the drill programme that turns `NFR-007` from an aspiration into evidence.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | **The recovery objectives**, per tier, including where they legitimately differ |
| 2 | **Backup design** — what, how, where, how long, and the 3-2-1-1-0 realisation |
| 3 | **Continuous WAL archiving** to a separate failure domain — `OP-02` precondition 1 |
| 4 | **`BKP-3`, the immutable copy outside the primary account** — `OP-02` precondition 2 |
| 5 | **Restore verification** — `NFR-052`'s weekly automated test, made meaningful |
| 6 | **Failover** per tier, and the promotion sequence |
| 7 | **`Z4` recovery — the `OP-01` answer**, built on `SC-007` §9 and `PE-001` §3.3 |
| 8 | **Degraded operation** — `SC-007` §9.2's route 1, made testable |
| 9 | Scenario coverage: site loss, data corruption, **ransomware, account compromise** |
| 10 | **The drill programme** — `NFR-051`, with what a drill must prove |
| 11 | Business continuity: manual fallbacks, `NFR-050`'s 0-of-13 |
| 12 | Recovery of the recovery system itself |
| 13 | Fitness functions `FF-155`…`FF-164` |

**Explicitly out of scope**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| Sites, the second site, the private link | **`PE-001`** §3, §8.2 | This document uses them |
| The `dr` environment's specification | **`PE-002`** §5.12 | Specified there; **operated here** |
| Scaling `dr` compute on failover | **`PE-003`** | `PE-002-D-07`'s warm standby mechanism |
| The residency classification and transfer gate | **`SC-007`** | This document recovers what `SC-007` classifies |
| Data retention and erasure policy | `DA-006` | §4.5 implements its schedule for backups |
| Incident command, comms, escalation | `SV-*`, `OP-004`, `OP-013` | This document recovers; `SV-*` runs the incident |
| The DR **playbook** — step-by-step operator procedure | **`OP-012`** | This document is the design `OP-012` executes |
| Manual fallback **procedures** per integration | `OP-014` | §11 states the obligation; `OP-014` writes the steps |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| **CTO, CFO, Legal Counsel** | §7 — the `Z4` decision, which is theirs and is unmade |
| Platform engineers | §4–§9 |
| **`OP-012`'s author** | §6 and §7 are the infrastructure its playbook assumes |
| Head of Service | §10's drills, §11's continuity |
| DPO | §7 — recovery as a residency question |
| Steering Committee | §12 — the RAG status and what changes it |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Concept | Conformance | Departure and rationale |
|---|---|---|---|
| **ISO 22301:2019** | Business continuity management | §11 — impact-driven continuity, exercised and reviewed | **Partial.** A full BIA is `GV-005`/business's; §11.1 states what this document assumes from it |
| **ISO/IEC 27031:2011** | ICT readiness for business continuity | §3's objectives, §10's exercise regime | None |
| **NIST SP 800-34 Rev.1** | Contingency planning — the seven-step process | §4–§10 map to steps 3–6 | None |
| **3-2-1-1-0** | 3 copies, 2 media, 1 offsite, **1 immutable, 0 errors on verification** | §4.2 | None — and the **"0"** is `NFR-052`'s weekly restore test |
| **PostgreSQL PITR / WAL archiving** | Point-in-time recovery | §4.3 | None |
| Uptime Institute Tier topology | Facility resilience | Inherited from `PE-001` §3.3 | |

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| **`AUDIT-017` `OP-01`, `OP-02`** | `../../project_content/_AUDIT/AUDIT-017_*.md` | **The two findings this document exists to close** |
| **`OP-012`** | `../../project_content/17_Operations_Support_and_Runbooks/OP-012_*.md` | The DR playbook, its three routes, `RD-01`, `HC-01`'s monthly RAG |
| `OP-014` | Ibid. | Manual fallback procedures; **13 P0 integrations enumerated** |
| **`SC-007` §9** | `../05_Security_Privacy_and_Compliance/SC-007_*.md` | The three routes; **`DG-1`…`DG-6` degraded mode**; options A/B/C; `SC-007-DR-1` |
| `AR-001` §8.4 | `../02_Architecture_and_Design/AR-001_*.md` | `DR-01`…`DR-04` as deployment-view constraints |
| **`PE-001`** §3, §8.2 | `./PE-001_*.md` | **`RGN-S`, `BD-R`, `BKP-3`**; three named in-country facilities; the private link |
| `PE-002` §5.12 | `./PE-002_*.md` | The `dr` specification and its warm-standby shape |
| `PE-003` §13 | `./PE-003_*.md` | **Bootstrap — the first step of a from-nothing rebuild** |
| `PE-005` `RC-05`, `PE-005-F-01` | `./PE-005_*.md` | **The `BD-R` registry replica dependency** |
| `05-06` | `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_*.md` | `NFR-007`, `NFR-050`, `NFR-051`, `NFR-052`, `NFR-086b` |
| `DA-006` | `../03_Data_and_Information_Architecture/DA-006_*.md` | Retention and erasure; **`BK-02` post-restore suppression** |

### 2.3 Audit findings this document closes or contributes to

| Finding | Source | Disposition |
|---|---|---|
| **`OP-01` (critical)** — no lawful DR path for `Z4` | `AUDIT-017` | **Designed, not closed.** §7 builds route 2 on `PE-001` §3.3's named facilities and designs route 1 properly. **Closes on a CTO/CFO procurement decision** — §7.5 |
| **`OP-02` (high)** — `dr` provisioned nowhere; three preconditions absent | `AUDIT-017` | **All three designed**: §4.3 WAL archiving, §4.4 `BKP-3`, §10 the drill programme. **Closes on provisioning and the first drill** |
| `OP-012` `OI-02`, `OI-03`, `OI-07` | `OP-012` | §7, §4.4, §10 respectively |
| **`NFR-050`** — every P0 integration has a **tested** fallback | `05-06` | §11.3 — **0 of 13 today**; `IN-008` §9 defines what "tested" means; this document schedules it |
| `NFR-052` — automated restore test weekly | `05-06` | §5 — **and §5.2 states why the obvious implementation is worthless** |
| `DA-006` `BK-02` — post-restore suppression | `DA-006` | §4.6 |
| `PE-005-F-01` — `BD-R` registry reachability | `PE-005` | §9.4 — **confirmed as a recovery dependency** |
| `SC-007-F-07` — option C is the current position **by default, not by decision** | `SC-007` | §7.5 forces the decision to be taken explicitly |

---

## 3. Recovery Objectives

### 3.1 The stated objectives

| NFR | Objective | Value |
|---|---|---|
| **`NFR-007`** | RPO / RTO | **RPO ≤ 15 minutes · RTO ≤ 2 hours** |
| `NFR-051` | DR drill | **Twice yearly, full failover, documented results** |
| `NFR-052` | Backup verification | **Automated restore test, weekly** |
| `NFR-050` | Graceful degradation | Every P0 integration has a documented, **tested** manual fallback |

### 3.2 Objectives per tier — because one number is not honest

> **`PE-007-D-01`. Recovery objectives are stated per tier. A single estate-wide RTO conceals the
> tier that cannot meet it.**

| Tier | RPO | RTO | Basis |
|---|---|---|---|
| **`Z3` regional data** | **≤ 15 min** | **≤ 2 h** | `NFR-007`; streaming replication + PITR |
| `Z2` application | n/a — stateless | **≤ 2 h**, and in practice minutes | Scaled from IaC (`PE-003`) |
| `Z1` ingress | n/a | Minutes | Provider HA |
| Object storage | ≤ 15 min | ≤ 2 h | Replicated |
| Event bus | **≤ 0** for committed events | ≤ 2 h | **The outbox is the durability guarantee** (`AR-009` §5.1) — events survive in the source database |
| **`Z4` resident** | **≤ 15 min *to an in-country standby*** | **UNBOUNDED until §7.5 is decided** | **`SC-007` §9.5** |
| **Search / analytical (ClickHouse, indexes)** | n/a — **rebuildable** | Hours to days | §3.4 |

### 3.3 The `Z4` line, stated plainly

`SC-007` §9.5: *"Until option A or B is in place, `NFR-007` does not apply to residency-classified
data, and the programme must say so… **Availability reporting must state the `Z4` RTO separately**,
because a green estate-level RTO conceals an unbounded one."*

> **`PE-007-F-01`. The estate's DR RAG status is red, and it is red for one reason: `Z4` has no
> recovery target.** Everything else in this document is buildable with a purchase order. **§7.5 is
> a decision, and it has been available to take since `OP-01` was raised.**

### 3.4 What is deliberately not recovered

| Item | Position |
|---|---|
| ClickHouse warehouse | **Rebuilt from the primary and the event stream.** Backing up a derived store doubles cost to shorten a rebuild |
| Search indexes | **Rebuilt** |
| Read replicas | **Recreated from the primary** |
| Caches (Redis) — cache keyspace | **Rebuilt.** Cold cache is a performance event, not a data-loss one |
| **Redis — session keyspace** | **Replicated.** Losing sessions logs out 800 internal and 75,000 portal users simultaneously — a recovery that creates an incident |
| Non-production environments | **Rebuilt from IaC** (`PE-003`) and re-cloned (`PE-002` §6.3) |

> **The distinction that matters is derived vs originating.** A derived store is recovered by
> recomputation; an originating store is recovered from backup. **`PE-007-D-02`: only originating
> data is backed up, and every derived store carries a documented, timed rebuild procedure** —
> because a rebuild whose duration nobody has measured is an unbounded RTO wearing a different hat.

---

## 4. Backup Design

### 4.1 What is backed up

| Class | Contents | Method | RPO |
|---|---|---|---|
| **`Z3` primary database** | All originating transactional data | **Base backup + continuous WAL** | **≤ 15 min, in practice seconds** |
| **`Z4` resident database** | NID, passport, TIN, biometric templates, recovered data, seller KYC | **Base backup + continuous WAL, in country** | ≤ 15 min |
| TimescaleDB | GPS, telemetry | Base + WAL; **compression-aware** | ≤ 15 min |
| **Object storage** | Documents, evidence, signatures, attachments | **Versioning + cross-region replication** | Near zero |
| **Secrets (Vault)** | Secret material and policies | **Encrypted snapshot; key escrow separate** | Daily; §4.7 |
| **IaC state** | Six layers × sites (`PE-003` §6.3) | Versioned backend + snapshot | Every write |
| Configuration | Environment configuration (`PE-009`) | In Git; the repository is itself backed up | Every commit |
| Container images | Production digests | Registry replication (`PE-005` `RC-05`) | Per push |
| **Event registry & schemas** | `IN-003`'s registrations | With the platform database | ≤ 15 min |
| **Audit and access logs** | `Z4` per-read log, privileged sessions | **Write-once storage** | Near zero |

### 4.2 The 3-2-1-1-0 realisation

| Rule | Realisation |
|---|---|
| **3 copies** | Production · `dr` replica · **`BKP-3`** |
| **2 media / failure domains** | Block storage (replica) + object storage (`BKP-3`) |
| **1 offsite** | `RGN-S`, a different availability zone or region (`PE-001` §3.1) |
| **1 immutable** | **`BKP-3`, retention-locked, outside the primary provider account** — §4.4 |
| **0 errors** | **`NFR-052`'s weekly restore test** — §5 |

> **`Z4` has its own 3-2-1-1-0, entirely inside Bangladesh.** Its three copies are the production
> HA pair, the in-country standby, and an in-country immutable copy. **None of them may be
> regional** (`SC-007-DR-1`).

### 4.3 Continuous WAL archiving — `OP-02` precondition 1

| # | Rule |
|---|---|
| **WA-01** | **WAL is archived continuously** to a destination in a **separate failure domain** from the primary |
| **WA-02** | The archive destination is **not** the same storage account or region as the database's own storage |
| **WA-03** | **Archive success is monitored**, and a failure to archive alerts within **five minutes**. `FF-155` |
| **WA-04** | **Archive lag is the RPO measurement.** `NFR-007`'s 15 minutes is measured here, not asserted |
| **WA-05** | A base backup is taken on a schedule that keeps **PITR replay time inside the RTO** — §4.3.1 |
| **WA-06** | `Z4`'s WAL archive is **in country**, in a separate in-country failure domain |

#### 4.3.1 The relationship nobody states

**Base backup frequency is an RTO decision, not a storage decision.** Recovery time is
*restore the base* + *replay the WAL since it*. A weekly base with six days of WAL to replay can
exceed a two-hour RTO on a 2 TB database regardless of how fast the restore is.

| # | Rule |
|---|---|
| **BB-01** | Base backups **daily** for `Z3` and `Z4` |
| **BB-02** | **Replay time is measured, not assumed** — §5.3's restore test records it |
| **BB-03** | **If measured replay time approaches the RTO, base frequency increases.** The trigger is the measurement |

### 4.4 `BKP-3` — the immutable copy, `OP-02` precondition 2

`OP-02`: *"Without it, the ransomware and account-compromise scenarios in `OP-012` §5 have no
assured recovery path."*

| # | Rule |
|---|---|
| **IM-01** | **A copy of every backup class in a separate account or with a separate provider** |
| **IM-02** | **Object-lock / retention-lock in compliance mode** — deletion is impossible until expiry, **including by the account owner** |
| **IM-03** | **Write credentials are distinct** from every other credential in the estate and are **not held by any workload** — the backup job writes; nothing deletes |
| **IM-04** | **Restore credentials are break-glass** (`PE-009`) |
| **IM-05** | **Immutability is verified quarterly** by attempting a deletion that **must fail** (`PE-001` `W-04`). A retention lock nobody has tested is a setting, not a control. `FF-156` |
| **IM-06** | Retention: **35 days minimum** for operational recovery; longer where `DA-006` requires |
| **IM-07** | **`Z4`'s immutable copy is in country** and separately credentialled |

> **`IM-03` is the control that defeats the scenario the others do not.** A ransomware actor with
> the estate's cloud credentials can delete replicas, snapshots and lifecycle-managed backups.
> **They cannot delete an object under a compliance-mode retention lock in an account whose
> credentials are not in the estate.**

### 4.5 Retention

| Class | Operational retention | Longer retention | Basis |
|---|---|---|---|
| `Z3` database | **35 days** PITR | Per `DA-006`'s schedule for the data classes within | `DA-006` |
| `Z4` database | **35 days** PITR, in country | Per `DA-006`; **erasure obligations apply** — §4.6 | `DA-006`, `NFR-093` |
| Object storage | 35 days versioning | Documents per their own retention | `DA-006`, `LG-009` |
| **Financial records** | — | **7 years** | Statutory; `AR-009` §8.4 |
| Audit and access logs | 35 days hot | **Per `SC-008`'s obligation period** | `SC-008` |
| Secrets snapshots | 35 days | — | |
| IaC state | 90 days | — | `PE-003` `ST-05` |

### 4.6 The tension backups create with erasure

> **`PE-007-F-02`. A backup is a copy, and a copy defeats erasure.**

`NFR-093` requires personal data erased on request. A 35-day backup chain means erased data persists
in backups for up to 35 days after erasure.

| # | Position |
|---|---|
| **ER-01** | **Backups are not selectively edited.** Rewriting a backup to remove one subject destroys its integrity and its restorability |
| **ER-02** | **The accepted position is time-bounded persistence**: erasure is applied to live systems immediately, and backups age out within the retention window |
| **ER-03** | **`DA-006` `BK-02` post-restore suppression is mandatory**: if a backup is restored, **erasure requests received since that backup are re-applied before the system returns to service** |
| **ER-04** | The suppression list is itself backed up, and **it is restored first** |
| **ER-05** | This position is **documented in the privacy notice and the DPIA** (`SC-003`), not left implicit |

> **`ER-03` is a recovery step with a legal consequence, and it belongs in the runbook.** A restore
> that returns erased personal data to production is a fresh processing of data the subject asked
> to have removed. **`OP-012`'s restore procedure must carry it**; referred as `PE-A-05`.

### 4.7 Backing up the secret manager

| # | Rule |
|---|---|
| **SB-01** | Vault state is snapshotted daily, **encrypted** |
| **SB-02** | **Unseal key material is escrowed separately** from the snapshot, split among named holders |
| **SB-03** | **`Z4`'s key material is escrowed in country** (`SC-006` `ES-3`) and never leaves it |
| **SB-04** | **Escrow recovery is rehearsed annually**, with the actual holders |
| **SB-05** | **A backup nobody can decrypt is not a backup.** `FF-157` verifies that the escrow can be assembled |

> **`SB-05` is the failure mode that ends companies.** Every other backup in this document is
> useless if the secret manager cannot be unsealed — and **unseal-key escrow is the one recovery
> path that depends on people rather than systems**, which is why §10.3 drills it with the actual
> holders rather than their deputies.

---

## 5. Restore Verification

### 5.1 What `NFR-052` requires

*"Automated restore test weekly."*

### 5.2 Why the obvious implementation is worthless

> **`PE-007-D-03`. A restore test that only checks the restore completed is not a restore test.**

A job that restores a backup and reports success proves the file was readable. **It does not prove
the data is correct, complete, current, or usable by the application** — and every one of those has
failed in real recoveries while the restore itself succeeded.

### 5.3 What the test must do

| # | Step |
|---|---|
| **RT-01** | Restore the **most recent** base backup into an isolated environment |
| **RT-02** | **Replay WAL to a target time**, exercising PITR rather than only the base |
| **RT-03** | **Measure and record**: restore duration, **replay duration**, total time to usable |
| **RT-04** | **Verify integrity**: row counts against expectation, referential integrity, checksum validation |
| **RT-05** | **Verify currency**: the most recent transaction present is within the RPO |
| **RT-06** | **Verify usability**: start the application against the restored database and run a **read and a write smoke test** |
| **RT-07** | **Compare the measured recovery time against `NFR-007`.** A test that takes 4 hours is a **failing** test even if every check passes |
| **RT-08** | Record the result as a **wave-gate artefact** (`FF-158`) |
| **RT-09** | **The restored environment is destroyed afterwards** — and it never contains unmasked personal data outside its lawful location (§5.4) |

### 5.4 The residency problem in restore testing

> **`PE-007-F-03`. Testing a `Z4` restore requires restoring residency-classified data, which may
> only happen in country.**

| # | Rule |
|---|---|
| **RZ-01** | **`Z4` restore tests run in Bangladesh**, in an isolated in-country environment |
| **RZ-02** | They **cannot** run in the regional test harness — that would be `TF-4`, a notifiable transfer (`SC-007` §6.1) |
| **RZ-03** | **This requires in-country test capacity**, which is a second reason `PE-001` §3.3's facility decision cannot be deferred |
| **RZ-04** | Until the in-country target exists, **`Z4` restore is unverified**, and `NFR-052` is unmet for that tier |

### 5.5 Cadence

| Test | Frequency | Scope |
|---|---|---|
| **Automated restore verification** | **Weekly** | `Z3` primary, `RT-01`…`RT-08` |
| `Z4` restore verification | **Weekly**, in country | Same, once §7.5 is decided |
| Object-storage restore | Monthly | Sample-based |
| **Secret escrow assembly** | **Annually**, with the actual holders | §4.7 |
| **`BKP-3` immutability** | **Quarterly** — a deletion that must fail | `IM-05` |
| **Full DR failover** | **Twice yearly** | §10 |

---

## 6. Failover

### 6.1 Declaring a disaster

| # | Rule |
|---|---|
| **DC-01** | **A named role declares a disaster** — the Head of Service, or the CTO out of hours. Failover is never an engineer's unilateral decision |
| **DC-02** | The declaration has **stated criteria**: primary site unreachable or unrecoverable within the RTO; data corruption beyond point-in-time recovery; a security event requiring isolation |
| **DC-03** | **The decision is time-boxed.** If the criteria are met, the declaration happens — deferring it while hoping consumes the RTO |
| **DC-04** | **Failing over is a decision with a cost**: `dr` runs the same artefact (`PE-004` `FF-134`) but with reduced capacity until scaled, and failing back is a second migration |

### 6.2 The sequence

| # | Step | Owner | Target |
|---|---|---|---|
| 1 | **Declare** (`DC-01`) | Head of Service / CTO | Minutes |
| 2 | **Freeze writes** at the primary if reachable, to bound divergence | Platform | Minutes |
| 3 | **Promote `Z3` standby** to primary | Platform | ≤ 15 min |
| 4 | **Promote `Z4` in-country standby** — *if it exists* (§7) | Platform | ≤ 15 min |
| 5 | **Scale `dr` compute from IaC** (`PE-003`, `PE-002` §5.12.1) | Platform | ≤ 30 min |
| 6 | **Repoint DNS / ingress** to `RGN-S` | Platform | ≤ 15 min, plus TTL |
| 7 | **Verify**: read and write smoke tests, `CD-233` reachability, integration health | Platform + QA | ≤ 20 min |
| 8 | **Re-establish egress allow-list and outbound credentials** from `RGN-S` | Platform | Within step 5 |
| 9 | **Apply `DA-006` `BK-02` post-restore suppression** if a restore was involved (`ER-03`) | Platform + DPO | Before service return |
| 10 | **Declare service restored**; notify per `OP-004` | Head of Service | — |

> **Steps 8 and 9 are the ones that get discovered during the first real failover.** Step 8: the
> `Z6` egress allow-list and vault-injected counterparty credentials are `RGN-P` constructs — if
> they are not provisioned in `RGN-S`, **every external integration fails after an otherwise
> successful failover.** Step 9 is `ER-03`'s legal obligation. **Both are in §10's drill checklist
> precisely because both are easy to omit.**

### 6.3 DNS and TTL

| # | Rule |
|---|---|
| **DN-01** | **Production DNS TTLs are short enough that a repoint takes effect inside the RTO** — a 24-hour TTL makes a 2-hour RTO impossible |
| **DN-02** | TTLs are **verified as part of the drill**, not assumed |
| **DN-03** | Health-checked failover routing is preferred to manual repointing where the provider supports it |

### 6.4 Failing back

| # | Rule |
|---|---|
| **FB-01** | **Fail-back is planned, never improvised.** It is a second migration, with its own window |
| **FB-02** | The original site is **rebuilt, not reused as-is**, unless the cause is understood |
| **FB-03** | Replication is **re-established in the new direction and verified** before cutting back |
| **FB-04** | **Fail-back is drilled at least once** — a drill that only fails over has rehearsed half the procedure |

---

## 7. `Z4` Recovery — The `OP-01` Answer

### 7.1 The problem, restated exactly

`SC-007` §9.1 gives three routes and finds all three unavailable or unlawful:

| Route | State |
|---|---|
| 1. Operate without the sensitive fields until the store returns | ✔ Available — **degraded, and only for an *unreachable* store, not a *lost* one** |
| 2. Restore from a resident backup **to a resident target** | ✖ **No resident DR target exists** — the only lawful full recovery |
| 3. Restore into the regional environment | ✖ **A regulatory act** under `NFR-086b`; `OP-012` `RD-01` forbids it, correctly |

### 7.2 What `PE-001` changed

`SC-007` §9.4 recommended option A — *provision a Bangladesh-resident DR target* — and could go no
further, because *"`SC-007` cannot choose; it can only make the choice explicit."*

**`PE-001` §3.3 named three certified in-country facilities**, verified 2026-08-19: a **Tier IV**
national facility with Uptime Institute certification of operational sustainability, a
**carrier-neutral Tier III** provider with 2N redundancy, and a **Tier III, PCI-DSS certified**
provider marketing private cloud for BFSI residency needs.

> **`PE-007-F-04`. Route 2 is procurable today.** `OP-01` has stood as critical since it was raised,
> and its remedy is a purchase order and a small environment — **`Z4` is "regulatory, not volume"
> sized** (`AR-001` §8.6), so the cost is far below a full DR environment (`SC-007` §9.4).
> **The obstacle was never technical availability. It is that nobody has been asked to decide.**

### 7.3 Route 2, designed

| Element | Design |
|---|---|
| **Target** | An in-country standby at a second facility, or a second hall in a Tier IV facility |
| **Replication** | Continuous WAL streaming **within Bangladesh**, encrypted in transit |
| **Key material** | **Separate, in country** (`SC-006` `ES-3`); the standby has its own escrow |
| **RPO / RTO** | ≤ 15 min / ≤ 2 h — **the same as `Z3`, once it exists** |
| **Failover** | §6.2 step 4 |
| **Restore testing** | **In country** (`RZ-01`) — this target is also the restore-test environment |
| **Backups** | An in-country immutable copy (`IM-07`) |
| **Registry** | A `BD-R` registry replica (`PE-005` `RC-05`) — §9.4 |
| **Network** | Reachable from `Z2` through `CD-233` only (`PE-001` `NR-02`), over the §8.2 link |

### 7.4 Route 1, designed properly — degraded operation

`SC-007` §9.2 designs the degraded mode *"because a survival mode nobody specified is a survival mode
that fails."* This document makes it **testable**.

| `SC-007` requirement | How it is exercised |
|---|---|
| `DG-1` — `CD-233` unavailability **degrades, does not fail** the estate; service orders, dispatch, invoicing, inventory and payroll calculation continue | **Drill scenario D-3** (§10.2): sever the link, verify each continues |
| `DG-2` — operations requiring a resident field **fail explicitly with a stated reason** | Verify the error is `451 data.residency_restricted` (`IN-002` §6.1), not a timeout or a silent skip |
| `DG-3` — **biometric attendance falls back to a non-biometric path** | Exercise the fallback; `SC-003` `A-05`(c) requires it to exist anyway |
| `DG-4` — **no operation silently proceeds without the field it needed** | Negative test: a NID verification that cannot happen is a **refusal**, not a skip |
| `DG-5` — **queued writes to `Z4` are held durably and replayed**, never dropped, never diverted regionally | Verify the queue survives a restart and replays on reconnection |
| `DG-6` — degraded mode has a **declared maximum duration**, then escalates to CTO and CDO | Verify the escalation fires |

> **`PE-007-D-04`. Degraded mode is drilled, not documented.** `DG-1`…`DG-6` describe behaviour
> nobody has induced. **A survival mode that has never been entered on purpose will be entered for
> the first time during the incident it exists for.**

### 7.5 The decision, forced

`SC-007` §9.4 costs three options and `SC-007-F-07` records: *"Option C is the current position by
default, not by decision… **A risk taken by omission is the one nobody owns.**"*

| Option | Requires | Consequence if chosen |
|---|---|---|
| **A. Provision an in-country DR target** | A purchase order; a small, availability-critical environment; in-country key escrow | **`NFR-007` becomes true for all data.** `PE-001` §3.3 names candidates |
| **B. Obtain the Authority's written position in advance**, with a pre-documented safeguard | Legal engagement with the NDMA; a standing notification; a pre-agreed safeguard | **Necessary regardless of A**, because it covers the case where the in-country target itself fails |
| **C. Accept that `NFR-007` does not apply to residency-classified data** | A **recorded, board-level** risk acceptance; `OP-012` and `NFR-007` amended; degraded mode becomes the only answer | **`M06` and biometric attendance unavailable for the duration of any `Z4` outage** |

> **`PE-007-D-05`. This document recommends A + B, and requires that C — if chosen — be chosen
> explicitly.**
>
> The design work for all three is complete: route 2 is designed (§7.3), route 1 is designed and made
> testable (§7.4), and route 3 remains forbidden (`SC-007-DR-1`). **What remains is a decision with a
> cost, and it belongs to the CTO, the CFO and Legal Counsel.**
>
> **`Q-01` is a Wave 1 blocker.** Until it is answered, §12's RAG status stays red and the `Z4` RTO
> is reported separately and as unbounded.

---

## 8. Scenarios

**`OP-012` §5 enumerates the scenarios. This section states what infrastructure each requires**, and
which are currently unrecoverable.

| # | Scenario | Recovery path | State today |
|---|---|---|:--:|
| **S-1** | Single node failure | HA within the tier (`PE-001` §9.2) | **Designed** |
| **S-2** | Availability-zone loss | Multi-AZ HA | **Designed** |
| **S-3** | **Regional site loss** | Failover to `RGN-S` (§6.2) | **Designed; `RGN-S` unprovisioned** |
| **S-4** | **Data corruption / bad migration** | **PITR to just before** (§4.3) | **Designed; WAL archiving unprovisioned** |
| **S-5** | Accidental deletion | PITR, or object versioning | **Designed** |
| **S-6** | **Ransomware** | **`BKP-3` immutable copy** (§4.4) | **Designed; `BKP-3` unprovisioned** — `OP-02` |
| **S-7** | **Cloud account compromise** | **`BKP-3`, separate account, separate credentials** + `PE-003` §13 bootstrap rebuild | **Designed; unprovisioned** |
| **S-8** | **`Z4` unreachable** (link or facility) | **Degraded mode** (§7.4) | **Designed; never drilled** |
| **S-9** | **`Z4` lost** (data loss) | **Route 2 — an in-country standby** | **UNRECOVERABLE until §7.5** |
| **S-10** | Secret manager loss | Escrow assembly (§4.7) | **Designed; never rehearsed** |
| **S-11** | **Registry unreachable from `BD-R`** | Registry replica (`PE-005` `RC-05`) | **Designed; §9.4** |
| **S-12** | Supplier / counterparty outage | **Manual fallback** (`NFR-050`, `OP-014`) | **0 of 13 tested** — §11.3 |
| **S-13** | Total loss — no site, no account | **`BKP-3` + `PE-003` §13 bootstrap** | §9 |

### 8.1 The two that are not merely unprovisioned

| # | Scenario | Why it is different |
|---|---|---|
| **S-9** | **`Z4` lost** | Every other row is *"designed, buy the infrastructure."* **S-9 is a decision nobody has taken** (§7.5), and the design is complete |
| **S-7** | **Account compromise** | The recovery depends on `BKP-3`'s credentials **not** being in the estate (`IM-03`). If they are, the scenario has no recovery path at all |

---

## 9. Recovering the Recovery System

**The scenario most plans omit: the recovery infrastructure is itself infrastructure.**

### 9.1 From nothing

`PE-003` §13 `BS-06` states it: *"`PE-007`'s worst-case scenario — account compromise, `BKP-3`
restore — begins with an empty account and no state backend. **If nobody has written down how the
first apply works, the recovery has no first step.**"*

| # | Step | Depends on |
|---|---|---|
| 1 | New account, new credentials | Provider relationship, out of band |
| 2 | **`PE-003` `bootstrap/`** — state backend, encryption key, pipeline identity | The bootstrap procedure and its **encrypted committed state** (`BS-02`) |
| 3 | Restore IaC state from backup | `PE-003` `ST-05` |
| 4 | **Apply infrastructure from code** | The repository — §9.2 |
| 5 | **Restore secrets from escrow** | §4.7; the actual key holders |
| 6 | Restore data from **`BKP-3`** | `IM-04` break-glass restore credentials |
| 7 | Restore images | Registry replica or rebuild from source |
| 8 | Apply `ER-03` post-restore suppression | The suppression list, restored first (`ER-04`) |
| 9 | Verify and return to service | §5.3's checks |

### 9.2 The repository dependency

> **`PE-007-F-05`. Every step from 4 onward depends on the source repository being available**, and
> the repository is a third-party service the estate does not control.

| # | Rule |
|---|---|
| **RP-01** | The repository is **mirrored** to a second location on every push |
| **RP-02** | The mirror includes **all branches, tags and the encrypted bootstrap state** |
| **RP-03** | **Mirror recovery is rehearsed annually** — cloning from the mirror and applying |
| **RP-04** | `GV-011` `PGD-A2-15` records that **644 files sit under no version control at all.** That is a documentation-estate finding; **for `infrastructure/` it would be a total-recovery failure**, and `PE-003` `PE-003-D-02` places IaC in the monorepo precisely so it is versioned |

### 9.3 The out-of-band record

| # | Rule |
|---|---|
| **OB-01** | A **printed or offline record** holds: provider account identifiers, support contacts, escrow holders, `BKP-3` account details, and the bootstrap procedure |
| **OB-02** | It is held by **at least two named people** in **two locations** |
| **OB-03** | It is **reviewed at every wave gate** |
| **OB-04** | It contains **no secret values** — only how to reach the people and systems that hold them |

> **`OB-01` sounds antiquated and is the difference between a nine-step recovery and an
> improvisation.** In scenario S-7 the estate's own systems — including the wiki holding the runbook —
> may be inaccessible.

### 9.4 `BD-R`'s recovery dependency

`PE-005-F-01` raises it; it is confirmed here as a **recovery** dependency, not merely an operational
convenience:

> **If `BD-R`'s only image source is a regional registry reached over the cross-border link, then a
> link failure makes the resident tier unrecoverable as well as unreachable — which converts
> `SC-007` §9.2's *degraded* mode into an *outage*.**

| # | Rule |
|---|---|
| **BR-01** | **`BD-R` holds a registry replica** (`PE-005` `RC-05`) |
| **BR-02** | It holds **its own IaC state** (`PE-003` `RS-01`) and **its own secret escrow** (`SB-03`) |
| **BR-03** | **`BD-R` must be recoverable with the regional site unavailable.** `FF-160` |

---

## 10. The Drill Programme

### 10.1 What `NFR-051` requires

*"Full failover exercised twice yearly with documented results."* `OP-012` `OI-07` records that **no
exercise is scheduled anywhere in `06-01`**.

### 10.2 The scenarios drilled

| # | Drill | Frequency | Proves |
|---|---|---|---|
| **D-1** | **Full regional failover to `RGN-S`** and back | **Twice yearly** (`NFR-051`) | `NFR-007` for `Z3`; §6.2 steps 1–10 |
| **D-2** | **PITR to a point in time** | Quarterly | S-4; `RT-02`, `RT-03` |
| **D-3** | **`Z4` unreachable — degraded mode** | **Twice yearly** | `DG-1`…`DG-6` (§7.4) |
| **D-4** | **`Z4` failover** to the in-country standby | Twice yearly, **once §7.5 is decided** | S-9 |
| **D-5** | **`BKP-3` restore** from the immutable copy | Annually | S-6, S-7 |
| **D-6** | **Secret escrow assembly**, with the actual holders | Annually | S-10; `SB-05` |
| **D-7** | **Bootstrap rebuild** in a scratch account | Annually | S-13; `PE-003` `BS-05` |
| **D-8** | **P0 integration manual fallbacks** | **Per wave gate** | `NFR-050`; `IN-008` §9 |
| **D-9** | **Repository mirror recovery** | Annually | `RP-03` |

### 10.3 What a drill must produce

| # | Rule |
|---|---|
| **DL-01** | **Measured times** for every step — a drill without a stopwatch proves nothing about RTO |
| **DL-02** | **A pass/fail against `NFR-007`**, not a narrative |
| **DL-03** | **Run by the people who would run it in an incident**, not by the engineer who built it (`IN-008` `DR-02`) |
| **DL-04** | **Defects found are logged and fixed**, and re-tested at the next drill |
| **DL-05** | **A failed drill blocks the wave gate.** It does not become a risk-register row (`IN-008` `DR-06`) |
| **DL-06** | The record is a **wave-gate artefact** (`FF-159`) |
| **DL-07** | **Every drill exercises §6.2 steps 8 and 9** — egress and post-restore suppression, the two most easily omitted |

### 10.4 The first drill

> **`PE-007-D-06`. The first `D-1` drill precedes the Wave 2 gate**, per `OP-02`'s remediation
> instruction: *"schedule the first full exercise before the W2 gate."*
>
> **It will fail.** A first drill against newly provisioned infrastructure, run by people who have not
> run it before, discovers DNS TTLs, missing egress rules, unrehearsed promotion steps and
> credentials nobody provisioned in `RGN-S`. **That is the drill's purpose**, and `DL-05` means it
> blocks the gate until the defects are fixed — which is the correct outcome, and it must be
> **planned for** rather than treated as a surprise.

---

## 11. Business Continuity

### 11.1 What this document assumes from the business

ISO 22301 requires a **business impact analysis** establishing maximum tolerable outage per business
process. **The estate does not have one.**

| # | Position |
|---|---|
| `NFR-007`'s RTO ≤ 2 h is used as the **technical** objective |
| **Whether two hours is tolerable for *every* business process is a business judgement nobody has made** |
| Examples where it plausibly is not: **payment reconciliation at month end**, **payroll on a payment date**, **a wave cutover in progress** |
| **`PE-007-F-06`: a BIA is a `GV-005` / business-owner deliverable, and its absence means the technical RTO is unvalidated against business need.** `Q-05` |

### 11.2 The two continuity mechanisms

| Mechanism | Covers | Owner |
|---|---|---|
| **Technical DR** (§6, §7) | Loss of 1000FiX infrastructure | This document |
| **Manual fallback** (`NFR-050`, `OP-014`) | Loss of a **counterparty** — payment rail, SMS gateway, courier, NBR portal | `IN-004`, `OP-014` |

**They are different failures with different responses**, and conflating them produces a plan that
fails over infrastructure when the problem is bKash.

### 11.3 `NFR-050`'s state

| Measure | Value |
|---|---|
| P0 integrations (**enumerated** from `05-03` §2, not from its summary) | **13** |
| With a documented fallback (`05-03` §7) | 12 — **`INT-013` email is absent** (`OP-03`) |
| **With a *tested* fallback** | **0** |

> **`PE-007-F-07`. `NFR-050` requires a *tested* fallback for every P0 integration and none has ever
> been tested.** `IN-008` §9 defines what "tested" means — timed, at realistic volume, by the people
> who would run it — and records the same 0-of-12 position from the integration side, against a
> denominator that was itself wrong. **This document schedules it as drill `D-8`, per wave gate**,
> and corrects the denominator to 13.

### 11.4 Communication

| # | Rule |
|---|---|
| **CM-01** | Incident and DR communication follows `OP-004`'s templates and `OP-005`'s status page |
| **CM-02** | **The status page must not depend on the estate it reports on** — `AUDIT-017` `OP-14` records exactly this defect. It is hosted independently |
| **CM-03** | **Counterparty notification obligations** (`PE-001` `FD-05`) are part of the DR communication plan, not an afterthought |
| **CM-04** | **`HC-01`'s monthly DR RAG report to the Steering Committee** (`OP-012` §3) carries the `Z4` RTO **as a separate line** (`SC-007` §9.5) |

---

## 12. Readiness Status

### 12.1 The honest position at issue

| Element | State | Closes when |
|---|---|---|
| Recovery objectives, per tier | **Designed** | — |
| Backup design | **Designed** | — |
| WAL archiving | **Designed, unprovisioned** | `PE-001` `Q-01` + build |
| **`BKP-3` immutable copy** | **Designed, unprovisioned** | Build |
| Restore verification | **Designed, unprovisioned** | Build |
| Regional failover | **Designed, unprovisioned** | `RGN-S` provisioned |
| **`Z4` recovery** | **Designed; DECISION UNMADE** | **§7.5 — `Q-01`** |
| Degraded mode | **Designed, never drilled** | Drill `D-3` |
| Drill programme | **Designed, unscheduled** | `GV-004` schedules it |
| **P0 manual fallbacks** | **0 of 13 tested** | Drill `D-8` |

### 12.2 The RAG status

> **`PE-007-D-07`. DR readiness is RED at issue, and this document does not change it.**
>
> `OP-012` §3 `HC-01` requires monthly RAG reporting to the Steering Committee, and `OP-02` states
> that *"the honest RAG status for DR readiness is red."* **Issuing a design does not provision
> infrastructure.** It goes amber when `RGN-S`, `BKP-3` and WAL archiving are live and `D-1` has
> passed; it goes green when **`Z4` has a recovery target and `D-4` has passed.**
>
> **Reporting green on the strength of a document would be precisely the defect `OP-01` describes:
> a constraint that is invisible until the night it binds.**

---

## 13. Fitness Functions

Allocation confirmed by enumerating every `FF-nn` definition across all authored categories at
**2026-08-19 01:45 (+06)**, per `PGD-AUDIT-007` `PGD-A7-01`.

| # | Check | Scope | Timing | Enforcement |
|---|---|---|---|---|
| **FF-155** | **WAL archiving is succeeding**, and archive lag is within `NFR-007`'s RPO, for `Z3` **and** `Z4` | Both tiers | Continuous | **Alert within 5 min** |
| **FF-156** | **`BKP-3` immutability verified quarterly** by an attempted deletion that must fail | `BKP-3` | Quarterly | **Fail** |
| **FF-157** | **Secret escrow can be assembled** by the named holders | Vault, both sites | Annually | **Fail** |
| **FF-158** | **A weekly restore test exists and passed**, including measured recovery time within `NFR-007` | `Z3`, `Z4` | Weekly | **Fail** |
| **FF-159** | **A DR drill record exists within the current wave**, with measured times and a pass/fail | Per gate | Wave gate | **Fail** |
| **FF-160** | **`BD-R` is recoverable with the regional site unavailable** — registry, state and escrow all in country | `BD-R` | Wave gate | **Fail** |
| **FF-161** | Backup retention meets `DA-006` for every data class, and no class lacks a retention decision | All classes | Monthly | **Fail** |
| **FF-162** | **Post-restore suppression (`ER-03`) is applied** on every restore, evidenced | Per restore | Per event | **Fail** |
| **FF-163** | **Every P0 integration has a fallback drill record within the current wave** — 13 of 13 | 13 | Wave gate | **Fail** |
| **FF-164** | **Production DNS TTLs permit a repoint inside the RTO** | All production zones | Monthly | **Fail** |

---

## 14. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `PE-007-D-01` | Recovery objectives | One estate-wide RTO · **per tier** | **Per tier** | A single number conceals the tier that cannot meet it — and one tier currently cannot meet any | §3.2; `Z4` reported separately |
| `PE-007-D-02` | What is backed up | Everything · **originating data only, derived stores rebuilt with a timed procedure** | **Originating only** | Backing up derived stores doubles cost to shorten a rebuild — but an unmeasured rebuild is an unbounded RTO | §3.4 |
| `PE-007-D-03` | Restore verification | Restore completes · **restore + replay + integrity + currency + usability + timing** | **All six** | A completed restore proves the file was readable and nothing else | `RT-01`…`RT-09`; `FF-158` |
| `PE-007-D-04` | Degraded mode | Documented · **drilled** | **Drilled** | `DG-1`…`DG-6` describe behaviour nobody has induced | Drill `D-3` |
| `PE-007-D-05` | `Z4` recovery | A · B · C · **recommend A + B, and force C to be explicit** | **A + B recommended** | All three designs are complete; what remains is a decision. **A risk taken by omission is the one nobody owns** | §7.5; `Q-01` is a W1 blocker |
| `PE-007-D-06` | First drill | After go-live · **before the W2 gate** | **Before W2** | `OP-02`'s remediation instruction — and the first drill is *expected* to fail, which is why it must be early | §10.4 |
| `PE-007-D-07` | RAG status at issue | Amber on design · **red until provisioned and drilled** | **Red** | Issuing a design does not provision infrastructure, and green on paper is the `OP-01` defect | §12.2 |
| `PE-007-D-08` | Erasure vs backups | Selective editing · **time-bounded persistence + post-restore suppression** | **Time-bounded** | Rewriting a backup destroys its integrity; `DA-006` `BK-02` covers the restore case | `ER-01`…`ER-05`; `FF-162` |

---

## 15. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| **Q-01** | **Option A, B or C for `Z4`?** All three designs are complete. **C is the current position by default** (`SC-007-F-07`) | **CTO + CFO + Legal Counsel** | **W1 — blocking** | `OP-01`, `NFR-007` for `Z4`, drill `D-4`, RAG status |
| **Q-02** | **Are `RGN-S`, `BKP-3` and WAL archiving funded and scheduled?** `OP-02` calls this *"the largest unfunded operational obligation the content register has surfaced"* | **CTO + CFO** | **W1 — blocking** | `NFR-007`, drill `D-1` |
| **Q-03** | **Is the drill programme in `GV-004`'s schedule?** `OP-012` `OI-07`: no exercise is scheduled anywhere | Programme Director | **W1** | `NFR-051`, `FF-159` |
| **Q-04** | Who are the **secret escrow holders**, and has escrow assembly ever been rehearsed? (`SB-05`) | CTO + Security Lead | **W1** | S-10, S-13, `FF-157` |
| **Q-05** | **Is there a business impact analysis?** The technical RTO is unvalidated against business need (`PE-007-F-06`) | Business Owners Forum + `GV-005` | **W2** | §11.1, ISO 22301 conformance |
| Q-06 | Does the in-country facility support a **second failure domain** for `Z4`'s WAL archive and immutable copy? (`WA-06`, `IM-07`) | Platform Engineering Lead | W1 | §7.3 |
| Q-07 | Who owns the **out-of-band record** (§9.3), and where are its two copies? | Head of Service | W1 | S-7, S-13 |

---

## 16. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | Recovery objectives are stated **per tier**, and the unbounded one is named | §3.2, §3.3 |
| AC-02 | **All three `OP-02` preconditions are designed** | §4.3 WAL · §4.4 `BKP-3` · §10 drills |
| AC-03 | 3-2-1-1-0 is realised, with `Z4` having its own entirely in country | §4.2 |
| AC-04 | Base-backup frequency is tied to **RTO**, not storage | §4.3.1 |
| AC-05 | **Restore verification proves usability and timing**, not completion | §5.2, §5.3 |
| AC-06 | The **residency constraint on restore testing** is identified | §5.4, `PE-007-F-03` |
| AC-07 | The failover sequence includes the **two steps most easily omitted** | §6.2 steps 8, 9 |
| AC-08 | **`OP-01` is answered**: route 2 designed against named facilities, route 1 designed and made testable | §7.2, §7.3, §7.4 |
| AC-09 | **The `Z4` decision is forced to be explicit** | §7.5, `PE-007-D-05` |
| AC-10 | **Recovering the recovery system** is designed, including the repository dependency | §9 |
| AC-11 | The drill programme states **what a drill must produce**, and that the first will fail | §10.3, §10.4 |
| AC-12 | **The RAG status is stated honestly and does not change on issue** | §12.2 |

**Definition of done.** Complete when every criterion is met, **Q-01 and Q-02 are decided**,
`RGN-S`/`BKP-3`/WAL archiving are provisioned, drills `D-1`, `D-3` and `D-5` have run, all 13 P0
fallbacks are drilled, `FF-155`…`FF-164` are enabled, and `PGD-000`'s `PE-007` row carries a fresh
enumeration timestamp. **`OP-01` closes on the `Z4` decision plus drill `D-4`. `OP-02` closes on
provisioning plus drill `D-1`. Neither closes on issue of this document, and §12.2 says so.**

---

## 17. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | **`PE-001`** §3, §8.2 | `RGN-S`, `BD-R`, `BKP-3`; **three named in-country facilities**; the private link |
| Upstream | **`PE-002`** §5.12 | The `dr` specification |
| Upstream | **`PE-003`** §6.3, §13 | State as a recovery object; **bootstrap as step 2 of a from-nothing rebuild** |
| Upstream | **`PE-005`** `RC-05` | The `BD-R` registry replica |
| Upstream | **`SC-007`** §9 | The three routes, `DG-1`…`DG-6`, options A/B/C, `SC-007-DR-1` |
| Upstream | `AR-001` §8.4 | `DR-01`…`DR-04` |
| Upstream | `DA-006` | Retention; **`BK-02` post-restore suppression** |
| Downstream | **`OP-012`** | **The playbook this design makes executable**; `ER-03` must enter its restore procedure |
| Downstream | `OP-014` | §11.3's 13 P0 fallbacks |
| Downstream | `SV-*` | Incident command consumes §6's failover |
| Downstream | `PE-008` | `FF-155`, `FF-164` and drill instrumentation |
| Downstream | `GV-004` | The drill programme needs a schedule |
| Downstream | `GV-005` | `Q-01`'s risk; `PE-007-F-06`'s BIA |
| Lateral | `../../project_content/_AUDIT/AUDIT-017_*.md` | **`OP-01`, `OP-02`, `OP-03`, `OP-14`** |

---

## 18. References

**Within this repository**
[`../PGD-000_Master_Register_of_Project_Guiding_Documents.md`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md) ·
[`./_CATEGORY_OVERVIEW.md`](./_CATEGORY_OVERVIEW.md) ·
[`./PE-001_Infrastructure_and_Network_Architecture_Design.md`](./PE-001_Infrastructure_and_Network_Architecture_Design.md) ·
[`./PE-002_Environment_Strategy_and_Specification.md`](./PE-002_Environment_Strategy_and_Specification.md) ·
[`./PE-003_Infrastructure_as_Code_Standard.md`](./PE-003_Infrastructure_as_Code_Standard.md) ·
[`./PE-005_Containerisation_and_Orchestration_Design.md`](./PE-005_Containerisation_and_Orchestration_Design.md) ·
[`./PE-006_Capacity_Plan_and_Performance_Engineering_Baseline.md`](./PE-006_Capacity_Plan_and_Performance_Engineering_Baseline.md) ·
[`./PE-008_Observability_and_Monitoring_Design.md`](./PE-008_Observability_and_Monitoring_Design.md) ·
[`./PE-009_Configuration_and_Secrets_Management_Standard.md`](./PE-009_Configuration_and_Secrets_Management_Standard.md) ·
[`../05_Security_Privacy_and_Compliance/SC-007_Data_Residency_and_Cross_Border_Transfer_Design.md`](../05_Security_Privacy_and_Compliance/SC-007_Data_Residency_and_Cross_Border_Transfer_Design.md) ·
[`../04_Integration_and_API_Engineering/IN-008_Integration_Test_Sandbox_and_Certification_Specification.md`](../04_Integration_and_API_Engineering/IN-008_Integration_Test_Sandbox_and_Certification_Specification.md)

**Workspace**
`../../project_content/_AUDIT/AUDIT-017_*.md` `OP-01`, `OP-02`, `OP-03`, `OP-14` ·
`../../project_content/17_Operations_Support_and_Runbooks/OP-012_*.md`, `OP-014_*.md` ·
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_*.md` ·
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-03_*.md` §2, §7

**External sources**

| Source | What it establishes | Verified |
|---|---|---|
| ISO 22301:2019 | Business continuity management systems; BIA and exercise requirements | 2026-08-19 |
| ISO/IEC 27031:2011 | ICT readiness for business continuity | 2026-08-19 |
| NIST SP 800-34 Rev.1 | Contingency planning process | 2026-08-19 |
| 3-2-1-1-0 backup rule | Three copies, two media, one offsite, one immutable, zero verification errors | 2026-08-19 |
| PostgreSQL PITR and WAL archiving | Continuous archiving; base backup plus replay | 2026-08-19 |
| **BDCCL National Data Center · BDCOLO · Felicity IDC** | Tier IV / Tier III certified in-country facilities — **the route-2 candidates** (`PE-001` §3.3) | 2026-08-19 |

---

## 19. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-19 | Platform Engineering | Initial issue. **Designs all three `OP-02` preconditions** — continuous WAL archiving, the `BKP-3` immutable copy outside the primary account, and the drill programme — and **answers `OP-01`** by designing route 2 against `PE-001`'s three named in-country facilities and making `SC-007`'s degraded mode testable rather than merely documented. **Forces the `Z4` decision to be explicit** (`PE-007-D-05`), records that route 2 has been procurable throughout (`PE-007-F-04`), and states that **DR readiness is RED at issue and does not change on the strength of a document** (`PE-007-D-07`). Designs recovery of the recovery system including the repository dependency (`PE-007-F-05`), identifies the **residency constraint on restore testing** (`PE-007-F-03`), and corrects `NFR-050`'s denominator to **13 P0 integrations, 0 tested** (`PE-007-F-07`) | *Pending — CTO, CFO, Legal Counsel; `GV-002` not constituted* |

---

*`PE-007` · Category 10 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
