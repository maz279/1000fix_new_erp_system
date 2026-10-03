---
id: SC-010
title: Audit Logging and Forensic Readiness Specification
category: 05 — Security, Privacy & Compliance
code: SC
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Chief Technology Officer, delegated to the Security Lead; evidential content jointly with the Quality Manager
approver: Design Authority (constituted under GV-002), countersigned by the Quality Manager
standards_basis: >
  ISO/IEC 27001:2022 A.8.15 (logging), A.8.16 (monitoring), A.8.17 (clock synchronisation) ·
  ISO/IEC 27037 (identification, collection and preservation of digital evidence) ·
  ISO/IEC 27041, 27042, 27043 (investigation assurance, analysis, incident investigation principles) ·
  NIST SP 800-92 (log management) · ISO 9001:2015 §7.5.3 · PDPA 2026 NFR-095 (5-year records)
traces_to: >
  PGD-000 SC-010 · M29 FR-SEC-037…043, T-02, T-03, T-13 · 05-06 NFR-014, NFR-095, §7 NFR-092 tracing ·
  05-04 §4 T5 · SC-001 SEC-C-038…044 · SC-002 TH-031…TH-033, TH-041…TH-046, TH-054 ·
  LG-019 · LG-009 · audit findings OP-19, DI-02
depends_on: SC-001 · SC-004 (attribution) · SC-006 (hash and signing) · SC-007 (residency of logs)
verified_on: 2026-08-18
priority: P1
needed_by: W2
enumeration_timestamp: 2026-08-18 15:10 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# SC-010 — Audit Logging and Forensic Readiness Specification

### Category 05 · Code `SC` · ISO/IEC 27001:2022 A.8.15–A.8.17 · ISO/IEC 27037 · NIST SP 800-92

---

> **Before writing, read this.**
>
> 1. **`PG-01` Register-first.** This document's row exists in `PGD-000` Category 05 as `SC-010`.
> 2. **`PG-03` Count, do not consult.** Volume and field figures counted at
>    **2026-08-18 15:10 (+06)**.
> 3. **`PG-06` Cite standards.** §2.1.
> 4. **`PG-M4` Verify citations.** **`OP-19` applies here**: `NFR-092` means two different things in
>    `05-06`. Every citation of `NFR-090`, `-091`, `-092` in this document **names its section**.

---

## 1. Purpose

This document specifies **what is recorded, how it is made untamperable, who may read it, how long
it is kept, and how it becomes evidence** — the log a regulator, a court, an ISO 9001 auditor, a
corporate client's security team and an incident responder each need, from one mechanism rather
than five.

Three commercial and regulatory claims in this programme **rest entirely on log quality**, and none
of them has a specification behind it:

| Claim | Depends on | Today |
|---|---|---|
| **ISO 9001:2015 certification** (`NFR-024`) | Documented information: who changed what, when, and the traceability of a nonconformity | ◐ `NFR-014` states the requirement in one line |
| **`M06` destruction and purge certificates** — a **commercial product** | Chain of custody, per-access logging, verifiable destruction evidence | ◐ `M06` specifies certificates; nothing specifies the log beneath them |
| **`LG-019` e-signature evidence** | An evidential chain that survives being challenged years later | ⚠ `LG-019` `O-07`: **no re-sealing policy exists** |

Add to those the statutory floor: **`NFR-095` requires processing records for a minimum of five
years**, and **`NFR-014` requires a complete immutable audit trail — who, what, when, before,
after** — and the position is that the estate has four consumers of an evidential-grade log and no
document defining one.

There is also a failure mode this document exists to prevent, and it is the one `SC-002` rates
highest in its class: **a log that contains personal data becomes a second copy of that data**, in
a system with weaker access control than the one it describes. `SC-001` `SEC-DC-4` states the rule —
**a log is a copy** — and `M29` `T-13` states the mechanism: redaction **at emission**, not at
ingestion.

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | **Six log classes**, their purpose, content and retention — they are not one thing |
| 2 | **What is logged** — event catalogue by class, with mandatory fields |
| 3 | **Attribution** — what makes an entry point to a natural person, and what defeats it |
| 4 | **Immutability** — insert-only at database privilege level, hash chaining, and what each protects against |
| 5 | **Personal data in logs** — the redaction-at-emission rule and the residency consequence |
| 6 | **Access to logs** — logs are `T5`, and the access log for the access log |
| 7 | **Retention and disposal**, including the interaction with erasure |
| 8 | **Time** — synchronisation, source of truth, and why it is a control |
| 9 | **Forensic readiness** — ISO/IEC 27037 identification, collection, acquisition, preservation |
| 10 | **The evidential chain** for `M06` certificates and `LG-019` signatures, and its re-sealing |
| 11 | **Volume, performance and searchability** |
| 12 | **Monitoring and alerting** (A.8.16) — what the logs are watched for |

**Explicitly out of scope:**

| Topic | Owned by | Why |
|---|---|---|
| Incident response process | `SC-011` | This document makes evidence available; `SC-011` uses it |
| Observability for performance | `AR-001` §9.2, `PE-005` | Traces and metrics are a neighbouring concern; §4.6 states the boundary |
| Retention **periods** | `LG-009` | Referenced, never restated (`CP-01`) |
| Legal effect of an e-signature | `LG-019` | This supplies the evidence; `LG-019` states the effect |
| Hash and signature algorithms | `SC-006` §3.4 | Referenced |
| Business reporting and analytics | `M25`, `M62` | An audit trail is not a data source for analytics |
| Control testing | `M60` | `M60` reads logs as evidence; it does not own them |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| **Platform Squad / `M29`** | §4 event catalogue, §5 immutability — the build specification |
| **Every module developer** | §4.7 — what you get for free, and the one thing you must do |
| **Quality Manager** | §10 evidential chain; ISO 9001 evidence |
| **`M06` Data Services** | §10.2 — the log beneath the certificate |
| **Incident responder** | §9 forensic readiness |
| **Auditor, regulator, court** | §5, §9, §10 — written to be relied on |
| **CDO** | §6 personal data in logs; §7 retention vs erasure |

---

## 2. Basis

### 2.1 Standards conformance

| Standard | How this document conforms | Departure |
|---|---|---|
| **ISO/IEC 27001:2022 A.8.15** | *Logging* — §4 event catalogue, §5 protection, §7 retention | — |
| **A.8.16** | *Monitoring activities* — §12 | Alerting depends on correlation capability `SEC-CON-03` does not fund. §12 states what is achievable without a SIEM |
| **A.8.17** | *Clock synchronisation* — §8 | Treated as a **control**, not an operational detail |
| **ISO/IEC 27037** | Identification, collection, acquisition and preservation of digital evidence — §9 | Full DEFR/DES role definition is disproportionate; §9.4 names the competence requirement instead |
| **ISO/IEC 27041, 27042, 27043** | Investigation assurance, analysis, incident-investigation principles | Referenced for `SC-011`; §9 provides the readiness half |
| **NIST SP 800-92** | Log management infrastructure, prioritisation, retention | — |
| **ISO 9001:2015 §7.5.3** | Control of documented information | §10.1 |
| **PDPA 2026** `NFR-095` | Processing records ≥ 5 years | §7.1 |

> **`OP-19` compliance note.** `05-06` uses `NFR-090`, `-091`, `-092` for **two different sets** —
> §6.3 privacy obligations and §7 maintainability. Every citation in this document names its
> section: **`05-06` §7 `NFR-092`** is distributed tracing with a single correlation id; **`05-06`
> §6.3 `NFR-092`** is the transparency notice. Following the convention `AUDIT-016` `AP-02` §5
> established.

### 2.2 Source material

| Source | Supplies |
|---|---|
| `M29` §5.5 | `FR-SEC-037`…`FR-SEC-043` — immutable trail, immutability, financial coverage, data-access logging, bulk export control, search and retention, processing records |
| `M29` §6 | `T-02` audit by inheritance · `T-03` insert-only at DB privilege, hash chaining per partition · `T-13` **no personal data in logs, redacted at emission** · `T-14` **~50M entries/year at Wave 8** |
| `M29` §10.1 | `fix.audit.entry`, `fix.data.access.log` field sets |
| `05-06` §4 | `NFR-014` complete immutable audit trail |
| `05-06` §6.3 | `NFR-095` ≥ 5 years |
| `05-06` §7 | `NFR-092` distributed tracing, single correlation id |
| `05-04` §4 | **`T5`** — audit logs are a restricted tier object |
| `DI-02` | **100% audit coverage of financial transactions, reconcilable to source** |
| `LG-009` | Retention classes; `RC-22` security logs |
| `LG-019` | e-signature evidence statement; **`O-07` no re-sealing policy** |
| `SC-006` §3.4, §10.4 | SHA-256 chain; `RS-1`…`RS-6` re-sealing |

### 2.3 Enumeration

| # | Figure | **Counted / stated 2026-08-18 15:10 (+06)** | Source |
|---|---|---:|---|
| 1 | Audit entries per year at Wave 8 | **~50 million** | `M29` `T-14` |
| 2 | Minimum retention | **5 years** | `NFR-095` |
| 3 | Implied working volume at 5-year retention | **~250 million entries** | Derived — §11 |
| 4 | Restricted field groups whose access must be logged | **13** | `05-04` §5 |
| 5 | `S3` field classes | **9** | `05-02` §10 |
| 6 | Residency-classified classes requiring per-read logging | **7** (+2 proposed) | `05-06` §6.4 |
| 7 | Log classes specified here | **6** | §3 |
| 8 | Documents specifying log content before this one | **0** | — |

---

## 3. Six Log Classes

> **The single most common logging failure is treating all logs as one thing.** An audit trail and
> an application log have different consumers, different retention, different tamper-resistance and
> different personal-data exposure. Conflating them produces either a trail too weak to be evidence
> or an application log too expensive to keep.

| # | Class | Answers | Store | Immutable? | Retention | Contains personal data? |
|---|---|---|---|:--:|---|---|
| **`L1`** | **Business audit trail** | *Who changed what, when, from what, to what* | `DS-07` (`Z3`) | **Yes — insert-only + hash chain** | **≥ 5 years** (`NFR-095`); financial per `LG-009` | **Field values, yes — by design.** §6.2 |
| **`L2`** | **Data access log** | *Who read which sensitive record, and why* | `DS-07` | **Yes** | ≥ 5 years | **Record identity, not content** |
| **`L3`** | **Authentication and authorisation log** | *Who signed in, from where, with what assurance; what was denied* | `DS-07` | **Yes** | ≥ 5 years | Identity + IP hash |
| **`L4`** | **Administrative and privileged log** | *What an administrator did, and under what elevation* | `DS-07` + session recordings | **Yes** | ≥ 5 years | Yes |
| **`L5`** | **Application and system log** | *What the software did and why it failed* | `DS-11` (`Z5`, Loki) | No | 30–90 days | **No — redacted at emission** |
| **`L6`** | **Evidential artefact chain** | *This certificate/signature was produced then, by whom, over what* | `M24` + `DS-07` anchor | **Yes — signed** | **Evidential life of the artefact**, potentially decades | Depends on the artefact |

| # | Rule |
|---|---|
| `LC-1` | **`L1`–`L4` and `L6` are `T5` objects** (`05-04` §4). Named allow-list, step-up authentication, every access logged |
| `LC-2` | **`L5` must never be relied on as evidence.** It is not immutable, it is short-retention, and it is redacted — that is correct for its purpose and disqualifying for evidence |
| `LC-3` | **A single correlation id ties an event across all six classes** (`05-06` §7 `NFR-092`) |
| `LC-4` | **`L6` is anchored into `L1`** so an artefact's existence is provable from the immutable trail even if the artefact store is compromised |

---

## 4. What Is Logged

### 4.1 `L1` — the business audit trail

**Coverage: every change to every controlled object.** `NFR-014`, `BRU-SEC-12`; `DI-02` requires
**100% of financial transactions, reconcilable to source**.

| Field | Content | From `M29` §10.1 |
|---|---|:--:|
| `model`, `res_id`, `field` | What object and which attribute | ✔ |
| `operation` | create / write / unlink / approve / state-change | ✔ |
| `old_value`, `new_value` | **Before and after** — `NFR-014` is explicit | ✔ |
| `actor_id` | The **natural person**, never a service identity alone — §4.5 | ✔ |
| `occurred_at` | Server-authoritative UTC + offset | ✔ |
| `correlation_id` | Ties to `L2`–`L6` | ✔ |
| `company_id`, `operating_unit_id` | Scope, so the trail is itself tier-filterable | ✔ |
| `hash_chain_ref` | Position in the tamper-evidence chain | ✔ |
| ⊕ `on_behalf_of` | Where a delegation applied — **`SC-002` `TH-079`** | new |
| ⊕ `elevation_ref` | Where an elevation applied — `PA-7` | new |
| ⊕ `source` | ui / api / job / migration / import — **a migration is not a user action and must not look like one** | new |

### 4.2 `L2` — the data access log

**Coverage: every access — including reads — to personal, `S3`-classified and residency-classified
data** (`FR-SEC-040`, `AS-14`, `EA-10`).

| Field | Content |
|---|---|
| `model`, `res_id`, `classification` | What was read, and its class |
| `actor_id`, `portal`, `ip_hash` | Who, from where — **IP hashed, not stored** |
| **`purpose`** | **The declared processing purpose** — `SC-003` `PD-1`. An access with no purpose is an exception |
| `occurred_at`, `correlation_id` | |
| `export_flag`, `record_count` | Bulk detection (`BRU-SEC-05`, `EA-12`) |
| ⊕ `step_up_ref` | The elevated-session reference that permitted a `T5` read (`SC-004` `SC-004-F-04`) |
| ⊕ `residency_service_ref` | For `Z4` reads, the `CD-233` call — **the single audit point `SEC-ZR-2` promises** |

| # | Rule |
|---|---|
| `DA-1` | **The entry is written before the value is returned** (`SC-002` `TH-043`). A log written after a successful read does not record a read that crashed the caller mid-response |
| `DA-2` | **A `T5` read that cannot be logged does not happen.** Fail closed |
| `DA-3` | **Reads are logged individually even when the elevation is amortised.** `SC-004` amortises step-up over a 15-minute session; **logging is never amortised** |
| `DA-4` | Bulk export writes **one entry per export with its scope and count**, plus the approval reference |

### 4.3 `L3` — authentication and authorisation

| Event | Logged |
|---|---|
| Authentication success / failure, with reason class | ✔ |
| **MFA enrolment, use, failure; step-up grant** | ✔ |
| Token issue, refresh, **revocation** | ✔ |
| Session start, end, forced termination | ✔ |
| **Authorisation denial** — `EP-2`…`EP-5` | ✔ **A denial is more interesting than a grant.** `SC-002` `AB-05` looks exactly like a series of denials |
| Federation assertion accepted from a client IdP | ✔ (`TH-007`) |
| Password reset, credential change, device registration | ✔ |

> **`SC-010-F-01`. Logging authorisation *denials* is the single highest-value low-cost detection
> control in this estate.** A customer enumerating invoice ids produces hundreds of `EP-4` denials
> and nothing else. Without denial logging, the only trace of `AB-05` being *attempted* is its
> success.

### 4.4 `L4` — administrative and privileged

| Event | Logged |
|---|---|
| **Elevation request, approval, grant, expiry** — **written by the grant path, before the elevation takes effect** (`SC-004` `PA-7`) | ✔ |
| **Every privileged session, recorded** (`NFR-070`); **recording failure terminates the session** | ✔ |
| **Break-glass use** — with the independent notification reference (`BG-A2`) | ✔ |
| Role, permission, record-rule and field-permission change | ✔ |
| **SoD exception grant, its mitigating control and expiry** | ✔ |
| Configuration change to a security control | ✔ |
| **Vault key access, rotation, zeroization** (`SC-006` `CE-4`) | ✔ |
| Direct database access, migration or data-fix execution | ✔ — `source` field, §4.1 |

### 4.5 Attribution — what makes an entry point to a person

| # | Rule | Defeated by |
|---|---|---|
| `AT-1` | **Every entry names a natural person**, or the service identity **and its accountable human owner** (`FR-SEC-012`) | A service account with no owner |
| `AT-2` | **A shared login destroys attribution entirely** — `SC-002` `TH-012`, `TH-041` rate it High, and `M29` §7.1 records that branch counters share logins *in practice* today | Shared credentials |
| `AT-3` | **A delegated action names both the delegate and the delegator** (`on_behalf_of`) | Delegation logged as the delegate only |
| `AT-4` | **An elevated action names the elevation** (`elevation_ref`) | Elevation not referenced |
| `AT-5` | **An automated action names the automation and the human who configured or triggered it** | "system" as an actor |
| `AT-6` | **A migration or import is marked `source=migration`** and never looks like a user action | Bulk load attributed to whoever ran it |

> **`SC-010-F-02`. `AT-2` is a people problem the log cannot fix and must not conceal.** Every
> mechanism in this document assumes one credential, one person. Shared logins at 51+ branch
> counters would make the entire `L1` trail attributable to a counter rather than to a person —
> **an ISO 9001 auditor and a fraud investigator would both reject it**. The mitigation is `SC-004`
> identity provisioning plus supervision, and it is named here because a logging specification that
> stays silent about it implies a guarantee it cannot give.

### 4.6 The boundary with observability

`AR-001` §9.2 defines the OTel → Prometheus/Loki/Tempo pipeline. That is `L5`, and it is a different
system with a different purpose.

| | `L1`–`L4`, `L6` (this document) | `L5` observability (`PE-005`) |
|---|---|---|
| Purpose | Evidence and accountability | Diagnosis and performance |
| Store | `DS-07`, transactional, in `Z3` | `DS-11`, `Z5` |
| Written | **In the same transaction as the change** | Asynchronously, best-effort |
| Loss tolerance | **Zero — the transaction fails** (`SC-001-D-06`) | Acceptable |
| Personal data | Present by design, protected as `T5` | **Absent — redacted at emission** |
| Retention | ≥ 5 years | 30–90 days |

> **`SC-010-F-03`. The two are frequently merged, and merging them fails both.** An evidential trail
> shipped through a best-effort pipeline is not evidence; an observability stack retaining personal
> data for five years is a `LG-009` and residency breach. **They share a correlation id and nothing
> else.**

### 4.7 What a module developer must do

Almost nothing — and that is the design (`SC-001` `SEC-SD-4`).

| # | Obligation |
|---|---|
| `MD-1` | **Nothing for `L1`.** Audit is inherited by base-model inheritance and ORM interception. **A module cannot opt out and a developer cannot forget** (`M29` `T-02`). Verified by a model-registry check in CI |
| `MD-2` | **Nothing for `L2` on classified fields.** The classification drives the log (`SC-007` `RC-3`) |
| `MD-3` | **`SR-26` prohibits a module writing its own audit code.** Module-written audit produces inconsistent, incomplete, unqueryable trails |
| `MD-4` | **The one obligation: declare the processing purpose** on any operation reading `S3` or residency-classified data, so `L2.purpose` is populated |
| `MD-5` | **Never log a classified value.** `SR-11` redaction is library-level; deliberately constructing a log line containing an `S3` value defeats it |

---

## 5. Immutability

Three mechanisms, each protecting against a different adversary. **One alone is insufficient and
the reason is worth stating**, because "the audit log is immutable" is usually a claim about only
the first.

| # | Mechanism | Protects against | Does **not** protect against |
|---|---|---|---|
| `IM-1` | **Insert-only at the database privilege level** — the application role holds **no `UPDATE` or `DELETE` grant** on audit tables (`M29` `T-03`) | The application, a compromised application account, an ordinary administrator acting through the app | A database superuser; direct DB access |
| `IM-2` | **Hash chaining per partition** (`M29` `T-03`), SHA-256 (`SC-006` §3.4) | **Silent modification or deletion by anyone**, including a DB superuser — the chain breaks | Someone who rewrites the whole chain forward from the change |
| `IM-3` | **External anchoring** — the chain head is periodically signed and written to an independent store (`M24`, and to the `L6` artefact chain) | **Chain rewriting**, because the historical head no longer matches | Nothing further; this is the ceiling of what is achievable in-estate |

| # | Rule |
|---|---|
| `IM-4` | **A chain verification job runs continuously**, and a break is a **security incident** (`SC-002` `TH-032`) |
| `IM-5` | **A break is never repaired.** It is recorded, investigated and the chain re-anchored forward. Repairing a broken chain destroys the only evidence that something happened |
| `IM-6` | **Anchoring cadence is at most hourly**, so the un-anchored window is bounded |
| `IM-7` | **Backups of `DS-07` are immutable copies** (`SEC-DR-04`) — otherwise `IM-1`…`IM-3` are defeated by restoring an older trail |
| `IM-8` | **`SC-006` `RS-2` re-sealing applies to the chain.** SHA-256 is sound today; an anchor signed with a 2027 algorithm must be re-sealed before that algorithm is disallowed (`HZ-02`, `HZ-03`) |

> **`SC-010-F-04`. `IM-2` without `IM-3` is a common and comfortable illusion.** A hash chain proves
> internal consistency; it does not prove that the current chain is the original one. An adversary
> with sufficient privilege recomputes it. **External anchoring is what makes the chain a
> commitment**, and it is cheap — one signed hash per hour.

---

## 6. Personal Data in Logs

### 6.1 The rule

> **`SC-001` `SEC-DC-4`: a log is a copy.** Classified fields are **redacted at emission**, not at
> ingestion (`M29` `T-13`, `OPS-04`, `BRU-SEC-24`).

| # | Rule |
|---|---|
| `PD-1` | **Redaction is a logging-library responsibility, configured from the field classification** — never a per-call developer decision (`SR-11`) |
| `PD-2` | **At emission, not at ingestion.** Redaction at ingestion means the plaintext existed in `Z2` memory, on the wire, and possibly on `Z2` disk |
| `PD-3` | **`L5` contains no personal data at all.** Not names, not phone numbers, not addresses — identifiers only |
| `PD-4` | **An error message or stack trace is a log** (`SR-23`, OWASP `A10:2025`) |
| `PD-5` | **A residency-classified value must never reach `DS-11`.** `DS-11` is in `Z5` and may be regional — **an unredacted resident value in a log aggregator is a residency breach nobody committed** (`SC-002` `TH-048`, `TH-054`) |

### 6.2 The deliberate exception — `L1` holds field values

`L1` records `old_value` and `new_value`, and `NFR-014` requires it. **That means the business audit
trail legitimately contains personal data**, including `S3` values, and it must be treated as such.

| # | Consequence |
|---|---|
| `PE-1` | **`L1` is `T5`** — named allow-list, step-up, every access logged (`LC-1`) |
| `PE-2` | **A change to a residency-classified field records its `L1` entry in `Z4`, not `Z3`** — otherwise the trail becomes the residency leak. §6.3 |
| `PE-3` | `L1` is **encrypted at field level** for `S3` values, under the same key class as the source field (`SC-006` §7) |
| `PE-4` | **`L1` access is itself logged into `L2`** — the access log for the audit log. Otherwise the most sensitive store in the estate is the one nobody watches |

### 6.3 The residency split of the trail

> **`SC-010-F-05`. This is a design consequence no source document states, and it is not optional.**
>
> If `L1` records `old_value`/`new_value` for an NID field, and `L1` lives in `Z3`, then **the audit
> trail becomes a regional copy of a resident value** — defeating `SC-007` entirely, through the one
> mechanism designed to be complete.
>
> **Position: the audit trail is split the same way the data is.** A change to a residency-classified
> field writes its `L1` entry to a **resident audit partition in `Z4`**, joined to the regional trail
> by the correlation id. The regional entry records **that** the field changed, by whom and when; the
> resident entry records **what it changed from and to**.
>
> Raised to `M29`, `AR-001` and `SC-007` as finding `SCA-11`. **This changes the `M29` §10.1
> `fix.audit.entry` design and must be resolved before W1 build.**

---

## 7. Retention, Access and Erasure

### 7.1 Retention

| Class | Minimum | Basis |
|---|---|---|
| `L1` business audit | **≥ 5 years** | `NFR-095`; financial records per `LG-009` and tax retention (7 years, `BRU-TAX-24`) |
| `L2` data access | ≥ 5 years | `NFR-095` |
| `L3` auth | ≥ 5 years | `NFR-095`; `LG-009` `RC-22` |
| `L4` privileged + recordings | ≥ 5 years | `NFR-070` |
| `L5` application | 30–90 days | Operational only |
| `L6` evidential chain | **Evidential life of the artefact** | `M06`, `LG-019` — potentially decades |

**Periods are `LG-009`'s** (`CP-01`). Where `LG-009` and `NFR-095` differ, the longer governs, and
`LG-009` §4.4's five-versus-seven-year reconciliation applies.

### 7.2 Access

| # | Rule |
|---|---|
| `AC-1` | **Logs are `T5`.** Named allow-list, step-up authentication, per-access logging |
| `AC-2` | **`R49` GRC / Internal Audit has read access under a recorded audit purpose** (`SC-004` `AP-R49`) |
| `AC-3` | **`R33` IT Administrator does not have unrestricted audit read.** Administering a system is not a reason to read who did what in it |
| `AC-4` | **Nobody has write or delete** — `IM-1` |
| `AC-5` | **Export of audit data is a bulk export**: approval, logging, rate limit (`SEC-C-042`) |
| `AC-6` | A regulator or court receives an extract under §9.3 chain of custody, not a database dump |

### 7.3 Erasure — the tension, resolved

> A data subject exercises erasure. The audit trail records what their data used to be. **What
> happens?**

| # | Position |
|---|---|
| `ER-1` | **The audit trail is retained.** `NFR-095` requires 5-year processing records; `BRU-SEC-23` prohibits purging anything under legal hold; erasure has a statutory-obligation exception (`CR-06`, `LG-008` `P-16` risk statement) |
| `ER-2` | **The erasure itself is a logged event**, with its basis |
| `ER-3` | **`L1` retains the *fact and basis*, and the `old_value` of an erased field is itself subject to the erasure where the retention basis does not require it.** A field erased because consent was withdrawn, with no statutory retention, has its historical values crypto-erased (`SC-006` §8.1) while the change record persists |
| `ER-4` | **`SC-002` §10 records this as a privacy harm — non-repudiation as harm**: the record that a named person exercised erasure outlives the erased data. **Accepted, with justification, and stated in `LG-008`** rather than concealed |
| `ER-5` | **The data subject is told this** — `LG-008` `P-16`: *"Some records must be kept by law even after you ask us to delete your data. We will tell you which and until when."* |

---

## 8. Time

A.8.17 makes clock synchronisation a control, and here is why: **an audit trail whose timestamps
cannot be trusted is not evidence.** A sequence of events across `Z1`, `Z2`, `Z4` and `Z6` is
reconstructable only if their clocks agree.

| # | Rule |
|---|---|
| `TM-1` | **All timestamps are server-authoritative.** A client-supplied time is recorded as a *claim*, in a separate field, never as `occurred_at` (`SC-002` `TH-039`) |
| `TM-2` | **All servers synchronise to a common, authenticated time source**, with drift monitored and alerted |
| `TM-3` | **Stored in UTC with the offset preserved.** Bangladesh operates at UTC+06 with no daylight saving; the offset is recorded anyway, because a second country is `BO-18` |
| `TM-4` | **Clock drift beyond a defined tolerance is a security event**, not a housekeeping ticket |
| `TM-5` | **Order within a partition is guaranteed by the hash chain**, so equal timestamps remain orderable |
| `TM-6` | **Offline-capable clients** (technician, rider apps — `AR-010`) record both **device time** and **server receipt time**; the server time is authoritative and the divergence is retained |

> **`TM-6` matters more than it looks.** `AR-010` specifies offline-first synchronisation for field
> applications. An offline technician's actions carry device time; a device with a wrong or
> manipulated clock would otherwise inject false chronology into the evidential trail.

---

## 9. Forensic Readiness

ISO/IEC 27037 defines identification, collection, acquisition and preservation. **Readiness means
these are possible before they are needed**, which is the difference between an investigation and a
scramble.

### 9.1 Readiness requirements

| # | Requirement |
|---|---|
| `FR-1` | **Sources are identified in advance.** A register names every log source, its location, format, retention and owner. **`SC-011` cannot begin an investigation by discovering where logs live** |
| `FR-2` | **Retention exceeds plausible detection latency.** Breaches are frequently found months later; 30-day logs would mean an undetectable history |
| `FR-3` | **Correlation is possible** — one id across six classes (`LC-3`) |
| `FR-4` | **Extraction does not disturb the source.** Read-only, from a replica where possible |
| `FR-5` | **Integrity is provable at extraction** — the hash chain and its anchors travel with the extract |
| `FR-6` | **Privileged session recordings are retrievable by session, actor and time** |
| `FR-7` | **`Z4` evidence is collectable without a cross-border transfer.** Collection, analysis and storage occur in-country, or the investigation itself becomes a `TF-1` transfer (`SC-007` §6.1) |

### 9.2 What is collected

| Source | Content |
|---|---|
| `L1`–`L4` | Filtered by actor, object, time, correlation id |
| Privileged session recordings | `L4` |
| `L5` application logs, if within retention | Context |
| Gateway logs | Request-level, `Z1` |
| Egress logs | `Z6` — **what left the company** |
| `CD-233` access logs | `Z4` reads |
| Identity provider logs | Sessions, tokens, revocations |
| System and container state | Where a host is implicated |

### 9.3 Chain of custody

| # | Requirement |
|---|---|
| `CC-1` | Every extraction records: **what, when, by whom, from where, under what authority, and the hash of the extract** |
| `CC-2` | **The extract is hashed at acquisition**, and the hash is recorded independently |
| `CC-3` | **Every transfer of custody is recorded**, both directions |
| `CC-4` | **Analysis is performed on a copy**; the acquired evidence is preserved unaltered |
| `CC-5` | **A legal hold suspends disposal** for the material in scope (`FR-GRC-039`, `BRU-SEC-23`), and the hold is instructed through `M24` transactionally — never partially applied |
| `CC-6` | Custody records are themselves `L6` and are anchored into `L1` |

### 9.4 Competence

| # | Requirement |
|---|---|
| `CP-1` | **A named person is accountable for evidence acquisition** and is trained for it. `SC-011` names the role |
| `CP-2` | **Acquisition is not performed by a person implicated in the incident** |
| `CP-3` | Where competence is not held in-house, an external specialist is engaged — **and the engagement is pre-arranged, not sourced during an incident** |

> **`SC-010-F-06`. `CP-3` is the readiness item most often missing.** `OP-09` records that the
> on-call rota needs ten people and has none; forensic competence is a further, narrower gap.
> **A retainer arranged in advance costs little; sourcing a specialist during a Sev1 costs days.**
> Raised to `SC-011` and `GV-005`.

---

## 10. The Evidential Chain

### 10.1 ISO 9001 evidence

| # | Requirement | ISO 9001 clause |
|---|---|---|
| `Q-1` | Documented information is identifiable, retrievable and protected from unintended alteration | §7.5.3 |
| `Q-2` | A nonconformity is traceable to the action that caused it and the correction applied | §10.2 |
| `Q-3` | **`L1` supplies the traceability; `M23` supplies the process** | — |
| `Q-4` | **100% audit coverage of financial transactions, reconcilable to source** (`DI-02`) is a certification-relevant claim and is tested, not asserted | — |

### 10.2 `M06` destruction and purge certificates

The certificate is the product; **the log is what makes it defensible** (`SC-006` §10).

| # | Requirement |
|---|---|
| `M6-1` | **Chain of custody from intake**: a serialised asset-tag event opens the log, and every stage appends |
| `M6-2` | **Every access to a data case is logged** (`BRU-SEC-03`), with dual-control evidence for secure-area movement (`BRU-DTS-01`) |
| `M6-3` | **The sanitisation event records technique, standard and version, tool and firmware version, operator, witness, verification result** (`SC-006` §10.1) |
| `M6-4` | **Cryptographic erase records the ISO/IEC 19790 zeroization confirmation** (`SC-006` `CE-4`) |
| `M6-5` | **The certificate is hashed, countersigned, and anchored into `L1`** — so its existence at a given time is provable from the immutable trail even if the certificate store is later compromised |
| `M6-6` | **The verification endpoint resolves a certificate number to its chain**, not merely to a stored PDF |
| `M6-7` | **`SC-006` `RS-2` re-sealing applies**, because a certificate outlives its signing algorithm (`HZ-02`, `HZ-03`) |

### 10.3 `LG-019` e-signature evidence — and `O-07`

| # | Requirement |
|---|---|
| `ES-1` | The signature event records: signer identity and **assurance level** (`SC-004` §6.1), the exact document hash, time, IP hash, consent to sign, and the notice version presented |
| `ES-2` | **The document hash, not the document, is the evidential anchor** |
| `ES-3` | **Anchored into `L1`** |
| `ES-4` | **`LG-019` `O-07` is closed by `SC-006` §10.4 `RS-1`…`RS-6`**: signatures and hashes record their algorithm and date, verification keys are retained for the artefact's evidential life, and **re-sealing preserves the original rather than replacing it** |
| `ES-5` | **A challenged signature is answerable years later** — which is the only test that matters |

---

## 11. Volume, Performance and Search

| # | Figure | Value | Source |
|---|---|---|---|
| `V-1` | Audit entries per year at Wave 8 | **~50 million** | `M29` `T-14` |
| `V-2` | Working population at 5-year retention | **~250 million** | Derived |
| `V-3` | Search requirement | **Sub-second on the working window** | `M29` `T-14` |
| `V-4` | Searchable by | actor, object, field, time, **correlation id** | `FR-SEC-042` |

| # | Design requirement |
|---|---|
| `PF-1` | **Time-partitioned**, with the hash chain **per partition** (`M29` `T-03`) |
| `PF-2` | **A working window stays hot; older partitions move to cold storage** — retrievable, immutable, still chained |
| `PF-3` | **The audit write is inside the transaction** and must not dominate its latency budget. `SEC-C-059` gives authorisation ≤ 15 ms p95 inside the `NFR-002` 400 ms budget; **audit write shares that budget and must be sized in `PE-006`** |
| `PF-4` | **Audit write failure fails the transaction** (`SC-001-D-06`). This makes audit durability an availability dependency and it must be engineered as one |
| `PF-5` | **`L1` is never the source for analytics.** `M25`/`M62` read business data, not the trail |

> **`SC-010-F-07`. `PF-3` and `PF-4` together are the sizing risk in this document.** An audit
> subsystem that fails closed and sits inside the transaction is a **correctness decision with an
> availability cost**. It is the right decision — `DI-02` requires 100% financial coverage and an
> unaudited financial transaction is worse than a refused one — but `PE-006` must size for it
> explicitly. Raised as a sizing input.

---

## 12. Monitoring and Alerting (A.8.16)

**What is achievable without a SIEM**, stated honestly, because `SEC-CON-03` funds no correlation
platform and `SC-001` §10 defers zero-trust tenet 7 for the same reason.

| # | Detection | Achievable now? |
|---|---|---|
| `MO-1` | **Hash-chain break** | ✔ A scheduled verification job — **the highest-value alert in the estate** |
| `MO-2` | **Authorisation-denial spike by actor** — `AB-05` enumeration | ✔ Query over `L3` |
| `MO-3` | **Bulk export by an identity in a notice period** — `AB-11` | ✔ `L2` + HR status |
| `MO-4` | **`T5` access without a linked work item** — `AB-09` | ✔ `L2` `purpose` + correlation |
| `MO-5` | **Break-glass use** | ✔ Independent notification path (`BG-A2`) |
| `MO-6` | **Elevation without a recorded approval** | ✔ `L4` reconciliation |
| `MO-7` | **A certification cycle with zero revocations** — `AB-13` | ✔ `SC-004` `CT-5` |
| `MO-8` | **Access to `Z4` outside `CD-233`** | ✔ Network-level; should be impossible (`SEC-ZR-2`) |
| `MO-9` | **Cross-source behavioural correlation** — identity + network + application + egress | ✖ **Requires a SIEM.** `SC-001` `Q-07` |
| `MO-10` | Real-time anomaly detection on access patterns | ✖ Same |

> **`SC-010-F-08`. Eight of ten detections are achievable with scheduled queries over a
> well-designed trail, and no product.** That is the value of specifying the log properly rather
> than buying a platform to compensate for a weak one. **The two that are not achievable are named
> rather than implied**, and they are the reason `SC-001` §10 defers tenets 5 and 7.

---

## 13. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | **Does the audit trail split across `Z3`/`Z4`?** (`SCA-11`, §6.3) | Chief Architect with CDO | **W1 — before `M29` build** | `fix.audit.entry` design; `SC-007` completeness |
| `Q-02` | What is the external anchoring target for `IM-3`? | Security Lead | W2 | Chain commitment |
| `Q-03` | Is the audit-write latency budget sized in `PE-006`? | Platform Eng | W1 | `PF-3`, `PF-4` |
| `Q-04` | Is a **forensic specialist retainer** arranged in advance? (`CP-3`) | CTO | W2 | `SC-011` capability |
| `Q-05` | Do `LG-009` retention classes cover all six log classes, or only `RC-22`? | Legal with CDO | W2 | §7.1 |
| `Q-06` | Is a SIEM funded, or do `MO-9`/`MO-10` stay out of scope? | CTO with CFO | W2 | `SC-001` `Q-07`; `SC-009` |
| `Q-07` | Who holds `AC-2` audit read besides `R49`, and under what recorded purpose? | Security Lead | W1 | `AP-R49`; `PE-4` |

---

## 14. Decisions Recorded

| # | Decision | Options | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `SC-010-D-01` | Log model | One log · **Six classes** | **Six** | Different consumers, retention, tamper-resistance and personal-data exposure. Merging fails both evidence and observability | Six retention policies; one correlation id |
| `SC-010-D-02` | Immutability | Insert-only · +chain · **+external anchor** | **All three** | A chain proves consistency, not originality. Anchoring is what makes it a commitment, and it is cheap | Hourly anchoring; `Q-02` target |
| `SC-010-D-03` | **Residency of the trail** | Single regional trail · **Split `Z3`/`Z4`** | **Split** | An `L1` entry holding `old_value` of an NID in `Z3` is a regional copy of a resident value — defeating `SC-007` through the one mechanism designed to be complete | **Changes `M29` §10.1.** `SCA-11`; `Q-01` |
| `SC-010-D-04` | Erasure vs audit | Erase the trail · Retain everything · **Retain the fact, erase the value where no basis requires it** | **Middle** | `NFR-095` needs the record; the subject's right needs the value gone where nothing requires it | `ER-3` crypto-erase of historical values; `ER-4` accepted privacy harm, disclosed |
| `SC-010-D-05` | Denial logging | Successes only · **Successes and denials** | **Both** | Enumeration is visible only as denials. Highest-value low-cost detection in the estate | Volume increase; `PF-1` partitioning absorbs it |
| `SC-010-D-06` | Audit write failure | Warn and proceed · Queue · **Fail the transaction** | **Fail** | `DI-02` 100% financial coverage; an unaudited financial transaction is worse than a refused one | Availability dependency; `PE-006` sizing |

---

## 15. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | Log classes are distinguished with purpose, store, retention and personal-data position | §3 — 6 classes |
| `AC-02` | Mandatory fields are specified per class | §4.1–§4.4 |
| `AC-03` | Attribution rules name what defeats them | §4.5 — 6 rules |
| `AC-04` | Immutability uses three mechanisms with stated limits | §5 |
| `AC-05` | Redaction is at emission and library-level | §6.1 |
| `AC-06` | **The residency consequence for the trail is stated** | §6.3; `SCA-11` |
| `AC-07` | The erasure-vs-retention tension is resolved and disclosed | §7.3 |
| `AC-08` | Time is treated as a control, including offline clients | §8 |
| `AC-09` | Forensic readiness is specified before it is needed | §9 |
| `AC-10` | The evidential chain closes `LG-019` `O-07` | §10.3 `ES-4` |
| `AC-11` | Volume and latency are sized inputs, not assumptions | §11 |
| `AC-12` | Achievable and unachievable detections are distinguished | §12 — 8 of 10 |

---

## 16. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `SC-001` | `SEC-C-038`…`-044`; `SEC-DC-4` |
| Upstream | `SC-004` | Attribution, elevation records, `PA-7` |
| Upstream | `SC-006` | SHA-256; `RS-1`…`RS-6` re-sealing |
| Upstream | `SC-007` | **§6.3 trail residency** |
| Downstream | `SC-009` | Chain-break and denial-spike detections |
| Downstream | `SC-011` | §9 forensic readiness; §12 detections |
| Downstream | `M29` | **`fix.audit.entry` redesign — `SCA-11`** |
| Downstream | `M06` | §10.2 chain beneath the certificate |
| Downstream | `M23`, `M24` | ISO 9001 evidence; legal hold |
| Downstream | `M60` | Reads logs as control-test evidence |
| Downstream | `PE-005`, `PE-006` | `L5` boundary; audit-write sizing |
| Lateral | `../../project_content/10_Legal_Policy_and_Compliance/LG-019_*.md` | `O-07` closed |
| Lateral | `../../project_content/10_Legal_Policy_and_Compliance/LG-009_*.md` | Retention classes |

---

## 17. References

**Within this repository**
`../PGD-000_*.md` · `./_CATEGORY_OVERVIEW.md` · `./SC-001`, `./SC-004`, `./SC-006`, `./SC-007`, `./SC-009`, `./SC-011` ·
`../02_Architecture_and_Design/AR-001_*.md` §9.2, `AR-010_*.md`

**Workspace**
`../../1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M29_*.md` §5.5, §6, §10.1 ·
`../../1000fix_ERP_Module/03_Modules/A_Service_Delivery_and_Operations/M06_*.md` ·
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04_*.md` §4, `05-06_*.md` §4, §6.3, §7 ·
`../../project_content/10_Legal_Policy_and_Compliance/LG-009_*.md`, `LG-019_*.md`

**External standards** *(all verified 2026-08-18; registered in `SC-008` §4.2)*

| Source | Version | Used for |
|---|---|---|
| ISO/IEC 27001 | :2022 + Amd 1:2024 — A.8.15, A.8.16, A.8.17 | Obligation |
| ISO/IEC 27037 | Current | §9 evidence handling |
| ISO/IEC 27041, 27042, 27043 | Current | Investigation assurance |
| NIST SP 800-92 | Current | Log management |
| ISO 9001 | :2015 §7.5.3, §10.2 | Evidence |
| PDPA 2026 | `NFR-095` — records ≥ 5 years | Retention floor |

---

## 18. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. Six log classes, three-layer immutability with external anchoring, redaction at emission, forensic readiness to ISO/IEC 27037, and the evidential chain beneath `M06` certificates and `LG-019` signatures — **closing `LG-019` `O-07` jointly with `SC-006`**. Raises **`SCA-11`: the audit trail must split across `Z3`/`Z4` or it defeats `SC-007`** | *Pending — no constituted body (`PGD-A2-25`)* |

---

*`SC-010` · Category 05 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
