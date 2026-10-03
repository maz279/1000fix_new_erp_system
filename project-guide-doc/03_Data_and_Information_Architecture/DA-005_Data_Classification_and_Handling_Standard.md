---
id: DA-005
title: Data Classification & Handling Standard
category: 03 — Data & Information Architecture
code: DA
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Chief Data Officer (unappointed — see DA-003 §5)
approver: Head of Information Security
standards_basis: >
  ISO/IEC 27001:2022 Annex A.5.12–A.5.14 (classification, labelling, transfer) ·
  ISO/IEC 27002:2022 · ISO/IEC 25012 · Bangladesh Personal Data Protection Act 2026 ·
  Cyber Security Ordinance 2025
traces_to: >
  PGD-000 DA-005 · 05-02 §10 (S0–S3) · NFR-086/086a/086b/086c · NFR-099 · NFR-061 · NFR-071 ·
  audit C-05 · AR-001 §8.2 (tiers T0–T5) · DA-002 attributes 21–23
depends_on: DA-002 · DA-003 · AR-001 · SC-007
verified_on: 2026-08-18
priority: P0
needed_by: W1
enumeration_timestamp: 2026-08-18 14:30 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# DA-005 — Data Classification & Handling Standard

### Category 03 · Code `DA` · ISO/IEC 27001:2022 A.5.12–A.5.14 · PDPA 2026

---

## 1. Purpose

`05-02` §10 defines four sensitivity classes, `S0`–`S3`, with a control note each. It is sound and it
is used across the estate. **It predates two things:** the PDPA 2026 finding that NID, TIN, biometric
templates and KYC documents are statutorily sensitive (audit `C-05`), and the split-residency
architecture that followed from it.

The result is that the estate has **one axis where it needs three**. Sensitivity, personal-data
category and residency are independent properties: a field can be `S1` and personal and non-resident;
another can be `S3` and not personal at all (an API credential); a third can be personal, `S2` and
residency-restricted. Collapsing them into one scale forces every handling rule to be written for the
worst case.

This document is the three-axis scheme, the handling rule **per class per data state**, and the
assignment procedure that makes `DA-002` attributes 21–23 answerable.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | The three classification axes and why they are separate |
| 2 | The **sensitivity scale** `S0`–`S3`, carried forward from `05-02` §10 and made testable |
| 3 | The **personal-data category** under PDPA 2026 |
| 4 | The **residency class**, and the finding that its statutory basis is in question |
| 5 | **The handling matrix** — every class × every data state |
| 6 | Labelling, marking and export watermarking |
| 7 | The assignment procedure, authority and review |
| 8 | Aggregation, inference and re-identification |
| 9 | The relationship to isolation tiers `T0`–`T5` and to trust zones `Z0`–`Z6` |

**Explicitly out of scope**

| Topic | Owned by | Why |
|---|---|---|
| Per-field assignment | `DA-002` attributes 21–23 | Scheme here; assignment there |
| Encryption algorithms, key lifecycle, HSM | `SC-006` | This document says *what* must be encrypted |
| Access control implementation | `SC-004` | This document says *what* must be restricted |
| The DPIA | `SC-003` | Consumes this scheme |
| Residency infrastructure | `SC-007`, `PE-001` | This document classifies; they place |
| Retention periods | `LG-009`, `DA-006` | Orthogonal — a class does not imply a period |
| Document confidentiality marking on templates | `RP-014`, `DT-*` | Consumes §7 |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| **Every developer** | §6 handling matrix — what you may do with a value |
| `DA-002` stewards | §8 assignment procedure |
| **DPO / CDO** | §4, §5 — the PDPA mapping and its open question |
| Head of InfoSec | §6, §9 — the control obligations this creates |
| QA | §6 rows are directly testable; §10 lists the negative tests |
| Content authors | §7 labelling and watermarking |

---

## 2. Basis and Findings

### 2.1 Standards conformance

| Standard | Conformance | Departure |
|---|---|---|
| **ISO/IEC 27001:2022 A.5.12** Classification of information | §3 scheme; §8 assignment and review | Full |
| **A.5.13** Labelling of information | §7 | Full |
| **A.5.14** Information transfer | §6 in-transit rows; §5.3 cross-border | Full |
| **ISO/IEC 27002:2022** | Control guidance for the above | Reference |
| **PDPA 2026** | §4 personal-data category; §5 residency | Statutory. **§5.3 records that the residency basis is in question** |
| **Cyber Security Ordinance 2025** | Critical Information Infrastructure definition referenced in §5.3 | In force (verified 2026-08-18) |
| ISO/IEC 25012 | Confidentiality as a data-quality characteristic | Reference |

### 2.2 Source material

| Source | Contribution |
|---|---|
| `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02_Data_Model_and_Entity_Catalogue.md` §10 | **`S0`–`S3` and the S3 field inventory** — the scheme this extends |
| `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md` §4, §6.3, §6.4 | NFR-061, NFR-071; NFR-090…NFR-099; NFR-086 and its sub-clauses |
| `../02_Architecture_and_Design/AR-001_Software_Architecture_Document.md` §8.1, §8.2, §8.3 | Trust zones `Z0`–`Z6`; isolation tiers `T0`–`T5`; residency topology |
| `./DA-001_*.md` §10 | The physical residency split and its §10.4 finding |
| `../../project_content/10_Legal_Policy_and_Compliance/LG-008`, `LG-012` | Purposes `P-01`…`P-20`; the cross-border transfer statement |
| `../../project_content/14_Reporting_Analytics_and_KPI/RP-014_Export_Watermark_and_Confidentiality_Marking_Rules.md` | Export marking — §7 consumes it |
| `../../project_content/15_Integration_and_Developer_Content/AP-012_Data_Sharing_and_Field_Level_Disclosure_Register.md` | Third-party disclosure per field |

### 2.3 Findings

> **`PGD-A5-09` — the estate has one classification axis where it needs three.**
>
> `05-02` §10's `S0`–`S3` conflates **sensitivity** (how much harm does disclosure cause), **personal-data
> category** (what does the statute say) and, implicitly, **residency**. The S3 row lists *"NID numbers,
> bank details, individual payroll, recovered customer data, call recordings, biometric templates"*
> alongside — in the S3 field inventory — *"API and integration credentials"*.
>
> **An API credential and a biometric template need different handling and are the same class.** A
> credential must never be displayed after creation but has no data-subject rights, no retention
> obligation to a person and no residency constraint. A biometric template has all three and may
> legitimately be *shown* to its subject.
>
> §3 separates the axes. `S0`–`S3` is retained unchanged so nothing already written becomes wrong.

> **`PGD-A5-10` — the S3 inventory is nine fields; the measured field population is 5,301.**
>
> `05-02` §10's S3 field inventory lists **nine fields**. `DA-001` measures **5,301 distinct field
> names across 1,335 tables**. The inventory is a worked example, not a classification — and no
> document in the estate claims otherwise, but several consume it as though it were complete.
> `DA-002` attribute 21 across ~17,000–19,000 elements is the real artefact, and it is 0% populated.

---

## 3. The Three Axes

### 3.1 Why they are separate

| Axis | Question it answers | Driven by | Consequence |
|---|---|---|---|
| **Sensitivity** `S0`–`S3` | How much harm does unauthorised disclosure cause? | Business and commercial judgement | Access control, encryption, logging |
| **Personal-data category** | What does the statute say about this? | **PDPA 2026** | Lawful basis, consent standard, data-subject rights, breach notification |
| **Residency** | Where may this physically live? | **PDPA 2026 transfer rules** | Storage location, replication, transfer notification |

**A field carries one value on each axis.** The handling rule is the **union of the three rows** in §6
— the strictest requirement on each dimension wins.

### 3.2 Worked examples showing why one axis fails

| Field | Sensitivity | Personal | Residency | The point |
|---|:--:|---|:--:|---|
| `fix_service_order.state` | `S1` | not personal | none | Ordinary internal data |
| `fix_party.primary_mobile` | `S2` | **personal** | none | Personal but not sensitive-category; drives OTP so it is operationally critical |
| `fix_identity_document.nid_number` | `S3` | **restricted** | **resident** | All three axes at maximum |
| `fix_attendance_record.biometric_template` | `S3` | **restricted** | **resident** | Same, and **may be shown to its subject** |
| `fix_integration_credential.secret` | `S3` | **not personal** | none | **Maximum sensitivity, no statutory dimension at all.** Never displayed after creation; no erasure right attaches |
| `fix_payslip.net_pay` | `S3` | **personal** | none | Sensitive, personal, but not a restricted identifier |
| `fix_mp_seller_document.criminal_check` | `S3` | **restricted** | **resident** | |
| `fix_recovered_inventory.index` | `S3` | **personal (processor)** | **resident** | **1000FiX is processor, not controller** (`AR-002` §5.4) |
| `fix_catalogue_item.list_price` | `S2` | not personal | none | Commercially confidential, no statutory dimension |
| `fix_branch.address` | `S0` | not personal | none | Published |

> **The credential row is the one that proves the case.** Under a single axis it sits with biometric
> templates and inherits data-subject rights it cannot have, an erasure obligation that would break
> production, and a residency constraint with no statutory basis.

---

## 4. Axis 1 — Sensitivity (`S0`–`S3`)

**Carried forward from `05-02` §10 unchanged in meaning**, with the definition made testable.

| Class | Definition | Test — *"if this were disclosed to an unauthorised person…"* | Examples |
|:--:|---|---|---|
| **`S0` Public** | Published or publishable without harm | *"…nothing happens"* | Service catalogue, branch addresses, published prices, opening hours |
| **`S1` Internal** | Business data, staff-visible | *"…a competitor learns how we operate; no individual is harmed"* | Service orders, stock levels, schedules, fault codes |
| **`S2` Confidential** | Restricted business or personal data | *"…a person is embarrassed or a commercial position is damaged"* | Customer contact details, pricing, margins, aggregate salary bands |
| **`S3` Restricted** | Highest sensitivity | *"…a person suffers material harm, or the company suffers a statutory or existential consequence"* | NID, bank details, individual payroll, recovered customer data, call recordings, biometric templates, **credentials** |

### 4.1 Assignment rules

| # | Rule |
|---|---|
| **SN-01** | **Default is `S1`.** A field with no assigned class is treated as `S1` and flagged for assignment — never as `S0` |
| **SN-02** | Sensitivity is assigned to the **field**, not the table. A `S3` field does not make its table `S3` |
| **SN-03** | **A derived value inherits the highest class of its inputs** unless the derivation is demonstrably irreversible (§9) |
| **SN-04** | An aggregate is `S1` **only** if it cannot be reduced to an individual (§9.1) |
| **SN-05** | Sensitivity may be **raised** by the data owner; **lowering requires CDO approval** |

---

## 5. Axis 2 and 3 — Personal Data and Residency

### 5.1 Personal-data category

| Value | Definition | Statutory consequence |
|---|---|---|
| `not_personal` | Not relatable to an identified or identifiable person | None |
| **`personal`** | Ordinary personal data | Purpose + lawful basis (NFR-090); transparency notice (NFR-092); data-subject rights (NFR-093); processing record 5 years (NFR-095) |
| **`sensitive`** | Heightened category | **Specific consent** unless a legitimate ground applies (NFR-091); heightened technical measures (NFR-097) |
| **`restricted`** | Government unique identifiers (NID, passport, TIN), biometric, genetic, criminal-record | **NFR-099 transfer restriction**; residency (§5.2); Authority notification on transfer (NFR-086b) |

| # | Rule |
|---|---|
| **PC-01** | **Default is `personal`** for any field in a table that identifies a person. Proving something is *not* personal is the assertion requiring evidence |
| **PC-02** | A **pseudonymised** value is still personal data (`DM-R2`). Only genuinely irreversible anonymisation exits the category |
| **PC-03** | **Assignment requires CDO approval** (`DA-003` §6). It is a statutory judgement, not a business preference |
| **PC-04** | Every `personal` field maps to at least one **purpose** in `LG-008` `P-01`…`P-20` and one **retention class** in `LG-009` `RC-01`…`RC-27` |

### 5.2 Residency class

| Value | Meaning |
|---|---|
| `none` | May live in the regional store |
| **`resident`** | `DA-001` §10 applies — value in Z4, `resident_key` in Z3, all access via CD-233 |
| **`resident_pending`** | **Unresolved pending `DEP-31`. Treated as `resident`** — the conservative direction |

### 5.3 The finding that puts the residency basis in question

> **`PGD-A5-03` (raised in `DA-001` §10.4, restated here because this is the classification document).**
> **Verified against public sources 2026-08-18; requires legal confirmation.**
>
> The estate classifies residency **by field type** — NID, passport, TIN, biometric, recovered data,
> KYC, criminal-record — and designs an **exclusive residency** model.
>
> Public reporting on **Personal Data Protection (Amendment) Ordinance, 2026 (No. 23 of 2026),
> promulgated 5 February 2026** describes a different obligation:
>
> | | Estate's basis | Reported statutory basis |
> |---|---|---|
> | Mechanism | Value exists **only** in Bangladesh | **At least one synchronised real-time copy** in Bangladesh |
> | Trigger | Field type | **"Restricted personal data"** and Critical Information Infrastructure (Cyber Security Ordinance 2025) |
> | Definition | Enumerated fields | **By impact** — national security, public order, defence, critical infrastructure, fundamental rights |
> | Direction | — | The Feb 2026 amendment **narrowed** the November 2025 scope |
>
> **The classification consequence.** If the trigger is impact-based, then the *set* of resident fields
> is not the estate's seven — it could be **smaller** (only data whose compromise affects national
> security or critical infrastructure) or **larger** (any data whose compromise affects fundamental
> rights, which is arguably most personal data).
>
> **What this document does about it, rather than waiting.**
>
> | # | Rule |
> |---|---|
> | **RD-01** | The seven enumerated fields are classified **`resident`** and handled as such. The conservative direction |
> | **RD-02** | Every field classified `personal` or above carries an **impact assessment note** — could its compromise affect national security, public order, defence, critical infrastructure or fundamental rights? This is the field `DEP-31`'s answer will be applied to |
> | **RD-03** | Fields where the impact answer is arguable are classified **`resident_pending`** |
> | **RD-04** | **The mechanism is built regardless** (`TR-02`). Classification is data; a change of legal opinion is a **reclassification, not a redesign** |
>
> **RD-02 is the practical response.** Rather than waiting for a legal opinion and then re-reviewing
> 17,000 elements, the impact question is asked **once, at assignment time**, so the opinion can be
> applied as a filter rather than as a re-survey.

---

## 6. The Handling Matrix

**The core of this document.** Every class, every data state. Where a field carries values on more
than one axis, **the strictest cell on each row applies**.

### 6.1 At rest

| State | `S0` | `S1` | `S2` | `S3` |
|---|---|---|---|---|
| Storage | Any | Encrypted volume | Encrypted volume | **Field-level encryption with separate key material** (NFR-061) |
| Key management | — | Platform key | Platform key | **`SC-006` — separate key, rotation, crypto-erase capable** |
| Backup | Standard | Encrypted (AES-256) | Encrypted | Encrypted; **`DM-3` crypto-erase must reach it** |
| Object storage | Public bucket permitted | Private | Private | Private + per-object key reference |

| Personal category | Additional at-rest rule |
|---|---|
| `personal` | Retention class assigned and enforced (`DA-006`) |
| `sensitive` | As `S3` at-rest handling regardless of sensitivity class |
| **`restricted`** | **Z4 only. Never a column in Z3** (`DA-001` RS-01) |

### 6.2 In transit

| State | `S0` | `S1` | `S2` | `S3` |
|---|---|---|---|---|
| Internal | Any | TLS 1.2+ | **TLS 1.3** | TLS 1.3 + mTLS between services |
| External | TLS | TLS 1.2+ | TLS 1.3 | TLS 1.3, **allow-listed destination via Z6** |
| Event payload | Permitted | Permitted | **Minimised** (IP-10) | **Never** — resident key only (`AR-009` P-03) |
| API response | Permitted | Scoped | Scoped + field permission | **Scoped + step-up + logged** |
| Email / SMS / WhatsApp | Permitted | Avoid | **Never in body** | **Never** |

### 6.3 In use

| State | `S0` | `S1` | `S2` | `S3` |
|---|---|---|---|---|
| Screen display | Any | Role-scoped | Field permission (CD-130) | **Masked by default; reveal is an explicit, logged action with step-up** |
| Print / PDF | Any | Watermark per `RP-014` | Watermark + recipient | **Watermark + recipient + purpose; `S3` on a printed page needs a stated reason** |
| Export (CSV/Excel) | Any | Logged | **Logged + watermarked + row-count alert** | **Prohibited without CDO approval per export** |
| Clipboard / screenshot | — | — | Discouraged | **Privileged sessions recorded** (NFR-070) |
| **Search index** | Indexed | Indexed | Indexed | **Never indexed** |
| **LLM prompt** | Permitted | Permitted if minimised | **Never** | **Never** (`AR-011` LLM-03) |

### 6.4 In logs, traces and telemetry

| State | `S0` | `S1` | `S2` | `S3` |
|---|---|---|---|---|
| Application log | Permitted | Permitted | **Never** | **Never** |
| Error message / stack trace | Permitted | Permitted | **Never** | **Never** |
| Distributed trace attribute | Permitted | Identifier only | **Identifier only** | **Never, not even the identifier** |
| Audit entry | Permitted | Permitted | Identifier + action | **Identifier + action + actor; never the value** |
| Metric label | Permitted | Low-cardinality only | **Never** | **Never** |

> **The whole of §6.4 is one rule with four columns: `OPS-04` — no personal data in logs.** It is
> stated as a matrix because *"no personal data in logs"* is routinely read as *"no NID in logs"* and
> then a customer's mobile number appears in an error message. `AR-012` `FF-32` enforces it.

### 6.5 In non-production

| State | Rule |
|---|---|
| `S0`, `S1` | May be copied |
| `S2` | **Masked** (NFR-071) |
| `S3` | **Masked or synthetic. Never real values** |
| `personal` and above | **Masked**, and masking runs **inside the clone job** so an unmasked clone cannot exist even briefly |
| **`resident`** | **NFR-086c is absolute — never present in any non-production environment, in any region, masked or not** |

### 6.6 In analytics and the warehouse

| State | Rule |
|---|---|
| `S0`, `S1` | Loaded |
| `S2` | Loaded with row-level security bound to a `05-04` tier (`RP-006` `SM-04`) |
| `S3` | **Excluded by default** (`RP-006` `SM-05`). Inclusion requires named, approved, time-limited authorisation recorded in the dataset's `excluded_fields` |
| **`resident`** | **Never leaves the resident store.** A dataset joins by resident key without duplicating the field (`RP-006` `SM-16`) |
| Derived / aggregated | §9 aggregation rules apply |

### 6.7 In third-party disclosure

| Rule |
|---|
| Every disclosure is registered per field in `AP-012` |
| `S2` and above requires a **contract with equivalent obligations** flowed down (NFR-098) |
| **`restricted`** requires **Authority notification and a documented safeguard *before* the transfer executes** (NFR-086b) |
| A processor's processing is treated as the controller's own (NFR-098) |

---

## 7. Labelling and Marking

| # | Rule |
|---|---|
| **LB-01** | **Every data element carries its three classifications in `DA-002`.** That is the authoritative label |
| **LB-02** | Every document carries a classification marking in its front matter and footer — this repository's own `classification:` key is the pattern |
| **LB-03** | Every **export** is watermarked per `RP-014` with recipient, timestamp and classification |
| **LB-04** | Every **report and dashboard** displays the highest classification of any field it contains |
| **LB-05** | A **screen** displaying `S3` shows a visible indicator that a restricted value is present, whether or not it is revealed |
| **LB-06** | **Labels are inherited, never re-derived.** A report containing one `S3` column is an `S3` report |

---

## 8. Assignment, Authority and Review

### 8.1 Procedure

| Step | Action | Who |
|:--:|---|---|
| 1 | A new field is created → `DA-002` `Candidate` registration (generated) | CI |
| 2 | **Sensitivity** proposed | Data owner (`DA-003` §3.2) |
| 3 | **Personal category** and **impact note** (RD-02) proposed | Data steward with DPO |
| 4 | **Residency** proposed | Data steward with Legal |
| 5 | **Approved** — all three axes | **CDO** (`DA-003` §6) |
| 6 | Registration reaches `Registered`; handling rules become enforceable | Registration Authority |

### 8.2 Rules

| # | Rule |
|---|---|
| **AS-01** | **No field reaches production without all three axes assigned** — `DA-002` `RC-3`, blocking at the wave gate |
| **AS-02** | Assignment is **per field**, never per table or per module |
| **AS-03** | **Raising a class is immediate; lowering requires CDO approval and a recorded reason** |
| **AS-04** | Changing any axis triggers **re-assessment in `SC-003`** (`DA-002` `RG-05`) |
| **AS-05** | Classification is reviewed at **every wave gate** and whenever a purpose changes |
| **AS-06** | A field whose classification is disputed is handled at the **higher** class until resolved |

### 8.3 The bootstrapping problem

> **`AS-01` blocks production; the CDO who must approve does not exist** (`DA-003` `PGD-A5-07`).

| Interim | Rule |
|---|---|
| **IN-01** | Until a CDO is appointed, the **Head of InfoSec with the DPO** jointly hold the approval, recorded as an interim mandate with a named review date (`DA-003` §5.4) |
| **IN-02** | The interim is registered in `GV-005` RAID **with an expiry** |
| **IN-03** | Every classification approved under the interim is **re-confirmed by the CDO on appointment** — a bulk re-confirmation, not a re-survey |

---

## 9. Aggregation, Inference and Re-identification

The three ways a correct per-field classification produces an incorrect outcome.

### 9.1 Aggregation

| # | Rule |
|---|---|
| **AG-01** | An aggregate is `S1` **only if it cannot be reduced to an individual** |
| **AG-02** | **Minimum group size for any personal-data aggregate is 5.** A "branch average technician earnings" over three technicians is three salaries |
| **AG-03** | Differencing is checked — two aggregates that differ by one member disclose that member |
| **AG-04** | `RP-006` datasets declare **prohibited joins** for exactly this reason (`SM-03`) |

### 9.2 Inference

| # | Rule |
|---|---|
| **IF-01** | A field permitting inference of a higher-class value **inherits that class** |
| **IF-02** | Worked example: `fix_location_ping` is `S1` operational data. **A technician's continuous location history for 90 days is not** — it discloses home address, movement pattern and working hours. `RC-24` limits full granularity to 90 days for this reason, and the aggregate tiers survive it |
| **IF-03** | ML features are assessed for inference before use (`AR-011` FT-06) |

### 9.3 Re-identification

| # | Rule |
|---|---|
| **RI-01** | **Anonymisation is deletion only if re-identification is genuinely impossible** (`LG-009` `DM-R2`) |
| **RI-02** | A quasi-identifier set — postcode + date of birth + gender — is personal data even with the name removed |
| **RI-03** | Masked non-production data is **still personal data if re-identifiable** (`LG-009` `RC-26`) |
| **RI-04** | Re-identification risk is assessed before any dataset is published outside the ERP |

---

## 10. Relationship to Isolation Tiers and Trust Zones

Three schemes exist and they are **orthogonal**. Confusing them is a common source of over- and
under-protection.

| Scheme | Separates | Defined in |
|---|---|---|
| **Classification** `S0`–`S3` + personal + residency | **What the data is** | This document |
| **Isolation tiers** `T0`–`T5` | **Which records a user may see** | `AR-001` §8.2 |
| **Trust zones** `Z0`–`Z6` | **Which networks a component sits in** | `AR-001` §8.1 |

### 10.1 Where they coincide

| Coincidence | Detail |
|---|---|
| **`S3` ↔ `T5`** | Almost every `S3` field is also `T5` (explicit grant, access logged, step-up). **Not identical**: a credential is `S3` and has no `T5` record-level grant because no user reads it |
| **`resident` ↔ `Z4`** | Exact. A `resident` value lives in `Z4` and nowhere else |
| **`resident` ⊂ `T5`** | Every resident field is `T5`; not every `T5` field is resident |

### 10.2 The rule that follows

> **A `T5` read of a `resident` field is a call to the residency service (CD-233), which performs the
> step-up check, logs the access and returns the value. It is never a direct database read.**
> One enforcement point, one audit point (`AR-001` §8.2).

---

## 11. Testing

Classification is testable, and §6's rows are the test cases.

| # | Negative test | Enforced by |
|---|---|---|
| **NT-01** | An `S3` value appears in an application log | `AR-012` `FF-32` |
| **NT-02** | A `resident` value appears in any Z3 table, index, cache or export | `FF-09` |
| **NT-03** | A `resident` value appears in a non-production environment | `FF-09`; NFR-086c |
| **NT-04** | An `S3` field appears in a warehouse dataset without recorded authorisation | `RP-006` `SM-05` |
| **NT-05** | An `S2`+ value appears in an event payload beyond the minimum | `AR-009` P-04 |
| **NT-06** | A `personal` field has no purpose or retention class | `DA-002` `RC-4` |
| **NT-07** | An export of `S2`+ occurs without watermark or log | `RP-014` |
| **NT-08** | An aggregate over fewer than 5 personal records is served | AG-02 |
| **NT-09** | A field reaches production with any axis unassigned | `DA-002` `RC-3` |
| **NT-10** | An `S3` value enters an LLM prompt | `AR-011` LLM-03 |

---

## 12. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| **Q-01** | **Is the residency trigger field-type or impact-based (`PGD-A5-03`)?** RD-02's impact note is the hedge; the answer determines the resident set | CFO / Legal / DPO — `DEP-31`, `D-13` | **Before the W1 schema is fixed** | `DA-001` §10; `SC-007`; `PE-001` |
| **Q-02** | **Who approves classification before a CDO exists?** §8.3's interim needs ratification | CTO / Head of InfoSec | **W0 — blocking** | Every field reaching production |
| **Q-03** | Is the three-axis scheme accepted, given `S0`–`S3` is cited across the estate? §3 retains `S0`–`S3` unchanged, but consumers must learn there are two more axes | Enterprise Architecture / Council | W1 | `DA-002` attributes 21–23 |
| **Q-04** | Is **minimum group size 5** (AG-02) correct for this business? A 51-branch network makes some legitimate operational aggregates small | CDO / Ops Director | W4 | `DA-007`; `RP-006` |
| **Q-05** | Does `05-02` §10 get reissued to three axes, or is `DA-005` the authority? | Enterprise Architecture | W1 | Which document a developer reads |
| **Q-06** | Does the **processor** position for M06 recovered data change its classification handling? A processor cannot unilaterally reclassify | DPO / Legal | W6 | M06; `LG-017` |

---

## 13. Decisions Recorded

| # | Decision | Options | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| D-D5-01 | Axes | One scale (`S0`–`S3`); **three independent axes** | **Three** | A credential and a biometric template need different handling and are the same class under one axis | Consumers must learn two more axes (Q-03) |
| D-D5-02 | `S0`–`S3` | Replace; **retain unchanged** | **Retain** | It is cited across the estate and it is correct for what it measures | Nothing already written becomes wrong |
| D-D5-03 | Default sensitivity | `S0`; **`S1`** | **`S1`** | An unassigned field defaulting to public is the wrong direction of error | SN-01 |
| D-D5-04 | Default personal category | `not_personal`; **`personal`** | **`personal`** | Proving something is *not* personal is the assertion that needs evidence | PC-01 |
| D-D5-05 | Unresolved residency | `none`; **`resident_pending`, treated as resident** | **`resident_pending`** | A wrongly-regional restricted field is a notifiable event | Some fields over-protected until `DEP-31` |
| D-D5-06 | Impact assessment | Wait for `DEP-31`; **ask the impact question at assignment (RD-02)** | **Ask now** | Otherwise the opinion triggers a re-survey of ~17,000 elements instead of a filter | One extra note per personal field |
| D-D5-07 | Aggregation floor | None; **minimum group size 5** | **5** | A three-technician branch average is three salaries | Q-04 tests it against a 51-branch network |
| D-D5-08 | Interim approval | Block until a CDO exists; **InfoSec + DPO jointly, with expiry** | **Interim** | Blocking would stop W1; an unrecorded workaround would be worse | `IN-03` bulk re-confirmation on appointment |

---

## 14. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | Three axes are defined, with worked examples showing why one fails | §3.1, §3.2 |
| AC-02 | `S0`–`S3` is carried forward unchanged and made testable | §4 |
| AC-03 | The PDPA personal-data categories map to statutory consequences | §5.1 |
| AC-04 | **A handling rule exists for every class in every data state** | §6 — 7 states |
| AC-05 | Labelling, marking and watermarking are specified | §7 |
| AC-06 | Assignment has a procedure, an authority and a stated interim | §8 |
| AC-07 | Aggregation, inference and re-identification are addressed | §9 |
| AC-08 | The relationship to tiers and zones is stated, including where they do **not** coincide | §10 |
| AC-09 | Every handling rule has a negative test | §11 — 10 tests |
| AC-10 | The residency finding is recorded with a practical hedge, not left pending | §5.3 RD-01…RD-04 |

**Definition of done.** Complete when every criterion is met, Q-01 and Q-02 are resolved, and
`PGD-000`'s `DA-005` row is updated.

---

## 15. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `AR-001` §8.1, §8.2 | Zones and tiers this scheme is orthogonal to |
| Upstream | `DA-003` §6 | CDO approval authority |
| Downstream | **`DA-002` attributes 21–23** | This scheme is what those attributes carry |
| Downstream | `DA-001` §10 | Residency drives the physical split |
| Downstream | `DA-006` | Class drives deletion method (`DM-3` crypto-erase for `S3`) |
| Downstream | `DA-007` | §6.6 warehouse rules |
| Downstream | **`SC-003` DPIA** | Consumes the personal-data axis |
| Downstream | `SC-004`, `SC-006`, `SC-007` | Access, cryptography, residency implementation |
| Downstream | `QA-004` | Test-data masking derives from §6.5 |
| Downstream | `AR-012` `FF-09`, `FF-32` | Enforcement |
| Lateral | `05-02` §10 | Retained as the `S0`–`S3` source; extended, not replaced (Q-05) |
| Lateral | `RP-014`, `AP-012` | Watermarking and disclosure registers |

---

## 16. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` · `./_CATEGORY_OVERVIEW.md` ·
`./DA-001_Logical_and_Physical_Data_Model_and_Database_Schema_Specification.md` §10 ·
`./DA-002_Data_Dictionary.md` §8 · `./DA-003_Data_Governance_Framework_and_Stewardship_Model.md` §5, §6 ·
`./DA-006_Data_Retention_Archival_and_Deletion_Design.md` ·
`../02_Architecture_and_Design/AR-001_Software_Architecture_Document.md` §8 ·
`../02_Architecture_and_Design/AR-011_AI_ML_Architecture_and_Model_Specification.md` §10 ·
`../02_Architecture_and_Design/AR-012_Architecture_Compliance_and_Fitness_Function_Standard.md`

**Workspace**
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02_Data_Model_and_Entity_Catalogue.md` §10 ·
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md` §4, §6.3, §6.4 ·
`../../project_content/10_Legal_Policy_and_Compliance/LG-012_Cross_Border_Data_Transfer_and_Residency_Statement.md` ·
`../../project_content/14_Reporting_Analytics_and_KPI/RP-014_Export_Watermark_and_Confidentiality_Marking_Rules.md` ·
`../../project_content/15_Integration_and_Developer_Content/AP-012_Data_Sharing_and_Field_Level_Disclosure_Register.md`

**External standards and sources**

| Source | Version / date | Verified |
|---|---|---|
| ISO/IEC 27001:2022 Annex A.5.12–A.5.14 | 2022 | 2026-08-18 |
| ISO/IEC 27002:2022 | 2022 | 2026-08-18 |
| [Bangladesh PDPA 2026 — categories, transfer, penalties](https://securiti.ai/bangladesh-personal-data-protection-act-overview/) | Enforcement ~13 May 2027 | 2026-08-18 |
| [Personal Data Protection (Amendment) Ordinance 2026, No. 23 of 2026](https://digitalpolicyalert.org/event/38601-president-implemented-personal-data-protection-amendment-ordinance-2026-ordinance-no-23-of-2026) | 5 February 2026 | 2026-08-18 |
| [Government eases data localisation rules — The Daily Star](https://www.thedailystar.net/news/bangladesh/news/govt-eases-data-localisation-rules-drops-jail-terms-tech-firms-4076391) | February 2026 | 2026-08-18 |
| Cyber Security Ordinance 2025 (Bangladesh) — CII definition | In force (21 May 2025) | 2026-08-18 |

---

## 17. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. Separates one classification axis into **three** — sensitivity, personal-data category, residency — retaining `S0`–`S3` unchanged. Publishes the handling matrix across **seven data states**. Raises `PGD-A5-09` (single axis insufficient) and `PGD-A5-10` (S3 inventory is 9 fields against 5,301 measured); restates `PGD-A5-03` with the RD-02 impact-note hedge | *Pending — Head of InfoSec* |

---

*`DA-005` · Category 03 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
