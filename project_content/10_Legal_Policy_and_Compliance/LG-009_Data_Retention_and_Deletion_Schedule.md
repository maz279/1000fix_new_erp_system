---
id: LG-009
title: Data Retention and Deletion Schedule
project: 1000FiX ERP System v2.0
content_type: Legal / policy
template: TPL_Legal_Document.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Legal & Compliance with the CFO and the Chief Data Officer
author: Legal & Compliance with the Chief Data Officer, Finance, HR, Quality and Enterprise Architecture
reviewers: [Legal Counsel, Chief Data Officer, CFO, Quality Manager, HR Director, CTO delegate, external tax adviser, external data-protection adviser]
approver: CFO with Legal Counsel
content_class: A
purpose: >
  The single authoritative schedule stating, for every class of data and every class of document the
  programme holds, how long it is kept, on what legal basis, from what trigger, how it is deleted
  and what overrides the schedule. Forty-four DT document templates defer their retention row to
  this file, LG-008 defers every retention reference in its processing inventory to it, and M60
  publishes it to M24 for machine enforcement — so until it exists, nothing in the repository can
  state how long anything is kept.
traces_to: [05-06 NFR-088, NFR-095, NFR-093, M24, M60, M51, M23, M06, M12, M21, M29, M33, M55, M56, LG-001, LG-008, LG-010, LG-012, LG-017, LG-018, LG-021, LG-024, DT-001, DT-002, DT-010, DT-014, DT-030, DT-031, DT-034, DT-041, MD-040, UI-042, BRU-GRC-14, BRU-GRC-15, BRU-GRC-17, BRU-DMS-01, BRU-DMS-02, BRU-DMS-03, BRU-DMS-04, BRU-DMS-05, BRU-DMS-06, BRU-CPM-11, BRU-CPM-15, BRU-DTS-03, BRU-DTS-06, BRU-DTS-18, BRU-QMS-13, BRU-RMS-12, BRU-SEC-11, BRU-SEC-23, BRU-TAX-24, FR-DMS-034, FR-DMS-035, FR-DMS-036, FR-DMS-039, FR-DMS-040, FR-GRC-032]
priority: P0
wave: W2
bilingual: yes
bn_counterpart: LG-009_Data_Retention_and_Deletion_Schedule_BN.md
sources:
  - source: 1000fix_ERP_Module/03_Modules/G_Finance_and_Treasury/M51 §9 BRU-TAX-24 — tax documents, registers, returns, challans, certificates and determination records are retained seven years and remain queryable
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 §6.3 NFR-095 — processing records maintained for a minimum of five years; §6.2 NFR-088 — records retention per the statutory schedule, enforced by the system
    verified: 2026-08-12
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M60 §9 BRU-GRC-14 — the statutory retention schedule is defined in M60 and published to M24; retention is never configured independently in M24; BRU-GRC-15 legal hold overrides every retention rule until released by M60
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M24 §5.4 FR-DMS-034 … FR-DMS-040 retention application, computation from a trigger, legal hold, disposal eligibility and approval, defensible disposal with a certificate, retention-violation detection in both directions; §9 BRU-DMS-01 … BRU-DMS-06
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M23 §9 BRU-QMS-13 — ISO management-system records are retained for three certification cycles and cannot be disposed while a certificate is live
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/A_Service_Delivery_and_Operations/M06 §9 BRU-DTS-03 case-workspace access logged immutably and retained five years; BRU-DTS-06 recovered data purged at the agreed date unless a documented hold applies; BRU-DTS-18 case records retained a minimum of five years as processing records
    verified: 2026-08-18
    class: P1
  - source: project_content/05_Document_and_Print_Templates/ — 44 DT templates, of which the great majority carry a "Retention period | LG-009; …" row deferring the period to this file. Enumerated across the folder 2026-08-18
    verified: 2026-08-18
    class: P1
  - source: VAT and Supplementary Duty Act 2012 and its rules — VAT records retained for at least five years from the end of the tax period; Income Tax Act 2023 — record-keeping obligations; Bangladesh Labour Act 2006 and Labour Rules 2015 — employment record obligations; Personal Data Protection Act 2026 — storage limitation and a five-year processing-record minimum. **Instrument-level citations from secondary sources. Every period marked ‡ is unverified at section level and is pending G6**
    verified: 2026-08-18
    class: P2
supersedes: none
review_due: 2027-02-18
---

# LG-009 — Data Retention and Deletion Schedule

| Item | Value |
|---|---|
| Document class | **Policy / schedule** — statutory retention schedule, machine-enforced |
| Counterparty | None. **Internal, regulator-facing, and quoted to data subjects** through `LG-008` §4.4 and `UI-042` |
| Governing law | **Bangladesh** |
| Effective date | On publication of version 1.0 — *pending G6* |
| Acceptance capture method | **`AC-6` publication.** The schedule is **defined here, published by `M60` to `M24`, and enforced by `M24`** (`BRU-GRC-14`) |
| Version accepted by users | n/a — but **every version is retained**, because a disposal executed under version 1.0 is defended by version 1.0 |
| External counsel review | **Required — G6**, by a named external tax adviser **and** a data-protection adviser. The two disciplines meet in this one file |
| Bengali version | **Required.** Employees read the employment rows; customers are told the invoice period at the point of an erasure request |

> ⚠ **Class A — statutory, and the single most load-bearing file in Category 10.**
>
> **Forty-four `DT` templates defer their retention row to this file.** Extraction across
> `05_Document_and_Print_Templates/` on 2026-08-18 found rows reading *"`LG-009`; warranty term plus
> the limitation period"*, *"`LG-009`; not less than the tax retention"*, *"`LG-009`; employment
> duration plus the limitation period"* and twenty-odd further variants. **Every one of them is a
> forward reference that has had nowhere to point until now.**
>
> `LG-008` §4.2 defers all twenty of its processing purposes here. `M60` `FR-GRC-032` defines the
> schedule from obligations and publishes it to `M24`; `BRU-GRC-14` prohibits `M24` from holding
> retention configuration of its own. **This file is the content half of that pipeline.**
>
> **Conformance note.** All ten template sections retained in order. The schedule occupies §4.2
> (data classes) and §4.3 (document classes) within §4 Terms; deletion methods are §4.6 and
> overrides §4.5. Gate questions and open items are §1.2 and §1.3 (`CP-09`).

---

## 1. Approval Record

| Role | Name | Date | Evidence |
|---|---|---|---|
| Drafted by | Legal & Compliance with CDO and Finance | 2026-08-18 | Draft issue v1.0 |
| G1 Editorial — Content Design | *pending* | | |
| G2 Factual — CFO, HR Director, Quality Manager | *pending* | | |
| G4 Linguistic — independent reviewer, in context (`BN-018`) | *pending* | | |
| **G5 Legal — Legal Counsel** | *pending* | | **Required** |
| **G6 Statutory — external tax adviser** | *pending* | | **Required for every tax and statutory row** |
| **G6 Statutory — external data-protection adviser** | *pending* | | **Required for every personal-data row** |
| Approved by — CFO with Legal Counsel | *pending* | | |

### 1.2 Questions for the external advisers (G6)

| # | Question | Adviser |
|---|---|---|
| **RT1** ‡ | **Confirm the VAT record-retention minimum and its trigger** — five years from the end of the tax period, or from another point? | Tax |
| **RT2** ‡ | **Confirm the income-tax record-keeping period** and whether it exceeds the VAT minimum | Tax |
| **RT3** | **Is the company's seven-year tax retention standard (`BRU-TAX-24`) a deliberate policy above the statutory minimum, or was it derived from a different instrument?** §4.4 treats it as policy; if it is statutory, §4.4's explanation is wrong | Tax + CFO |
| **RT4** ‡ | **Confirm the employment record-retention obligations** under the Labour Act 2006 and Labour Rules 2015, including payroll, attendance, accident and disciplinary records | Labour / Legal |
| **RT5** ‡ | **Confirm the personal-data storage-limitation standard** and the five-year processing-record minimum, and whether "processing records" means the record of processing activities only or also the underlying data | Data protection |
| **RT6** ‡ | **What is the lawful retention period for a criminal-record check and for a biometric template?** (`LG-008` `PN7`, `PN8`) | Data protection |
| **RT7** ‡ | **Confirm the e-waste and environmental record obligations** under the Hazardous Waste (E-waste) Management Rules 2021 and the Environment Conservation Act 1995 | Environmental / Legal |
| **RT8** | **What is the limitation period this schedule should use** for contract and tort claims, and does it run from breach, from discovery, or from another point? **Twenty-odd `DT` rows say "plus the limitation period" and none of them state a number** | Legal |
| **RT9** | Is a **retention period longer than statute requires** itself a storage-limitation breach where the data is personal? §4.4 assumes the longest applicable obligation governs | Data protection |
| **RT10** | **Is CCTV, call-recording and location-history retention proportionate as scheduled in §4.2?** | Data protection |

### 1.3 Open items

| # | Open item | Blocking? | Owner |
|---|---|:--:|---|
| **O-01** | **`RT1`–`RT10` unanswered. Every `‡` period is provisional, and `CG-012` `PR-04` blocks approval of a Class A file containing a provisional claim** | **Yes — blocks `Approved`** | CFO with CDO |
| **O-02** | **`RT8` is the largest single gap in the repository's retention position.** *"Plus the limitation period"* appears in more than twenty `DT` retention rows and in `DT-031` §9. **No document states the number.** Until it is stated, `M24` cannot compute a disposal date for any of them (`FR-DMS-035`) | **Yes — blocks disposal computation for the whole contract and warranty set** | Legal Counsel |
| **O-03** | **The 5-versus-7-year tax divergence is real and now reconciled in §4.4** — but the reconciliation is a policy reading pending `RT3`, and **`UI-042` currently interpolates a period into customer-facing copy** (`LG-008` §4.7.2) | **Yes** | CFO with Legal |
| **O-04** | **`M60` is the publishing authority (`BRU-GRC-14`) and `M60` is not delivered until its wave.** Until then, retention is enforced by nothing. **A `W2` go-live with `LG-009` written and unenforced is a stated position, not an accident** | **Yes — architectural** | CTO with CFO |
| **O-05** | **`BRU-QMS-13` retains ISO records for "three certification cycles" and never defines a cycle.** §4.3 `DC-19` reads it as three years each, nine years total; that reading needs Quality confirmation | Yes — blocks `DC-19` | Quality Manager |
| **O-06** | **Recovered customer data is purged "at the agreed date"** (`BRU-DTS-06`). The agreement is per case; **no maximum is set**, and an indefinite hold by agreement would defeat storage limitation | **Yes — blocks `RC-09`** | CDO with Technical Services Head |
| **O-07** | **No archival deletion capability is proven.** `FR-DMS-039` requires irreversible disposal with a certificate; `FR-DMS-040` requires detection of records retained beyond schedule **and records missing before it**. Both are `P0` and unbuilt | Yes — the schedule is unenforceable without them | CTO |
| **O-08** | **Backups.** Deleting a record from the live store does not delete it from backup media. §4.6.5 states the position; **it needs G6 confirmation that a backup-cycle lag is acceptable** | **Yes** | CTO with CDO |

---

## 2. Scope and Parties

**In scope:** every class of personal and business data the ERP holds; every class of document
`M24` files; the retention trigger, period, legal basis and deletion method for each; what overrides
the schedule; how disposal is approved and evidenced; and the reconciliation with `LG-008` and
`LG-012` that audit check **F6** tests.

**Out of scope:**

| Subject | Owned by |
|---|---|
| Purposes and lawful bases | [`LG-008_Privacy_Notice_and_Consent_Copy.md`](LG-008_Privacy_Notice_and_Consent_Copy.md) §4.2 |
| Where data may be stored and what may leave Bangladesh | [`LG-012_Cross_Border_Data_Transfer_and_Residency_Statement.md`](LG-012_Cross_Border_Data_Transfer_and_Residency_Statement.md) |
| Handling an erasure request and what the data subject is told | [`LG-010_Data_Subject_Request_Handling_Content.md`](LG-010_Data_Subject_Request_Handling_Content.md) |
| The **sanitisation technique** for physical media and devices | [`LG-017_Data_Recovery_and_Secure_Destruction_Terms.md`](LG-017_Data_Recovery_and_Secure_Destruction_Terms.md) §4.6 |
| Document numbering, archive format and reprint control | `DT-001` §12 and `MD-040` |
| The obligation register that generates statutory requirements | `M60` `FR-GRC-023`; content in [`LG-024_Regulatory_Disclosure_and_Statutory_Notice_Register.md`](LG-024_Regulatory_Disclosure_and_Statutory_Notice_Register.md) |
| Security controls over retained data | [`LG-021_ISMS_Policy_Set.md`](LG-021_ISMS_Policy_Set.md) |

---

## 3. Definitions

| Term | Meaning |
|---|---|
| **Retention period** | The time a record is kept, measured from its **trigger**, not from its creation unless the trigger is creation |
| **Trigger** | The event that starts the clock: creation, transaction close, contract expiry, employment termination, last customer transaction, case closure, or certificate expiry (`FR-DMS-035`) |
| **Retention class** | The class `M24` applies to a document at filing. **Every document has exactly one document class and one retention class at all times** (`BRU-DMS-01`) |
| **Limitation period** | The period within which a legal claim may be brought. **Its value is `RT8` and is not stated in this version** |
| **Legal hold** | A hold instructed by `M60` that **overrides every retention rule and cannot be bypassed by any code path** (`BRU-DMS-03`, `BRU-GRC-15`) |
| **Disposal** | Irreversible destruction of content, **system-executed after approval, never manual, always producing a certificate** (`BRU-DMS-05`) |
| **Disposal register** | The metadata retained **permanently after the content is gone** (`BRU-DMS-06`) |
| **Erasure override** | A statutory obligation that defeats an erasure request. **The override and its basis must be stated to the data subject** (`BRU-CPM-11`) |
| **‡** | A period resting on a secondary source, **unverified at section level, pending G6** |

---

## 4. Terms

### 4.1 The governing rules

| # | Rule |
|---|---|
| **RS-01** | **The longest applicable obligation governs.** Where a record is caught by two obligations, it is kept for the longer, and the shorter obligation is not a licence to delete early |
| **RS-02** | **A retention period is a maximum as well as a minimum for personal data.** Keeping personal data beyond the purpose that justifies it is a storage-limitation breach, not prudence — subject to `RT9` |
| **RS-03** | **Retention is defined here and published to `M24` by `M60`. `M24` holds no independent retention configuration** (`BRU-GRC-14`, `BRU-DMS-02`) |
| **RS-04** | **Disposal is system-executed after approval, never manual, and always produces a certificate of destruction** (`BRU-DMS-05`, `FR-DMS-039`) |
| **RS-05** | **The disposal register survives the content permanently** (`BRU-DMS-06`). The company must be able to say what it destroyed and when, after it no longer has it |
| **RS-06** | **A legal hold beats everything**, including an erasure request (`BRU-SEC-23`, `BRU-DMS-02`, `BRU-GRC-15`) |
| **RS-07** | **Both directions are violations.** A record retained beyond its schedule and a record missing before its schedule expires are equally reportable (`FR-DMS-040`) |
| **RS-08** | **Audit entries are insert-only and cannot be deleted by anyone, including administrators** (`BRU-SEC-11`). They are disposed of only by scheduled disposal, never by an actor |
| **RS-09** | A released document version is immutable; a correction is a new version (`BRU-DMS-07`, `BRU-DMS-03`). **Retention attaches to the version, not to the document** |
| **RS-10** | **A period in this schedule is never shortened to accommodate a storage cost.** Storage tiering (`FR-DMS-014`) is the answer to cost, not deletion |

### 4.2 Retention by data class — `RC-01` … `RC-23`

> **Each row maps one-to-one to a purpose in `LG-008` §4.2.** That mapping is the F6 axis: every
> purpose has a retention row, and every retention row has a purpose.

| # | `LG-008` purpose | Data class | Trigger | Period | Legal basis ‡ | Deletion method (§4.6) |
|---|---|---|---|---|---|---|
| **RC-01** | `P-01` | Service order, work order, diagnosis, repair record, evidence photographs | Service order close | **Warranty period + limitation period**, minimum the tax retention (`RC-03`) | Contract; consumer claim defence; VAT where it evidences a supply | `DM-1` |
| **RC-02** | `P-02` | Identity documents and National ID captured for a statutory purpose | Purpose discharge | **Tax retention where captured for the cash rule; otherwise delete on verification** | Legal obligation | `DM-3` field-level crypto-erase |
| **RC-03** | `P-03` | Tax invoices, registers, returns, challans, certificates, determination records | End of the tax period | **7 years** — the company standard (`BRU-TAX-24`), above the **5-year ‡** statutory minimum. **§4.4 explains the difference** | VAT and income-tax record-keeping | `DM-1`, after `DM-4` archive |
| **RC-04** | `P-04` | Notification and delivery logs | Send | **13 months** | Contract; dispute evidence | `DM-2` partition drop |
| **RC-05** | `P-05` | Marketing consent record, campaign contact history | **Consent withdrawal or account closure** | **Consent record: relationship + limitation period.** Contact history: **24 months** | **The consent record is evidence that past processing was lawful** (`LG-001` `LR-15`) | `DM-1` for history; consent record survives |
| **RC-06** | `P-06` | Loyalty points ledger, referral attribution | Account closure or attribution expiry | **Relationship + tax retention on payments made** | Contract; tax on commission | `DM-1` |
| **RC-07** | `P-07` | Warranty claim, evidence pack, brand correspondence | Claim decision | **Claim decision + the brand agreement's audit window**, minimum the tax retention | Contract; brand audit right | `DM-1` |
| **RC-08** | `P-08` | Contract, entitlement consumption, SLA measurement, credit calculation | **Contract expiry** | **Contract term + limitation period** (`DT-031` §9) | Contract; credit liability defence | `DM-1`, after `DM-4` |
| **RC-09** | `P-09` | **Recovered customer data and its index** | **The agreed purge date** | **Purged at the agreed date unless a documented, approved and time-limited hold applies** (`BRU-DTS-06`). **No maximum is currently set — `O-06`** | Contract; storage limitation | **`DM-3` crypto-erase of the case key, then `DM-5`** |
| | | **Case record and access log** (distinct from the data) | Case closure | **5 years minimum** (`BRU-DTS-03`, `BRU-DTS-18`) | Processing-record obligation | `DM-1` |
| **RC-10** | `P-10` | Employee core record, contract, service dates | **Employment termination** | **Employment + limitation period ‡** | Labour Act; claim defence | `DM-1` |
| **RC-11** | `P-10` | **Payroll, tax deduction and statutory contribution records** | End of the tax period | **7 years**, aligned to `RC-03` | Tax; labour | `DM-1`, after `DM-4` |
| **RC-12** | `P-10` | Attendance, roster, leave | Period end | **Labour Act period ‡, minimum 3 years** | Labour | `DM-2` |
| **RC-13** | `P-10` | **Biometric attendance template** | **Employment termination** | **Delete at termination.** The template exists to verify attendance and has no purpose after it | Storage limitation; heightened category — **`RT6`** | **`DM-3` irreversible** |
| **RC-14** | `P-11` | Supplier and seller qualification, KYC documents, bank details | **Relationship end** | **Relationship + tax retention on transactions**, and **criminal-record checks per `RT6`** | Contract; tax; anti-fraud | `DM-3` for `S3` fields, `DM-1` for the rest |
| **RC-15** | `P-12` | **Call recordings and chat transcripts** | Capture | **6 months ‡**, extended where a complaint, claim or dispute attaches | Quality; dispute evidence — **`RT10`** | `DM-2` |
| **RC-16** | `P-13` | AI assistant conversation records | Conversation end | **90 days** for the raw conversation | Contract; service improvement within `PN5` | `DM-2` |
| **RC-17** | `P-14` | **Anonymised derived corpora** — FAQ source sets, utterance libraries, evaluation sets | Corpus supersession | **Provisional. Not operative until `LG-008` `PN5` is answered** | **UNCONFIRMED** — `AUDIT-010` HC-01 | `DM-1` and rebuild |
| **RC-18** | `P-15` | Fraud scores, investigation records | Case closure | **Limitation period** | Legitimate ground; claim defence | `DM-1` |
| **RC-19** | `P-16` | Statutory filings, returns, regulator correspondence, licences | Filing or expiry | **7 years for tax; per instrument otherwise** (`LG-024`) | Legal obligation | `DM-4` then `DM-1` |
| **RC-20** | `P-17` | Rights-request records and identity evidence | Request closure | **Request record: 5 years** as a processing record. **Identity evidence: delete on closure** | Processing-record obligation; storage limitation | `DM-1`; `DM-3` for identity evidence |
| **RC-21** | `P-18` | Complaints, disputes, legal matters, insurance claims | Matter closure | **Limitation period from closure**, and **never while a hold is in force** | Claim defence; legal hold | `DM-1` |
| **RC-22** | `P-19` | **Access logs, audit entries, security events** | Entry | **5 years**, aligned to the processing-record minimum, and **longer for privileged-access and break-glass records** | Processing records; security; `BRU-SEC-11` | `DM-2`; **never by an actor** |
| **RC-23** | `P-20` | Recruitment applications, assessments, references | Decision | **Successful: merges into `RC-10`. Unsuccessful: 12 months**, then delete | Consent; discrimination-claim defence | `DM-1` |

**Additional classes with no `LG-008` purpose row, retained for completeness:**

| # | Data class | Trigger | Period | Note |
|---|---|---|---|---|
| **RC-24** | **Location history** — technician and rider GPS pings | Capture | **90 days** at full granularity, then aggregate only | `05-02` compresses telemetry after 7 days; **`RT10`** |
| **RC-25** | **CCTV at branches and warehouses** | Capture | **30 days ‡**, extended where an incident attaches | **`RT10`**; not currently in any module's feature register |
| **RC-26** | **Non-production environment data** | Refresh | **Deleted at refresh.** Production data used in non-production must be masked (`BRU-SEC-08`) and **never contains unmasked residency-classified data in any region** (`NFR-086c`) | A masked copy is still personal data if re-identifiable |
| **RC-27** | **Backups** | Backup cycle | **Per the backup retention cycle** (§4.6.5, `O-08`) | Deletion from live does not delete from backup |

### 4.3 Retention by document class — `DC-01` … `DC-22`

> **This is the table the 44 `DT` templates point at.** Each `DT` file's row reads *"`LG-009`; …"*
> with a form of words; the authoritative period is here. **`RS-11`: where a `DT` row and this table
> differ, this table governs and the `DT` row is corrected.**

| # | Document class | `DT` files | Trigger | Period | Basis ‡ |
|---|---|---|---|---|---|
| **DC-01** | **Statutory tax documents** — Mushak 6.3, 6.2, 6.1, 6.6, 9.1 | `DT-010`…`DT-014` | End of the tax period | **7 years** (`RC-03`) | VAT and income tax |
| **DC-02** | Other finance documents — credit and debit notes, receipts, statements, proforma, consolidated invoices | `DT-015`…`DT-020` | Transaction close | **7 years**, aligned to `DC-01` — they evidence the same supplies | Tax |
| **DC-03** | **Dunning and collection letters** | `DT-018` | Issue | **Limitation period** — *"the letter trail is the evidence in any recovery action"* (`DT-018`) | Claim defence |
| **DC-04** | **Service intake and custody documents** | `DT-002`, `DT-009`, `DT-028` | Device release | **Warranty period + limitation period**, minimum the tax retention | Custody dispute; consumer claim |
| **DC-05** | Job cards, diagnostic and condition reports, completion reports | `DT-003`, `DT-004`, `DT-007` | Order close | Aligned to `DC-04` | Claim defence; warranty |
| **DC-06** | **Estimates and approval records** | `DT-005`, `DT-006` | Order close | **Identical to `DC-04` — the pair is read together or not at all** (`DT-005`/`DT-006`) | Approval evidence |
| **DC-07** | Quality checklist records | `DT-008` | Order close | **Not less than the repair warranty period plus the limitation period** | Quality; warranty |
| **DC-08** | **Procurement documents** — requisition, RFQ, PO, GRN, RTV | `DT-021`…`DT-025` | Payment or closure | **Not less than the tax retention on the purchase**, and with the award decision | Tax; procurement audit |
| **DC-09** | Stock transfer, gate pass, delivery challan, manifest, count and adjustment sheets | `DT-026`, `DT-027`, `DT-029` | Movement or count close | **Not less than the tax retention period** | Tax; stock control |
| **DC-10** | **Contracts and SLA annexes** | `DT-030`, `DT-031` | **Contract expiry** | **Term + limitation period**, with **`MD-028` version pinning preserved** (`DT-031` §9) | Contract |
| **DC-11** | **Warranty certificates and extensions** | `DT-032` | Warranty expiry | **Warranty term + limitation period** | Warranty claim |
| **DC-12** | Warranty claim evidence packs | `DT-033` | Claim decision | **Claim decision + brand audit window**, minimum tax retention (`RC-07`) | Brand agreement |
| **DC-13** | **Data destruction certificates** | `DT-034` | Issue | **Permanently, or not less than the customer's own audit window plus the limitation period.** A destruction certificate that no longer exists cannot prove the destruction | Evidence of a discharged duty |
| **DC-14** | **E-waste disposal and material recovery certificates** | `DT-035` | Issue | **Per the e-waste rules ‡** (`RT7`), not less than the tax retention and the corporate client's audit window | Environmental; `BRU-ESG-04` reconciliation |
| **DC-15** | Refurbishment grading records | `DT-036` | Sale | **Not less than the tax retention**, longer where title is questioned | Consumer claim |
| **DC-16** | Rental agreements and handover records | `DT-037` | Rental end | **Rental term + limitation period**, and while any charge is disputed | Contract |
| **DC-17** | Trade-in offer and acceptance records | `DT-038` | Completion | **Not less than the tax retention on the purchase it evidences** | Tax; title |
| **DC-18** | Seller payout and partner commission statements | `DT-039`, `DT-040` | Statement period | **Not less than the tax retention on the payments** | Tax; commission dispute |
| **DC-19** | **ISO management-system records** — NCR, CAPA, internal audit reports | `DT-043` | Record close | **Three certification cycles, and never while a certificate is live** (`BRU-QMS-13`). **Read as 9 years — `O-05`** | ISO 9001:2015 clause 7.5; certification |
| **DC-20** | **Payslips and salary certificates** | `DT-041` | Pay period | **7 years**, aligned to `RC-11` | Tax; labour |
| **DC-21** | **HR letters** — offer, confirmation, warning, termination | `DT-042` | Employment termination | **Employment + limitation period** (`RC-10`) | Labour; claim defence |
| **DC-22** | Labels, barcodes and format specifications | `DT-044` | Supersession | **Specification, not a record.** Retained while any labelled item is in circulation | Traceability |

**Governance and content documents:**

| # | Class | Trigger | Period |
|---|---|---|---|
| **DC-23** | **Legal documents in this category** (`LG-002`…`LG-024`) and every prior version | Supersession | **Permanently.** A term is defended by the version accepted, and `BRU-CPM-08` makes a notice version evidence. `CP-10` archives rather than deletes |
| **DC-24** | Controlled operational documents — SOPs, policies, work instructions | Supersession | **Not less than the ISO certification cycle plus one**, so a surveillance audit can sample the prior cycle |
| **DC-25** | Programme and content records — decision log, risk register, audit reports | Programme close | **7 years from programme close** |

### 4.4 The five-versus-seven-year reconciliation

> **`CL-01`. Two figures are in the repository and both are correct.** `AUDIT-005` found the same
> failure shape — a figure restated in eleven places and reconciled in none — so this is stated
> explicitly rather than left for a reader to trip over.

| Figure | Where it appears | What it means |
|---|---|---|
| **5 years** | Master Index Category 10 row; `CG-007` G6 checklist; `05-06` NFR-095; seven `DT` files' "at least 5 years" rows | **The statutory minimum.** VAT records must be kept at least five years ‡; processing records must be kept a minimum of five years |
| **7 years** | `M51` `BRU-TAX-24` | **The company's own retention standard** for tax documents, registers, returns, challans, certificates and determination records — *"retained seven years and remain queryable"* |

| # | Rule |
|---|---|
| **RS-12** | **`RS-01` resolves it: the longest applicable obligation governs, so the operative period for a tax record is 7 years.** The 5-year statements are not wrong; they state a floor |
| **RS-13** | **Customer-facing copy must quote the period the company actually applies, not the statutory floor.** `UI-042` `flow.dsr.erase_limits` interpolates `{years}`; **the bound value is 7** (`LG-008` §4.7.2) |
| **RS-14** | Where a tax record also contains personal data, **7 years is also the maximum** for that record, and `RS-02` applies to the personal data in it at the end of it |
| **RS-15** | **`RT3` may invert this.** If seven years turns out to be statutory rather than policy, §4.4 stops being a reconciliation and becomes a single figure — and the 5-year statements across the repository become **wrong**, not conservative |

### 4.5 What overrides the schedule

| # | Override | Effect | Authority |
|---|---|---|---|
| **OV-01** | **Legal hold** | **Absolute.** No disposal, no erasure, no code path (`BRU-DMS-03`, `BRU-DMS-04`, `BRU-SEC-23`) | Instructed and released only by `M60` (`BRU-GRC-15`, `FR-GRC-039`) |
| **OV-02** | **Live ISO certificate** | ISO records cannot be disposed while a certificate is live (`BRU-QMS-13`) | Quality Manager |
| **OV-03** | **Open dispute, claim or complaint** | Retention extends to closure plus the limitation period (`RC-21`) | Legal |
| **OV-04** | **Open regulatory matter or inspection** | Retention extends to closure | Legal with CFO |
| **OV-05** | **Unreconciled e-waste batch** | Records stay open until every item reconciles to a certificate (`BRU-ESG-04`) | Quality Manager |
| **OV-06** | **A statutory obligation defeating erasure** | Erasure refused for the affected records. **The override and its basis are stated to the data subject** (`BRU-CPM-11`) | CDO with Legal |

**The erasure-override table quoted to data subjects** — this is the set `LG-008` §4.4 and `LG-010`
must state, and no other set:

| What cannot be erased on request | Until | Because |
|---|---|---|
| Tax invoices and the transaction records behind them | **7 years** from the end of the tax period | Tax record-keeping |
| Payroll and statutory deduction records | **7 years** | Tax and labour |
| Records under a legal hold | The hold is released | `OV-01` |
| Complaint, dispute and claim records | Closure + the limitation period | Claim defence |
| Audit and access logs | Their scheduled period | `BRU-SEC-11`; they evidence lawful access |
| Consent records | Relationship + the limitation period | They prove past processing was lawful |
| Processing records (record of processing activities) | **5 years minimum** | `BRU-GRC-17`, `BRU-CPM-15` |
| Warranty and service records within warranty | Warranty expiry + the limitation period | The customer's own claim right depends on them |

### 4.6 Deletion methods

| # | Method | What it is | Used for | Evidence |
|---|---|---|---|---|
| **DM-1** | **Approved disposal batch** | Eligible records identified, presented for approval by class, disposed irreversibly, certificate issued (`FR-DMS-038`, `FR-DMS-039`) | Documents and structured records | Certificate + permanent disposal register (`BRU-DMS-06`) |
| **DM-2** | **Partition or chunk drop** | Time-partitioned data dropped on schedule (`05-02` §11) | Logs, notifications, telemetry, recordings, location history | Drop record in the disposal register |
| **DM-3** | **Crypto-erase** | Destruction of the field-level or case-level key, rendering the ciphertext unrecoverable | **`S3` fields**, biometric templates, recovered-data case content | Key-destruction record |
| **DM-4** | **Archive then dispose** | Move to cold storage in **PDF/A** for the statutory tail, then `DM-1` | Tax and contract documents | Archive manifest + `DM-1` certificate |
| **DM-5** | **Physical destruction** | For media that cannot be verifiably erased. **The technique is `LG-017` §4.6, applying the recognised sanitisation standards named in `BRU-DTS-08`** | Physical media, devices | Destruction certificate (`DT-034`) |
| **DM-6** | **Anonymisation in place** | Irreversibly removing identifiability and retaining the record for statistics | Aggregate analytics | Method record; **if reversible, it is not deletion** |

| # | Rule |
|---|---|
| **DM-R1** | **Disposal is never manual** (`BRU-DMS-05`). A person approves; the system executes |
| **DM-R2** | **`DM-6` is deletion only if re-identification is genuinely impossible.** A pseudonymised record is still personal data |
| **DM-R3** | **§4.6.5 backups.** Deletion from the live store does not delete from backup media. A record deleted from live **is not restored** on a subsequent restore, and the backup copy ages out on the backup cycle. **This position requires G6 confirmation — `O-08`** |
| **DM-R4** | **Where erasure cannot be verified, physical destruction is mandatory** (`BRU-DTS-10`) |
| **DM-R5** | Every disposal batch, and every refusal to dispose because of an override, is reported |

### 4.7 Enforcement and monitoring

| # | Rule |
|---|---|
| **EN-01** | The schedule is **defined here, published by `M60`, applied by `M24` at filing** (`FR-DMS-034`), and computed from the trigger (`FR-DMS-035`) |
| **EN-02** | **`FR-DMS-040` detects both violations**: records retained beyond schedule, and records missing before their schedule expires. **Both are treated as violations** (`RS-07`) |
| **EN-03** | A retention violation is a control failure and is recorded as one (`BRU-GRC-12`) |
| **EN-04** | **Until `M60` and `M24` deliver, the schedule is unenforced** (`O-04`). That is a stated risk, not an assumption |
| **EN-05** | An evidence pack for a claim, audit, dispute or regulatory request must be assemblable in **under five minutes** with a manifest and completeness check (`FR-DMS-041`). **A schedule that has disposed of something an evidence pack needs is a schedule error, not a retrieval failure** |

---

## 5. Liability, Exclusions and Limits

| # | Clause |
|---|---|
| **5.1** | **This schedule creates no contractual limitation.** It is an internal policy with statutory consequences |
| **5.2** | **Deleting too early is the more damaging error.** A record disposed of before its obligation expires cannot be recovered, and its absence is the company's problem in a tax assessment, a consumer claim or a regulatory inspection |
| **5.3** | **Keeping too long is a breach with a named penalty.** Personal data retained beyond its purpose is a storage-limitation failure, exposed to the penalties in `LG-008` §5.2 |
| **5.4** | **A disposal properly executed under an approved version of this schedule is defensible.** That is why `DC-23` retains every version permanently |
| **5.5** | Nothing in this schedule excuses a failure to produce a record the company was obliged to keep |

---

## 6. Data Protection

> **Audit check F6 requires zero contradiction between `LG-008`, `LG-009` and `LG-012`.**

| Axis | This file | Reconciles with |
|---|---|---|
| Purpose-to-retention mapping | `RC-01`…`RC-23` map one-to-one to `LG-008` `P-01`…`P-20` | **`LG-008` §4.2** — every purpose has a row; every row has a purpose |
| Erasure overrides quoted to data subjects | §4.5 override table | **`LG-008` §4.4 and `LG-010` §4.5** — the same set, worded the same way |
| Residency-restricted fields and their deletion method | `RC-02`, `RC-13`, `RC-14`, `DM-3` | **`LG-012` §4.3** — identical field list |
| Cross-border copies | `RC-27` backups; `RC-26` non-production | **`LG-012` §4.4** — `NFR-086c` prohibits unmasked residency-classified data in non-production in any region |
| Customer-facing period | `RS-13` — 7 years | **`UI-042` `flow.dsr.erase_limits`** and `LG-008` §4.7.2 |
| Processing-record minimum | `RC-20`, `RC-22` — 5 years | **`BRU-GRC-17`, `BRU-CPM-15`, `NFR-095`** |

| # | Rule |
|---|---|
| **F6-04** | **A change to any period in §4.2, §4.3 or §4.5 re-opens `LG-008` and `LG-010`** and every `DT` retention row that cites it (`CG-007` §7) |
| **F6-05** | **A change here is also a `M60` publication event.** The schedule in the system and the schedule in this file cannot diverge (`BRU-GRC-14`) |

---

## 7. Termination and Consequences

| Event | Consequence |
|---|---|
| **A relationship ends** | Retention continues on the triggers in §4.2. **Ending a relationship does not start a deletion; it starts a clock** |
| **A record reaches its disposal date** | It is presented for approval by class, and disposed only if approved and unheld (`FR-DMS-038`) |
| **A legal hold is placed** | Disposal stops absolutely, and the hold is evidenced with scope, instruction and authority (`FR-DMS-037`) |
| **A legal hold is released** | The disposal clock resumes; it does not restart |
| **This schedule is superseded** | The prior version is **retained permanently** (`DC-23`). A disposal is defended by the version in force when it was executed |
| **The company ceases to hold a data class** | The **disposal register survives permanently** (`BRU-DMS-06`) |

---

## 8. Dispute Resolution

| Step | Route |
|---|---|
| **1 — Retention question from a business owner** | The Chief Data Officer, with Legal for the basis and Finance for tax classes |
| **2 — A data subject disputes an erasure refusal** | `LG-010` §4.5; the override and its basis must have been stated (`BRU-CPM-11`) |
| **3 — A regulator or auditor challenges a period** | Legal Counsel with the external adviser who verified it at G6 |
| **4 — Two documents state different periods** | **Escalate immediately under `CG-013` `T-C05`.** This file governs (`RS-11`) |
| **5 — Courts** | The courts of Dhaka, Bangladesh |

---

## 9. Change Control

| Version | Date | Change | Notice given to users | Re-acceptance required |
|---|---|---|---|:--:|
| 1.0 | 2026-08-18 | Initial issue — draft, blocked on G6 by two advisers | n/a | n/a |

| # | Rule |
|---|---|
| **9.1** | **A period is never shortened retrospectively.** A record already disposed of under an earlier version stays disposed; a record still held under a longer earlier period is reassessed, not auto-deleted |
| **9.2** | **Lengthening a period for personal data requires a stated basis**, because `RS-02` makes the period a maximum too |
| **9.3** | A statutory change re-opens **G2, G5 and G6** on this file and on `LG-008`, `LG-024` and every `DT` row citing it |
| **9.4** | **Every version is retained permanently** (`DC-23`) |
| **9.5** | **12 months without a trigger re-opens G6** (`CG-006` §4.2) |
| **9.6** | **`RT3` and `RT8` answers are MAJOR changes by definition** — one may invert §4.4, the other populates more than twenty currently-unnumbered periods |

---

## 10. Cross-References

| Document | Relationship | Must not contradict |
|---|---|---|
| [`LG-008_Privacy_Notice_and_Consent_Copy.md`](LG-008_Privacy_Notice_and_Consent_Copy.md) | **Every retention reference in its §4.2** | Check **F6** — one-to-one purpose mapping |
| [`LG-010_Data_Subject_Request_Handling_Content.md`](LG-010_Data_Subject_Request_Handling_Content.md) | The §4.5 override table is what `LG-010` quotes to a requester | The overrides, worded identically |
| [`LG-012_Cross_Border_Data_Transfer_and_Residency_Statement.md`](LG-012_Cross_Border_Data_Transfer_and_Residency_Statement.md) | Residency fields, backups, non-production | Check **F6** |
| [`LG-017_Data_Recovery_and_Secure_Destruction_Terms.md`](LG-017_Data_Recovery_and_Secure_Destruction_Terms.md) | **`DM-5` technique and `RC-09` purge** | The sanitisation standard; the purge agreement |
| [`LG-018_EWaste_EPR_and_Environmental_Compliance_Statements.md`](LG-018_EWaste_EPR_and_Environmental_Compliance_Statements.md) | `DC-14` and `OV-05` | Environmental record obligations |
| [`LG-021_ISMS_Policy_Set.md`](LG-021_ISMS_Policy_Set.md) | `RC-22` logs; `DM-3` key destruction | Log retention; key management |
| [`LG-024_Regulatory_Disclosure_and_Statutory_Notice_Register.md`](LG-024_Regulatory_Disclosure_and_Statutory_Notice_Register.md) | `RC-19` and `DC-01` | The obligations that generate the periods |
| [`LG-001_Legal_Content_Register_and_Signoff_Log.md`](LG-001_Legal_Content_Register_and_Signoff_Log.md) | `DC-23`; the acceptance ledger's own retention (`LR-16`) | Version retention |
| [`../05_Document_and_Print_Templates/DT-001_Document_Template_Standard_and_Branding_Rules.md`](../05_Document_and_Print_Templates/DT-001_Document_Template_Standard_and_Branding_Rules.md) | The category standard whose §12 spine carries the retention row | **`RS-11`: this table governs every `DT` row** |
| [`../05_Document_and_Print_Templates/05D_Commercial_and_Contract/DT-031_SLA_Schedule_and_Service_Credit_Annex.md`](../05_Document_and_Print_Templates/05D_Commercial_and_Contract/DT-031_SLA_Schedule_and_Service_Credit_Annex.md) | `DC-10`, including `MD-028` version pinning | Pinning survives disposal of nothing |
| [`../03_UI_Copy_and_Microcopy/03D_Critical_Flows/UI-042_Consent_Privacy_and_Preference_Centre_Copy.md`](../03_UI_Copy_and_Microcopy/03D_Critical_Flows/UI-042_Consent_Privacy_and_Preference_Centre_Copy.md) | `RS-13` — the `{years}` value is **7** | The period quoted to customers |
| `OP-*` runbooks · `TS-017` security and privacy test pack | Operate and verify §4.6 and §4.7 | Deletion actually deletes |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Legal_Document.md` — ten sections in order; additions declared
- [x] **27 data classes and 25 document classes scheduled** with trigger, period, basis and deletion method
- [x] **`RC-01`…`RC-23` map one-to-one to `LG-008` `P-01`…`P-20`** — the F6 axis is constructed, not asserted
- [x] **The 5-versus-7-year divergence found, reconciled and explained** (§4.4), with the inversion risk named (`RS-15`)
- [x] **Six overrides stated, and the erasure-override set that must be quoted to data subjects fixed once** (§4.5)
- [x] Six deletion methods defined, including crypto-erase for `S3` and the backup position
- [x] **The "plus the limitation period" gap identified as `RT8`/`O-02`** — more than twenty `DT` rows depend on a number nobody has stated
- [x] Enforcement pipeline stated: defined here → published by `M60` → applied by `M24`
- [x] All internal links resolve
- [ ] **G6 by an external tax adviser and an external data-protection adviser** — outstanding. **`WV-02`: cannot be waived**
- [ ] **`RT1`–`RT10` answered; every `‡` period verified against a primary source** — outstanding, `PR-04` blocks approval
- [ ] **The limitation period stated** — outstanding, `O-02`; blocks disposal computation for the contract and warranty set
- [ ] **Recovered-data purge maximum set** — outstanding, `O-06`
- [ ] **Disposal and violation-detection capability proven** — outstanding, `O-07`
- [ ] **Bengali counterpart authored and signed off in context** — outstanding
- [ ] Named approver recorded — pending
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
