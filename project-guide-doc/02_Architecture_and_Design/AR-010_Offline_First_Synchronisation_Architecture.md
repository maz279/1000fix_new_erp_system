---
id: AR-010
title: Offline-First Synchronisation Architecture
category: 02 — Architecture & Design
code: AR
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Solution Architect
approver: Chief Architect
standards_basis: >
  Command-sourcing / append-only journal · Idempotent receiver (EIP) · Server-authoritative
  conflict resolution · ISO/IEC/IEEE 42010:2022 process viewpoint
traces_to: >
  PGD-000 AR-010 · AS-13 · DI-04 · NFR-037, NFR-047, NFR-018, NFR-082 · ADR-024 ·
  risk TR-01 · 05-03 §6 · UI-009 (conflict copy)
depends_on: AR-001 · AR-009 (idempotency semantics) · CD-015, APP-01
verified_on: 2026-08-18
priority: P0
needed_by: W2
enumeration_timestamp: 2026-08-18 02:05 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# AR-010 — Offline-First Synchronisation Architecture

### Category 02 · Code `AR` · Command journal · Server-authoritative conflict resolution

---

> **This is the hardest technical requirement in the programme, and its failure mode is social.**
> Three applications must operate **24 hours with no connectivity and no data loss**, and sync within
> **30 seconds** on 3G. Getting it wrong does not degrade a feature — it produces a technician who
> cannot tell whether four hours of work is safe. Technicians who stop trusting the app revert to
> paper, and the field data model becomes permanently incomplete. Risk `TR-01`, rated **H × H**.

---

## 1. Purpose

`05-03` §6 gives a protocol **sketch** — eleven rows describing local store, action model, upload,
download and conflict policy. `UI-009` writes the **copy** a user sees when a conflict is resolved.
**The algorithm that produces those conflicts does not exist.** This document is that algorithm.

It designs the shared offline engine (ADR-024) consumed by APP-01 (technician, W2), APP-02 (rider,
W3) and APP-03 (auditor, W5), and it specifies the test harness that is the release gate for all
three.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | The command model — why actions, not records, are synchronised |
| 2 | Local store design, encryption and lifecycle |
| 3 | The sync protocol — upload, download, tokens, batching, checksums |
| 4 | Server-side idempotency and the command ledger |
| 5 | **Conflict detection and the resolution authority matrix** |
| 6 | Conflict disclosure — what the user is told, and why silence is forbidden |
| 7 | Scope resolution — what data a device holds and how it changes |
| 8 | Evidence handling (photos, video, voice) on a deferred channel |
| 9 | Failure modes and their behaviours |
| 10 | **The offline test harness** — the release gate |
| 11 | Security: device loss, remote revocation, local encryption |

**Explicitly out of scope**

| Topic | Owned by | Why |
|---|---|---|
| Application UI and interaction design | `UX-006` | This document specifies *what must be conveyable*; `UX-006` designs how |
| Offline copy strings | `UI-009` (content) | Written; this document ensures the states exist to write copy for |
| Flutter implementation | `AR-003` `APP-01` SDD | Design vs code |
| The portal PWA degraded mode | `AR-001` §9.4, `UX-006` | Different problem: cached read, not offline write |
| Push notification delivery | `AR-009` E4, M27 | |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| **APP-01 developers** | The engine is built here, in Wave 2, for three applications |
| Server-side developers | §5 idempotency ledger and §4 endpoints are server obligations |
| QA lead | §10 is the release gate, and it is not negotiable |
| Service Operations Director | §6 is the difference between an app technicians trust and one they abandon |
| Head of InfoSec | §11 device loss and local encryption |

---

## 2. Basis and Inputs

### 2.1 The requirement set

| ID | Requirement | Source |
|---|---|---|
| **NFR-047** | Technician app functional without connectivity for **24 hours** | `05-06` §2 |
| **NFR-037** | Offline sync completion after 24 h offline: **≤ 30 s on 3G** | `05-06` §1 |
| **NFR-018** | Offline mode with automatic sync on reconnection | `05-06` §5 |
| **NFR-036** | Job list load on 3G: ≤ 8 s cold, ≤ 2 s warm | `05-06` §1 |
| **NFR-082** | Battery ≤ **12% per 8-hour shift** excluding navigation | `05-06` §5 |
| **NFR-017** | Android 11+, 3 GB RAM, intermittent 4G | `05-06` §5 |
| **DI-04** | Offline sync guarantees **zero data loss and zero double-application** | `05-06` §8 |
| **AS-13** | Append-only local journal with server-side conflict resolution | `02-01` §10 |
| `P02` NN-06 | **Every state-changing action is queued locally and idempotent on the server** | `04-00` |
| `P02` NN-07 | **No feature requires a connection that a technician cannot complete offline** | `04-00` |
| `P09` | Rider: full offline with queued sync | `04-00` |
| `P11` | Auditor: complete audit checklists offline, capture evidence, sync to M23 | `04-00` |

### 2.2 Source material

| Source | Contribution |
|---|---|
| `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-03_*.md` §6 | The eleven-row protocol sketch this document designs |
| `../../primary-doc/…Technology_Stack_Specification.md` §16 | Engine technology, conflict authority table, the two-state UX insight, test harness scenario classes |
| Ibid. §23 `TR-01` | The risk and its named controls |
| `../../1000fix_ERP_Module/04_Portals_and_Applications/04-00_*.md` P02, P09, P11 | Capability sets and non-negotiable requirements |
| `.../03_Modules/A_.../M02_*.md` | `fix.offline.journal`, `fix.field.session`, CD-015 `cd_offline_sync` |
| `../../project_content/03_UI_Copy_and_Microcopy/UI-009*` | Conflict-resolution copy — the states this design must produce |

### 2.3 Audit findings addressed

| Finding | How |
|---|---|
| `PGD-000` `AR-010` — *"`05-03` §6 gives a protocol sketch; the algorithm that produces those conflicts does not exist"* | §5, §6 are the algorithm |
| `TR-01` (H × H) | §10 test harness as a release gate; §5 authority matrix; §6 disclosure |
| `AR-006` §5.2 stub risk | §5.4 — the certification stub returning "eligible" also affects offline assignment validation |

---

## 3. The Command Model

### 3.1 Why commands, not records

The decision that determines everything else.

| Approach | Behaviour offline | Verdict |
|---|---|---|
| **Sync records** (last-write-wins on a row) | The device holds a copy of `fix.service.order`; on sync, whichever version is newer wins | **Rejected.** A technician's notes and a dispatcher's reassignment both touch the same row. Last-write-wins **destroys one of them silently** — the exact outcome that loses field trust |
| **Sync a diff** (CRDT / operational transform) | Merge field-by-field | **Rejected.** CRDTs are excellent for text and sets. They cannot express *"a part may only be consumed if stock is reserved"* — business invariants are not mergeable |
| **Sync commands** (append-only journal of intents) | The device records **what the technician did**, not what the record became. The server replays the intents against current state and applies its own rules | **Chosen (AS-13)** |

> **The property that makes commands correct where records are not:** a command carries *intent*, so
> the server can apply its own invariants to it. `consume_part(part_id, qty=2)` can be rejected for
> insufficient stock; `service_order.parts = [...]` cannot be, because it has already decided the
> outcome.

### 3.2 Command structure

```json
{
  "command_id":   "uuid",              // client-generated. THE idempotency key
  "device_id":    "uuid",
  "user_id":      442,
  "sequence":     127,                 // monotonic per device; ordering within the journal
  "issued_at":    "2026-08-18T11:20:04+06:00",
  "issued_at_utc":"2026-08-18T05:20:04Z",
  "clock_offset_ms": -1450,            // device-vs-server skew at last sync (§9.4)
  "command_type": "work_order.consume_part",
  "target":       { "type": "work_order", "id": 918234 },
  "payload":      { "part_id": 4471, "quantity": 2, "van_stock_line_id": 88123 },
  "base_version": 7,                   // aggregate version the device last saw (§5.2)
  "evidence_refs":["local://photo/9f2a…"]  // deferred channel (§8)
}
```

| Field | Purpose |
|---|---|
| `command_id` | **Client-generated UUID.** The server's idempotency ledger key. A retried upload is recognised, not re-applied |
| `sequence` | Monotonic per device. **Replay order within a device's journal is guaranteed**; across devices it is not |
| `issued_at` + `issued_at_utc` + `clock_offset_ms` | Device clocks drift and are user-settable. The server uses `issued_at_utc` corrected by the last known offset, and flags implausible values (§9.4) |
| `base_version` | The aggregate version the device held. **This is what makes conflict detection possible** rather than guessed |
| `evidence_refs` | Local references; binaries travel on the deferred channel (§8) |

### 3.3 Command catalogue rules

| # | Rule |
|---|---|
| **CM-01** | Every offline-capable action is a **named command type**, registered alongside the module's events in `IN-003` |
| **CM-02** | A command is **idempotent by `command_id`** at the server |
| **CM-03** | A command carries everything needed to evaluate it. **No command requires a callback to the device** |
| **CM-04** | A command that cannot be evaluated offline **must not be offered offline** (`P02` NN-07). Where the answer is unknowable, the app **defers the action** with a clear message rather than guessing |
| **CM-05** | Commands are **append-only**. An "undo" is a new compensating command, never a deletion from the journal |
| **CM-06** | A rejected command remains in the journal with its rejection reason. **The journal is the field record of what the technician did**, independent of what the server accepted |

> **CM-06 is what makes the design defensible.** If a technician's part consumption is rejected
> because stock was consumed elsewhere, the journal still records that they fitted the part. That is
> an operational fact, and it must not be erased by a stock rule.

---

## 4. Local Store and Sync Protocol

### 4.1 Local store

| Aspect | Design |
|---|---|
| Technology | **Encrypted SQLite (SQLCipher)** |
| Key | Derived from device credentials + a server-issued key; **wiped on remote revocation** |
| Contents | (a) the **command journal**, append-only; (b) a **read cache** of assigned work and reference data; (c) **pending evidence** blobs |
| Read cache | Rebuilt from server state on sync. **Never authoritative** — the journal is the only local truth |
| Pruning | Synced, closed work older than the retention window is pruned. **A command is never pruned until acknowledged** |
| Size budget | Bounded; on approaching the limit the app prunes the read cache first, then warns, and **never prunes the journal** |

### 4.2 Sync sequence

```
DEVICE                                            SERVER
  │                                                 │
  │  1. POST /api/v1/technician/sync/upload         │
  │     { device_id, last_ack_sequence,             │
  │       commands:[…], batch_checksum }            │
  │────────────────────────────────────────────────►│
  │                                                 │ verify checksum
  │                                                 │ FOR EACH command IN sequence order:
  │                                                 │   ├ seen command_id? → return prior result
  │                                                 │   ├ evaluate guards + invariants
  │                                                 │   ├ detect conflict (§5.2)
  │                                                 │   ├ apply | reject | apply-with-conflict
  │                                                 │   └ write idempotency ledger entry
  │  ◄──── { results:[ {command_id, outcome,        │  (one DB transaction per command,
  │           conflict?, server_state} ], ack_seq } │   never per batch — §4.3)
  │                                                 │
  │  2. GET /api/v1/technician/sync/download        │
  │     ?since=<sync_token>                         │
  │────────────────────────────────────────────────►│ compute scope (§7)
  │  ◄──── { changes:[…], new_sync_token,           │ delta since token
  │           scope_changes:[…] }                   │
  │                                                 │
  │  3. Deferred evidence channel (§8) — low priority, resumable
  │                                                 │
  │  4. Local: apply results, surface conflicts to the user (§6),
  │            prune acknowledged commands, update read cache
```

### 4.3 Protocol rules

| # | Rule | Why |
|---|---|---|
| **SP-01** | Commands are uploaded **in `sequence` order** and applied in that order | A part consumption after a job start must not be evaluated first |
| **SP-02** | **One transaction per command, not per batch** | A batch transaction means one rejected command rolls back nine accepted ones. Per-command means partial progress is real progress |
| **SP-03** | **Per-batch checksum.** A failed batch is retried **whole, never partially applied** (DI-04) | A truncated upload must not be interpreted as a complete one |
| **SP-04** | The server acknowledges **each command by `command_id`** | The device prunes only what is acknowledged |
| **SP-05** | Download is **delta since the last successful sync token**; a full refresh is available on demand | 30 s on 3G (NFR-037) is not achievable with a full refresh |
| **SP-06** | The sync token is **server-issued and opaque**. The device never constructs one | Prevents a device requesting an arbitrary window |
| **SP-07** | Upload precedes download **in the same sync cycle** | So the download reflects the device's own accepted work; otherwise the user sees their work vanish and reappear |
| **SP-08** | Sync is **resumable**. An interrupted sync resumes from the last acknowledged command | Intermittent 3G is the normal case, not the exception |
| **SP-09** | Evidence upload **never blocks state sync** (§8) | A 40 MB photo backlog must not delay a job status |

> **SP-07 is a small ordering decision with a large user consequence.** Download-then-upload means
> the technician's screen briefly shows the server's older state, their work appears to be gone, and
> then it returns. Users do not wait to find out; they re-enter the work.

### 4.4 Server-side idempotency ledger

| Aspect | Design |
|---|---|
| Key | `command_id` |
| Stored | `command_id`, `device_id`, `user_id`, outcome, conflict record, `applied_at`, result payload |
| On repeat | **Return the original result.** Never re-evaluate |
| Retention | 90 days, ≥ 3× the maximum plausible offline window |
| Index | `(command_id)` unique; `(device_id, applied_at)` for diagnostics |

**The ledger is the single mechanism that makes "zero double-application" (DI-04) true.** It is
server-side, because a client-side guarantee is lost with the device.

---

## 5. Conflict Detection and Resolution

### 5.1 What a conflict is

> A conflict occurs when a command's `base_version` is **older than the aggregate's current version**
> **and** the intervening change affects the same domain as the command.

Both halves matter. A dispatcher adding a customer note does not conflict with a technician's part
consumption, even though both bumped the version. **Version mismatch is a trigger for evaluation, not
a conflict in itself** — treating it as one produces constant false conflicts, and users learn to
dismiss conflict messages without reading them.

### 5.2 Detection

| Step | Action |
|---|---|
| 1 | Compare `command.base_version` with the aggregate's current version |
| 2 | If equal → **no conflict**. Apply, subject to invariants |
| 3 | If older → compute the **change set** between the two versions |
| 4 | Intersect the change set with the command's **affected domain** (§5.3) |
| 5 | Empty intersection → **no conflict**. Apply |
| 6 | Non-empty → **conflict**. Resolve by the §5.3 authority matrix |

### 5.3 The authority matrix

| Domain | Authority | Rationale |
|---|---|---|
| **Assignment** — who owns the job | **Server** | Dispatch may have reassigned it, with information the device did not have |
| **Pricing** — rates, discounts, totals | **Server** | The price book may have changed |
| **Stock** — availability, reservation, consumption | **Server** | Another technician may have consumed the part |
| **State** — order/work-order lifecycle | **Server** | The order may have been cancelled or put on hold |
| **Entitlement** — warranty, contract coverage | **Server** | Coverage may have been amended |
| **Evidence** — photos, video, voice notes | **Client** | Captured in the field; **cannot be recreated** |
| **Notes and diagnosis** | **Client** | The technician's own observation |
| **Field timestamps** — when work actually happened | **Client** | The device was there; the server was not |
| **Measurements** — readings, checklist answers | **Client** | Same |

> **The principle underneath the matrix:** the server wins where it holds information the device could
> not have; the client wins where it holds information the server could not have. Neither is "more
> trusted" — each is authoritative over what only it can know.

### 5.4 Resolution outcomes

| Outcome | Behaviour |
|---|---|
| **Applied** | No conflict, or the client held authority. State updated |
| **Applied with conflict** | Server-authoritative domain changed, **but the client's authoritative data is preserved and attached**. This is the most important outcome and the design's core promise |
| **Rejected** | An invariant cannot be satisfied. The command remains in the journal with its reason (CM-06); the user is told what to do |
| **Deferred** | Requires a decision the system cannot make. Raised as a task for the user or a supervisor |

**The worked example the whole design serves.** A technician completes a job offline at 11:20.
Dispatch reassigned it at 10:55.

| Element | Outcome |
|---|---|
| Assignment | **Server wins** — the job belongs to the other technician |
| Diagnosis, photographs, time entries | **Preserved and attached to the job** |
| The technician sees | *"This job was reassigned to another technician at 10:55 while you were offline. Your work has been saved to the job."* |

**Nothing is lost, and nothing is silently overwritten.** That sentence is the acceptance criterion
for the whole engine.

### 5.5 Invariant evaluation

Conflict resolution does not bypass invariants (`AR-008` §5). A command that survives conflict
resolution is still evaluated against every **H**-class rule, at the model layer.

| Case | Behaviour |
|---|---|
| `consume_part` but stock was consumed elsewhere | **Rejected.** Invariant I-31 (Σ reservations ≤ on-hand). The user is told, and a parts request is offered |
| `complete_work_order` but QC has not passed | **Rejected.** Invariant I-03 (`BRU-SRM-04`) |
| `assign_to_self` for an expired certification | **Rejected.** Invariant I-38 — **currently stubbed to "eligible" until Wave 5** (`AR-006` §5.2). **Registered in `GV-005` with an expiry**; until then this invariant is not enforced offline or online |

---

## 6. Conflict Disclosure

**The rule that makes the system usable rather than merely correct:**

> **Any resolved conflict is shown to the user, with what changed and why. The system never silently
> picks a winner on something a technician entered by hand.**

### 6.1 The two states that must never be conflated

| State | Meaning | Indicator |
|---|---|---|
| **Saved on this device** | The command is in the local journal. It survives app kill, battery death and reboot | One indicator |
| **Sent to the office** | The server has acknowledged it | A **distinct** indicator |

> **This distinction is the single most important UX decision in the offline design.** A technician
> who cannot tell the difference has no way to know whether four hours of work is safe, and the
> rational response to that uncertainty is to write it on paper as well — which is the failure mode
> the whole programme is trying to end.

### 6.2 What must always be visible

| Requirement | Note |
|---|---|
| Online / offline status | Persistent and unambiguous |
| Saved-on-device vs sent-to-office | §6.1 — two distinct indicators |
| Queued action count | Always visible |
| Last successful sync time | Always visible |
| Sync failure state **and what to do** | In Bengali, per NFR-078 |

### 6.3 Conflict presentation

| Element | Requirement |
|---|---|
| What changed | The specific field or decision, not "a conflict occurred" |
| When | Timestamp, in the technician's timezone |
| Who | The actor, where a person |
| **What happened to their work** | Explicit — preserved and attached, or rejected with a reason |
| What to do next | An action, or an explicit "nothing to do" |

**Content is `UI-009`'s** (written); **the states are this document's** (specified here); **the layout
is `UX-006`'s** (not yet designed). All three must exist before APP-01 ships.

---

## 7. Scope Resolution

### 7.1 What a device holds

| Class | Contents | Refresh |
|---|---|---|
| **Assigned work** | The user's jobs for the horizon (default: today + 2 days) | Every sync |
| **Job context** | Customer, device, history, entitlement, diagnostic tree, QC checklist per assigned job | Every sync |
| **Reference data** | Fault codes, hold reasons, part catalogue subset, price snapshot, branch and zone data | Daily or on change |
| **Van stock** | The technician's own van stock lines | Every sync |
| **Knowledge** | Repair manuals and past notes for assigned device models | On change, deferred channel |
| **Never** | Any residency-classified value; other technicians' work; unassigned customer data | — |

### 7.2 Scope rules

| # | Rule | Why |
|---|---|---|
| **SR-01** | Scope is **re-evaluated on every sync** | Assignment changes daily |
| **SR-02** | Scope **narrowing** removes data at the next sync; the **journal is never removed** | A command about a removed job still uploads |
| **SR-03** | **Residency-classified values are never downloaded** (`AR-001` LB-08). A device shows a masked form and reads through CD-233 online only | An unencrypted-at-rest NID on a lost phone is a notifiable breach |
| **SR-04** | Scope is enforced **server-side** (API-10). The device never requests a scope | A compromised client must not be able to widen its own scope |
| **SR-05** | Reference data is **versioned**; the device sends its version and receives a delta | 30 s on 3G (NFR-037) |

> **SR-03 has a real operational consequence that must be designed for, not discovered:** a technician
> offline cannot see a customer's NID. That is correct, and the app must state it clearly rather than
> showing an empty field.

---

## 8. Evidence Handling

Photographs, short video and voice notes are large, essential and **not urgent**.

| Aspect | Design |
|---|---|
| Capture | Written to encrypted local storage immediately; referenced by the command via `evidence_refs` |
| Upload | **Deferred, low-priority, resumable channel**, separate from command sync |
| Priority | **Evidence upload never delays state sync** (SP-09) |
| Compression | On-device, to a declared quality floor. Originals retained until acknowledged |
| Chunking | Resumable chunked upload; a dropped connection resumes, never restarts |
| Retention on device | Until server acknowledgement, then pruned |
| **A command referencing unuploaded evidence** | **Still applies.** The state change is not held hostage to a photograph |
| Completeness | The server records evidence as pending and surfaces it in the branch console, so an incomplete evidence pack is visible before it blocks a claim (`warranty_claim.evidence_incomplete`, `AR-009` §10.5) |
| Battery | Upload deferred to charging or Wi-Fi where policy allows (NFR-082, ≤ 12%/8 h) |

---

## 9. Failure Modes

| # | Failure | Behaviour |
|---|---|---|
| **F-01** | Sync interrupted mid-batch | Batch checksum fails; **retried whole** (SP-03). Per-command transactions mean accepted commands stay accepted (SP-02) |
| **F-02** | Battery death mid-sync | Journal intact; resume from last acknowledged (SP-08) |
| **F-03** | App killed mid-write | Journal write is transactional in SQLite. A partially written command is discarded and the action is re-offered |
| **F-04** | Local storage full | Prune read cache → warn → **block new evidence capture**. **Never prune the journal.** Escalate to supervisor |
| **F-05** | Server rejects a command | Journal retains it with the reason (CM-06). User is told and offered a next action |
| **F-06** | Command rejected repeatedly (3×) | Quarantine; escalate to dispatch; **do not block the queue** (mirrors `AR-009` C-04) |
| **F-07** | Device clock skew | §9.4 |
| **F-08** | Two devices, one user | Each device has its own `device_id` and journal. Commands interleave by server arrival; conflicts resolve normally |
| **F-09** | Offline beyond 24 h | Continues working. **Sync time is no longer guaranteed** and the user is told the queue is unusually large |
| **F-10** | Device lost or stolen | §11 |

### 9.4 Clock skew

Device clocks are user-settable and drift. A field timestamp is **client-authoritative** (§5.3), which
makes skew a data-integrity issue rather than a cosmetic one.

| Rule | Detail |
|---|---|
| The device records `issued_at` (local), `issued_at_utc` and `clock_offset_ms` measured at the last successful sync |
| The server stores the device's assertion **and** its own arrival time |
| A timestamp implying work **before its job was assigned**, or **in the future**, is flagged — applied, but marked for review |
| Monotonic device uptime is used to order commands **within** a journal, so ordering survives a clock change |

---

## 10. The Offline Test Harness

> **Offline correctness cannot be verified by inspection, and it cannot be verified by manual
> testing.** The defects live in specific interleavings of network loss, concurrent edit and retry.
> A dedicated harness runs **before every mobile release, as a gate**.

| Class | Scenarios |
|---|---|
| **Duration** | 24 h offline with continuous work; **48 h offline (beyond guarantee) with graceful behaviour, not corruption** |
| **Conflict** | Reassignment while offline · price change while offline · part consumed elsewhere · order cancelled while offline · **concurrent edit by two technicians** · entitlement amended while offline |
| **Failure** | Sync interrupted mid-batch · battery death mid-sync · app killed mid-write · storage full · **clock skew (forward and backward)** · server 500 mid-batch · duplicate upload |
| **Volume** | 200 queued commands · 500 pending evidence items · 3-day scope |
| **Network** | 3G · 2G · **intermittent connection dropping every 10 seconds** · captive portal returning HTTP 200 with the wrong body |
| **Security** | Device lost → remote revocation wipes the local store · local store unreadable without device credentials · **scope narrowing removes data but not the journal** |

**Every scenario asserts two invariants: zero data loss and zero double-application (DI-04).**

| Gate rule | |
|---|---|
| The harness runs in CI on every APP-01/02/03 build | Blocks release |
| A harness failure is a **release blocker**, never a known issue | |
| **New conflict scenarios discovered in the field are added to the harness before the fix is released** | The harness grows with what the field teaches |
| A **field pilot with respected senior technicians precedes general rollout** | `TR-01` control; adoption is as much at risk as correctness |

---

## 11. Security

| # | Rule |
|---|---|
| **SEC-01** | Local store encrypted (SQLCipher); key derived from device credentials + a server-issued component |
| **SEC-02** | **The local store is unreadable without device credentials** — an extracted database file is inert |
| **SEC-03** | **Remote revocation wipes the local store** and invalidates the device's tokens. Exercised in the harness |
| **SEC-04** | Device registration is per user per device; a `device_id` is bound at enrolment |
| **SEC-05** | **No residency-classified value is ever stored locally** (SR-03) |
| **SEC-06** | Evidence is encrypted at rest locally and in transit |
| **SEC-07** | An offline session has a maximum life; beyond it the app requires re-authentication to continue **submitting** — but **never to view queued work or capture evidence** |
| **SEC-08** | Scope is enforced server-side (SR-04). A tampered client cannot widen it |

> **SEC-07's asymmetry is deliberate.** A technician in a basement with an expired session must still
> be able to record what they did. Locking them out protects nothing — the work happens anyway, on
> paper — and loses the data.

---

## 12. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| Q-01 | Is the offline horizon **today + 2 days** correct for all three applications? APP-03 auditors may need a longer scope | Service Ops / Quality | **W2** | Scope design, storage budget |
| Q-02 | `UX-006` (Mobile UX Specification) is ⛔ **not written**. §6's states need a design before APP-01 ships in W2 | `UX-006` owner | **W2 — blocking** | APP-01 release |
| Q-03 | Does APP-03 (auditor) need **client-authoritative** resolution on any field where APP-01 needs server-authoritative? If so, ADR-024's shared engine assumption needs revisiting | Quality Manager | W4 | ADR-024 |
| Q-04 | What is the maximum offline session life (SEC-07)? | Head of InfoSec | W2 | Session policy |
| Q-05 | The I-38 certification invariant is stubbed to "eligible" until W5. Is offline assignment validation acceptable without it? | Service Ops / Head of InfoSec | **W2** | `GV-005` risk with expiry |

---

## 13. Decisions Recorded

| # | Decision | Options | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| D-A10-01 | Sync unit | Records; diffs/CRDT; **commands** | **Commands** | Only intent lets the server apply its own invariants | Every offline action is a registered command type |
| D-A10-02 | Conflict authority | Client wins; server wins; **per-domain matrix** | **Per-domain (§5.3)** | Each side is authoritative over what only it can know | Nine domains ruled |
| D-A10-03 | Conflict disclosure | Silent resolution; **always disclose** | **Always disclose** | Silent resolution on hand-entered data is what loses field trust | Every conflict has a user-facing state |
| D-A10-04 | Transaction granularity | Per batch; **per command** | **Per command** | One rejection must not roll back nine acceptances | SP-02 |
| D-A10-05 | Evidence channel | Same channel; **deferred separate channel** | **Deferred** | A 40 MB photo backlog must not delay a job status | SP-09 |
| D-A10-06 | Engine sharing | Per app; **one shared engine** | **Shared (ADR-024)** | Three implementations = three sets of conflict bugs | APP-01 in W2 carries generalisation cost |
| D-A10-07 | Test harness status | Test suite; **release gate** | **Release gate** | Offline defects are invisible to inspection and to manual testing | A harness failure blocks release |

---

## 14. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | The sync unit is decided with the rejected alternatives analysed | §3.1 |
| AC-02 | The command structure supports conflict detection, idempotency and ordering | §3.2 — `command_id`, `sequence`, `base_version` |
| AC-03 | Conflict detection is an algorithm, not a policy statement | §5.2 — six steps |
| AC-04 | Every domain has a declared resolution authority with a rationale | §5.3 — nine domains |
| AC-05 | Disclosure requirements are specified, including the saved-vs-sent distinction | §6.1, §6.2 |
| AC-06 | Every failure mode has a defined behaviour | §9 — ten modes |
| AC-07 | The test harness is a release gate with named scenario classes | §10 — six classes |
| AC-08 | Security covers device loss, local encryption and residency | §11 — eight rules |
| AC-09 | Zero data loss and zero double-application are traceable to a mechanism | §4.4 ledger, §3.2 `command_id`, §10 |

**Definition of done.** Complete when every criterion is met, `UX-006` exists (Q-02), and `PGD-000`'s
`AR-010` row is updated with a fresh enumeration timestamp.

---

## 15. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `AR-001` §10 QAS-05 | The quality-attribute scenario this document designs |
| Upstream | `AR-004` ADR-024 | One shared engine |
| Upstream | `AR-008` §5 | Invariants evaluated after conflict resolution |
| Upstream | `AR-009` | Idempotency and dead-letter semantics, mirrored here |
| Downstream | `AR-003` `APP-01`/`02`/`03` SDDs | Implementation design |
| Downstream | **`UX-006`** | Mobile UX realising §6's states — **not yet written (Q-02)** |
| Downstream | `QA-005` | §10 harness in the automation framework |
| Downstream | `SC-002` | Device-loss and local-store threats |
| Downstream | `IN-002` | Sync endpoints in OpenAPI |
| Lateral | `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-03` §6 | The sketch this document designs |
| Lateral | `../../project_content/03_UI_Copy_and_Microcopy/UI-009` | Conflict copy — written before the states existed |

---

## 16. References

**Within this repository**
`../PGD-000_*.md` · `./_CATEGORY_OVERVIEW.md` · `./AR-001` · `./AR-004` · `./AR-008` · `./AR-009` ·
`./AR-012` · `../_AUDIT/PGD-AUDIT-003_*.md`

**Workspace**
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-03` §6, `05-06` §1, §2, §5, §8 ·
`.../04_Portals_and_Applications/04-00` P02, P09, P11 · `.../03_Modules/A_.../M02_*.md` ·
`../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §16, §23 `TR-01` ·
`../../project_content/03_UI_Copy_and_Microcopy/UI-009*`

**External sources**

| Source | Verified |
|---|---|
| Hohpe & Woolf, *Enterprise Integration Patterns* — idempotent receiver, message store | 2026-08-18 |
| SQLCipher — encrypted SQLite | 2026-08-18 |
| Flutter 3.44 / Dart 3.12 (Impeller default on Android) | 2026-08-18 |

---

## 17. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. Converts `05-03` §6's protocol sketch into a command-journal design with a six-step conflict algorithm, a nine-domain authority matrix and a release-gating test harness. Raises Q-02: `UX-006` is not written and blocks APP-01 | *Pending — Chief Architect* |

---

*`AR-010` · Category 02 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
