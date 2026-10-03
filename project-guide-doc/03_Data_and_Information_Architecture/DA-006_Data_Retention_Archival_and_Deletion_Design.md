---
id: DA-006
title: Data Retention, Archival & Deletion Design
category: 03 — Data & Information Architecture
code: DA
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Data Architect
approver: Chief Data Officer (unappointed — see DA-003 §5)
standards_basis: >
  ISO/IEC 27001:2022 A.5.33, A.8.10 · ISO 15489-1:2016 (records management) ·
  Bangladesh PDPA 2026 (erasure, processing records) · VAT and SD Act 2012 ·
  Saga pattern with compensating actions
traces_to: >
  PGD-000 DA-006 · LG-009 (RC-01…RC-27, DC-01…DC-25, DM-1…DM-6, OV-01…OV-06, RS-01…RS-15) ·
  NFR-093, NFR-095, NFR-088 · DI-08 · CD-248 · M24, M60
depends_on: DA-001 · DA-002 · DA-005 · LG-009
verified_on: 2026-08-18
priority: P0
needed_by: W2
enumeration_timestamp: 2026-08-18 14:30 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# DA-006 — Data Retention, Archival & Deletion Design

### Category 03 · Code `DA` · ISO 15489-1:2016 · PDPA 2026 · Saga with compensating actions

---

## 1. Purpose

`LG-009` is a **44 KB retention schedule** and it is genuinely strong: 27 data classes, 25 document
classes, six deletion methods, six overrides, fifteen governing rules, and a reconciliation of the
five-versus-seven-year question. It states **what must be kept, for how long, and why**.

**It states almost nothing about how.** Its own rule `EN-04` says so plainly: *"Until `M60` and `M24`
deliver, the schedule is unenforced. That is a stated risk, not an assumption."*

This document is the mechanism: the disposal engine, the job that finds eligible records across
**1,335 tables**, the erasure saga that must reach the primary, the replicas, the warehouse, the
object store, the search index, the event store and the backups — and the tombstone that survives all
of it.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | The retention data model — how a period attaches to a record |
| 2 | **The disposal engine** — selection, approval, execution, evidence |
| 3 | The six deletion methods, made executable |
| 4 | **The erasure saga (CD-248)** and every store it must reach |
| 5 | **The backup problem**, and the position `LG-009` leaves open |
| 6 | The event store, the warehouse and the search index |
| 7 | Legal hold — mechanism, not policy |
| 8 | Archival, storage tiering and PDF/A |
| 9 | **Tombstones** — what survives deletion, and why |
| 10 | Detection of both violation directions (`RS-07`) |
| 11 | The `M24`/`M60` timing gap and the interim |

**Explicitly out of scope**

| Topic | Owned by | Why |
|---|---|---|
| Retention **periods** | `LG-009` | Referenced, never restated. `RS-11`: where a document differs, `LG-009` governs |
| Legal basis for a period | `LG-009`, Legal | |
| Classification | `DA-005` | Class drives method, not period |
| Backup schedules and restore testing | `PE-007` | This document states the retention obligation on them |
| Destruction certificates as a product (M06) | `LG-017`, `SC-006` | Different artefact; same techniques |
| Data-subject request handling | `LG-010`, `SC-003` | This document builds the erasure half |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| **M24 / M60 developers** | This is the design brief for `FR-DMS-034`…`041` |
| CD-248 developers | §5 is the saga specification |
| Platform engineers | §6 backups; §8 tiering |
| DPO / CDO | §5, §9 — what an erasure actually reaches, and what it does not |
| QA | §11 — both violation directions are testable |
| Auditors | §4.5 evidence chain |

---

## 2. Basis and Findings

### 2.1 Standards conformance

| Standard | Conformance | Departure |
|---|---|---|
| **ISO 15489-1:2016** Records management | §4 disposal authority, §9 evidence, §8 archival | Not a certification target |
| **ISO/IEC 27001:2022 A.5.33** Protection of records | §4, §7 legal hold | Full |
| **A.8.10** Information deletion | §4.4 methods, §5 saga | Full |
| **PDPA 2026** | §5 erasure (NFR-093); §9 processing records 5 years (NFR-095) | Statutory |
| **VAT and SD Act 2012** | 7-year tax retention via `LG-009` `RC-03` | Statutory |
| **Saga with compensating actions** | §5 | The only viable pattern across seven stores |

### 2.2 Source material

| Source | Contribution |
|---|---|
| `../../project_content/10_Legal_Policy_and_Compliance/LG-009_Data_Retention_and_Deletion_Schedule.md` | **The policy this mechanises** — `RC-01`…`RC-27`, `DC-01`…`DC-25`, `DM-1`…`DM-6`, `OV-01`…`OV-06`, `RS-01`…`RS-15`, `EN-01`…`EN-05` |
| `./DA-001_*.md` §9 | **Partition keys** — the basis of `DM-2` |
| `./DA-002_*.md` attribute 24 | Retention class per field |
| `./DA-005_*.md` §6.1 | `S3` crypto-erase capability requirement |
| `../02_Architecture_and_Design/AR-001_Software_Architecture_Document.md` §7.5 RS-04 | The erasure saga's outline |
| `../02_Architecture_and_Design/AR-009_*.md` §8.4 | Event retention by class, and the erasure/processing-record tension |
| `../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §8.2 | CD-248 data-subject request orchestrator |

### 2.3 Findings

> **`PGD-A5-11` — the retention schedule is unenforced by its own admission, and the modules that
> would enforce it arrive in W3 and W6.**
>
> `LG-009` `EN-01` states the chain: *"defined here, published by `M60`, applied by `M24` at filing,
> computed from the trigger."* **`M24` is a Wave 3 module and `M60` is Wave 6.** `EN-04` records the
> consequence.
>
> Meanwhile `RC-04` (notification logs, 13 months) and `RC-22` (audit entries, 5 years) begin
> accruing in **Wave 1**, and `RC-16` (AI conversation records, 90 days) in Wave 4. **Records subject
> to a schedule nobody can execute accumulate from the first wave.**
>
> §12 states the interim.

> **`PGD-A5-12` — the backup position is stated as requiring confirmation and has not been confirmed.**
>
> `LG-009` `DM-R3` (§4.6.5): *"Deletion from the live store does not delete from backup media. A
> record deleted from live is not restored on a subsequent restore, and the backup copy ages out on
> the backup cycle. **This position requires G6 confirmation — `O-08`.**"*
>
> The backup ladder is **daily 30 days, weekly 1 year, monthly 7 years** (NFR-030). **A record erased
> under NFR-093 therefore persists in monthly backups for up to seven years.** §6 designs the
> mechanism that makes `DM-R3` true rather than assumed; the legal confirmation remains open.

> **`PGD-A5-13` — no document assigns a retention class to the 1,335 tables.**
>
> `LG-009` assigns periods to **data classes** and **document classes**. `DA-002` attribute 24 carries
> the class per field. **The mapping between them does not exist**, and without it the disposal engine
> cannot select a single row. §3.2 specifies the mapping; populating it is `DA-002`'s W0–W9 schedule.

---

## 3. The Retention Data Model

### 3.1 How a period attaches to a record

A retention period is **computed, never stored as a date at creation** — the trigger may not have
occurred yet.

| Element | Source | Notes |
|---|---|---|
| `retention_class` | **`DA-002` attribute 24** → `LG-009` `RC-nn` / `DC-nn` | Assigned per field; the **table's class is the strictest of its fields** |
| `retention_trigger` | `LG-009` column "Trigger" | Service order close, contract expiry, employment termination, capture, period end |
| `trigger_at` | **Computed** when the trigger event occurs | Set by the owning module; **null means not yet triggered** |
| `retention_period` | `LG-009` column "Period" | May be absolute (7 years) or relative (warranty + limitation) |
| `disposal_due_date` | **Computed** = `trigger_at` + period | Null while `trigger_at` is null |
| `hold_ref` | `fix_legal_hold` | **Non-null blocks everything** (§7) |
| `disposed_at`, `disposal_batch_id` | Set on disposal | The tombstone (§9) |

### 3.2 The mapping that does not yet exist

> `LG-009` speaks in **data classes** (`RC-01` "Service order, work order, diagnosis, repair record,
> evidence photographs"). `DA-001` speaks in **tables** (`fix_service_order`, `fix_work_order`,
> `fix_diagnostic_result`, …). **Nothing joins them.**

| # | Rule |
|---|---|
| **RM-01** | **Every table in `DA-001` is assigned exactly one `RC-nn`**, recorded in `DA-002` and generated into the disposal engine's selection catalogue |
| **RM-02** | Where a table's fields carry different classes, **the table takes the longest** (`RS-01`: the longest applicable obligation governs) |
| **RM-03** | A table with **no** assigned class **cannot be disposed of** and is reported as a gap — never silently retained forever, and never silently deleted |
| **RM-04** | A **document** stored in `fix_document` takes its `DC-nn` from its document class, independent of the table |
| **RM-05** | The mapping is **reviewed at every wave gate** as tables are added |

**Worked mapping, Category A:**

| `LG-009` class | Tables |
|---|---|
| `RC-01` Service order and work record | `fix_service_order`, `fix_work_order`, `fix_work_order_task`, `fix_diagnostic_result`, `fix_qc_result`, `fix_service_report` |
| `RC-04` Notification and delivery logs | `fix_notification_log` |
| `RC-09` Recovered customer data | `fix_recovered_inventory`, `fix_media_item`, `fix_recovery_attempt` |
| `RC-09` (second row) Case record and access log | `fix_data_case`, `fix_data_access_log` |
| `RC-15` Call recordings and chat transcripts | `fix_call_record`, `fix_conversation_message` |
| `RC-22` Access logs, audit entries, security events | `fix_audit_entry`, `fix_data_access_log`, `fix_security_event` |
| `RC-24` Location history | `fix_location_ping` |

> **`fix_data_access_log` appears under two classes** — as part of `RC-09`'s case record and under
> `RC-22`. `RM-02` resolves it: **the longest governs**, so 5 years minimum either way. The mapping
> exercise will surface more of these, and each is a decision, not a defect.

---

## 4. The Disposal Engine

### 4.1 Shape

```
  ┌──────────────────────────────────────────────────────────────────────┐
  │ 1. SELECT       Nightly. For each RC-nn in the catalogue:            │
  │                   disposal_due_date <= today                         │
  │                   AND hold_ref IS NULL                               │
  │                   AND no OV-02..OV-05 override active                │
  │                 → candidate batch, grouped by class                  │
  ├──────────────────────────────────────────────────────────────────────┤
  │ 2. PRESENT      Batch presented for approval BY CLASS, with counts,  │
  │                 date ranges, sample records and the override check   │
  │                 (FR-DMS-038)                                          │
  ├──────────────────────────────────────────────────────────────────────┤
  │ 3. APPROVE      A person approves. The system executes. Never the    │
  │                 reverse (LG-009 DM-R1)                                │
  ├──────────────────────────────────────────────────────────────────────┤
  │ 4. EXECUTE      Method per DM-1..DM-6 (§4.4), irreversibly           │
  ├──────────────────────────────────────────────────────────────────────┤
  │ 5. EVIDENCE     Certificate issued; permanent disposal register entry │
  │                 (BRU-DMS-06); tombstone written (§9)                  │
  └──────────────────────────────────────────────────────────────────────┘
```

### 4.2 Selection rules

| # | Rule |
|---|---|
| **SL-01** | Selection runs **nightly**, per class, never as one estate-wide scan |
| **SL-02** | **The selection index is `DA-001` §8.3's `(retention_class, disposal_due_date) WHERE NOT disposed`.** Without it, selection across 1,335 tables is a nightly full scan |
| **SL-03** | A record with `trigger_at IS NULL` is **not eligible** — its clock has not started |
| **SL-04** | Every override in `LG-009` §4.5 is checked **at selection and again at execution**. A hold placed between the two must win |
| **SL-05** | Selection is **idempotent**. A re-run selects the same set |
| **SL-06** | A batch exceeding a declared size threshold is **split**, not deferred |

### 4.3 Approval

| # | Rule |
|---|---|
| **AP-01** | **Disposal is never manual and never automatic** (`DM-R1`). A person approves; the system executes |
| **AP-02** | Approval is **by class**, by the class's data owner (`DA-003` §3.2) |
| **AP-03** | `S3` or `personal` classes additionally require **CDO** approval |
| **AP-04** | The approval record names the approver, the batch, the count and the date range, and is retained **permanently** |
| **AP-05** | **A refusal to dispose is recorded with its reason** (`DM-R5`) — a batch that is never approved and never refused is an unenforced schedule |

### 4.4 The six methods, made executable

| Method | `LG-009` definition | **Mechanism** |
|---|---|---|
| **`DM-1`** Approved disposal batch | Identify, approve, dispose irreversibly, certificate | `DELETE` in bounded transactions with the tombstone written in the same transaction. For soft-deleted rows, the row is **hard-deleted** — this is the DI-08 exception, and it is the only one |
| **`DM-2`** Partition or chunk drop | Time-partitioned data dropped on schedule | **`DETACH PARTITION` then `DROP`** — `DA-001` §9.1 names the key for all 12 partitioned tables. TimescaleDB `drop_chunks()` for hypertables |
| **`DM-3`** Crypto-erase | Destroy the field- or case-level key | **Key destruction in `SC-006`'s key store.** The ciphertext remains and is unrecoverable. **This is how a `resident` value is erased without a Z4 row delete** |
| **`DM-4`** Archive then dispose | Move to cold storage in **PDF/A**, then `DM-1` | §8 |
| **`DM-5`** Physical destruction | For media that cannot be verifiably erased | `LG-017` §4.6; certificate `DT-034` |
| **`DM-6`** Anonymisation in place | Irreversibly remove identifiability, retain the record | §4.6 — **and `DM-R2` means most attempts are not deletion** |

### 4.5 The evidence chain

| # | Rule |
|---|---|
| **EV-01** | Every disposal produces a **certificate**: batch id, class, count, date range, method, approver, executor, timestamp |
| **EV-02** | **The disposal register survives the content permanently** (`RS-05`). The company must be able to say what it destroyed and when, after it no longer has it |
| **EV-03** | The register is **insert-only** and cannot be deleted by anyone, including administrators (`RS-08` applied) |
| **EV-04** | An evidence pack for a claim, audit or regulatory request must be assemblable in **under five minutes** (`EN-05`) |
| **EV-05** | **A schedule that has disposed of something an evidence pack needs is a schedule error, not a retrieval failure** (`EN-05`) |

### 4.6 `DM-6` anonymisation — the honest position

| # | Rule |
|---|---|
| **AN-01** | **`DM-6` is deletion only if re-identification is genuinely impossible** (`DM-R2`) |
| **AN-02** | A pseudonymised record is **still personal data** (`DA-005` PC-02) |
| **AN-03** | Removing a name from a record that retains postcode, date of birth and service history is **not** anonymisation (`DA-005` RI-02) |
| **AN-04** | Every `DM-6` application records its **method**, and the method is reviewed by the CDO before first use |
| **AN-05** | Where anonymisation cannot be demonstrated, the method is **`DM-1`**, not `DM-6` |

> **`DM-6` is the method most likely to be chosen because it is convenient and most likely to be
> wrong.** It appears to satisfy both the retention obligation and the analytics appetite. In a
> 51-branch service business, a "fully anonymised" service record with branch, date, device model and
> fault code frequently identifies one person.

---

## 5. The Erasure Saga

> **The hard part is not the export; it is the erasure.** An erasure must remove personal data from
> the regional primary, the resident store, **every read replica, the warehouse, the object store, the
> search index and the backups in scope** — while **preserving** the processing record NFR-095
> requires be kept five years.

### 5.1 Why a saga and not a transaction

Seven stores, three of them not transactional, one of them offline media. **There is no distributed
transaction that spans them.** CD-248 is a saga with compensating actions.

### 5.2 The stores an erasure must reach

| # | Store | Mechanism | Compensating action |
|:--:|---|---|---|
| **1** | **Regional primary** (Z3) | `DM-1` hard delete or `DM-3` crypto-erase | Restore from the pre-erasure snapshot held for the saga's duration |
| **2** | **Read replicas ×2** | **Automatic** — streaming replication propagates the delete | None needed; verified, not assumed |
| **3** | **Resident store** (Z4) | **`DM-3` crypto-erase via CD-233.** Never a direct delete | Key restore is **impossible by design** — this step is therefore **last** (§5.3) |
| **4** | **Warehouse** (ClickHouse) | Delete from fact and dimension; **`DA-007` §6 Type-2 SCD rows for the subject** | Reload from source — but the source is gone, so this step is also late |
| **5** | **Object storage** (MinIO) | Delete objects by manifest; **evidence photographs, documents, call recordings** | Object versioning retained for the saga window |
| **6** | **Search index** | Delete by document id; reindex | Rebuild from source |
| **7** | **Event store** | §5.5 — the hardest case | — |
| **8** | **Backups** | §6 — **not deleted**; `DM-R3` position | — |

### 5.3 Ordering — reversible steps first

| Step | Store | Reversible? |
|:--:|---|:--:|
| 1 | Search index | ✔ rebuild |
| 2 | Warehouse | ✔ while source exists |
| 3 | Object storage (versioning on) | ✔ within window |
| 4 | Regional primary + replicas | ✔ from saga snapshot |
| 5 | **Resident store crypto-erase** | **✘ irreversible** |
| 6 | Write tombstone + processing record | — |

> **The ordering is the design.** Every reversible step runs first; the **one irreversible step runs
> last**, after every other store has confirmed. A saga that crypto-erases the key first and then
> fails on the warehouse has destroyed the data and left an inconsistent estate with no recovery.

### 5.4 Saga rules

| # | Rule |
|---|---|
| **SG-01** | Each step is **idempotent** — a retried step is safe |
| **SG-02** | Each step **confirms** before the next begins |
| **SG-03** | A failed step triggers **compensation of completed reversible steps**, and the request enters a **manual queue with the CDO notified**. It is never silently abandoned |
| **SG-04** | The saga is **auditable end to end**: a per-store record of what was erased and when |
| **SG-05** | **The processing record is written before step 5**, so the evidence that the erasure happened survives the erasure |
| **SG-06** | Completion within the statutory window; **controller-side consumers notified within 30 days** (NFR-093) |
| **SG-07** | An erasure is **refused** where `OV-06` applies, and **the refusal and its basis are stated to the data subject** (`BRU-CPM-11`) |

### 5.5 The event store

`AR-009` §8.4 raises the tension and this document resolves it.

| # | Rule |
|---|---|
| **ES-01** | **Event payloads carry no personal data beyond the minimum** (`AR-009` P-04) and **never a residency-classified value** (P-03). This is the primary control |
| **ES-02** | Where a payload does carry personal data, the event store is **in erasure scope** and is store 7 in §5.2 |
| **ES-03** | The **outbox is pruned at 7 days** (`AR-009` §5.3) and Redpanda retention is 30 days — so the exposure window is bounded by design, not by erasure |
| **ES-04** | **Financial and personal-data event classes retained 7 and 5 years respectively** (`AR-009` §8.4) are the exception, and are subject to `OV-06`: a tax event is not erasable |
| **ES-05** | An erasure **does not rewrite history in the event stream.** It removes personal data from payloads where present; the *fact* that a service order was completed survives |

> **ES-05 is the position that keeps both obligations satisfiable.** NFR-095 requires the processing
> record; NFR-093 requires the personal data gone. Keeping the event and emptying the personal fields
> satisfies both. Deleting the event would destroy the processing record that proves the processing
> was lawful.

---

## 6. Backups — the Open Position

### 6.1 The problem

| Fact | Consequence |
|---|---|
| Backup ladder: **daily 30 days, weekly 1 year, monthly 7 years** (NFR-030) | A record erased today persists in monthly backups for up to **7 years** |
| `DM-R3` position | *"A record deleted from live is not restored on a subsequent restore, and the backup copy ages out"* |
| `LG-009` `O-08` | **The position requires legal confirmation and has not received it** (`PGD-A5-12`) |

### 6.2 The mechanism that makes `DM-R3` true

`DM-R3` asserts that an erased record is *not restored* on a subsequent restore. **Assertion is not
mechanism.** Three components:

| # | Component | Rule |
|---|---|---|
| **BK-01** | **Erasure ledger** | Every erased subject key is recorded in an insert-only ledger that is **itself never restored from backup** — it lives outside the backup set or is always taken from live |
| **BK-02** | **Post-restore suppression** | Any restore is followed **automatically, before the system is returned to service**, by a re-application of the erasure ledger. A restore that skips it is an incident |
| **BK-03** | **Restore testing includes it** | The weekly automated restore verification (NFR-052) asserts that a previously erased subject is absent after restore |

> **Without BK-02, `DM-R3` is a hope.** A restore from a six-month-old monthly backup reinstates every
> erasure performed in those six months, silently, and the system returns to service holding data it
> told a data subject it had deleted.

### 6.3 The crypto-erase alternative

| # | Rule |
|---|---|
| **BK-04** | For **`S3` and `resident`** values, `DM-3` crypto-erase **also solves the backup problem** — the backup holds ciphertext whose key no longer exists |
| **BK-05** | This is a strong argument for **field-level encryption of personal data beyond the `S3` set**, and it is `SC-006`'s decision. **Recorded here because the backup consequence is the strongest reason for it** |

---

## 7. Legal Hold

| # | Rule |
|---|---|
| **LH-01** | **A legal hold beats everything**, including an erasure request (`OV-01`, `RS-06`) |
| **LH-02** | A hold is placed and released **only by `M60`** (`BRU-GRC-15`) |
| **LH-03** | A hold is a **row in `fix_legal_hold`** with scope, reason, instructing authority, placed-by and placed-at — never a flag on a record |
| **LH-04** | Scope may be a record, a party, a matter, a class or a date range. **The selection query joins it**; a hold is not enforced by a person remembering |
| **LH-05** | Held records are **excluded at selection and re-checked at execution** (SL-04) |
| **LH-06** | An erasure request against held data is **refused with the basis stated** (`OV-06`, SG-07) |
| **LH-07** | Release is logged; released records become eligible at the **next** selection run, never immediately |
| **LH-08** | An open hold is **reported at every wave gate** — a hold nobody reviews becomes indefinite retention |

---

## 8. Archival and Tiering

| # | Rule |
|---|---|
| **AR-01** | **Storage cost is answered by tiering, never by deletion** (`RS-10`) |
| **AR-02** | `DM-4` moves records to cold storage in **PDF/A** for the statutory tail, then `DM-1` |
| **AR-03** | Archived records remain **retrievable within the `EN-05` five-minute evidence-pack window** — an archive that cannot be retrieved in time is a disposal |
| **AR-04** | Tax and contract documents are the primary `DM-4` classes (`DC-01`, `DC-02`, `DC-10`) |
| **AR-05** | Archival **does not restart the retention clock** |
| **AR-06** | The archive manifest is part of the evidence chain (EV-01) |

---

## 9. Tombstones

**What survives deletion.** The estate's obligations require that deletion is provable, and a proof
that is itself deleted proves nothing.

| Survives | Content | Retention | Basis |
|---|---|---|---|
| **Disposal register entry** | Batch, class, count, range, method, approver, timestamp | **Permanent** | `RS-05`, `BRU-DMS-06` |
| **Per-record tombstone** | Table, surrogate id, retention class, `disposed_at`, batch id. **No business content, no personal data** | With the disposal register | Referential explicability |
| **Processing record** | That processing occurred, its purpose and lawful basis — **not the data processed** | **5 years minimum** | NFR-095 |
| **Erasure ledger entry** | Subject key, request id, completed-at | **Permanent** | BK-01, BK-02 |
| **Audit entries about the disposal** | Who approved, who executed | Per `RC-22` | `RS-08` |

| # | Rule |
|---|---|
| **TS-01** | A tombstone carries **no business content and no personal data** — it is the fact of deletion, not a copy of what was deleted |
| **TS-02** | A tombstone is **never disposed of by the class it records**. It has its own retention |
| **TS-03** | An inbound reference to a disposed record resolves to its tombstone with *"disposed under `RC-nn` on `<date>`"* — never a bare "not found" |

> **TS-03 is small and it matters.** A customer quoting a 2027 order number in 2035 should be told the
> record was disposed of under schedule, not that it never existed.

---

## 10. Detection — Both Directions

`LG-009` `RS-07`: *"A record retained beyond its schedule and a record missing before its schedule
expires are equally reportable."* Most retention programmes measure only the first.

| # | Check | Detects | Cadence |
|---|---|---|---|
| **DT-01** | Records with `disposal_due_date < today` and not disposed and not held | **Over-retention** | Nightly |
| **DT-02** | Records referenced but absent, whose class has not expired | **Premature loss** | Nightly, via FK and tombstone checks |
| **DT-03** | Tables with no `retention_class` assigned | Gap (RM-03) | Wave gate |
| **DT-04** | Disposal batches presented and neither approved nor refused for > 30 days | **Unenforced schedule** (AP-05) | Weekly |
| **DT-05** | Open legal holds not reviewed in the current wave | Indefinite retention (LH-08) | Wave gate |
| **DT-06** | Erasure sagas incomplete beyond the statutory window | Statutory breach | Daily |
| **DT-07** | A restore performed without erasure-ledger re-application | **BK-02 violation** | On every restore |

**A retention violation is a control failure and is recorded as one** (`EN-03`, `BRU-GRC-12`), and it
feeds `DA-003` `GM-09`.

---

## 11. Testing

| # | Negative test |
|---|---|
| NT-01 | A record past `disposal_due_date` with an active hold is selected → must not be |
| NT-02 | A hold placed between selection and execution → execution must abort |
| NT-03 | An erasure saga fails at step 4 → reversible steps compensate; CDO notified; **key not destroyed** |
| NT-04 | A restore from backup reinstates an erased subject → **BK-02 must suppress it** |
| NT-05 | A tax record within 7 years is erased on request → must be refused with the basis stated |
| NT-06 | A disposed record's id is referenced → resolves to a tombstone, not a bare not-found |
| NT-07 | An anonymised record is re-identified from quasi-identifiers → `DM-6` was misapplied |
| NT-08 | A `resident` value is erased by `DM-1` rather than `DM-3` → must be refused |

---

## 12. The `M24` / `M60` Timing Gap

> `EN-04`: *"Until `M60` and `M24` deliver, the schedule is unenforced."* **`M24` is W3; `M60` is W6.**
> `RC-04`, `RC-22` and `RC-24` begin accruing in **W1**.

### 12.1 The interim

| # | Rule | Wave |
|---|---|:--:|
| **IM-01** | **The retention-class mapping (§3.2) is authored in W0–W1** for every W1–W2 table, whether or not `M24` exists. The mapping is data, not code | W0–W1 |
| **IM-02** | **`DM-2` partition drop is available from W1** — `DA-001` §9.1 partitions `fix_notification_log`, `fix_api_usage_log`, `fix_audit_entry` and `fix_domain_event` from Wave 1. **The cheapest deletion method needs no module** | W1 |
| **IM-03** | `RC-04` (13 months) and `RC-24` (90 days) are therefore **enforceable in W1** by scheduled partition drop | W1 |
| **IM-04** | `RC-22` (5 years) does not expire until W5 at the earliest, so `M24`'s W3 arrival is **in time** for it | — |
| **IM-05** | **`DM-1` approved disposal is not available until `M24` (W3).** Classes needing it before W3 are recorded as a **known, bounded gap** in `GV-005` with an expiry | W1–W3 |
| **IM-06** | **The erasure saga (CD-248) is W4**, matching PDPA enforcement at ~13 May 2027. **A data-subject erasure request received before W4 is handled manually, with the manual procedure written and rehearsed** | W4 |
| **IM-07** | Legal hold (`fix_legal_hold`) is **W1**, not W6. A hold is a row and a join; it does not need `M60`. **`M60` later owns who may place one** | W1 |

> **IM-07 is the one worth pulling forward.** A legal hold is cheap to build and catastrophic to lack:
> if a matter arises in W2 and there is no hold mechanism, the only options are to suspend all
> disposal or to lose evidence.

---

## 13. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| **Q-01** | **Is the `DM-R3` backup position legally confirmed (`LG-009` `O-08`, `PGD-A5-12`)?** BK-01…BK-03 make it mechanically true; the legal position is open | Legal / DPO | **W2** | The erasure promise made to data subjects |
| **Q-02** | **Who authors the retention-class mapping for 1,335 tables (`PGD-A5-13`)?** Without it the engine selects nothing | Data Architect / domain owners | **W1 — blocking** | Every disposal |
| **Q-03** | Is `IM-06` accepted — manual erasure handling until W4? | CDO / DPO | **W1** | Pre-W4 data-subject requests |
| **Q-04** | Is field-level encryption extended beyond `S3` so crypto-erase solves the backup problem (BK-05)? | Head of InfoSec / `SC-006` | W2 | Backup erasure exposure |
| **Q-05** | `RC-09` sets no maximum for recovered customer data (`LG-009` `O-06`). A purge date with no ceiling is an indefinite retention | Technical Services Head / Legal | W6 | M06 |
| **Q-06** | `RC-17` (anonymised derived corpora) is **provisional and not operative** pending `LG-008` `PN5` | DPO | W6 | `AR-011` training corpora |
| **Q-07** | Is `DC-19`'s "three certification cycles" read as 9 years (`LG-009` `O-05`)? | Quality Manager | W5 | ISO record disposal |

---

## 14. Decisions Recorded

| # | Decision | Options | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| D-D6-01 | Period storage | Store a disposal date at creation; **compute from trigger** | **Compute** | The trigger may not have occurred; a contract's expiry is unknown at signature | `trigger_at` null = not eligible |
| D-D6-02 | Table→class mapping | Per record; **per table, strictest field wins** | **Per table (RM-02)** | 1,335 tables is tractable; 25 M rows is not | Populating it is `DA-002`'s schedule |
| D-D6-03 | Saga ordering | Any; **reversible first, irreversible last** | **Reversible first** | A failed saga that already destroyed the key leaves no recovery | Crypto-erase is always step 5 |
| D-D6-04 | Event store erasure | Delete events; **empty personal fields, keep the event** | **Keep the event** | NFR-095 needs the processing record; NFR-093 needs the data gone. Both are satisfiable | ES-05 |
| D-D6-05 | Backups | Assert `DM-R3`; **assert + mechanism (BK-01…BK-03)** | **Mechanism** | An assertion is not a control; a restore silently reinstates erasures | Post-restore suppression is mandatory |
| D-D6-06 | Tombstones | None; **fact-only tombstone** | **Fact-only** | Deletion must be provable, and TS-03 answers an inbound reference honestly | TS-01 forbids business content |
| D-D6-07 | Legal hold timing | With `M60` (W6); **W1** | **W1** | A hold is a row and a join; lacking it in W2 forces suspend-all or lose-evidence | IM-07 |
| D-D6-08 | `DM-6` anonymisation | Preferred where possible; **only where irreversibility is demonstrated** | **Demonstrated** | In a 51-branch business, branch + date + model + fault often identifies one person | AN-05 defaults to `DM-1` |

---

## 15. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | Retention attaches to a record by a computed, not stored, mechanism | §3.1 |
| AC-02 | **The `LG-009` class → table mapping is specified**, with rules for multi-class and unmapped tables | §3.2 RM-01…RM-05 |
| AC-03 | The disposal engine has selection, approval, execution and evidence, with `DM-R1` respected | §4 |
| AC-04 | All six `LG-009` methods are made executable | §4.4 |
| AC-05 | **The erasure saga names every store, its compensating action and the ordering rule** | §5.2, §5.3 |
| AC-06 | The backup position has a mechanism, not only an assertion | §6.2 BK-01…BK-03 |
| AC-07 | Legal hold is a joined row, enforced at selection and execution | §7 |
| AC-08 | Tombstones are specified, carrying no business content | §9 |
| AC-09 | **Both violation directions are detected** (`RS-07`) | §10 DT-01, DT-02 |
| AC-10 | The `M24`/`M60` gap has an interim with what is and is not available | §12.1 |

**Definition of done.** Complete when every criterion is met, Q-01 and Q-02 are resolved, and
`PGD-000`'s `DA-006` row is updated.

---

## 16. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | **`LG-009`** | The policy this mechanises. **Where they differ, `LG-009` governs** (`RS-11`) |
| Upstream | `DA-001` §9 | Partition keys — the basis of `DM-2` |
| Upstream | `DA-002` attribute 24 | Retention class per field |
| Upstream | `DA-005` §6.1 | `S3` crypto-erase capability |
| Downstream | **`M24`**, **`M60`** | The design brief for `FR-DMS-034`…`041` |
| Downstream | **CD-248** | §5 is the saga specification |
| Downstream | `SC-003` | Erasure is a DPIA control |
| Downstream | `SC-006` | Key destruction for `DM-3`; BK-05 |
| Downstream | `PE-007` | BK-02 post-restore suppression; NFR-052 restore testing |
| Downstream | `DA-003` `GM-09` | Both-direction violation metric |
| Lateral | `LG-010` | Data-subject request handling — this builds the erasure half |
| Lateral | `AR-009` §8.4 | Event retention; ES-05 resolves the tension it raises |

---

## 17. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` · `./_CATEGORY_OVERVIEW.md` ·
`./DA-001_Logical_and_Physical_Data_Model_and_Database_Schema_Specification.md` §8, §9 ·
`./DA-002_Data_Dictionary.md` · `./DA-003_Data_Governance_Framework_and_Stewardship_Model.md` ·
`./DA-005_Data_Classification_and_Handling_Standard.md` ·
`../02_Architecture_and_Design/AR-001_Software_Architecture_Document.md` §7.5 ·
`../02_Architecture_and_Design/AR-009_Event_Driven_Architecture_and_Messaging_Design.md` §8.4

**Workspace**
`../../project_content/10_Legal_Policy_and_Compliance/LG-009_Data_Retention_and_Deletion_Schedule.md` ·
`../../project_content/10_Legal_Policy_and_Compliance/LG-010_Data_Subject_Request_Handling_Content.md` ·
`../../project_content/10_Legal_Policy_and_Compliance/LG-017_Data_Recovery_and_Secure_Destruction_Terms.md` ·
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md` §6.3, §8 ·
`../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §8.2 (CD-248)

**External standards**

| Standard | Version | Verified |
|---|---|---|
| ISO 15489-1 — Records management | 2016 | 2026-08-18 |
| ISO/IEC 27001:2022 A.5.33, A.8.10 | 2022 | 2026-08-18 |
| [Bangladesh PDPA 2026 — erasure, processing records](https://securiti.ai/bangladesh-personal-data-protection-act-overview/) | Enforcement ~13 May 2027 | 2026-08-18 |
| VAT and Supplementary Duty Act 2012 — record keeping | In force | 2026-08-18 |

---

## 18. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. Converts `LG-009`'s policy into a disposal engine, an eight-store erasure saga with reversible-first ordering, and a backup mechanism (BK-01…BK-03) that makes `DM-R3` true rather than asserted. Raises `PGD-A5-11` (schedule unenforced until W3/W6), `PGD-A5-12` (backup position unconfirmed) and `PGD-A5-13` (no class→table mapping exists) | *Pending — CDO, unappointed* |

---

*`DA-006` · Category 03 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
