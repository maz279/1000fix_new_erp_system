---
id: OP-007
title: Runbook — Core ERP Platform
project: 1000FiX ERP System v2.0
content_type: Runbook
template: TPL_Runbook.md
template_version: 1.0
version: 1.0
date: 2026-08-20
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Platform Engineering
author: Platform Engineering with Content Design
reviewers: [Chief Technology Officer, Enterprise Architect, Database Administrator, Security Lead, Support Lead, QA Lead]
approver: Chief Technology Officer
content_class: C
purpose: >
  The start, stop, scale, backup, restore, job-monitoring and failure-mode procedures for the Odoo
  19 core, its PostgreSQL cluster, its filestore and its job workers. Restoring service without a
  runbook depends on one person being reachable; `05-06` §7 NFR-091 requires every module to ship with an
  operational runbook, and this is the one every other runbook assumes.
traces_to: [02-05, M30, M64, 05-06 NFR-006, NFR-007, NFR-030, NFR-052, NFR-091, OPS-01, OPS-05, OPS-07, OP-008, OP-009, OP-012, OP-013, OP-014, NT-021]
priority: P1
wave: W1
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md §1, §4, §8.1, §9 — Odoo 19 CE, PostgreSQL 16, PgBouncer, Redis 7, MinIO, Nginx, Docker/K3s; production sizing; environments local/dev/staging/training/prod/dr
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 NFR-007 RPO ≤ 15 min RTO ≤ 2 h; NFR-030 backup retention 30 d / 1 y / 7 y; NFR-052 weekly automated restore test; §7 NFR-091 every module ships with an operational runbook — **note the collision recorded in AUDIT-016 AP-02: §6.3 also uses NFR-091 for the PDPA consent standard**; OPS-05 every scheduled job reports success, failure and duration; OPS-07 forward-only migrations
    verified: 2026-08-20
    class: P1
  - source: Odoo 19.0 documentation — command-line interface, database backup archive containing dump plus filestore, database neutralisation for non-production. https://www.odoo.com/documentation/19.0/developer/reference/cli.html
    verified: 2026-08-20
    class: P2
  - source: Odoo backup and recovery practice — database and filestore must be backed up together; restore procedure tested monthly to a staging environment. https://oec.sh/guides/odoo-backup-recovery
    verified: 2026-08-20
    class: P3
supersedes: none
review_due: 2027-02-20
---

# Runbook — Core ERP Platform

> **Read §7 first if the system is down and customers are waiting.** Everything else in this file
> assumes you have time.
>
> **Verification status.** This runbook is authored at W0/W1, before the production environment
> exists. Every command, path and threshold below is **indicative and must be verified against the
> built environment before gate G3** ([`CG-007`](../00_Content_Governance_and_Standards/CG-007_Review_Approval_and_Signoff_Workflow.md) §2.1). A runbook that has never been executed is a
> plan, not a runbook — see Open Items.

| Item | Value |
|---|---|
| System | Odoo 19 Community Edition core — the ERP application, its database, filestore and workers |
| Owner team | Platform Engineering (Platform Squad) |
| Criticality | **P0** — every module, every portal and every integration depends on it |
| Availability target | `NFR-006` ≥ 99.9% (09:00–22:00 BST) · `NFR-045` ≥ 99.7% 24×7 · `NFR-007` RPO ≤ 15 min, RTO ≤ 2 h |
| On-call rota | [`OP-013`](OP-013_On_Call_Escalation_and_Handover_Content.md) |
| Escalation path | On-call engineer → Platform lead → CTO → [`SP-005`](../06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-005_Escalation_Matrix.md) TE-E1 |

---

## 1. What This System Does

The Odoo 19 CE core holds the system of record for every business object in the programme: the
customer, the device, the service order, the part, the invoice, the employee. All 12 portals read
and write through it, either directly or through the API gateway ([`OP-008`](OP-008_Runbook_Integration_and_Event_Platform.md)). Every scheduled job
that produces a statutory output, a payout file or a management figure runs on its cron nodes.

**If it stops:** no job can be created, dispatched, invoiced or closed; the customer portal shows
errors; the technician app continues working offline for up to 24 hours (`NFR-047`) and queues its
sync; branches fall back to paper ([`OP-014`](OP-014_Manual_Fallback_Procedure_Set.md)). Money continues to be taken only if the payment path
is independent at that moment — it is not, for order creation.

---

## 2. Architecture Summary

| Component | Purpose | Depends on |
|---|---|---|
| **Nginx** | TLS termination, reverse proxy, static asset serving, request routing | Certificates, DNS |
| **Odoo application nodes** (4 × 8 vCPU / 32 GB, 12 workers each at steady state) | HTTP request handling, business logic, ORM | PostgreSQL, Redis, filestore |
| **Odoo cron nodes** (2 × 4 vCPU / 16 GB) | Scheduled actions and queue jobs, isolated from user traffic | PostgreSQL, filestore |
| **PgBouncer** | Connection pooling between Odoo workers and PostgreSQL | PostgreSQL |
| **PostgreSQL 16 primary** (16 vCPU / 64 GB / 2 TB NVMe) | The system of record | Storage, WAL archiving |
| **PostgreSQL replicas** (2) | Read offload, BI queries, failover candidate | Streaming replication from primary |
| **Filestore** (MinIO object storage, 20 TB growing) | Attachments, generated documents, evidence photographs | Object storage availability |
| **Redis 7** | Sessions, cache, locks, queue backing | — |
| **K3s / Docker** | Orchestration, scaling, rollout | Container registry |
| **Observability** — OpenTelemetry, Prometheus, Loki, Tempo, Grafana | Metrics, logs, traces, dashboards | Independent of the ERP estate |

> **The one architectural fact that governs every recovery procedure:** the database and the
> filestore are **separate stores that must be restored together and to the same point in time**.
> A database restored without its filestore produces invoices with no PDFs and jobs with no
> photographs; a filestore restored without its database produces orphaned files nobody can reach.

---

## 3. Health Checks

| Check | Command / dashboard | Healthy looks like |
|---|---|---|
| Application liveness | `GET /web/health` through the load balancer | HTTP 200 from **every** application node |
| Worker saturation | Grafana → *ERP Core* → Worker utilisation | < 70% sustained; brief peaks acceptable |
| Request latency | Grafana → *ERP Core* → p95 by route | ≤ 2 s p95 screens (`NFR-001`), ≤ 400 ms p95 API (`NFR-002`) |
| Database connections | `SELECT count(*) FROM pg_stat_activity;` and PgBouncer `SHOW POOLS;` | Below 80% of `max_connections`; PgBouncer `cl_waiting` = 0 |
| Longest running query | `SELECT max(now()-query_start) FROM pg_stat_activity WHERE state='active';` | < 30 s outside reporting windows |
| Replication lag | `SELECT now()-pg_last_xact_replay_timestamp();` on each replica | **< 15 minutes always** — this is the `NFR-007` RPO boundary |
| WAL archiving | `SELECT * FROM pg_stat_archiver;` | `last_failed_time` null; `archived_count` increasing |
| Disk headroom | Node exporter → filesystem | > 25% free on database volumes; > 30% on WAL |
| Filestore reachable | Object store health endpoint + a read of a known object | 200 and the expected byte count |
| Redis | `INFO` — memory, evicted keys | No evictions; memory < 70% |
| Scheduled actions | Odoo → Settings → Technical → Scheduled Actions, and the job dashboard | No action with `nextcall` in the past by more than its interval (`OPS-05`) |
| Queue jobs | Job dashboard: pending, started, failed counts | Failed = 0; pending draining |
| Certificate expiry | Monitoring alert `alert.sys.cert` ([`NT-021`](../04_Notification_and_Messaging/04D_In_App_Voice_and_System/NT-021_System_Integration_and_Job_Failure_Alert_Library.md) #10) | > 30 days remaining |
| Backup success | Backup job report | Last night's backup completed **and verified** |

**Daily operational check (09:00 BST, 10 minutes).** Replication lag · backup verified · failed
jobs · overdue scheduled actions · disk headroom · open `Sev3`+ incidents. Recorded; a missed
check is itself recorded (`OPS-05` discipline).

---

## 4. Routine Operations

| Operation | Steps | Risk | Approval needed |
|---|---|---|:--:|
| **Rolling restart of application nodes** | Drain node at the load balancer → wait for in-flight requests → restart container → health check → return to pool → next node | Low if one node at a time; **never restart all nodes together** | Standard change |
| **Scale out application nodes** | Increase replica count in the orchestrator → verify database connection headroom **first** (each worker holds a connection) → health check | Medium — scaling application without database headroom exhausts connections | Standard change |
| **Restart cron nodes** | Confirm no long-running job is mid-execution → stop → start → verify the job dashboard drains | Medium — a job killed mid-write must be idempotent to be safe (`IP-04`) | Standard change |
| **Enable/disable a scheduled action** | Settings → Technical → Scheduled Actions → toggle `active` → record in the change register | Medium — a disabled action fails silently, which `OPS-05` exists to prevent | Normal change |
| **Install or upgrade an Odoo module** | Staging first → backup → maintenance window if downtime → `-u <module>` → verify → smoke test ([`TS-013`](../13_Test_and_Acceptance_Content/TS-013_Regression_Pack_and_Smoke_Test_Checklist.md)) | **High** — module upgrade runs migrations | Normal change (CAB) |
| **Apply a database migration** | Forward-only, tested against a production-sized dataset (`OPS-07`) → backup → apply → verify → record the documented reversal procedure | **High** | Normal change (CAB) |
| **Vacuum / reindex a large table** | Off-peak window → `VACUUM (ANALYZE)` → monitor lock waits → `REINDEX CONCURRENTLY` where needed | Medium — locks | Standard change |
| **Rotate application secrets** | Vault rotation → rolling restart → verify integrations (`OP-008`) | Medium | Normal change |
| **Clear a stuck queue job** | Inspect the job payload → confirm idempotency → requeue **or** cancel with a recorded reason | Medium — cancelling a financial job loses a posting | Normal change |
| **Restore a single record from backup** | Restore to an isolated environment → extract → re-enter through the application, **never by direct write** ([`OP-003`](OP-003_Service_Desk_Macro_and_Canned_Response_Library.md) `mac.int.no_direct_db`) | Medium | Normal change + data owner |
| **Refresh a non-production environment** | Restore production backup → **neutralise** (disable outbound mail, payments, scheduled actions) → **mask residency-classified and personal data** (`NFR-071`, `NFR-086c`) → confirm before release to users | **High** — an un-neutralised copy sends real messages to real customers | Normal change + DPO |

> **`RO-01`.** The non-production refresh is the single most dangerous routine operation in this
> file. It has caused real customer messages to be sent from test systems in other organisations.
> **Neutralisation and masking are verified by a second person before anyone is given access**, and
> that verification is recorded.

---

## 5. Common Failure Modes

| Symptom | Likely cause | Diagnosis | Fix | Escalate if |
|---|---|---|---|---|
| All portals slow, screens time out | Worker saturation or database contention | Worker utilisation; `pg_stat_activity` for long queries; lock waits | Kill the offending query; scale workers if headroom exists; identify the report or export that caused it | Not resolved in 15 min or recurring the same day |
| "Too many connections" | Connection exhaustion after scaling or a pooler restart | PgBouncer `SHOW POOLS`; `pg_stat_activity` count | Restart PgBouncer; reduce worker count; raise pool limits only after checking database capacity | Repeats after restart |
| One node returns errors, others fine | Node-local failure (disk, memory, container) | Node metrics; container logs | Drain and replace the node | Two or more nodes affected |
| Screens load, saving fails | Filestore unreachable or full | Object store health; free capacity | Restore object store access; extend capacity | Data loss suspected — **`Sev1`** |
| Attachments and PDFs missing | Filestore/database point-in-time mismatch after a restore | Compare a known attachment reference against the object store | Restore filestore to the database's point in time | Any production mismatch — **`Sev1`** |
| Scheduled actions not running | Cron node down, action deactivated, or a stuck job holding the queue | Job dashboard; `nextcall` values; cron node health | Restart cron nodes; clear the stuck job; re-enable the action | Statutory or financial job missed its window |
| Nightly optimisation overruns | Data volume growth beyond `NFR-044`'s 20-minute budget | Job duration trend | Let it complete; dispatch starts unoptimised; capacity review (`OPS-08`) | Overrun repeats three nights |
| Replication lag rising | Long transaction on primary, network, or replica I/O | `pg_stat_replication`; replica load | End the long transaction; throttle BI queries on the replica | **Lag > 15 min — this breaches `NFR-007` RPO, `Sev1`** |
| Disk filling rapidly | WAL not archiving, runaway logging, or an unbounded table | `pg_stat_archiver`; largest relations; log volume | Fix archiving; rotate logs; archive the growing table | < 15% free |
| Sign-in fails for everyone, app otherwise healthy | Identity provider, not the ERP | Keycloak health ([`OP-009`](OP-009_Runbook_Identity_and_Access.md)) | Follow `OP-009` | Always — different runbook, same incident |
| Reports correct, dashboards wrong | Warehouse pipeline, not the ERP | [`OP-010`](OP-010_Runbook_Data_Platform_and_Warehouse.md) | Follow `OP-010` | — |
| Data appears wrong after a release | Migration defect | Compare against pre-release backup in an isolated restore | Assess reversibility; consider rollback (`§10`) | Any financial or statutory field — **`Sev1`** |
| Deadlocks reported in logs | Concurrent writes to the same records, often batch vs interactive | Deadlock entries in PostgreSQL log | Reschedule the batch; review the transaction boundary | Recurring — raises a problem record |

---

## 6. Incident Response

| Severity | Response time | First actions | Who to notify | Comms template ([`OP-004`](OP-004_Incident_Communication_Template_Set.md)) |
|---|---|---|---|---|
| **Sev1** | Page immediately, 15 min acknowledge | Declare · confirm blast radius · take a manual backup **before** any remediation that could lose state · start the timeline | Incident Commander, CTO, Support Lead, Operations Director | 1, 3, 5 |
| **Sev2** | 30 min in hours | Confirm scope · apply the known workaround · decide whether it degrades to `Sev3` with a fallback | Platform lead, Support Lead | 2 |
| **Sev3** | Next business day | Ticket, diagnose, schedule | Platform team | — |
| **Sev4** | Backlog | Record for trend | — | — |

**First five minutes of a `Sev1` on this system**

1. **Declare** — severity, and name the Incident Commander (`OP-013` §4.6). Do not investigate first.
2. **Publish** — `OP-004` template 1 internally, [`OP-005`](OP-005_Status_Page_and_Maintenance_Notice_Copy.md) status page within 15 minutes.
3. **Preserve** — before remediation, capture: current logs, `pg_stat_activity` snapshot, the last
   backup timestamp, and the deployment history for the last 24 hours. Remediation destroys
   evidence; the post-incident review needs it.
4. **Tell branches what to do** — `OP-014` fallback reference in the same message, not later.
5. **Then** diagnose.

---

## 7. Manual Fallback

> Required for every P0 integration (`IP-09`). This section states how the **business keeps
> trading** while the core is unavailable — the detailed procedures are `OP-014`.

| Scenario | Fallback procedure | Duration tolerable | Reconciliation on recovery |
|---|---|---|---|
| Core unavailable, branches open | `OP-014` FB-01 — paper job card, manual money receipt, customer mobile recorded on every form | **4 hours** before customer impact becomes reputational | Batch entry by the branch within 24 h; duplicates prevented by the receipt number as the natural key |
| Core unavailable, field technicians working | No action — the technician app holds 24 hours offline (`NFR-047`) and syncs on recovery | 24 hours | Automatic sync; conflicts resolved per [`OP-011`](OP-011_Runbook_Portal_and_Mobile_App_Operations.md) §Sync |
| Core unavailable, customer wants to book | Hotline 16743 takes the booking on paper; customer told the reference will follow by SMS | 4 hours | Entered by the contact centre; SMS sent on creation |
| Core unavailable at month-end close | Close is deferred; the close calendar has a defined slack ([`SP-020`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-020_SOP_Month_End_and_Year_End_Close.md)) | 1 working day | Finance re-runs the close sequence |
| Core available but invoicing broken | Manual invoice from the fallback pack, **sequential numbering from the reserved manual range** | 8 hours | Manual invoices entered and matched; VAT sequence integrity checked before filing ([`DT-011`](../05_Document_and_Print_Templates/05B_Finance_and_Statutory/DT-011_Sales_Register_Mushak_6_2.md)) |

**Rule `FB-01`:** every paper form produced during a fallback carries the customer's mobile number
and the branch code. That is what makes reconciliation possible; without it, entry produces
duplicates that then have to be found by hand.

---

## 8. Backup and Recovery

| Item | RPO | RTO | Procedure | Last tested |
|---|---|---|---|---|
| PostgreSQL — point in time | **≤ 15 min** (WAL archiving, continuous) | ≤ 2 h | Restore base backup → replay WAL to target time → verify row counts and control totals | *Not yet — environment does not exist* |
| PostgreSQL — nightly full | 24 h | ≤ 2 h | Automated nightly; 30-day retention (`NFR-030`) | *Not yet* |
| Filestore | ≤ 15 min (object versioning + replication) | ≤ 2 h | Restore to the **same timestamp as the database** | *Not yet* |
| Weekly backup | 7 d | — | 1-year retention (`NFR-030`) | *Not yet* |
| Monthly backup | 30 d | — | **7-year retention** (`NFR-030`, and the statutory schedule under `NFR-088`) | *Not yet* |
| Configuration and infrastructure | Per commit | ≤ 1 h | Rebuild from version-controlled definitions (`OPS-02`) | *Not yet* |
| Secrets | Per rotation | ≤ 1 h | Vault restore; **never** from a code repository (`NFR-062`) | *Not yet* |

**Restore procedure (production, full)**

1. Declare `Sev1` and confirm the restore decision with the CTO. A restore discards everything
   written after the target time — that is a business decision, not a technical one.
2. Choose the target time. Default: **the last consistent point before the damaging event**, not
   simply the latest backup.
3. Stop application and cron nodes. Leave the load balancer serving the maintenance page
   (`OP-005` template 10).
4. Restore the database base backup and replay WAL to the target time.
5. Restore the filestore **to the same target time**.
6. Start **one** application node. Run the verification set: control totals ([`DM-011`](../12_Data_Migration_Content/DM-011_Data_Quality_Rules_Cleansing_and_Deduplication_Standard.md) reconciliation
   pattern), last-transaction check per module, an attachment retrieval, and a document render.
7. Start remaining nodes; start cron nodes **last**, so scheduled actions do not fire against a
   half-verified system.
8. Reconcile the gap: everything between the target time and the incident must be re-entered or
   re-processed. Identify it before users do.
9. Post-incident review is mandatory ([`OP-016`](OP-016_Post_Incident_Review_Template_and_Register.md)).

**Verification (`NFR-052`).** An automated restore test runs **weekly** into an isolated
environment and asserts row counts, a checksum of a control table, an attachment fetch and a
document render. **A backup that has not been restored is not a backup**; the weekly test result is
reported to the CTO and a failure is a `Sev2` in its own right.

---

## 9. Break-Glass Access

| Scenario | Who may authorise | Procedure | Audit record |
|---|---|---|---|
| Identity provider unavailable, ERP administration required | CTO (or Operations Director if CTO unreachable, recorded) | Local emergency administrator credential retrieved from the vault break-glass path; **two people present**, one acting and one witnessing | Vault retrieval log, session recording (`NFR-070`), incident record, review within 1 working day |
| Direct database access required to diagnose | CTO | Read-only role first; write access only with a second authoriser and a stated statement of what will be written | Session recording, statement of change, `OP-016` item |
| Production data correction that cannot be made through the application | CTO **and** the data owner | Script reviewed by a second engineer, executed in a transaction, with the row count asserted before commit and a backup taken first | Change record, before/after extract retained 7 years |
| Emergency change during an incident | Incident Commander | [`SP-031`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-031_SOP_IT_Service_Desk_and_Change_Management.md) emergency change; retrospective CAB within 2 working days | Change record, incident record |

| # | Rule |
|---|---|
| **BG-01** | Break-glass credentials are **rotated immediately after use**, without exception |
| **BG-02** | Every break-glass session is recorded and reviewed by Security within 1 working day (`NFR-070`) |
| **BG-03** | Break-glass is **never** used for convenience, for speed, or because an approval is slow. Using it that way is a disciplinary matter, and stating so here is deliberate |
| **BG-04** | If break-glass is used and the reason was an approval bottleneck, the bottleneck is the finding (`OP-016`), not the engineer |

---

## 10. Change and Rollback

| Change type | Approval | Rollback procedure | Verification |
|---|---|---|---|
| Configuration (no code) | Domain owner, standard change | Revert the configuration value from the change record | Re-run the affected transaction |
| Application deployment | Release manager, CAB for normal changes | Redeploy the previous image; **containers make this fast, migrations do not** | Smoke pack (`TS-013`) |
| Deployment **with a database migration** | CAB | **Forward-only** (`OPS-07`). Rollback is by restore or by a compensating migration, both of which are slower than the deployment — plan the decision point before deploying | Control totals + smoke pack |
| Odoo module upgrade | CAB | Restore from the pre-upgrade backup | Module-specific test set |
| Infrastructure change | CTO | Re-apply the previous version-controlled definition (`OPS-02`) | Health checks §3 |
| Emergency change | Incident Commander | As above, with the retrospective review | Incident closure criteria |

> **`CR-01`.** The rollback question is decided **before** deployment, not during an incident:
> *"If this is wrong at 21:00, what do we do and how long does it take?"* A deployment whose answer
> is "restore from backup" is a deployment that needs a maintenance window and a communication
> (`OP-005`), not a zero-downtime release.
>
> **`CR-02`.** Feature flags (`OPS-06`) are the preferred rollback for behaviour changes: disabling
> a flag is instant and needs no deployment. Any new capability that cannot be disabled by a flag
> must justify that in its change record.

---

## 11. Post-Incident

Every `Sev1` and `Sev2` requires a review recorded in `OP-016`, within 5 working days for `Sev1`
and 10 for `Sev2`. This runbook is a **standing input and a standing output** of that review:

| Review question | Runbook consequence |
|---|---|
| Was the failure mode in §5? | If not, it is added — with the diagnosis that actually worked |
| Did the health checks in §3 detect it before users did? | If not, an alert is added to `NT-021` or removed as noise (`AL-05`) |
| Was the fallback in §7 usable by the branch? | If not, `OP-014` is corrected, not the branch |
| Was break-glass used, and why? | Every use is reviewed (`BG-02`) |
| Did the restore behave as §8 describes? | Untested steps are the ones that fail; the test schedule is corrected |
| Was the rollback decision made before deployment (`CR-01`)? | If not, the change process is the finding |

**Runbook currency rule `RC-01`:** a runbook step that failed during an incident is corrected
**within 2 working days**, before the detail is lost. [`OP-002`](OP-002_Hypercare_Plan_and_Exit_Criteria.md) `HX-14` makes this a hypercare exit
criterion.

---

## Open Items

1. **OP-007-OI-01** — **Nothing in this runbook has been executed.** The environment does not exist
   at authoring time. G3 technical verification cannot pass until W1 build completes, and the
   register nonetheless requires this file at W1. The honest position: this is a *design* runbook
   until first execution, and each procedure carries an execution date thereafter.
2. **OP-007-OI-02** — Backup **destination and residency** are undecided. `NFR-086` requires
   Bangladesh residency for sensitive personal data; a backup is a copy, so backup residency is a
   statutory question, not an operational one. Blocks §8 sign-off.
3. **OP-007-OI-03** — `NFR-007` RPO of 15 minutes requires continuous WAL archiving to a
   **separate failure domain**. `02-05` §8.1 does not provision one. Escalated to Platform.
4. **OP-007-OI-04** — Database administration capability is not named in `02-05` §8 or in the
   staffing model; §4 and §8 assume a DBA who does not currently exist.
5. **OP-007-OI-05** — `05-06` §7 `NFR-091` requires *every module* to ship with an operational runbook. The
   register carries **five component runbooks** (`OP-007`…`OP-011`) and one playbook (`OP-012`),
   which are platform-scoped, not module-scoped. **No module-level runbook is registered for any of
   the 67 modules.** Either `NFR-091` is satisfied by component runbooks — which must be stated, not
   assumed — or 67 module runbooks are an unregistered obligation. **Cite this requirement as `05-06` §7 `NFR-091`**: §6.3 uses the same number for the PDPA consent standard (`AUDIT-016` AP-02). Raised in the Category 17 audit
   as a register gap, not an authoring gap.
6. **OP-007-OI-06** — The 7-year monthly backup retention (`NFR-030`) intersects the PDPA erasure
   right (`NFR-093`). Legal must state how an erasure request is honoured against immutable
   long-retention backups. This is unresolved across the programme, not only here.

---

## Definition of Done

Tick every box before setting `status: Approved`. Full checklist in [`CG-008`](../00_Content_Governance_and_Standards/CG-008_Content_Definition_of_Done_and_QA_Checklist.md).

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Runbook.md` — all eleven sections present; `Open Items` added, justified
- [x] Every factual, statutory, pricing or capability claim carries a source and a verification date
- [x] Terminology matches [`CG-004`](../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md)
- [x] All internal links resolve
- [ ] Accessibility standard [`CG-011`](../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md) — n/a; engineering audience
- [x] Bengali counterpart — n/a; English-only by [`CG-010`](../00_Content_Governance_and_Standards/CG-010_Bilingual_Content_Policy.md) §3.2 ("runbooks are for engineers")
- [ ] Named approver recorded — CTO; sign-off deferred until G3 is possible (OI-01)
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)
- [ ] Decision(s) taken while authoring logged in `RF-006` — six open items pending

**Gates required (Class C):** G1 ●, G2 ●, **G3 ● — currently unachievable, see OI-01**. G4 n/a.

---

*`OP-007` · 1000FiX ERP Programme · CONFIDENTIAL — Internal Use Only*
