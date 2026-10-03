---
id: FIX-ERP2-M24
module_id: M24
module_code: DMS
module_name: Document, Records & E-Signature
category: I — Governance, Risk, Quality & Knowledge
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Quality Manager
system_owner: Governance Squad
priority: P1
wave: W3
---

# M24 — Document, Records & E-Signature
### Category I · Code `DMS` · Existing module, re-scoped in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M24 |
| **Module code** | `DMS` |
| **Category** | I — Governance, Risk, Quality & Knowledge |
| **Status** | Existing (re-scoped — knowledge content moved to M61; retention *policy* moved to M60; M24 retains retention *enforcement*) |
| **Priority** | **P1** — infrastructure; from Wave 3 every module files into it |
| **Delivery wave** | W3 (Months 9–13) |
| **Business owner** | Quality Manager |
| **System owner** | Governance Squad |
| **Delivery layers** | L1 (Odoo `mail`, `attachment`) + L2 (OCA `dms` family, `attachment_indexation`, `document_page`) + L5 (custom) + L6 (optional e-signature provider) |
| **Custom modules** | `cd_document_core`, `cd_records_retention`, `cd_esignature`, `cd_evidence_pack`, `cd_template_engine` |
| **Requirement range** | FR-DMS-001 … FR-DMS-042 |
| **Requirement count** | **42** *(measured; register estimate 28)* |
| **Effort estimate** | **19 person-weeks** *(measured; register estimate 15 PW)* |
| **Depends on** | M29 Identity · M28 Integration · M30 Platform Admin · M33 Party Master · M60 GRC *(retention policy — see §16.3)* |
| **Depended on by** | **Every module.** Principal consumers: M01, M31, M02, M03, M06, M08, M09, M12, M13, M14, M16, M18, M19, M20, M21, M23, M36, M40, M42, M51, M56, M60, M61 · Portals P01, P02, P03, P04, P05, P07, P08, P09, P11, P12 |

> **Register note.** Measured scope exceeds the pre-specification estimate by 50% in
> requirements and 27% in effort. The increase is concentrated in evidence-pack assembly and
> retention enforcement, both of which the estimate treated as incidental and which are in fact
> the module's two hardest problems. `02-02` §3 must be restated when all four Category I
> specifications are complete.

---

## 2. Purpose

M24 is **where everything is filed, and the reason anything can be found again**.

It is the single repository for every document and record the company creates or receives: job
sheets, service reports, quotations, contracts, invoices, Mushak documents, warranty evidence
packs, KYC files, employee records, calibration certificates, disposal certificates, audit
reports, policies, brand authorisations and signed customer approvals. It handles their capture,
classification, versioning, retrieval, signature, retention and — the part almost every
organisation gets wrong — their **defensible disposal at the end of retention**.

It is deliberately **not** the knowledge base. The category overview draws the distinction
sharply: M24 holds *records of what happened*, valued for legal and audit defensibility, created
once and disposed at end of retention, with restricted and logged access. M61 holds *knowledge
of how to do things*, valued for technician capability, continuously revised, broadly searchable
and available offline. Merging them produces a repository that is simultaneously too restricted
to be useful and too loose to be defensible.

### Why It Exists

The company runs on paper. Job sheets are filed in branch cabinets across 51+ locations.
Contracts are in a drawer. Warranty evidence is in an email thread. Finding a two-year-old
service record means a phone call to a branch and a physical search — the category KPI describes
today's retrieval time as **"minutes to days"** against a target of **under 10 seconds**.

That is an operational cost, but the larger exposure is legal. The statutory retention schedule
in `_CATEGORY_OVERVIEW.md` §7 runs to fourteen document classes with retentions from three
certification cycles to ten years, grounded in the Companies Act, NBR rules, the Bangladesh
Labour Act, the ICT Act and ISO obligations. Nobody can currently demonstrate compliance with
any of it. The category risk register rates *"records disposed of before retention expiry"* as
**High — legal exposure**, and the mitigation is unambiguous: **disposal is system-enforced,
never manual; legal hold overrides retention**.

M24 also carries a target that only a system can meet: **zero paper documents in active use by
Wave 6**.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD §8.22 (BR-DMS-001…018) | Document capture, versioning, search, retention, e-signature |
| ERP URD §15 (US-DMS-*) | Retrieval, filing and signature user stories |
| `_CATEGORY_OVERVIEW.md` §4 | The records/knowledge distinction and why it matters |
| `_CATEGORY_OVERVIEW.md` §7 | The fourteen-class statutory retention schedule with legal basis |
| `_CATEGORY_OVERVIEW.md` §8 | KPIs: > 96% auto-filed, < 10 s retrieval, zero paper by W6, < 5 min evidence packs, zero retention violations |
| `_CATEGORY_OVERVIEW.md` §9 | "M24 comes early because it is infrastructure" |
| `_CATEGORY_OVERVIEW.md` §10 | The High risk of premature disposal; disposal must be system-enforced |
| ISO 9001:2015 clause 7.5 | Documented information — creation, control, retention and disposition |
| M09 §5.4 FR-WTY-039, §6 T-08 | The warranty evidence pack — sealed, hashed, retained, retrievable |
| M36 §5.4 FR-QTE-037, FR-QTE-038 | E-signature and the acceptance evidence pack |
| M08 §5.1 FR-CTR-010, FR-CTR-011 | Contract documents, execution and retention |
| M12 §5.1 FR-MKP-004 | Seller KYC documents at restricted tier T5 |
| M60 §5.3 FR-GRC-032 | The retention schedule is defined by M60 and enforced by M24 |
| Bangladesh PDPA 2026 | Retention limitation and deletion procedures; records of processing retained ≥ 5 years |

---

## 3. Scope Boundary

> **This is the anti-overlap control.** Both sides of every boundary must agree.

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | The document repository: storage, addressing, deduplication and integrity of every document and record |
| 2 | **Automatic filing** — documents generated by transactions are classified, indexed and filed without human action |
| 3 | Capture from every source: system generation, upload, mobile photograph, scan, email, portal, API and bulk import |
| 4 | Classification: document class, record type, business object linkage, entity, branch, confidentiality tier |
| 5 | Metadata model, mandatory metadata per class, and metadata validation at capture |
| 6 | **Versioning** — major and minor versions, check-out/check-in, comparison, and permanent immutability of released versions |
| 7 | Controlled-document workflow: draft, review, approve, publish, supersede, withdraw *(content authored by M23, M60, M61)* |
| 8 | Full-text search and OCR, in Bengali and English, across the repository within permission scope |
| 9 | Retrieval by business object, party, asset, date, class, metadata or free text |
| 10 | **Templates and document generation** — bilingual, branded, versioned templates driving every generated document |
| 11 | **E-signature** — envelopes, signer sequencing, authentication method, signature capture, tamper-evident sealing, audit certificate |
| 12 | Wet-signature capture by scan with equivalent evidentiary metadata |
| 13 | **Retention enforcement** — applying M60's published schedule, computing disposal dates, and executing defensible disposal |
| 14 | **Legal hold** — placing, propagating, evidencing and releasing holds that override retention |
| 15 | Disposal: eligibility evaluation, approval, execution, certificate of destruction and disposal register |
| 16 | **Evidence pack assembly** — assembling a sealed, hashed, complete set of documents for a claim, audit, dispute or regulator |
| 17 | Controlled external release: scoped, approved, time-boxed and logged access for auditors, brand partners and counsel |
| 18 | Access control, confidentiality tiering and access logging on every document |
| 19 | Watermarking, redaction and controlled printing where the class requires it |
| 20 | Physical-records register: where a paper original exists, its location, custody and destruction |
| 21 | Storage lifecycle: hot, warm and cold tiers, with cost-appropriate placement and retrieval guarantees |
| 22 | Integrity assurance: content hashing, tamper detection and periodic verification sweeps |
| 23 | The document API, storage service and events consumed across the estate |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| Knowledge content — repair procedures, diagrams, solution articles, troubleshooting trees | **M61** Knowledge | Knowledge is revised continuously and read broadly; records are fixed and read narrowly *(category overview §4)* |
| The **retention policy itself** — what class is kept how long, and on what legal basis | **M60** GRC | Retention duration derives from a compliance obligation; M24 enforces the published schedule and never sets it *(BRU-GRC-14)* |
| The decision to place a legal hold | **M60** GRC | A hold arises from a legal matter; M24 executes and evidences it |
| Quality checklist content and quality records' meaning | **M23** Quality | M23 authors and interprets; M24 stores and controls |
| Policy content and attestation | **M60** GRC | — |
| Data classification scheme and data governance | **M62** Data Platform | M24 applies the confidentiality tier; M62 defines the scheme |
| Encryption key management, network and platform security | **M29** Identity & Security | M24 consumes the platform's security services |
| Identity, authentication and permission enforcement | **M29** Identity & Security | M24 declares required access; M29 authenticates and authorises |
| Business meaning of any document — what an invoice owes, what a contract commits | The owning module | M24 is deliberately content-agnostic below the metadata layer |
| Email as a communication channel | **M27** Contact Centre | M24 captures emails that are records; it is not a mail client |
| Media assets for marketing and storefront merchandising | **M35** / **M38** | Marketing media is not a record |
| Product images and catalogue media | **M37** Catalogue | Referenced by the catalogue, stored in object storage, not managed as records |
| Backup, disaster recovery and infrastructure resilience | **M29** / platform | M24 defines retrievability requirements; the platform delivers them |

### 3.3 Shared Concepts

| Concept | M24's Role | Owning Module |
|---|---|---|
| Document / record | **Owner** | M24 |
| Document class and metadata model | **Owner** | M24 |
| Retention schedule | Enforces the published version | M60 (policy) / M24 (enforcement) |
| Legal hold | Executes and evidences | M60 (decision) / M24 (execution) |
| E-signature envelope | **Owner** | M24 |
| Evidence pack | **Owner** of assembly and sealing | M24 |
| Controlled document | Controls the artefact | M23 / M60 / M61 (content) |
| Confidentiality tier | Applies to the document | M62 (scheme) / M29 (enforcement) |
| Template | **Owner** | M24 |
| Physical original | **Owner** of the register | M24 |
| Warranty evidence pack | Assembles and seals on M09's request | M09 (composition) / M24 (assembly) |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **ISO 15489** — records management | Records as evidence: authenticity, reliability, integrity and usability; metadata, classification, retention and disposition as controlled processes | **The four record characteristics as design requirements**, and the principle that a record's metadata is as much a part of the record as its content. This is the standard M24 is built against | ISO 15489's full appraisal methodology; the retention schedule is derived from statute and contract rather than from an appraisal exercise |
| **ISO 9001:2015 clause 7.5** | Control of documented information: identification, format, review and approval, availability, protection, distribution, retention and disposition | **Controlled-document workflow with mandatory approval and superseding**, and clause traceability shared with M23 | — |
| **EDRMS platforms** (Newgen, OpenText, LogicalDOC, SimplerQMS class) | Retention schedules, lifecycle control, legal hold, OCR and automated capture, workflow and approval automation, e-signature, ERP integration | **Retention and legal hold as enforced system behaviour**, **OCR-backed capture**, and the observation that ERP integration is what separates a records system from a file share. Industry framing is direct: automated capture and retention are the difference between a DMS and a folder | Buying an EDRMS: the licence cost breaches the zero-licence-cost principle, and — more importantly — auto-filing at > 96% requires the repository to live *inside* the ERP, not beside it |
| **SAP DMS / ArchiveLink** | Documents linked to business objects, with the object as the primary retrieval path | **Business-object linkage as the primary index.** Users search for "the service order", not "the file" — the single most important usability decision in the module | SAP's content-server architecture |
| **E-signature platforms** (DocuSign, Adobe Sign class) | Envelopes, signer sequencing, authentication levels, tamper-evident sealing, completion certificates, audit trails | **The envelope model in full** — sequencing, per-signer authentication, sealing and a completion certificate that is itself a record | Signing every document through a commercial provider; OTP-verified in-app signature covers the high-volume customer path at zero marginal cost, with a provider reserved for high-value instruments |
| **Bangladesh evidentiary practice** | Electronic records and signatures under the ICT Act; documentary requirements under NBR and the Companies Act | **A tiered signature model** with the assurance level matched to the instrument's legal weight, and the question of what suffices deliberately raised as an open question rather than assumed | Assuming that a click is sufficient for every instrument |
| **Odoo 19 + OCA** — `dms`, `dms_field`, `attachment_indexation`, `document_page`, `sign` | Document directories, files linked to records, full-text indexation of attachments, page-based controlled documents, signature request flows | **OCA `dms` as the L2 repository base** and `attachment_indexation` for full-text search; `dms_field` gives the business-object linkage directly | Odoo's assumption that attachments are incidental to records — retention, hold and disposal have no equivalent and are the bulk of the custom build |

**Design position.** 1000FiX differs from the benchmarks in six ways.

First, **filing is a by-product, not a task**. The target is **> 96% of documents auto-filed from
transactions**. A service report generated at handover, an invoice posted by M20, a photograph
captured on the technician app and a KYC document uploaded by a seller are all classified,
indexed, linked and retained without anyone choosing a folder. The 4% left over is genuinely
exceptional material. A records system that depends on people filing correctly fails within a
quarter — every organisation that has tried one knows this, and most conclude the users are at
fault.

Second, **the primary index is the business object, not the folder**. "Show me everything about
this service order" and "show me everything about this customer" are the two queries that matter.
Folder hierarchies exist for browsing, not for retrieval, and no user is ever required to know
one.

Third, **disposal is enforced, and it is the hardest requirement in the module**. Most document
systems retain forever because deletion is frightening. That is itself a legal exposure under
PDPA 2026's retention-limitation principle, and it is why the category KPI is *zero retention
violations* — violations in **both** directions. M24 computes disposal eligibility from M60's
published schedule, requires approval, executes irreversibly, issues a certificate of
destruction, and records the disposal permanently. A held document is never disposed, and the
hold survives every other rule.

Fourth, **evidence-pack assembly is a first-class function with a five-minute target**. A
warranty claim, a brand audit, a customer dispute and a regulator's request all need the same
thing: a complete, sealed, verifiable set of documents about one subject. Assembling those by
hand takes hours and is where evidence goes missing. M24 assembles them by reference, seals them
with a hash and logs the release.

Fifth, **bilingual OCR is a requirement, not an enhancement**. A very large proportion of
inbound documents are photographed paper — job sheets, receipts, NIDs, trade licences — much of
it handwritten Bengali. Search that does not index Bengali serves a fraction of the corpus.
Where OCR confidence is low, the system says so rather than silently returning nothing.

Sixth, **the storage strategy is designed for the cost profile of a Bangladeshi mid-market
company**. Photographic evidence at 250,000+ monthly interactions grows fast. Hot, warm and cold
tiers with declared retrieval guarantees keep seven-year retention affordable — an explicit
design constraint rather than an afterthought.

---

## 5. Functional Areas & Features

### 5.1 Capture, Classification & Repository

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-DMS-001 | Automatic filing from transactions | Classify, index, link and file every system-generated document without human action, deriving class and metadata from the generating transaction | P0 | L5 |
| FR-DMS-002 | Multi-source capture | Accept documents from system generation, web upload, mobile camera, scanner, monitored email, customer and partner portals, API and bulk import | P0 | L5 |
| FR-DMS-003 | Mobile capture quality | Capture photographed documents on the technician, rider and auditor applications with edge detection, deskew, compression and offline queuing | P0 | L5 |
| FR-DMS-004 | Document class model | Maintain a document-class taxonomy with mandatory metadata, confidentiality tier, retention class, template linkage and permitted sources per class | P0 | L5 |
| FR-DMS-005 | Business-object linkage | Link every document to one or more business objects — service order, contract, party, asset, invoice, claim, employee — as the primary retrieval path | P0 | L2 |
| FR-DMS-006 | Metadata validation | Enforce mandatory metadata per class at capture, and refuse to file an unclassifiable document without routing it to an exception queue | P0 | L5 |
| FR-DMS-007 | Deduplication | Detect duplicate content by hash and link rather than store twice, while preserving each filing context | P1 | L5 |
| FR-DMS-008 | OCR and text extraction | Extract text from images and PDFs in Bengali and English, record confidence, and flag low-confidence extractions rather than failing silently | P0 | L5 |
| FR-DMS-009 | Full-text and metadata search | Search across content and metadata within the user's permission scope, bilingually, returning ranked results in under 3 seconds | P0 | L2 |
| FR-DMS-010 | Object-centric retrieval | Retrieve every document for a business object, party or asset in one call, in under 10 seconds end to end | P0 | L5 |
| FR-DMS-011 | Folder and browse structure | Provide a browsable structure for users who prefer it, without making it the retrieval mechanism | P2 | L2 |
| FR-DMS-012 | Bulk import | Import legacy documents in bulk with mapping, classification rules, per-row validation and an outcome report | P1 | L5 |
| FR-DMS-013 | Physical-records register | Register the location, custody and condition of paper originals where they must be retained, and track their eventual destruction | P1 | L5 |
| FR-DMS-014 | Storage tiering | Place documents in hot, warm or cold storage by class, age and access pattern, with declared retrieval guarantees per tier | P1 | L5 |

### 5.2 Versioning, Templates & Controlled Documents

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-DMS-015 | Versioning | Maintain major and minor versions with check-out/check-in, and make every released version permanently immutable | P0 | L2 |
| FR-DMS-016 | Version comparison | Compare two versions of a text document and present the differences readably | P2 | L5 |
| FR-DMS-017 | Controlled-document workflow | Move controlled documents through draft, review, approval, publication, superseding and withdrawal, with approvers recorded | P0 | L2 |
| FR-DMS-018 | Superseding and obsolescence | Mark superseded versions clearly, prevent their use in current processes, and retain them for the required period | P0 | L5 |
| FR-DMS-019 | Distribution and acknowledgement | Distribute a published controlled document to a named population and track acknowledgement | P1 | L5 |
| FR-DMS-020 | Template engine | Maintain versioned, branded, bilingual templates for every generated document, with merge fields resolved from the source object | P0 | L5 |
| FR-DMS-021 | Template governance | Require approval for template changes and bind a generated document permanently to the template version used | P0 | L5 |
| FR-DMS-022 | Rendering | Render documents to PDF/A for records and to a mobile-readable format for customer delivery, asynchronously and at scale | P0 | L5 |
| FR-DMS-023 | Watermarking and controlled print | Apply watermarks, copy control and print restrictions where the class requires, and log printing of restricted classes | P1 | L5 |
| FR-DMS-024 | Redaction | Produce a redacted derivative for external release, retaining the unredacted original and linking the two | P1 | L5 |

### 5.3 E-Signature

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-DMS-025 | Signature envelopes | Create envelopes containing one or more documents, with named signers, roles, sequence and deadline | P0 | L5 |
| FR-DMS-026 | Tiered authentication | Support signature assurance levels — in-app authenticated, phone OTP, email link, wet-signature scan, and provider-backed qualified signature — selected by document class | P0 | L5 |
| FR-DMS-027 | In-person signature capture | Capture a drawn signature on the technician app, rider app or counter terminal, with identity verification, timestamp, GPS and device identity | P0 | L5 |
| FR-DMS-028 | Remote signature | Deliver a signature request by portal, WhatsApp, SMS or email, and capture the signature on a mobile browser over 3G | P0 | L5 |
| FR-DMS-029 | Sealing and tamper evidence | Seal the signed document with a content hash and tamper-evident protection at completion | P0 | L5 |
| FR-DMS-030 | Completion certificate | Generate a signature completion certificate recording every signer, method, authentication evidence, timestamp and IP or device — itself retained as a record | P0 | L5 |
| FR-DMS-031 | Reminders, expiry and decline | Remind signers on schedule, expire envelopes at deadline, and record declines with reason | P1 | L5 |
| FR-DMS-032 | Provider integration | Integrate an external qualified e-signature provider for instruments above the declared value or risk threshold, without changing the calling interface | P2 | L6 |
| FR-DMS-033 | Signature verification | Verify the integrity and signer evidence of a previously signed document on demand, years later | P0 | L5 |

### 5.4 Retention, Legal Hold & Disposal

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-DMS-034 | Retention schedule application | Consume M60's published, versioned retention schedule and apply the correct retention class to every document at filing | P0 | L5 |
| FR-DMS-035 | Retention computation | Compute the disposal date from the retention trigger — creation, transaction close, contract expiry, employment termination, last customer transaction — per class | P0 | L5 |
| FR-DMS-036 | Legal hold | Place a hold on a scope defined by object, party, class, date range or matter; propagate it transactionally; and prevent disposal absolutely while it is in force | P0 | L5 |
| FR-DMS-037 | Hold evidencing and release | Evidence when a hold was placed, by whose instruction, over what scope, and record its release with authority | P0 | L5 |
| FR-DMS-038 | Disposal eligibility and approval | Identify documents eligible for disposal, present them for approval by class, and refuse disposal of anything held or unapproved | P0 | L5 |
| FR-DMS-039 | Defensible disposal | Execute disposal irreversibly, issue a certificate of destruction, and retain the disposal register permanently as metadata after the content is gone | P0 | L5 |
| FR-DMS-040 | Retention violation detection | Detect and report documents retained beyond their schedule and documents missing before their schedule expires, and treat both as violations | P0 | L5 |
| FR-DMS-041 | **Evidence pack assembly** | Assemble a complete, sealed, hashed evidence pack for a claim, audit, dispute or regulatory request in under five minutes, with a manifest and completeness check | P0 | L5 |
| FR-DMS-042 | Controlled external release | Release documents or packs to an external party under scoped, approved, time-boxed, watermarked and fully logged access | P0 | L5 |

*(Full requirement text is mirrored in `05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md`.)*

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Content-addressed storage** | Documents are stored by content hash in object storage; the database holds metadata and references only. Deduplication and tamper detection follow from the addressing scheme |
| T-02 | **Immutable released versions** | A released version is write-once. Correction produces a new version; the prior version is never mutated or deleted outside the disposal process |
| T-03 | **Metadata is part of the record** | Metadata is versioned with the document and included in the integrity hash, per ISO 15489 |
| T-04 | **Transactional filing** | A document generated by a transaction is filed in the same transaction as the business event, through the outbox. A committed invoice always has its document |
| T-05 | **Hold precedence** | Legal hold is evaluated last and overrides every other rule. No code path can dispose a held document — enforced at the storage layer, not only in application logic |
| T-06 | **Irreversible, evidenced disposal** | Disposal removes content from every tier including backups within the declared window, and writes a permanent disposal record that survives the content |
| T-07 | **Offline capture queue** | Mobile-captured documents queue locally, survive app restart, and replay idempotently; a photograph taken offline is never lost |
| T-08 | **Async rendering pipeline** | Generation and OCR run asynchronously with retry and dead-lettering; a rendering failure never blocks a business transaction |
| T-09 | **Bilingual indexing** | Full-text indexing supports Bengali and English with ICU collation and transliteration handling; index lag ≤ 60 s after filing |
| T-10 | **Permission-scoped search** | Search results are filtered by permission before ranking, so a user can never infer the existence of a document they may not see |
| T-11 | **Access logging on every read** | Every retrieval of a restricted-tier document is logged with actor, purpose where required, and time *(EA-10)* |
| T-12 | **Storage tier transparency** | Tier placement is invisible to callers; cold retrieval returns a declared wait rather than an error |
| T-13 | **Integrity sweeps** | A scheduled sweep verifies stored content against its hash and reports any divergence as an incident |
| T-14 | **Signature evidence longevity** | Signature verification remains possible for the full retention period, independent of any external provider's continued existence |
| T-15 | **Performance envelope** | Object-centric retrieval ≤ 10 s end to end · search ≤ 3 s p95 · document read ≤ 500 ms p95 for hot tier · evidence pack ≤ 5 min · filing throughput ≥ 50 documents/second sustained |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M24 |
|---|---|---|
| **Service centre agent** | Files a paper job sheet in a cabinet; a two-year-old record means a physical search | Every document for a customer or device appears on the record in seconds |
| **Technician** | Carries paper forms and hands them in at the end of the day | Captures evidence on the phone; it files itself against the job, offline-tolerant |
| **Warranty officer** | Assembles claim evidence from email threads and folders over hours | Requests an evidence pack; it arrives sealed and complete in minutes |
| **Finance officer** | Searches for the invoice and the supporting document separately | Both are on the transaction, linked, with the Mushak document retained to schedule |
| **Account manager** | Cannot find the executed contract; sends the customer the wrong version | The current executed version is on the contract, with every prior version retained |
| **HR officer** | Keeps employee files in a locked cabinet with no retention discipline | Files are tiered, access-logged and retained for the statutory ten years |
| **Quality Manager** | Spends the week before an audit assembling evidence | Releases a scoped pack to the auditor, watermarked, time-boxed and logged |
| **Customer** | Loses their job sheet and cannot prove what was agreed | Downloads the signed approval, service report and invoice from the portal |
| **CFO / legal counsel** | Cannot demonstrate compliance with any retention obligation | Sees retention position by class, holds in force, disposals executed and violations — of which there should be none |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Document retrieval time** | Object-centric indexing over a content-addressed repository | **Minutes-to-days → under 10 seconds** *(category KPI)*. Across 51+ branches and 250,000+ monthly interactions this is a structural change in how quickly the company can answer any question about its own history |
| **Automatic filing** | Documents generated by transactions file themselves | **> 96% auto-filed** *(category KPI)* — the mechanism that makes every other benefit achievable |
| **Elimination of paper** | Digital capture, signature and retention across every process | **Zero paper documents in active use by Wave 6** *(category KPI)*, removing physical storage cost, courier movement between branches, and loss |
| **Evidence pack assembly** | Assembly by reference with sealing and manifest | **Hours → under 5 minutes** *(category KPI)*. This is the mechanism behind M09's **> 95% of claims submitted within 72 hours**, which in turn carries the **BDT 100 lac/year** warranty recovery |
| **Retention compliance** | System-enforced retention and defensible disposal with hold precedence | **Zero retention violations** *(category KPI)*, against a **High** rated legal exposure. Premature disposal of a record needed in litigation, or retention of personal data beyond its lawful period under PDPA 2026, are both material |
| **Administrative labour** | No filing, no searching, no re-sending, no re-printing | A significant component of the **BDT 62 lac/year** administrative saving in the business case |
| **Dispute defensibility** | Signed acceptances, condition photographs and handover records retrievable years later | Supports M36's **< 1.5% quotation-to-invoice variance** and reduces write-offs from unwinnable disputes |
| **Audit cost** | One evidence request serves the certification body, the brand partner and the statutory auditor | Reduces the internal cost of every audit the company undergoes |

> **Discipline note.** M24 is infrastructure. Its benefits are realised *through* other modules —
> M09's claim speed, M36's dispute defensibility, M23's audit readiness. No standalone revenue
> should be attributed to it, and none is claimed. Its own measures are the five category KPIs
> above, all of which are operational rather than financial.

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Corporate memory** | The company stops losing its own history to branch cabinets, staff departures and water damage |
| **Legal defensibility** | A record with authenticity, integrity, reliability and usability — the four ISO 15489 characteristics — is admissible. A photocopy in a drawer is arguable |
| **Privacy compliance as a positive act** | Deleting personal data at the end of its lawful period is a PDPA 2026 obligation. A system that only ever retains is not compliant, merely cautious |
| **Trust with brand partners and corporates** | Producing complete, sealed, timely evidence changes how institutional counterparties treat the company |
| **Resilience** | Documents in tiered object storage with integrity verification survive fire, flood and theft in a way that branch cabinets across 51+ locations do not |
| **Environmental** | Eliminating paper across 51+ branches is a measurable environmental improvement consistent with the M18 sustainability position |
| **Foundation for AI** | Every M26 model that reads documents — OCR-driven intake, fault classification from photographs, contract analysis — depends on a corpus that exists and is indexed |

---

## 8. Lifecycle & State Model

M24 owns three lifecycles: the **document record**, the **signature envelope**, and the
**disposal batch**.

### 8.1 Document Record

```
              ┌──────────┐
              │ CAPTURED │ from transaction, upload, mobile, scan, email, API
              └────┬─────┘
                   │ classified; mandatory metadata validated
        ┌──────────┴───────────┐
        │ classification fails │
   ┌────▼──────────┐           │
   │  EXCEPTION    │           │ (worked queue — never silently dropped)
   │    QUEUE      │───────────┘
   └────┬──────────┘
        │ classified manually
   ┌────▼─────┐
   │  FILED   │ indexed, linked to business objects, retention class applied
   └────┬─────┘
        │
        ├──────────────► (controlled documents only)
        │               DRAFT ─► IN REVIEW ─► APPROVED ─► PUBLISHED ─► SUPERSEDED
        │
   ┌────▼─────┐
   │  ACTIVE  │ retrievable, searchable, within retention
   └────┬─────┘
        │ retention period elapsed
   ┌────▼──────────────┐
   │ DISPOSAL ELIGIBLE │◄──── blocked absolutely while ON HOLD
   └────┬──────────────┘
        │ disposal approved by class owner
   ┌────▼──────────┐
   │  DISPOSING    │
   └────┬──────────┘
        │ content removed from all tiers; certificate issued
   ┌────▼──────────┐
   │   DISPOSED    │ metadata and disposal record retained permanently
   └───────────────┘

  Cross-cutting: ON HOLD is a flag, not a state. It is evaluated last, overrides
  every retention rule, and can be applied at any point from Filed onward.
```

### 8.2 Signature Envelope

```
DRAFT ──► SENT ──► VIEWED ──► PARTIALLY SIGNED (sequenced signers) ──► COMPLETED
   │        │                                                             │
   │        ├──► DECLINED (reason recorded)                    sealed + certificate
   │        └──► EXPIRED (deadline elapsed)                               │
   └──► VOIDED (by issuer, reason recorded)                          ┌────▼─────┐
                                                                     │  FILED   │
                                                                     └──────────┘
```

### 8.3 Disposal Batch

```
PROPOSED (eligibility computed) ──► UNDER REVIEW (held items excluded and listed)
   ──► APPROVED (by class owner) ──► EXECUTING ──► COMPLETED (certificate issued)
                                          │
                                          └──► FAILED (partial disposal impossible;
                                                       batch rolled back, incident raised)
```

### Transition Guards

| From | To | Guard | Actor |
|---|---|---|---|
| Captured | Filed | Class assigned; mandatory metadata present and valid; retention class resolved | System / capturing user |
| Captured | Exception Queue | Classification or mandatory metadata cannot be resolved | System |
| Exception Queue | Filed | Class and metadata supplied manually | Records officer |
| Filed | Published *(controlled)* | Approval recorded by an approver other than the author | Document owner + approver |
| Published | Superseded | A later version published, or explicit withdrawal | Document owner |
| Active | Disposal Eligible | Retention period elapsed per the published schedule **and** no hold in force | System |
| Disposal Eligible | Disposing | Disposal batch approved by the class owner | Class owner + Quality Manager |
| Disposing | Disposed | Content removed from every tier; certificate issued; disposal record written | System |
| Any | On Hold | Hold instructed by M60 with a matter reference | M60 |
| On Hold | *(hold released)* | Release instructed by M60 with authority recorded | M60 |
| Draft *(envelope)* | Sent | All signers, sequence, authentication level and deadline defined | Issuer |
| Partially Signed | Completed | Every required signer has signed | System |
| Completed | Filed | Document sealed; completion certificate generated and filed | System |

---

## 9. Business Rules

Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-DMS-01 | Every document has exactly one document class and one retention class at all times | **H** | Quality Manager |
| BRU-DMS-02 | The retention schedule is published by M60 and applied by M24; M24 holds no independent retention configuration | **H** | CFO |
| BRU-DMS-03 | A legal hold overrides every retention rule and cannot be bypassed by any code path | **H** | CFO |
| BRU-DMS-04 | A held document can never be disposed, and a hold can be released only by M60 with recorded authority | **H** | CFO |
| BRU-DMS-05 | Disposal is system-executed after approval, never manual, and always produces a certificate of destruction | **H** | Quality Manager |
| BRU-DMS-06 | Disposal metadata and the disposal register are retained permanently, after the content is gone | **H** | Quality Manager |
| BRU-DMS-07 | A released document version is immutable; correction produces a new version | **H** | CTO |
| BRU-DMS-08 | A document that cannot be classified is queued as an exception; it is never discarded and never filed unclassified | **H** | Quality Manager |
| BRU-DMS-09 | A generated document binds permanently to the template version used | **H** | Quality Manager |
| BRU-DMS-10 | The approver of a controlled document cannot be its author | **H** | Quality Manager |
| BRU-DMS-11 | A superseded controlled document cannot be used in a current process and is visibly marked | **H** | Quality Manager |
| BRU-DMS-12 | Every access to a restricted-tier document is logged with actor and time *(EA-10)* | **H** | CTO |
| BRU-DMS-13 | External release of any document requires scope, approval, expiry and logging | **H** | Quality Manager |
| BRU-DMS-14 | Search never reveals the existence of a document the user may not access | **H** | CTO |
| BRU-DMS-15 | A signed document is sealed at completion and its completion certificate is itself retained as a record | **H** | Quality Manager |
| BRU-DMS-16 | Signature verification must remain possible for the document's full retention period, independent of any external provider | **H** | CTO |
| BRU-DMS-17 | The signature assurance level is determined by document class and cannot be downgraded by the requester | **H** | CFO |
| BRU-DMS-18 | A transaction that generates a document files it in the same transaction; a committed business event never lacks its document | **H** | CTO |
| BRU-DMS-19 | Retention violations in either direction — retained too long, or missing too early — are reported and investigated | **H** | Quality Manager |
| BRU-DMS-20 | Personal data is disposed at the end of its lawful retention period unless held; retention beyond that period is a violation, not caution *(PDPA 2026)* | **H** | CFO |

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.document` | `fix_document` | The record | name, class_id, content_hash, storage_ref, storage_tier, mime, size, language, source, captured_at, captured_by, entity_id, branch_id, confidentiality_tier, retention_class_id, disposal_due_at, state, current_version_id |
| `fix.document.version` | `fix_document_version` | Versions | document_id, major, minor, content_hash, storage_ref, created_at, created_by, released, release_note, superseded_by_id |
| `fix.document.class` | `fix_document_class` | Class taxonomy | code, name_bn, name_en, parent_id, mandatory_metadata_json, confidentiality_tier, retention_class_id, template_id, permitted_sources, requires_signature, signature_assurance_level |
| `fix.document.link` | `fix_document_link` | Business-object linkage | document_id, object_model, object_id, link_role, primary |
| `fix.document.metadata` | `fix_document_metadata` | Class-specific metadata | document_id, key, value, valid_from, included_in_hash |
| `fix.document.text` | `fix_document_text` | Extracted text and OCR | document_id, version_id, language, text, ocr_confidence, extracted_at, engine_version |
| `fix.document.exception` | `fix_document_exception` | Unclassifiable capture queue | source, raw_ref, cause, received_at, assigned_to, resolved_at, resulting_document_id |
| `fix.document.template` | `fix_document_template` | Templates | code, class_id, version, language, body_ref, merge_fields_json, approved_by, effective_from, state |
| `fix.document.access.log` | `fix_document_access_log` | Access logging | document_id, actor_id, action (view/download/print/release), at, ip_or_device, purpose, external_party_id |
| `fix.retention.class` | `fix_retention_class` | Applied retention classes | code, schedule_version, description, trigger_event, duration_months, legal_basis, source_obligation_ref |
| `fix.retention.schedule.version` | `fix_retention_schedule_version` | Published schedule from M60 | version, published_at, published_by, content_hash, classes_json |
| `fix.legal.hold` | `fix_legal_hold` | Holds | matter_ref, scope_json, instructed_by, instructed_at, released_by, released_at, evidence_ref, state |
| `fix.legal.hold.document` | `fix_legal_hold_document` | Hold membership | hold_id, document_id, applied_at, released_at |
| `fix.disposal.batch` | `fix_disposal_batch` | Disposal batches | code, class_id, period, proposed_count, excluded_held_count, approved_by, approved_at, executed_at, certificate_document_id, state |
| `fix.disposal.record` | `fix_disposal_record` | Permanent disposal register | document_ref, class_id, captured_at, disposed_at, batch_id, approver_id, content_hash_at_disposal, certificate_ref |
| `fix.retention.violation` | `fix_retention_violation` | Violations in both directions | document_ref, violation_type (over_retained/missing_early), detected_at, class_id, state, investigation_ref |
| `fix.signature.envelope` | `fix_signature_envelope` | Envelopes | code, subject_object_ref, document_ids, assurance_level, deadline_at, state, created_by, completed_at, sealed_hash |
| `fix.signature.signer` | `fix_signature_signer` | Signers | envelope_id, party_id, role, sequence, auth_method, delivery_channel, viewed_at, signed_at, declined_at, decline_reason, ip_or_device, geo |
| `fix.signature.certificate` | `fix_signature_certificate` | Completion certificate | envelope_id, document_id, signers_json, evidence_json, generated_at, hash |
| `fix.evidence.pack` | `fix_evidence_pack` | Assembled packs | purpose (claim/audit/dispute/regulatory), subject_object_ref, requested_by, document_ids, manifest_json, completeness_state, sealed_hash, assembled_at, released_to, expires_at |
| `fix.external.release` | `fix_external_release` | Controlled release grants | subject_type, subject_id, external_party_id, scope_json, approved_by, granted_at, expires_at, watermark_applied, access_log_ref, revoked_at |
| `fix.physical.record` | `fix_physical_record` | Paper originals | document_id, location, custodian_id, box_ref, received_at, condition, destruction_due_at, destroyed_at, destruction_evidence_ref |
| `fix.document.integrity.check` | `fix_document_integrity_check` | Integrity sweeps | run_at, documents_checked, divergences_found, incident_refs |

### 10.2 Referenced Entities

| Entity | Owned By | Access Pattern |
|---|---|---|
| Retention schedule (policy), legal hold instructions | M60 | Command intake + published configuration |
| Confidentiality tier scheme, data classification | M62 | Configuration read |
| Identity, roles, permissions, external party scoping | M29 | Live read; enforcement delegated |
| Party records for signers and recipients | M33 | Live read |
| Every business object a document links to | Owning module | Reference only; M24 never interprets |
| Controlled-document content ownership | M23, M60, M61 | Content authored elsewhere |
| Branch, entity, language configuration | M30 | Configuration read |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-DMS-01 | Any module generates a document | Classify from the generating context, apply metadata, link the business object, apply the retention class, file transactionally | Roll back with the transaction; never commit a business event without its document |
| AUT-DMS-02 | Document filed | Queue OCR and text extraction; index for search | Retry with backoff; flag as unindexed rather than failing the filing |
| AUT-DMS-03 | Classification cannot be resolved | Place in the exception queue and assign to a records officer with the source context | Escalate after the declared interval; never discard |
| AUT-DMS-04 | OCR confidence below threshold | Flag the document as low-confidence, retain the extraction, and exclude it from confident search claims | Log |
| AUT-DMS-05 | Duplicate content detected | Link to the existing content rather than storing again, preserving each filing context | Store separately and flag for review |
| AUT-DMS-06 | M60 publishes a new retention schedule version | Adopt the version, recompute disposal dates across affected classes, and report the change impact | Block adoption; alert the CFO and Quality Manager; continue on the prior version |
| AUT-DMS-07 | M60 instructs a legal hold | Apply the hold across the declared scope transactionally and evidence the application | Fail the instruction visibly; never partially apply |
| AUT-DMS-08 | Retention period elapses | Mark disposal-eligible, excluding anything held | Log; retry |
| AUT-DMS-09 | Disposal cycle due | Propose a disposal batch by class, list excluded held items, and route for approval | Escalate to the Quality Manager |
| AUT-DMS-10 | Disposal batch approved | Execute removal across every storage tier, issue the certificate, write the permanent disposal record | Roll back the batch; raise an incident; never partially dispose |
| AUT-DMS-11 | Nightly retention scan | Detect over-retained and missing-early documents and raise violations | Log; escalate on repeat |
| AUT-DMS-12 | Signature envelope sent | Deliver to each signer in sequence on their channel, start the deadline clock, schedule reminders | Retry on the fallback channel; alert the issuer after two failures |
| AUT-DMS-13 | All signers complete | Seal the document, generate the completion certificate, file both, and notify the requesting module | Retry sealing; block completion notification until sealed |
| AUT-DMS-14 | Envelope deadline reached | Expire, notify the issuer, and offer re-issue | Log |
| AUT-DMS-15 | Evidence pack requested | Assemble by reference, verify completeness against the requested composition, seal and hash, notify the requester | Return a partial pack explicitly marked incomplete with the missing items named — never silently |
| AUT-DMS-16 | External release granted | Apply watermarking, set expiry, provision scoped access, and begin access logging | Deny the release; alert |
| AUT-DMS-17 | External release expires | Revoke access automatically and produce the access log for the release | Force revocation; alert |
| AUT-DMS-18 | Storage tiering evaluation | Move documents between hot, warm and cold tiers by class, age and access pattern | Leave in place; log |
| AUT-DMS-19 | Scheduled integrity sweep | Verify stored content against hashes and raise incidents on divergence | Escalate to CTO |
| AUT-DMS-20 | Physical record destruction due | Notify the custodian, require destruction evidence, and record it against the physical register | Escalate to Quality Manager |

---

## 12. Interfaces

### 12.1 Upstream — M24 Consumes

| Source | What | Mechanism |
|---|---|---|
| **M60 GRC** | The published, versioned retention schedule; legal hold and release instructions | Command + configuration |
| M62 Data Platform | Confidentiality tier scheme and data classification | Configuration read |
| M29 Identity | Identity, roles, permissions, external party scoping, encryption services | Live read + platform service |
| M33 Party Master | Parties as signers, recipients and external release targets | Live read |
| M30 Platform Admin | Entity, branch, language and channel configuration | Configuration read |
| **Every transactional module** | Generated documents, captured evidence, uploaded files, and the business context that classifies them | API + transactional outbox |
| M23 Quality · M60 GRC · M61 Knowledge | Controlled-document content requiring version and approval control | API |
| M27 Contact Centre | Emails and attachments that constitute records | Event + API |

### 12.2 Downstream — M24 Provides

| Consumer | What | Mechanism |
|---|---|---|
| **Every module** | Document storage, retrieval, versioning, templates, rendering | REST + service |
| M09 Warranty | Warranty evidence pack assembly and sealing; claim document retention | REST `POST /api/v1/documents/evidence-pack` |
| M36 Quotation | Quotation rendering, e-signature envelopes, acceptance evidence packs | REST |
| M08 Contract | Contract documents, execution envelopes, version control, retention | REST |
| M12 Marketplace | Seller KYC storage at tier T5, agreement execution | REST |
| M23 Quality | Controlled procedures, audit reports, evidence release for auditors | REST |
| M60 GRC | Evidence storage for control tests, policy artefacts, hold confirmation, disposal evidence | REST + events |
| M19 · M20 · M51 | Financial documents and Mushak retention to the statutory schedule | REST |
| M21 · M56 | Employee records at ten-year retention | REST |
| M06 Data Services · M18 E-Waste | Destruction and disposal certificates at seven-year retention | REST |
| M61 Knowledge | Storage of manuals and diagrams referenced by articles | REST |
| M25 BID | Document volume, retention position and access analytics | Warehouse extract |
| All portals | Customer, partner, seller and auditor document access within scope | REST via M28 |

### 12.3 Domain Events Published

| Event | Payload Summary | Principal Consumers |
|---|---|---|
| `document.filed` | document id, class, links, retention class, disposal due | Owning module, M25 |
| `document.classification_failed` | source, cause, exception id | Records officer alerting |
| `document.version_released` | document id, version, approver | M23, M60, M61 |
| `document.superseded` | document id, old version, new version | M23, M60, M61 |
| `signature.envelope_sent` | envelope id, signers, deadline | Requesting module, M27 |
| `signature.completed` | envelope id, document id, certificate ref, sealed hash | **M36, M08, M12, M40** |
| `signature.declined` / `signature.expired` | envelope id, signer, reason | Requesting module |
| `evidence_pack.assembled` | pack id, purpose, subject, completeness, sealed hash | **M09, M23, M60** |
| `document.hold_applied` / `hold_released` | hold id, scope, document count | **M60**, audit |
| `document.disposal_executed` | batch id, class, count, certificate ref | **M60**, M23, audit |
| `document.retention_violation` | document ref, type, class | **M60**, M23, Quality alerting |
| `document.external_release_granted` / `expired` | release id, party, scope, expiry | M60, audit |
| `document.integrity_divergence` | document ref, expected hash, found hash | CTO, incident management |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-DMS-01 | Object storage and CDN | Bidirectional | Content storage across hot, warm and cold tiers |
| INT-DMS-02 | OCR engine (self-hosted, Bengali-capable) | Outbound | Text extraction from photographed and scanned documents |
| INT-DMS-03 | Qualified e-signature provider *(L6, optional)* | Bidirectional | Provider-backed signature for high-value instruments |
| INT-DMS-04 | Monitored email mailboxes | Inbound | Capture of emails and attachments that constitute records |
| INT-DMS-05 | Scanner and MFD fleet | Inbound | Bulk scanning during the paper-elimination programme |
| INT-DMS-06 | Malware scanning service | Outbound | Scanning of every inbound file before storage |

### 12.5 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/documents` | POST | File a document with class and links | Every module, portals |
| `/api/v1/documents/{id}` | GET | Retrieve metadata and a content URL, permission-scoped | Every module, portals |
| `/api/v1/documents/by-object` | GET | Every document for a business object | Every module, portals |
| `/api/v1/documents/search` | GET | Bilingual full-text and metadata search within scope | P03, P01, P04 |
| `/api/v1/documents/{id}/versions` | GET/POST | Version history; create a new version | P03, M23, M60 |
| `/api/v1/documents/generate` | POST | Render a document from a template and source object | Every module |
| `/api/v1/documents/evidence-pack` | POST | Assemble, verify and seal an evidence pack | M09, M23, M60, P03 |
| `/api/v1/signatures/envelopes` | POST | Create and send a signature envelope | M36, M08, M12, M40, P02 |
| `/api/v1/signatures/envelopes/{id}` | GET | Envelope status and signer progress | Requesting module |
| `/api/v1/public/sign/{token}` | GET/POST | Tokenised remote signing surface | Unauthenticated signer |
| `/api/v1/signatures/{id}/verify` | POST | Verify integrity and signer evidence | P03, dispute handling |
| `/api/v1/retention/schedule` | POST | Publish a retention schedule version *(M60 only)* | **M60** |
| `/api/v1/holds` | POST/DELETE | Apply and release a legal hold *(M60 only)* | **M60** |
| `/api/v1/disposal/batches` | GET/POST | Propose, approve and execute disposal | P03 |
| `/api/v1/releases` | POST | Grant a scoped, time-boxed external release | P03 |
| `/api/v1/documents/exceptions` | GET/POST | Work the classification exception queue | P03 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R32 Quality Manager / ISO Coordinator | C R U D A | All — the module's principal owner; disposal approval |
| R02 Chief Technology Officer | R U A | Configuration, integrity, storage, security |
| R03 Chief Financial Officer | R A | Financial records, retention position, holds, disposal oversight |
| R26 Finance Manager | C R U | Financial and tax documents |
| R30 HR Manager / R31 HR Officer | C R U | Employee records (T5 where personal) |
| R06 Branch Manager | C R U | Own branch's documents |
| R08 Service Centre Agent | C R | Own branch — capture and retrieve |
| R10 / R11 / R12 Technician | C R | Own jobs — capture evidence, read job documents |
| R16 Rider / Delivery Agent | C R | Own manifest — POD and handover capture |
| R28 Warranty Claims Officer | C R | Claim documents and evidence packs |
| R24 Marketplace Operations Officer | C R | Seller KYC (T5) and agreements |
| R22 Account Manager (Corporate) | C R | Contracts and customer documents in scope |
| R33 IT / System Administrator | R U | Configuration, storage tiers, integrations |
| R36 Customer | R | Own documents only — job sheets, reports, invoices, signed approvals |
| R37 Corporate Portal User | R | Own company's documents, role-scoped |
| R38 External Party | R | **Scoped, approved, time-boxed, watermarked, logged release only** *(EA-01, EA-02, EA-10)* |
| — Records Officer *(new position under R32)* | C R U | Exception queue, classification, physical register, disposal preparation |

**Field-level restrictions and tiering.** Confidentiality tiers follow `05-04` §4. Tier **T5**
documents — payroll, NID records, bank details, data-recovery case content, call recordings,
audit logs, biometric templates, seller KYC — require named allow-list access, step-up
authentication and logged access. `nid_number`, `bank_account` and `seller_kyc_document`
restrictions in `05-04` §5 are enforced at the document level as well as the field level.

**Segregation of duties.** The approver of a controlled document cannot be its author
(BRU-DMS-10). **SOD-23** *(to be registered in `05-04` §6)* — the officer who prepares a disposal
batch cannot approve it. Legal hold placement and release are reserved to M60 and cannot be
performed within M24 by any role.

---

## 14. Reports & Analytics

| Report / Dashboard | Audience | Frequency | Key Content |
|---|---|---|---|
| Retention position by class | CFO, Quality Manager | Monthly | Documents by class, age band, disposal due, held, over-retained |
| **Retention violation register** | CFO, Quality Manager, M60 | Weekly | Over-retained and missing-early documents with cause and investigation status |
| Disposal register | Quality Manager, auditor | Per batch | What was disposed, when, under what approval, with which certificate |
| Legal hold register | CFO, legal counsel | Monthly | Holds in force, scope, document counts, age, matter reference |
| Auto-filing rate | Quality Manager, CTO | Weekly | Proportion filed automatically vs manually vs via exception queue, by source module |
| Classification exception queue | Records Officer, Quality Manager | Daily | Open exceptions by age, source and cause |
| Retrieval performance | CTO, Quality Manager | Weekly | Retrieval and search latency against the 10-second and 3-second targets, by tier |
| Paper elimination progress | Quality Manager, Ops Director | Monthly | Paper documents still in active use by process and branch, against the zero-by-W6 target |
| E-signature performance | CCO, Quality Manager | Weekly | Envelopes sent, viewed, completed, declined, expired; completion time by channel and assurance level |
| Evidence pack performance | Warranty Officer, Quality Manager | Weekly | Packs assembled, completeness rate, assembly time against the 5-minute target |
| External release log | Quality Manager, CFO, M60 | Monthly | Releases granted, to whom, scope, expiry, access made |
| Restricted access audit | CTO, Quality Manager, M60 | Monthly | Access to T5 documents by actor, purpose and volume; anomalies |
| Storage cost and tiering | CTO, CFO | Monthly | Volume and cost by tier and class; tiering effectiveness |
| Integrity sweep results | CTO | Monthly | Documents verified, divergences, incidents raised |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W5 Target | W8 Target |
|---|---|---|---|---|
| KPI-C24-01 | Documents auto-filed from transactions | 0% | 90% | **> 96%** |
| KPI-C24-02 | Document retrieval time | minutes to days | < 30 s | **< 10 s** |
| KPI-C24-03 | Paper documents in active use | 100% | 25% | **Zero by W6** |
| KPI-C24-04 | Evidence pack assembly time | hours | < 15 min | **< 5 min** |
| KPI-C24-05 | Retention violations | unknown | 0 | **0** |
| KPI-C24-06 | Search latency p95 | n/a | ≤ 4 s | **≤ 3 s** |
| KPI-C24-07 | Classification exception rate | n/a | < 8% | **< 3%** |
| KPI-C24-08 | Exception queue items resolved within 2 working days | n/a | 90% | **> 98%** |
| KPI-C24-09 | E-signature completion rate | n/a | 80% | **> 92%** |
| KPI-C24-10 | Median time to signature completion | n/a | < 24 h | **< 6 h** |
| KPI-C24-11 | Evidence packs complete on first assembly | n/a | 90% | **> 98%** |
| KPI-C24-12 | Documents disposed on schedule after eligibility | n/a | 95% | **100%** |
| KPI-C24-13 | Held documents disposed in error | n/a | **0** | **0** |
| KPI-C24-14 | Integrity divergences detected | n/a | 0 | **0** |
| KPI-C24-15 | OCR extraction success on Bengali documents | n/a | 80% | **> 92%** |

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo `mail`, `base` attachments, `portal` | 10% |
| L2 | OCA `dms`, `dms_field`, `dms_attachment_link`, `attachment_indexation`, `document_page`, `document_page_approval`, `queue_job` | 30% |
| L5 | `cd_document_core`, `cd_records_retention`, `cd_esignature`, `cd_evidence_pack`, `cd_template_engine` | 58% |
| L6 | Qualified e-signature provider *(optional, threshold-based)* | 2% |

> **Layer note.** OCA `dms` provides the repository, directory model and business-object linkage
> (`dms_field`), and `attachment_indexation` provides full-text indexing. Retention enforcement,
> legal hold, defensible disposal, evidence-pack assembly and the signature envelope model have
> no OCA equivalent and constitute the bulk of the custom build.

### 16.2 Custom Development

| CD ID | Component | Type | Effort |
|---|---|---|---|
| CD-C24-01 | `cd_document_core` — class taxonomy, auto-filing pipeline, metadata validation, exception queue, content-addressed storage, tiering, integrity sweeps | Odoo module + service | 6 PW |
| CD-C24-02 | `cd_records_retention` — schedule adoption from M60, retention computation, legal hold, disposal batches, certificates, violation detection | Odoo module + service | 5 PW |
| CD-C24-03 | `cd_esignature` — envelopes, tiered authentication, in-app and remote signing, sealing, completion certificates, verification, provider adapter | Odoo module + service | 4 PW |
| CD-C24-04 | `cd_evidence_pack` — pack composition, assembly by reference, completeness verification, sealing, controlled external release | Odoo module | 2 PW |
| CD-C24-05 | `cd_template_engine` — bilingual versioned templates, merge resolution, PDF/A rendering pipeline, watermarking and redaction | Odoo module + service | 2 PW |
| | | **Total** | **19 PW** |

### 16.3 Sequencing

> ⚠ **Wave inversion — unresolved.** M24 is scheduled in **W3** (P1) but declares a dependency on 1 module(s) that land later: **M60** (W6). One of three things must be true before the W3 gate, and the programme must say which:
>
> 1. the dependency is **not** a true prerequisite for the W3 scope, and §1 overstates it;
> 2. a defined **interim capability** covers the gap (name it, and the wave it retires in); or
> 3. the wave assignment of M24 or of the prerequisite is **wrong** and must change in `06-01`.
>
> Until this is resolved the W3 plan for M24 is not buildable as specified. *(Audit finding A3-07, 2026-08-13.)*

| Prerequisite | Reason |
|---|---|
| M29 Identity *(W1)* | Access control, external party scoping, encryption services |
| M28 Integration *(W1)* | Every module files through the gateway; events are the filing trigger |
| M30 Platform Admin *(W1)* | Entity, branch, language configuration |
| M33 Party Master *(W1)* | Signers and release recipients are parties |
| **M60 GRC retention schedule** | **Sequencing conflict — see below** |

> **Sequencing conflict, stated plainly.** M24 lands in **W3**; M60, which owns the retention
> policy, lands in **W6**. M24 cannot enforce a schedule that does not yet exist as versioned
> configuration.
>
> Two options, and the programme board must choose:
>
> 1. **Advance a W3 slice of M60** — approximately 3 PW covering retention-schedule publication
>    and the PDPA processing register *(already recommended in M60 §16.3)*. This is the
>    architecturally correct answer and keeps BRU-DMS-02 true from day one.
> 2. **Bootstrap the schedule in M24 for W3–W6**, seeded from `_CATEGORY_OVERVIEW.md` §7, with a
>    hard commitment to migrate ownership to M60 at W6.
>
> **Option 1 is recommended.** Option 2 creates a second retention authority, which is exactly
> what BRU-DMS-02 and BRU-GRC-14 exist to prevent, and experience says temporary authorities
> become permanent. If option 2 is chosen it must be recorded as a time-boxed exception with a
> W6 removal date, not as a design.

**Because every module from W3 onward files into M24, it must be accepted before M19, M20, M36
and M03 can be accepted.** It is the widest-blocking module in the programme after M28 and M29.

### 16.4 Data Migration

| Source | Volume | Target Entity | Wave |
|---|---|---|---|
| Branch paper job sheets and service records | 500,000+ historical *(profiling required)* | `fix.document` (archive class, OCR-indexed) | W3–W6 |
| Contract and agreement originals | ~3,000–5,000 | `fix.document` linked to M08 contracts | W4 |
| Financial records and Mushak documents | 7 years statutory | `fix.document` linked to M19/M20 | W3–W4 |
| Employee files | Per headcount, 10-year retention | `fix.document` (T5) | W5 |
| ISO records | 3 certification cycles | `fix.document` linked to M23 | W5 |
| Brand authorisation documents | 17+ | `fix.document` linked to M40 | W4 |
| Physical originals that must remain physical | To be profiled | `fix.physical.record` | W3–W6 |

**Migration rule.** Historical paper is digitised **by priority of need, not by chronology**:
open contracts, live warranty evidence and current statutory records first; the historical
archive progressively through Waves 3–6. Every digitised document is classified and given a
retention class on capture — bulk-loading unclassified scans would create exactly the
unmanageable corpus M24 exists to prevent. Where a paper original must legally be retained, the
digital copy is filed *and* the physical original registered; the two are never confused.

**The paper-elimination programme is a change-management project, not a scanning project.**
Reaching zero paper in active use by Wave 6 requires every process that currently ends in a
signature on paper to end in a signature in M24 instead. That work sits with the owning process
modules; M24 provides the capability.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | A document generated by a business transaction is filed, classified, linked and retention-assigned in the same transaction, with no human action | End-to-end test across ten generating modules |
| AC-02 | Auto-filing exceeds 96% of documents by volume, measured over a full month of production-equivalent load | Auto-filing rate report |
| AC-03 | Every document for a business object is retrieved in under 10 seconds end to end, at full corpus size | Performance test at projected 3-year volume |
| AC-04 | Bilingual search returns permission-scoped results in ≤ 3 s p95, and never reveals a document the user may not access | Load test + negative permission test |
| AC-05 | A held document cannot be disposed by any code path, including direct ORM and scheduled batch | Negative test via UI, API, ORM and disposal batch |
| AC-06 | Disposal is irreversible, removes content from every tier including backups within the declared window, and produces a certificate | Disposal test with post-disposal recovery attempt |
| AC-07 | The disposal register and metadata survive permanently after content removal | Post-disposal inspection |
| AC-08 | M24 has no independent retention configuration; the enforced schedule is exactly M60's published version | Schema inspection + joint test with M60 |
| AC-09 | Retention violations are detected in both directions and reported | Injected-violation test, both types |
| AC-10 | An evidence pack for a warranty claim assembles, verifies completeness and seals in under 5 minutes | Timed test with M09 |
| AC-11 | An incomplete evidence pack is returned explicitly marked incomplete with missing items named, never silently partial | Negative test with a missing artefact |
| AC-12 | A customer signs a quotation on a mobile browser over 3G, and the sealed document plus completion certificate are verifiable three years later | Field test + simulated-time verification test |
| AC-13 | An external release is scoped, watermarked, time-boxed, fully logged and auto-revoked at expiry | Security test with an external auditor account |
| AC-14 | Bengali OCR achieves ≥ 92% extraction success on a representative sample of photographed job sheets, and low-confidence extractions are flagged | OCR benchmark on 500 sampled documents |
| AC-15 | Named business super-users sign off UAT for all P0 and P1 requirements; zero critical or high security findings, with particular attention to T5 documents and tokenised signing surfaces | Signed UAT record + security review record |

**Definition of done:** all 17 criteria in `02-02` §8 plus the criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | Does the programme board choose option 1 (advance an M60 W3 slice) or option 2 (bootstrap retention in M24)? *(§16.3)* | CTO / CFO / Programme Board | **W2 — blocking** |
| Q-02 | What electronic signature form is legally sufficient in Bangladesh for each instrument class — a customer repair approval, an AMC contract, an employment contract, a seller agreement? *(cross-reference M36 Q-01)* | Legal / CFO | **W3 — blocking for §5.3** |
| Q-03 | Above what value or risk threshold is a provider-backed qualified signature required rather than OTP? | CFO / Legal | W3 build |
| Q-04 | Which document classes must retain a physical original in addition to the digital record, under Bangladeshi law and NBR practice? | Legal / CFO | **W3 — determines the physical register scope** |
| Q-05 | How far back is the historical paper archive digitised — 3 years, 5 years, or all? *(carried from M01 Q-04)* | Ops Director / CTO | W3 planning |
| Q-06 | Who staffs the Records Officer position, and is one sufficient for the exception queue at projected volume? | Quality Manager | W3 build |
| Q-07 | Where does the data-residency line fall for documents containing personal data, given the split-residency decision in `00-02` §2? | CTO / CFO | **W3 — architectural** |
| Q-08 | Does the disposal-removal window from backups meet PDPA 2026 expectations, and what window is defensible? | CTO / Legal | W3 build |
| Q-09 | Is an external qualified e-signature provider budgeted as an L6 component, and does it require CFO approval under principle 2? | CFO | W3 build |
| Q-10 | Who approves disposal per document class — the class owner, the Quality Manager, or both? | Quality Manager / CFO | W3 build |

---

## 19. References

**Internal**
`03_Modules/I_Governance_Risk_Quality_and_Knowledge/_CATEGORY_OVERVIEW.md` §4, §7, §8, §9, §10 ·
`M60_Governance_Risk_and_Compliance.md` §5.3 FR-GRC-032, §5.4 FR-GRC-039, §16.3 ·
`M23_Quality_Management_System.md` §3, §12 ·
`M61_Knowledge_Management_and_Technical_Library.md` §3 ·
`03_Modules/C_Commercial_Pricing_and_Revenue/M09_Warranty_Protection_Plans_and_Claims.md` §5.4, §6 T-08 ·
`03_Modules/C_Commercial_Pricing_and_Revenue/M36_Quotation_Estimation_and_Tender_Management.md` §5.4 ·
`03_Modules/C_Commercial_Pricing_and_Revenue/M08_Contract_Lifecycle_Management.md` §5.1 ·
`03_Modules/C_Commercial_Pricing_and_Revenue/M12_Marketplace_and_Seller_Ecosystem.md` §5.1 ·
`00_Governance_and_Charter/00-02_Executive_Summary_and_Scope_Charter.md` §2 (split residency), §7 principle 2 ·
`02_Architecture/02-02_Module_Catalogue_Master_Register.md` §2, §8 ·
`05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md` ·
`05-04_Role_Permission_and_Access_Matrix.md` §4 (tiers), §5, §8 EA-01, EA-02, EA-10 ·
`05-06_NonFunctional_Requirements_and_Standards.md` ·
`06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md`

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` §8.22 ·
`1000FiX_ERP_System_Comprehensive_URD.md` §15

**External benchmark**
ISO 15489 records management — authenticity, reliability, integrity, usability; metadata, classification, retention and disposition ·
ISO 9001:2015 clause 7.5 — control of documented information ·
EDRMS practice (Newgen, OpenText, LogicalDOC, SimplerQMS) — retention schedules, lifecycle control, legal hold, OCR capture, e-signature, ERP integration ·
SAP DMS / ArchiveLink — business-object linkage as the primary retrieval path ·
E-signature platform practice (DocuSign, Adobe Sign) — envelopes, sequencing, tiered authentication, tamper-evident sealing, completion certificates ·
Bangladesh Personal Data Protection Act 2026 — retention limitation and deletion procedures ·
Bangladesh statutory retention bases — Companies Act, NBR rules, Labour Act, ICT Act ·
Odoo 19 / OCA `dms` family, `attachment_indexation`, `document_page`

---

*Module M24 · Category I · 1000FiX ERP System v2.0 · CONFIDENTIAL*
