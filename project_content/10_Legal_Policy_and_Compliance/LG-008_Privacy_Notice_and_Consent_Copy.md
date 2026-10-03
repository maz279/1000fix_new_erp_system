---
id: LG-008
title: Privacy Notice and Consent Copy
project: 1000FiX ERP System v2.0
content_type: Legal / policy
template: TPL_Legal_Document.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Legal & Compliance with the Chief Data Officer
author: Legal & Compliance with the Chief Data Officer, Content Design and Enterprise Architecture
reviewers: [Legal Counsel, Chief Data Officer, CTO, CFO delegate, HR Director, Content Design Lead, Localisation Lead, Accessibility reviewer, external data-protection adviser]
approver: Legal Counsel with the Chief Data Officer
content_class: A
purpose: >
  The transparency notice the company is required to issue before or during processing, and the
  operative consent wording relied on for lawfulness — stating for every processing purpose the
  data categories, the lawful basis, the retention, the recipients, the residency and how a data
  subject exercises their rights. Notice text is operative legal content, not marketing copy: a
  purpose processed without a stated basis and a presented notice is unlawful processing, whatever
  the system does correctly around it.
traces_to: [05-06 NFR-086, NFR-090, NFR-091, NFR-092, NFR-093, NFR-094, NFR-095, NFR-096, NFR-097, NFR-098, NFR-099, M33, M60, M29, M24, M06, M12, M27, M32, M55, LG-001, LG-009, LG-010, LG-011, LG-012, LG-016, LG-017, LG-020, LG-021, UI-042, MD-013, DT-002, HC-019, BRU-CPM-06, BRU-CPM-07, BRU-CPM-08, BRU-CPM-09, BRU-CPM-10, BRU-CPM-11, BRU-CPM-15, BRU-CPM-16, BRU-GRC-16, BRU-GRC-17, BRU-SEC-05, BRU-SEC-13, BRU-DTS-14, BRU-DTS-16, BRU-DTS-17, BRU-DTS-18, BRU-MKP-19, BRU-TAX-19, FR-GRC-033, FR-GRC-037]
priority: P0
wave: W2
bilingual: yes
bn_counterpart: LG-008_Privacy_Notice_and_Consent_Copy_BN.md
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 §6.1 statutory currency table — Personal Data Protection Act 2026 (Law 63 of 2026) in force, enacted April 2026, complaint and enforcement mechanisms activating approximately 13 May 2027; Personal Data Protection Ordinance 2025 issued 6 November 2025 and amended by Ordinance No. 23 of 2026 on 5 February 2026
    verified: 2026-08-12
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 §6.3 NFR-090 … NFR-099 — the statutory obligations restated as testable requirements, with the National Data Management Authority named as regulator and penalty exposure of BDT 25 lakh, rising to BDT 50 lakh for a significant data fiduciary
    verified: 2026-08-12
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 §6.4 NFR-086, NFR-086a–c and the residency-restricted field table — National ID, passport, TIN, biometric attendance template, recovered customer data and index, marketplace seller KYC documents, criminal record checks
    verified: 2026-08-12
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/B_Customer_Engagement_and_Experience/M33 §9 BRU-CPM-06 … BRU-CPM-16 — residency, recorded lawful basis, consent invalid without the notice version, immediate withdrawal, 30-day rectification notification, erasure override, five-year processing records, minors
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02 §10 data classification S0–S3 and the S3 field inventory
    verified: 2026-08-18
    class: P1
  - source: project_content/03_UI_Copy_and_Microcopy/03D_Critical_Flows/UI-042_Consent_Privacy_and_Preference_Centre_Copy.md §3 consent, purpose, preference and rights copy, and §9 open questions asking this file to confirm the residency wording and the invoice retention period
    verified: 2026-08-18
    class: P1
  - source: Personal Data Protection Act 2026 as summarised by published legal analysis — consent defined as clear, explicit, specific and freely given; data-subject rights including access, portability, rectification, erasure and withdrawal; children defined as under 18 with verifiable parental consent; processing records for at least five years; National Data Management Authority as regulator. **Secondary source. Section-level content is unverified and every clause marked with a section reference is pending G6 verification against the enacted instrument**
    verified: 2026-08-18
    class: P2
supersedes: none
review_due: 2027-02-18
---

# LG-008 — Privacy Notice and Consent Copy

| Item | Value |
|---|---|
| Document class | **Notice** — a transparency notice, plus the operative consent wording |
| Counterparty | **Every data subject**: customers, technicians and employees, corporate portal users, sellers, riders, partners, brand-partner contacts, applicants, visitors |
| Governing law | **Bangladesh** |
| Effective date | On publication of version 1.0 — *pending G6* |
| Acceptance capture method | **`AC-6` publication for the notice; `AC-5` per-purpose consent for the consent strings.** A notice is presented, not agreed. **Accepting portal terms is not consent** (`LG-001` `LR-08`) |
| Version accepted by users | **The notice version presented is recorded with every consent** — `BRU-CPM-08` invalidates consent recorded without it |
| External counsel review | **Required — G6.** A named external data-protection adviser must confirm conformance against the enacted instrument |
| Bengali version | **Required and operative.** Bengali is the default presentation on customer and field surfaces (`PS-03`), so **the Bengali notice is the notice most data subjects will actually read** |

> ⚠ **Class A — statutory. This is the highest-consequence file in Category 10.**
>
> Bangladesh has a binding personal-data statute in the company's own jurisdiction, enacted since
> the programme began. `05-06` §6.3 already restates its obligations as ten testable requirements
> and records penalty exposure of **BDT 25 lakh, rising to BDT 50 lakh for a significant data
> fiduciary**, as programme risk `RSK-032`. **`AUDIT-010` finding HC-01 is the first finding in ten
> audits about the lawfulness of the work rather than its correctness, and it points here.**
>
> **What this file is not.** It is not a page about how much the company values privacy. Every
> sentence in §4.2 is either true of the system or a misstatement to a regulator.
>
> **Conformance note.** All ten template sections retained in order. The processing inventory is
> §4.2 and the consent register §4.3, both within §4 Terms. Gate questions and open items are §1.2
> and §1.3 (`CP-09`).

---

## 1. Approval Record

| Role | Name | Date | Evidence |
|---|---|---|---|
| Drafted by | Legal & Compliance with the Chief Data Officer | 2026-08-18 | Draft issue v1.0 |
| G1 Editorial — Content Design | *pending* | | |
| G2 Factual — CDO with Enterprise Architecture | *pending* | | |
| G4 Linguistic — independent reviewer, in context (`BN-018`) | *pending* | | |
| **G5 Legal — Legal Counsel** | *pending* | | **Required** |
| **G6 Statutory — external data-protection adviser** | *pending* | | **Required, blocking. `WV-02`: G6 can never be waived** |
| Approved by — Legal Counsel with CDO | *pending* | | |

> **`CG-012` `PR-04`: a provisional claim in a Class A file blocks approval. There is no
> provisional route for statutory content.** Every clause below carrying a `‡` marker rests on a
> secondary source and **must be verified against the enacted instrument at G6** before this file
> can leave `Draft`.

### 1.2 Questions for the external adviser and Legal Counsel (G6, G5)

| # | Question | Gate |
|---|---|---|
| **PN1** ‡ | Is the company a **"significant" data fiduciary**? If so, a Chief Data Officer appointment with defined authority and reporting line is mandatory (`NFR-096`), and the penalty ceiling doubles | G6 |
| **PN2** ‡ | Does the notice in §4.2 contain **every mandated element in the mandated form**? `NFR-092` lists categories, purposes, risks, retention, third-party transfers and the withdrawal procedure — **"risks" is an element the company has not previously drafted for** | G6 |
| **PN3** ‡ | What is the **prescribed breach-notification timeframe** to the National Data Management Authority, and what threshold constitutes "likely to cause significant damage"? (`NFR-094`) | G6 |
| **PN4** ‡ | Which of the §4.3 purposes may lawfully rest on a **legitimate ground** rather than consent, and specifically: service delivery, fraud prevention, service-quality analytics, and staff monitoring | G6 + G5 |
| **PN5** ‡ | Is **anonymised transcript and chat-log reuse** for content authoring and model training within the consent basis on which the data was collected? **This is `AUDIT-010` HC-01 and it gates `HC-015` at W2 and `HC-017` collection at W2** | G6 + G5 |
| **PN6** ‡ | Is the **split-residency design** (`NFR-086`) sufficient, and does the amended residency requirement — a synchronised real-time copy held in Bangladesh for restricted or critical-infrastructure-processed data — apply to this company? **`05-06` DEP-31 / D-13 and `CG-013` `CR-08`** | G6 |
| **PN7** ‡ | Is **biometric attendance** processing lawful, and on what basis, given biometric identifiers are a heightened category? (`M55`, `05-06` §6.4) | G6 + G5 |
| **PN8** ‡ | Is a **criminal-record check on a marketplace seller** lawful to collect and retain, and for how long? (`05-06` §6.4, `LG-004` `MP8`) | G6 + G5 |
| **PN9** | Is the §4.5.2 **automated-decision** disclosure adequate for seller visibility reduction (`BRU-MKP-06`), credit hold (`BRU-ARB-13`) and fraud scoring (`BRU-WTY-21`)? | G5 |
| **PN10** ‡ | Does the **child** definition of under-18 with verifiable parental consent require a hard age gate at registration, or is a declared-age model sufficient? | G6 |

### 1.3 Open items

| # | Open item | Blocking? | Owner |
|---|---|:--:|---|
| **O-01** | **`PN1`–`PN10` unanswered. Every `‡` clause is provisional and `PR-04` blocks approval** | **Yes — blocks `Approved` absolutely** | CDO with Legal Counsel |
| **O-02** | **The split-residency legal opinion is outstanding** (`05-06` DEP-31, decision D-13, `CG-013` `CR-08`). `CR-08` states the consequence plainly: *"`LG-008`, `LG-012` and every consent string may be wrong"* | **Yes — blocks W1 architecture fix and this file** | CTO with Legal Counsel |
| **O-03** | **`AUDIT-010` HC-01 is unresolved and this file is the resolution point** (`PN5`). Three Category 09 files depend on it, and `HC-015` transcript mining is scheduled at **W2** | **Yes — blocks `HC-015`, `HC-017`, `HC-019`** | Legal Counsel with CDO |
| **O-04** | **`NFR-092` requires the notice to state the *risks* of processing.** No programme document has drafted risk statements for a data subject. §4.2 carries a `risks` column populated to the company's current understanding and **it is the least-verified column in the file** | **Yes** | CDO |
| **O-05** | The Chief Data Officer role is referenced across the module register (`BRU-CPM-07`…`BRU-CPM-16` name `CDO` as rule owner) but **no appointment is recorded**. `CG-013` `CR-03` records the analogous gap for the Content Lead | **Yes — every rule in `M33` §9 has no owner** | CEO |
| **O-06** | **Marketing consent for existing customers migrated from legacy systems has no consent record.** `DM-004` migrates customer data; a migrated contact with no recorded consent cannot lawfully receive marketing | **Yes — blocks marketing at W2** | CDO with Data Migration Lead |
| **O-07** | `UI-042` §9 asks this file two questions. **Both are answered in §4.7.1 and §4.7.2** — recorded here as an inbound resolution | No — resolved | — |

---

## 2. Scope and Parties

| Party | Role |
|---|---|
| **1000FiX Services Limited** | The **data fiduciary** (controller) for the processing in §4.2, except where §4.2 states otherwise |
| **The data subject** | Any natural person whose personal data the company processes |

**In scope:** every processing purpose the ERP and its twelve portals perform; the lawful basis for
each; the consent wording relied on; the rights statement; the residency position summarised from
`LG-012`; and the boundary with `UI-042`.

**Out of scope:**

| Subject | Owned by |
|---|---|
| **How long each data class is kept, and how it is deleted** | [`LG-009_Data_Retention_and_Deletion_Schedule.md`](LG-009_Data_Retention_and_Deletion_Schedule.md) — §4.2 cites it and never restates a period |
| **Handling a rights request** — intake, verification, templates, refusal grounds, timelines | [`LG-010_Data_Subject_Request_Handling_Content.md`](LG-010_Data_Subject_Request_Handling_Content.md) |
| **Cookies and similar technologies** | [`LG-011_Cookie_and_Tracking_Policy.md`](LG-011_Cookie_and_Tracking_Policy.md) |
| **What may leave Bangladesh, the safeguards and the sub-processor register** | [`LG-012_Cross_Border_Data_Transfer_and_Residency_Statement.md`](LG-012_Cross_Border_Data_Transfer_and_Residency_Statement.md) |
| **The security controls behind §4.6** | [`LG-021_ISMS_Policy_Set.md`](LG-021_ISMS_Policy_Set.md) |
| **In-product wording, keys, character budgets and screen placement** | [`../03_UI_Copy_and_Microcopy/03D_Critical_Flows/UI-042_Consent_Privacy_and_Preference_Centre_Copy.md`](../03_UI_Copy_and_Microcopy/03D_Critical_Flows/UI-042_Consent_Privacy_and_Preference_Centre_Copy.md) — §4.7 sets the boundary |
| Recovered customer data under a data-services case | [`LG-017_Data_Recovery_and_Secure_Destruction_Terms.md`](LG-017_Data_Recovery_and_Secure_Destruction_Terms.md) |
| Employee monitoring detail and internal access rules | [`LG-020_Acceptable_Use_and_Internal_Access_Policy.md`](LG-020_Acceptable_Use_and_Internal_Access_Policy.md) |

---

## 3. Definitions

| Term | Meaning in this notice |
|---|---|
| **Personal data** | Information relating to an identified or identifiable natural person |
| **Sensitive / restricted personal data** | The heightened categories: government unique identifiers (National ID, passport, TIN), biometric identifiers, genetic information and criminal-record data. In the company's own classification these are **`S3`** (`05-02` §10) |
| **Processing** | Any operation on personal data — collection, recording, storage, retrieval, use, disclosure, transfer, erasure |
| **Data fiduciary** | The party that determines the purposes and means of processing. **The company, for §4.2** |
| **Processor** | A party processing on the company's instruction. **Its processing is treated as the company's own** (`NFR-098`) |
| **Consent** | A **clear, explicit, specific and freely given** positive indication of agreement (`NFR-091`) |
| **Legitimate ground** | A basis other than consent on which processing is lawful — contract performance, a legal obligation, employment duties, a medical emergency, or the data subject's own public disclosure ‡ |
| **The Authority** | The **National Data Management Authority** (`05-06` §6.3) |
| **Residency-restricted** | A field that must be written only to the Bangladesh-resident store (`NFR-086`, `BRU-SEC-13`) |
| **Governing text** | The **English** version (`LG-001` `LR-03`), with `LR-04` preserving the Bengali version's operative effect |

---

## 4. Terms

### 4.1 The notice obligation

**The company issues this notice before or during processing** (`NFR-092`), stating the data
categories, the purposes, the **risks**, the retention periods, third-party transfers and the
withdrawal procedure. Processing without a recorded lawful basis does not begin
(`BRU-CPM-07`, `BRU-GRC-16`), and the record of processing activities is maintained for a
**minimum of five years** (`NFR-095`, `BRU-GRC-17`, `BRU-CPM-15`).

### 4.2 The processing inventory

> **This table is the notice.** It is also the content half of the record of processing activities
> `M60` `FR-GRC-033` maintains — **`PI-01`: where the two disagree, `FR-GRC-033` is the system of
> record and this table is regenerated from it.** Retention is a reference to `LG-009`, never a
> restated period (`CP-01`).
>
> **The `Risks` column is the `NFR-092` element the programme has not previously drafted for
> (`O-04`), and it is the least-verified column here.**

| # | Purpose | Data categories | Lawful basis ‡ | Recipients | Residency | Retention | Risks stated to the data subject |
|---|---|---|---|---|---|---|---|
| **P-01** | **Provide the service** — book, diagnose, repair, deliver, invoice a service order | Name, contact, address, device identity, fault description, photographs, service history | **Contract performance** | Technicians, branch staff, couriers, marketplace seller on an awarded job | Regional store; device photographs regional | `LG-009` `RC-01` | Photographs of a device may incidentally show your home or your data. A seller sees your contact details for an awarded job only |
| **P-02** | **Verify identity** at device release, high-value cash receipt, and rights requests | National ID or equivalent | **Legal obligation** (cash) / **contract** (release) | Finance, compliance roles only (`05-04` §5) | **Bangladesh-resident, encrypted** | `LG-009` `RC-02` | Your National ID is used only for the statutory purpose it was collected for, and every access to it is logged (`BRU-TAX-19`) |
| **P-03** | **Take payment and issue a tax invoice** | Payment token, last four digits, amount, TIN where the invoice requires it | **Legal obligation** | Payment gateway, NBR through statutory filings | TIN **Bangladesh-resident**; token regional | `LG-009` `RC-03` | Card details are never stored — only a gateway token and the last four digits (`BRU-ARB-25`) |
| **P-04** | **Send service notifications** — status, arrival, ready-for-collection, breach | Contact point, order reference | **Contract performance** | SMS, WhatsApp, email and push providers | Regional | `LG-009` `RC-04` | Service updates cannot be switched off while a service is active |
| **P-05** | **Send marketing and service reminders** | Contact point, segment, preferences | **Consent** — withdrawable at any time | Campaign platform | Regional | `LG-009` `RC-05` | You can stop these at any time; stopping them does not stop service updates |
| **P-06** | **Operate loyalty and referral** | Membership tier, points, referral link, attributed conversions | **Contract performance** | Partner sees conversion, not the customer record | Regional | `LG-009` `RC-06` | A referral partner is told a conversion occurred, not who you are beyond what you gave them |
| **P-07** | **Warranty claim to a brand partner** | Device identity, diagnosis, photographs, parts, named technician and certification, purchase proof | **Contract performance** + legitimate ground | **The brand partner** (`LG-005` §4.3) | **Cross-border where the brand is abroad — registered transfer required** | `LG-009` `RC-07` | A claim discloses your device data, and photographs, to the manufacturer. It does not disclose your National ID |
| **P-08** | **Manage a contract, SLA and service credits** | Corporate user identity, estate, entitlement, SLA measurement | **Contract performance** | Client's own administrators | Regional | `LG-009` `RC-08` | Your employer's administrators can see requests you raise |
| **P-09** | **Data recovery and secure destruction** | The customer's own recovered data and its index | **Contract performance**, with specific consent for access | **Case-assigned staff only**, dual control (`BRU-DTS-01`, `BRU-DTS-02`) | **Bangladesh-resident; never replicated abroad** (`BRU-DTS-16`) | `LG-009` `RC-09` | We may see the contents of your data. Access is restricted to the assigned team, logged, and the data is purged at the agreed date. **It is never used to train a model** (`BRU-DTS-14`) |
| **P-10** | **Employ and pay staff** | Identity, TIN, bank account, salary, attendance, biometric template, performance, discipline | **Employment and social-security duties** | Payroll, HR, statutory filings | **TIN and biometric template Bangladesh-resident** | `LG-009` `RC-10`, `RC-11`, `RC-12`, `RC-13` | Your biometric template is stored as an irreversible template and is never exported (`05-02` §10). **Subject to `PN7`** |
| **P-11** | **Qualify a supplier or seller** | Identity, trade licence, KYC documents, bank details, criminal-record check where a category requires | **Contract performance** + legal obligation | Onboarding and compliance roles only | **KYC documents and checks Bangladesh-resident** (`BRU-MKP-19`) | `LG-009` `RC-14` | KYC documents are restricted data with logged access. **Criminal-record retention subject to `PN8`** |
| **P-12** | **Handle a contact, call or chat** | Contact point, transcript, call recording, disposition | **Contract performance** | Contact centre, quality reviewers | Recordings regional; **restricted (`S3`)** | `LG-009` `RC-15` | Calls may be recorded for quality and training. You are told at the start of the call |
| **P-13** | **Operate the AI assistant** | Your message, and the context needed to answer it | **Contract performance**; **consent for reuse** | Model service (`M32`) | Per `LG-012` | `LG-009` `RC-16` | You are talking to an automated assistant. It can hand you to a person. **It does not commit us to a price or a promise** (`HC-019`) |
| **P-14** | **Improve the service and train models** from contact and search data | **Anonymised** transcripts, chat logs, search queries | **`PN5` — UNCONFIRMED** | Content and AI teams | Regional | `LG-009` `RC-17` | **Provisional. This purpose is not operative until `PN5` is answered** |
| **P-15** | **Prevent fraud and abuse** | Transaction patterns, claim history, device and IP signals | **Legitimate ground** ‡ | Fraud and finance roles | Regional | `LG-009` `RC-18` | We check transactions for fraud. A high score triggers a human review, never an automatic rejection (`BRU-WTY-21`) |
| **P-16** | **Meet statutory and regulatory obligations** — tax, labour, environmental, filings, disclosures | As each instrument requires | **Legal obligation** | NBR, and the regulators in `LG-024` | Per `LG-012` | `LG-009` `RC-19` | Some records must be kept by law even after you ask us to delete your data. We will tell you which and until when |
| **P-17** | **Respond to a rights request** | Your identity evidence and the request record | **Legal obligation** | DPO function | Regional | `LG-009` `RC-20` | We must verify who you are before sharing your data |
| **P-18** | **Handle a complaint, dispute or legal matter** | The complaint record, evidence, correspondence | **Legitimate ground** / legal obligation | Quality, Legal, insurers, counsel | Regional | `LG-009` `RC-21` | A record under legal hold is not deleted, even on request (`BRU-SEC-23`) |
| **P-19** | **Secure the platform and audit access** | Identity, access logs, audit entries, security events | **Legal obligation** + legitimate ground | Security roles; audit logs are restricted (`T5`) | Regional | `LG-009` `RC-22` | Audit entries cannot be modified or deleted by anyone, including administrators (`BRU-SEC-11`) |
| **P-20** | **Recruit** | Application, CV, references, assessment | **Consent** / pre-contract | HR, hiring managers | Regional | `LG-009` `RC-23` | An unsuccessful application is kept only for the period we state, then deleted |

| # | Rule |
|---|---|
| **PI-02** | **A purpose not in this table is not processed.** Adding a purpose requires a new row, a recorded lawful basis before processing begins (`BRU-GRC-16`), a retention row in `LG-009`, and a re-issued notice |
| **PI-03** | **`P-14` is marked provisional and is not operative.** `AUDIT-010` HC-01 named the exposure; `PN5` closes it. Until then, `HC-015` and `HC-017` cannot mine transcripts |
| **PI-04** | Where a processor is used, equivalent obligations flow down and **the processor's processing is the company's own** (`NFR-098`, `BRU-GRC-18`) |
| **PI-05** | **Bulk export of personal data requires approval and is logged** (`BRU-SEC-05`). No purpose in this table authorises an unlogged bulk extract |
| **PI-06** | A privacy impact assessment is required and recorded before new higher-risk processing begins (`FR-GRC-037`) |

### 4.3 The consent register

Consent is required only where §4.2 says so. **Everywhere else, asking for consent and then
processing regardless is worse than not asking** — it misrepresents the basis.

| Consent | Purpose | Granularity | Withdrawal effect | Bundling |
|---|---|---|---|---|
| **CN-01 Marketing** | `P-05` | Per channel where the channel is chosen | Immediate, every channel, every module (`BRU-CPM-09`) | **Never bundled with service notifications** (`LG-001` `LR-07`, `NT-002`) |
| **CN-02 Marketplace fulfilment** | `P-01` where a seller performs the work | Per job, before broadcast | The job is not broadcast | **Explicit, with the implications stated** (`BRU-MKP-07`) |
| **CN-03 Review publication** | Publishing a review | Per review | The review is unpublished | **Explicit** (`BRU-CXM-13`) |
| **CN-04 Data-case access** | `P-09` | Per case | Work stops; media returned | Specific consent; separate from the service order |
| **CN-05 Remote-access session** | `LG-016` | **Per session**, logged (`BRU-RMS-01`) | The session cannot start or continues no further | Standing consent only where a contract grants it (`BRU-RMS-02`) |
| **CN-06 Cookies and tracking** | `LG-011` | Per category | Category stops | Never bundled with terms acceptance |
| **CN-07 Lead submission by a partner** | `LG-007` §4.6 | Per individual, obtained **by the partner** | The lead is not created | The partner records it and warrants it |
| **CN-08 Survey participation** | `M34` | Per survey, subject to a frequency cap (`BRU-CXM-09`) | No further surveys | Consent evaluated through `M33` at dispatch (`BRU-CXM-14`) |
| **CN-09 Parental consent** | Any purpose where the subject is under 18 | Verifiable, from a parent or guardian | Processing stops | **Valid until the child reaches 18** ‡ (`BRU-CPM-16`) |

| # | Rule |
|---|---|
| **CN-R1** | **Consent is invalid unless the version of this notice presented is recorded with it** (`BRU-CPM-08`). The ledger field is `notice_version_shown` (`LG-001` §4.5) |
| **CN-R2** | Consent is captured by an **affirmative act**. A pre-ticked box, an inferred consent, or silence is not consent |
| **CN-R3** | Withdrawal is as easy as giving. It is available in the preference centre, and **takes effect immediately across every channel and every module** (`BRU-CPM-09`) |
| **CN-R4** | Withdrawal does not make prior processing unlawful, and **the consent record is retained as evidence that it was lawful** (`LG-001` `LR-15`) |
| **CN-R5** | Where a purpose rests on a legitimate ground, the notice says so. **The data subject is not offered a choice that does not exist** |
| **CN-R6** | **A migrated customer with no consent record has no consent** (`O-06`). Marketing to them requires consent to be obtained afresh |

### 4.4 Data subject rights

| Right | What the company does | Timeline |
|---|---|---|
| **Access and portability** | Provides the data in a concise, intelligible, portable format, and discloses the third parties that received it ‡ | Per `LG-010` §4.4 |
| **Rectification** | Corrects the data and **notifies the data subject within 30 days** (`NFR-093`, `BRU-CPM-10`) | 30 days |
| **Erasure** | Deletes, **except where a statutory retention obligation overrides it. Where it does, the override and its basis are stated to the data subject** (`BRU-CPM-11`) | Per `LG-010` |
| **Withdraw consent** | Through a simplified procedure, immediately effective (`CN-R3`) | Immediate |
| **Object to a purpose resting on a legitimate ground** | Assesses and records the outcome | Per `LG-010` |
| **Complain** | To the company, and **to the Authority** | — |

**How to exercise them:** in the preference centre in `P01` or the relevant portal, by email to the
address in §4.9, or at any branch. **`LG-010` is the process; this is the statement of the rights.**

### 4.5 Automated processing and profiling

| # | Clause |
|---|---|
| **4.5.1** | The company uses automated processing for dispatch optimisation, fraud scoring, seller ranking and visibility, credit hold, and the AI assistant |
| **4.5.2** | **Where an automated outcome affects a person materially, the notice says so and a human route exists**: a fraud score above threshold triggers investigation, **never an automatic rejection** (`BRU-WTY-21`); a seller's visibility reduction is appealable to a different operator (`BRU-MKP-18`); a ranking decision is reconstructible on request (`BRU-MKP-22`); a credit hold is released by an authorised role (`BRU-ARB-14`) — subject to `PN9` |
| **4.5.3** | **The AI assistant is disclosed as automated** and hands over to a person (`HC-019`) |
| **4.5.4** | **Recovered customer data is never used as training data for any model** (`BRU-DTS-14`), and recovered data from a data case is never used as retrieval data for the assistant |

### 4.6 Security

The company implements technical and organisational measures proportionate to the risk
(`NFR-097`): field-level encryption on restricted data, explicit grant with step-up authentication,
full access logging, insert-only audit entries (`BRU-SEC-11`), masking in non-production
(`BRU-SEC-08`), malware scanning on every upload (`BRU-SEC-22`) and redaction of classified fields
from logs at emission (`BRU-SEC-24`). **The controls themselves are `LG-021`.**

### 4.7 The `UI-042` boundary — and the two questions it asks this file

> **`CL-01`. Two files could each hold the consent wording, and that is the drift `CP-01` exists
> to prevent.** The boundary is drawn once, here.

| # | Rule |
|---|---|
| **UB-01** | **This file owns the *operative meaning*:** which purposes exist, which need consent, what must be disclosed, and what a statement must convey to be lawful |
| **UB-02** | **`UI-042` owns the *rendered wording*** — keys, string values, Bengali text, character budgets, screen placement, error copy |
| **UB-03** | A `UI-042` string that changes the meaning of a §4.3 consent is a change to **this** file and re-opens G5 and G6 |
| **UB-04** | Where the two conflict, **this file governs on meaning and `UI-042` governs on wording**. A conflict is escalated under `CG-013` `T-C05`, not resolved locally |

**`UI-042` §9 asks two questions of this file. Both are answered:**

| `UI-042` question | Answer |
|---|---|
| *"Is the residency wording confirmed by Legal and the DPO?"* — marked blocking G6 | **§4.7.1.** The wording *"It is stored in Bangladesh and is not shared"* is **correct in substance for the residency-restricted fields** — National ID, TIN and bank details are written only to the Bangladesh-resident store (`BRU-CPM-06`, `BRU-SEC-13`). **But "is not shared" is too absolute for TIN**, which appears on statutory outputs and is disclosed to the NBR through filings (`P-03`, `P-16`). **`UI-042` `flow.consent.purpose.tin` must be amended** to *"It is stored in Bangladesh and is used only for your invoice and tax records."* Recorded as a `UI-042` change request. **Final confirmation remains subject to `PN6`** |
| *"Is the statutory retention period for invoices confirmed at five years?"* | **§4.7.2.** The statutory **minimum** is five years. **The company's own retention standard for tax documents is seven years** (`BRU-TAX-24`), and `LG-009` `RC-03` applies **seven**. `UI-042` `flow.dsr.erase_limits` interpolates `{years}`; **the value bound to it must be 7, not 5**, or the customer is told a shorter period than the company actually applies. `LG-009` §4.4 explains why the two figures differ |

### 4.8 Breach

A breach likely to cause significant damage is **notified to the Authority within the prescribed
timeframe** (`NFR-094`, `FR-GRC-036`, `BRU-DTS-17`) — **the timeframe is `PN3`**. Affected data
subjects are informed where the risk to them requires it. The breach register, assessment,
containment, notification decision and evidence are held in `M60` `FR-GRC-036`.

### 4.9 Who to contact

| Role | Contact |
|---|---|
| **Chief Data Officer / data-protection contact** | Via info@1000fix.com marked for the attention of the Chief Data Officer — **`O-05`: the appointment is not recorded** |
| Hotline | 16743 |
| Registered office | 1000FiX Services Limited, Bangladesh |
| **The Authority** | The National Data Management Authority |

---

## 5. Liability, Exclusions and Limits

> **A notice does not limit liability, and nothing in this section attempts to.** The section is
> retained because the template requires it and because two positions belong here.

| # | Clause |
|---|---|
| **5.1** | **This notice creates no contractual limitation and excludes nothing.** Statutory data-protection liability cannot be excluded by notice, and the company does not attempt it |
| **5.2** | Statutory exposure is **BDT 25 lakh** for a security failure or a rights violation, rising to **BDT 50 lakh** where the company is a significant data fiduciary, with further fines for repeat violations (`05-06` §6.3, risk `RSK-032`) ‡ |
| **5.3** | **A processor's processing is the company's own** (`NFR-098`). Contracting with a processor does not transfer the company's statutory responsibility, and no clause in `LG-004`, `LG-005`, `LG-006` or `LG-007` should be read as doing so |
| **5.4** | Where a counterparty's breach causes the company's liability, the company's recovery is under that counterparty's indemnity — **and the company's liability to the data subject and to the Authority is unaffected by it** |

---

## 6. Data Protection

> This whole file is the data-protection position. **§6 records the reconciliation gate rather than
> repeating §4.**

**Audit check F6 requires zero contradiction between `LG-008`, `LG-009` and `LG-012`.** The
reconciliation is run on this axis and recorded:

| Axis | `LG-008` says | Must match |
|---|---|---|
| Purposes and lawful bases | §4.2, 20 purposes `P-01`…`P-20` | `LG-009` retention rows `RC-01`…`RC-23` — **every purpose has a retention row and every retention row has a purpose** |
| Residency-restricted fields | §4.2 residency column; §4.7.1 | `LG-012` §4.3 field table — **identical field lists** |
| Cross-border transfers | `P-07`, `P-13`, `P-16` | `LG-012` §4.5 transfer register and §4.6 sub-processor register |
| Erasure override | §4.4 and `BRU-CPM-11` | `LG-009` §4.5 override table — **the overrides stated to the data subject are exactly those in `LG-009`** |
| Consent record fields | `CN-R1`, `notice_version_shown` | `LG-001` §4.5 ledger |
| Rights timelines | §4.4 | `LG-010` §4.4 — **30 days for rectification in both** |
| Retention periods | **None stated here** (`CP-01`) | `LG-009` is the only source |

| # | Rule |
|---|---|
| **F6-01** | The reconciliation is run **whenever any of the three files changes**, not at wave boundaries only |
| **F6-02** | **A contradiction between the three is a compliance defect, not a documentation defect**, and escalates immediately under `CG-013` `T-C05` |
| **F6-03** | A change to §4.2 re-opens `LG-009` and `LG-012` for the affected rows, and re-opens G5 on every file citing §4.2 (`CG-007` §7) |

---

## 7. Termination and Consequences

| Event | Consequence |
|---|---|
| **A data subject withdraws consent** | The consent-based purpose stops immediately across every channel and module (`BRU-CPM-09`). Contract-based and legally required purposes continue, and the notice says which |
| **A data subject requests erasure** | Honoured except where a statutory retention obligation overrides; **the override and its basis are stated** (`BRU-CPM-11`, `LG-009` §4.5) |
| **An account closes or a relationship ends** | Processing reduces to the purposes with a continuing basis — `P-16`, `P-18`, `P-19` — for the periods in `LG-009` |
| **A legal hold is in force** | **Data is never purged, regardless of retention schedule or erasure request** (`BRU-SEC-23`, `BRU-DMS-02`) |
| **This notice is superseded** | The prior version is archived, not deleted (`CP-10`), because **it is the notice a past consent was given against** and `BRU-CPM-08` makes it evidence |

---

## 8. Dispute Resolution

| Step | Route |
|---|---|
| **1 — Rights request or query** | The Chief Data Officer contact in §4.9; handled under `LG-010` |
| **2 — Internal escalation** | Legal Counsel, then the CFO (`CG-013` §3) |
| **3 — The Authority** | **The data subject may complain to the National Data Management Authority. Nothing in any company document conditions or delays that right** |
| **4 — Courts** | The courts of Dhaka, Bangladesh |

> **Enforcement mechanisms — complaint, investigation and penalty procedures — activate around
> 13 May 2027** (`05-06` §6.1), which is **inside Wave 4**. The company's obligations apply now;
> the enforcement machinery arrives during delivery.

---

## 9. Change Control

| Version | Date | Change | Notice given to users | Re-acceptance required |
|---|---|---|---|:--:|
| 1.0 | 2026-08-18 | Initial issue — draft, blocked on G6 | n/a | n/a |

| # | Rule |
|---|---|
| **9.1** | **Every version of this notice is retained permanently.** A consent given against version 1.0 is evidence only if version 1.0 can be produced (`BRU-CPM-08`, `CP-10`) |
| **9.2** | A change to a purpose, a lawful basis, a recipient, a residency position or a right is **MAJOR**: the notice is re-issued, and **consent resting on the changed purpose is re-obtained** |
| **9.3** | A statutory change re-opens **G2, G5 and G6** on this file and on every file citing it (`CG-007` §7, `LG-001` §4.8) |
| **9.4** | **12 months without a trigger re-opens G6 anyway** (`CG-006` §4.2, `CG-007` §7) |
| **9.5** | A `UI-042` string change that alters meaning re-opens this file (`UB-03`) |

---

## 10. Cross-References

| Document | Relationship | Must not contradict |
|---|---|---|
| [`LG-009_Data_Retention_and_Deletion_Schedule.md`](LG-009_Data_Retention_and_Deletion_Schedule.md) | **Every retention reference in §4.2** | Check **F6** — purposes to retention rows, one to one |
| [`LG-012_Cross_Border_Data_Transfer_and_Residency_Statement.md`](LG-012_Cross_Border_Data_Transfer_and_Residency_Statement.md) | Residency and transfers | Check **F6** — identical field lists |
| [`LG-010_Data_Subject_Request_Handling_Content.md`](LG-010_Data_Subject_Request_Handling_Content.md) | §4.4 process | Timelines, refusal grounds |
| [`LG-011_Cookie_and_Tracking_Policy.md`](LG-011_Cookie_and_Tracking_Policy.md) | `CN-06` | Consent categories |
| [`LG-001_Legal_Content_Register_and_Signoff_Log.md`](LG-001_Legal_Content_Register_and_Signoff_Log.md) | `notice_version_shown`; version retention | `CN-R1` |
| [`LG-017_Data_Recovery_and_Secure_Destruction_Terms.md`](LG-017_Data_Recovery_and_Secure_Destruction_Terms.md) | `P-09` | Access control, purge, no-training rule |
| [`LG-016_Managed_Services_and_Remote_Access_Consent_Terms.md`](LG-016_Managed_Services_and_Remote_Access_Consent_Terms.md) | `CN-05` | Per-session consent |
| [`LG-020_Acceptable_Use_and_Internal_Access_Policy.md`](LG-020_Acceptable_Use_and_Internal_Access_Policy.md) · [`LG-021_ISMS_Policy_Set.md`](LG-021_ISMS_Policy_Set.md) | `P-10`, `P-19`, §4.6 | Monitoring notice; security controls |
| [`../03_UI_Copy_and_Microcopy/03D_Critical_Flows/UI-042_Consent_Privacy_and_Preference_Centre_Copy.md`](../03_UI_Copy_and_Microcopy/03D_Critical_Flows/UI-042_Consent_Privacy_and_Preference_Centre_Copy.md) | **§4.7 boundary; two change requests raised** | `UB-01`…`UB-04` |
| [`../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-013_Customer_and_Party_Master_Standard.md`](../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-013_Customer_and_Party_Master_Standard.md) | The `S3` fields and `PTY-05` residency rule | Field classification |
| [`../05_Document_and_Print_Templates/05A_Service_and_Operations/DT-002_Service_Intake_Receipt_and_Device_Handover_Form.md`](../05_Document_and_Print_Templates/05A_Service_and_Operations/DT-002_Service_Intake_Receipt_and_Device_Handover_Form.md) | Where `P-01` is first presented | The notice reference at intake |
| `HC-019` AI Guardrail and Disclosure | §4.5.3, `P-13` | Disclosure and data-use notice |
| `LG-002`…`LG-007` §6 | All defer to this file | **Every one — check F6** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Legal_Document.md` — ten sections in order; additions declared
- [x] **Twenty processing purposes enumerated with categories, basis, recipients, residency, retention reference and risk statement**
- [x] **No retention period restated** — every one is a reference to `LG-009` (`CP-01`)
- [x] Nine consents registered with granularity, withdrawal effect and the anti-bundling rule
- [x] **The `UI-042` boundary drawn, and both `UI-042` §9 questions answered with two change requests raised** (§4.7)
- [x] **`AUDIT-010` HC-01 located as `PN5` and `P-14` marked non-operative until answered**
- [x] Automated-decision disclosure with a human route for each material outcome
- [x] F6 reconciliation stated as a seven-axis gate, not an assertion
- [x] All internal links resolve
- [x] Accessibility standard `CG-011` applied
- [ ] **G6 external verification against the enacted instrument** — outstanding. **`WV-02`: cannot be waived. Blocks `Approved`**
- [ ] **Every `‡` clause verified against a primary source** — outstanding; `PR-04` blocks approval while any remains
- [ ] **`PN1`–`PN10` answered** — outstanding
- [ ] **Split-residency legal opinion obtained** — outstanding, `O-02`
- [ ] **Chief Data Officer appointed** — outstanding, `O-05`
- [ ] **Bengali counterpart authored and signed off in context** — outstanding; **Bengali is the operative presentation for most data subjects**
- [ ] Named approver recorded — pending
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
