---
id: SC-008
title: Regulatory Compliance Obligations Register
category: 05 — Security, Privacy & Compliance
code: SC
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Chief Data Officer (unappointed) with Legal Counsel and the CTO
approver: Audit Committee (constituted under GV-002), countersigned by Legal Counsel
standards_basis: >
  ISO/IEC 27001:2022 A.5.31–A.5.36 (legal, statutory, regulatory and contractual requirements) ·
  ISO/IEC 27701:2025 · ISO 19600 / ISO 37301 (compliance management systems) ·
  ISO 9001:2015 §7.5, §9.2 · the "regulatory currency review" control proposed in 00-06 §9
traces_to: >
  PGD-000 SC-008 · 05-06 §6.1 regulatory currency, §6.2 NFR-021…NFR-101, §6.3 NFR-090…099 ·
  M60 FR-GRC-023…027, FR-GRC-033…036 · LG-024 · LG-021 IS-13 · SC-001…SC-007, SC-009…SC-011 ·
  audit findings C-04a, C-04b, H-01, H-05, RQA-05, OP-18, LG-021 O-04, LG-024 O-02, O-08, O-09
depends_on: SC-003 (DPIA determinations) · SC-006 (standards currency) · SC-007 (transfer obligations)
verified_on: 2026-08-18
priority: P0
needed_by: Now
enumeration_timestamp: 2026-08-18 14:40 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# SC-008 — Regulatory Compliance Obligations Register

### Category 05 · Code `SC` · ISO/IEC 27001:2022 A.5.31–A.5.36 · ISO 37301 · the currency control from `00-06` §9

---

> **Before writing, read this.**
>
> 1. **`PG-01` Register-first.** This document's row exists in `PGD-000` Category 05 as `SC-008`.
> 2. **`PG-03` Count, do not consult.** Obligation and citation counts derived at
>    **2026-08-18 14:40 (+06)**.
> 3. **`PG-06` Cite standards.** §2.1.
> 4. **`PG-M4` Verify citations.** **This document is the instrument that makes `PG-M4` operate
>    across the whole estate.** Every row carries a `verified_on` date and a source class.

---

## 1. Purpose

This document is the **currency control**. It holds every statutory, regulatory and standards
obligation that bears on how this system is **engineered**, with — for each — its source, its
owner, the control that discharges it, the evidence that control produces, and **the date the
citation was last verified**.

It exists because the estate has demonstrated, three times, that it cannot keep a citation current
without one:

| Finding | Severity | What happened |
|---|---|---|
| **`C-04a`** | **Critical** | Multiple documents cited the **Digital Security Act 2018** as a live obligation. It had been **repealed twice** — by the Cyber Security Act 2023, then the Cyber Security Ordinance 2025 |
| **`C-04b`** | **Critical** | The repository made **no reference at all** to the **Personal Data Protection Act 2026**, the governing data-protection statute, *"which directly regulates almost everything this ERP does"* |
| **`H-01`** | High | `M06` was built throughout on **NIST SP 800-88 Revision 1**, **withdrawn 26 September 2025** |
| `RQA-05` | Medium | The quality model in use was the superseded **ISO/IEC 25010:2011** |

`00-06` §9 proposed the remedy and named it precisely:

> **"Regulatory currency review** — Every statutory and standards citation carries a *verified-on*
> date and is re-verified at each wave gate. **This would have caught `C-04` and `H-01`.**"

**That control was proposed and never built.** This document is it.

### 1.1 What this document is **not**

`LG-024` already exists and is good. It is the **business-side** register: regulators, filing
obligations, licences, notices, and how to handle a regulator. **This document does not duplicate
it.**

| | `LG-024` | **`SC-008`** |
|---|---|---|
| Question answered | *What must the company file, notify or hold?* | *What must the **system** do, and what proves it?* |
| Population | Filing deadlines, licences, disclosures, regulator relationships | **Engineering obligations** — the ones that become a control, a test or a design constraint |
| Owner | Legal & Compliance | **CDO with the CTO** |
| Relationship | **Authoritative for filing deadlines and licences.** `SC-008` references, never restates | **Authoritative for the currency of every statute and standard the engineering estate cites** |
| Overlap rule | Where the two touch — PDPA obligations, cyber-incident notification — **`LG-024` owns the external act; `SC-008` owns the system control that makes it possible** | |

### 1.2 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | **The currency register** — every statute, ordinance and standard the engineering estate cites, with status, source class and `verified_on` |
| 2 | **The obligations register `CR-01`…`CR-38`** — obligation, source, owner, control, evidence, verification date, state |
| 3 | **Superseded-citation sweep** — every stale citation found in the estate, and where it lives |
| 4 | **Two regulators, four notification clocks** — the PDPA/NDMA and Cyber Security Ordinance/NCSA positions |
| 5 | **Disclosure obligations** — the claims the programme may **not** make, and why |
| 6 | **Standards with a deprecation horizon inside the system's evidential life** |
| 7 | **The verification procedure** — who re-verifies, how, when, and what a failed verification triggers |
| 8 | **Coverage analysis** — obligations with no control, and controls with no evidence |

**Explicitly out of scope:**

| Topic | Owned by | Why |
|---|---|---|
| Filing deadlines, licences, regulator handling | `LG-024` | Business-side; referenced |
| Whether processing is lawful | `SC-003` | Assessment, not registry |
| The control implementations | `SC-001`…`SC-011` | This register names the control; the document specifies it |
| Control **testing** | `M60` `FR-GRC-014`, `FR-GRC-015` | `M60` tests; this registers |
| Enterprise risk | `GV-005`, `M60` | §9 escalates |
| Contract obligations to clients and brands | `CO-00x`, `LG-005`, `LG-006` | Except where they impose a system control |
| Tax computation rules | `M51`, `LG-024` | `NFR-021`, `NFR-100`, `NFR-101` registered here only as system constraints |

---

## 2. Basis and Method

### 2.1 Standards conformance

| Standard | How this document conforms |
|---|---|
| **ISO/IEC 27001:2022 A.5.31** | *Identification of legal, statutory, regulatory and contractual requirements* — §5 is that identification, with owners |
| **A.5.32–A.5.34** | Intellectual property, records protection, privacy and PII protection — `CR-19`…`CR-24` |
| **A.5.35, A.5.36** | Independent review and compliance with policies and standards — §8 verification procedure; `M60` `FR-GRC-014` |
| **ISO/IEC 27701:2025** | Controller and processor obligation set — `CR-19`…`CR-28` |
| **ISO 37301** | Compliance management: identify, assess, control, monitor, review, improve — the register's lifecycle in §8 |
| **ISO 9001:2015 §7.5, §9.2** | Documented information and internal audit — evidence retention and `R49` review |
| **`00-06` §9 currency control** | **The control this document implements.** §4 is the register; §8 is the review cadence |

### 2.2 Source classes

Adopted from `SC-003` §2.3, because a register whose rows do not state their evidential quality is
a register that will be over-relied on.

| Class | Meaning |
|---|---|
| **`P1`** | The enacted instrument or the published standard, read directly |
| **`P2`** | Published analysis, cross-checked across independent sources |
| **`P3`** | Single-source commentary — **may not be the sole basis of a statutory claim** |
| **`V`** | Vendor or standards-body status page / catalogue entry |

### 2.3 Enumeration

| # | Figure | **Counted / derived 2026-08-18 14:40 (+06)** | Note |
|---|---|---:|---|
| 1 | Statutes and ordinances in the currency register | **9** | §4.1 |
| 2 | Standards rows in the currency register | **36** | §4.2 |
| 3 | **Entries with status ❌ withdrawn, repealed or superseded** | **10** | §4.3. *(The first issue stated 24 and 9; corrected during the Category 05 audit — `SCA-13`)* |
| 4 | Engineering obligations registered | **38** (`CR-01`…`CR-38`) | §5 |
| 5 | Obligations with a **named control that exists in specification** | **31** | §7.1 |
| 6 | Obligations with **no control at all** | **4** | §7.2 |
| 7 | Obligations whose control exists but **produces no evidence today** | **34** | §7.3 — because nothing is built |
| 8 | **Notification clocks that may run simultaneously** | **4** | §6 |
| 9 | Obligations with a **deadline the programme cannot state as fact** | **2** | `OP-18`; `CR-25`, `CR-26` |
| 10 | Disclosure prohibitions | **6** | §10 |

---

## 3. The Rules This Register Operates Under

Adapted from `LG-024` §4.1 `RG-R1`…`RG-R12`, with four additions for the engineering context.

| # | Rule |
|---|---|
| `CR-R1` | **Every obligation has a named owner, a control, an evidence requirement and a stated consequence of breach.** A row missing any of the four is not a register entry |
| `CR-R2` | **An obligation discharged without evidence is recorded as a control failure, not as discharged** (`BRU-GRC-12`, `LG-021` §4.1.6) |
| `CR-R3` | **A breached obligation is recorded, assessed and escalated. It is never quietly closed** (`BRU-GRC-13`) |
| `CR-R4` | **A deadline is taken from the instrument, not from custom** (`RG-R9`) |
| `CR-R5` | **The register is reviewed at least quarterly and at every wave gate** |
| ⊕ `CR-R6` | **Every citation carries a `verified_on` date and a source class.** A citation older than one review cycle is treated as **unverified** until re-checked |
| ⊕ `CR-R7` | **A `P2` or `P3` claim may not be stated as fact** in a tender response, a client assurance pack or a certificate |
| ⊕ `CR-R8` | **A standard's status is not a stable fact.** Withdrawal is a normal event, and the register's job is to notice it (§4.3 records nine) |
| ⊕ `CR-R9` | **An obligation with a deprecation horizon inside the evidential life of what it protects is registered with that horizon as a dated action**, not as background knowledge (§4.4) |

---

## 4. The Currency Register

### 4.1 Statutes and ordinances — Bangladesh

| # | Instrument | **Status at 2026-08-18** | Src | `verified_on` | Owner |
|---|---|---|:--:|---|---|
| `ST-01` | **Digital Security Act 2018** | ❌ **REPEALED** by the Cyber Security Act 2023 (13 September 2023) | `P2` | 2026-08-18 | Legal |
| `ST-02` | **Cyber Security Act 2023** | ❌ **REPEALED** by the Cyber Security Ordinance 2025 | `P2` | 2026-08-18 | Legal |
| `ST-03` | **Cyber Security Ordinance 2025** (Ordinance No. 25 of 2025) | ✅ **IN FORCE.** Gazetted 21 May 2025. Establishes the **National Cyber Security Agency**; regulates **critical information infrastructure**; a declared CII must operate **its own CERT/CIRT and SOC**, with **quarterly reports** to the NCSA | `P2` | 2026-08-18 | **CTO** |
| `ST-04` | **Personal Data Protection Ordinance 2025** | ❌ Issued 6 November 2025; amended by **Ordinance No. 23 of 2026** (5 February 2026); **repealed on enactment of the Act** | `P2` | 2026-08-18 | Legal |
| `ST-05` | **Personal Data Protection Act 2026 (Law 63 of 2026)** | ✅ **IN FORCE** — enacted April 2026. **Complaint and enforcement mechanisms activate ~13 May 2027 — inside Wave 4.** Regulator: **National Data Management Authority**, reporting to the Prime Minister's Office. Penalties **BDT 25 lakh**, **BDT 50 lakh** for a significant data fiduciary, plus repeat-violation fines. **Breach-notification period and DPIA methodology are left to regulations/SOPs not yet published** | `P2` | 2026-08-18 | **CDO** |
| `ST-06` | ICT Act 2006 | ✅ In force | `P2` | 2026-08-18 | Legal |
| `ST-07` | VAT and Supplementary Duty Act 2012 | ✅ In force | `P2` | 2026-08-18 | CFO |
| `ST-08` | Bangladesh Labour Act 2006 (as amended) | ✅ In force | `P2` | 2026-08-18 | HR Director |
| `ST-09` | Consumer rights protection framework | ✅ In force | `P3` | 2026-08-18 | Legal |

> **`SC-008-F-01`. Four of nine statutory rows are ❌.** Three are repealed instruments the estate
> once cited as live; one is a repealed ordinance superseded by its own Act. **This is the shape of
> `C-04a` made visible**, and it is why the register lists dead instruments rather than deleting
> them: a citation of `ST-01` anywhere in the estate must resolve to a row that says *repealed*, not
> to nothing.

### 4.2 Standards

| # | Standard | **Status at 2026-08-18** | Src | Used by |
|---|---|---|:--:|---|
| `SD-01` | **ISO/IEC 27001:2022 + Amd 1:2024** | ✅ Current. Amd 1 (Feb 2024) — climate action, clauses 4.1/4.2; **no new Annex A controls**. 93 controls, 4 themes | `V` | `SC-001` |
| `SD-02` | ISO/IEC 27002:2022 | ✅ Current | `V` | `SC-001` |
| `SD-03` | **ISO/IEC 27701:2025** | ✅ Current — **standalone edition, 14 October 2025. Replaces :2019.** No longer requires ISO/IEC 27001 as a base | `V` | `SC-003`, `SC-007` |
| `SD-04` | ISO/IEC 27701:2019 | ❌ **Superseded** | `V` | — |
| `SD-05` | **ISO/IEC 29134:2023** | ✅ Current (Edition 2) | `V` | `SC-003` |
| `SD-06` | ISO/IEC 29134:2017 | ❌ **WITHDRAWN** | `V` | — |
| `SD-07` | ISO/IEC 29100:2024 | ✅ Current | `V` | `SC-003` |
| `SD-08` | ISO/IEC 27005:2022 | ✅ Current | `V` | `SC-002`, `SC-003` |
| `SD-09` | ISO/IEC 27035 (incident management) | ✅ Current | `V` | `SC-011` |
| `SD-10` | ISO/IEC 27033 (network security) | ✅ Current | `V` | `SC-001` |
| `SD-11` | ISO/IEC 27018, 29151 | ✅ Current | `V` | `SC-007` |
| `SD-12` | ISO 9001:2015 | ✅ Current | `V` | `M23`, `NFR-024` |
| `SD-13` | ISO 10007:2017 | ✅ Current | `V` | `GV-011` |
| `SD-14` | ISO 37301 | ✅ Current | `V` | **This document** |
| `SD-15` | **NIST SP 800-88 r1** | ❌ **WITHDRAWN 26 September 2025** | `V` | — (`H-01`) |
| `SD-16` | **NIST SP 800-88 r2** | ✅ Current — published 26 September 2025 | `V` | `SC-006`, `M06` |
| `SD-17` | **IEEE 2883-2022** | ✅ Current | `V` | `SC-006`, `M06` |
| `SD-18` | **IEEE 2883.1-2025** | ✅ Current — **newer companion `M06` does not cite** (`SCA-08`) | `V` | `SC-006` |
| `SD-19` | ISO/IEC 19790 | ✅ Current | `V` | `SC-006` |
| `SD-20` | NIST SP 800-57 Part 1 Rev. 5 | ✅ Current | `V` | `SC-006` |
| `SD-21` | **FIPS 140-2** | ❌ **Superseded**; no new validations | `V` | — |
| `SD-22` | **FIPS 140-3** | ✅ Current | `V` | `SC-006` |
| `SD-23` | **FIPS 203 / 204 / 205** | ✅ Final, August 2024 — ML-KEM, ML-DSA, SLH-DSA | `V` | `SC-006` §11 |
| `SD-24` | **NIST IR 8547** | ✅ Current — **112-bit classical deprecated after 2030, disallowed after 2035** | `P2` | `SC-006` §10.4 |
| `SD-25` | **NIST SP 800-218 SSDF v1.1** | ✅ Current final (Feb 2022). **SP 800-218r1 (v1.2) is an initial public draft, released 17 December 2025, in public comment — not adopted** | `V` | `SC-005` |
| `SD-26` | NIST SP 800-218A | ✅ Current (July 2024) — generative-AI profile | `V` | `SC-005` §12 |
| `SD-27` | NIST SP 800-61 **r3** | ✅ Current — April 2025, CSF 2.0 community profile. **Supersedes r2** | `V` | `SC-011` |
| `SD-28` | NIST SP 800-61 r2 | ❌ **Superseded** | `V` | — |
| `SD-29` | NIST SP 800-63-4 | ✅ Current | `V` | `SC-004` |
| `SD-30` | NIST SP 800-207 | ✅ Current | `V` | `SC-001` §10 |
| `SD-31` | **OWASP ASVS 5.0.0** | ✅ Current — **30 May 2025. Supersedes 4.0.3** | `V` | `SC-001`, `SC-005` |
| `SD-32` | **OWASP ASVS 4.0.3** | ❌ **Superseded** — **and cited by `_CATEGORY_OVERVIEW.md` and `PGD-000`** | `V` | — (`SCA-03`) |
| `SD-33` | **OWASP Top 10:2025** | ✅ Current — 6 November 2025, finalised January 2026. New `A03` Software Supply Chain Failures, `A10` Mishandling of Exceptional Conditions | `V` | `SC-002`, `SC-005` |
| `SD-34` | **ISO/IEC 25010:2011** | ❌ **Superseded** by :2023 (`RQA-05`) | `V` | — |
| `SD-35` | ISO/IEC 25010:2023 | ✅ Current | `V` | `RQ-006`, `AR-001` |
| `SD-36` | ISO/IEC/IEEE 29148:2018, 42010:2022, IEEE 1016-2009, ISO/IEC/IEEE 29119-3:2021 | ✅ Current | `V` | Categories 01, 02, 08 |

**Counted: 36 standards rows, 10 entries with status ❌** — regenerated by counting rows in §4.1 and §4.2, per `PG-M10`. 3 of the 9 `ST-` rows and 7 of the 36 `SD-` rows are ❌.

### 4.3 The ten ❌ entries, and where they still live in the estate

> **A superseded citation is only a finding if something still cites it.** This is the sweep.

| ❌ Entry | Still cited in | Action | Owner |
|---|---|---|---|
| `ST-01` DSA 2018 | **Corrected** in `05-06` §6.1; `M06` and the Category I overview were remediated under `C-04a` | ✔ Closed — **re-verify by sweep at each gate** | Legal |
| `ST-02` CSA 2023 | Historical references only | ✔ | Legal |
| `ST-04` PDP Ordinance 2025 | Referenced correctly as superseded | ✔ | Legal |
| `SD-04` ISO/IEC 27701:**2019** | Not cited anywhere; `SC-003` and `SC-007` cite :2025 | ✔ | — |
| `SD-06` ISO/IEC 29134:2017 | Not cited anywhere | ✔ | — |
| `SD-15` **NIST SP 800-88 r1** | `M06` **rebased on r2**; r1 appears only as a struck-through historical row | ✔ Closed (`H-01`) | Quality Manager |
| `SD-21` FIPS 140-2 | Not cited | ✔ | — |
| `SD-28` NIST SP 800-61 r2 | Not cited | ✔ | — |
| `SD-32` **OWASP ASVS 4.0.3** | ⚠ **`05_Security_Privacy_and_Compliance/_CATEGORY_OVERVIEW.md` and `PGD-000` Category 05 preamble both cite "OWASP ASVS 4"** | ⚠ **OPEN — corrected in `SC-001` §2.1 and `SC-005`; the two source documents must be updated** | Enterprise Architecture |
| `SD-34` **ISO/IEC 25010:2011** | ⚠ `RQA-05` records it; corrected in `RQ-006` | ⚠ Verify the sweep completed | Enterprise Architecture |

> **`SC-008-F-02`. Two of ten are still live in the estate, and one of them is in this very
> category's own overview.** `SCA-03`. **This is the fourth occurrence of the stale-citation defect
> class** after `C-04a`, `H-01` and `RQA-05` — which is precisely the recurrence pattern `GV-010`
> found: *"five defect classes accounting for eighteen instances."* The register does not prevent
> the defect; **it makes the defect findable in one place**, which is the most a register can do.

### 4.4 Deprecation horizons inside the system's evidential life

`CR-R9`. These are dated, foreseeable obligations — not background knowledge.

| # | Horizon | Date | Affects | Registered as |
|---|---|---|---|---|
| `HZ-01` | **PDPA 2026 enforcement mechanisms activate** | **~13 May 2027 — inside Wave 4** | Everything in `SC-003` | `CR-19`…`CR-28` |
| `HZ-02` | **RSA/ECC (112-bit) deprecated** | **After 2030** | `M06` destruction certificates; `LG-019` e-signatures; audit hash chain | `CR-31`; `SC-006` `RS-5` |
| `HZ-03` | **RSA/ECC disallowed** | **After 2035** | As `HZ-02`, and any artefact still within evidential life | `CR-31` |
| `HZ-04` | **SSDF v1.2 finalisation** | Unknown — draft in comment since 17 Dec 2025 | `SC-005` §4 | `CR-34`; `RM` trigger |
| `HZ-05` | **PDPA breach-notification regulations published** | Unknown | `SC-011`; `OP-004` `RN-03`'s 72-hour planning assumption | `CR-25` |
| `HZ-06` | **NDMA DPIA SOP published** | Unknown | `SC-003` methodology conformance | `CR-27` |

---

## 5. The Obligations Register

**38 obligations.** Columns: **Source** the instrument or standard · **Control** the `SC-` control
or document that discharges it · **Evidence** what proves it operated · **St** ● control exists in
specification · ◐ specified, not built · ✖ **no control**.

### 5.1 Data protection — PDPA 2026 (`CR-01`…`CR-15`)

| ID | Obligation | Source | Owner | Control | Evidence | St |
|---|---|---|---|---|---|:--:|
| `CR-01` | Process personal data only on consent or a stated legitimate ground, recorded per purpose | `NFR-090` §6.3 | CDO | `M33`; `SC-003` §3.4; `PD-1` | Processing record `FR-GRC-033` | ◐ |
| `CR-02` | Consent clear, explicit, specific, freely given; **heightened standard for sensitive data**; easily revocable | `NFR-091` §6.3 | CDO | `M33` consent register; `PD-4`, `PD-5` | Consent records with notice version | ◐ |
| `CR-03` | **Transparency notice** stating categories, purposes, **risks**, retention, transfers, withdrawal | `NFR-092` §6.3 | CDO | `LG-008` | Published notice + version binding | ◐ |
| `CR-04` | Access and portability | `NFR-093` | CDO | `PD-3` DSR orchestrator | DSR fulfilment records | ◐ |
| `CR-05` | **Rectification with recipient notification within 30 days** | `NFR-093`, `BRU-CPM-10` | CDO | `M33`; recipient list from `SC-007` §8.2 | Notification records | ◐ |
| `CR-06` | Erasure on purpose cessation, withdrawal, unlawful processing or legal requirement | `NFR-093`, `BRU-CPM-11` | CDO | `PD-2`; `BRU-SEC-23` legal-hold override | Erasure records with override basis | ◐ |
| `CR-07` | Withdrawal through a simplified procedure, all channels, immediate | `BRU-CPM-09` | CDO | `PD-4` | Propagation evidence | ◐ |
| `CR-08` | **Verifiable parental consent for subjects under 18** | `BRU-CPM-16`, `CN-09` | CDO | `PD-7`; **`SC-003` `A-13`** | Parental consent records | ◐ |
| `CR-09` | **Appoint a Chief Data Officer if a significant data fiduciary** | `NFR-096` | **CEO/Board** | — | Appointment record | **✖** |
| `CR-10` | Technical and organisational measures proportionate to risk | `NFR-097` | CTO | `SC-001` — 68 controls | Control test results | ◐ |
| `CR-11` | **Processing records retained ≥ 5 years** | `NFR-095` | CDO | `M60` `FR-GRC-033`; `SC-010` | The register itself | ◐ |
| `CR-12` | **Processor obligations flowed down by contract to every processor and sub-processor** | `NFR-098` | CTO/Procurement | `SC-007` §8.4 | **Sub-processor register — does not exist** | **✖** |
| `CR-13` | **Restrict large-scale transfer of Sensitive PII; notify the Authority; disclose safeguards** | `NFR-099`, `NFR-086b` | CDO | `SC-007` §6 gate | Transfer register + notification refs | ◐ |
| `CR-14` | **Split residency — sensitive PII in a Bangladesh-resident store** | `NFR-086`, `086a` | CDO/Architect | `SC-007` §4, §5 | Write-time enforcement test | ◐ |
| `CR-15` | **Non-production never holds unmasked residency-classified data, in any region** | `NFR-086c` | CTO | `SEC-NP-1`…`-4` | Masking verification per clone | ◐ |

### 5.2 Cyber security — Cyber Security Ordinance 2025 (`CR-16`…`CR-18`)

| ID | Obligation | Source | Owner | Control | Evidence | St |
|---|---|---|---|---|---|:--:|
| `CR-16` | **Determine whether 1000FiX is critical information infrastructure** | `ST-03` | **Legal Counsel** | — | A recorded determination | **✖** |
| `CR-17` | **If CII: operate an own CERT/CIRT and SOC, with quarterly reports to the NCSA** | `ST-03` | CTO | `SC-011` §9 | Quarterly report submissions | ◐ **conditional on `CR-16`** |
| `CR-18` | Cyber-incident reporting to the national structure | `ST-03` | CTO | `SC-011` §6 clock (b) | Notification records | ◐ |

> **`SC-008-F-03`. `CR-16` is unowned and undated, and everything about `CR-17` depends on it.**
> `LG-024` §4.2 already names the national cyber-security structure with the CTO as owner and marks
> it `RG7`/`O-09`. **A CII designation would impose an own-SOC-and-CIRT obligation with a quarterly
> reporting cadence that no document in the estate has costed** — `GV-007` and `GV-008` carry no
> line for it. Escalated to `GV-005` and `GV-008`. `SC-001` `Q-04`.

### 5.3 Security control obligations (`CR-19`…`CR-28`)

| ID | Obligation | Source | Owner | Control | Evidence | St |
|---|---|---|---|---|---|:--:|
| `CR-19` | Role-based access with field-level granularity | `NFR-011` | CTO | `SEC-C-016`; `SC-004` §8 | 67 access profiles + negative tests | ◐ |
| `CR-20` | MFA for admin, finance, HR and privileged roles | `NFR-012` | CTO | `SEC-C-004`; `SC-004` §6.1 | Realm policy + login records | ◐ |
| `CR-21` | AES-256 at rest; TLS 1.2+ in transit | `NFR-013` | CTO | `SC-006` §3 | Configuration evidence | ◐ |
| `CR-22` | **Complete immutable audit trail** | `NFR-014` | CTO | `SEC-C-038`, `-039`; `SC-010` | Chain verification job | ◐ |
| `CR-23` | Branch-level isolation at the record level | `NFR-015` | CTO | `SEC-C-015`; `T2` negative test | Test results | ◐ |
| `CR-24` | Segregation of duties enforced by the permission engine | `NFR-064` | CFO/CTO | `SC-004` §11; `SP-006` | Controlled violation attempts | ◐ |
| `CR-25` | **Notify the NDMA of a breach likely to cause significant damage, within the prescribed timeframe** | `NFR-094` | CDO | `SC-011` §6 clock (a) | Breach register + notification | ⚠ **The period is not prescribed** (`OP-18`, `HZ-05`) |
| `CR-26` | **Contractual breach notification to clients, brands and insurers** | `LG-004`…`LG-007` | Legal | `SC-011` §6 clock (d) | Notification records | ◐ |
| `CR-27` | **Privacy impact assessment before new higher-risk processing** | `FR-GRC-037`, `ST-05` | CDO | **`SC-003`** | The assessment | ◐ — **conformance to the NDMA SOP is `HZ-06`** |
| `CR-28` | Vulnerability discovery, triage and remediation to SLA | `NFR-066`, `BRU-SEC-21` | CTO | `SC-009` | Scan results, SLA compliance | ◐ |

### 5.4 Records, evidence and quality (`CR-29`…`CR-33`)

| ID | Obligation | Source | Owner | Control | Evidence | St |
|---|---|---|---|---|---|:--:|
| `CR-29` | ISO 9001:2015 audit trail and documented information | `NFR-024` | Quality Manager | `SC-010`; `M23`, `M24` | Certification audit | ◐ |
| `CR-30` | **Records retention per the statutory schedule, enforced by the system** | `NFR-088` | Legal/CFO | `PD-2`; `LG-009` | Retention enforcement records | ◐ |
| `CR-31` | **Cryptographic re-sealing before an algorithm's deprecation horizon** | `SD-24`, `SC-006` `RS-5` | CTO | `SC-006` §10.4 | Re-seal records | ◐ — **first review W4; unconditional trigger at `HZ-02`** |
| `CR-32` | **Media sanitisation programme to SP 800-88 r2 with IEEE 2883 techniques and vendor-trust verification** | `SD-16`, `SD-17` | Quality Manager | `SC-006` §9 | Certificates, verification records, `VT-1`…`VT-6` | ◐ |
| `CR-33` | e-signature evidence sufficient for legal effect | `LG-019` | Legal | `SC-006` §10.4; `SC-010` | Signature + re-seal chain | ◐ |

### 5.5 Tax, labour and sector (`CR-34`…`CR-38`)

Registered here **only as system constraints**; the filing obligations are `LG-024`'s.

| ID | Obligation | Source | Owner | Control | Evidence | St |
|---|---|---|---|---|---|:--:|
| `CR-34` | **Mushak 6.3 tax-invoice format compliance** | `NFR-021`, `ST-07` | CFO | `M51`, `M20` | Invoice format validation | ◐ |
| `CR-35` | **Mushak 9.1 monthly VAT return by the 15th, via the NBR portal** | `NFR-100` (`H-05`) | CFO | `M51` | Filing records — **`LG-024` owns the act** | ◐ |
| `CR-36` | **Input VAT credit blocked without a valid Mushak 6.3 invoice** | `NFR-101` (`H-05`) | CFO | `M51` hard rule | Blocked-claim records | ◐ |
| `CR-37` | Labour Act compliance in HR and payroll | `NFR-083`, `ST-08` | HR Director | `M21`, `M56` | Payroll compliance records | ◐ |
| `CR-38` | E-waste and environmental handling; EPR | `NFR-084` | Quality Manager | `M18` | Disposal certificates | ◐ |

---

## 6. Four Notification Clocks

`LG-021` §4.10.2 identifies them; this register dates and owns them. **They may run
simultaneously, they are different, and the clock starts at detection.**

| # | Clock | Trigger | Deadline | Owner | State |
|---|---|---|---|---|---|
| **(a)** | **National Data Management Authority** | A personal-data breach **likely to cause significant damage** | **Prescribed by regulations — not yet published** (`HZ-05`) | **CDO** | ⚠ `OP-004` `RN-03` uses a **72-hour planning assumption, explicitly marked as a planning figure and not a legal statement**. `CR-25` |
| **(b)** | **National cyber-security structure / NCSA** | A cyber incident, **if 1000FiX is CII** | Per `ST-03` and its rules | **CTO** | ✖ **Depends on `CR-16`, undetermined** |
| **(c)** | **Affected data subjects** | Where the risk to them requires it | Per `ST-05`; `LG-008` §4.8 | CDO | ◐ |
| **(d)** | **Clients, brand partners, insurers** | Per contract | Per instrument — **often shorter than statute** | Legal | ◐ |

| # | Rule |
|---|---|
| `NC-1` | **The clock starts at detection**, not at confirmation, not at containment |
| `NC-2` | **A decision not to notify is recorded with its reasoning** (`LG-021` §4.10.3) |
| `NC-3` | **Until the period is prescribed, no document may state a notification deadline as fact** (`OP-18`) |
| `NC-4` | **The shortest applicable clock governs operational readiness.** Contractual (d) is frequently shorter than statutory (a), and planning to the statute alone would breach the contract |

---

## 7. Coverage Analysis

### 7.1 Obligations with a control that exists in specification — 31

31 of 38. The specification quality is high; the build has not started.

### 7.2 Obligations with **no control at all** — 4

| ID | Obligation | Why nothing covers it | Escalated to |
|---|---|---|---|
| **`CR-09`** | **Appoint a Chief Data Officer** | An organisational act. `NFR-096`; `LG-024` `O-08`; `SC-003` §11 — **this DPIA cannot be signed without it** | Board; `GV-005` |
| **`CR-12`** | **Processor and sub-processor flow-down** | **The sub-processor register does not exist** (`LG-012` `O-05`) | CDO; `SC-007` §8.4 |
| **`CR-16`** | **CII determination** | Nobody has been asked the question | Legal; `GV-005` |
| ⊕ | **Security awareness training delivery** | `LG-021` §4.12.4: **`TR-025` statutory induction is unregistered**, so the annual obligation has no vehicle | CTO with L&D; `SC-001` `SEC-E-06` |

### 7.3 Obligations whose control produces no evidence today — 34

**34 of 38.** The reason is uniform and expected: **nothing is built**. `LG-021` §4.13.1 records
that the control register itself does not exist (`O-04`), and §4.13.6 that no scanning,
penetration-testing or assessment evidence exists (`O-09`).

> **`SC-008-F-04`. The gap between 31 obligations with a control and 4 obligations with evidence is
> the whole compliance position of this programme, stated in one line.** `CR-R2` says an obligation
> discharged without evidence is a control failure. Applied literally today, **34 of 38 obligations
> are in a control-failure state** — which is the correct and honest reading for a programme at W0,
> **provided the reading is published rather than smoothed**. `GV-009` wave gates are where it stops
> being acceptable.

### 7.4 The four with evidence today

| ID | Evidence that exists |
|---|---|
| `CR-13`, `CR-14` | **This document and `SC-007`** — the design is evidenced even where the build is not |
| `CR-27` | **`SC-003` exists** — the first DPIA in the programme's history |
| `CR-32` | **`M06` rebased on r2, and `SC-006` supplies the programme** — `H-01`'s substantive remediation is evidenced |

---

## 8. Verification Procedure

**This is the `00-06` §9 control.** It is a procedure, not an intention.

| # | Step | Who | When |
|---|---|---|---|
| `VP-1` | **Re-verify every `ST-` and `SD-` row**: status, supersession, amendment, withdrawal | Legal (statutes), Security Lead (standards) | **Quarterly and at every wave gate** |
| `VP-2` | Update `verified_on` and the source class. **A row not re-verified in a cycle is marked unverified**, not left silently stale | as above | `VP-1` cadence |
| `VP-3` | **Sweep the estate** for citations of any ❌ row — `grep` across all five repositories | Enterprise Architecture | With `VP-1` |
| `VP-4` | A status change triggers an **impact assessment within 30 days** across every consuming document | Security Lead | On change |
| `VP-5` | **A superseded citation found in a live document is a finding**, raised in the current audit, not noted for later | Auditor | On discovery |
| `VP-6` | `HZ-` horizons are reviewed for proximity; one inside 24 months becomes a **dated action with an owner** | CDO with CTO | `VP-1` cadence |
| `VP-7` | Results are **`GV-009` wave-gate evidence** | CDO | Per gate |

**What a failed verification triggers:**

| Outcome | Action |
|---|---|
| Instrument repealed or standard withdrawn | `VP-4` impact assessment; `VP-3` sweep; update every consuming document; **raise a finding** |
| New instrument in force not in the register | Register it; assess whether it creates a new `CR-` obligation; escalate if it does |
| A deadline becomes prescribed (`HZ-05`) | **Replace the planning assumption, do not inherit it** (`OP-004` `RN-03`) |
| A `P2` claim becomes verifiable as `P1` | Upgrade the source class; **`SC-003` determinations conditional on `G6` may then be confirmed** |

---

## 9. Escalation to `GV-005`

| ID | Risk | Rating | Owner | Trigger |
|---|---|:--:|---|---|
| `RSK-SC-06` | **No CDO appointed** (`CR-09`) — the DPIA cannot be signed, the Authority has no named contact, and `NFR-096` is unmet as enforcement approaches | **Critical** | Board | `HZ-01` — ~13 May 2027 |
| `RSK-SC-07` | **CII status undetermined** (`CR-16`) — an unknown, uncosted obligation set including an own SOC and CIRT | **High** | Legal/CTO | Any NCSA enquiry; W2 gate |
| `RSK-SC-08` | **Sub-processor flow-down unevidenced** (`CR-12`) — `NFR-098` makes a processor's processing the company's own | **High** | CDO | First external portal go-live |
| `RSK-SC-09` | **Breach-notification period unknown** (`CR-25`, `HZ-05`) — the programme plans to 72 hours with no legal basis | **High** | Legal | Any personal-data breach |
| `RSK-SC-10` | **Cryptographic deprecation horizon** (`CR-31`, `HZ-02`/`HZ-03`) — `M06` certificate and `LG-019` signature defensibility past 2030 | Medium | CTO | W4 review |

---

## 10. Disclosure Prohibitions

`CR-R7`. Claims the programme may **not** make, each with the document that establishes why. These
matter because they appear in tender responses, client assurance packs and certificates — the
places where an overstatement becomes a misrepresentation.

| # | May **not** be claimed | Because | Established by |
|---|---|---|---|
| `DP-1` | **ISO/IEC 27001 certification** | The company does not hold a certificate. `NFR-025` requires *alignment*; `NFR-089` requires *readiness* | `LG-021` §4.1.4 (`CS3`, `O-03`) |
| `DP-2` | **FIPS 140-3 validation of 1000FiX's own cryptography** | No validated module is budgeted (`SEC-CON-03`) | `SC-006` §3.5 |
| `DP-3` | **"Zero-trust architecture"** without the tenet decomposition | 4 adopted, 1 partial, **2 deferred** | `SC-001` §10 `SEC-ZT-1` |
| `DP-4` | **Compliance with the PDPA 2026** | Sixteen conformance elements are unevidenced; the DPIA is unsigned | `SC-003` §11; `SC-007` §11 |
| `DP-5` | **Data is unrecoverable** (destruction certificates) without naming technique and verification | An unqualified absolute is what a reviewer attacks first | `SC-006` `CN-4` |
| `DP-6` | **A residency conformance position** while `SC-007` §11 contains a blocking row | The statement is not published externally until then | `LG-012` §4.7.2 |

---

## 11. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | **Who is the Chief Data Officer?** (`CR-09`) | CEO/Board | **Now** | `SC-003` sign-off; NDMA contact; `RSK-SC-06` |
| `Q-02` | **Is 1000FiX critical information infrastructure?** (`CR-16`) | Legal | **W2** | `CR-17`, `CR-18`; cost and cadence |
| `Q-03` | **Is 1000FiX a significant data fiduciary?** | Legal | **Now** | Penalty band; `CR-09` trigger |
| `Q-04` | What is the prescribed breach-notification period and the "significant damage" threshold? (`HZ-05`) | Legal | W2 | `CR-25`; `SC-011` |
| `Q-05` | Does the NDMA publish a DPIA methodology this programme must conform to? (`HZ-06`) | Legal | W4 | `CR-27`; `SC-003` re-issue |
| `Q-06` | Who performs `VP-1` in the absence of a CDO and a Security Lead? | CTO | **Now** | The whole control |
| `Q-07` | Are the two live stale citations (`SD-32`, `SD-34`) swept? | Enterprise Architecture | **W1** | `SCA-03` |

---

## 12. Decisions Recorded

| # | Decision | Options | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `SC-008-D-01` | Relationship to `LG-024` | Merge · Duplicate · **Complement** | **Complement** | Two audiences, two questions. `LG-024` owns the external act; this owns the system control | §1.1 overlap rule; cross-reference discipline required |
| `SC-008-D-02` | Keep dead instruments in the register? | Delete · **Retain with ❌** | **Retain** | A citation of a repealed statute must resolve to a row saying *repealed*, not to nothing | 9 of 33 rows are ❌ — the register looks cluttered and is correct |
| `SC-008-D-03` | State the evidence gap? | Report control coverage · **Report evidence coverage** | **Evidence** | `CR-R2`: an obligation without evidence is a control failure. Reporting 31/38 control coverage would read as 82% compliant when 4/38 is evidenced | §7.3 publishes 34 in a control-failure state |
| `SC-008-D-04` | Notification deadlines | Adopt 72 h · **State it as a planning assumption** | **Planning assumption** | `OP-18`: the period is not law yet. `NC-3` | Readiness planned to the shortest applicable clock (`NC-4`) |
| `SC-008-D-05` | Disclosure prohibitions | Leave to reviewers · **Publish a list** | **Publish** | Overstatements happen in tender responses written under time pressure by people who never read `LG-021` §4.1.4 | §10 is six lines and prevents six categories of misrepresentation |

---

## 13. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | Every statute and standard the engineering estate cites is registered with a status | §4.1, §4.2 — 9 + 24 |
| `AC-02` | Every row carries `verified_on` and a source class | §4; `CR-R6` |
| `AC-03` | Superseded entries are retained and swept, not deleted | §4.3 — 9 ❌, 2 still live |
| `AC-04` | Every obligation has owner, control, evidence and state | §5 — 38 rows |
| `AC-05` | Obligations with no control are named | §7.2 — 4 |
| `AC-06` | Evidence coverage is reported, not control coverage | §7.3 |
| `AC-07` | All four notification clocks are dated and owned | §6 |
| `AC-08` | Deprecation horizons are dated actions | §4.4 — 6 |
| `AC-09` | The verification procedure has a cadence, an owner and a failure path | §8 |
| `AC-10` | Disclosure prohibitions are published | §10 — 6 |
| `AC-11` | Risks are escalated to `GV-005` | §9 — 5 |
| `AC-12` | The register does not duplicate `LG-024` | §1.1 |

---

## 14. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `SC-003` | Determinations become `CR-01`…`CR-08`, `CR-27` |
| Upstream | `SC-006` §2.4 | The standards currency table this register absorbs and extends |
| Upstream | `SC-007` §3 | Residency obligations `CR-13`…`CR-15` |
| Downstream | **Every `SC-` document** | `VP-4` impact assessment propagates status changes |
| Downstream | `M60` | `FR-GRC-023`…`027` obligation register; `FR-GRC-033` processing records |
| Downstream | `SC-011` | §6 clocks |
| Downstream | `GV-005`, `GV-008`, `GV-009` | §9 risks; `CR-17` cost; gate evidence |
| Downstream | `CO-003` | §10 disclosure prohibitions bind tender responses |
| Lateral | `../../project_content/10_Legal_Policy_and_Compliance/LG-024_*.md` | The business-side register this complements |
| Lateral | `../../project_content/10_Legal_Policy_and_Compliance/LG-021_*.md` `IS-13` | Compliance and assurance policy |

---

## 15. References

**Within this repository**
`../PGD-000_*.md` · `./_CATEGORY_OVERVIEW.md` · `./SC-001` … `./SC-011` ·
`../00_Programme_Governance_and_Control/GV-005_*.md`, `GV-009_*.md`, `GV-010_*.md`

**Workspace**
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_*.md` §6 ·
`../../1000fix_ERP_Module/00_Governance_and_Charter/00-06_*.md` §9 — **the control this implements** ·
`../../1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M60_*.md` ·
`../../project_content/10_Legal_Policy_and_Compliance/LG-021_*.md`, `LG-024_*.md` ·
`../../project_content/_AUDIT/AUDIT-017_*.md` (`OP-18`)

**External** — every instrument and standard in §4.1 and §4.2, each with its own status and
`verified_on: 2026-08-18`. **Source classes: `P2` for all statutory content, `V` for standards
status.**

---

## 16. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. **Implements the "regulatory currency review" control proposed in `00-06` §9 and never built.** 9 statutes and 36 standards rows registered with status and verification date; **10 superseded entries retained and swept, 2 found still live**; 38 engineering obligations with owner, control, evidence and state; four notification clocks dated; six disclosure prohibitions published | *Pending — no constituted body (`PGD-A2-25`)* |

---

*`SC-008` · Category 05 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
