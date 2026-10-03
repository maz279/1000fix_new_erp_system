---
id: LG-019
title: E-Signature Legal Notice and Evidence Statement
project: 1000FiX ERP System v2.0
content_type: Legal / policy
template: TPL_Legal_Document.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Legal & Compliance with the CTO
author: Legal & Compliance with the CTO, Platform Engineering and Enterprise Architecture
reviewers: [Legal Counsel, CTO, Chief Data Officer, Quality Manager, CFO delegate, Enterprise Architect, Localisation Lead, external legal adviser]
approver: Legal Counsel with the CTO
content_class: A
purpose: >
  What constitutes valid electronic consent and a valid electronic signature in the company's
  systems, what evidence is retained for each assurance level, how non-repudiation is established,
  and how a signature is verified years later in a dispute. E-signature is used for estimates,
  contracts, seller agreements, handovers and portal acceptances; its evidentiary basis must be
  stated once, authoritatively, rather than assumed differently by each document that relies on it.
traces_to: [M24, M29, M60, M01, M02, M12, M40, P01, P02, P04, P05, P07, P09, P12, LG-001, LG-002, LG-003, LG-004, LG-005, LG-006, LG-007, LG-013, LG-015, LG-016, LG-020, LG-021, LG-024, DT-002, DT-005, DT-006, DT-009, DT-028, DT-030, UI-038, UI-042, BRU-DMS-03, BRU-DMS-07, BRU-DMS-09, BRU-DMS-10, BRU-DMS-11, BRU-SEC-01, BRU-SEC-02, BRU-SEC-11, BRU-CPM-08, FR-DMS-025, FR-DMS-026, FR-DMS-027, FR-DMS-028, FR-DMS-029, FR-DMS-030, FR-DMS-031, FR-DMS-032, FR-DMS-033, FR-DMS-041, NFR-023, NFR-095]
priority: P1
wave: W2
bilingual: yes
bn_counterpart: LG-019_ESignature_Legal_Notice_and_Evidence_Statement_BN.md
sources:
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M24 §5.3 FR-DMS-025 signature envelopes with named signers, roles, sequence and deadline; FR-DMS-026 tiered authentication — in-app authenticated, phone OTP, email link, wet-signature scan, provider-backed qualified signature, selected by document class; FR-DMS-027 in-person capture with identity verification, timestamp, GPS and device identity; FR-DMS-028 remote capture over 3G by portal, WhatsApp, SMS or email; FR-DMS-029 sealing with a content hash and tamper-evident protection; FR-DMS-030 completion certificate recording every signer, method, authentication evidence, timestamp and IP or device; FR-DMS-031 reminders, expiry and recorded declines; FR-DMS-032 external qualified provider above a declared value or risk threshold; FR-DMS-033 verification of integrity and signer evidence years later
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M24 §9 BRU-DMS-03 a signed document cannot be modified and a change requires a new version and a new signature; BRU-DMS-07 a released version is immutable; BRU-DMS-09 a generated document binds permanently to the template version used; BRU-DMS-10 the approver of a controlled document cannot be its author
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 §6.1 — ICT Act 2006 in force, verified 2026-08-12; §6.2 NFR-023 Bangladesh ICT Act 2006 and Cyber Security Ordinance 2025 compliance
    verified: 2026-08-12
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-007_Review_Approval_and_Signoff_Workflow.md §4.3 SO-06 — electronic approval is acceptable and preferred, and its evidentiary basis is stated once in LG-019, not per file
    verified: 2026-08-18
    class: P1
  - source: Information and Communication Technology Act 2006 — the legal recognition of electronic records and electronic signatures in Bangladesh. **Instrument-level citation; the section-level requirements for a valid electronic signature, and the status of any certifying-authority regime, are unverified and are pending G6**
    verified: 2026-08-18
    class: P2
  - source: Evidence Act 1872 as amended by the Evidence (Amendment) Act 2022, enacted November 2022 — introducing a definition of digital or electronic record covering data generated, prepared, sent, received or stored in magnetic, electro-magnetic, optical or computer memory including audio, video, CCTV and device records, and adding provisions on the admissibility of digital records subject to conditions, including that the computer was under the lawful control of the person producing it. **Secondary source; the section-level conditions are unverified and are pending G6**
    verified: 2026-08-18
    class: P2
supersedes: none
review_due: 2027-02-18
---

# LG-019 — E-Signature Legal Notice and Evidence Statement

| Item | Value |
|---|---|
| Document class | **Notice + evidence statement** — the basis on which every other electronic acceptance rests |
| Counterparty | **Every signing counterparty** — customer, corporate user, seller, supplier, partner, employee |
| Governing law | **Bangladesh** |
| Effective date | On publication of version 1.0 — *pending G6* |
| Acceptance capture method | **`AC-6` publication.** This document is not itself signed; **it is the reason the others can be** |
| Version accepted by users | n/a. **Every version is retained permanently**, because a signature is judged against the regime stated when it was given |
| External counsel review | **Required — G6.** Validity of an electronic signature and admissibility of a digital record are statutory questions |
| Bengali version | **Required.** A technician presents an estimate for signature on a phone screen, in Bengali, at a customer's door |

> ⚠ **Class A — statutory, and the single point of failure for the whole acceptance model.**
>
> `CG-007` `SO-06` says it outright: *"Electronic approval is acceptable and preferred. **Its
> evidentiary basis is stated once in `LG-019`, not per file.**"*
>
> **Every one of the twenty-three other `LG` files depends on this one.** `LG-001` §4.4 defines six
> acceptance mechanisms; four of them are electronic. `LG-002` binds 250,000+ customers a month by
> click-wrap. `LG-004` gates a seller's ability to transact on an e-signature. `LG-013` captures a
> warranty acceptance on a technician's phone.
>
> **If the evidentiary basis is wrong, none of them is provable.** That is why this file is `P1` at
> `W2` rather than a technical appendix.
>
> **Conformance note.** All ten template sections retained in order. Assurance levels are §4.3,
> evidence per level §4.4, verification §4.6, within §4 Terms. Gate questions and open items are §1.2
> and §1.3 (`CP-09`).

---

## 1. Approval Record

| Role | Name | Date | Evidence |
|---|---|---|---|
| Drafted by | Legal & Compliance with the CTO | 2026-08-18 | Draft issue v1.0 |
| G1 Editorial — Content Design | *pending* | | |
| G2 Factual — CTO with Enterprise Architecture | *pending* | | |
| **G3 Technical — Platform Engineering: the evidence in §4.4 is actually captured and retrievable** | *pending* | | **Required. A stated evidence set the platform does not capture is worse than none** |
| G4 Linguistic — independent reviewer, in context (`BN-018`) | *pending* | | |
| **G5 Legal — Legal Counsel** | *pending* | | **Required** |
| **G6 Statutory — external legal adviser** | *pending* | | **Required, blocking. `WV-02`: G6 can never be waived** |
| Approved by — Legal Counsel with the CTO | *pending* | | |

### 1.2 Questions for the external adviser and Legal Counsel (G6, G5)

| # | Question | Gate |
|---|---|---|
| **ES1** ‡ | **What makes an electronic signature legally valid in Bangladesh** under the ICT Act 2006, and is there a distinction between a simple electronic signature and one requiring a certifying authority? | G6 |
| **ES2** ‡ | **Is a certifying-authority-issued certificate required for any of the document classes in §4.5**, and if so which? | G6 |
| **ES3** ‡ | **What conditions must be met for a digital record to be admissible** under the Evidence Act 1872 as amended in 2022, and does the company's evidence set in §4.4 meet them? **The lawful-control condition is the one the company must be able to prove about its own systems** | G6 |
| **ES4** ‡ | **Is a click-wrap acceptance a valid contract formation** with a consumer, and does anything additional need to be shown or retained? | G6 + G5 |
| **ES5** ‡ | **Is a drawn signature captured on a technician's phone** sufficient for an estimate approval, a device handover, and a warranty acceptance? | G6 + G5 |
| **ES6** ‡ | **Are any of the company's instruments required to be in writing, wet-signed, notarised, witnessed or stamped?** The Stamp Act 1899 and the Registration Act are the candidates. **`LG-015` contracts and `LG-004` agreements are the exposure** | G6 |
| **ES7** | **What retention is required for signature evidence to remain useful**, given `FR-DMS-033` requires verification *years later*? | G5 + G6 |
| **ES8** | **Is an OTP to a phone number sufficient identity evidence**, and what happens where the number is later reassigned or the SIM is replaced? | G5 |
| **ES9** | **Where a signature is disputed, what does the company have to produce**, and is the §4.4 evidence set the right set? | G5 |
| **ES10** | **Is a signature captured while a person was offline, and synced later, valid as at the time of capture?** `P02`, `P09` and `P11` are offline-first by requirement | G5 + G6 |
| **ES11** | Does **withdrawal of a device from the signer's possession** — a technician holding the phone while the customer signs — weaken the evidence? | G5 |

### 1.3 Open items

| # | Open item | Blocking? | Owner |
|---|---|:--:|---|
| **O-01** | **`ES1`–`ES11` unanswered. Every `‡` position is provisional and `CG-012` `PR-04` blocks approval of a Class A file containing one** | **Yes — blocks `Approved`, and every `LG` file that relies on electronic acceptance** | Legal Counsel with CTO |
| **O-02** | **`ES6` is the one that could invalidate a whole document class.** If a contract, a seller agreement or a guarantee must be wet-signed, notarised or stamped, then `LG-004` `AC-2` and `LG-015`'s executed-contract model are wrong at the mechanism level, not the wording level | **Yes** | Legal Counsel |
| **O-03** | **`ES10` offline capture is a `P02` non-negotiable.** `04-00` requires full operation offline for 24 hours with no data loss, and a technician captures estimate approvals and handover signatures offline. **A signature whose timestamp is the sync time rather than the capture time is a different signature** | **Yes — blocks the `P02` estimate and handover path** | CTO with Legal |
| **O-04** | **No provider-backed qualified signature capability is selected.** `FR-DMS-032` provides for an external provider **above a declared value or risk threshold**; **the threshold is not declared and no provider is chosen** | **Yes — blocks §4.5 tier `AL-5`** | CTO with Legal |
| **O-05** | **G3 has not run.** §4.4 states an evidence set per assurance level. **Until Platform Engineering confirms each item is captured and retrievable, §4.4 is a specification of intent** | **Yes** | CTO |
| **O-06** | **`LG-001` §4.5's version-acceptance ledger has no owning module** (`LG-001` `O-06`). This file states what evidence must exist; **nothing indexes it by party and version** | **Yes** | CTO |
| **O-07** | **Long-term verification is unproven.** `FR-DMS-033` requires integrity and signer evidence to be verifiable years later. That depends on hash algorithm longevity, key custody and archive format, and **no crypto-agility position exists** | **Yes — the failure appears years later, which is why it must be decided now** | CTO with Security |
| **O-08** | **A wet-signature scan is an assurance level in `FR-DMS-026` and is the weakest form of evidence in the set.** §4.3 `AL-1` says so; **operations will reach for it because it is easy**, and nothing currently restricts when it may be used | Yes — blocks §4.5 allocation | Legal Counsel with Quality |

---

## 2. Scope and Parties

**In scope:** what the company treats as a valid electronic signature and a valid electronic
acceptance; the assurance levels available; the evidence retained at each; how a document is sealed;
how a signature is verified later; which document classes require which level; and the limits of what
electronic execution can achieve.

**Out of scope:**

| Subject | Owned by |
|---|---|
| **Which version a counterparty accepted, and when** | [`LG-001_Legal_Content_Register_and_Signoff_Log.md`](LG-001_Legal_Content_Register_and_Signoff_Log.md) §4.5 — **this file says what evidence must exist; `LG-001` indexes it** |
| The substance of any term being signed | The `LG` file that owns it |
| Retention of the evidence | [`LG-009_Data_Retention_and_Deletion_Schedule.md`](LG-009_Data_Retention_and_Deletion_Schedule.md) — `DC-23` and `RC-01` |
| Identity and authentication as controls | [`LG-021_ISMS_Policy_Set.md`](LG-021_ISMS_Policy_Set.md); `M29` |
| Personal data in signature evidence | `LG-008`, `LG-009`, `LG-012` |
| Employee attestation to internal policies | [`LG-020_Acceptable_Use_and_Internal_Access_Policy.md`](LG-020_Acceptable_Use_and_Internal_Access_Policy.md) — **which uses `AL-2`** |
| The envelope, sealing and verification implementation | `M24` §5.3 — **this file states the requirement** |

---

## 3. Definitions

| Term | Meaning |
|---|---|
| **Electronic signature** | Data logically associated with a document, executed by a person with intent to sign |
| **Electronic acceptance** | An affirmative act indicating agreement, where no signature mark is captured — a click-wrap tick |
| **Envelope** | The `M24` container of one or more documents, named signers, roles, sequence and deadline (`FR-DMS-025`) |
| **Assurance level** | The strength of identity and intent evidence — `AL-1`…`AL-5` (§4.3) |
| **Seal** | The tamper-evident protection applied at completion, with a **content hash** (`FR-DMS-029`) |
| **Completion certificate** | The record of every signer, method, authentication evidence, timestamp and IP or device (`FR-DMS-030`) |
| **Non-repudiation** | The state in which a signer cannot credibly deny having signed |
| **Verification** | Confirming the integrity of a signed document and its signer evidence, **years later** (`FR-DMS-033`) |
| **Decline** | A recorded refusal to sign, with reason (`FR-DMS-031`) |
| **‡** | A position resting on a secondary source, unverified, **pending G6** |

---

## 4. Terms

### 4.1 The statutory frame — stated, not asserted

| # | Position | Status |
|---|---|---|
| **4.1.1** | Bangladesh recognises electronic records and electronic signatures under the **ICT Act 2006**, which `05-06` §6.1 confirms is in force (verified 2026-08-12) and which `NFR-023` makes a `P0` compliance requirement | **In force. Section-level requirements unverified — `ES1`** |
| **4.1.2** | The **Evidence Act 1872, as amended in 2022**, defines a digital or electronic record broadly and provides for the admissibility of digital records subject to conditions ‡ | **`ES3` — the conditions are the operative part, and they are unverified** |
| **4.1.3** | Whether a **certifying authority** must issue a certificate for any class of signature is `ES2` | **Unverified** |
| **4.1.4** | Whether any instrument the company uses must be **in writing, wet-signed, notarised, witnessed or stamped** is `ES6` | **Unverified — `O-02`** |

> **`CL-01`. This section is the whole document's foundation and it is four unverified statements.**
> `CG-012` `EV-01` is explicit: **Class A statutory content requires a primary source, with no
> exception and no waiver.** Stating the frame honestly, with each element's verification status
> attached, is the only defensible position until G6 runs — and it is more useful than a confident
> paragraph, because **the four questions are now on someone's desk.**

### 4.2 The company's position

| # | Clause |
|---|---|
| **4.2.1** | The company executes documents and captures acceptances electronically, and **treats them as binding on the terms in this file** |
| **4.2.2** | **The signer's intent to sign is what makes a signature.** The mechanism evidences the intent; it does not create it |
| **4.2.3** | **Every signature is captured through `M24`.** No module implements its own signing (compare `BRU-SEC-09` for authentication) |
| **4.2.4** | **A signed document cannot be modified. A change requires a new version and a new signature** (`BRU-DMS-03`) |
| **4.2.5** | **A released version is immutable** (`BRU-DMS-07`), and **a generated document binds permanently to the template version used** (`BRU-DMS-09`) |
| **4.2.6** | **A decline is recorded with its reason** (`FR-DMS-031`). A document nobody signed is not a document that disappears |
| **4.2.7** | **The company does not rely on an electronic signature where `ES6` says it cannot** — and until `ES6` is answered, `LG-004` and `LG-015` execution carry that risk explicitly (`O-02`) |

### 4.3 Assurance levels

> **`FR-DMS-026` provides five methods. They are not equivalent, and §4.5 allocates them by document
> class rather than by convenience.**

| Level | Method | Identity evidence | Intent evidence | Strength |
|---|---|---|---|---|
| **`AL-1`** | **Wet-signature scan** — signed on paper, scanned and filed | **The paper, and whoever handed it over.** Nothing digital | The mark on the page | **Weakest in the digital set.** The scan proves a page existed, not who signed it or when — **`O-08`** |
| **`AL-2`** | **In-app authenticated** — the signer is already logged in through `M29` single sign-on | The authenticated session, MFA where the surface requires it (`BRU-SEC-01`) | An affirmative act in the session | **Strong for a known account holder.** Used for portal acceptance and employee attestation |
| **`AL-3`** | **Phone OTP** | A one-time code to a registered number | Entering the code and confirming | **Moderate.** Depends on the number remaining the signer's — **`ES8`** |
| **`AL-4`** | **In-person captured signature** — drawn on a technician, rider or counter device | Identity verification at the point of capture, **plus timestamp, GPS and device identity** (`FR-DMS-027`) | The drawn mark plus the context | **Strong, and the richest context in the set** — the company can show where and on what device |
| **`AL-5`** | **Provider-backed qualified signature** | An external qualified provider's own identity assurance (`FR-DMS-032`) | Per the provider | **Strongest — and not selected. `O-04`** |
| **`AL-0`** | **Email-link acceptance** — a link sent by email, clicked and confirmed | **Control of an email account only** | The click | **Weakest overall.** Listed because `FR-DMS-026` includes it; **§4.5 restricts it to low-consequence acceptances** |

| # | Rule |
|---|---|
| **AL-R1** | **The level is selected by document class (§4.5), not by what is convenient at the counter** |
| **AL-R2** | **A lower level is never substituted because a higher one failed.** Where `AL-4` cannot be captured, the work waits or a different route is used — it does not fall back to `AL-0` |
| **AL-R3** | **`AL-1` is used only where a wet signature is required or unavoidable**, and the reason is recorded — `O-08` |
| **AL-R4** | **Sensitive actions require step-up authentication** (`BRU-SEC-02`), so `AL-2` on a sensitive action means MFA re-verified at the point of signing |
| **AL-R5** | **The level used is recorded on the completion certificate**, so a dispute starts from the right question |

### 4.4 The evidence set — **specification pending G3 (`O-05`)**

> **`FR-DMS-030` requires a completion certificate recording every signer, method, authentication
> evidence, timestamp and IP or device. This is that certificate's content, per level.**

**Always captured, every level:**

| # | Evidence |
|---|---|
| 1 | The **document content hash** at the moment of signing (`FR-DMS-029`) |
| 2 | The **document version and template version** bound to it (`BRU-DMS-09`) |
| 3 | The **envelope reference**, the named signers, their roles and the sequence (`FR-DMS-025`) |
| 4 | The **assurance level used** (`AL-R5`) |
| 5 | The **timestamp**, stored UTC and presented Asia/Dhaka (`05-02` DM-08) |
| 6 | **The language version presented** — which text the signer actually saw (`LG-001` §4.5) |
| 7 | **The seal**, applied at completion, tamper-evident |
| 8 | The **immutable audit entry** of the signing event (`BRU-SEC-11`) |
| 9 | **Declines, reminders and expiry**, where they occurred (`FR-DMS-031`) |

**Additional, by level:**

| Level | Additional evidence |
|---|---|
| **`AL-0`** | The email address, the send and click timestamps, the link token, the originating IP |
| **`AL-1`** | The scan, who received the paper, when it was filed, and **where the paper original is registered** (`FR-DMS-013`) |
| **`AL-2`** | The authenticated session identifier, the authentication method, MFA result, IP, device fingerprint |
| **`AL-3`** | The number the OTP was sent to, send and verification timestamps, attempt count, IP |
| **`AL-4`** | The captured signature image, **the device identity, GPS coordinates and accuracy**, the technician's own authenticated identity, and the identity check performed on the signer |
| **`AL-5`** | The provider's own evidence package and certificate chain |

| # | Rule |
|---|---|
| **EV-R1** | **An evidence item that is stated here and not captured is a defect, not an aspiration.** G3 exists to catch that (`O-05`) |
| **EV-R2** | **The completion certificate is itself retained as a record** (`FR-DMS-030`) |
| **EV-R3** | **Evidence is retained at least as long as the signed document** (`LG-009` `DC-23`, `RC-01`), and **long enough for `FR-DMS-033` verification to remain possible** — `ES7` |
| **EV-R4** | **Personal data in the evidence set — IP, device, GPS, phone number — is processed under `LG-008` `P-19`** and is minimised to what evidences the signature |
| **EV-R5** | **GPS at `AL-4` is captured because it is signature context, not because the company tracks people.** `LG-020` covers workforce location disclosure |

### 4.5 Which level for which document — **pending `ES2`, `ES5`, `ES6`, `O-04`, `O-08`**

| Document class | Level | Rationale |
|---|---|---|
| **Portal terms acceptance** — `LG-002`, `LG-003`, `LG-011` cookie categories | **`AL-2`** | The signer is an authenticated account holder; the act is a tick recorded with a hash |
| **Estimate and revised-estimate approval** — `DT-005`, `DT-006` | **`AL-2` in the portal; `AL-4` on a technician device** | Money is committed. `UI-038` presents it |
| **Device intake and handover** — `DT-002`, `DT-009`, `DT-028` | **`AL-4`** | Custody transfer, in person, with location and device context |
| **Warranty acceptance** — `LG-013` at intake | **`AL-4` at a counter; `AL-2` in the portal** | The principal consumer liability limit |
| **Contract and AMC execution** — `DT-030`, `LG-015` | **`AL-5` where available, otherwise `AL-2` with `AL-1` fallback** | **`ES6` and `O-04`. The highest-value instruments and the weakest current capability** |
| **Marketplace seller agreement** — `LG-004` | **`AL-5` where available, otherwise `AL-3` plus `AL-2`** | `BRU-MKP-01` gates transacting on it; the signer is often a new counterparty with no account history |
| **Supplier and partner agreements** — `LG-006`, `LG-007` | **`AL-2` plus `AL-3`** | Business counterparties with verified onboarding |
| **Brand partner annex** — `LG-005` | **`AL-5` or the brand's own execution route** | International counterparty, likely their paper |
| **Employee policy attestation** — `LG-020`, `LG-021`, `LG-022`, `LG-023` | **`AL-2`** | Authenticated employee, `FR-GRC-030` tracks it |
| **Consent for a remote session** — `LG-016` `RC-T1` | **`AL-2` or `AL-3`**, logged per session | `BRU-RMS-01` |
| **Data-services case opening** — `LG-017` | **`AL-4`** at handover of media, with identity verification | The most sensitive engagement in the estate |
| **Payment authorisation** | **`AL-2` with step-up** (`BRU-SEC-02`) | Financial consequence (`EA-09`) |
| **Low-consequence acknowledgement** — a notice read, a survey started | **`AL-0`** | The only place `AL-0` is permitted |

### 4.6 Verification — years later

> **`FR-DMS-033`: verify the integrity and signer evidence of a previously signed document on demand,
> years later.** That is a harder requirement than it looks, and `O-07` records that it is unproven.

| # | Rule |
|---|---|
| **4.6.1** | Verification recomputes the content hash and compares it to the sealed hash. **A mismatch means the document was altered, and the document is not the one that was signed** |
| **4.6.2** | Verification produces the completion certificate, the audit entry and the evidence set for the level used |
| **4.6.3** | **An evidence pack for a dispute is assembled in under five minutes with a manifest and completeness check** (`FR-DMS-041`) |
| **4.6.4** | **Verification must survive an algorithm becoming obsolete.** A hash chosen today may be weak in ten years; **the archive format, hash agility and re-sealing policy are `O-07`** |
| **4.6.5** | **Verification must survive a provider change.** `AL-5` evidence held only in a provider's platform is evidence the company does not control — a selection criterion for `O-04` |
| **4.6.6** | Archive format is **PDF/A** with the evidence set attached (`DT-001`, `DT-031` §9) |
| **4.6.7** | **Re-rendering a signed document is prohibited** (`DT-031` §9). A reprint is watermarked COPY and logged (`FR-DMS-023`) |

### 4.7 Offline capture — **pending `ES10`, `O-03`**

| # | Clause |
|---|---|
| **4.7.1** | `P02`, `P09` and `P11` operate offline for 24 hours by requirement (`04-00` P02 non-negotiable 1, `PS-08`), and capture signatures while offline |
| **4.7.2** | **The signature timestamp is the moment of capture on the device, not the moment of sync.** The device's clock, its offset from server time, and the sync time are all recorded |
| **4.7.3** | **Every state-changing action is queued locally and idempotent on the server** (`04-00` P02 non-negotiable 6), so a signature is never duplicated or lost by a retry |
| **4.7.4** | **The document version presented offline is the version cached on the device**, and the cache version is recorded with the signature. **A signature against a stale cached version is a real risk and is recorded rather than hidden** |
| **4.7.5** | **`ES10` asks whether an offline-captured, later-synced signature is valid as at capture.** Until answered, the risk sits on the `P02` estimate and handover path (`O-03`) |

### 4.8 What electronic execution does not achieve

| # | Clause |
|---|---|
| **4.8.1** | **It does not make an unenforceable term enforceable.** A signature on a void clause signs nothing |
| **4.8.2** | **It does not establish that the signer read or understood the document.** `LG-001` `AC-1` says the same of click-wrap. **Comprehension is a content-design problem, addressed by `CG-011` reading level and by Bengali presentation, not by a signature** |
| **4.8.3** | **It does not establish authority.** A person signing for an organisation may lack authority — `LG-003` `CO1` |
| **4.8.4** | **It does not cure a defective notice.** Consent is invalid unless the notice version presented is recorded with it (`BRU-CPM-08`) |
| **4.8.5** | **It does not substitute for a formality the law requires** — `ES6` |
| **4.8.6** | **It does not make the company's records true.** `ES3`'s lawful-control condition means the company must be able to evidence the integrity of its own systems, which is `LG-021`'s job |

---

## 5. Liability, Exclusions and Limits

| # | Clause |
|---|---|
| **5.1** | This file creates no contractual limitation |
| **5.2** | **A signature the company cannot evidence is a term the company cannot rely on.** That is the whole exposure, and it is not transferable to a counterparty |
| **5.3** | **The company bears the risk of its own assurance-level choice.** Choosing `AL-0` for a high-value instrument is the company's decision and its consequence — which is why §4.5 allocates by class and `AL-R2` forbids downgrading |
| **5.4** | Where a signature is repudiated and the evidence set supports it, the company relies on §4.4 and §4.6. **Where the evidence set is incomplete, it does not** |
| **5.5** | A counterparty who signs is not thereby prevented from disputing the term's enforceability (§4.8.1) |
| **5.6** | Nothing limits liability that cannot lawfully be limited |

---

## 6. Data Protection

> Must reconcile with `LG-008`, `LG-009`, `LG-012`. Check **F6**.

| # | Clause |
|---|---|
| **6.1** | Signature evidence — identity, IP, device, GPS, phone number, signature image — is personal data, processed under `LG-008` `P-19` and the purpose of the document signed |
| **6.2** | **Evidence is minimised to what evidences the signature** (`EV-R4`). The company does not capture more because the device could |
| **6.3** | **GPS at `AL-4` is signature context.** Workforce location processing generally is disclosed under `LG-020`, and `LG-011` §4.7.3 states it for the work applications |
| **6.4** | Evidence is retained per `LG-009` — **with the signed document** (`DC-23`, `RC-01`), and long enough for §4.6 verification |
| **6.5** | **A signature image is biometric-adjacent** and is held with the same care as restricted data; **it is not used for identification elsewhere** |
| **6.6** | **Erasure of signature evidence is refused under `LG-009` §4.5** while the underlying obligation subsists, and the override and its basis are stated (`BRU-CPM-11`) |
| **6.7** | Where a signature envelope is delivered by WhatsApp, SMS or email (`FR-DMS-028`), that delivery is a transfer if the provider is abroad (`LG-012` `TR-03`) |

---

## 7. Termination and Consequences

| Event | Consequence |
|---|---|
| **An envelope expires unsigned** | Recorded, with reminders sent and the expiry logged (`FR-DMS-031`). **The document is not treated as accepted** |
| **A signer declines** | Recorded with the reason. The transaction does not proceed on an assumption |
| **A signed document must change** | **A new version and a new signature** (`BRU-DMS-03`). The old version stays, signed, as the record of what was agreed |
| **A signature is disputed** | §4.6 verification; §4.4 evidence produced; the assurance level used determines what can be shown |
| **A hash algorithm becomes obsolete** | **`O-07` — the re-sealing policy that would answer this does not exist** |
| **A provider relationship ends (`AL-5`)** | Evidence must already be held by the company (`4.6.5`), or it is lost with the provider |
| **This statement is superseded** | **Prior versions retained permanently** (`LG-009` `DC-23`). A signature given under version 1.0 is judged against version 1.0 |

---

## 8. Dispute Resolution

| Step | Route |
|---|---|
| **1 — Signature challenged** | Verification under §4.6, producing the completion certificate and evidence set |
| **2 — Internal escalation** | Legal Counsel with the CTO |
| **3 — Formal** | Per the instrument's own dispute clause. **The evidence set is what the company produces, and `ES9` asks whether it is the right set** |
| **4 — Courts** | The courts of Dhaka, Bangladesh. **Admissibility is `ES3`, and it is the question the whole file turns on** |

---

## 9. Change Control

| Version | Date | Change | Notice given to users | Re-acceptance required |
|---|---|---|---|:--:|
| 1.0 | 2026-08-18 | Initial issue — draft, blocked on G6 and G3. Six assurance levels and the evidence set per level established | n/a | n/a |

| # | Rule |
|---|---|
| **9.1** | A change to an assurance level, an evidence item or a §4.5 allocation is **MAJOR** |
| **9.2** | **A change does not retrospectively weaken a signature already given.** A signature is judged against the version in force when it was given |
| **9.3** | **A statutory change re-opens G2, G5 and G6 here, and re-opens G5 on every `LG` file relying on electronic acceptance** — which is all of them (`CG-007` §7) |
| **9.4** | **A `ES6` answer requiring a formality is MAJOR and changes the acceptance mechanism in `LG-001` §4.4**, not just this file |
| **9.5** | Every version retained permanently (`LG-009` `DC-23`) |
| **9.6** | **12 months without a trigger re-opens G6** (`CG-006` §4.2) |

---

## 10. Cross-References

| Document | Relationship | Must not contradict |
|---|---|---|
| [`LG-001_Legal_Content_Register_and_Signoff_Log.md`](LG-001_Legal_Content_Register_and_Signoff_Log.md) | **`SO-06`: the basis is stated here once. `AC-1`, `AC-2`, `AC-3`, `AC-5` all rest on this file** | The acceptance mechanisms and the ledger fields |
| [`LG-004_Marketplace_Seller_Agreement_and_Policy_Handbook.md`](LG-004_Marketplace_Seller_Agreement_and_Policy_Handbook.md) · [`LG-015_AMC_SLA_Master_Terms_and_Service_Credit_Rules.md`](LG-015_AMC_SLA_Master_Terms_and_Service_Credit_Rules.md) | **The two highest-value electronic executions — `ES6`, `O-02`, `O-04`** | The execution mechanism |
| [`LG-002_Portal_Terms_of_Use_Customer.md`](LG-002_Portal_Terms_of_Use_Customer.md) · [`LG-003_Portal_Terms_of_Use_Corporate.md`](LG-003_Portal_Terms_of_Use_Corporate.md) | Click-wrap at `AL-2` — `ES4` | Acceptance validity |
| [`LG-013_Service_Terms_Warranty_Terms_and_Exclusions.md`](LG-013_Service_Terms_Warranty_Terms_and_Exclusions.md) | `AL-4` at intake; `AL-3` fallback | The presentation and capture at a counter |
| [`LG-016_Managed_Services_and_Remote_Access_Consent_Terms.md`](LG-016_Managed_Services_and_Remote_Access_Consent_Terms.md) | Per-session consent evidence | `RC-R7` version recording |
| [`LG-020_Acceptable_Use_and_Internal_Access_Policy.md`](LG-020_Acceptable_Use_and_Internal_Access_Policy.md) · [`LG-021_ISMS_Policy_Set.md`](LG-021_ISMS_Policy_Set.md) | `AL-2` attestation; §4.8.6 lawful-control evidence | Attestation tracking; system integrity |
| [`LG-009_Data_Retention_and_Deletion_Schedule.md`](LG-009_Data_Retention_and_Deletion_Schedule.md) | `EV-R3`, `DC-23`, `RC-01` | Evidence retention |
| [`LG-012_Cross_Border_Data_Transfer_and_Residency_Statement.md`](LG-012_Cross_Border_Data_Transfer_and_Residency_Statement.md) | §6.7 envelope delivery abroad | `TR-03` |
| [`../05_Document_and_Print_Templates/05A_Service_and_Operations/DT-005_Repair_Estimate_and_Quotation.md`](../05_Document_and_Print_Templates/05A_Service_and_Operations/DT-005_Repair_Estimate_and_Quotation.md) · [`../05_Document_and_Print_Templates/05A_Service_and_Operations/DT-002_Service_Intake_Receipt_and_Device_Handover_Form.md`](../05_Document_and_Print_Templates/05A_Service_and_Operations/DT-002_Service_Intake_Receipt_and_Device_Handover_Form.md) | `AL-4` capture points | What is signed and when |
| [`../03_UI_Copy_and_Microcopy/03D_Critical_Flows/UI-038_Estimate_and_Approval_Flow_Copy.md`](../03_UI_Copy_and_Microcopy/03D_Critical_Flows/UI-038_Estimate_and_Approval_Flow_Copy.md) | The signing moment's copy | What the signer is told before signing |
| [`../00_Content_Governance_and_Standards/CG-007_Review_Approval_and_Signoff_Workflow.md`](../00_Content_Governance_and_Standards/CG-007_Review_Approval_and_Signoff_Workflow.md) | **`SO-06` names this file as the single source** | Electronic approval of content itself |
| `TS-017` Security and Privacy Test Case Pack · `AP-*` integration content | Where §4.4 capture and §4.6 verification are tested | The evidence set actually captured |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Legal_Document.md` — ten sections in order; additions declared
- [x] **The statutory frame stated with each element's verification status attached** (`CL-01`), rather than asserted
- [x] **Six assurance levels defined with identity and intent evidence and a strength assessment**, including the two weakest named as weakest
- [x] **Evidence set specified per level**, with nine items captured at every level
- [x] **Document-class allocation table** so the level is chosen by consequence, not convenience (`AL-R1`, `AL-R2`)
- [x] **Long-term verification requirement stated with its unsolved parts named** (§4.6, `O-07`)
- [x] **Offline capture addressed as a `P02` non-negotiable, with the stale-cache risk recorded** (§4.7)
- [x] **§4.8 states what electronic execution does not achieve** — the six things people assume it does
- [x] All internal links resolve
- [ ] **G6 external verification of `ES1`–`ES3` and `ES6`** — outstanding. **`WV-02`: cannot be waived. Every `LG` file's acceptance model depends on it**
- [ ] **G3: the §4.4 evidence set confirmed captured and retrievable** — outstanding, `O-05`
- [ ] **`ES1`–`ES11` answered; every `‡` position verified** — outstanding; `PR-04` blocks approval
- [ ] **Formality question `ES6` answered** — outstanding, `O-02`; may invalidate a whole execution route
- [ ] **Offline signature validity confirmed** — outstanding, `O-03`
- [ ] **`AL-5` provider selected and the value threshold declared** — outstanding, `O-04`
- [ ] **Long-term verification and re-sealing policy established** — outstanding, `O-07`
- [ ] **Bengali counterpart authored and signed off in context** — outstanding
- [ ] Named approver recorded — pending
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
