---
id: LG-017
title: Data Recovery and Secure Destruction Terms
project: 1000FiX ERP System v2.0
content_type: Legal / policy
template: TPL_Legal_Document.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Legal & Compliance with Technical Services
author: Legal & Compliance with Technical Services, the Chief Data Officer and Quality
reviewers: [Legal Counsel, Chief Data Officer, Technical Services Head, Quality Manager, CTO delegate, Localisation Lead, Accessibility reviewer]
approver: Legal Counsel with Technical Services Head
content_class: B
purpose: >
  The terms for data recovery and secure destruction — success-dependent fees, what happens when
  nothing is recovered, confidentiality over data the company necessarily reads, the handling of
  unlawful content it may discover, the destruction standard applied, and the certificate that
  evidences it. This is the only service in which the company deliberately looks inside a customer's
  data, so the confidentiality and unlawful-content positions have to be explicit rather than implied.
traces_to: [M06, M18, M14, M24, M29, M60, P01, P04, LG-001, LG-002, LG-008, LG-009, LG-012, LG-013, LG-014, LG-016, LG-018, LG-021, DT-034, DT-035, SP-012, SP-026, UI-042, HC-003, BRU-DTS-01, BRU-DTS-02, BRU-DTS-03, BRU-DTS-04, BRU-DTS-05, BRU-DTS-06, BRU-DTS-07, BRU-DTS-08, BRU-DTS-09, BRU-DTS-10, BRU-DTS-11, BRU-DTS-12, BRU-DTS-13, BRU-DTS-14, BRU-DTS-15, BRU-DTS-16, BRU-DTS-17, BRU-DTS-18, BRU-ESG-01, BRU-SEC-03, BRU-SEC-04, BRU-SEC-23, NFR-086, NFR-094]
priority: P1
wave: W2
bilingual: yes
bn_counterpart: LG-017_Data_Recovery_and_Secure_Destruction_Terms_BN.md
sources:
  - source: 1000fix_ERP_Module/03_Modules/A_Service_Delivery_and_Operations/M06 §9 BRU-DTS-01 two distinct authenticated signatures for media entering or leaving the secure area; BRU-DTS-02 named case-assigned MFA-authenticated access only; BRU-DTS-03 every access logged immutably and retained five years; BRU-DTS-04 work performed on an image never the original where technically possible; BRU-DTS-05 recovered data encrypted with a case-specific key; BRU-DTS-06 automatic purge at the agreed date unless a documented approved time-limited hold applies; BRU-DTS-07 recovered data may not leave the controlled environment except through the approved handover path
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/A_Service_Delivery_and_Operations/M06 §9 BRU-DTS-08 — the sanitisation technique is selected by data confidentiality, media type and final disposition under the Company's documented sanitisation programme, applying IEEE 2883 as the approved technique standard per NIST SP 800-88r2
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/A_Service_Delivery_and_Operations/M06 §9 BRU-DTS-09 no device proceeds to refurbishment, resale or recycling without a valid certificate of destruction; BRU-DTS-10 where erasure cannot be verified physical destruction is mandatory; BRU-DTS-11 every certificate binds to a specific media serial number and blanket certificates are not permitted; BRU-DTS-12 staff confidentiality undertakings recorded per case before access; BRU-DTS-13 case details communicated only by authorised roles and only to the verified customer contact; BRU-DTS-14 recovered customer data is never used as training data for any model; BRU-DTS-15 a partner laboratory referral requires a signed confidentiality agreement and continuous custody documentation
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/A_Service_Delivery_and_Operations/M06 §9 BRU-DTS-16 recovered customer data and its index are held in a Bangladesh-resident store and may not be replicated to a foreign region; BRU-DTS-17 a breach affecting customer data held under a data case is assessed and notified to the National Data Management Authority where the threshold is met; BRU-DTS-18 case records retained a minimum of five years as processing records independently of the purge of the data itself
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04 §7 approval authority matrix — data destruction requires a Data Services Technician plus a witness; §4 T5 restricted tier covers data-recovery case content; §5 recovered_data_index visible to R14 case-assigned only, R02 with approval
    verified: 2026-08-18
    class: P1
  - source: Cyber Security Ordinance 2025 and the Penal Code 1860 — the position where unlawful content is discovered on media in the Company's possession, and the obligations that may arise. **Instrument-level citation from secondary sources; clause-level content unverified and pending G5. §4.8 deliberately states no reporting obligation as fact**
    verified: 2026-08-18
    class: P2
supersedes: none
review_due: 2027-02-18
---

# LG-017 — Data Recovery and Secure Destruction Terms

| Item | Value |
|---|---|
| Document class | **Terms** — service terms for two related services |
| Counterparty | An individual or organisation whose media the Company receives for recovery or destruction |
| Governing law | **Bangladesh** |
| Effective date | On publication of version 1.0 — *pending approval* |
| Acceptance capture method | **`AC-3` signature at case opening**, with **`AC-5` specific consent for access to the data**. Destruction is evidenced on `DT-034` |
| Version accepted by users | Recorded in `LG-001` per case |
| External counsel review | **Required** — the §4.8 unlawful-content position and the §5.3 no-recovery fee |
| Bengali version | **Required.** A customer hands over media containing their whole life at a counter, in Bengali |

> ⚠ **Class B, and the only service in the register where the Company deliberately reads a customer's
> data as the work itself.**
>
> Every other document limits what the Company may see. Here the Company must see, to do the job.
> That inverts the usual drafting problem: **the protections cannot be "we will not look", they have
> to be about who may look, under what control, for how long, and what happens to what they find.**
>
> `M06` supplies eighteen hard rules for exactly this, and **§4.8 — unlawful content — is the one
> question none of them answers.**
>
> **Conformance note.** All ten template sections retained in order. Recovery terms are §4.3–§4.5,
> destruction terms §4.6, unlawful content §4.8, within §4 Terms. Gate questions and open items are
> §1.2 and §1.3 (`CP-09`).

---

## 1. Approval Record

| Role | Name | Date | Evidence |
|---|---|---|---|
| Drafted by | Legal & Compliance with Technical Services | 2026-08-18 | Draft issue v1.0 |
| G1 Editorial — Content Design | *pending* | | |
| G2 Factual — Technical Services Head with Quality Manager | *pending* | | |
| G4 Linguistic — independent reviewer, in context (`BN-018`) | *pending* | | |
| **G5 Legal — Legal Counsel** | *pending* | | **Required** |
| Approved by — Legal Counsel with Technical Services Head | *pending* | | |

### 1.2 Questions for Legal Counsel (G5)

| # | Question | Why it matters |
|---|---|---|
| **DS1** | **What must the Company do if it discovers apparently unlawful content on media in its possession** — child sexual abuse material, terrorist material, or evidence of a serious offence? Is there a **reporting obligation**, to whom, and does reporting breach the confidentiality it owes the customer? | **§4.8. This is the single most serious question in Category 10, and it will arise. A technician will find something.** |
| **DS2** | If content must or may be reported, **may the Company continue the engagement, and must it tell the customer** it has reported? | Telling could amount to tipping off; not telling breaches the customer relationship |
| **DS3** | Is a **no-recovery, no-fee** model with a non-refundable diagnostic charge lawful and enforceable, and must the charge be disclosed in a particular way? | §4.4 and §5.3 |
| **DS4** | Is the **§5.4 exclusion of liability for data that cannot be recovered** enforceable, given the customer's data is already lost when they arrive? | The customer's loss pre-dates the engagement, but the Company can make it worse |
| **DS5** | May the Company **destroy media** the customer abandons, and after what notice? | §4.9, and the same question as `LG-013` `WT5` |
| **DS6** | Is **`IEEE 2883` applied per `NIST SP 800-88r2`** an adequate destruction standard to state to a corporate client and a regulator? | `BRU-DTS-08` names it; §4.6 states it |
| **DS7** | What must a **destruction certificate** contain to be relied on by a corporate client for its own compliance? | `DT-034`; `BRU-DTS-11` prohibits blanket certificates |
| **DS8** | Where recovery **succeeds partially**, how is the fee assessed, and is "partial success" a defensible fee trigger? | §4.4.4 |
| **DS9** | May the Company require the customer to **warrant that they own the data or are entitled to access it**, and does that warranty protect the Company? | §4.2.3 |
| **DS10** | Is the **`BRU-DTS-06` "agreed date"** purge model sufficient, and must a **maximum** be imposed regardless of agreement? | `LG-009` `O-06` raises the same point from the retention side |

### 1.3 Open items

| # | Open item | Blocking? | Owner |
|---|---|:--:|---|
| **O-01** | `DS1`–`DS10` unanswered | **Yes — blocks `Approved`** | Legal Counsel |
| **O-02** | **`DS1` cannot wait for the file's approval.** The service exists at `W2`; a technician will encounter content before the terms are approved. **An interim instruction is needed now**, separate from this document's approval | **Yes — an operational instruction, immediately** | Legal Counsel with Technical Services Head |
| **O-03** | **No maximum purge period exists.** `BRU-DTS-06` purges "at the agreed date"; an indefinite agreed date defeats storage limitation. Raised as `LG-009` `O-06` and `DS10` | **Yes — blocks §4.5.4** | CDO |
| **O-04** | **Fees are not published.** §4.4 states the model; `MD-029` holds rate cards and no data-services rate is registered | **Yes — blocks §4.4** | CCO with Finance |
| **O-05** | **`BRU-DTS-08` names `IEEE 2883` and `NIST SP 800-88r2` and there is no documented sanitisation programme.** The rule refers to *"the Company's documented sanitisation programme"* — which does not exist | **Yes — blocks §4.6** | Technical Services Head with Quality |
| **O-06** | **The abandoned-media position in §4.9 is the same question as `LG-013` `WT5`** (uncollected devices) and must be answered once for both | Yes | Legal Counsel |
| **O-07** | **`LG-018` is `W5` and this file is `W2`.** §4.7 routes destroyed media into the e-waste chain whose environmental position `LG-018` sets three waves later — **the same sequencing defect as `LG-006` `O-02`** | **Yes — sequencing** | Programme Content Lead |
| **O-08** | **A partner laboratory referral requires a signed confidentiality agreement** (`BRU-DTS-15`). **No such agreement template exists**, and it is not registered as a `DT` document | Yes — blocks §4.10 | Legal Counsel |

---

## 2. Scope and Parties

| Party | Identity |
|---|---|
| **The Company** | 1000FiX Services Limited |
| **The Customer** | The person or organisation delivering media for recovery or destruction |

**Two services, one document:**

| Service | What it is |
|---|---|
| **Data recovery** | Attempting to retrieve data from failed, damaged or corrupted media |
| **Secure destruction** | Irreversibly rendering data on media unrecoverable, and evidencing it |

**Out of scope:**

| Subject | Owned by |
|---|---|
| **Data loss occurring during an ordinary repair** | [`LG-013_Service_Terms_Warranty_Terms_and_Exclusions.md`](LG-013_Service_Terms_Warranty_Terms_and_Exclusions.md) §4.7 — **and §4.7.5 there prohibits charging for recovery of data the Company lost** |
| Remote access to a live system | [`LG-016_Managed_Services_and_Remote_Access_Consent_Terms.md`](LG-016_Managed_Services_and_Remote_Access_Consent_Terms.md) |
| **What happens to the media afterwards, environmentally** | [`LG-018_EWaste_EPR_and_Environmental_Compliance_Statements.md`](LG-018_EWaste_EPR_and_Environmental_Compliance_Statements.md) — **`O-07`** |
| Retention of case records and recovered data | [`LG-009_Data_Retention_and_Deletion_Schedule.md`](LG-009_Data_Retention_and_Deletion_Schedule.md) `RC-09` |
| Residency of recovered data | [`LG-012_Cross_Border_Data_Transfer_and_Residency_Statement.md`](LG-012_Cross_Border_Data_Transfer_and_Residency_Statement.md) §4.3 |
| Refunds and compensation | [`LG-014_Refund_Cancellation_and_Compensation_Policy.md`](LG-014_Refund_Cancellation_and_Compensation_Policy.md) |
| The operating procedure | [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-012_SOP_Data_Recovery_and_Secure_Data_Handling.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-012_SOP_Data_Recovery_and_Secure_Data_Handling.md) |

---

## 3. Definitions

| Term | Meaning |
|---|---|
| **Media** | The physical device or storage the Customer delivers |
| **Case** | The engagement, with a case reference and a named assigned team |
| **Secure area** | The controlled physical environment where media and case work are held. **Media entering or leaving requires two distinct authenticated signatures** (`BRU-DTS-01`) |
| **Image** | A forensic copy. **Work is performed on an image, never on the original, wherever technically possible** (`BRU-DTS-04`) |
| **Recovered data** | Data retrieved from the media, **encrypted with a case-specific key** (`BRU-DTS-05`) |
| **Handover** | The approved path by which recovered data reaches the Customer. **Recovered data may not leave the controlled environment any other way** (`BRU-DTS-07`) |
| **Purge** | Automatic deletion of recovered data at the agreed date (`BRU-DTS-06`) |
| **Sanitisation** | Rendering data unrecoverable, by technique selected under §4.6 |
| **Certificate of destruction** | The evidence that specific media was sanitised — `DT-034`. **Bound to a specific serial number; blanket certificates are not permitted** (`BRU-DTS-11`) |
| **Governing text** | The **English** version (`LG-001` `LR-03`) |

---

## 4. Terms

### 4.1 What the Customer is told before the case opens

| # | Clause |
|---|---|
| **4.1.1** | **The Company will necessarily be able to see the contents of the Customer's data.** That is stated plainly, before the media is handed over, and it is not softened |
| **4.1.2** | Who may see it — **only named, case-assigned, authenticated staff** (`BRU-DTS-02`) |
| **4.1.3** | **Recovery may fail.** Some media cannot be recovered, and the attempt itself carries a risk to the media |
| **4.1.4** | The fee model, including any non-refundable diagnostic charge (§4.4) |
| **4.1.5** | **When the recovered data will be purged** (§4.5.4) |
| **4.1.6** | **That the data is held in Bangladesh and is never replicated abroad** (`BRU-DTS-16`) |
| **4.1.7** | **That it is never used to train a model** (`BRU-DTS-14`) |
| **4.1.8** | **That unlawful content, if found, may have consequences the Company cannot control** — the honest form of §4.8 pending `DS1` |

### 4.2 The Customer's obligations and warranties

| # | Clause |
|---|---|
| **4.2.1** | The Customer identifies themselves and, for a business, the person authorised to instruct |
| **4.2.2** | The Customer describes the media, the failure and what they are trying to recover |
| **4.2.3** | **The Customer warrants that they own the media and the data, or are otherwise entitled to access it**, and indemnifies the Company for a breach of that warranty — subject to `DS9` |
| **4.2.4** | The Customer nominates the verified contact to whom case details may be given. **Case details are communicated only by authorised roles and only to that contact** (`BRU-DTS-13`) |
| **4.2.5** | The Customer tells the Company where the media is known to contain another person's data, so §4.3 controls can be set accordingly |
| **4.2.6** | The Customer does not deliver media they know to contain unlawful content |

### 4.3 Controls over the case

> **These are `M06`'s eighteen hard rules restated as contractual undertakings.** The customer is
> entitled to know them, and the Company is entitled to be held to them.

| # | Control | Rule |
|---|---|---|
| **4.3.1** | **Two distinct authenticated signatures** for media entering or leaving the secure area | `BRU-DTS-01` |
| **4.3.2** | **Access limited to named, case-assigned, MFA-authenticated staff** | `BRU-DTS-02`, `BRU-SEC-03` |
| **4.3.3** | **Every access logged immutably and retained five years** | `BRU-DTS-03`, `BRU-SEC-11` |
| **4.3.4** | **Work on an image, never the original, wherever technically possible** | `BRU-DTS-04` |
| **4.3.5** | **Recovered data encrypted at rest with a case-specific key** | `BRU-DTS-05` |
| **4.3.6** | **Recovered data leaves the controlled environment only by the approved handover path** | `BRU-DTS-07` |
| **4.3.7** | **A confidentiality undertaking is recorded per case, per person, before access is granted** | `BRU-DTS-12` |
| **4.3.8** | **Case details go only to the verified contact, and only from an authorised role** | `BRU-DTS-13` |
| **4.3.9** | **Recovered data is never used as training data for any model** | `BRU-DTS-14` |
| **4.3.10** | **Recovered data and its index are held in Bangladesh and never replicated to a foreign region** | `BRU-DTS-16`, `NFR-086` |
| **4.3.11** | **Case content is restricted-tier data** — allow-list access, step-up authentication, dual control on the index | `05-04` §4 `T5`, §5 |
| **4.3.12** | **A breach affecting case data is assessed and notified to the National Data Management Authority where the threshold is met** | `BRU-DTS-17`, `NFR-094` |
| **4.3.13** | **Case records are retained a minimum of five years as processing records, independently of the purge of the data itself** | `BRU-DTS-18` |

> **`CL-01`. §4.3.13 is the distinction customers misunderstand most.** The **data** is purged at the
> agreed date. The **case record** — that a case existed, for whom, what was attempted, who accessed
> it — is retained for five years as a processing record. **Purging the data does not erase the fact
> of the case, and the customer is told so** (`LG-009` `RC-09`).

### 4.4 Fees — **pending `DS3`, `DS8`, `O-04`**

| # | Clause |
|---|---|
| **4.4.1** | **A diagnostic assessment establishes whether recovery is feasible and at what cost.** Its charge, if any, is stated before it begins and is **non-refundable only if disclosed as such** |
| **4.4.2** | **The recovery fee is quoted after diagnosis, and the Customer approves it before recovery begins** |
| **4.4.3** | **Where nothing is recovered, no recovery fee is charged** (§5.3). The diagnostic charge stands if it was disclosed |
| **4.4.4** | **Where recovery is partial, the fee is assessed against what was recovered relative to what was quoted**, and the basis is stated in the quotation — subject to `DS8` |
| **4.4.5** | **The Customer is not charged for recovery of data the Company itself lost during a repair** (`LG-013` §4.7.5) |
| **4.4.6** | A media replacement or transfer medium is charged separately and disclosed |
| **4.4.7** | **Fees are published in the portal — `O-04`: they are not** |

### 4.5 Handover and purge

| # | Clause |
|---|---|
| **4.5.1** | Recovered data is handed over on encrypted media, or by another approved path, **to the verified contact only** (`BRU-DTS-07`, `BRU-DTS-13`) |
| **4.5.2** | The Customer confirms receipt and confirms that the recovered data is readable **before the purge clock starts** |
| **4.5.3** | **The Company keeps a copy for a stated grace period**, so a failed handover can be repeated |
| **4.5.4** | **At the agreed date, recovered data is purged automatically** unless a documented, approved and time-limited hold applies (`BRU-DTS-06`, `BRU-SEC-04`). **The purge is by destruction of the case key** (`LG-009` `DM-3`) |
| **4.5.5** | **`O-03`: no maximum agreed date exists.** Until one is set, a hold cannot be indefinite and the Company will not agree to one |
| **4.5.6** | **The purge is evidenced**, and the Customer may request the evidence |
| **4.5.7** | **A legal hold overrides the purge** (`BRU-SEC-23`, `BRU-DMS-02`), and the Customer is told that a hold exists unless telling them is unlawful |

### 4.6 The destruction standard — **pending `DS6`, `O-05`**

| # | Clause |
|---|---|
| **4.6.1** | **The sanitisation technique is selected by data confidentiality, media type and final disposition, under the Company's documented sanitisation programme, applying `IEEE 2883` as the approved technique standard per `NIST SP 800-88r2`** (`BRU-DTS-08`) |
| **4.6.2** | **`O-05`: the documented sanitisation programme the rule refers to does not exist.** It must, because the technique selection is what makes §4.6.1 more than a citation |
| **4.6.3** | **Where erasure cannot be verified, physical destruction is mandatory** (`BRU-DTS-10`, `LG-009` `DM-R4`) |
| **4.6.4** | **Every certificate binds to a specific media serial number. Blanket certificates are not permitted** (`BRU-DTS-11`) |
| **4.6.5** | **Destruction requires the Data Services Technician and a witness** (`05-04` §7) |
| **4.6.6** | The certificate is `DT-034` and states what was destroyed, by what technique, when, by whom and witnessed by whom — subject to `DS7` |
| **4.6.7** | **A certificate is retained for the period in `LG-009` `DC-13`.** A destruction certificate that no longer exists cannot prove the destruction |
| **4.6.8** | The Company does not certify destruction it did not perform |

### 4.7 The gate into refurbishment, resale and recycling

| # | Clause |
|---|---|
| **4.7.1** | **No device proceeds to refurbishment, resale or recycling without a valid certificate of destruction** (`BRU-DTS-09`, `BRU-ESG-01`). **This is a hard system gate, not a checklist item** |
| **4.7.2** | The gate applies equally to a **donated** device (`BRU-ESG-15`) and to a device disposed of under `LG-013` §4.9 |
| **4.7.3** | A recycling partner **must not accept media arriving without the record, and must report it** (`LG-006` §4.7.7) |
| **4.7.4** | What happens to the media after destruction, and the environmental claims the Company may make about it, are `LG-018` — **`O-07`: three waves later** |

### 4.8 Unlawful content — **the honest position, pending `DS1`**

> **`CL-02`. This section is deliberately not drafted as an answer.**
>
> A data-recovery technician will, at some point, encounter material that is a serious criminal
> offence to possess. When that happens the Company will be holding it, will know it is holding it,
> and will have a customer relationship, a confidentiality undertaking and possibly a legal duty all
> pointing in different directions.
>
> **`CG-013` `T-A02` and `T-A17` both fire here, and `CG-012` `PR-01` requires the gap to be visible
> rather than filled with a plausible-sounding clause.**

| # | Clause |
|---|---|
| **4.8.1** | **The Company does not search for unlawful content.** It looks only at what the recovery work requires |
| **4.8.2** | **Where a member of staff believes they have encountered apparently unlawful content, they stop work, touch nothing further, and escalate immediately** to the Technical Services Head and Legal Counsel. **They do not investigate, do not copy, do not show a colleague, and do not tell the customer** |
| **4.8.3** | **The case is frozen.** Access is restricted to the escalation route; the immutable access log continues (`BRU-DTS-03`) |
| **4.8.4** | **Legal Counsel determines the response.** Whether a report must or may be made, to whom, whether the engagement may continue, and whether the customer may be told, **are questions this document does not answer** — `DS1`, `DS2` |
| **4.8.5** | **The Company may suspend or terminate the engagement**, and may decline to return recovered data, where continuing would be unlawful |
| **4.8.6** | The Customer's confidentiality is preserved **so far as the law permits, and no further.** §4.11 says so explicitly rather than promising confidentiality the Company may not be able to keep |
| **4.8.7** | **`O-02`: an interim operational instruction is required now, before `DS1` is answered**, because the service is live at `W2` and the situation does not wait for a document to be approved |

### 4.9 Abandoned media — **pending `DS5`, `O-06`**

Where a Customer does not collect media or recovered data, the Company notifies them on the schedule
in `NT-020`, may apply a storage charge if published, and **after a longer stated period and after
notice may destroy the media** — passing the §4.6 standard and issuing a certificate. **The periods
and the notice requirements are `DS5`, and are the same question as `LG-013` `WT5`.** The Company
does not destroy media that is the subject of an open complaint, dispute or hold.

### 4.10 Partner laboratories

| # | Clause |
|---|---|
| **4.10.1** | Some recoveries require a specialist laboratory. **The Customer is told before a referral is made and may decline it** |
| **4.10.2** | **A referral requires a signed confidentiality agreement and continuous custody documentation** (`BRU-DTS-15`) — **`O-08`: no such agreement template exists** |
| **4.10.3** | **A referral outside Bangladesh is a cross-border transfer of restricted data and is prohibited** by `BRU-DTS-16` and `LG-012` §4.3. **A laboratory abroad is not an option for recovered data** |
| **4.10.4** | The Company remains responsible to the Customer for a partner's handling (`NFR-098`) |

### 4.11 Confidentiality — stated with its limit

| # | Clause |
|---|---|
| **4.11.1** | The Company treats everything it sees as the Customer's confidential information |
| **4.11.2** | It is not disclosed to anyone outside the case-assigned team, and **not to another part of the Company** without the Customer's instruction |
| **4.11.3** | Staff undertakings are recorded per case, before access (`BRU-DTS-12`), and survive the individual leaving the Company |
| **4.11.4** | **Confidentiality is preserved so far as the law permits.** §4.8 is the exception, and the Company does not promise a confidentiality it may be compelled to break |
| **4.11.5** | The Company does not use anything it sees for its own purposes — **not for analysis, not for marketing, not for training a model** (`BRU-DTS-14`) |

---

## 5. Liability, Exclusions and Limits

| # | Clause |
|---|---|
| **5.1** | The Company performs the work with reasonable skill and care, using the controls in §4.3 |
| **5.2** | **The Company does not warrant that recovery will succeed.** The data was already inaccessible when the media arrived |
| **5.3** | **Where nothing is recovered, no recovery fee is charged** (§4.4.3). That is the Customer's principal protection and it is stated as a term, not a courtesy — subject to `DS3` |
| **5.4** | **The Company is not liable for data it cannot recover**, or for the pre-existing condition of the media — provisional pending `DS4` |
| **5.5** | **The Company is liable for making the situation worse** — for damage to media caused by its own failure to exercise reasonable skill and care, and for loss of recovered data it held. **§4.3.4 imaging exists to reduce that risk, not to disclaim it** |
| **5.6** | **Cap.** Aggregate liability for a case is limited to the fees paid for it plus the reasonable cost of a further recovery attempt elsewhere — provisional pending G5 |
| **5.7** | The Company is not liable for a consequence of §4.8, where it acts on Legal Counsel's determination |
| **5.8** | **Nothing limits liability that cannot lawfully be limited**, including for a statutory data-protection liability, and **the consumer's right to complain to the DNCRP is preserved and unconditional** |
| **5.9** | The Customer indemnifies the Company for a breach of the §4.2.3 warranty |

---

## 6. Data Protection

> Must reconcile with `LG-008`, `LG-009`, `LG-012`. Check **F6**.

| # | Clause |
|---|---|
| **6.1** | This service is `LG-008` `P-09`, on contract performance with specific consent for access |
| **6.2** | **The recovered data may contain personal data about people who are not the Customer.** The Company processes it only to perform the work, never for its own purposes, and §4.2.5 asks the Customer to say when it will |
| **6.3** | **Recovered data and its index are held in a Bangladesh-resident store and are never replicated to a foreign region** (`BRU-DTS-16`, `LG-012` §4.3). **This is absolute — there is no registered-transfer route for it** |
| **6.4** | Recovered data is purged at the agreed date (`RC-09`); **case records are retained a minimum of five years** as processing records (`BRU-DTS-18`, `RC-09` second row) |
| **6.5** | **Purge is by destruction of the case-specific key** (`LG-009` `DM-3`), which is why `BRU-DTS-05` requires one per case |
| **6.6** | Access is logged immutably and retained five years (`BRU-DTS-03`, `RC-22`) |
| **6.7** | **A breach affecting case data is assessed and notified to the Authority where the threshold is met** (`BRU-DTS-17`), and the Customer is told |
| **6.8** | **Recovered data is never training or retrieval data** (`BRU-DTS-14`; `LG-008` §4.5.4) |
| **6.9** | An erasure request over case records is subject to the `LG-009` §4.5 override — the processing-record minimum — and the override and its basis are stated (`BRU-CPM-11`) |

---

## 7. Termination and Consequences

| Event | Consequence |
|---|---|
| **Case completed, data handed over** | Grace period runs (§4.5.3), then automatic purge at the agreed date (§4.5.4) |
| **Recovery fails** | **No recovery fee** (§5.3). Media returned; any image destroyed under §4.6 |
| **Customer cancels mid-case** | Work done and disclosed charges are payable; media returned; images destroyed |
| **Company cancels** — media unrecoverable, or beyond capability | No recovery fee; media returned; the Customer is told what was attempted |
| **Media abandoned** | §4.9, pending `DS5` |
| **§4.8 escalation** | Case frozen; Legal Counsel determines the response; the engagement may be suspended or terminated |
| **In every case** | §4.11 confidentiality survives, **subject to §4.11.4**; case records are retained five years; the purge of the data is separate from the retention of the record (`CL-01`) |

---

## 8. Dispute Resolution

| Step | Route |
|---|---|
| **1 — Case query** | The assigned team lead, then the Technical Services Head. **Case details only to the verified contact** (`BRU-DTS-13`) |
| **2 — Fee dispute** | Against the quotation and §4.4; then Finance |
| **3 — Complaint** | `SP-028`, closed only on the Customer's confirmation (`BRU-QMS-04`) |
| **4 — Consumer authority** | **The DNCRP — unconditional** |
| **5 — Courts** | The courts of Dhaka, Bangladesh |

**A §4.8 matter is not a dispute** and does not follow this route. It follows §4.8.4.

---

## 9. Change Control

| Version | Date | Change | Notice given to users | Re-acceptance required |
|---|---|---|---|:--:|
| 1.0 | 2026-08-18 | Initial issue — draft for G5. **§4.8 deliberately left as a stated gap pending `DS1`** | n/a | n/a |

| # | Rule |
|---|---|
| **9.1** | A change to fees, the purge model, the destruction standard or §4.8 is **MAJOR** |
| **9.2** | **A case in progress keeps the terms accepted when it opened** |
| **9.3** | **`DS1`'s answer is MAJOR and may require an immediate operational instruction ahead of the document** (`O-02`) |
| **9.4** | A change to §4.6.1 requires the sanitisation programme to be updated in the same release (`O-05`) |

---

## 10. Cross-References

| Document | Relationship | Must not contradict |
|---|---|---|
| [`LG-013_Service_Terms_Warranty_Terms_and_Exclusions.md`](LG-013_Service_Terms_Warranty_Terms_and_Exclusions.md) | §4.4.5; §4.7.7 destruction gate; **`WT5`/`DS5` are one question** | No charge for data the Company lost |
| [`LG-018_EWaste_EPR_and_Environmental_Compliance_Statements.md`](LG-018_EWaste_EPR_and_Environmental_Compliance_Statements.md) | §4.7.4 — **written three waves later (`O-07`)** | Environmental claims about destroyed media |
| [`LG-012_Cross_Border_Data_Transfer_and_Residency_Statement.md`](LG-012_Cross_Border_Data_Transfer_and_Residency_Statement.md) | **§6.3 absolute residency; §4.10.3 no overseas laboratory** | `BRU-DTS-16` |
| [`LG-009_Data_Retention_and_Deletion_Schedule.md`](LG-009_Data_Retention_and_Deletion_Schedule.md) | `RC-09` two-row structure; `DM-3`, `DM-5`; `DC-13` | **`O-03`/`LG-009` `O-06` purge maximum** |
| [`LG-008_Privacy_Notice_and_Consent_Copy.md`](LG-008_Privacy_Notice_and_Consent_Copy.md) | `P-09` and its risk statement | Check **F6** |
| [`LG-016_Managed_Services_and_Remote_Access_Consent_Terms.md`](LG-016_Managed_Services_and_Remote_Access_Consent_Terms.md) | §7 unlawful content on a Client system | The §4.8 escalation applies there too |
| [`LG-006_Vendor_Portal_Terms_and_Supplier_Code_of_Conduct.md`](LG-006_Vendor_Portal_Terms_and_Supplier_Code_of_Conduct.md) | §4.7.3 — the recycling partner's duty to refuse | The destruction gate |
| [`LG-021_ISMS_Policy_Set.md`](LG-021_ISMS_Policy_Set.md) | §4.3 controls; key management for `BRU-DTS-05` | Encryption and access policy |
| [`../05_Document_and_Print_Templates/05D_Commercial_and_Contract/DT-034_Data_Destruction_Certificate.md`](../05_Document_and_Print_Templates/05D_Commercial_and_Contract/DT-034_Data_Destruction_Certificate.md) | **§4.6.6 — what the certificate states** | `BRU-DTS-11` serial binding |
| [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-012_SOP_Data_Recovery_and_Secure_Data_Handling.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-012_SOP_Data_Recovery_and_Secure_Data_Handling.md) | **Operates every clause** | The §4.8 escalation steps |
| `HC-003` Help Set `P01` · `TR-*` data-services training | Explain the service | **No help may promise recovery, or an unqualified confidentiality (§4.11.4)** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Legal_Document.md` — ten sections in order; additions declared
- [x] **All eighteen `BRU-DTS-*` rules restated as contractual undertakings** the customer can hold the Company to (§4.3)
- [x] **The purge/retention distinction stated explicitly** — data purged, case record retained five years (`CL-01`)
- [x] **Unlawful content addressed as a stated gap with an operational escalation, not a drafted answer** (`CL-02`, `PR-01`)
- [x] Success-dependent fee model stated, including no charge for data the Company itself lost
- [x] Destruction standard cited as `BRU-DTS-08` states it, with the missing programme flagged
- [x] **Confidentiality stated with its limit** (§4.11.4) rather than promised absolutely
- [x] Overseas partner laboratories ruled out on residency grounds (§4.10.3)
- [x] All internal links resolve
- [ ] **`DS1`–`DS10` answered at G5** — outstanding, blocks `Approved`
- [ ] **Interim unlawful-content instruction issued** — outstanding, **`O-02`; the service is live at `W2` and this cannot wait for the document**
- [ ] **Purge maximum set** — outstanding, `O-03`
- [ ] **Fees published** — outstanding, `O-04`
- [ ] **Documented sanitisation programme created** — outstanding, `O-05`
- [ ] **Partner-laboratory confidentiality agreement created** — outstanding, `O-08`
- [ ] **Bengali counterpart authored and signed off in context** — outstanding
- [ ] Named approver recorded — pending
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
