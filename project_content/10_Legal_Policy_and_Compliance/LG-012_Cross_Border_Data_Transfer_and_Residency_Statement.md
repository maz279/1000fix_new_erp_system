---
id: LG-012
title: Cross-Border Data Transfer and Residency Statement
project: 1000FiX ERP System v2.0
content_type: Legal / policy
template: TPL_Legal_Document.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Legal & Compliance with the Chief Data Officer and the CTO
author: Legal & Compliance with the Chief Data Officer, Enterprise Architecture and Platform Engineering
reviewers: [Legal Counsel, Chief Data Officer, CTO, CFO delegate, Enterprise Architect, Security lead, external data-protection adviser]
approver: Legal Counsel with the CTO
content_class: A
purpose: >
  The statement of which data is Bangladesh-resident, which may leave the country, the safeguards
  applied to each transfer and the register of sub-processors that receive it. NFR-086 replaced a
  single-region topology with split residency precisely because of this obligation, and a residency
  architecture the company cannot describe on paper is an architecture it cannot demonstrate to a
  regulator, a corporate client or a brand partner's auditor.
traces_to: [05-06 NFR-086, NFR-086a, NFR-086b, NFR-086c, NFR-099, NFR-090, NFR-094, NFR-095, NFR-098, 02-05, M29, M33, M60, M62, M65, M06, M12, M55, M21, LG-001, LG-005, LG-006, LG-008, LG-009, LG-010, LG-011, LG-017, LG-021, LG-024, UI-042, MD-013, BRU-SEC-13, BRU-SEC-14, BRU-SEC-15, BRU-SEC-08, BRU-CPM-06, BRU-DTS-16, BRU-MKP-19, BRU-GRC-18, FR-GRC-034, TS-017]
priority: P0
wave: W2
bilingual: yes
bn_counterpart: LG-012_Cross_Border_Data_Transfer_and_Residency_Statement_BN.md
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 §6.4 — NFR-086 split-residency data architecture with sensitive personally identifiable data in a Bangladesh-resident store joined by a resident key and never duplicated; NFR-086a field-level residency classification enforced at write time; NFR-086b Authority notification and documented safeguard before any cross-border transfer of a classified field; NFR-086c no unmasked residency-classified data in non-production in any region
    verified: 2026-08-12
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 §6.4 — the residency-restricted field table: National ID and passport number on fix.identity.document, TIN on fix.party and hr.employee, biometric attendance template on fix.attendance.record, recovered customer data and index on fix.recovered.inventory, marketplace seller KYC documents and criminal record checks on fix.mp.seller.document
    verified: 2026-08-12
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 §6.4 — audit finding C-05 recorded that the previous NFR-086 mandated a single approved region inherited from the v1.0 assumption of Singapore hosting, and that the position conflicted with NFR-099; dependency DEP-31 and decision D-13 record that a legal opinion on the split-residency design is required before the Wave 1 architecture is fixed
    verified: 2026-08-12
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M29 §9 BRU-SEC-13 a residency-classified field is written only to the Bangladesh-resident store and a write to the regional store fails; BRU-SEC-14 cross-border transfer is blocked until an Authority notification record and a documented safeguard exist; BRU-SEC-15 field-level encryption with separate key material
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M60 §5.4 FR-GRC-034 cross-border transfer register with basis, safeguards and destination consistent with the split-residency architecture; §9 BRU-GRC-18
    verified: 2026-08-18
    class: P1
  - source: Personal Data Protection Act 2026 and the Personal Data Protection (Amendment) Ordinance 2026 (Ordinance No. 23 of 2026, 5 February 2026) — restriction on large-scale transfer of sensitive personally identifiable data with Authority notification and disclosed safeguards, and an amended residency requirement obliging at least one synchronised real-time copy to be held within Bangladesh for data categorised as restricted or processed by critical information infrastructure as defined in the Cyber Security Ordinance 2025. **Secondary source. The applicability of the synchronised-copy requirement to this company, and the definition of "large-scale", are unverified and are pending G6**
    verified: 2026-08-18
    class: P2
supersedes: none
review_due: 2027-02-18
---

# LG-012 — Cross-Border Data Transfer and Residency Statement

| Item | Value |
|---|---|
| Document class | **Statement** — a published demonstration of conformance |
| Counterparty | The **Authority**, corporate clients, brand partners and their auditors, and data subjects |
| Governing law | **Bangladesh** |
| Effective date | On publication of version 1.0 — *pending G6 and pending decision D-13* |
| Acceptance capture method | **`AC-6` publication.** A statement is demonstrated, not agreed |
| Version accepted by users | n/a. **Every version is retained**, because it is the evidence of the position the company held at a point in time |
| External counsel review | **Required — G6**, and **the `05-06` DEP-31 legal opinion on the split-residency design is a prerequisite, not a parallel activity** |
| Bengali version | **Required.** `UI-042` tells customers in Bengali that their identifiers are stored in Bangladesh; this is the statement behind that sentence |

> ⚠ **Class A — statutory, and the file with the clearest upstream blocker in the register.**
>
> `05-06` audit finding **C-05** records that the previous `NFR-086` mandated a **single approved
> region, inherited from a v1.0 assumption of Singapore hosting**, and that the position
> **conflicted with `NFR-099`**. The architecture was corrected to split residency. **`DEP-31` and
> decision `D-13` record that a legal opinion on that design is required before the Wave 1
> architecture is fixed, and it has not been obtained.**
>
> `CG-013` `CR-08` states the content consequence in one line: *"`LG-008`, `LG-012` and every consent
> string may be wrong."*
>
> **This document therefore states the architecture as designed, the obligations as understood, and
> the gap between them — rather than asserting conformance the company cannot yet evidence.**
>
> **Conformance note.** All ten template sections retained in order. The field table is §4.3, the
> transfer register §4.5 and the sub-processor register §4.6, within §4 Terms. Gate questions and
> open items are §1.2 and §1.3 (`CP-09`).

---

## 1. Approval Record

| Role | Name | Date | Evidence |
|---|---|---|---|
| Drafted by | Legal & Compliance with CDO and Enterprise Architecture | 2026-08-18 | Draft issue v1.0 |
| G1 Editorial — Content Design | *pending* | | |
| G2 Factual — CTO with Enterprise Architect | *pending* | | |
| G4 Linguistic — independent reviewer, in context (`BN-018`) | *pending* | | |
| **G5 Legal — Legal Counsel** | *pending* | | **Required** |
| **G6 Statutory — external data-protection adviser** | *pending* | | **Required, blocking. `WV-02`: G6 can never be waived** |
| **Prerequisite — `DEP-31` / `D-13` split-residency legal opinion** | *pending* | | **Required before the Wave 1 architecture is fixed** |
| Approved by — Legal Counsel with CTO | *pending* | | |

### 1.2 Questions for the external adviser (G6)

| # | Question | Why it blocks |
|---|---|---|
| **RD1** ‡ | **Is the split-residency design sufficient?** Sensitive identifiers in a Bangladesh store, the remainder of the record in a regional store, joined by a resident key and never duplicated (`NFR-086`) | This is `D-13`. **If the answer is no, the Wave 1 architecture changes and every downstream statement changes with it** |
| **RD2** ‡ | **Does the amended residency requirement apply** — at least one synchronised real-time copy held within Bangladesh for restricted data, or data processed by critical information infrastructure as defined in the Cyber Security Ordinance 2025? | If it applies, §4.4 needs a synchronised-copy commitment the architecture does not currently describe |
| **RD3** ‡ | **Is the company critical information infrastructure**, or does it process for an entity that is? A national repair network serving hospitals, diagnostics and government clients is a plausible candidate | It determines `RD2` and imports a separate regulatory regime |
| **RD4** ‡ | **What is "large-scale" transfer** for the notification obligation, and is notification per transfer, per destination, per category or periodic? | §4.5 assumes a **per-destination registration with a per-transfer record**. A per-transfer notification duty would be operationally different |
| **RD5** ‡ | **What safeguards are accepted** — contractual clauses, an adequacy-style assessment, encryption with keys held in Bangladesh, or something prescribed? | §4.5.3 lists what the company intends to rely on |
| **RD6** ‡ | Is a **regional store outside Bangladesh** lawful for the non-sensitive remainder of a record about a Bangladeshi data subject? | The whole split-residency design assumes yes |
| **RD7** ‡ | Is disclosure to an **overseas brand partner** through `P08` a transfer requiring registration, and does a claim evidence pack count as large-scale where volumes are high? | `LG-005` §6.4 gates brand onboarding on this |
| **RD8** ‡ | Does **encryption with Bangladesh-held keys** remove data from the residency restriction, or is the ciphertext still resident data wherever it sits? | This is the single most consequential architectural question after `RD1` |
| **RD9** ‡ | Do **backups and disaster-recovery copies** of a Bangladesh-resident store have to remain in Bangladesh? | §4.4.4 assumes yes |
| **RD10** | Does **remote access from outside Bangladesh** — a vendor support engineer viewing a screen — constitute a transfer even where no data is copied? | §4.5.6 treats it as one |

### 1.3 Open items

| # | Open item | Blocking? | Owner |
|---|---|:--:|---|
| **O-01** | **`RD1`–`RD10` unanswered. Every `‡` position is provisional and `CG-012` `PR-04` blocks approval of a Class A file containing one** | **Yes — blocks `Approved` absolutely** | CDO with Legal Counsel |
| **O-02** | **`DEP-31` / `D-13` — the split-residency legal opinion — is outstanding and is a prerequisite to fixing the Wave 1 architecture** (`05-06` §6.4). `CG-013` `CR-08` records the content consequence | **Yes — blocks W1 architecture and this file** | CTO with Legal Counsel |
| **O-03** | **`RD2` and `RD3` are new since `05-06` was verified on 2026-08-12.** The amending Ordinance introduced a synchronised-in-country-copy requirement tied to the Cyber Security Ordinance 2025's critical-information-infrastructure definition. **`05-06` §6.4 does not reflect it, and `05-06` §6.1 lists the Ordinance without recording the amendment's residency effect.** This is an **upstream specification gap**, not a content gap | **Yes — `05-06` requires an update** | CTO with Enterprise Architecture |
| **O-04** | **The regional store's country is not named** in `05-06` or `02-05`. C-05 removed "Singapore" as an inherited assumption without replacing it. **A residency statement that cannot name where the non-resident half lives is not a statement** | **Yes — blocks §4.4 and §4.6** | CTO |
| **O-05** | **No sub-processor register exists.** `FR-GRC-034` provides for one in `M60`; `NFR-098` requires equivalent obligations to flow to every sub-processor. **§4.6 is a specification with no populated rows** | **Yes — blocks publication** | CDO with Procurement |
| **O-06** | **`BRU-SEC-13` requires a write of a residency-classified field to the regional store to *fail*.** That is a platform behaviour, not a policy. **Nothing evidences that it has been built or tested**; `TS-017` specifies residency verification | **Yes** | CTO with QA |
| **O-07** | **Third-party tags on customer surfaces are transfers.** `LG-011` §4.3 declares third-party analytics, chat, video and advertising rows. **Each is a cross-border transfer needing a §4.6 entry**, and `LG-011` `F6-06` points here | **Yes** | CDO with CTO |
| **O-08** | **`M65` multi-entity, multi-country and localisation is the module that would extend beyond Bangladesh.** A future second country makes this statement a multi-jurisdiction problem; **nothing yet states what happens then** | No — forward risk | CTO |

---

## 2. Scope and Parties

**In scope:** the residency classification of every field the platform holds; where each class is
stored; what may leave Bangladesh and on what basis; the transfer register; the sub-processor
register; the safeguards; non-production and backup positions; and the reconciliation with `LG-008`
and `LG-009` that check **F6** tests.

**Out of scope:**

| Subject | Owned by |
|---|---|
| Purposes and lawful bases | [`LG-008_Privacy_Notice_and_Consent_Copy.md`](LG-008_Privacy_Notice_and_Consent_Copy.md) §4.2 |
| How long each class is kept, and its deletion method | [`LG-009_Data_Retention_and_Deletion_Schedule.md`](LG-009_Data_Retention_and_Deletion_Schedule.md) |
| Disclosing transfers in an access response | [`LG-010_Data_Subject_Request_Handling_Content.md`](LG-010_Data_Subject_Request_Handling_Content.md) `T-2` |
| Third-party tags on web surfaces | [`LG-011_Cookie_and_Tracking_Policy.md`](LG-011_Cookie_and_Tracking_Policy.md) §4.3 — **but each is a transfer and belongs in §4.6** |
| Encryption, key management and access control as controls | [`LG-021_ISMS_Policy_Set.md`](LG-021_ISMS_Policy_Set.md) |
| Recovered customer data handling | [`LG-017_Data_Recovery_and_Secure_Destruction_Terms.md`](LG-017_Data_Recovery_and_Secure_Destruction_Terms.md) |
| The physical topology, regions and failover design | `02-05` architecture and `05-06` §6.4 — **this file states the legal position, not the design** |
| The obligation register and regulator notifications | [`LG-024_Regulatory_Disclosure_and_Statutory_Notice_Register.md`](LG-024_Regulatory_Disclosure_and_Statutory_Notice_Register.md) |

---

## 3. Definitions

| Term | Meaning |
|---|---|
| **Residency-restricted field** | A field that must be written **only** to the Bangladesh-resident store. A write to the regional store **fails** (`BRU-SEC-13`, `NFR-086a`) |
| **Bangladesh-resident store** | A data store physically located in Bangladesh |
| **Regional store** | A data store outside Bangladesh holding the non-restricted remainder of records — **its country is `O-04`** |
| **Resident key** | The identifier joining a record across the two stores. **The sensitive field is never duplicated to make the join work** (`NFR-086`) |
| **Transfer** | Any movement, copy, replication, remote view or disclosure of personal data outside Bangladesh, **including remote access where no copy is made** (`RD10`) |
| **Registered transfer** | A transfer with an **Authority notification record and a documented safeguard, both existing before the transfer executes** (`NFR-086b`, `BRU-SEC-14`) |
| **Sub-processor** | Any party a processor engages. **Equivalent obligations flow to it by contract** (`NFR-098`, `BRU-GRC-18`) |
| **‡** | A position resting on a secondary source, unverified, **pending G6** |

---

## 4. Terms

### 4.1 The statement

**The company holds sensitive personally identifiable data about Bangladeshi data subjects in
Bangladesh, and does not transfer it out.** The remainder of a record may be held in a regional
store. Where any personal data leaves Bangladesh, it does so only under a registered transfer with a
documented safeguard.

**That is the position the architecture is designed to deliver. §4.7 states honestly what is not yet
evidenced.**

### 4.2 The rules

| # | Rule |
|---|---|
| **RD-R1** | **Residency is a property of a field, carried in the data model and enforced at write time — not by convention** (`NFR-086a`) |
| **RD-R2** | **A write of a residency-restricted field to the regional store fails.** It does not warn, log and proceed (`BRU-SEC-13`) — **`O-06`: unevidenced** |
| **RD-R3** | **A restricted field is never duplicated across the boundary to make a join convenient.** Records join by a resident key (`NFR-086`) |
| **RD-R4** | **No cross-border transfer of a classified field executes without an Authority notification record and a documented safeguard already in place** (`NFR-086b`, `BRU-SEC-14`). The gate precedes the transfer |
| **RD-R5** | **Restricted fields are encrypted at field level with key material separate from the database key** (`BRU-SEC-15`), and the keys are held in Bangladesh — **subject to `RD8`** |
| **RD-R6** | **Non-production environments never contain unmasked residency-classified data in any region** (`NFR-086c`, `BRU-SEC-08`) |
| **RD-R7** | **Every transfer is registered with its basis, safeguards and destination** (`FR-GRC-034`, `BRU-GRC-18`) |
| **RD-R8** | **A processor's or sub-processor's processing is the company's own** (`NFR-098`). Engaging one transfers no responsibility |
| **RD-R9** | **A remote view is a transfer** (`RD10`). A support engineer abroad seeing a screen containing personal data has received it |
| **RD-R10** | **Where a restricted field is requested by a counterparty, the answer is no**, and the evidential need is met another way (`LG-005` §6.5) |

### 4.3 The residency classification — field by field

> **This table must be identical to `LG-008` §4.2's residency column and to `05-06` §6.4. That
> identity is the F6 axis.**

**Bangladesh-resident only — never leaves, never replicated regionally:**

| Field | Entity | Owning module | Basis | Also |
|---|---|---|---|---|
| **National ID number** | `fix.identity.document` | `M33` | `NFR-086`, `BRU-CPM-06` | `S3`; `T5`; visible to finance and compliance roles only (`05-04` §5) |
| **Passport number** | `fix.identity.document` | `M33` | `NFR-086` | `S3` |
| **TIN** | `fix.party`, `hr.employee` | `M33`, `M21` | `NFR-086` | `S3`; **appears on statutory outputs and is disclosed to the NBR through filings** — see `LG-008` §4.7.1 |
| **Biometric attendance template** | `fix.attendance.record` | `M55` | `NFR-086` | `S3`; **irreversible template, never exported** (`05-02` §10); deleted at termination (`LG-009` `RC-13`) |
| **Recovered customer data and its index** | `fix.recovered.inventory` | `M06` | `NFR-086`, **`BRU-DTS-16`** | **`BRU-DTS-16` is explicit: may not be replicated to a foreign region.** Per-case keys; dual control |
| **Marketplace seller KYC documents** | `fix.mp.seller.document` | `M12` | `NFR-086`, `BRU-MKP-19` | `S3`; `T5`; allow-list access, step-up authentication, logged |
| **Criminal-record checks, where collected** | `fix.mp.seller.document` | `M12` | `NFR-086` | `S3`; **lawfulness and retention are `LG-008` `PN8` and `LG-009` `RT6`** |

**Additional fields the company classifies as restricted beyond the `05-06` list:**

| Field | Entity | Why | Status |
|---|---|---|---|
| **Bank account details** | `fix.party`, `hr.employee` | `S3` in `05-02` §10; a payment instrument for a Bangladeshi individual | **Proposed addition — `RD1` scope question.** `05-06` §6.4 does not list it |
| **Individual payroll and payslip** | `hr.payslip`, `fix.salary.structure` | `S3`; employment data of Bangladeshi employees | **Proposed addition** |

> **`CL-01`. Two proposed additions are declared rather than silently added.** `05-06` §6.4 is the
> authoritative field list, and this file may not extend it unilaterally — `CG-013` `T-B04` makes
> contradicting an approved specification an escalation. **The additions are put to `RD1` and to
> Enterprise Architecture as a question, and until answered the `05-06` list governs.**

**May be held in the regional store:**

Service orders and work orders, device records and history, diagnosis and repair notes, evidence
photographs, contracts and entitlements, invoices and payment tokens, notification logs, contact
records and call recordings, complaints, loyalty and referral records, inventory and procurement
data, analytics datasets, and audit and access logs — **subject to `RD6` and to `O-04` naming the
region.**

### 4.4 Where data lives

| Store | Contents | Location | Backups |
|---|---|---|---|
| **Bangladesh-resident store** | Every field in §4.3 | **Bangladesh** | **In Bangladesh — `RD9`** |
| **Regional store** | The remainder | **`O-04` — not named in any approved specification** | Same region |
| **Non-production** | Masked data only; **never unmasked restricted data in any region** (`NFR-086c`) | Either | Not applicable |
| **Backups and disaster recovery** | Mirrors the store they protect | **A backup of the resident store stays in Bangladesh** (§4.4.4) | — |
| **Third-party processors** | Only what §4.6 registers | Per §4.6 | Per processor |

| # | Rule |
|---|---|
| **4.4.1** | **The resident store is authoritative for its fields.** No regional cache, no read replica, no search index holds them |
| **4.4.2** | **A search index is a copy.** Full-text search over restricted fields, if required, runs in Bangladesh |
| **4.4.3** | **A log is a copy.** Classified fields are redacted from logs at emission (`BRU-SEC-24`), so a regional log aggregator does not become a residency breach |
| **4.4.4** | **A backup of the resident store remains in Bangladesh** — `RD9` |
| **4.4.5** | **A synchronised in-country copy requirement, if `RD2` applies, is an additional commitment this section does not currently make** (`O-03`) |

### 4.5 The transfer register

> `FR-GRC-034` provides the register in `M60`. **This is its content specification and its governing
> rules.** Every transfer of personal data outside Bangladesh has a row **before** it happens.

| Field | Notes |
|---|---|
| `transfer_id` | Immutable |
| `data_categories` | Which categories — **never a restricted field (`RD-R10`)** |
| `purpose` | The `LG-008` §4.2 purpose reference |
| `destination_country` | Named |
| `recipient` | Named entity, not a category |
| `recipient_role` | Controller / processor / sub-processor |
| `basis` | The lawful basis for the transfer ‡ |
| `safeguard` | §4.5.3 |
| `authority_notification_ref` | **Where notification is required. `BRU-SEC-14` blocks the transfer until it exists** |
| `volume_class` | Whether it is "large-scale" — **`RD4`** |
| `registered_on` / `reviewed_on` | Registration and review dates |
| `status` | Active / suspended / ended |

**Transfers currently anticipated — every row unregistered:**

| # | Transfer | Recipient | Purpose | Status |
|---|---|---|---|---|
| **TR-01** | Non-restricted record fields to the regional store | The company's own regional infrastructure | Platform operation | **Unregistered. Region unnamed (`O-04`)** |
| **TR-02** | Warranty claim data and evidence packs to overseas brand partners | 17+ brand partners | `LG-008` `P-07` | **Unregistered. `LG-005` §6.4 gates onboarding on this. `RD7`** |
| **TR-03** | Notification delivery — SMS, WhatsApp, email, push | Messaging providers | `P-04`, `P-05` | **Unregistered** |
| **TR-04** | Payment processing tokens and transaction references | Gateways | `P-03` | **Unregistered.** Card data is not stored (`BRU-ARB-25`) |
| **TR-05** | Third-party tags — analytics, chat, video, advertising | Per `LG-011` §4.3 | `P-01`, `P-05` | **Unregistered — `O-07`** |
| **TR-06** | AI model inference for the assistant | Model service | `P-13` | **Unregistered.** `BRU-DTS-14`: recovered data is never training data |
| **TR-07** | Remote support access by an overseas vendor engineer | Software vendors | Platform support | **Unregistered — `RD10`, `RD-R9`** |
| **TR-08** | Cloud infrastructure management-plane metadata | Cloud provider | Platform operation | **Unregistered** |

| # | Rule |
|---|---|
| **4.5.1** | **A transfer with no row does not happen.** The row precedes the traffic (`RD-R4`) |
| **4.5.2** | **A restricted field never appears in a row.** If a transfer would need one, the transfer is redesigned (`RD-R10`) |
| **4.5.3** | **Safeguards the company relies on** — subject to `RD5`: contractual data-protection terms flowing equivalent obligations (`NFR-098`); encryption in transit and at rest with keys held in Bangladesh (`BRU-SEC-15`); purpose and volume limitation; access logging (`EA-10`); a right to audit; deletion or return on termination; and onward-transfer restriction |
| **4.5.4** | Registered transfers are **reviewed at least annually**, and on any change of recipient, purpose, volume or destination |
| **4.5.5** | **A suspended transfer stops.** The Authority may order suspension, and the platform must be able to stop a transfer without stopping the service that depends on it — **a design requirement this file raises** |
| **4.5.6** | **Remote access from outside Bangladesh is a transfer** and is registered (`TR-07`) |

### 4.6 The sub-processor register — **specified, unpopulated (`O-05`)**

| Field | Notes |
|---|---|
| `processor` / `sub_processor` | Named entity and its parent |
| `service` | What it does |
| `data_categories` | What it receives |
| `location` | Where it processes, and where it stores |
| `transfer_ref` | The §4.5 row that authorises it |
| `contract_ref` | The instrument flowing equivalent obligations (`NFR-098`) |
| `security_evidence` | Certification or assessment held (`NFR-097`) |
| `onward_transfers` | Its own sub-processors — **`RD-R8` reaches them too** |
| `added_on` / `notice_given` | **Adding a sub-processor is notified to affected counterparties** |
| `exit_plan` | Deletion or return on termination |

| # | Rule |
|---|---|
| **4.6.1** | **The register is published as part of this statement.** A sub-processor register that exists internally and is not disclosed does not discharge a disclosure obligation |
| **4.6.2** | **Adding a sub-processor is a MAJOR change** to this statement (§9.2) and is notified |
| **4.6.3** | **A sub-processor that will not accept equivalent obligations is not engaged** |
| **4.6.4** | Every third-party row in `LG-011` §4.3 has an entry here (`LG-011` `F6-06`, `O-07`) |
| **4.6.5** | **A processor cannot use a further sub-processor without disclosure**, and `LG-005` §4.3.3, `LG-006` §6.4 and `LG-007` §6.3 all impose that upward |

### 4.7 What is not yet evidenced — stated plainly

> **`CL-02`. `CG-012` `EX-01` requires a claim that an artefact exists to be verified by checking
> that it exists.** Applied to a residency statement, that means the company may not claim
> conformance it has not demonstrated. The list below is what a regulator, a corporate client or a
> brand auditor would ask for, and what the answer currently is.

| What conformance requires | Status today |
|---|---|
| A legal opinion that the split-residency design satisfies the obligation | **Not obtained** — `DEP-31`, `D-13`, `O-02` |
| The regional store's country named in an approved specification | **Not named** — `O-04` |
| Field-level residency classification present in the data model | Specified (`NFR-086a`); **build unevidenced** |
| A write of a restricted field to the regional store demonstrably failing | **Unevidenced** — `O-06`; `TS-017` specifies the test |
| A populated transfer register | **Empty** — eight anticipated transfers, none registered |
| A populated and published sub-processor register | **Does not exist** — `O-05` |
| Authority notification records where required | **None** — and `RD4` has not established when they are required |
| Confirmation that the synchronised in-country copy requirement does or does not apply | **Not established** — `RD2`, `RD3`, `O-03` |
| Non-production masking verified in every region | Specified (`NFR-086c`, `BRU-SEC-08`); **unevidenced** |

| # | Rule |
|---|---|
| **4.7.1** | **This section is republished with every version, updated, until it is empty.** It is the honest half of the statement and is not removed for presentation |
| **4.7.2** | **The statement is not published externally while §4.7 contains a blocking row.** Internally it circulates as the position of record; **externally an unqualified claim would be a misstatement** |

---

## 5. Liability, Exclusions and Limits

| # | Clause |
|---|---|
| **5.1** | This statement creates no contractual limitation |
| **5.2** | **A transfer executed without a registered basis and a documented safeguard is a breach** exposed to the penalties in `LG-008` §5.2, and the Authority may order suspension of transfers |
| **5.3** | **`RD-R8`: engaging a processor transfers no responsibility.** No clause in `LG-004`, `LG-005`, `LG-006` or `LG-007` should be read as moving the company's statutory position |
| **5.4** | **A misstatement in this document is worse than a gap.** A corporate client relying on a residency claim in a tender, or a brand partner relying on it in an audit, is relying on a statement that must be true — which is why §4.7 exists |
| **5.5** | Where a counterparty's breach causes an unlawful transfer, the company's recovery is under that counterparty's indemnity, and **its own liability to the Authority is unaffected** |

---

## 6. Data Protection

> Must reconcile with `LG-008` and `LG-009`. Check **F6**.

| Axis | This file | Reconciles with |
|---|---|---|
| **Residency-restricted field list** | §4.3, seven fields from `05-06` §6.4 plus **two declared proposals** | **`LG-008` §4.2 residency column; `05-06` §6.4; `MD-013` `PTY-05`** — the seven must be identical; the two proposals are marked as proposals |
| Transfers per purpose | §4.5 `TR-01`…`TR-08` | **`LG-008` `P-01`…`P-20`** — every transfer names its purpose |
| Sub-processors | §4.6 | **`LG-008` `PI-04`; `LG-011` §4.3 third-party rows** |
| Backups and non-production | §4.4 | **`LG-009` `RC-26`, `RC-27`** |
| Recovered data | §4.3, `BRU-DTS-16` | **`LG-017` §4; `LG-009` `RC-09`** |
| Customer-facing residency wording | §4.3 TIN row | **`LG-008` §4.7.1 and the `UI-042` change request** — *"stored in Bangladesh"* is right, *"not shared"* is wrong for TIN |
| Breach notification | §4.5.5 suspension; `NFR-094` | **`LG-008` §4.8** |

| # | Rule |
|---|---|
| **F6-08** | **A change to §4.3 re-opens `LG-008` §4.2, `LG-009` §4.2 and `05-06` §6.4** — and a change originating here that contradicts `05-06` is escalated under `T-B04`, never applied locally |
| **F6-09** | **A new sub-processor or transfer re-opens `LG-011` §4.3 and every counterparty document with a data clause** |

---

## 7. Termination and Consequences

| Event | Consequence |
|---|---|
| **A processor relationship ends** | Data is returned or deleted per the exit plan (§4.6), evidenced; the transfer row is set to `ended`, **not deleted** |
| **The Authority orders suspension of a transfer** | The transfer stops. §4.5.5 requires the platform to be able to stop it without stopping the dependent service |
| **A sub-processor is replaced** | MAJOR change: notice, register update, republication |
| **The regional store moves country** | **MAJOR change**, re-opens G5 and G6, and re-registers every affected transfer |
| **A restricted field is added to `05-06` §6.4** | Existing regional copies must be migrated to the resident store and the regional copies destroyed. **A classification change is a data-migration event, not a documentation edit** |
| **This statement is superseded** | Prior versions are retained permanently (`LG-009` `DC-23`), because they evidence the position held when a transfer was made |

---

## 8. Dispute Resolution

| Step | Route |
|---|---|
| **1 — Internal challenge to a classification** | Enterprise Architecture with the CDO; a change to `05-06` follows `T-B04` |
| **2 — Client or auditor challenge** | Legal Counsel with the CTO, producing the register and the §4.7 position |
| **3 — Authority engagement** | Legal Counsel with the CDO; **notifications and correspondence are recorded in `LG-024`** |
| **4 — Courts** | The courts of Dhaka, Bangladesh |

---

## 9. Change Control

| Version | Date | Change | Notice given to users | Re-acceptance required |
|---|---|---|---|:--:|
| 1.0 | 2026-08-18 | Initial issue — draft. **Blocked on `D-13`, on G6, and on §4.7** | n/a | n/a |

| # | Rule |
|---|---|
| **9.1** | A change to §4.3, §4.4, §4.5 or §4.6 is **MAJOR** |
| **9.2** | **Adding a sub-processor is MAJOR and is notified to affected counterparties** (§4.6.2) |
| **9.3** | A statutory change re-opens **G2, G5 and G6**, and re-opens `LG-008` and `LG-009` |
| **9.4** | **Every version is retained permanently** (`LG-009` `DC-23`) |
| **9.5** | **12 months without a trigger re-opens G6** (`CG-006` §4.2) |
| **9.6** | **`RD1`, `RD2` and `RD8` answers are each MAJOR by definition**, and any of them may change the Wave 1 architecture rather than this document |

---

## 10. Cross-References

| Document | Relationship | Must not contradict |
|---|---|---|
| [`LG-008_Privacy_Notice_and_Consent_Copy.md`](LG-008_Privacy_Notice_and_Consent_Copy.md) | Residency column; transfers per purpose | Check **F6** — identical field lists |
| [`LG-009_Data_Retention_and_Deletion_Schedule.md`](LG-009_Data_Retention_and_Deletion_Schedule.md) | Backups, non-production, `DM-3` crypto-erase | `RC-26`, `RC-27` |
| [`LG-010_Data_Subject_Request_Handling_Content.md`](LG-010_Data_Subject_Request_Handling_Content.md) | `T-2` discloses recipients and transfers | The register is what is disclosed |
| [`LG-011_Cookie_and_Tracking_Policy.md`](LG-011_Cookie_and_Tracking_Policy.md) | **`F6-06` — every third-party tag is a transfer** | §4.6 entries |
| [`LG-005_Brand_Partner_Portal_Terms.md`](LG-005_Brand_Partner_Portal_Terms.md) | **§6.4 gates `P08` onboarding on `TR-02`** | Registration before disclosure |
| [`LG-006_Vendor_Portal_Terms_and_Supplier_Code_of_Conduct.md`](LG-006_Vendor_Portal_Terms_and_Supplier_Code_of_Conduct.md) · [`LG-007_Referral_and_Alliance_Partner_Agreement.md`](LG-007_Referral_and_Alliance_Partner_Agreement.md) | Overseas counterparties | §6 transfer gates |
| [`LG-017_Data_Recovery_and_Secure_Destruction_Terms.md`](LG-017_Data_Recovery_and_Secure_Destruction_Terms.md) | **`BRU-DTS-16` — recovered data never replicated abroad** | The absolute prohibition |
| [`LG-021_ISMS_Policy_Set.md`](LG-021_ISMS_Policy_Set.md) | `RD-R5` encryption and key location | Key management |
| [`LG-024_Regulatory_Disclosure_and_Statutory_Notice_Register.md`](LG-024_Regulatory_Disclosure_and_Statutory_Notice_Register.md) | Authority notifications as tracked obligations | Notification records |
| [`../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-013_Customer_and_Party_Master_Standard.md`](../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-013_Customer_and_Party_Master_Standard.md) | `PTY-05` — `S3` fields to the resident store | The field classification |
| [`../03_UI_Copy_and_Microcopy/03D_Critical_Flows/UI-042_Consent_Privacy_and_Preference_Centre_Copy.md`](../03_UI_Copy_and_Microcopy/03D_Critical_Flows/UI-042_Consent_Privacy_and_Preference_Centre_Copy.md) | The customer-facing residency sentence | `LG-008` §4.7.1 change request |
| `TS-017` Security and Privacy Test Case Pack | **Where `RD-R2` and `NFR-086c` are actually verified** | Residency verification tests |
| `05-06` §6.4 · `02-05` architecture | **The upstream authority. `O-03` and `O-04` are gaps in it, not in this file** | `T-B04` — never contradicted locally |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Legal_Document.md` — ten sections in order; additions declared
- [x] **Seven residency-restricted fields reproduced exactly from `05-06` §6.4**, with two proposed additions **declared as proposals rather than added** (`CL-01`)
- [x] Ten residency rules stated, each traced to an `NFR` or a `BRU`
- [x] **Transfer register specified to field level, with eight anticipated transfers enumerated and all marked unregistered**
- [x] **Sub-processor register specified, with the disclosure obligation stated**
- [x] **§4.7 states what is not yet evidenced, and §4.7.2 prohibits external publication while a blocking row stands** (`CL-02`, `EX-01`)
- [x] **The `05-06` gap on the amended residency requirement raised as an upstream finding** (`O-03`), not silently absorbed
- [x] All internal links resolve
- [ ] **`DEP-31` / `D-13` split-residency legal opinion obtained** — outstanding. **A prerequisite, not a parallel activity**
- [ ] **G6 external verification** — outstanding. `WV-02`: cannot be waived
- [ ] **`RD1`–`RD10` answered; every `‡` position verified** — outstanding; `PR-04` blocks approval
- [ ] **The regional store's country named in an approved specification** — outstanding, `O-04`
- [ ] **Transfer and sub-processor registers populated** — outstanding, `O-05`, `O-07`
- [ ] **`BRU-SEC-13` write-failure behaviour evidenced by test** — outstanding, `O-06`
- [ ] **Bengali counterpart authored and signed off in context** — outstanding
- [ ] Named approver recorded — pending
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
