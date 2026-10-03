---
id: SC-007
title: Data Residency and Cross-Border Transfer Design
category: 05 — Security, Privacy & Compliance
code: SC
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Chief Data Officer (unappointed — NFR-096) with the Chief Architect
approver: Design Authority (constituted under GV-002), countersigned by Legal Counsel
standards_basis: >
  Personal Data Protection Act 2026 (Law 63 of 2026), Bangladesh — NFR-086, NFR-086a/b/c, NFR-099 ·
  ISO/IEC 27701:2025 (PIMS) · ISO/IEC 27018 (PII in public cloud) · ISO/IEC 29151 (PII protection
  controls) · ISO/IEC/IEEE 42010:2022 (design description)
traces_to: >
  PGD-000 SC-007 · 05-06 §6.4 NFR-086…086c, §6.3 NFR-099 · AR-001 §8.3 · SC-001 §5, §8 ·
  SC-002 TH-047, TH-048, TH-055, TH-093 · SC-003 DPIA-01, -02, -09, A-12 · LG-012 · M29 FR-SEC-047…049 ·
  audit findings C-05, OP-01, OP-02, LG-012 O-01…O-07
depends_on: SC-001 (Z4 topology) · SC-006 (K-4 key separation) · DA-002 (field classification)
verified_on: 2026-08-18
priority: P0
needed_by: Now
enumeration_timestamp: 2026-08-18 14:25 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# SC-007 — Data Residency and Cross-Border Transfer Design

### Category 05 · Code `SC` · PDPA 2026 `NFR-086`/`NFR-099` · ISO/IEC 27701:2025 · ISO/IEC 27018

---

> **Before writing, read this.**
>
> 1. **`PG-01` Register-first.** This document's row exists in `PGD-000` Category 05 as `SC-007`.
> 2. **`PG-03` Count, do not consult.** Field and transfer counts taken from the source documents
>    at **2026-08-18 14:25 (+06)**.
> 3. **`PG-06` Cite standards.** §2.1.
> 4. **`PG-M4` Verify citations.** Statutory claims carry `verified_on: 2026-08-18` and the
>    **`P2` source class** established in `SC-003` §2.3.

---

## 1. Purpose

This document is the **engineering design of split residency**: which fields are Bangladesh-resident,
how a record is assembled across two stores, how the boundary is enforced at write time, how a
cross-border transfer is gated, what the transfer register contains, and — the part no document in
the estate has yet answered — **how residency-classified data is recovered when the resident store
fails**.

It closes, or contributes to closing, **two critical audit findings**:

> **`C-05` (Critical)** — *"Data residency architecture may be unlawful."* The Singapore-region
> topology inherited from v1.0 `ASM-13` stores NID, TIN, biometric templates, recovered customer
> data and seller KYC documents outside Bangladesh, and the PDPA 2026 restricts large-scale
> transfer of exactly those categories.

> **`OP-01` (Critical)** — *"The lawful disaster-recovery path for Bangladesh-resident personal data
> does not exist."* `OP-012` §4.3 has three recovery routes and **the only lawful one is
> unavailable**: no resident DR target exists, and restoring into the regional environment is a
> **regulatory act** under `NFR-086b`, not a recovery step.

`OP-01` is the sharper of the two, and it is worth stating in the terms the audit used:

> *"In an outage affecting the resident store, an engineer at 02:00 has a choice between a two-hour
> RTO and a cross-border transfer of exactly the data category the Act singles out… **That leaves no
> route that both restores service and complies, and the constraint is invisible until the night it
> binds.**"*

`LG-012` states the **position**; `AR-001` §8.3 states the **topology**; neither states the
**design**. This document does — and it does so knowing that the legal opinion (`DEP-31`, `D-13`)
has not been obtained, which is why §4 is built to make a change of opinion a **reclassification
rather than a redesign**.

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | The **residency classification model** — how a field is classified, by whom, and what the classification does |
| 2 | The **authoritative field list**, reconciled across `05-06` §6.4, `LG-012` §4.3 and `05-02` §10 |
| 3 | The **split-record design** — resident key, join semantics, what may and may not be duplicated |
| 4 | **The residency service `CD-233`** — its contract, its failure behaviour, and why it is the only path |
| 5 | **Write-time enforcement** — the mechanism that makes `NFR-086a` real |
| 6 | **The transfer gate** — `NFR-086b` pre-execution notification and safeguard check |
| 7 | The **transfer register** content and rules; the **sub-processor register** |
| 8 | **The quiet-copy prohibitions** — cache, index, log, replica, warehouse, backup |
| 9 | **Disaster recovery for `Z4`** — the `OP-01` design |
| 10 | **Non-production** and masking |
| 11 | **Reclassification procedure** — how the field list changes without a migration |
| 12 | **What is not yet evidenced**, republished until empty |

**Explicitly out of scope:**

| Topic | Owned by | Why |
|---|---|---|
| Whether a processing purpose is lawful or proportionate | `SC-003` | This document moves data lawfully; `SC-003` decides whether to process it at all |
| `Z4` network placement and zone rules | `SC-001` §5 | This document uses the zone; it does not design it |
| Key material and `K-4` location | `SC-006` §5.3 | Cross-referenced; `SC-006` specifies |
| Notice wording, transfer statement copy | `LG-012` | This document is the engineering counterpart |
| Retention periods | `LG-009` | Referenced, never restated |
| DR environment sizing and provisioning | `PE-002`, `PE-007` | This document sets the **constraint**; `PE` builds it |
| Physical data-centre selection | `PE-001` | `O-04` — the region is not named in any approved specification |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| **Chief Architect / Platform Squad** | §4, §5, §6 — the build specification for `CD-233` |
| **Developers** | §5.3 what fails and how; §7 the prohibitions |
| **CDO / Legal Counsel** | §3 statutory basis; §8 transfer register; §12 open questions |
| **Platform Engineering** | §9 DR constraints — **the `OP-01` design** |
| **National Data Management Authority** | §4, §6, §8 — written to answer *"show me one place where this is enforced"* |
| **Enterprise client / brand auditor** | §11 what is not yet evidenced |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | How this document conforms | Departure and rationale |
|---|---|---|
| **PDPA 2026** *(`P2` source class; verified 2026-08-18)* | §3 restates `NFR-099`'s restriction on large-scale transfer of Sensitive Personally Identifiable Data, the Authority-notification duty and the safeguard-disclosure duty | **Published analysis is consistent that the Act imposes no general data-localisation mandate** — it restricts *sensitive-category* transfer and requires notification. §3.2 states why this matters commercially |
| **ISO/IEC 27701:2025** *(standalone edition, 14 Oct 2025)* | Controller obligations for transfer, records and sub-processors | The 2025 edition is standalone; a future PIMS certification no longer requires ISO/IEC 27001 first |
| **ISO/IEC 27018** | PII protection in public cloud — the sub-processor and disclosure controls in §8.4 | — |
| **ISO/IEC 29151** | PII protection control set | Used as a checklist for §7 |
| **ISO/IEC/IEEE 42010:2022** | This is a **design description** subordinate to `AR-001` §8.3; the topology is inherited, not re-derived | Preventing the drift `PGD-A3-18` identifies as this repository's dominant defect class |

### 2.2 Source material

| Source | What it supplies |
|---|---|
| `05-06` §6.4 | **`NFR-086`, `086a`, `086b`, `086c`** and the **authoritative 7-field residency list** |
| `05-06` §6.3 | `NFR-099` — the statutory restriction |
| `AR-001` §8.3 | The split-residency topology, the resident-key rule, and `TR-02` risk absorption |
| `SC-001` §5.1, §5.3, §8 | `Z4`, the single-path rule, the quiet-copy prohibitions |
| `SC-006` §5.3 | `K-4` Bangladesh-resident key material |
| `LG-012` §4.1–§4.7 | The position, `RD-R1`…`RD-R10`, the field table, the transfer register content, the sub-processor register, and **§4.7's honest what-is-not-evidenced list** |
| `M29` §5.6 | `FR-SEC-047`, `-048`, `-049`; `T-04`, `T-05` |
| `M06` `BRU-DTS-16` | Recovered customer data **may not be replicated to a foreign region** |
| `M12` `BRU-MKP-19` | Seller KYC residency |
| `AUDIT-017` `OP-01`, `OP-02` | The DR findings this document designs against |
| `OP-012` §4.3, `RD-01` | The three recovery routes and the prohibition |

### 2.3 Audit findings

| Finding | Source | Disposition |
|---|---|---|
| **`C-05` (Critical)** | `00-06` | **Closed at the design level.** §4 and §5 make residency a field property enforced at write time through a single service. **The legal opinion remains outstanding** (`Q-01`) — the design is built to survive either answer |
| **`OP-01` (Critical)** | `AUDIT-017` | **Design supplied, provisioning outstanding.** §9 fixes the constraint (`Z4` recovers only to a resident target) and specifies the three options. **Until one is provisioned, `NFR-007` does not apply to residency-classified data and §9.5 says so** |
| `OP-02` (High) | `AUDIT-017` | Contributes. §9.4 states `Z4`'s DR requirements so `PE-002` cannot size the `dr` environment without them |
| `LG-012` `O-01`…`O-07` | `LG-012` §4.7 | §11 carries all seven forward, updated, with owners |
| `SC-002` `TH-047`, `TH-048`, `TH-055`, `TH-093` | `SC-002` | Treated in §5.3, §7, §9, §4.4 |
| `SC-003` `A-12` | `SC-003` | **Accepted.** §4.3 recommends bank details and individual payroll for reclassification |

### 2.4 Enumeration

| # | Figure | **Counted 2026-08-18 14:25 (+06)** | Note |
|---|---|---:|---|
| 1 | Residency-classified field classes — **authoritative** | **7** (`05-06` §6.4) | The governing list |
| 2 | Proposed additions | **2** (`LG-012` §4.3 `RD1`) | Bank details; individual payroll |
| 3 | `S3` sensitivity classes | **9** (`05-02` §10) | Different list, different purpose — §4.3 reconciles |
| 4 | Anticipated cross-border transfers | **8** (`LG-012` §4.5 `TR-01`…`TR-08`) | **0 registered** |
| 5 | Sub-processors registered | **0** | The register does not exist (`O-05`) |
| 6 | External integration destinations | **47** (`05-03` §2) | Every one is a candidate transfer |
| 7 | Regional store's country named in an approved specification | **0** | `O-04` — **still unnamed** |
| 8 | Lawful DR routes for `Z4` today | **0 of 3** | `OP-01`. §9 |
| 9 | `LG-012` §4.7 rows still unevidenced | **9 of 9** | §11 |

---

## 3. Statutory Basis

### 3.1 The obligation

| # | Obligation | Realised by |
|---|---|---|
| `RB-1` | **Restrict large-scale transfer of Sensitive Personally Identifiable Data** — government unique identifiers (NID, passport, TIN), biometric identifiers, genetic information, criminal records | §4 classification; §6 gate |
| `RB-2` | **Notify the Authority** of cross-border transfers of such data | §6.3, §8.2 |
| `RB-3` | **Disclose the safeguards applied** | §8.3; `LG-012` publication |
| `RB-4` | A processor's processing is the controller's own; **equivalent obligations flow to every processor and sub-processor** (`NFR-098`) | §8.4 |
| `RB-5` | Maintain processing records ≥ 5 years (`NFR-095`) | `M60` `FR-GRC-033` |

### 3.2 What the statute does **not** require — and why it matters commercially

> **`SC-007-F-01`. Published analysis of the PDPA 2026 is consistent that there is no general
> data-localisation mandate.** The Act restricts **transfer of sensitive categories** and requires
> notification and safeguard disclosure; the February 2026 Amendment Ordinance (No. 23 of 2026)
> addressed residency for **critical information infrastructure and limited personal data**, which
> `M29` §4 notes *materially reduces the scope of `NFR-086`*.

This distinction is not academic. It determines the size of `Z4` and therefore the cost:

| If the obligation were… | Then… |
|---|---|
| **General localisation of all personal data** | The regional store is unlawful for the whole estate. `Z4` becomes the primary store. `TD-01`…`TD-08` and the entire `02-05` sizing collapse |
| **Restriction on sensitive-category transfer** *(the position taken)* | The regional store is lawful for the great majority. **`Z4` is a targeted control over 7–9 field classes**, not a repatriation |

**Source class `P2`.** This is `Q-01` — the `DEP-31`/`D-13` legal opinion — and it is the single
highest-value legal question in the programme. **`SC-007-D-01` states how the design survives either
answer.**

### 3.3 The second regulator

The **Cyber Security Ordinance 2025** creates the National Cyber Security Agency and regulates
**critical information infrastructure**. A CII designation would bring separate obligations —
including, per published analysis, **operating its own CERT/CIRT and SOC with quarterly reports to
the NCSA** — and the February 2026 PDPA amendment's residency provisions attach partly to CII
status. **Whether 1000FiX is CII is `SC-001` `Q-04`** and it is a residency question as much as a
security one.

---

## 4. The Residency Classification Model

### 4.1 The principle

> **`RD-P1`. Residency is a property of a field, carried in the data model, enforced by the platform
> at write time — not by convention, not by documentation, not by developer discipline**
> (`NFR-086a`, `LG-012` `RD-R1`).

This is `SC-001` `SEC-DC-1` and it is the decision the whole design rests on, for a reason that is
about risk absorption rather than elegance:

> **`SC-007-D-01`. The mechanism is built in Wave 1 regardless of what the legal opinion says.**
> Because classification is **data**, a change of legal opinion is a **reclassification — a data
> change** — not a redesign. If the opinion narrows the list, fields move out. If it widens the
> list, fields move in. **Neither requires touching the architecture.** `AR-001` §8.3 records this
> as `TR-02`; it is repeated here because it is the reason this document can be written before the
> opinion arrives.

### 4.2 The classification attributes

Every field in the model carries:

| Attribute | Values | Set by | Changed by |
|---|---|---|---|
| `residency_class` | `RESIDENT` · `REGIONAL` · `UNCLASSIFIED` | Design-time, at field creation | **Reclassification procedure only** (§10) |
| `sensitivity_class` | `S0` · `S1` · `S2` · `S3` | Design-time | Change request |
| `lawful_basis_ref` | `LG-008` purpose reference | Design-time | `SC-003` `PI-02` |
| `retention_class` | `LG-009` `RC-nn` | Design-time | `LG-009` revision |
| `owning_module` | `M01`…`M67` | Design-time | Architecture change |

| # | Rule |
|---|---|
| `RC-1` | **`UNCLASSIFIED` is not a permitted state at merge.** `SC-005` `G-03` blocks a commit adding a field with no classification |
| `RC-2` | A field's classification is **visible in the data dictionary** (`DA-002`) and is the same fact the platform enforces — one source, not two |
| `RC-3` | **The classification is what tells a person which rule applies** (`LG-021` §4.2.6), and what tells the platform which store to write to |

### 4.3 The field list — reconciled

Three lists exist. Conflating them is a live error risk, and `SC-001` §8.4 already flagged it.

**Authoritative — `RESIDENT` (`05-06` §6.4, 7 classes):**

| # | Field | Entity | Module | Also `S3`? | Note |
|---|---|---|---|:--:|---|
| 1 | **National ID number** | `fix.identity.document` | `M33` | Yes | Finance and compliance roles only |
| 2 | **Passport number** | `fix.identity.document` | `M33` | *(not in the 9-field `S3` list)* | §4.5 |
| 3 | **TIN** | `fix.party`, `hr.employee` | `M33`, `M21` | *(not in `S3` list)* | **Appears on statutory outputs and is disclosed to the NBR through filings** — §6.5 |
| 4 | **Biometric attendance template** | `fix.attendance.record` | `M55` | Yes | Irreversible; **never exported**; `SC-006` §7.3 |
| 5 | **Recovered customer data and its index** | `fix.recovered.inventory` | `M06` | Yes | **`BRU-DTS-16`: may not be replicated to a foreign region.** Per-case keys, dual control |
| 6 | **Marketplace seller KYC documents** | `fix.mp.seller.document` | `M12` | Yes | `BRU-MKP-19`; allow-list, step-up, logged |
| 7 | **Criminal-record checks, where collected** | `fix.mp.seller.document` | `M12` | *(not in `S3` list)* | **`SC-003` `A-11`: outcome-retained, record-discarded** unless Legal establishes a retention basis (`PN8`) |

**Proposed additions — `LG-012` `RD1`, and this document's position:**

| # | Field | Entity | `LG-012` status | **`SC-007` position** |
|---|---|---|---|---|
| 8 | **Bank account details** | `fix.party`, `hr.employee` | Proposed; `05-06` §6.4 does not list it | **Support the addition.** `SC-003` `A-12` |
| 9 | **Individual payroll and payslip** | `hr.payslip`, `fix.salary.structure` | Proposed | **Support the addition.** `SC-003` `A-12` |

> **`SC-007-F-02`. `LG-012` correctly declines to extend `05-06` §6.4 unilaterally, and correctly
> raises `RD1` instead** — `CG-013` `T-B04` makes contradicting an approved specification an
> escalation. **This document is the right place to make the recommendation**, and the
> recommendation is: **add them.**
>
> The reasoning is architectural, not merely precautionary. A Bangladeshi individual's bank account
> and payslip are precisely the categories a regulator would expect in `Z4`. **Adding them after
> go-live means moving live `S3` data across a residency boundary — which `NFR-086b` makes a
> notifiable act.** `SC-001-D-08` therefore provisions `Z4` with capacity and key separation for
> **all nine**, so that a positive answer to `RD1` is a **reclassification, not a migration**.
> Owner: CDO with Enterprise Architecture. `Q-02`.

**`S3` but explicitly `REGIONAL`** — named so they are not assumed to be in `Z4`:

| Field | Why regional |
|---|---|
| Call recordings | Not a sensitive-category identifier under `NFR-099`. Protected by `T5`, field permissions and access logging |
| API and integration credentials | Vault-native; not personal data |

### 4.4 The resident key

| # | Rule | Source |
|---|---|---|
| `RK-1` | Regional and resident records are joined by an **opaque resident key** | `M29` `T-05` |
| `RK-2` | The key **carries no personal information** and **cannot be reversed** to a natural identifier | `M29` `T-05`, `AR-001` §8.3 |
| `RK-3` | The key is **not derived from** a natural identifier — not a hash of NID, not a hash of anything the subject supplies | **`SC-002` `TH-093` identifiability** |
| `RK-4` | The key is **not correlatable across data subjects or across purposes** — it is a random identifier, allocated once | `TH-093` |
| `RK-5` | **`QA-007` tests the property, not the sentence**: given a corpus of resident keys and the full regional dataset, no re-identification is achievable | `SC-002` §10 |

> **`RK-3` and `RK-5` matter more than they appear.** A resident key derived from a natural
> identifier would be an identifier — it would carry the very linkability `Z4` exists to prevent,
> and it would do so **in the regional store, in plain sight**. This is a design error that is easy
> to make for good reasons (deterministic derivation makes joins simpler) and impossible to reverse
> once data exists.

### 4.5 The `S3`/residency divergence, explained

| Relationship | Members | Why |
|---|---|---|
| Both `S3` **and** `RESIDENT` | NID, customer identity documents, biometric templates, recovered data index, seller KYC | The overlap the design optimises for — `T5` ≈ `Z4` (`SC-001` `SEC-IS-1`) |
| `RESIDENT`, **not** in the 9-field `S3` list | Passport, TIN, criminal-record checks | **`05-02` §10's `S3` list is older than `05-06` §6.4's residency list.** These three should be `S3` as well |
| `S3`, **regional** | Call recordings, API credentials | Sensitive, but not a `NFR-099` category |

> **`SC-007-F-03`. Passport number, TIN and criminal-record checks are residency-classified but do
> not appear in `05-02` §10's `S3` inventory.** That is an inconsistency between two approved
> specifications, and it has a build consequence: `SC-006` §7.1 encrypts by `S3` class, so a field
> that is `RESIDENT` but not `S3` would land in `Z4` **without field-level encryption**. **Position:
> every `RESIDENT` field is `S3` by construction.** Raised to `05-02` and `DA-002` as finding
> `SCA-09`.

---

## 5. The Split-Record Design

### 5.1 The shape

```
   REGIONAL STORE (Z3)                        BANGLADESH-RESIDENT STORE (Z4)
   ┌────────────────────────────┐             ┌──────────────────────────────┐
   │ fix.party                  │             │ fix.party.resident           │
   │  id                        │             │  resident_key  ◄── opaque,   │
   │  name                      │             │                   random,    │
   │  phone, address, email     │             │                   one-way    │
   │  segment, credit_limit     │             │  nid_number      (K-4)       │
   │  ★ resident_key ───────────┼─────────────┤  passport_number (K-4)       │
   │                            │   join      │  tin             (K-4)       │
   │ NO nid, NO passport,       │   only      │  bank_account    (K-4, RD1)  │
   │ NO tin, NO biometric       │             │                              │
   └────────────────────────────┘             └──────────────────────────────┘
              ▲                                            ▲
              │                                            │
        any Z2 workload                       ★ ONLY the residency service
                                                   CD-233 (SEC-ZR-2)
```

| # | Rule | Source |
|---|---|---|
| `SR-1` | **The resident store is authoritative for its fields.** No regional cache, replica or index holds them | `LG-012` §4.4.1 |
| `SR-2` | **A restricted field is never duplicated across the boundary to make a join convenient** | `RD-R3`, `NFR-086` |
| `SR-3` | The regional record holds the **resident key only** | `RK-1` |
| `SR-4` | **A record is assembled at read time**, never materialised across the boundary | `SR-1` |
| `SR-5` | **Absence of the resident store degrades the record, it does not fail it** — the estate operates without the sensitive fields (`OP-012` §4.3 route 1) | §9.2 |

### 5.2 The residency service `CD-233`

| Attribute | Specification |
|---|---|
| **Position** | `Z2`, one of the 16 domain services (`AR-001` §6.1). **The only component permitted to open a connection to `Z4`** |
| **Contract** | Read, write, transfer-request, reclassify. **No bulk-read endpoint** |
| **Authentication** | Service mTLS **plus** the propagated end-user context **plus** a declared purpose |
| **Authorisation** | Re-evaluates `T5` allow-list membership and step-up claim. **Does not trust the caller's assertion** |
| **Logging** | **Per-read access log written before the value is returned** (`SC-002` `TH-043`; `SC-010`) |
| **Failure** | **Fails closed.** Residency reads and writes fail; the rest of the estate continues (`SC-001` §12) |
| **Availability** | Availability-critical for `S3` paths; **not** for the estate. Sized in `PE-006` |
| **Audit position** | *"The residency rule is implemented in exactly one place and can therefore be audited in exactly one place — which is what a regulator will ask for"* (`SC-001` `SEC-ZR-2`) |

**Prohibited on `CD-233`:**

| # | Prohibition |
|---|---|
| `CD-1` | **No bulk read.** A bulk export of `Z4` content is a separate, approved, rate-limited, logged operation under `SEC-C-042` — not an API affordance |
| `CD-2` | **No caching of returned values** anywhere outside the calling transaction |
| `CD-3` | **No write path that accepts a regional target.** The service cannot be asked to write a resident field regionally |
| `CD-4` | **No debug or diagnostic endpoint that returns plaintext** |
| `CD-5` | **No direct database access for humans**, including platform engineers (`SC-001` §5.5) |

### 5.3 Write-time enforcement — making `NFR-086a` real

> **`NFR-086a`: the platform enforces residency at write time. `M29` `T-04`: a write that would
> place such a field in the regional store *fails — it does not warn*.**

**Three enforcement layers, because one is not enough:**

| Layer | Mechanism | Catches |
|---|---|---|
| **Build time** | `SC-005` `G-03` — a new field without a classification blocks the commit | The developer who did not think about it |
| **ORM / write path** | The ORM routes by `residency_class`. A `RESIDENT` field on a regional model **raises and aborts the transaction** | `AB-21` — the ordinary developer adding an NID field to a regional model because the ORM allowed it |
| **Database** | The regional schema **has no column** for a `RESIDENT` field. There is nothing to write to | Migrations, data-fix scripts, direct SQL, and anything that bypasses the ORM (`SC-002` `TH-036`) |

> **`SC-007-F-04`. The third layer is the one that actually holds, and it is the one most likely to
> be omitted.** An ORM-level check protects application code. `TH-036` is a **migration script**,
> which does not go through the ORM. **The regional schema must not contain a column that a
> resident field could land in** — then the strongest enforcement is structural rather than
> procedural, and `AB-21` fails with a database error rather than succeeding quietly.

**Test obligation** (`SC-005` `AT-5`): the test **attempts the prohibited write and asserts the
transaction aborts**. A warning is a failure of the test, not a pass.

---

## 6. The Transfer Gate

### 6.1 What counts as a transfer

Broader than most readers assume, and `LG-012` is right about all of these:

| # | Is a transfer | Source |
|---|---|---|
| `TF-1` | Sending data to a recipient outside Bangladesh | obvious |
| `TF-2` | **A remote view.** A support engineer abroad seeing a screen containing personal data **has received it** | `RD-R9`, `RD10` |
| `TF-3` | **A backup or replica placed outside Bangladesh** | `RD9` |
| `TF-4` | **A restore into the regional environment** | `NFR-086b`; **`OP-01`** |
| `TF-5` | A cache, index or log entry landing regionally | `SEC-DC-2`…`-4` |
| `TF-6` | Making data available to a processor whose processing occurs abroad | `RD-R8` |
| `TF-7` | Model inference where the model service is abroad | `TR-06` |

### 6.2 The gate

> **`NFR-086b` / `BRU-SEC-14`: no cross-border transfer of a residency-classified field executes
> until an Authority notification record and a documented safeguard already exist. The gate precedes
> the transfer** (`RD-R4`).

```
   Transfer requested (any TF-1…TF-7)
        │
        ├─► Is any field RESIDENT-classified? ──── no ──► Register (§8) and proceed
        │                                                  under the applicable purpose
        yes
        │
        ├─► Does a transfer-register row exist?  ── no ──► ✖ BLOCK
        │
        ├─► Does an Authority notification       ── no ──► ✖ BLOCK
        │   record exist for it?
        │
        ├─► Is a documented safeguard recorded?  ── no ──► ✖ BLOCK
        │
        ├─► Is the row status Active (not         ── no ──► ✖ BLOCK
        │   suspended by the Authority)?
        │
        └─► ✔ EXECUTE — and log the transfer with its row reference
```

| # | Rule |
|---|---|
| `TG-1` | **The gate is synchronous and fails closed.** There is no queue-and-retry path — a blocked transfer is a decision, not an outage |
| `TG-2` | **`RD-R10`: where a restricted field is requested by a counterparty, the answer is no**, and the evidential need is met another way |
| `TG-3` | **`4.5.2`: a restricted field never appears in a transfer row.** If a transfer would need one, the transfer is redesigned |
| `TG-4` | **A suspended transfer stops.** The Authority may order suspension, and **the platform must be able to stop one transfer without stopping the service that depends on it** — `LG-012` §4.5.5 raises this as a design requirement, and §6.4 answers it |
| `TG-5` | `SC-005` `G-13` enforces the register at **build time** as well: a new outbound destination with no allow-list entry and no transfer row **fails the build** |

### 6.3 Authority notification

| # | Requirement |
|---|---|
| `AN-1` | A notification record carries: transfer id, categories, purpose, destination, recipient, safeguards, volume class, submission date, reference, response |
| `AN-2` | **The record must exist before execution.** A notification submitted concurrently with the transfer does not satisfy `NFR-086b` |
| `AN-3` | **`RD4` is unresolved: when is a transfer "large-scale"?** Until answered, **treat every transfer of a `NFR-099` category as notifiable** — the conservative reading, stated as such |
| `AN-4` | Notification is re-made on any change of recipient, purpose, volume or destination |
| `AN-5` | **The notification and its response are retained for the life of the transfer plus 5 years** (`NFR-095`) |

### 6.4 Suspension — answering `LG-012` §4.5.5

> `LG-012` raises it as an unanswered design requirement: *"the platform must be able to stop a
> transfer without stopping the service that depends on it."*

**Design position:**

| # | Mechanism |
|---|---|
| `SU-1` | **Transfer status is a runtime property of the register row**, evaluated by the gate on every execution — not a deployment-time configuration |
| `SU-2` | Suspending a row causes the gate to block **that transfer class only** |
| `SU-3` | **The dependent service must have a declared degraded mode** for each transfer it relies on. `05-03` §7's fallback register is where that lives, and it is extended to cover transfer suspension |
| `SU-4` | **A transfer with no declared degraded mode may not be registered.** This forces the question at registration time rather than at suspension time |
| `SU-5` | Suspension is **logged, alerted and reported** to the CDO and the Steering Committee |

> **`SU-4` is the load-bearing rule.** It converts an unanswerable operational question — *what do
> we do if the Authority suspends `TR-02`?* — into a **registration prerequisite**. Owner: CDO with
> the owning module.

### 6.5 The TIN exception, stated

**TIN is `RESIDENT`, and it appears on statutory outputs disclosed to the NBR through filings**
(`LG-012` §4.3, `LG-008` `P-03`, `P-16`).

| # | Position |
|---|---|
| `TX-1` | **A statutory disclosure to a Bangladeshi authority is not a cross-border transfer.** It is domestic and it is a legal obligation |
| `TX-2` | The TIN may therefore be **rendered onto a Mushak 6.3 invoice and into an NBR filing** without the §6.2 gate |
| `TX-3` | **The rendered document is then subject to the same residency rules as any other artefact containing a resident field** — a tax invoice PDF containing a TIN is `RESIDENT` and is stored accordingly |
| `TX-4` | An invoice delivered to an **overseas** counterparty containing a TIN **is** a transfer and is gated |

> **`SC-007-F-05`. `TX-3` is a consequence nobody in the estate has stated, and it has a real
> operational effect.** `M24` document storage, `M20` invoicing and `DT-` templates all produce
> artefacts that may embed a resident field. **A generated document inherits the residency
> classification of the most restricted field it contains.** Raised to `M24`, `M20` and `SC-010` as
> finding `SCA-10`.

---

## 7. The Quiet-Copy Prohibitions

`LG-012` §4.4 identified three; this document adds three more and makes each a testable rule. These
are the ways a residency control is defeated **without anyone deciding to defeat it** — and
`SC-002` §12.1's attack tree finds path `B` (around the application) is the cheapest route to bulk
`Z4` data precisely because of them.

| # | Prohibition | Test |
|---|---|---|
| `QC-1` | **A cache is a copy.** No Redis, no application cache, no memoisation holds a resident value beyond the transaction | Inspect cache contents for resident-field patterns after a `Z4` read |
| `QC-2` | **A search index is a copy.** No regional GIN, no ClickHouse column, no external search service over a resident field | Schema assertion in `SC-005` `G-07` |
| `QC-3` | **A log is a copy.** Redaction **at emission**, configured from the classification | Emit a resident value through the logging path; assert it is absent from `DS-11` |
| `QC-4` | **A read replica is a copy.** The two `Z3` replicas replicate the regional store only | Replication topology assertion |
| `QC-5` | **An analytics extract is a copy.** `Z4` values never enter the warehouse; aggregates are computed `Z4`-side and only the aggregate crosses | `SC-002` `TH-056`; `DA-00x` propagation rules |
| `QC-6` | **A backup is a copy.** A backup of the resident store **stays in Bangladesh** | `RD9`; §9 |
| `QC-7` | **A generated document is a copy.** An artefact embedding a resident field inherits its classification | `SCA-10`, §6.5 |
| `QC-8` | **A screen is a copy.** A remote session displaying a resident field to a viewer outside Bangladesh is a transfer | `TF-2`; `Z7` origin restriction |

---

## 8. The Registers

### 8.1 Why two registers

`NFR-098` makes a processor's processing the controller's own. Two registers are therefore needed:
**what leaves** (transfers) and **who else touches it** (sub-processors). **Neither exists today.**

### 8.2 The transfer register

Content per `LG-012` §4.5, adopted without change; the engineering additions are marked ⊕.

| Field | Note |
|---|---|
| `transfer_id` | Immutable |
| `data_categories` | **Never a restricted field** (`RD-R10`) |
| `purpose` | `LG-008` §4.2 reference |
| `destination_country` · `recipient` · `recipient_role` | Named entity, not a category |
| `basis` · `safeguard` | §8.3 |
| `authority_notification_ref` | **The gate blocks until it exists** |
| `volume_class` | `RD4` — unresolved; `AN-3` conservative reading applies |
| `registered_on` · `reviewed_on` · `status` | Active / suspended / ended |
| ⊕ `egress_allow_list_ref` | The `Z6` entry this row authorises (`SC-005` `G-13`) |
| ⊕ `degraded_mode_ref` | **`SU-4`: the declared behaviour if this transfer is suspended** |
| ⊕ `owning_module` · ⊕ `technical_owner` | Who fixes it when the gate blocks |

**The eight anticipated transfers, and their state at 14:25 (+06):**

| # | Transfer | Registered? | `SU-4` degraded mode declared? |
|---|---|---|---|
| `TR-01` | Non-restricted fields to the regional store | **No.** Region unnamed (`O-04`) | No |
| `TR-02` | Warranty claim data to overseas brand partners | **No.** `LG-005` §6.4 gates brand onboarding on it | No |
| `TR-03` | Notification delivery — SMS/WhatsApp/email/push | **No** | No — **and `05-03` §7 has a fallback register that should carry it** |
| `TR-04` | Payment tokens to gateways | **No** | No |
| `TR-05` | Third-party tags — analytics, chat, video, advertising | **No** (`O-07`) | No — **`SC-002` `TH-059`** |
| `TR-06` | AI model inference | **No** | No |
| `TR-07` | Remote support by an overseas engineer | **No** (`RD10`, `RD-R9`) | No |
| `TR-08` | Cloud management-plane metadata | **No** | No |

> **`SC-007-F-06`. Zero of eight registered, and `SC-005` `G-13` will fail the build for every one
> of them.** That is **correct behaviour**, and it is the point: a governance gap that was
> previously invisible becomes a **visible, dated, owned build blocker** rather than a runtime
> compliance failure discovered by a regulator. **`TR-03` blocks every portal that sends a
> notification, which is all of them.** Owner: CDO with Legal. **W1 blocker.**

### 8.3 Safeguards

`LG-012` §4.5.3, subject to `RD5`:

| # | Safeguard |
|---|---|
| 1 | Contractual data-protection terms flowing **equivalent obligations** (`NFR-098`) |
| 2 | **Encryption in transit and at rest with keys held in Bangladesh** (`SC-006` `K-4`) |
| 3 | Purpose and volume limitation |
| 4 | Access logging (`EA-10`) |
| 5 | A right to audit |
| 6 | Deletion or return on termination |
| 7 | **Onward-transfer restriction** |

### 8.4 The sub-processor register

Content per `LG-012` §4.6. **It does not exist** (`O-05`).

| # | Rule |
|---|---|
| `SP-1` | **The register is published as part of the residency statement.** One that exists internally and is not disclosed does not discharge a disclosure obligation |
| `SP-2` | Adding a sub-processor is a **MAJOR change** and is notified |
| `SP-3` | **A sub-processor that will not accept equivalent obligations is not engaged** |
| `SP-4` | Every third-party row in `LG-011` §4.3 has an entry here |
| `SP-5` | **A processor cannot use a further sub-processor without disclosure** |
| ⊕ `SP-6` | **Each of the 47 egress destinations is assessed for sub-processor status at allow-list registration** — the two registers are populated by the same act, not separately |

---

## 9. Disaster Recovery for `Z4` — the `OP-01` Design

### 9.1 The problem, precisely

`OP-012` §4.3 has three routes. **All three are currently unavailable or unlawful.**

| Route | State | Assessment |
|---|---|---|
| **1. Operate without the sensitive fields until the store returns** | ✔ Available | **Degraded, and only for an *unreachable* store — not a *lost* one.** It is not a recovery; it is a survival mode |
| **2. Restore from a resident backup to a resident target** | ✖ **No resident DR target exists** | **The only lawful full recovery.** Requires provisioning |
| **3. Restore into the regional environment** | ✖ **A regulatory act** under `NFR-086b` | `OP-012` `RD-01` forbids it, correctly. It is `TF-4` and it needs prior notification and a documented safeguard |

### 9.2 Route 1, designed properly

Route 1 is currently the *de facto* answer and it has never been designed. It is designed here,
because a survival mode nobody specified is a survival mode that fails.

| # | Requirement |
|---|---|
| `DG-1` | **`CD-233` unavailability degrades, it does not fail the estate.** Service orders, dispatch, invoicing, inventory and payroll *calculation* continue |
| `DG-2` | **Operations requiring a resident field fail explicitly with a stated reason** — device release requiring NID verification, KYC onboarding, biometric attendance, `M06` case access |
| `DG-3` | **Biometric attendance falls back to a non-biometric path** — which `SC-003` `A-05`(c) requires to exist anyway. **The DR case and the privacy case require the same alternative** |
| `DG-4` | **No operation silently proceeds without the field it needed.** A NID verification that cannot happen is a refusal, not a skip |
| `DG-5` | **Queued writes to `Z4` are held durably and replayed**, never dropped and never diverted regionally |
| `DG-6` | Degraded mode has a **declared maximum duration** after which the business decision escalates to the CTO and CDO |

### 9.3 The constraint

> **`SC-007-DR-1`. `Z4` fails over only to a Bangladesh-resident standby.** A regional DR target
> for `Z4` data is not an option — `NFR-086b` makes it a notifiable regulatory act, not a recovery
> step. This is `AR-001` `DR-02` and `SC-001` `SEC-DR-02`, restated here as the **design
> constraint** rather than an operational preference, so that no runbook can quietly adopt route 3.

### 9.4 Three options, costed by consequence

The programme must choose one. **`SC-007` cannot choose; it can only make the choice explicit.**

| Option | What it requires | Consequence | Assessment |
|---|---|---|---|
| **A. Provision a Bangladesh-resident DR target** | A second in-country environment sized for `Z4` — small by volume, **availability-critical**; in-country key escrow (`SC-006` `ES-3`); replication within the border | Infrastructure cost `PE-002` does not currently carry. `Z4` is *"regulatory, not volume"*-sized (`AR-001` §8.6), so the cost is **far below** a full DR environment | **Recommended.** It is the only option that makes `NFR-007` true for all data |
| **B. Obtain the Authority's position in advance, in writing, with a pre-documented safeguard** | Legal engagement with the NDMA; a standing notification covering emergency restoration; a pre-agreed safeguard | No infrastructure cost. **Depends on a regulator's advance answer**, and the Authority's SOPs are not yet published (`SC-003` `RV-05`) | **Necessary regardless of A**, because it also covers the case where the resident DR target itself fails |
| **C. Accept that `NFR-007` does not apply to residency-classified data** | A recorded, board-level risk acceptance; `OP-012` and `NFR-007` amended to say so; degraded mode (§9.2) becomes the *only* answer | Zero cost, honest. **`M06` and biometric attendance become unavailable for the duration of any `Z4` outage** | **The default if neither A nor B is done — and the programme is currently on this path without having chosen it** |

> **`SC-007-F-07`. Option C is the current position by default, not by decision.** `OP-01` says the
> constraint is *"invisible until the night it binds"*. **A risk taken by omission is the one nobody
> owns.** This document's recommendation is **A + B**: provision the resident target, and obtain the
> written position for the residual case. `Q-03`; escalated to `GV-005` as `RSK-SC-01` and to the
> Board through `GV-008`.

### 9.5 The honest statement

> **Until option A or B is in place, `NFR-007` (RPO ≤ 15 min, RTO ≤ 2 h) does not apply to
> residency-classified data, and the programme must say so** rather than imply otherwise —
> `AUDIT-017` `OP-01`'s own words. **Availability reporting must state the `Z4` RTO separately**,
> and `OP-012` §3 `HC-01`'s monthly DR RAG report to the Steering Committee must carry it as a
> distinct line. Otherwise a green estate-level RTO conceals an unbounded one.

---

## 10. Reclassification

The procedure that makes `SC-007-D-01` real: a change of legal opinion must be a data change.

| # | Step |
|---|---|
| `RL-1` | A reclassification is a **change request** with a legal basis, an owner and an assessed impact |
| `RL-2` | **`REGIONAL` → `RESIDENT`**: the field is migrated to `Z4`, the regional column is **dropped**, and — because moving existing values across the boundary is `TF-4` — **the migration itself is assessed against §6.2**. Where the data is already in Bangladesh this is trivial; where it is not, it is a notifiable act |
| `RL-3` | **`RESIDENT` → `REGIONAL`**: permitted only with a recorded legal basis. The field is migrated out, and **this is a transfer** |
| `RL-4` | **`Z4` is provisioned for all nine `S3` classes** (`SC-001-D-08`), so `RD1`'s likely outcome is a `RL-2` with no cross-border movement |
| `RL-5` | Every reclassification is recorded in the field's history and in `M60`'s records of processing |
| `RL-6` | **`QA-007` re-runs the residency test suite** after any reclassification |

---

## 11. What Is Not Yet Evidenced

`LG-012` §4.7 established the discipline and §4.7.1 requires republication until empty. Updated at
**2026-08-18 14:25 (+06)**.

| What conformance requires | Status | Owner | Closes with |
|---|---|---|---|
| A legal opinion that split residency satisfies the obligation | **Not obtained** — `DEP-31`, `D-13`, `O-02` | Legal Counsel | `Q-01` |
| The regional store's country named in an approved specification | **Not named** — `O-04` | Chief Architect | `PE-001` |
| Field-level residency classification present in the data model | Specified; **build unevidenced** | Platform Squad | `DA-002`, W1 |
| A write of a restricted field to the regional store **demonstrably failing** | **Unevidenced** — `O-06` | QA | `SC-005` `AT-5` |
| A populated transfer register | **Empty — 8 anticipated, 0 registered** | CDO | §8.2, W1 |
| A populated and published sub-processor register | **Does not exist** — `O-05` | CDO | §8.4 |
| Authority notification records where required | **None**, and `RD4` has not established when they are required | Legal Counsel | `AN-3` |
| Whether the synchronised in-country copy requirement applies | **Not established** — `RD2`, `RD3`, `O-03` | Legal Counsel | `Q-01` |
| Non-production masking verified in every region | Specified; **unevidenced** | QA | `SC-005`, `QA-007` |
| ⊕ **A lawful DR path for `Z4`** | **Does not exist** — `OP-01` | CTO with Legal | §9, `Q-03` |
| ⊕ **In-country key escrow for `K-4`** | **Not provisioned** | CTO | `SC-006` `ES-3`, `Q-04` |
| ⊕ **`SU-4` degraded modes for the 8 transfers** | **None declared** | CDO with owning modules | §6.4 |

**12 rows. 12 open.** §11 is republished with every version until it is empty, and **this document
is not published externally while a blocking row stands** (`LG-012` §4.7.2).

---

## 12. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | **Does the split-residency design satisfy the PDPA 2026 obligation?** (`DEP-31`, `D-13`, `O-02`, `RD2`, `RD3`) | Legal Counsel | **Before W1 architecture freeze** | The field list; `Z4` sizing; `C-05` closure |
| `Q-02` | **Do bank details and individual payroll become `RESIDENT`?** (`RD1`) | CDO with EA | **W1** | §4.3; a later change is a migration |
| `Q-03` | **Option A, B, C or A+B for `Z4` DR?** | CTO with CFO and Legal | **W2** | `OP-01`; `NFR-007` applicability |
| `Q-04` | Is in-country `K-4` escrow provisioned? | CTO | W2 | `SC-006` `ES-3`; option A |
| `Q-05` | **When is a transfer "large-scale"?** (`RD4`) | Legal Counsel | W2 | `AN-3`; every notification decision |
| `Q-06` | **What country is the regional store in?** (`O-04`) | Chief Architect | **W1** | Every transfer row; `TR-01` |
| `Q-07` | Is 1000FiX **critical information infrastructure**? | Legal Counsel | W2 | Feb-2026 amendment residency scope; NCSA obligations |
| `Q-08` | Who registers the 8 transfers, and by when? | CDO | **W1** | `SC-005` `G-13`; every portal build |

---

## 13. Decisions Recorded

| # | Decision | Options | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `SC-007-D-01` | Build before or after the legal opinion? | Wait · **Build the mechanism now** | **Build now** | Classification is data; a change of opinion is a reclassification, not a redesign | W1 cost incurred before the answer; `TR-02` risk absorbed |
| `SC-007-D-02` | Enforcement layers | ORM only · **Build + ORM + schema** | **Three layers** | An ORM check does not protect migration scripts (`TH-036`); **a column that does not exist cannot be written to** | Regional schema must omit resident columns entirely |
| `SC-007-D-03` | `RD1` position | Stay silent · **Recommend addition** | **Recommend** | The categories a regulator would expect in `Z4`; adding later is a notifiable migration | `Z4` provisioned for 9 classes (`SC-001-D-08`) |
| `SC-007-D-04` | Transfer suspension | Deployment config · **Runtime register property** | **Runtime** | `TG-4` requires stopping one transfer without stopping the service | `SU-4` — a transfer with no declared degraded mode may not be registered |
| `SC-007-D-05` | `Z4` DR | Accept degraded · **Recommend A + B** | **A + B** | Option C is the current position **by default rather than by decision**, and `Z4` is small — regulatory-sized, not volume-sized | `PE-002` cost; `Q-03` decision required at W2 |
| `SC-007-D-06` | Notification threshold | Await `RD4` · **Conservative reading** | **Treat every `NFR-099`-category transfer as notifiable** | An unnotified transfer is a breach; an over-notified one is administrative cost | `AN-3`; revisited when `RD4` answers |
| `SC-007-D-07` | Generated documents | Silent · **Inherit classification** | **Inherit the most restricted field's class** | A tax invoice containing a TIN is a resident artefact | `SCA-10` to `M24`, `M20` |

---

## 14. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | The authoritative field list is stated and reconciled across three sources | §4.3, §4.5 |
| `AC-02` | Classification is a model attribute with a permitted-value set and a change procedure | §4.2, §10 |
| `AC-03` | The resident key's non-identifiability is a **tested** property | `RK-5` |
| `AC-04` | Write-time enforcement has more than one layer, including a structural one | §5.3; `SC-007-D-02` |
| `AC-05` | The transfer gate is specified with its block conditions | §6.2 |
| `AC-06` | What counts as a transfer is enumerated beyond the obvious | §6.1 — 7 classes |
| `AC-07` | `LG-012` §4.5.5's suspension design requirement is answered | §6.4; `SU-1`…`SU-5` |
| `AC-08` | Quiet-copy prohibitions are testable | §7 — 8 rules, 8 tests |
| `AC-09` | **`OP-01` has a design, three costed options and a recommendation** | §9 |
| `AC-10` | Degraded mode is designed, not assumed | §9.2 — `DG-1`…`DG-6` |
| `AC-11` | The honest statement about `NFR-007` applicability is made | §9.5 |
| `AC-12` | What is not evidenced is republished and not removed | §11 — 12 rows |

---

## 15. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `AR-001` §8.3 | Topology inherited |
| Upstream | `SC-001` §5, §8 | `Z4`, single-path rule, quiet copies |
| Upstream | `SC-003` | `A-12` reclassification recommendation; proportionality |
| Upstream | `SC-006` §5.3 | `K-4` in Bangladesh |
| Downstream | `SC-005` `G-13` | Build-time transfer-register enforcement |
| Downstream | `SC-008` | Every obligation in §3 becomes a register row with a verification date |
| Downstream | `SC-010` | Per-read access logging on `CD-233`; document classification inheritance |
| Downstream | `PE-002`, `PE-007` | `Z4` DR provisioning — **option A** |
| Downstream | `DA-002` | Field classification carried in the data dictionary |
| Downstream | `M24`, `M20` | `SCA-10` document classification inheritance |
| Downstream | `QA-007` | `AT-5` residency test suite; `RK-5` |
| Lateral | `../../project_content/10_Legal_Policy_and_Compliance/LG-012_*.md` | The statement this is the engineering counterpart of |
| Lateral | `../../project_content/17_Operations_Support_and_Runbooks/OP-012_*.md` | The DR playbook §9 constrains |

---

## 16. References

**Within this repository**
`../PGD-000_*.md` · `./_CATEGORY_OVERVIEW.md` · `./SC-001`, `./SC-002`, `./SC-003`, `./SC-005`, `./SC-006`, `./SC-008` ·
`../02_Architecture_and_Design/AR-001_*.md` §8.3

**Workspace**
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_*.md` §6.3, §6.4 ·
`../../1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M29_*.md` §5.6 ·
`../../1000fix_ERP_Module/03_Modules/A_Service_Delivery_and_Operations/M06_*.md` (`BRU-DTS-16`) ·
`../../1000fix_ERP_Module/00_Governance_and_Charter/00-06_*.md` (`C-05`) ·
`../../project_content/10_Legal_Policy_and_Compliance/LG-012_*.md` ·
`../../project_content/17_Operations_Support_and_Runbooks/OP-012_*.md` ·
`../../project_content/_AUDIT/AUDIT-017_*.md` (`OP-01`, `OP-02`)

**External standards and sources** *(all verified 2026-08-18; statutory content source class `P2`)*

| Source | Version / status | Used for |
|---|---|---|
| **Personal Data Protection Act 2026 (Law 63 of 2026)**, Bangladesh | Enacted April 2026; enforcement ~13 May 2027. Regulator **National Data Management Authority**. **Restricts large-scale transfer of sensitive categories — NID, passport, TIN, biometric, genetic, criminal records — with Authority notification and safeguard disclosure. No general localisation mandate identified.** Amendment Ordinance No. 23 of 2026 (5 Feb 2026) addressed residency for CII and limited personal data | §3 |
| **Cyber Security Ordinance 2025** (No. 25 of 2025) | Gazetted 21 May 2025; in force. NCSA; CII designation and obligations | §3.3; `Q-07` |
| **ISO/IEC 27701** | **:2025, standalone (14 Oct 2025)** — replaces :2019 | Controller transfer obligations |
| ISO/IEC 27018 | Current | Sub-processor and disclosure controls |
| ISO/IEC 29151 | Current | PII protection control checklist |
| ISO/IEC/IEEE 42010 | :2022 | Design-description position |

---

## 17. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. Supplies the engineering design beneath `LG-012`'s position: classification model, reconciled field list, three-layer write-time enforcement, the transfer gate, the suspension design `LG-012` §4.5.5 asked for, eight quiet-copy prohibitions, and — **closing the design half of `OP-01`** — a `Z4` DR design with three costed options and a recommendation. Recommends `RD1` addition of bank details and payroll | *Pending — no constituted body (`PGD-A2-25`)* |

---

*`SC-007` · Category 05 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
