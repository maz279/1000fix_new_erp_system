---
id: RL-006
title: Legacy Decommissioning Plan
category: 12 — Release, Deployment & Transition
code: RL
project: 1000FiX ERP System v2.0
version: 1.1
date: 2026-08-19
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Chief Technology Officer with the Data Migration Lead
approver: Chief Technology Officer with the Chief Financial Officer and the Data Protection Officer
standards_basis: >
  NIST SP 800-88r2 Guidelines for Media Sanitization (published 26 September 2025; r1 withdrawn the
  same day) with IEEE 2883:2022 as the approved technique standard · ISO/IEC 27001:2022 + Amd 1:2024
  Annex A — A.5.10 acceptable use and disposal, A.8.10 information deletion, A.5.37 documented
  operating procedures · ISO 15489-1:2016 records management (archive and disposition) ·
  ISO/IEC 20000-1:2018 + Amd 1:2024 §8.5.3 (release, deployment and service retirement) ·
  Bangladesh PDPA 2026 (Law 63 of 2026) storage limitation and erasure
traces_to: >
  PGD-000 RL-006 row (⛔) · RFP §4.3 Legacy Decommission Map (21 practices) ·
  DM-002 §2.2 source register (48 sources) · GV-001 §5.2 and §12.1 ·
  MG-007 RBK-16 (raised there as Q-04 — the interface this document must honour) ·
  MG-001, MG-002 LPX-32 · DM-014 CV-03, C9 · BRD §6.5 · CM-012 §4.8 #3 ·
  LG-009 retention schedule · DA-006 retention and deletion design · SC-007 residency ·
  AR-002 EP-07 · RL-001 RMP-45 · RL-004 RLO-19
depends_on: >
  RL-001, RL-002, RL-003, RL-004, RL-005 (issued) · MG-001, MG-002, MG-004, MG-007 (issued) ·
  DA-005, DA-006 (issued) · SC-006, SC-007, SC-008 (issued) · PE-007 (issued) ·
  CO-004 Licence & Open-Source Compliance Register (ABSENT ◐) ·
  SV-002 Platform SLA / Service Catalogue (ISSUED 2026-08-19) ·
  DEP-35 media sanitisation programme document (ABSENT — GV-005)
verified_on: 2026-08-19
enumeration_timestamp: 2026-08-19 01:40 (+06)
rule_prefix: DCM — verified unused across all 777 markdown files of the workspace, re-verified at audit 2026-08-19 02:10 (+06)
priority: P1
needed_by: W3
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# RL-006 — Legacy Decommissioning Plan

### Category 12 · Code `RL` · Rule space `DCM` · NIST SP 800-88r2 + IEEE 2883:2022 · ISO/IEC 27001:2022 A.8.10 · ISO 15489-1:2016

---

> **`PGD-000` records this document as ⛔ with the note:** *"The RFP §4 commits to legacy
> decommissioning. **48 legacy sources are named in `DM-002` with no retirement plan.** Systems that
> are never formally switched off keep costing and keep holding personal data."*
>
> **The 48 figure is right and the sentence built on it is not.** Counted from `DM-002` §2.2 at
> 2026-08-19 01:40 (+06): **32** of the 48 carry a decommission wave, **4 are deliberately
> retained**, **1** is purged rather than decommissioned, and **11 are not systems that can be
> switched off at all**. §3 does that count and §4 states what it means for `GV-001` §12.1's
> programme-closure criterion, which as written cannot be met.

---

## 1. Purpose

A legacy system that is replaced but never retired is worse than one that was never replaced. It
keeps a licence bill, keeps an unpatched attack surface, keeps personal data outside the retention
schedule, and — most damaging — keeps offering staff a place to work the old way.

This document states, **per source**: when it may be retired, what happens to its data, how its
media are sanitised, how its licences and contracts are ended, how its access is revoked, and
**what constitutes proof that it is off**.

### 1.1 The interface this document was written to honour

`MG-007` `RBK-16`, raised there as `Q-04` against an unwritten `RL-006`:

> *"Once a wave's legacy processes are withdrawn (`CV-03`, BRD §6.5), fallback has no destination.
> **`RL-006` legacy decommissioning must not retire a source until the parallel run has exited and a
> declared stabilisation period has passed.** `RL-006` is ⛔; this rule is the interface it must
> honour."*

**It is honoured, and the declared stabilisation period is derived rather than chosen.** §6.3
supplies it. `MG-007` `Q-04` is answered.

### 1.2 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | **The population, counted** — 48 sources resolved into four dispositions (§3) |
| 2 | **The reconciliation** — `DM-002`'s 48, RFP §4.3's 21, and `GV-001` §12.1's *"all 48"* (§4) |
| 3 | **Seven retirement states**, and why withdrawal is not decommissioning (§5) |
| 4 | **The stabilisation period**, derived (§6) |
| 5 | **Data archive** — what is kept, for how long, where, and who can read it (§7) |
| 6 | **Media sanitisation** — NIST SP 800-88r2 and IEEE 2883:2022 (§8) |
| 7 | **Access revocation and credential rotation** (§9) |
| 8 | **Licence, contract and cost termination** (§10) |
| 9 | **Proof of off** — the evidence standard, in `GV-009` classes (§11) |
| 10 | **The paper estate** — twelve sources for which "switch off" means something else (§12) |
| 11 | **The decommission register** — the artefact `GV-001` §12.1 requires (§13) |

**Explicitly out of scope:**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| Extracting data from a legacy source | `MG-002` | Extraction precedes retirement and has its own irreversible deadline (`LPX-32`) |
| Transformation, load and reconciliation | `MG-003`, `MG-004` | Migration ends at parallel-run exit; decommissioning is a separate discipline (`MG-001`) |
| Rollback and fallback | `MG-007` | §6 exists so that fallback still has a destination |
| Retention periods per data class | `LG-009`, `DA-006` | **Consumed, never restated.** §7.2 states the relationship |
| Data classification and handling | `DA-005` | Consumed |
| Residency constraints on the archive | `SC-007` | Consumed; §7.4 |
| Cryptographic erase key management | `SC-006` | Consumed; §8.3 |
| Deprecating a **live** capability | `RL-001` §11 | `RMP-45` routes legacy removal here; this document does not do deprecation |
| Which branch stops using what, and when | `RL-004` §6.2, `CM-012` §4.8 | Withdrawal is a site event; decommissioning is a source event |
| The media sanitisation **programme** document | `DEP-35` (unwritten) | §8.1 records that its absence blocks `DCM-27` |

### 1.3 Intended audience

| Audience | What they use this document for |
|---|---|
| CTO | The whole document. The owner of most sources and of the proof |
| Data Migration Lead | §5, §6 — when a source may move state, and the `MG-007` interface |
| Data Protection Officer | §7, §8, §9 — the PDPA 2026 obligations decommissioning discharges or breaches |
| Chief Financial Officer | §10 — the cost that stops, and `SRC-004`'s statutory retention |
| Security Lead | §8, §9 — sanitisation and revocation |
| Quality Manager | §8, §12 — sanitisation technique selection and the paper estate |
| PMO | §13 — the register `GV-001` §12.1 requires for programme closure |
| Steering Committee | §4.3 — the closure criterion that cannot be met as written |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause | How this document conforms | Departure and rationale |
|---|---|---|---|
| **NIST SP 800-88r2** *(published 26 September 2025; r1 withdrawn the same day)* | Media sanitization **programme** framing; logical versus physical sanitisation; vendor-trust verification | §8 requires a sanitisation decision per source, recorded, with a per-device certificate where media leave custody | **Departure:** r2 does not prescribe individual techniques; it requires adherence to **IEEE 2883:2022**, NSA standards, or an organisation-approved alternative. §8.2 selects IEEE 2883:2022, matching `M06` `BRU-DTS-08` |
| **IEEE 2883:2022** | Sanitization: **Clear · Purge · Destruct** | §8.2's technique-by-media-and-disposition table | None |
| **ISO/IEC 27001:2022 + Amd 1:2024** | **A.8.10** information deletion · **A.5.10** acceptable use and disposal · **A.5.37** documented operating procedures | §7 and §8 are A.8.10's deletion controls; §13's register is A.5.37's record | Amd 1:2024 adds climate-action wording to clauses 4.1/4.2 and **no new Annex A controls** |
| **ISO 15489-1:2016** | Records management — appraisal, retention and **disposition**; records must remain accessible for their retention period | §7 and §12 treat archive as a records problem, not a storage problem: an archive nobody can read is a deletion that happened early | None |
| **ISO/IEC 20000-1:2018 + Amd 1:2024** | §8.5.3 — release, deployment and **service retirement** | §5's seven states are a retirement lifecycle with a defined exit | None |
| **PDPA 2026 (Law 63 of 2026)** | Storage limitation; erasure | §7.3 makes retirement the moment personal data leaves an unmanaged store. **Enforcement activates ~13 May 2027, inside Wave 4** (`SC-001` §D-1) | **Departure recorded**: `SC-003` classifies the enacted Bengali instrument as source class `P2` — it has not been read clause by clause. Obligations are taken from `SC-008`'s register, not from the instrument |

### 2.2 Source material relied on

| Source | What it establishes |
|---|---|
| **`DM-002` §2.2** | The **48-source register**, in eight classes, with a Decommission column per source |
| **RFP §4.3** | The **Legacy Decommission Map** — 21 legacy *practices* with their replacing module and wave, and the accountability statement |
| `GV-001` §5.2, §12.1 | Decommissioning as a **chartered obligation**; *"All 48 legacy systems decommissioned"* as a programme-closure criterion |
| `MG-007` `RBK-16`, §8.2 | The stabilisation interface; fallback needs legacy present and un-frozen |
| `MG-002` `LPX-32`, `DM-002` §10 | `SRC-001`/`SRC-002` are withdrawn at W2 and their data is then **lost and unrecoverable** |
| `DM-014` `CV-03`, `C9` | `P4` is a gate, not a date; legacy withdrawal is confirmed per site |
| BRD §6.5 | *"A wave gate is not passed while its legacy process is still running beyond the agreed parallel-run period"* |
| `CM-012` §4.8 #3, `RB-12` | The site's legacy-withdrawal confirmation at Go + 4 weeks, and that it is a **wave-gate input** |
| `LG-009` | 44 KB retention schedule — 27 data classes, 25 document classes, `RC-nn` / `DC-nn` |
| `DA-006` | Retention, archival and deletion design; retention computed, never stored at creation |
| `SC-007` | Residency classification; the two-pass load and the permitted stores |
| `M06` `BRU-DTS-08`, `FR-DTS-020b` | IEEE 2883 as the approved technique standard per SP 800-88r2; vendor-trust verification |
| `GV-005` `DEP-35` | The media sanitisation **programme document** naming IEEE 2883 — **required by W6 minus 2 months, unwritten** |
| `AR-002` `EP-07` | Target-state consequence: no legacy source persists as a shadow system |

### 2.3 Register gaps and audit findings this document closes or raises

| Finding | Source | Position |
|---|---|---|
| `RL-006` ⛔ | `PGD-000` | Closed in specification |
| `MG-007` `Q-04` | `MG-007` `RBK-16` | **Answered.** §6.3 derives the stabilisation period |
| *"48 legacy sources with no retirement plan"* | `PGD-000` | **Corrected.** 32 are decommissionable; §3 counts all four dispositions |
| **`GV-001` §12.1 cannot be met as written** | This document, §4.3 | **New finding `RLA-10`.** *"All 48 legacy systems decommissioned"* is unachievable: 4 are retained by design, 4 are external published registers, 3 are people, and 4 are credential stores that are rotated rather than retired |
| **`DM-002` and RFP §4.3 are two different enumerations** | This document, §4.2 | **New finding `RLA-11`.** 32 decommissionable sources against 21 named practices, and their wave distributions disagree at W2, W3, W4, W5 and W8 |
| **RFP §4.3's W8 item has no `DM-002` source** | This document, §4.2 | **New finding `RLA-12`.** *"Excel management reporting packs → M25 + M62, W8"* maps to no registered `SRC-nnn`, and `DM-002` has no W8 decommission at all |
| `DEP-35` unwritten | `GV-005` | §8.1 records that `DCM-27`'s technique selection is unenforceable without it |
| `CO-004` ◐ | `PGD-000` | §10.2 records that no document holds the legacy licence inventory |

### 2.4 The rule space

Rules carry the prefix **`DCM`**, verified at **zero** occurrences across all markdown files of the
workspace before allocation, re-verified at 2026-08-19 01:40 (+06).

---

## 3. The Population, Counted

### 3.1 Method

`DM-002` §2.2 registers 48 sources across eight class tables. Five of the eight tables carry a
**Decommission** column; three (`PEOPLE`, `PUB`, `CFG`) do not, because their members are not
systems that can be switched off.

Counted by reading the Decommission column of every `SRC-nnn` row at **2026-08-19 01:40 (+06)**.
Reproduction: `awk -F'|' '/^\| ID \|/{...find "Decommission" column...} /^\| \`SRC-/{print}'` over
`DM-002_Legacy_Source_System_Inventory_and_Extract_Catalogue.md`.

### 3.2 The four dispositions

| Disposition | Count | Meaning |
|---|---:|---|
| **`R` — Retire** | **32** | Carries a decommission wave. This document's subject |
| **`K` — Keep by design** | **4** | Marked *"Retained"*. `SRC-020`, `SRC-021`, `SRC-022` become integrations or remain counterparty systems; `SRC-031` retains physical originals for legal reasons |
| **`P` — Purge only** | **1** | `SRC-023` recruitment portals — disposition `P` under `M58` §16.4 and PDPA 2026. Nothing is migrated and nothing is retired; the data is destroyed |
| **`N` — Not a system** | **11** | 3 `PEOPLE` (knowledge, captured not migrated) · 4 `PUB` (external published registers, ongoing reference feeds) · 4 `CFG` (credential and job stores, rotated or reset) |
| | **48** | ✓ against `DM-002`'s counted total |

### 3.3 The 32 retirements by wave

| Wave | Count | Sources |
|:--:|---:|---|
| **W2** | **10** | `SRC-001`, `SRC-002`, `SRC-003`, `SRC-005`, `SRC-006`, `SRC-007`, `SRC-008`, `SRC-009`, `SRC-027`, `SRC-028` |
| **W3** | **6** | `SRC-004`, `SRC-011`, `SRC-012`, `SRC-016`, `SRC-018`, `SRC-025` |
| **W4** | **3** | `SRC-010`, `SRC-019`, `SRC-024` |
| **W5** | **9** | `SRC-013`, `SRC-014`, `SRC-015`, `SRC-017`, `SRC-029`, `SRC-030`, `SRC-032`, `SRC-033`, `SRC-035` |
| **W6** | **3** | `SRC-026`, `SRC-036`, `SRC-037` |
| **W7** | **1** | `SRC-034` |
| **W8** | **0** | — |
| **W9** | **0** | — |
| | **32** | |

> **`DCM-01`. Decommissioning is front-loaded and finishes at W7.** Nineteen of the thirty-two
> retire in W2 and W5 — the two waves that also carry the largest physical cutovers (stock count and
> payroll). **Decommissioning capacity competes with cutover capacity in exactly the two waves that
> have least of it**, and no plan has previously placed the two demands on the same calendar.

### 3.4 The eight classes, and what retirement means in each

| Class | Count | Retire | What "decommissioned" means | § |
|---|---:|---:|---|:--:|
| `DB` application databases | 4 | 4 | Service stopped, data archived, host destroyed, licence ended | 5–11 |
| `SS` spreadsheet estate | 14 | 14 | **Files made read-only, then removed from every share and endpoint.** The hardest class, because copies proliferate | 5–11, `DCM-12` |
| `PORTAL` third-party portals | 5 | 1 | Account closed with the counterparty, or converted to an integration | 9, 10 |
| `MAIL` email archives | 2 | 2 | Mailbox exported, then deleted under `LG-009` | 7 |
| `PAPER` physical records | 12 | 11 | **Records disposition under ISO 15489-1**, not deletion | **12** |
| `PEOPLE` knowledge | 3 | 0 | Not decommissionable. The person remains | 3.2 |
| `PUB` published registers | 4 | 0 | Not decommissionable. They become reference feeds | 3.2 |
| `CFG` credential/job stores | 4 | 0 | **Rotated or reset**, never retired | 9 |
| **Total** | **48** | **32** | | |

---

## 4. The Reconciliation

### 4.1 Three enumerations of "legacy"

| Source | Counts | Unit | Purpose |
|---|---:|---|---|
| **`DM-002` §2.2** | **48** (32 retirable) | A **source** — a place data comes from | Extraction |
| **RFP §4.3** | **21** | A **practice** — a way of working that stops | Contractual accountability |
| **`GV-001` §12.1** | **48** | *"legacy systems"* | Programme closure |

> **`DCM-02`. A source and a practice are not the same object, and 48 ≠ 21 is not an error.** One
> practice — *"service order spreadsheets (per branch)"* — is one RFP row and one `DM-002` source
> holding 51+ files. One source — `SRC-004` standalone accounting software — is replaced by three
> modules and appears as **two** RFP rows (accounting software, and manual invoice preparation).
> **The two registers are both correct and neither is a superset of the other**, which is why §4.4
> merges them rather than choosing one.

### 4.2 Where they disagree, by wave

| Wave | `DM-002` retirable sources | RFP §4.3 practices | Reading |
|:--:|---:|---:|---|
| W2 | **10** | 7 | Sources are finer-grained; the 51-file spreadsheet estate splits into four `SRC` rows |
| W3 | **6** | 3 | `SRC-011` price sheets, `SRC-012` parts lists and `SRC-018` tender register have **no RFP practice row** |
| W4 | **3** | 2 | `SRC-010` AMC spreadsheets and `SRC-019` brand portals map to RFP's two; `SRC-024` email archive is inside RFP's *"email-based warranty claims"* |
| W5 | **9** | 4 | `SRC-017` fixed assets, `SRC-030` personnel files, `SRC-033` vehicle folders and `SRC-035` calibration certificates have **no RFP practice row** |
| W6 | **3** | 3 | Aligned |
| W7 | **1** | 1 | **Both present, and they are different objects.** `SRC-034` is lease and licence documents; RFP W7 is *"manual partner commission calculation"* |
| **W8** | **0** | **1** | **`RLA-12`** — RFP retires *"Excel management reporting packs"* at W8 and `DM-002` registers no such source and no W8 decommission at all |

> **`DCM-03`. Nine sources carry a retirement wave and no contractual accountability, and one
> contractual commitment has no source behind it.** The nine are `SRC-011`, `SRC-012`, `SRC-018`,
> `SRC-017`, `SRC-030`, `SRC-033`, `SRC-035`, `SRC-034` and `SRC-028`. The one is RFP §4.3's W8 row.
> §4.4's merged register is where both are given an owner.

### 4.3 `GV-001` §12.1 cannot be met as written

`GV-001` §12.1 lists, among the criteria for programme closure:

> *"All 48 legacy systems decommissioned — `RL-006` decommission register complete, with proof each
> is switched off."*

| Why it cannot be met | Count |
|---|---:|
| Deliberately **retained** — `SRC-020` and `SRC-021` are payment and bank portals that become integrations and counterparty channels; `SRC-022` is a telematics provider portal; `SRC-031` retains physical contract originals for legal reasons | **4** |
| **Not systems** — 4 externally published registers (`SRC-041`…`SRC-044`) that the platform will consume indefinitely, 3 bodies of human knowledge, 4 credential and job stores that are rotated rather than retired | **11** |
| **Purged, not decommissioned** — `SRC-023`, whose disposition is destruction | **1** |
| **Genuinely decommissionable** | **32** |

> **`DCM-04`. `GV-001` §12.1's criterion is restated as: *"All **32** retirable legacy sources
> decommissioned with proof; the **4** retained sources confirmed as deliberate retentions with a
> named owner and a review date; the **1** purge-disposition source confirmed destroyed; the **11**
> non-system sources confirmed as converted, captured or rotated."***
>
> This is not a relaxation of the criterion. It is four criteria where there was one, and three of
> them had no owner. Recorded as `RLA-10` and raised to `GV-001`'s owner as a v1.1 amendment.

### 4.4 The merged register

> **`DCM-05`. The decommission register (§13) is keyed on `SRC-nnn` and carries the RFP §4.3
> practice as an attribute, not the reverse.** `SRC-nnn` is the finer grain, it is already allocated
> in discovery order and never reused, and every source has one. A register keyed on practice would
> have 21 rows and lose nine sources.

| # | Rule |
|---|---|
| **`DCM-06`** | Every one of the 48 sources appears in the register, including the 16 that will never be retired. A source absent from the register is a source nobody will check |
| **`DCM-07`** | Each of RFP §4.3's 21 practices maps to **at least one** `SRC-nnn`. The W8 row that maps to none (`RLA-12`) is registered as an **unmapped contractual commitment** with an owner, not silently dropped |
| **`DCM-08`** | The nine sources with no RFP practice row (`DCM-03`) are marked **"no contractual accountability"** in the register, so that a vendor scope discussion can see them |

---

## 5. Seven Retirement States

### 5.1 Withdrawal is not decommissioning

The estate uses *"withdrawal"* and *"decommissioning"* interchangeably and they are different
events, separated by weeks and by a different risk.

| | **Withdrawal** | **Decommissioning** |
|---|---|---|
| Means | People stop using it | It stops existing |
| Confirmed by | The branch manager, per site (`CM-012` §4.8 #3, `DM-014` `C9`) | The source's custodian, once |
| Timing | Go + 4 weeks | §6.3's stabilisation period, later |
| Reversible | Yes — people can be told to use it again | **No** |
| Gate relevance | **A wave gate is not passed while a legacy process is still running** (BRD §6.5) | Not a gate criterion |
| Fallback | Still available | **Gone** — this is `MG-007` `RBK-16`'s concern |

### 5.2 The seven states

> **`DCM-09`. A source moves through seven states in order, and never skips one.** Each transition
> has an owner, a precondition and a record.

| # | State | Definition | Transition owner | Precondition |
|:--:|---|---|---|---|
| **`D0`** | **In use** | The system of record, or running in parallel | — | — |
| **`D1`** | **Withdrawn** | No one uses it. It runs, is readable and is writable | Branch manager per site; Data Migration Lead overall | `DM-014` `C9` confirmed at **every** site in scope |
| **`D2`** | **Frozen** | Read-only. Writes are technically prevented, not merely discouraged | Source custodian | `D1` at every site, plus the §6.3 stabilisation period elapsed |
| **`D3`** | **Archived** | Data extracted to the archive; the archive is **verified readable** | Data Migration Lead | `D2`; `MG-004` reconciliation signed; §7 archive test passed |
| **`D4`** | **Access revoked** | Every credential and every route in is closed | Security Lead | `D3` |
| **`D5`** | **Sanitised** | Media sanitised per §8, with a certificate where media leave custody | Quality Manager with the Security Lead | `D4` |
| **`D6`** | **Terminated** | Licence ended, hosting stopped, contract closed, cost removed | CFO for cost; CTO for service | `D5` |
| **`D7`** | **Verified off** | Proof recorded per §11 | **CTO**, countersigned by the DPO where the source held personal data | `D6` |

| # | Rule |
|---|---|
| **`DCM-10`** | **`D2` is the state that matters most and is the one most often skipped.** A withdrawn system that is still writable is a shadow system waiting for the first person who finds the new one slow. `AR-002` `EP-07` names the target state; `D2` is how it is reached |
| **`DCM-11`** | **`D1` → `D2` is irreversible in practice.** Un-freezing a legacy source to serve a fallback is `MG-007` §8.2's procedure and requires the same authority as the fallback itself (CTO with the Programme Director). §6 exists so this is not needed |
| **`DCM-12`** | For the **`SS` spreadsheet estate — 14 of the 32 retirements** — `D2` means removal of write access **at every location a copy exists**: file shares, individual endpoints, email attachments and personal cloud storage. `DM-002` records `SRC-005` and `SRC-006` at *"51+ files"* each. **This is the hardest single task in this document**, and §9.3 gives it a method rather than an aspiration |

---

## 6. The Stabilisation Period

### 6.1 What `MG-007` asked for

`RBK-16` requires a *"declared stabilisation period"* after parallel-run exit, before retirement.
It does not state a length, and a period with no length is satisfied by whatever happens.

### 6.2 The constraints that bound it

| Constraint | Source | Effect |
|---|---|---|
| Parallel run exits at Go + 2 weeks; finance at one full close | `DM-014` `CV-19`, `C8` | The earliest point at which legacy is not in use |
| Legacy withdrawal confirmed per site at Go + 4 weeks | `CM-012` §4.8 #3 | The earliest point at which **every** site has stopped |
| Rollback windows close at 5–10 working days | `OP-002` `RB-03` | After this, rollback is not an option and fallback's destination matters less |
| Hypercare runs 4–8 weeks by wave | `OP-002` §4.3 | The period during which failure is still expected |
| Hypercare exits on **criteria**, not the calendar; `HD-02` requires one full instance of every business cycle | `OP-002` `HX-01`…`HX-18`, `HD-02` | **The first point at which the wave has done its job once** |
| A wave gate is not passed while a legacy process is still running | BRD §6.5, `DM-014` `CV-03` | Withdrawal is a gate input |
| Where a wave rolls out in tranches, the hypercare clock runs from the **last** tranche | `OP-002` `HD-03`; `RL-004` `RLO-27` | The stabilisation clock cannot start at the first site |

### 6.3 The derivation

> **`DCM-13`. The stabilisation period runs from the *later* of hypercare exit and the wave gate
> decision, and lasts one further full business cycle of the longest cycle the source supports —
> with a floor of 30 calendar days.**

The reasoning, step by step:

| Step | Reasoning |
|---|---|
| 1 | Retirement must not remove a fallback destination while fallback is plausible. Fallback is plausible until the wave is stable |
| 2 | *"Stable"* is already defined in this estate, and not by this document: it is **`OP-002`'s eighteen `HX` exit criteria**, four of which are not waivable. Inventing a second definition would create a second answer |
| 3 | `HD-02` guarantees hypercare contains **one full instance of every business cycle the wave touches**. So at hypercare exit, each cycle has run **once** on the new system |
| 4 | Once is not evidence. A month-end that closed, a payroll that paid, a filing that was accepted — each needs a **second** instance before the first is known not to have been luck |
| 5 | Hence: **one further full cycle** after the later of hypercare exit and the gate |
| 6 | For a source supporting no periodic cycle — a paper archive, an order-tracking website — there is no cycle to wait for, so a **floor of 30 calendar days** applies, matching `OP-006`'s deprecation notice period, the shortest interval this estate treats as adequate warning for an irreversible removal |

### 6.4 The period per wave

| Wave | Longest cycle the wave's sources support | Stabilisation after the later of exit/gate |
|:--:|---|---|
| **W2** | None periodic — stock is continuous | **30 calendar days** (floor) |
| **W3** | **Month-end close** | **One further full month-end close, signed** |
| **W4** | Contract and claim cycle; brand claim settlement | **One further claim settlement cycle**, or 30 days, whichever is longer |
| **W5** | **Payroll and statutory filing** | **One further full payroll run, paid**, **and** one further statutory filing accepted |
| **W6** | None periodic | **30 calendar days** (floor) |
| **W7** | Lease and licence renewal — annual | **30 calendar days** (floor). §6.5 |

### 6.5 The annual-cycle exception

> **`DCM-14`.** Where a source's longest cycle is **annual** — `SRC-034`'s lease, tenancy, trade and
> fire licence documents — waiting one further full cycle would delay retirement by a year and
> retire nothing. The floor applies instead, **and the source's `D3` archive is retained for the
> full statutory period under `LG-009`** so that the annual cycle can be served from the archive.
> This is the general principle: **where waiting is impractical, the archive carries the
> obligation, not the live system.**

### 6.6 The two sources the stabilisation rule does not protect

> **`DCM-15`.** `SRC-001` (`station.1000fix.com`) and `SRC-002` (the legacy tracker) are recorded in
> `DM-002` §10 and `MG-002` `LPX-32` as sources whose data is **lost and unrecoverable** once
> withdrawn at W2 — *"the only irreversible deadline in the programme"* (`PGD-000` §2.1).
>
> **That deadline is about extraction, not retirement, and the two must not be conflated.**
> Extraction must complete before W2 withdrawal; retirement still waits for §6.3's period. But
> because the data cannot be re-extracted, **the `D3` archive verification for these two sources is
> the only proof that anything survived**, and it is therefore performed **before** `D1`, not
> after — the single exception to `DCM-09`'s ordering, and it is stated as an exception rather than
> allowed to happen by accident.

---

## 7. Data Archive

### 7.1 The question archive answers

A retired source's data does not stop being needed. It stops being *transacted*. Statutory
retention, audit, dispute resolution, warranty history and legacy order lookup (`FR-SRM-088`) all
outlive the system.

### 7.2 Retention is `LG-009`'s and `DA-006`'s, not this document's

> **`DCM-16`. Every archived dataset carries a retention class from `LG-009` (`RC-nn` / `DC-nn`)
> and is governed by `DA-006`'s design. This document assigns no periods and invents no classes.**
> `DA-006` §-notes already record `PGD-A5-13` — *"no document assigns a retention class to the 1,335
> tables"* — and adding a 49th unclassified store here would make that finding worse.

| # | Rule |
|---|---|
| **`DCM-17`** | A source may not reach `D3` until **every dataset it holds has an assigned `LG-009` retention class**. Where no class fits, the DPO assigns one before archive, not after |
| **`DCM-18`** | Retention is **computed from a trigger, never stored as a date at creation** (`DA-006`). An archive stamped with a fixed deletion date is an archive that will be deleted on the wrong day |

### 7.3 Retirement is when personal data leaves an unmanaged store

| # | Rule |
|---|---|
| **`DCM-19`** | **A legacy source holding personal data is the programme's largest standing PDPA 2026 exposure**, because it is outside the retention schedule, outside the erasure mechanism and outside the access controls the new system provides. `DM-002` marks **`SRC-008`, `SRC-013`, `SRC-014`, `SRC-023` and `SRC-030` as holding personal data at the highest sensitivity**. Retiring them is a **compliance activity**, and §11's proof is compliance evidence |
| **`DCM-20`** | PDPA 2026 **enforcement activates ~13 May 2027, inside Wave 4** (`SC-001` §D-1). Every source still at `D0` or `D1` on that date is a live exposure, and §13's register reports the count at every wave gate from `G3` |
| **`DCM-21`** | `SRC-023` (recruitment portals, disposition `P`) is **destroyed, never archived**. `M58` §16.4 and PDPA 2026 make historical applications purge-only; archiving them would create the retention the disposition exists to prevent |

### 7.4 Where the archive lives

| # | Rule |
|---|---|
| **`DCM-22`** | The archive obeys `SC-007`'s residency rules **in full**. A residency-classified field archived outside its permitted store is the same breach it would be in production, and `MTS-E2` applies to archives as it does to environments |
| **`DCM-23`** | The archive is held **independently of the migration staging schema**, which `MG-004` destroys at parallel-run exit. An archive inside staging is deleted by a process designed to delete staging |
| **`DCM-24`** | The archive is covered by `PE-007`'s backup and restore design, and its restore is tested at the same cadence as production's. `SG-6` — *backup taken and restore tested* — applies |

### 7.5 An archive nobody can read is a deletion

ISO 15489-1:2016 requires records to remain **accessible** for their retention period.

| # | Rule |
|---|---|
| **`DCM-25`** | **`D3` is not reached when the data is copied. It is reached when a named person has read a sample from the archive, using tooling that will still exist when the source is gone.** A proprietary export readable only by the retired application is not an archive |
| **`DCM-26`** | Archive readability is **re-tested annually** and the test recorded. Format obsolescence is slow, silent, and discovered at the moment the data is needed |

---

## 8. Media Sanitisation

### 8.1 The programme, not the technique

NIST SP 800-88r2 — published **26 September 2025**, the same day r1 was withdrawn — changed the
framing: it requires an organisation to establish a **media sanitisation programme** and to adhere
to IEEE 2883:2022, NSA standards or an organisation-approved alternative, rather than prescribing
techniques itself.

> **`DCM-27`. The technique is selected under the Company's documented sanitisation programme, which
> is `DEP-35` and which does not exist.** `GV-005` registers `DEP-35` — *"media sanitisation
> programme document naming IEEE 2883 as the approved technique standard, per NIST SP 800-88r2"* —
> as required by **W6 minus 2 months**, and `00-06` `H-01` records that `M06`'s certificates are
> *"otherwise indefensible"*.
>
> **W6 minus 2 months is too late for this document.** The first sanitisation obligation arises at
> **W2**, when 10 sources retire, four of them holding personal data. Raised as `Q-01`.

### 8.2 Technique by media and disposition

Adopted from IEEE 2883:2022's three categories, applied per `DA-005` classification and final
disposition. **This table is an interim standing until `DEP-35` issues**, at which point `DEP-35`
supersedes it.

| Media | Data class | Disposition | Technique | Evidence |
|---|---|---|---|---|
| Cloud-hosted database | Any | Service terminated | **Cryptographic erase** — destroy the key under `SC-006`, plus provider deletion confirmation | Provider confirmation + key-destruction record |
| Self-hosted disk, reused internally | ≤ D2 | Reuse | **Clear** | Tool and version, operator, date |
| Self-hosted disk, reused internally | **D1 sensitive PII** | Reuse | **Purge** | As above, plus verification pass |
| Any media leaving Company custody | Any | Disposal or resale | **Destruct**, or Purge with verification | **Per-device Certificate of Sanitization** (`M06`), serial-numbered |
| Endpoint holding a legacy spreadsheet copy | Any | Endpoint retained | **Clear** of the specific files, plus a verified absence scan | Scan result per endpoint |
| Backup media of a retired source | Any | Retention expired | **Purge** or **Destruct** by media type | Certificate |
| Paper | Any | Disposition under §12 | **Cross-cut shredding** or witnessed destruction | Destruction certificate |

| # | Rule |
|---|---|
| **`DCM-28`** | **Where a sanitisation tool or third-party service is used, the evidence establishing trust in that vendor's implementation is recorded** — `M06` `FR-DTS-020b`, per SP 800-88r2's vendor-trust requirement. A destruction certificate from an unverified vendor is a receipt, not evidence |
| **`DCM-29`** | Cryptographic erase is only sanitisation **where the key was the sole means of access and its destruction is recorded** (`SC-006`, ISO/IEC 19790). A cloud provider's "delete" without key destruction is a deletion request, not a sanitisation |

### 8.3 The class that has no media

> **`DCM-30`.** Eleven of the 32 retirements are `PAPER` and four are `PORTAL`, `MAIL` or `SS`
> estates hosted by a third party. **For these, sanitisation is not something the Company performs;
> it is something the Company obtains evidence of** — a counterparty deletion confirmation (`E8`),
> or a witnessed physical destruction. §11's evidence classes distinguish the two, because a
> certificate the Company issued about its own act and a confirmation obtained from a third party
> have different reliability and different failure modes.

---

## 9. Access Revocation and Credential Rotation

### 9.1 `D4` — revocation

| # | Rule |
|---|---|
| **`DCM-31`** | `D4` closes **every** route in, enumerated rather than assumed: named user accounts, service accounts, API keys, VPN and network routes, database logins, shared credentials, vendor support access, and any account created for the migration itself |
| **`DCM-32`** | The enumeration is produced by the **source custodian and independently checked by the Security Lead**. A custodian listing their own system's access routes will omit the ones they forgot, which are the ones that matter |
| **`DCM-33`** | Revocation is verified by **attempting access and failing** (`E1`), not by reading a configuration. `SC-004`'s negative-test discipline applies |

### 9.2 The `CFG` class — rotate, never retire

`DM-002`'s four `CFG` sources are not decommissioned:

| Source | Treatment |
|---|---|
| `SRC-045` Integration credentials in config files and developers' notes | **Moved to vault and rotated on migration**, on the assumption that anything previously in plain text is compromised (`M28` §16.4) |
| `SRC-046` Internal user accounts and passwords | **All credentials reset**, never carried (`M29` §16.4) |
| `SRC-047` Customer portal accounts | Migrated with **forced re-authentication on first use** — not a mass reset, which would be a support incident at 250,000+ scale |
| `SRC-048` Legacy cron jobs and scheduled scripts | **Surveyed and registered** — *"an unregistered job that stops running is invisible"* (`M30` §16.4) |

| # | Rule |
|---|---|
| **`DCM-34`** | `SRC-048`'s survey is a **decommissioning prerequisite, not a migration one**. A scheduled job pointing at a source that reaches `D2` fails silently, and the first symptom is a missing report weeks later. Every job is registered, mapped to its source, and explicitly retired or repointed **before** that source reaches `D2` |
| **`DCM-35`** | `SRC-045`'s rotation assumes prior compromise. **The rotation is completed before the source reaches `D1`, not after `D6`** — a credential that was in plain text is compromised whether or not the system holding it is still running |

### 9.3 The spreadsheet estate — a method, not an aspiration

`DCM-12` names this the hardest task. The method:

| Step | Action | Owner | Evidence |
|:--:|---|---|---|
| 1 | Enumerate every known location: file shares, SharePoint/Drive, endpoints, mailboxes | IT Administrator per zone | Location list per source |
| 2 | Make the canonical copies **read-only** at `D2`; announce it (`OP-005`) | IT Administrator | Permission change record |
| 3 | Run a **content scan** across shares and managed endpoints for the file signature | Security Lead | Scan result with counts |
| 4 | Remove copies found; record count removed and count remaining | IT Administrator | Removal record |
| 5 | **Re-scan after 30 days.** New copies appearing after `D2` indicate the old way is still in use | Security Lead | Second scan |
| 6 | Where copies persist, escalate as an **adoption** finding to `CH-004`, not as an IT finding | Change Lead | `CH-004` intervention |

| # | Rule |
|---|---|
| **`DCM-36`** | **Step 5's re-scan is the control, and step 6 is why.** A spreadsheet reappearing after `D2` is not a file-management failure; it is a user telling the programme that the new system does not do something the old one did. `06-02` §5's success criterion is *zero shadow spreadsheets*, and this is the only mechanism in the estate that measures it |
| **`DCM-37`** | Step 3's scan requires endpoint management that **`PE-001`/`PE-009` may or may not provide**. Where it does not exist, step 3 is performed by declaration from each branch manager, and the register records **"declared, not scanned"** — a materially weaker evidence class (`E4` rather than `E2`) |

---

## 10. Licence, Contract and Cost Termination

### 10.1 `D6` — termination

| # | Rule |
|---|---|
| **`DCM-38`** | `D6` requires **four** confirmations, not one: the licence is ended, the hosting or service is stopped, the supporting contract is closed, and **the cost has left the budget**. The fourth is the one that is skipped, and it is the one the CFO cares about |
| **`DCM-39`** | Termination follows the contract's **notice period**, which is frequently longer than the retirement window. The notice is served at `D2`, not at `D6`, so that the notice period runs concurrently with stabilisation rather than after it |
| **`DCM-40`** | A source may reach `D7` with a licence still running **only** where the notice period has been served and its expiry date is recorded in the register. This is the single permitted `D7` exception, and it is dated |

### 10.2 No document holds the legacy licence inventory

> **`DCM-41`.** `CO-004` (Licence & Open-Source Compliance Register) is **◐** in `PGD-000`, resting
> on `02-05` §4, and it addresses the **target** estate's licences. **No document in the workspace
> inventories the licences, hosting contracts and support agreements of the 48 legacy sources.**
>
> The consequence is direct: **`D6` cannot be completed for any source until that inventory
> exists**, because there is nothing to check the four confirmations against. Producing it is a
> W2-minus-2-months task and it is raised as `Q-02`.

### 10.3 The cost that decommissioning releases

| # | Rule |
|---|---|
| **`DCM-42`** | The register records, per source, the **annual run cost** — licence, hosting, support, and the staff time the manual practice consumed. `06-02` §3's benefit model claims automation benefits; **a legacy system still running is a benefit not realised**, and `RL-005` `A3` reads this column |
| **`DCM-43`** | Where a source's run cost is unknown, the register records **"unknown"** rather than zero. A zero in a cost column is read as free |

---

## 11. Proof of Off

### 11.1 The evidence standard

`GV-001` §12.1 requires *"proof each is switched off"*. Evidence classes are `GV-009` §4.1's
`E1`…`E8`, used unchanged.

| State | Evidence required | Class | Who produces it |
|:--:|---|:--:|---|
| `D1` Withdrawn | Legacy-withdrawal confirmation from **every** site in scope | **`E4`** | Branch managers via `DM-014` `C9` |
| `D2` Frozen | Write attempt made and **failed** | **`E1`** | Source custodian, witnessed |
| `D3` Archived | Archive readability test: named person, sample read, tooling recorded | **`E1`** + **`E2`** | Data Migration Lead |
| `D4` Access revoked | Access attempt made and **failed**, per enumerated route | **`E1`** | Security Lead |
| `D5` Sanitised | Certificate of Sanitization, or counterparty deletion confirmation | **`E4`** or **`E8`** | Quality Manager / counterparty |
| `D6` Terminated | Licence end confirmation, service stop confirmation, contract closure, budget line removed | **`E8`** + **`E2`** | CFO with the CTO |
| `D7` Verified off | All of the above, plus a **negative scan**: the host does not answer, the share is gone, the account does not exist | **`E1`** + **`E2`** | **CTO**, countersigned by the DPO where personal data was held |

| # | Rule |
|---|---|
| **`DCM-44`** | **Every proof is a *negative* test — an attempt that fails.** A configuration screenshot showing a service disabled is not proof it is off; `GA-06`'s logic — *"zero findings from a test that did not run is not zero findings"* — applies with full force to a claim that something no longer exists |
| **`DCM-45`** | Where the source is a third party's system (`PORTAL`, hosted `SS`), the proof is an **`E8` counterparty confirmation naming the counterparty, the contact, the reference and the date**. A closed account the Company cannot verify is a claim, not a proof |
| **`DCM-46`** | `D7` is countersigned by the **DPO** for every source that held personal data. The five highest-sensitivity sources (`DCM-19`) may not reach `D7` on the CTO's signature alone |

### 11.2 The false proof to guard against

> **`DCM-47`.** The most common false proof in a decommissioning programme is *"nobody has
> complained"*. Silence after a system is withdrawn means either that it was successfully replaced
> or that the work it did is not being done at all, and the two are indistinguishable without a
> measurement. `DCM-36`'s re-scan and `CH-004`'s adoption measurement are the two instruments that
> tell them apart, and one of them must be cited in the register before `D7`.

---

## 12. The Paper Estate

### 12.1 Twelve sources for which "switch off" means something else

`DM-002` registers **12 `PAPER` sources**, of which **11 carry a retirement wave** (`SRC-031`
retains physical originals by design). They include a **500,000+ document** service history archive
(`SRC-026`), personnel files for 500+ employees (`SRC-030`), and contract originals (`SRC-031`).

> **`DCM-48`. A paper archive is not decommissioned; it is *dispositioned* under ISO 15489-1:2016.**
> The states in §5.2 apply with different meanings: `D2` is *"no new documents are filed here"*,
> `D3` is *"scanned, indexed and quality-checked"*, `D5` is destruction, and `D6` is the end of a
> storage arrangement rather than of a licence.

### 12.2 What differs

| Aspect | Digital source | **Paper source** |
|---|---|---|
| `D2` freeze | Write access removed | **Physical**: the file room stops accepting new filings, and it is labelled |
| `D3` archive | Data export, readability tested | **Scan, OCR-index, quality-check.** `SRC-026` is digitised *"by priority of need, not chronology"* (`M24` §16.4) — so `D3` is reached **progressively**, not at an instant |
| `D5` sanitise | Cryptographic or media sanitisation | Cross-cut shredding or witnessed destruction, certificated |
| Legal original | Rarely an issue | **`SRC-031`: where a paper original must legally be retained, the scan *and* the physical record are both registered** (`M24` §16.4). It never reaches `D5` |
| Timescale | Days | **`SRC-026` retires at W6 — four waves after the data it holds is needed** |

| # | Rule |
|---|---|
| **`DCM-49`** | **A paper source reaches `D3` progressively and the register records percentage complete**, not a boolean. `SRC-026` at 500,000+ documents digitised by priority of need will be partially archived for the whole programme, and a register that can only say "yes" or "no" will say "no" for four years and then "yes" |
| **`DCM-50`** | **Destruction of a paper record is irreversible and is authorised by the record's retention class in `LG-009`, never by the decommissioning schedule.** A source may reach `D6` — its storage arrangement ended — with its records moved to managed storage rather than destroyed. Retirement of the *source* and destruction of the *records* are different decisions with different authorities |
| **`DCM-51`** | `SRC-036` (data recovery job cards) holds **residual customer data from past work**, disposition `P`, *"audited and purged before W6"*. This is a purge with a deadline, not a retirement, and it is tracked as a **PDPA obligation** in `SC-008`, not only here |

---

## 13. The Decommission Register

### 13.1 The artefact `GV-001` §12.1 requires

> **`DCM-52`. One register, keyed on `SRC-nnn`, holding all 48 sources, owned by the CTO, and a
> configuration item under `GV-011`.**

| Column | Content | Source |
|---|---|---|
| `source_id` | `SRC-nnn` | `DM-002` |
| `name`, `custodian` | | `DM-002` |
| `class` | `DB`·`SS`·`PORTAL`·`MAIL`·`PAPER`·`PEOPLE`·`PUB`·`CFG` | `DM-002` §2.1 |
| **`disposition`** | **`R` retire · `K` keep · `P` purge · `N` not a system** | §3.2 |
| `holds_pii` | ✔ / — | `DM-002` |
| `retire_wave` | W2…W7, or *n/a* | `DM-002` |
| **`rfp_practice`** | The RFP §4.3 row(s), or **"no contractual accountability"** | §4.4, `DCM-08` |
| **`state`** | `D0`…`D7` | §5.2 |
| `state_date`, `state_owner` | | §5.2 |
| **`stabilisation_start`, `stabilisation_end`** | Computed per `DCM-13` | §6.3 |
| `retention_class` | `LG-009` `RC-nn` / `DC-nn` | `DCM-17` |
| `archive_location`, `archive_verified_on` | | §7.5 |
| `sanitisation_technique`, `certificate_ref` | | §8.2 |
| `licence_end_date`, `contract_notice_served_on` | | §10 |
| **`annual_run_cost`** | Or **"unknown"** — never zero | `DCM-42`, `DCM-43` |
| **`proof_ref`** | The `D7` evidence pack reference | §11 |
| `dpo_countersign` | Required where `holds_pii` | `DCM-46` |
| `archive_percent_complete` | Paper sources only | `DCM-49` |

### 13.2 Reporting

| # | Rule |
|---|---|
| **`DCM-53`** | The register reports at **every wave gate** (`GV-009` §6.2): sources due for retirement in the wave, sources retired, sources overdue, and — from `G3` — **the count still at `D0`/`D1` holding personal data**, per `DCM-20` |
| **`DCM-54`** | An **overdue** source is one whose `retire_wave` has passed and whose state is below `D7`. Overdue count is reported, never netted against early retirements |
| **`DCM-55`** | The register is the evidence for `RL-005` §11.2 question 4 at the **M42 programme review**, and for `GV-001` §12.1's restated criterion (`DCM-04`) |

### 13.3 Ownership

| # | Rule |
|---|---|
| **`DCM-56`** | Every source has **one named custodian**, taken from `DM-002` and confirmed here. `DM-002`'s custodians are roles — CTO, CFO, HR Director, Warehouse Manager, Branch Operations Lead, Chief Commercial Officer, Quality Manager, Logistics Manager, Finance Director, Service Ops Director, Technical Services Head, Marketing Head, Master Data Owner, Security Lead, Corporate Services Head, Retail Operations Head — and a role, not a person, is what survives three years |
| **`DCM-57`** | **The four `K` (keep) sources are reviewed annually** by their custodian, and the review is recorded. A deliberate retention with no review date becomes an accidental one within two years, which is the failure mode this whole document exists to prevent |

---

## 14. Governing Rules — Consolidated

| # | Rule | § |
|---|---|:--:|
| `DCM-01` | Decommissioning is front-loaded; 19 of 32 retire in W2 and W5, the two heaviest cutover waves | 3.3 |
| `DCM-02` | A source and a practice are different objects; 48 ≠ 21 is not an error | 4.1 |
| `DCM-03` | Nine sources have no contractual accountability; one commitment has no source | 4.2 |
| `DCM-04` | **`GV-001` §12.1's single criterion is restated as four** | 4.3 |
| `DCM-05` | The register is keyed on `SRC-nnn`, with the RFP practice as an attribute | 4.4 |
| `DCM-06` | All 48 appear in the register, including the 16 never retired | 4.4 |
| `DCM-07` | Every RFP practice maps to ≥ 1 source; the unmapped W8 row is registered as such | 4.4 |
| `DCM-08` | Sources with no RFP row are marked "no contractual accountability" | 4.4 |
| `DCM-09` | Seven states, in order, never skipped | 5.2 |
| `DCM-10` | `D2` freeze is the state most often skipped and the one that prevents shadow systems | 5.2 |
| `DCM-11` | `D1` → `D2` is irreversible in practice; un-freezing takes fallback authority | 5.2 |
| `DCM-12` | For 14 spreadsheet sources, `D2` means write access removed **everywhere a copy exists** | 5.2 |
| `DCM-13` | **Stabilisation = later of hypercare exit and gate, + one further full business cycle, floor 30 days** | 6.3 |
| `DCM-14` | Annual-cycle sources take the floor; the archive carries the obligation | 6.5 |
| `DCM-15` | `SRC-001`/`SRC-002` archive-verify **before** `D1` — the single ordering exception | 6.6 |
| `DCM-16` | Retention classes are `LG-009`'s; this document assigns none | 7.2 |
| `DCM-17` | No `D3` until every dataset has an assigned retention class | 7.2 |
| `DCM-18` | Retention is computed from a trigger, never stored as a date | 7.2 |
| `DCM-19` | A legacy source holding personal data is the largest standing PDPA exposure | 7.3 |
| `DCM-20` | PDPA enforcement lands inside W4; the `D0`/`D1` PII count is reported from `G3` | 7.3 |
| `DCM-21` | `SRC-023` is destroyed, never archived | 7.3 |
| `DCM-22` | The archive obeys `SC-007` residency in full | 7.4 |
| `DCM-23` | The archive is independent of the migration staging schema | 7.4 |
| `DCM-24` | The archive is backed up and its restore tested at production cadence | 7.4 |
| `DCM-25` | `D3` is reached when a person **reads** a sample, not when data is copied | 7.5 |
| `DCM-26` | Archive readability is re-tested annually | 7.5 |
| `DCM-27` | **Technique selection is unenforceable until `DEP-35` issues; W6−2mo is too late for W2** | 8.1 |
| `DCM-28` | Vendor-trust evidence is recorded where a tool or service performs sanitisation | 8.2 |
| `DCM-29` | Cryptographic erase counts only with recorded key destruction | 8.2 |
| `DCM-30` | For third-party and paper sources, sanitisation is evidence obtained, not performed | 8.3 |
| `DCM-31` | `D4` enumerates every route in, including migration-created accounts | 9.1 |
| `DCM-32` | The custodian enumerates; the Security Lead independently checks | 9.1 |
| `DCM-33` | Revocation is verified by attempting access and failing | 9.1 |
| `DCM-34` | `SRC-048`'s job survey is a decommissioning prerequisite | 9.2 |
| `DCM-35` | `SRC-045` rotation completes before `D1`, not after `D6` | 9.2 |
| `DCM-36` | The 30-day re-scan is the shadow-spreadsheet control; persistence is an adoption finding | 9.3 |
| `DCM-37` | Without endpoint management, step 3 is "declared, not scanned" — a weaker evidence class | 9.3 |
| `DCM-38` | `D6` requires four confirmations; the cost leaving the budget is the fourth | 10.1 |
| `DCM-39` | Contract notice is served at `D2` so it runs concurrently with stabilisation | 10.1 |
| `DCM-40` | The one permitted `D7` exception is a served notice with a recorded expiry | 10.1 |
| `DCM-41` | **No document inventories legacy licences; `D6` is blocked until one exists** | 10.2 |
| `DCM-42` | The register records annual run cost; a running legacy system is an unrealised benefit | 10.3 |
| `DCM-43` | Unknown cost is recorded as "unknown", never as zero | 10.3 |
| `DCM-44` | Every proof is a negative test — an attempt that fails | 11.1 |
| `DCM-45` | Third-party sources need an `E8` counterparty confirmation | 11.1 |
| `DCM-46` | The DPO countersigns `D7` for every personal-data source | 11.1 |
| `DCM-47` | *"Nobody has complained"* is not proof; cite the re-scan or `CH-004` | 11.2 |
| `DCM-48` | A paper archive is dispositioned under ISO 15489-1, not decommissioned | 12.1 |
| `DCM-49` | Paper `D3` is a percentage, not a boolean | 12.2 |
| `DCM-50` | Record destruction is authorised by retention class, not by the retirement schedule | 12.2 |
| `DCM-51` | `SRC-036`'s residual customer data is a PDPA purge with a deadline | 12.2 |
| `DCM-52` | One register, all 48 sources, CTO-owned, a `GV-011` configuration item | 13.1 |
| `DCM-53` | The register reports at every wave gate, including the PII exposure count from `G3` | 13.2 |
| `DCM-54` | Overdue count is reported, never netted against early retirements | 13.2 |
| `DCM-55` | The register is the evidence for M42 question 4 and for `GV-001` §12.1 | 13.2 |
| `DCM-56` | Every source has one named custodian, held as a role | 13.3 |
| `DCM-57` | The four retained sources are reviewed annually and the review recorded | 13.3 |

**Fifty-seven rules.** Counted from this table at 2026-08-19 01:40 (+06).

---

## 15. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | **`DEP-35` is required at W6 minus 2 months; the first sanitisation obligation is at W2.** Does `DEP-35` move forward, or does §8.2's interim table stand until then? | Quality Manager with the Security Lead | **W2 minus 2 months** | `DCM-27`; `D5` for 10 W2 sources |
| `Q-02` | **Who produces the legacy licence, hosting and support inventory?** `CO-004` covers the target estate only | CFO with the CTO | **W2 minus 2 months** | `DCM-41`; `D6` for every source |
| `Q-03` | Does `GV-001` v1.1 adopt `DCM-04`'s restated closure criterion? | Programme Director | W1 | `RLA-10`; programme closure |
| `Q-04` | Who owns RFP §4.3's unmapped W8 commitment — *"Excel management reporting packs → M25 + M62"*? | PMO with the Data Migration Lead | W3 | `RLA-12`; `DCM-07` |
| `Q-05` | Is endpoint content scanning available (`PE-001`/`PE-009`), or is §9.3 step 3 declaration-based? | Platform Lead with the Security Lead | **W2** | `DCM-37`; the evidence class for 14 sources |
| `Q-06` | Where does the archive physically sit, and is it inside `SC-007`'s permitted stores for residency-classified fields? | Solution Architect with the DPO | **W2** | `DCM-22`, `DCM-23` |
| `Q-07` | Do the four retained sources (`SRC-020`, `021`, `022`, `031`) have named annual reviewers? | CTO with the CFO | W3 | `DCM-57` |
| `Q-08` | `SRC-026` holds 500,000+ paper documents digitised *"by priority of need"*. What percentage must be archived before `D6` — its storage arrangement — may end? | Service Ops Director with the Quality Manager | W5 | `DCM-49` |

---

## 16. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `RL-006-D-01` | How to reconcile `DM-002`'s 48 with RFP §4.3's 21 | (a) Adopt 48 · (b) Adopt 21 · (c) Merge, keyed on `SRC-nnn` | **(c)** | A source and a practice are different objects; neither register is a superset. Keying on practice would lose nine sources | Nine sources are marked "no contractual accountability" and one RFP commitment is marked unmapped |
| `RL-006-D-02` | Whether to restate `GV-001` §12.1 | (a) Report 48 as decommissioned and count retained ones as done · (b) Restate as four criteria | **(b)** | Reporting a retained payment-gateway portal as *"decommissioned"* is a false statement in a closure criterion | `GV-001` needs a v1.1 amendment (`Q-03`) |
| `RL-006-D-03` | The stabilisation period | (a) A fixed 90 days · (b) Later of hypercare exit and gate, + one further business cycle, floor 30 days | **(b)** | A fixed period is arbitrary and would be either too long for a website or too short for payroll. `HD-02` already guarantees one cycle; the second is what makes the first evidence | W5's stabilisation runs to a second payroll **and** a second filing — the longest in the programme |
| `RL-006-D-04` | Whether to define retention periods here | (a) Define per source · (b) Cite `LG-009` and `DA-006` | **(b)** | `PGD-A5-13` already records that no document classifies 1,335 tables; a 49th unclassified store would worsen it | `DCM-17` blocks `D3` until a class is assigned, which surfaces the gap rather than filling it silently |
| `RL-006-D-05` | Sanitisation technique, given `DEP-35` is unwritten | (a) Wait for `DEP-35` · (b) Publish an interim table that `DEP-35` supersedes | **(b)** | The first obligation is at W2 and `DEP-35` is due at W6−2mo. Waiting means ten W2 sources sanitised with no standard | §8.2 is explicitly interim; `Q-01` asks for `DEP-35` to move |
| `RL-006-D-06` | Whether `SRC-001`/`SRC-002` may break the state ordering | (a) Hold the ordering · (b) Archive-verify before `D1` | **(b)** | Their data is unrecoverable after withdrawal; verifying the archive afterwards verifies nothing that can be fixed | The single stated exception to `DCM-09` |

---

## 17. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | The population is **counted**, not quoted, with a reproduction method | §3.1, §3.2 — 32 / 4 / 1 / 11 = 48 ✓ |
| `AC-02` | The retirement waves are counted per source | §3.3 — 10 / 6 / 3 / 9 / 3 / 1 = 32 ✓ |
| `AC-03` | `DM-002`, RFP §4.3 and `GV-001` §12.1 are reconciled, and the disagreements named | §4.1–§4.3; `RLA-10`, `RLA-11`, `RLA-12` |
| `AC-04` | `MG-007` `RBK-16`'s interface is honoured and its `Q-04` answered | §1.1, §6.3, `DCM-13` |
| `AC-05` | The stabilisation period is **derived** from named constraints | §6.2, §6.3 — six steps |
| `AC-06` | Withdrawal and decommissioning are separated and the seam with `CM-012`/`DM-014` stated | §5.1, §5.2 |
| `AC-07` | Every proof is a negative test, and third-party proofs are distinguished | `DCM-44`, `DCM-45`, `DCM-30` |
| `AC-08` | The paper estate is treated as a records-disposition problem | §12, `DCM-48`…`DCM-51` |
| `AC-09` | Standards are cited at their current edition with a verification date | §2.1 — SP 800-88**r2**, IEEE 2883:**2022**, 27001:2022**+Amd 1:2024**, ISO 15489-1:**2016** |
| `AC-10` | The register's columns are specified, including the ones that are usually missing | §13.1 — disposition, cost, proof, DPO countersign, archive percentage |
| `AC-11` | Every blocker is named with its owner and needed-by date | §15 — eight questions |
| `AC-12` | No rule identifier collides with any existing identifier | §2.4 — `DCM` verified at zero |

**Definition of done.** As `RL-001` §16, subject to the same `PGD-A2-25` qualification.

---

## 18. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `DM-002` §2.2 | The 48-source register; every column in §13.1 that is not new comes from here |
| Upstream | RFP §4.3 | The 21 contractual practices; the accountability statement |
| Upstream | `GV-001` §5.2, §12.1 | The chartered obligation and the closure criterion `DCM-04` restates |
| Upstream | `MG-007` `RBK-16` | The interface honoured; `Q-04` answered |
| Upstream | `MG-002` `LPX-32` | The irreversible extraction deadline that `DCM-15` works around |
| Upstream | `DM-014` `CV-03`, `C9`; BRD §6.5 | Withdrawal as a wave-gate input |
| Upstream | `CM-012` §4.8 #3 | Per-site withdrawal confirmation |
| Upstream | `LG-009`, `DA-006` | Retention classes and deletion design, consumed |
| Upstream | `SC-006`, `SC-007`, `SC-008` | Key management, residency, regulatory obligations |
| Upstream | `OP-002` `HD-02`, `HX-*`, `RB-03` | The stabilisation derivation's inputs |
| Downstream | **`RL-005`** §11.2 | M42 question 4 reads this register |
| Downstream | `GV-001` | Requires a v1.1 amendment to §12.1 (`Q-03`) |
| Downstream | `GV-009` | The register reports at every wave gate (`DCM-53`) |
| Downstream | `CH-004` | Persistent shadow spreadsheets escalate as adoption findings (`DCM-36`) |
| Downstream | `GV-005` `DEP-35` | Must move forward to W2−2mo (`Q-01`) |
| Downstream | `CO-004` ◐ | Must be extended to the legacy estate, or a new inventory created (`Q-02`) |
| Lateral | `AR-002` `EP-07` | The target-state consequence this document executes |
| Lateral | `M06` | Sanitisation certificates and vendor-trust verification |
| Lateral | `RL-001` `RMP-45` | Routes legacy removal here rather than through deprecation |

---

## 19. References

**Within this repository**
[`../PGD-000_Master_Register_of_Project_Guiding_Documents.md`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md) ·
[`./_CATEGORY_OVERVIEW.md`](./_CATEGORY_OVERVIEW.md) ·
[`RL-001`](RL-001_Release_Management_and_Versioning_Policy.md) ·
[`RL-004`](RL-004_Rollout_and_Branch_Wave_Deployment_Plan.md) ·
[`RL-005`](RL-005_Post_Implementation_Review_Standard.md) ·
[`../09_Data_Migration_and_Cutover/MG-002_Legacy_System_Profiling_and_Extract_Specification.md`](../09_Data_Migration_and_Cutover/MG-002_Legacy_System_Profiling_and_Extract_Specification.md) ·
[`../09_Data_Migration_and_Cutover/MG-007_Rollback_and_Fallback_Plan.md`](../09_Data_Migration_and_Cutover/MG-007_Rollback_and_Fallback_Plan.md) ·
[`../00_Programme_Governance_and_Control/GV-001_Programme_Charter_and_Mandate.md`](../00_Programme_Governance_and_Control/GV-001_Programme_Charter_and_Mandate.md) ·
[`../03_Data_and_Information_Architecture/DA-006_Data_Retention_Archival_and_Deletion_Design.md`](../03_Data_and_Information_Architecture/DA-006_Data_Retention_Archival_and_Deletion_Design.md) ·
[`../05_Security_Privacy_and_Compliance/SC-007_Data_Residency_and_Cross_Border_Transfer_Design.md`](../05_Security_Privacy_and_Compliance/SC-007_Data_Residency_and_Cross_Border_Transfer_Design.md)

**Workspace**
`../../project_content/12_Data_Migration_Content/DM-002_Legacy_Source_System_Inventory_and_Extract_Catalogue.md` §2.2 ·
`../../project_content/12_Data_Migration_Content/DM-014_Cutover_Data_Checklist_and_Freeze_Communication.md` ·
`../../project_content/10_Legal_Policy_and_Compliance/LG-009_Data_Retention_and_Deletion_Schedule.md` ·
`../../project_content/16_Change_Management_and_Comms/CM-012_Branch_Readiness_Communication_Checklist.md` §4.8 ·
`../../project_content/17_Operations_Support_and_Runbooks/OP-002_Hypercare_Plan_and_Exit_Criteria.md` §4.3, §4.8 ·
`../../1000fix_ERP_Module/03_Modules/A_Service_Delivery_and_Operations/M06_Data_Services_and_Secure_Data_Handling.md` ·
`../../primary-doc/1000FiX_ERP_System_Comprehensive_RFP.md` §4.3

**External standards and sources** *(all verified 2026-08-19)*

| Source | Edition / date | Used for |
|---|---|---|
| **NIST SP 800-88r2** *Guidelines for Media Sanitization* | **Published 26 September 2025**; **r1 (December 2014) withdrawn the same day** | §8 — programme framing, vendor-trust verification |
| **IEEE 2883:2022** | Current — Clear / Purge / Destruct | §8.2 technique selection, per SP 800-88r2's requirement to adopt an approved technique standard |
| ISO/IEC 27001:2022 **+ Amd 1:2024** | Amendment February 2024 — climate action; **no new Annex A controls** | A.5.10, A.5.37, **A.8.10** information deletion |
| ISO 15489-1:2016 | Current | §7.5, §12 — appraisal, retention, disposition, continued accessibility |
| ISO/IEC 20000-1:2018 **+ Amd 1:2024** | §8.5.3 | §5's retirement lifecycle |
| ISO/IEC 19790 | Cryptographic module requirements | `DCM-29`, via `SC-006` |
| Bangladesh **PDPA 2026 (Law 63 of 2026)** | Enacted April 2026; **enforcement activates ~13 May 2027** | §7.3 — storage limitation and erasure. Obligations taken from `SC-008`, not from the instrument (`SC-003` source class `P2`) |

> **Currency note for `RR-005`.** `00-06` `H-01` recorded SP 800-88 r1's withdrawal as a **critical**
> finding after `M06` was drafted on the superseded revision. **This document is written on r2 from
> the outset and cites IEEE 2883:2022 as r2 requires.** The item needing re-verification before W6
> is whether IEEE 2883 has been revised; nothing in this document changes if it has.

---

## 20. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| **1.1** | 2026-08-19 | Enterprise Architecture with Data Migration | **Audit refresh, `PGD-AUDIT-CAT-12`.** `SV-002` confirmed issued; **`CO-003`, `CO-004` and `DEP-35` re-verified as still absent**, so `DCM-27` (no sanitisation standard for the ten W2 retirements) and `DCM-41` (no legacy licence inventory, blocking `D6` for every source) stand unchanged. The 32 / 4 / 1 / 11 population count re-verified against `DM-002` by script at audit | *Pending — `GV-001` `CC-01`* |
| 1.0 | 2026-08-19 | Enterprise Architecture with Data Migration | Initial issue. Fifty-seven `DCM` rules; seven retirement states; a derived stabilisation period; a 20-column decommission register. **Counts the population for the first time**: of `DM-002`'s 48 sources, **32 are retirable, 4 are retained by design, 1 is purge-only and 11 are not systems** — so **`GV-001` §12.1's *"all 48 decommissioned"* cannot be met as written** (`RLA-10`), and is restated as four criteria. Reconciles `DM-002`'s 32 retirements with RFP §4.3's 21 practices, finding **nine sources with no contractual accountability and one contractual commitment with no source** (`RLA-11`, `RLA-12`). Answers `MG-007` `Q-04`. Written on **NIST SP 800-88r2** and **IEEE 2883:2022** from the outset | *Pending — `GV-001` `CC-01`* |

---

*`RL-006` · Category 12 · Rule space `DCM` · 1000FiX ERP System v2.0 · CONFIDENTIAL*
