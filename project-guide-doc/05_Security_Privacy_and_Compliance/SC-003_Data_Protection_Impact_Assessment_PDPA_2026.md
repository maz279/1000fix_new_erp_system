---
id: SC-003
title: Data Protection Impact Assessment (DPIA) — Personal Data Protection Act 2026
category: 05 — Security, Privacy & Compliance
code: SC
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Chief Data Officer (unappointed — NFR-096; see §12 Q-01)
approver: Data Protection Forum (constituted under GV-002), countersigned by Legal Counsel
standards_basis: >
  ISO/IEC 29134:2023 (Guidelines for privacy impact assessment — supersedes :2017) ·
  ISO/IEC 27701:2025 (PIMS, standalone edition) · ISO/IEC 29100:2024 (privacy framework) ·
  Personal Data Protection Act 2026 (Law 63 of 2026), Bangladesh · ISO/IEC 27005:2022 (risk method)
traces_to: >
  PGD-000 SC-003 · 05-06 §6.3 NFR-090…NFR-099 · LG-008 P-01…P-20 · LG-009 RC-01…RC-23 ·
  LG-010 · LG-012 · M33 BRU-CPM-06…16 · M60 FR-GRC-033…037 · M29 FR-SEC-040…052 ·
  audit findings C-04b, HC-01, OP-18, OP-19
depends_on: SC-001 (controls) · SC-002 (§10 privacy threats) · DA-002 (PII flags) · SC-007 (residency)
verified_on: 2026-08-18
priority: P0
needed_by: Now
enumeration_timestamp: 2026-08-18 13:25 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# SC-003 — Data Protection Impact Assessment (DPIA)
# Personal Data Protection Act 2026 (Law 63 of 2026), Bangladesh

### Category 05 · Code `SC` · ISO/IEC 29134:2023 · ISO/IEC 27701:2025

---

> **Before writing, read this.**
>
> 1. **`PG-01` Register-first.** This document's row exists in `PGD-000` Category 05 as `SC-003`.
> 2. **`PG-03` Count, do not consult.** Estate figures counted at **2026-08-18 13:25 (+06)**.
> 3. **`PG-06` Cite standards.** §2.1. **ISO/IEC 29134:2017 is withdrawn; :2023 is used.**
> 4. **`PG-M4` Verify citations.** Every statutory claim carries `verified_on: 2026-08-18` and a
>    **source class** under §2.3 — because the enacted instrument has not been read line by line,
>    and a DPIA that overstates its own evidentiary basis is worse than no DPIA.

---

## 1. Purpose

This is the **statutory assessment of high-risk processing** for the 1000FiX ERP System: what
personal data is processed, for what purposes, on what lawful basis, whether the processing is
necessary and proportionate, what risk it creates **for the individuals whose data it is**, what
reduces that risk, and what risk remains after everything reasonable has been done.

It exists because **the workspace contains no assessment of any kind**. Counted at 13:25 (+06):
"DPIA" appears **17 times across 7 files** outside `project-guide-doc/` — in the RFP, a
field-disclosure register, a glossary, a decision log, an ownership directory, an audit report and
the content master index. **Six consumers reference it. Zero producers exist.** Audit `C-04b`
records the wider position: the repository made *"no reference at all"* to the governing statute
until `05-06` §6.3 was written.

Three things make this urgent rather than important:

1. **Enforcement lands inside the build.** The PDPA 2026 was enacted April 2026; its complaint and
   enforcement mechanisms activate around **13 May 2027 — inside Wave 4**. Penalty exposure is up
   to **BDT 25 lakh**, and **BDT 50 lakh** for a significant data fiduciary, with additional fines
   for repetition.
2. **A Wave 2 activity has no confirmed lawful basis.** `AUDIT-010` `HC-01` (Critical) records that
   customer-transcript mining is scheduled at W2 and *"three files assume"* a basis that has never
   been confirmed. `LG-008` marks purpose `P-14` **provisional and not operative** (`PI-03`). This
   DPIA is what makes that determination.
3. **Four processing operations independently trigger an assessment** — biometric attendance, NID
   and identity-document capture, KYC with criminal-record checks, and recovered customer data held
   in custody. Any one would require a DPIA; the programme has all four and no assessment.

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | The **processing inventory** — 20 purposes `P-01`…`P-20` reconciled against `LG-008` §4.2 |
| 2 | **Threshold assessment** — which purposes require a DPIA, applying stated criteria rather than intuition |
| 3 | **Ten full assessments** `DPIA-01`…`DPIA-10` for the high-risk operations |
| 4 | **Necessity and proportionality** for each — including the less-intrusive alternatives considered and rejected |
| 5 | **Privacy risk register** `PR-01`…`PR-38` — risk **to data subjects**, not to the company |
| 6 | **Risk treatment** mapped to `SC-001` controls, with residual risk stated after treatment |
| 7 | **Data-subject rights realisability** — whether each right can actually be executed, per purpose |
| 8 | **Children's data** — the under-18 population and the `PN10` age-gate determination |
| 9 | **The `P-14` determination** — the answer `HC-01` requires before W2 |
| 10 | **Consultation record** and the **sign-off** the statute requires |
| 11 | **Review triggers** — when this assessment is re-run |

**Explicitly out of scope:**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| Security threats to the system | `SC-002` | A threat model asks *how is it attacked*; a DPIA asks *what harm reaches a person*. `SC-002` §10 covers the four privacy harms that are system properties |
| Residency mechanism, transfer register, Authority notification | `SC-007` | This document assesses **whether** a transfer is proportionate; `SC-007` builds the gate |
| The obligations register itself | `SC-008` | This document assesses processing; `SC-008` tracks obligations to evidence |
| Notice wording, consent copy, DSR response templates | `LG-008`, `LG-010` | Content, in Bengali and English. This document assesses whether the notice **discharges** `NFR-092` |
| Retention periods | `LG-009` | Referenced, never restated (`CP-01`) |
| Breach notification procedure | `SC-011` | This document assesses breach **impact on subjects**; `SC-011` runs the response |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| **Chief Data Officer / DPO** | The assessment of record; the artefact the Authority asks for |
| **Legal Counsel** | §3.4 lawful-basis determinations; §6 `DPIA-06` the `P-14` ruling |
| **Design Authority** | §7 treatments that are **design constraints**, not policy statements |
| **Developers** | §7 — the privacy controls that must be built, and when |
| **National Data Management Authority** | The whole document. Written to be read by a regulator, not around one |
| **Enterprise clients and brand partners** | §8 residual risk; §9 rights realisability |

---

## 2. Method and Basis

### 2.1 Standards conformance

| Standard | How this document conforms | Departure and rationale |
|---|---|---|
| **ISO/IEC 29134:2023** *(Edition 2; **:2017 withdrawn**; verified 2026-08-18)* | The report structure follows the standard: scope (§1), privacy requirements (§3), processing description (§4), threshold (§5), necessity and proportionality (§6), risk identification/analysis/evaluation (§7), treatment (§7), residual risk and conclusion (§8), consultation (§10), sign-off (§11), follow-up (§13) | 29134 assumes a defined organisational PIA programme. **1000FiX has none, and no CDO** (`NFR-096`). §11 records the sign-off the standard requires **and that it cannot presently be given** |
| **ISO/IEC 27701:2025** *(standalone edition, published 14 October 2025; **replaces :2019**; verified 2026-08-18)* | PIMS controls referenced for controller obligations; §7 treatments map to them | **The 2025 edition is standalone** — it no longer requires ISO/IEC 27001 as a base. This materially lowers the cost of a future PIMS certification and is recorded as an opportunity in §13, not claimed as a position |
| **ISO/IEC 29100:2024** | The eleven privacy principles are the assessment lens in §6 | — |
| **PDPA 2026 (Law 63 of 2026)** | §3.1 restates the obligations; every assessment in §6 is tested against them | **Source class `P2`** — see §2.3. The enacted Bengali instrument has not been read clause by clause |
| **ISO/IEC 27005:2022** | §7 uses the same likelihood/impact anchors as `SC-002` §4 **with the impact scale re-anchored on harm to individuals** | A security impact scale measures loss to the organisation. Reusing it unmodified is the most common DPIA error, and it systematically under-rates distress, discrimination and loss of control |

### 2.2 The impact scale is re-anchored — this is the central methodological point

> **A DPIA that scores impact on organisational loss is not a DPIA.** The subject of the assessment
> is the individual. `SC-002` §4.2's top anchor is *"statutory penalty exposure BDT 25–50 lakh"* —
> a loss to 1000FiX. Here, the top anchor is what happens **to a person**.

| Score | **Harm to the data subject** | Worked example from this estate |
|---|---|---|
| **5 Severe** | Irreversible harm; identity theft; physical danger; loss of employment or liberty; harm that cannot be undone by any action the company can take | A leaked **biometric template** — a fingerprint cannot be reissued. A leaked **criminal-record check** on a seller. Recovered data containing a customer's private material disclosed |
| **4 Major** | Significant, lasting harm requiring the individual to take remedial action | **NID or passport number** exposed → identity-fraud exposure the person must monitor for years. Bank details exposed. Salary disclosed to colleagues |
| **3 Moderate** | Distress, embarrassment or inconvenience; the individual must act but recovery is achievable | Service history disclosed to a neighbour (`AB-09`). Contact details sold on. An erasure request refused without a stated basis |
| **2 Minor** | Nuisance; a right delayed rather than denied | A DSR answered late. Marketing received after withdrawal |
| **1 Negligible** | No material effect on the individual | An internal metric derived from aggregate data |

**Likelihood anchors are inherited unchanged from `SC-002` §4.1**, so that a risk appearing in both
registers carries a comparable likelihood and only its impact differs. This is deliberate: it makes
the *divergence* visible. `TH-088` (biometric exfiltration) is rated `L2 × I5` in both — but the
`I5` means different things, and §7 records both.

### 2.3 Source classes — the honesty constraint

`LG-008` established the convention and it is adopted here. **The enacted PDPA 2026 instrument has
not been read clause by clause by the author of this document.** The statutory content below rests
on published legal analysis and on `05-06` §6.3, which itself carries a `verified_on` date.

| Class | Meaning | Used for |
|---|---|---|
| **`P1`** | The enacted instrument, read directly | **Nothing in this document.** No clause citation of the form "s.14(2)" appears, because none can be supported |
| **`P2`** | Published legal analysis of the enacted instrument, cross-checked across independent sources | Every statutory obligation in §3.1 |
| **`P3`** | Single-source commentary | Used only where flagged; **may not be the sole basis of a statutory claim** |

> **`SC-003-CL-01`. Every determination in §6 is therefore conditional on `G6` verification against
> the enacted instrument by Legal Counsel.** This is stated once here and not repeated per finding.
> It is not a weakening of the assessment — it is the difference between an assessment a regulator
> can rely on and one that would collapse under a single question. `OP-18` records the same
> discipline for the breach-notification clock: *"until then, no document may state a notification
> deadline as fact."*

### 2.4 Enumeration

| # | Figure | **Counted 2026-08-18 13:25 (+06)** | Published elsewhere | Disposition |
|---|---|---:|---|---|
| 1 | Occurrences of "DPIA" outside `project-guide-doc/` | **17 in 7 files** | "four" (`PGD-000`) | Published figure **4.25× low**; none is an assessment. `SC-001` `SCA-01` |
| 2 | Processing purposes registered | **20** (`P-01`…`P-20`) | 20 | ✓ |
| 3 | Purposes crossing the DPIA threshold | **10** | — | §5 |
| 4 | Purposes with an **unconfirmed** lawful basis | **1** (`P-14`) | 1 (`PI-03`) | ✓ — and it is a W2 activity |
| 5 | Residency-classified field classes | **7** authoritative + **2** proposed | 7 (`05-06` §6.4) + 2 (`LG-012` `RD1`) | §6 `DPIA-09` assesses the two proposed |
| 6 | `S3` restricted fields | **9** | 9 (`05-02` §10) | ✓ |
| 7 | Data-subject populations | **6** | — | §4.2 |
| 8 | External recipients / processors | **47** integration destinations | 47 | **0 of 8 anticipated transfers registered**; sub-processor register does not exist |
| 9 | Privacy risks identified | **38** | — | §7 |
| 10 | Risks rated Severe (I5) | **9** | — | §7.6 |

---

## 3. Privacy Requirements

### 3.1 Statutory obligations — PDPA 2026

Source class `P2` throughout; verified 2026-08-18.

| # | Obligation | Statement | Realised by | State today |
|---|---|---|---|---|
| `O-1` | **Lawful basis** | Personal data is processed only on consent or a stated legitimate ground, recorded per purpose | `NFR-090`; `M33` | ◐ 19 of 20 purposes have a stated basis; **`P-14` does not** |
| `O-2` | **Consent standard** | Clear, explicit, specific and freely given, with a **heightened "specific consent"** standard for sensitive data unless a legitimate ground applies; easily revocable | `NFR-091`; `LG-008` §4.3 | ◐ Consent register specified; not built |
| `O-3` | **Transparency notice** | Issued before or during processing, stating **data categories, purposes, risks, retention, third-party transfers and the withdrawal procedure** | `NFR-092`; `LG-008` | ◐ Drafted. **The `Risks` column is the element the programme had never drafted for** (`LG-008` `O-04`) |
| `O-4` | **Access and portability** | Data summaries and transfer capability | `NFR-093`; `LG-010` | ◐ `P-17` DSR orchestrator specified, not built |
| `O-5` | **Rectification** | Correct inaccurate data and **notify recipients within 30 days** | `NFR-093`; `BRU-CPM-10` | ◐ The **only** period the statute states explicitly |
| `O-6` | **Erasure** | On purpose cessation, consent withdrawal, unlawful processing, or legal requirement | `NFR-093`; `BRU-CPM-11` | ◐ With statutory-retention override |
| `O-7` | **Withdrawal** | Simple revocation at any time, across every channel | `NFR-093`; `BRU-CPM-09` | ◐ |
| `O-8` | **Breach notification** | Notify the **National Data Management Authority** where a breach is likely to cause **significant damage**, within the timeframe prescribed by regulations | `NFR-094`; `SC-011` | ⚠ **The period is not yet prescribed** (`OP-18`). `OP-004` `RN-03` uses a **72-hour planning assumption**, marked as such |
| `O-9` | **Processing records** | Register and preserve records of processed personal data for **at least 5 years** | `NFR-095`; `FR-GRC-033` | ◐ |
| `O-10` | **Chief Data Officer** | A **significant** data controller appoints a qualified CDO as the primary Authority contact | `NFR-096` | ✖ **Not appointed.** §12 `Q-01` |
| `O-11` | **Security measures** | Technical and organisational measures proportionate to risk | `NFR-097`; `SC-001` | ◐ 68 controls specified; 19 do not exist |
| `O-12` | **Processor obligations** | A processor's processing is the controller's own; equivalent obligations flow to every processor and sub-processor by contract | `NFR-098` | ✖ **Sub-processor register does not exist** (`LG-012` `O-05`) |
| `O-13` | **Sensitive-data transfer** | Restrict **large-scale transfer of Sensitive Personally Identifiable Data** — government unique identifiers (NID, passport, TIN), biometric identifiers, genetic information, criminal records — notify the Authority of cross-border transfers and **disclose the safeguards applied** | `NFR-099`, `NFR-086b`; `SC-007` | ◐ Mechanism designed; **0 of 8 transfers registered** |
| `O-14` | **Children** | Processing a person **under 18** requires **verifiable parental consent** | `BRU-CPM-16`; `LG-008` `CN-09` | ⚠ Consent type registered; **the age-gate mechanism is undetermined** (`PN10`). §6 `DPIA-10` |
| `O-15` | **DPIA** | Privacy impact assessment referenced within the Authority's Standard Operating Procedures | `FR-GRC-037`; **this document** | ✖ **This document is the first.** The Authority's SOP methodology is not yet published — §13 `RV-05` |

> **`SC-003-F-01`. `O-13` deserves separate emphasis because it is the obligation the architecture
> was redesigned around.** `05-06` §6.4 replaced a single-region topology with split residency
> precisely because of it (`C-05`). **Published analysis is consistent that the Act imposes no
> general data-localisation mandate** — it restricts transfer of *sensitive* categories and requires
> notification and safeguard disclosure. That distinction matters commercially: it means the
> regional store is lawful for the great majority of the estate, and `Z4` is a targeted control
> rather than a wholesale repatriation. Source class `P2`; `G6` verification required before this
> is relied on in a tender or a client assurance pack.

### 3.2 Other applicable requirements

| Source | Requirement | Effect here |
|---|---|---|
| **Cyber Security Ordinance 2025** (Ordinance No. 25 of 2025; gazetted 21 May 2025; **in force**) | Establishes the National Cyber Security Agency; regulates **critical information infrastructure**; a declared CII must operate its **own CERT/CIRT and SOC with quarterly reports** to the NCSA | **A second regulator and a second notification clock.** `LG-021` §4.10.2(b) records it as `CS1`. Whether 1000FiX is CII is `SC-001` `Q-04` |
| ISO 9001:2015 (`NFR-024`) | Audit trail and documentation | Retention interacts with erasure — `O-6` override |
| Bangladesh Labour Act 2006 | Employment records | `P-10` retention override |
| VAT & SD Act 2012; NBR | Tax records, TIN on statutory outputs | **`P-16` overrides erasure**, and the notice must say so |
| Contractual — 17+ brand partners, corporate clients | Warranty evidence packs; audit rights | `P-07` cross-border transfer, currently **unregistered** |

### 3.3 The four DPIA triggers present in this system

Each independently requires an assessment. The programme has all four.

| # | Trigger | Present as | Why it triggers |
|---|---|---|---|
| `TR-1` | **Large-scale processing of sensitive personal data** | NID, passport, TIN, biometric templates, KYC, criminal records | Named in `O-13` as the categories the statute singles out |
| `TR-2` | **Systematic monitoring** | Biometric attendance (500+ staff); technician GPS at 800 points/min; call recording; privileged session recording | Continuous observation of identified individuals |
| `TR-3` | **Data of unknown category held in custody** | `M06` recovered customer data | **The only asset class whose content classification is unknown by design.** It may contain any category, including health or criminal data |
| `TR-4` | **Novel or repurposed use** | `P-14` transcript mining for content authoring and model training | Reuse for a purpose other than that of collection, at scale, feeding an automated system |

### 3.4 Lawful basis by purpose

Reproduced from `LG-008` §4.2 as the assessment input. **Where this assessment disagrees with the
registered basis, the disagreement is stated in §6 and escalated — it is not silently corrected**,
because `LG-008` is the system of record for the notice and `FR-GRC-033` for the processing record.

| Basis | Purposes | Count | Assessment note |
|---|---|---:|---|
| Contract performance | `P-01`, `P-04`, `P-06`, `P-07`, `P-08`, `P-09`, `P-11`, `P-12`, `P-13` | 9 | `P-12` call **recording** is assessed in `DPIA-05` as exceeding what contract performance supports without separate notice |
| Legal obligation | `P-02`, `P-03`, `P-16`, `P-17`, `P-19` | 5 | Strongest basis; least discretion |
| Consent | `P-05`, `P-20` | 2 | Withdrawable; must not be bundled |
| Employment / social-security duty | `P-10` | 1 | **Biometric element assessed separately** — `DPIA-04` |
| Legitimate ground | `P-15`, `P-18` | 2 | Requires a balancing record the estate does not hold — §6 `DPIA-08` |
| **Unconfirmed** | **`P-14`** | **1** | **`DPIA-06` — the determination `HC-01` requires** |

---

## 4. Description of the Processing

### 4.1 What is processed, at what scale

| Category | Examples | `S` class | `Z4`? | Volume |
|---|---|:--:|:--:|---|
| Identity and contact | Name, phone, address, email | `S2` | No | 250,000+ customers/month |
| **Government identifiers** | **NID, passport, TIN** | **`S3`** | **Yes** | Per verification event; all 800+ staff |
| **Biometric** | **Attendance template** | **`S3`** | **Yes** | **500+ employees, daily** |
| Financial | Bank account, payment token, credit limit, payout detail | `S3`/`S2` | Proposed | All staff; 500–2,000 sellers |
| Employment | Salary, payslip, attendance, performance, discipline, medical | `S3`/`S2` | Proposed | 800+ |
| Device and service | Device identity, fault, diagnosis, repair notes, **evidence photographs** | `S1`/`S2` | No | 5M service orders/year at steady state |
| **Recovered customer data** | **Content of unknown classification** | **`S3`** | **Yes** | Per `M06` case |
| **KYC and vetting** | **Seller KYC documents, criminal-record checks** | **`S3`** | **Yes** | 500–2,000 sellers |
| Communications | Call recordings, chat transcripts, contact dispositions | `S3`/`S2` | **No — regional** | Contact centre volume |
| Location | Technician and rider GPS history | `S2` | No | **800 points/minute** |
| Security | Access logs, audit entries, security events | `S3` (`T5`) | No | ~50M audit entries/year at W8 |

### 4.2 Whose data — six populations, with materially different power positions

> **The power position is not decoration.** It determines whether consent can be freely given —
> `O-2`'s standard — and it is why the same processing is proportionate for one population and not
> for another.

| # | Population | Size | Relationship | Power position | Consequence for this assessment |
|---|---|---:|---|---|---|
| `DS-1` | Individual customers | 250,000+/mo | Consumer contract | **Balanced** — can decline and go elsewhere | Consent is meaningful; withdrawal must be real |
| `DS-2` | Corporate portal users | 500–2,000 | Employees of a client | **Weak** — their employer chose the system, not them | They cannot decline. Notice must reach **them**, not only their employer |
| `DS-3` | **Employees** | 800+ | Employment | **Weakest** | **Consent is generally not a valid basis in an employment relationship.** `DPIA-04` turns on this |
| `DS-4` | Marketplace sellers | 500–2,000 | Commercial, dependent | **Weak** — livelihood dependency | Vetting is proportionate; scope creep is not |
| `DS-5` | Vendors, partners, couriers, auditors | 1,000–3,000 | Commercial | Balanced | Minimum-necessary applies (`EA-07`) |
| `DS-6` | **`M06` data-recovery customers** | Per case | Custody of their private material | **Highly exposed** | `TR-3`. Highest per-subject impact in the estate |

### 4.3 Data flows that leave the immediate processing context

| # | Flow | Recipient | Basis | Registered? |
|---|---|---|---|---|
| `F-1` | Warranty claim + evidence to overseas brand partners | 17+ brands | `P-07` contract | **No** (`TR-02` unregistered) |
| `F-2` | Notification delivery | SMS/WhatsApp/email/push providers | `P-04` | **No** (`TR-03`) |
| `F-3` | Payment tokens | Gateways | `P-03` | **No** (`TR-04`) |
| `F-4` | Third-party portal tags | Analytics, chat, video, advertising | `P-01`, `P-05` | **No** (`TR-05`) — `SC-002` `TH-059` |
| `F-5` | AI model inference | Model service | `P-13` | **No** (`TR-06`) |
| `F-6` | **Remote support by an overseas engineer** | Vendors | Platform support | **No** (`TR-07`) — **a remote view is a transfer** |
| `F-7` | Cloud management-plane metadata | Provider | Operation | **No** (`TR-08`) |
| `F-8` | Awarded-job contact details to a marketplace seller | 500–2,000 sellers | `P-01` | Internal; `EA-04` time-bounded |
| `F-9` | Statutory filings | NBR and regulators in `LG-024` | `P-16` legal obligation | Statutory; not discretionary |

> **`SC-003-F-02`. Eight anticipated transfers, zero registered, and `NFR-086b` blocks a
> residency-classified transfer until a notification record exists.** The architecture therefore
> **fails closed on all eight** — which is correct behaviour and a **W1 go-live blocker for any
> portal that depends on `F-2` or `F-4`**. Owner: CDO with Legal. Escalated to `GV-005` as
> `RSK-SC-05` by `SC-002` §11.

---

## 5. Threshold Assessment

Applying the `TR-1`…`TR-4` triggers of §3.3 plus scale, vulnerability of the population, and
whether the individual can reasonably avoid the processing.

| Purpose | Sensitive? | Systematic? | Vulnerable population? | Avoidable? | **DPIA?** |
|---|:--:|:--:|:--:|:--:|:--:|
| `P-01` provide the service | — | — | — | Yes | No — but see `DPIA-07` (photographs) |
| **`P-02` verify identity (NID)** | **Yes** | — | — | No | **`DPIA-01`** |
| `P-03` payment and tax invoice | Partial (TIN) | — | — | No | Covered by `DPIA-01` |
| `P-04` service notifications | — | — | — | No | No |
| `P-05` marketing | — | — | — | Yes | No |
| `P-06` loyalty and referral | — | — | — | Yes | No |
| **`P-07` warranty claim to brand** | — | — | — | No | **`DPIA-03`** (cross-border) |
| `P-08` contract and SLA | — | — | `DS-2` | No | No |
| **`P-09` data recovery and destruction** | **Unknown category** | — | **`DS-6`** | No | **`DPIA-02`** |
| **`P-10` employ and pay (biometric)** | **Yes** | **Yes** | **`DS-3`** | **No** | **`DPIA-04`** |
| **`P-11` qualify supplier/seller (KYC, criminal)** | **Yes** | — | **`DS-4`** | No | **`DPIA-09`** |
| **`P-12` handle contact (recording, transcript)** | — | **Yes** | — | Partly | **`DPIA-05`** |
| `P-13` AI assistant | — | — | — | Partly | Covered by `DPIA-06` |
| **`P-14` improve service / train models** | — | **Yes** | — | **No** | **`DPIA-06`** — the `HC-01` determination |
| **`P-15` fraud prevention** | — | **Yes** | — | No | **`DPIA-08`** |
| `P-16` statutory obligations | Partial | — | — | No | No — no discretion exists |
| `P-17` respond to a rights request | — | — | — | No | No — but `AB-19` abuse assessed in `PR-31` |
| `P-18` complaint / dispute | — | — | — | No | No |
| **`P-19` secure the platform and audit** | — | **Yes** | **`DS-3`** | **No** | **`DPIA-08`** (with `P-15`) |
| `P-20` recruit | — | — | Applicants | Yes | No |
| — | — | — | — | — | **`DPIA-07`** evidence photographs |
| — | — | — | — | — | **`DPIA-10`** children under 18 |

**Ten assessments.** Regenerated by counting the `DPIA-` identifiers in the right-hand column:
`DPIA-01`…`DPIA-10` = **10** ✓.

---

## 6. The Ten Assessments

Each: **what**, **why it is necessary**, **is it proportionate**, **less-intrusive alternatives
considered**, **determination**.

### `DPIA-01` — Government identifier capture (NID, passport, TIN) · `P-02`, `P-03`

| | |
|---|---|
| **Processing** | Capture and retain NID or equivalent for identity verification at device release, high-value cash receipt and rights requests; TIN where a tax invoice requires it |
| **Populations** | `DS-1`, `DS-3`, `DS-4` |
| **Necessity** | **Established.** Device release without verification is a legal exposure to the true owner; high-value cash receipt is a statutory AML/tax control; a rights request must verify the requester or it becomes `AB-19`. TIN on a Mushak 6.3 invoice is a statutory content requirement |
| **Proportionality** | **Proportionate with three constraints.** (a) capture at the **verification event**, not at registration — the estate must not accumulate NIDs from every customer who books a repair; (b) `Z4`-resident, field-encrypted, `T5` allow-listed, step-up authenticated, every access logged; (c) visible to finance and compliance roles only |
| **Less-intrusive alternatives considered** | **Hash-only storage** — rejected: the number must be re-presentable for a statutory filing and for dispute evidence. **Last-four retention** — rejected for the same reason; retained as a **display** representation. **Sight-and-do-not-store** — **accepted for device release below the value threshold**, and this is the change this assessment makes |
| **Residual risk** | `PR-01` identity fraud following disclosure (`I5`); `PR-02` over-collection at registration (`I4`) |
| **Determination** | **Proceed, amended.** `SC-003-A-01`: adopt a **sight-and-verify-without-storing** path for device release below the `SP-004` threshold, so that the stored NID population is a fraction of the customer base rather than all of it. Raise to `M33` and `M04` |

### `DPIA-02` — Recovered customer data in custody · `P-09`

| | |
|---|---|
| **Processing** | Hold, index, recover and purge a customer's own data during an `M06` case |
| **Population** | `DS-6` — the most exposed population in the estate |
| **Necessity** | **Established and inseparable from the service.** Data recovery cannot be performed without access to the data being recovered |
| **Proportionality** | **Proportionate only under the existing control set, all of which is mandatory:** case-scoped access (`BRU-SEC-03`), **dual control** for secure-area media movement (`BRU-DTS-01`), per-access logging, `Z4` residency with **`BRU-DTS-16` prohibiting replication abroad**, per-case encryption keys (`BRU-DTS-05`), **purge by key destruction**, time-boxed retention with an automatic purge and certificate, and **`BRU-DTS-14`: never training data** |
| **Less-intrusive alternatives** | **Customer-side recovery** — not commercially viable and not what the service is. **Blind recovery without indexing** — technically infeasible for verification and for the customer's own file selection |
| **Residual risk** | `PR-05` insider browsing outside the case (`I5`, `AB-15`); `PR-06` retention beyond the agreed date (`I4`); `PR-07` **detectability** — an observer infers a named person is a recovery customer (`I4`, `SC-002` `TH-096`) |
| **Determination** | **Proceed.** `SC-003-A-02`: `PR-07` requires **metadata minimisation** in notifications and case references — a purpose no document currently states. Raise to `M06` and `OP-004` |

### `DPIA-03` — Cross-border warranty evidence to brand partners · `P-07`

| | |
|---|---|
| **Processing** | Device identity, diagnosis, **photographs**, parts, named technician and certification, purchase proof, sent to 17+ brand partners, many overseas |
| **Necessity** | **Established.** A claim without evidence is not a claim; the brand relationship is the commercial basis of the warranty business |
| **Proportionality** | **Proportionate for the claim payload; not yet demonstrable for the transfer.** `LG-008` `P-07` correctly states *"it does not disclose your National ID"* — the restricted-field prohibition (`RD-R10`) holds. But **`TR-02` is unregistered**, and `LG-005` §6.4 gates brand onboarding on it |
| **Less-intrusive alternatives** | **Pseudonymised claim reference** — partially adopted; brands need device identity, not customer identity, for most claim types. **This assessment finds the customer's name is not required for a warranty claim in the majority of cases** |
| **Residual risk** | `PR-09` unregistered transfer (`I3` to subjects, high to the company); `PR-10` **photographs incidentally showing the customer's home, screen or documents** (`I4`) |
| **Determination** | **Proceed, conditional.** `SC-003-A-03`: register `TR-02` before the next brand onboarding. `SC-003-A-04`: **default the claim payload to device-identified rather than customer-identified**, with customer identity included only where the brand's scheme requires it. Raise to `M09` |

### `DPIA-04` — Biometric attendance · `P-10`

**The highest-scrutiny assessment in this document.**

| | |
|---|---|
| **Processing** | Fingerprint or equivalent template captured for attendance across 500+ employees, daily |
| **Population** | `DS-3` employees — **the weakest power position in the estate** |
| **Necessity** | **Asserted, not established.** The stated need is accurate attendance across 51+ branches with shift work and a history of buddy-punching. **Accurate attendance is a legitimate need; biometric attendance is one of several ways to meet it** |
| **Proportionality** | ⚠ **Not demonstrated.** Three problems: (a) **consent is not a valid basis in an employment relationship** where refusal has employment consequences — the registered basis is "employment and social-security duties", which is stronger, but does not by itself make *biometric* processing necessary; (b) the harm is **irreversible** — a compromised template cannot be reissued (`I5`); (c) **no alternative was assessed** anywhere in the estate before the design was fixed |
| **Less-intrusive alternatives — which this assessment requires to be considered on the record** | **Card or fob + PIN**: buddy-punching remains possible. **Geofenced mobile check-in**: device-dependent; the technician population already carries devices. **Facial verification without template retention** (match-and-discard). **Biometric with on-device template storage** — the template never enters the estate at all. **Supervisor attestation** for small branches |
| **Existing mitigations** | Irreversible template, **never exported** (`05-02` §10); `Z4` resident; `S3` field-encrypted; deleted at termination (`LG-009` `RC-13`) |
| **Residual risk** | `PR-13` **template exfiltration — irreversible** (`L2 × I5` = **High**); `PR-14` function creep — attendance data used for performance or discipline (`I4`); `PR-15` **no genuine opt-out for an employee** (`I4`) |
| **Determination** | ⚠ **PROCEED ONLY IF `SC-003-A-05` COMPLETES.** Legal Counsel and the HR Director must record, **before W5 build**, (a) the ground relied on and why consent is not it, (b) why a less-intrusive alternative is insufficient, and (c) a **non-biometric alternative available to any employee on request, without detriment**. **Without (c) the processing should not proceed**, because a control the individual cannot refuse and cannot recover from requires the strongest possible justification. Raise to `M55`, `M21`, `GV-005` |

### `DPIA-05` — Call recording and contact transcripts · `P-12`

| | |
|---|---|
| **Processing** | Recording of calls; transcripts; dispositions; quality review |
| **Necessity** | **Established for quality assurance and dispute evidence**; `NFR-024` and ISO 9001 support it |
| **Proportionality** | **Proportionate for the primary purpose, with one gap.** The notice states *"calls may be recorded for quality and training. You are told at the start of the call"* — correct. **The gap is the secondary use**, which is `P-14` and is assessed separately |
| **Less-intrusive alternatives** | **Sampling rather than full recording** — rejected for dispute evidence, where the un-sampled call is the one in dispute. **Transcript-only, audio discarded** — **viable and not considered**; a transcript serves quality review and disposition analysis, and carries materially less biometric-adjacent risk than a voice recording |
| **Residual risk** | `PR-17` recordings accessed outside quality purpose (`I3`); `PR-18` **voice as a biometric identifier** — a recording is more than its words (`I4`) |
| **Determination** | **Proceed, amended.** `SC-003-A-06`: adopt **transcript-primary retention** with audio retained only for the shorter dispute window, and record the two periods separately in `LG-009` |

### `DPIA-06` — Reuse of transcripts for content authoring and model training · `P-14`

**This is the determination `AUDIT-010` `HC-01` requires before W2.**

| | |
|---|---|
| **Processing** | Anonymised transcripts, chat logs and search queries mined to build the `HC-015` FAQ bank (**W2**), the `HC-017` intent and utterance library (W6), and to improve models |
| **Necessity** | **Weak as framed.** The stated need is that FAQ items *"come from observed demand"* (`FQ-01`) and that Bengali utterances must be *collected from real users* (`IL-04`). Both are genuine quality needs. **Neither establishes that the corpus must be built from personal data**, as opposed to from aggregated dispositions, agent-authored summaries, or consented panels |
| **Proportionality** | ⚠ **Cannot be assessed, because two prerequisites do not exist.** (a) **No confirmed lawful basis** — `LG-008` marks `P-14` `PN5` UNCONFIRMED and `PI-03` renders it **not operative**. (b) **No anonymisation standard** — and `SC-002` `TH-092` finds the corpus **re-identifiable** through order references, device serials and rare fault text. *"Anonymised"* asserted is not anonymised demonstrated |
| **Less-intrusive alternatives** | **Disposition codes and volumes only** — sufficient for `FQ-01`'s observed-demand requirement, and it is **not personal data**. **Agent-authored summaries** — the agent writes what was asked, not what was said. **Explicit consented panel** for Bengali utterance collection. **Synthetic utterance generation reviewed by native speakers** — `IL-04` prohibits *translated* utterances, not *generated* ones |
| **Residual risk** | `PR-21` processing at scale on an unverified footing (`I4`); `PR-22` **re-identification of an anonymised corpus** (`I4`); `PR-23` **irreversibility** — a model trained on unlawfully processed data may not be remediable by deletion of the corpus (`I5`) |
| **Determination** | ⛔ **DO NOT PROCEED.** `P-14` remains **not operative**. Three conditions, all required before any transcript-derived work begins at W2 — `SC-003-A-07`: (1) Legal Counsel confirms the basis for **reuse** against the basis on which the data was collected; (2) an **anonymisation standard is published and tested**, not asserted, closing `TH-092`; (3) the **less-intrusive alternatives above are tried first** — specifically, `HC-015` is built from dispositions and agent summaries, and only escalates to transcripts if demonstrably insufficient. **`PR-23` is the reason this is a hard stop:** the remedy for unlawfully derived content is deletion, and the remedy for an unlawfully trained model may be retraining or retirement |

### `DPIA-07` — Evidence photographs · `P-01`

| | |
|---|---|
| **Processing** | Photographs at intake, during repair and at handover, across 5M service orders/year at steady state |
| **Necessity** | **Established.** Condition evidence protects both parties in a device-custody dispute |
| **Proportionality** | **Proportionate to the device; disproportionate to its surroundings.** `LG-008` `P-01` already discloses the risk honestly: *"photographs of a device may incidentally show your home or your data"*. **A disclosed risk is not a mitigated risk** |
| **Less-intrusive alternatives** | **Framing guidance and in-app capture guides** — cheap and unimplemented. **On-device redaction prompt** where a screen is visible. **`MM-002` redaction standard exists** and is not bound to the capture flow |
| **Residual risk** | `PR-25` incidental capture of a home interior, a screen, a document or a third party (`I3`); `PR-26` **a photograph of a powered-on device screen may capture the customer's own data** (`I4`) |
| **Determination** | **Proceed, amended.** `SC-003-A-08`: bind `MM-002` redaction to the `P02` technician capture flow and require **device-only framing**, with a screen-visible warning. Raise to `P02`, `M01`, `MM-002` |

### `DPIA-08` — Fraud detection, security monitoring and staff location · `P-15`, `P-19`

| | |
|---|---|
| **Processing** | Transaction patterns, claim history, device and IP signals; access logs and security events; **technician and rider GPS at 800 points/minute** |
| **Populations** | `DS-1`, `DS-3`, `DS-4` |
| **Necessity** | **Established for fraud and security.** `SOD-01`…`SOD-12` name real fraud paths; `NFR-097` requires security measures |
| **Proportionality** | **Proportionate for fraud and audit; not assessed for location.** GPS at 800 points/minute across a technician workforce is **continuous location monitoring of identified employees**, justified operationally by dispatch and ETA. **The operational justification is real; the retention is not bounded by it.** Dispatch needs current position; it does not need a year of history |
| **Existing safeguards** | `BRU-WTY-21`: a high fraud score triggers **human review, never automatic rejection** — this is a strong control and it is already specified. Audit entries are `T5` |
| **Less-intrusive alternatives** | **Short-horizon location retention** (operational window only) with aggregation thereafter. **Geofence events rather than continuous track** for compliance purposes |
| **Residual risk** | `PR-29` **location history reconstructs an employee's movements beyond the operational purpose** (`I3`, `SC-002` `TH-060`); `PR-30` legitimate-ground balancing **not recorded** for `P-15` and `P-18` (`I2` to subjects; an evidential gap for the company) |
| **Determination** | **Proceed, amended.** `SC-003-A-09`: set an explicit **operational retention horizon** for raw GPS in `LG-009`, with aggregation beyond it. `SC-003-A-10`: record the **legitimate-ground balancing test** for `P-15` and `P-18` — currently asserted, never documented |

### `DPIA-09` — Seller KYC and criminal-record checks · `P-11`

| | |
|---|---|
| **Processing** | Identity, trade licence, KYC documents, bank details, **criminal-record checks where a category requires** |
| **Population** | `DS-4` — livelihood-dependent |
| **Necessity** | **Established for KYC.** A marketplace admitting 500–2,000 sellers who enter customers' homes and handle their devices has a duty of care. **Criminal-record checks: necessary for a subset, not for all** |
| **Proportionality** | **Proportionate if scoped by category and time.** `LG-008` `PN8` already flags that criminal-record **lawfulness and retention** are unresolved. A criminal-record check retained indefinitely is not proportionate to a vetting decision made once |
| **Less-intrusive alternatives** | **Check-and-record-outcome-only** — retain the decision, not the record. **Category-scoped checks** — only for seller categories with in-home or high-value access |
| **Residual risk** | `PR-33` **criminal-record retention without a resolved basis** (`I5` — discrimination and livelihood harm); `PR-34` **`RD1`** — bank details and individual payroll are `S3` but **not residency-classified** (`I4`) |
| **Determination** | **Proceed, restricted.** `SC-003-A-11`: **criminal-record checks are category-scoped, outcome-retained and record-discarded** unless Legal establishes a basis for retention (`PN8`). `SC-003-A-12`: **this assessment supports `LG-012` `RD1`** — bank details and individual payroll of Bangladeshi individuals **should be residency-classified**. `SC-001-D-08` already provisions `Z4` for all nine `S3` classes so the change is a reclassification, not a migration |

### `DPIA-10` — Children under 18 · `O-14`

| | |
|---|---|
| **Processing** | Any purpose where the data subject is under 18 |
| **Necessity** | **The company does not target minors**, but at 250,000+ customers a month **it will inevitably process some** — a student booking a phone repair is the ordinary case |
| **Proportionality** | ⚠ **Undetermined, because the detection mechanism is undetermined.** `LG-008` `CN-09` registers parental consent as a consent type valid until the child reaches 18; `BRU-CPM-16` requires it. **`PN10` asks the operative question: does under-18 with verifiable parental consent require a hard age gate at registration, or is a declared-age model sufficient?** Until answered, the obligation has a rule and no trigger |
| **Less-intrusive alternatives** | **Declared age at registration** — low friction, weak verification. **Age gate with verification** — high friction across 250,000 registrations/month, and **collects more data from everyone to protect a minority**, which is itself a proportionality problem. **Risk-based**: no gate at registration; parental consent required at the point a **sensitive** processing operation arises |
| **Residual risk** | `PR-36` a minor's data processed without parental consent (`I4`); `PR-37` **an age gate collecting date of birth from every customer to catch a small minority** (`I3`) — the mitigation creating a new risk |
| **Determination** | **Proceed pending `SC-003-A-13`.** Legal to answer `PN10`. **This assessment's recommendation is the risk-based option**: no universal age gate, a declared-age field, and a **hard parental-consent requirement at any `S3` capture or financial action**. It meets `O-14` where the harm is real and avoids `PR-37` |

### 6.11 Summary of determinations

| Assessment | Determination | Actions |
|---|---|---|
| `DPIA-01` NID / TIN | **Proceed, amended** | `A-01` |
| `DPIA-02` Recovered data | **Proceed** | `A-02` |
| `DPIA-03` Brand transfer | **Proceed, conditional** | `A-03`, `A-04` |
| `DPIA-04` **Biometric** | ⚠ **Proceed only if `A-05` completes** | `A-05` |
| `DPIA-05` Call recording | **Proceed, amended** | `A-06` |
| `DPIA-06` **`P-14` transcript reuse** | ⛔ **DO NOT PROCEED** | `A-07` |
| `DPIA-07` Photographs | **Proceed, amended** | `A-08` |
| `DPIA-08` Fraud / security / location | **Proceed, amended** | `A-09`, `A-10` |
| `DPIA-09` KYC / criminal record | **Proceed, restricted** | `A-11`, `A-12` |
| `DPIA-10` Children | **Proceed pending** | `A-13` |

**Counted: 10 assessments, 13 actions, 1 hard stop, 1 conditional stop.**

---

## 7. Privacy Risk Register and Treatment

38 risks. Impact scored on **harm to the individual** (§2.2). Residual is after the stated
treatment, assuming the treatment is built.

### 7.1 Severe-impact risks (`I5`) — nine

| ID | Risk to the individual | L | I | R | Treatment | Control | Residual |
|---|---|:--:|:--:|:--:|---|---|:--:|
| `PR-01` | Identity fraud following NID disclosure | 2 | 5 | **H** | `Z4`, field encryption, `T5` + step-up, per-read log, **`A-01` reduce the stored population** | `SEC-C-047`, `-041`, `-050` | **M** |
| `PR-05` | Private material in a recovery case seen outside the assigned team | 3 | 5 | **C** | Case-scoped access, dual control, per-access log, per-case keys | `BRU-SEC-03`, `BRU-DTS-01` | **H** |
| `PR-13` | **Biometric template exfiltrated — irreversible** | 2 | 5 | **H** | Irreversible template, never exported, `Z4`, separate key material, **`A-05` alternative path** | `SEC-C-047` | **M**, only with `A-05` |
| `PR-23` | **A model trained on unlawfully processed data may not be remediable** | 4 | 5 | **C** | **`A-07` — do not proceed** | — | **L** if `A-07` holds; **C** if not |
| `PR-33` | Criminal-record retention causing livelihood or discrimination harm | 3 | 5 | **C** | **`A-11` outcome-retained, record-discarded**, category-scoped | `SEC-C-041` | **M** |
| `PR-38` | Cross-border restore of `Z4` exposes every sensitive category at once | 2 | 5 | **H** | `SEC-DR-02` resident DR target | **none exists** | **H — untreated** |
| `PR-11` | Salary or medical data disclosed to colleagues | 2 | 5 | **H** | Field permissions; `R46` sole medical access | `SEC-C-016` | **L** |
| `PR-27` | A leaked audit or access log reveals who accessed whose record | 2 | 5 | **H** | `T5` on logs; step-up; insert-only | `SEC-C-039`, `-043` | **M** |
| `PR-20` | Recovered data used as model training data | 2 | 5 | **H** | `BRU-DTS-14` absolute prohibition | `SEC-C-050` | **L** |

### 7.2 Major-impact risks (`I4`) — selected

| ID | Risk | L | I | R | Treatment | Residual |
|---|---|:--:|:--:|:--:|---|:--:|
| `PR-02` | NID over-collected at registration rather than at verification | 4 | 4 | **H** | `A-01` sight-and-verify path | **M** |
| `PR-06` | Recovery data retained beyond the agreed purge date | 3 | 4 | **H** | Automatic purge + certificate; escalation on overdue | **L** |
| `PR-07` | **Detectability** — a person is inferable as a recovery customer | 2 | 4 | **M** | `A-02` metadata minimisation | **L** |
| `PR-10` | Photograph shows the customer's home, screen or documents | 5 | 4 | **C** | `A-08` device-only framing + redaction binding | **M** |
| `PR-14` | Attendance biometric repurposed for performance or discipline | 3 | 4 | **H** | Purpose limitation in the model; `PI-02` | **M** |
| `PR-15` | Employee has no genuine opt-out | 4 | 4 | **H** | **`A-05`(c) non-biometric alternative without detriment** | **L** with `A-05`; **H** without |
| `PR-18` | Voice recording is more than its words | 3 | 4 | **H** | `A-06` transcript-primary | **M** |
| `PR-22` | Anonymised corpus re-identified | 4 | 4 | **H** | `A-07`(2) tested anonymisation standard | **M** |
| `PR-26` | Photograph of a powered-on screen captures the customer's own data | 4 | 4 | **H** | `A-08` screen-visible warning | **M** |
| `PR-31` | **DSR channel abused to extract another person's file** | 4 | 4 | **H** | Identity verification before assembly; rate limit (`AB-19`) | **M** |
| `PR-34` | Bank details and payroll `S3` but not residency-classified | 3 | 4 | **H** | **`A-12` reclassify**; `Z4` already provisioned | **L** |
| `PR-36` | A minor's data processed without parental consent | 3 | 4 | **H** | `A-13` risk-based gate at `S3`/financial actions | **M** |
| `PR-12` | Notice not reaching `DS-2` corporate users, only their employer | 4 | 4 | **H** | Notice presented **in the portal to the individual**, not only in the client contract | **M** |
| `PR-19` | Third-party portal tags collect personal data undisclosed | 4 | 4 | **H** | `TR-05` registration; CSP standard | **H — untreated** |
| `PR-35` | Sub-processor receives data undisclosed and uncontracted | 4 | 4 | **H** | `LG-012` §4.6 register | **H — untreated** |

### 7.3 Moderate and minor risks

`PR-03`, `PR-04`, `PR-08`, `PR-09`, `PR-16`, `PR-17`, `PR-21`, `PR-24`, `PR-25`, `PR-28`,
`PR-29`, `PR-30`, `PR-32`, `PR-37` — rated `I2`–`I3`, treated by existing controls or by the §6
actions, and reviewable at wave gate.

### 7.4 Treatments that are design constraints, not policy

The seven treatments a developer must build. **A privacy treatment expressed only as a policy is
`LG-021` §4.1.6's "control asserted as operating without evidence".**

| # | Design constraint | Realises | Owner | Wave |
|---|---|---|---|---|
| `PD-1` | **Purpose is a field on the processing record, and an access outside the recorded purpose is a logged exception** | `PI-02`, `O-1` | `M60`, `M29` | W2 |
| `PD-2` | **Retention is enforced technically and refuses to purge under legal hold** | `O-6`, `BRU-SEC-23` | `M24` | W2 |
| `PD-3` | **A DSR enumerates every module holding the subject's data through a registered data map** — a module absent from the map is invisible to the right | `O-4`, `M60` `T-08` | `P-17` | W2 |
| `PD-4` | **Consent withdrawal propagates immediately across every channel and module** | `BRU-CPM-09` | `M33` | W2 |
| `PD-5` | **The notice version in force at collection is bound to the consent record** — consent to a superseded notice is not consent | `BRU-CPM-13` | `M33` | W1 |
| `PD-6` | **`A-01` sight-and-verify**: an identity check that does not persist the identifier | `DPIA-01` | `M33`, `M04` | W1 |
| `PD-7` | **`A-13` parental-consent gate at `S3` capture and financial action**, not at registration | `O-14` | `M33` | W2 |

---

## 8. Residual Risk and Conclusion

### 8.1 The position after treatment

| Residual rating | Count | Position |
|---|---:|---|
| **Critical** | **1** | `PR-23` — **only if `A-07` is not observed.** With the hard stop honoured, it falls to Low |
| **High** | **4** | `PR-05`, `PR-38`, `PR-19`, `PR-35` |
| **Medium** | 14 | Acceptable with named owners and wave-gate review |
| **Low** | 19 | Accepted |
| **Total** | **38** | |

Check: 1 + 4 + 14 + 19 = **38** ✓ against a counted register of 38.

### 8.2 The four High residuals, and why they stay High

| ID | Why treatment does not reduce it further |
|---|---|
| `PR-05` | Recovery-case access **cannot be reduced below the assigned team** without making the service impossible. Dual control, logging and per-case keys are the ceiling of what design can do. **The remaining control is people** — vetting, training and supervision, which `LG-021` `IS-12` owns and currently has no delivery vehicle (`SC-001` `SEC-E-06`) |
| `PR-38` | **No Bangladesh-resident DR target exists** (`OP-01`). Untreatable inside Category 05 |
| `PR-19` | **`TR-05` unregistered and no CSP standard published.** Untreatable until the transfer register is populated |
| `PR-35` | **The sub-processor register does not exist** (`LG-012` `O-05`). `NFR-098` is a contractual obligation with no instrument behind it |

### 8.3 Conclusion

> **The processing may proceed, with one prohibition, one condition and eleven amendments.**
>
> - **`P-14` transcript reuse must not proceed** until `A-07`'s three conditions are met. This is
>   the answer `HC-01` asked for, and it is a **stop**, not a caution.
> - **Biometric attendance must not proceed** unless `A-05` records the ground, the rejected
>   alternatives, and a **non-biometric path available without detriment**.
> - The remaining eight assessments proceed with the amendments in §6.11.
> - **Four residual High risks are outside this document's power to close** and are carried to
>   `GV-005`.
>
> **This conclusion is conditional on `SC-003-CL-01`** — `G6` verification of every `P2` statutory
> claim against the enacted instrument, by Legal Counsel.

---

## 9. Data-Subject Rights Realisability

`O-4`…`O-7` are only real if they can be executed. Assessed per right.

| Right | Mechanism | Realisable today? | Blocker |
|---|---|:--:|---|
| **Access** | `P-17` DSR orchestrator enumerates every module via a registered data map | **No** | `PD-3` not built; **the data map does not exist** |
| **Portability** | Structured export in a machine-readable form | **No** | Not built; format not specified anywhere |
| **Rectification + 30-day recipient notification** | `BRU-CPM-10` | **No** | Recipient list per record does not exist — it requires `F-1`…`F-9` to be registered |
| **Erasure** | `BRU-CPM-11`, with statutory override | **Partially** | Retention is enforced; **erasure across 47 integration destinations is not** |
| **Withdrawal** | `BRU-CPM-09` immediate, all channels | **No** | `PD-4` not built |
| **Complaint to the Authority** | Direct to NDMA | **Yes** | Unconditional — `LG-008` §3 correctly states nothing conditions or delays it |

> **`SC-003-F-03`. Five of six rights are unrealisable today, and the sixth is the one 1000FiX
> does not control.** This is not a criticism of the estate — the rights are specified and the
> build has not started. It is stated because **`LG-010` §4.4 applies a 30-day period to every
> right as a provisional working assumption** (`DR1`, `O-02`), taken from the one period the
> statute states explicitly, which is for *rectification notification*. **If the statutory period
> for any other right is shorter, the process is already too slow.** Owner: Legal Counsel.
> Escalated with `A-14`.

---

## 10. Consultation

ISO/IEC 29134:2023 requires the stakeholder consultation to be recorded, including where it did not
happen.

| Stakeholder | Consulted | Record |
|---|---|---|
| Legal Counsel | **No** | Required for `A-05`, `A-07`, `A-11`, `A-13`, `A-14` and for `SC-003-CL-01` |
| Chief Data Officer | **No — the role does not exist** (`O-10`) | `Q-01` |
| Employee representatives | **No** | **Required for `DPIA-04`.** A biometric assessment without consulting the affected workforce is incomplete under the standard, and this is stated rather than glossed |
| Data subjects / customers | **No** | Proportionate at this stage; the notice is the consultation instrument, and `LG-008` is drafted |
| Brand partners | **No** | `DPIA-03` `A-04` changes their claim payload |
| Marketplace seller representatives | **No** | `DPIA-09` `A-11` changes vetting |
| External data-protection adviser | **No** | Named as a reviewer in `LG-008`, `LG-009`, `LG-012`; **not engaged** |
| Internal: EA, Security, HR, Quality | Partially — through the source documents | Not a substitute for consultation |

> **`SC-003-F-04`. Seven of eight stakeholder groups were not consulted, and two of the omissions
> are material to a determination** — Legal (five actions) and employee representatives
> (`DPIA-04`). The assessment is issued nonetheless, because an unissued DPIA discharges nothing
> and W2 is approaching; but it is issued **as a draft for consultation**, and §11 records that it
> cannot be signed in this state.

---

## 11. Sign-Off

| Role | Required by | Signature | State |
|---|---|---|---|
| **Chief Data Officer** | `O-10`, ISO/IEC 29134:2023 | — | **Role does not exist** |
| **Legal Counsel** | `SC-003-CL-01`; five actions | — | Not consulted |
| **Data Protection Forum** | `GV-002` | — | Constituted on paper; **has not met** |
| **CTO** | `O-11` security measures | — | Pending |

> **`SC-003-F-05`. This DPIA cannot be signed, and the reason is `NFR-096`.** The statute requires a
> significant data controller to appoint a CDO; 1000FiX at 250,000+ customers a month will almost
> certainly be classified as one; **the appointment has not been made.** Under `PGD-A2-25` no
> document in this estate can carry an unqualified ✅ until a constituted body can approve one — and
> for this document the gap is not merely procedural. **A DPIA is an accountability artefact; an
> unsigned one is an assessment, not an accountability record.** Escalated to `GV-005` and to the
> Board.

---

## 12. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | **Who is the Chief Data Officer?** (`NFR-096`, `O-10`) | CEO with the Board | **Now** | §11 sign-off; every determination in §6 |
| `Q-02` | Is 1000FiX a **significant data fiduciary**? | Legal Counsel | **Now** | `O-10`; penalty exposure BDT 25 vs 50 lakh |
| `Q-03` | What is the **prescribed breach-notification period and the "significant damage" threshold**? (`PN3`, `OP-18`) | Legal Counsel | W2 | `SC-011`; `OP-004` `RN-03`'s 72-hour assumption |
| `Q-04` | Does each right carry a different statutory response period? (`DR1`) | Legal Counsel | W2 | `LG-010` §4.4; `A-14` |
| `Q-05` | Hard age gate or declared age? (`PN10`) | Legal Counsel | W2 | `A-13`; `DPIA-10` |
| `Q-06` | Is there a lawful basis for **retaining** a criminal-record check after the vetting decision? (`PN8`) | Legal Counsel | W2 | `A-11` |
| `Q-07` | What anonymisation standard discharges `PR-22`, and how is it **tested**? | CDO with EA | **W2 — before `HC-015`** | `A-07`(2) |
| `Q-08` | Does the Authority publish a **DPIA methodology** in its SOPs that this document must conform to? | Legal Counsel | W4 | `RV-05`; re-issue of this document |
| `Q-09` | Is a **non-biometric attendance path** operationally acceptable to HR and Operations? | HR Director with COO | **Before W5** | `A-05`(c); `DPIA-04` determination |

---

## 13. Review and Follow-Up

| # | Trigger | Action | Owner |
|---|---|---|---|
| `RV-01` | A new processing purpose is proposed | Threshold assessment (§5); full DPIA if triggered. **`PI-02`: a purpose not in the table is not processed** | CDO |
| `RV-02` | Lawful basis for `P-14` is determined | Re-issue `DPIA-06`; release or confirm the stop | CDO with Legal |
| `RV-03` | The residency legal opinion (`D-13`) returns | Re-assess `DPIA-01`, `-02`, `-09`; re-rate `PR-34`, `PR-38` | CDO |
| `RV-04` | **Each wave gate** | Re-rate every High and Critical residual; confirm treatments built | CDO; `GV-009` evidence class |
| `RV-05` | The Authority publishes DPIA SOPs or breach regulations | Re-verify §3.1 from `P2` to `P1`; re-issue | Legal Counsel |
| `RV-06` | A personal-data breach occurs | Re-assess the affected purpose; feed `SC-011` post-incident review | CDO |
| `RV-07` | A new sub-processor or transfer is added | Assess before engagement; register before traffic (`RD-R4`) | CDO |
| `RV-08` | **Annually, unconditionally** | Full re-run. ISO/IEC 29134:2023 treats a PIA as a living artefact | CDO |

---

## 14. Decisions Recorded

| # | Decision | Options | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `SC-003-D-01` | Impact scale | Reuse `SC-002` §4.2 · Re-anchor on harm to individuals | **Re-anchor** | An organisational-loss scale systematically under-rates distress and loss of control — the most common DPIA error | Ratings are not directly comparable to `SC-002`; §2.2 states why, and likelihood is held common so divergence is visible |
| `SC-003-D-02` | Statutory source class | Cite clauses · Cite analysis with a class marker | **Class-marked analysis (`P2`)** | No clause citation can be supported without reading the enacted instrument | Every determination is conditional on `G6`; stated once in `SC-003-CL-01` |
| `SC-003-D-03` | Issue unsigned and unconsulted, or hold? | Hold until CDO appointed · **Issue as draft for consultation** | **Issue** | W2 approaches and `HC-01` needs a determination. An unissued DPIA discharges nothing | §10 and §11 record the gaps rather than implying completeness |
| `SC-003-D-04` | `P-14` position | Permit with safeguards · Permit pending review · **Stop** | **Stop** | `PR-23` — a model trained on unlawfully processed data may not be remediable by deleting the corpus | `HC-015` must be built from dispositions and agent summaries at W2 |
| `SC-003-D-05` | Biometric position | Accept as designed · Stop · **Conditional on an alternative path** | **Conditional** | The need is genuine; the *method* was never assessed against alternatives, and the harm is irreversible | `A-05` becomes a W5 gate item |
| `SC-003-D-06` | Children | Universal age gate · Declared age · **Risk-based gate at `S3`/financial** | **Risk-based** | A universal gate collects date of birth from 250,000 people a month to protect a small minority — the mitigation creates `PR-37` | Recommendation to Legal under `A-13`; `PN10` decides |

---

## 15. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | Every registered purpose is threshold-assessed | §5 — 20 purposes, stated outcome each |
| `AC-02` | Every triggered purpose has a full assessment with necessity, proportionality and alternatives | §6 — 10 assessments, 4 headings each |
| `AC-03` | Impact is scored on harm to individuals, with published anchors | §2.2; `SC-003-D-01` |
| `AC-04` | Less-intrusive alternatives are recorded, including those rejected and why | §6 — every assessment |
| `AC-05` | Each risk has a treatment and a residual rating | §7 — 38 risks |
| `AC-06` | Residual totals are regenerated by counting, not by arithmetic on a prior issue | §8.1 — check line |
| `AC-07` | Rights realisability is assessed per right, not asserted | §9 — 6 rights, 5 unrealisable |
| `AC-08` | Consultation is recorded, **including where it did not happen** | §10 — 7 of 8 not consulted |
| `AC-09` | Sign-off state is stated honestly | §11 — cannot be signed; reason given |
| `AC-10` | Statutory claims carry a source class | §2.3; `SC-003-CL-01` |
| `AC-11` | `HC-01` receives a determination | `DPIA-06` — **do not proceed** |
| `AC-12` | Review triggers are defined | §13 — 8 triggers |

---

## 16. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `SC-001` | Controls that treat the risks in §7 |
| Upstream | `SC-002` | §10 privacy threats; `TH-091`, `TH-092`, `TH-096` |
| Upstream | `DA-002` | PII flags — Category 03, authored concurrently |
| Downstream | `SC-007` | `A-12` reclassification; transfer registration |
| Downstream | `SC-008` | `O-1`…`O-15` become register rows with evidence and verification dates |
| Downstream | `SC-010` | `PD-1` purpose-bound access logging |
| Downstream | `SC-011` | `O-8` breach notification; `Q-03` |
| Downstream | `M33`, `M55`, `M06`, `M09`, `M12` | `A-01`…`A-13` land as module changes |
| Downstream | `HC-015`, `HC-017` | **Blocked by `DPIA-06`** |
| Lateral | `../../project_content/10_Legal_Policy_and_Compliance/LG-008_*.md` | The processing inventory this assesses |
| Lateral | `../../project_content/10_Legal_Policy_and_Compliance/LG-009_*.md`, `LG-010_*.md`, `LG-012_*.md` | Retention, rights, residency |
| Lateral | `../../project_content/_AUDIT/AUDIT-010_Category_09_HC_Content_Audit.md` | `HC-01`, which `DPIA-06` answers |

---

## 17. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` · `./_CATEGORY_OVERVIEW.md` ·
`./SC-001`, `./SC-002`, `./SC-007`, `./SC-008`, `./SC-011` ·
`../00_Programme_Governance_and_Control/GV-002_*.md`, `GV-005_*.md`

**Workspace**
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_*.md` §6.3, §6.4 ·
`../../1000fix_ERP_Module/03_Modules/B_Customer_Engagement_and_Experience/M33_*.md` ·
`../../1000fix_ERP_Module/03_Modules/A_Service_Delivery_and_Operations/M06_*.md` ·
`../../1000fix_ERP_Module/03_Modules/H_People_and_Workforce/M55_*.md` ·
`../../1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M60_*.md` ·
`../../project_content/10_Legal_Policy_and_Compliance/LG-008_*.md`, `LG-009_*.md`, `LG-010_*.md`, `LG-012_*.md` ·
`../../project_content/_AUDIT/AUDIT-010_*.md`, `AUDIT-017_*.md`

**External standards and sources** *(all verified 2026-08-18; source class `P2` for statute)*

| Source | Version / date | Used for |
|---|---|---|
| **ISO/IEC 29134** | **:2023, Edition 2 — supersedes and withdraws :2017** | Report structure and method |
| **ISO/IEC 27701** | **:2025, published 14 October 2025 — standalone, replaces :2019.** No longer requires ISO/IEC 27001 as a base | PIMS control reference; §13 opportunity |
| ISO/IEC 29100 | :2024 | Privacy principles as the assessment lens |
| ISO/IEC 27005 | :2022 | Risk method |
| **Personal Data Protection Act 2026 (Law 63 of 2026)**, Bangladesh | Ordinance issued 6 Nov 2025; amended by **Ordinance No. 23 of 2026** (5 Feb 2026); **enacted April 2026**; enforcement ~**13 May 2027**. Regulator: **National Data Management Authority**, reporting to the Prime Minister's Office. Penalties **BDT 25 lakh**, **BDT 50 lakh** for significant data fiduciaries, plus repeat-violation fines. **Children: under 18, verifiable parental consent.** Records: **≥ 5 years**. Rectification recipient notification: **30 days**. **Breach-notification period and DPIA methodology are left to regulations/SOPs not yet published** | §3.1, §6, §12 |
| **Cyber Security Ordinance 2025** (No. 25 of 2025) | Gazetted 21 May 2025; in force. NCSA; CII obligations incl. own CERT/CIRT and SOC with quarterly reporting | §3.2; second notification clock |

---

## 18. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture, on behalf of the unappointed CDO | Initial issue. First DPIA in the programme's history. 20 purposes threshold-assessed, 10 full assessments, 38 privacy risks, 13 actions. **`P-14` transcript reuse determined DO NOT PROCEED, answering `HC-01`.** Biometric attendance made conditional. Issued as a **draft for consultation** — unsigned, because `NFR-096` is not met | *Cannot be signed — no CDO (§11)* |

---

*`SC-003` · Category 05 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
