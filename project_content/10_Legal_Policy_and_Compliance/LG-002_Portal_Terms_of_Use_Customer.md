---
id: LG-002
title: Portal Terms of Use — Customer
project: 1000FiX ERP System v2.0
content_type: Legal / policy
template: TPL_Legal_Document.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Legal & Compliance
author: Legal & Compliance with Content Design and Customer Experience
reviewers: [Legal Counsel, Chief Data Officer, CFO delegate, Customer Service Manager, Content Design Lead, Localisation Lead, Accessibility reviewer]
approver: Legal Counsel
content_class: B
purpose: >
  The binding terms on which an individual customer holds a P01 account and transacts through it —
  eligibility, account duties, acceptable use, how a service is ordered and priced, what the
  company does and does not promise, suspension, and the law that governs the relationship.
  250,000+ customers a month transacting under no accepted terms is unmanaged liability, and every
  downstream limit the company relies on has to attach to something the customer agreed to.
traces_to: [P01, M01, M20, M10, M12, M27, M33, M34, M38, LG-001, LG-008, LG-009, LG-011, LG-013, LG-014, LG-017, LG-019, UI-042, UI-037, UI-039, DT-002, DT-005, DT-009, DT-010, HC-019, BRU-MKP-07, BRU-CXM-13, BRU-ARB-07, BRU-SRM-02, PS-03, PS-04]
priority: P0
wave: W2
bilingual: yes
bn_counterpart: LG-002_Portal_Terms_of_Use_Customer_BN.md
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 P01 capability set and design requirements — account, devices, booking, tracking, approvals, payments, contracts, warranty, loyalty, shop, trade-in, data services, recycling, support, feedback; Bengali-first with professional translation; WCAG 2.1 AA
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-MKP-07 — the customer must explicitly consent to marketplace fulfilment, with the implications stated, before a job is broadcast
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-CXM-13 — reviews are published only with the customer's explicit consent; BRU-ARB-07 — a cash receipt above BDT 50,000 requires the customer's NID
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 §6.1 statutory currency table — ICT Act 2006 in force; Personal Data Protection Act 2026 in force with enforcement mechanisms activating approximately 13 May 2027
    verified: 2026-08-12
    class: P1
  - source: Consumer Rights Protection Act 2009 — the consumer complaint route to the Directorate of National Consumer Rights Protection, and the statutory limits on excluding consumer remedies. Instrument-level citation; clause-level content is unverified in this file and is verified at gate G5
    verified: 2026-08-18
    class: P2
  - source: Digital Commerce Operation Guidelines 2021 (Ministry of Commerce, issued 4 July 2021) — delivery and refund timelines applicable to the P01 shop and advance-payment paths. Instrument-level citation; clause-level content pending G5
    verified: 2026-08-18
    class: P2
supersedes: none
review_due: 2027-02-18
---

# LG-002 — Portal Terms of Use (Customer)

| Item | Value |
|---|---|
| Document class | **Terms** — click-wrap contract with a consumer |
| Counterparty | Individual customer holding a `P01` account (web portal and mobile application) |
| Governing law | **Bangladesh** |
| Effective date | On publication of version 1.0 — *pending approval* |
| Acceptance capture method | **`AC-1` click-wrap at registration**, version and hash recorded in the `LG-001` §4.5 ledger; re-acceptance on any MAJOR change (`LR-19`) |
| Version accepted by users | Recorded in `LG-001` — per user, per version, per language presented |
| External counsel review | **Required** — consumer enforceability and the §5 limits |
| Bengali version | **Required** (`CG-010` §3.2). Bengali is the **default** presentation on `P01` (`PS-03`); English governs in a dispute (`LG-001` `LR-03`) |

> ⚠ **Class B — legal, consumer-facing, at the largest scale in the register.** Every limit in §5
> and every disclaimer in §4 is only as good as the acceptance record behind it. `LG-001` §4.5 is
> not an administrative annex to this document; it is what makes this document operative.
>
> **Conformance note.** All ten template sections are retained in order. Outstanding gate
> questions and open items appear as **§1.2 and §1.3** rather than as added sections, so the
> `TPL_Legal_Document.md` spine is unaltered (`CP-09`, gate E7).

---

## 1. Approval Record

| Role | Name | Date | Evidence |
|---|---|---|---|
| Drafted by | Legal & Compliance with Content Design | 2026-08-18 | Draft issue v1.0 |
| G1 Editorial — Content Design | *pending* | | |
| G2 Factual — Customer Service Manager | *pending* | | |
| G4 Linguistic — independent reviewer, in context (`BN-018`) | *pending* | | |
| **G5 Legal — Legal Counsel** | *pending* | | **Required** |
| Approved by — Legal Counsel | *pending* | | |

> No file of this class may reach `status: Approved` without every row completed (`CG-007`,
> rule `CM-R7`, audit check **E2**).

### 1.2 Questions for Legal Counsel (G5)

| # | Question | Why it cannot be answered internally |
|---|---|---|
| **CU1** | Are the §5 liability caps enforceable against a consumer under Bangladesh law, and at what level? | A cap that a consumer-protection instrument voids leaves the company with **no** limit, not a lower one |
| **CU2** | Is the §4.9 **data-loss disclaimer** enforceable where the company handled the device, and does it survive if the loss was avoidable? | This is the single most likely consumer claim against a repair business |
| **CU3** | Is the §4.11 **uncollected-device** regime — storage charge, then disposal after a stated period — lawful, and what notice is required before disposal? | Disposing of another person's property requires a lawful basis, not a term |
| **CU4** | Does continued use, as distinct from an affirmative act, ever bind a consumer to changed terms? `LR-19` assumes not | If it does, §9 can be simplified. If it does not, the re-acceptance build is mandatory |
| **CU5** | Does the Digital Commerce Operation Guidelines 2021 delivery-and-refund regime apply to the `P01` **shop and trade-in** paths, to **repair services**, or to both? | It changes the refund clock in `LG-014` and the promises made at checkout |
| **CU6** | Is arbitration under §8 available and enforceable in a consumer contract, or must the consumer route remain open in all cases? | §8 must not appear to close a statutory complaint route |
| **CU7** | Is the §4.13 marketplace disclosure sufficient for the company to be the customer's counterparty while a third party performs the work? | `BRU-MKP-20` has the company remedy first and recover separately — the terms must match that posture |

### 1.3 Open items

| # | Open item | Blocking? | Owner |
|---|---|:--:|---|
| **O-01** | `CU1`–`CU7` unanswered | **Yes — blocks `Approved`** | Legal Counsel |
| **O-02** | The `LG-001` §4.5 version-acceptance ledger has no owning module (`LG-001` `O-06`). **Without it these terms are published but not provably accepted** | **Yes — blocks W2 go-live, not this document** | CTO |
| **O-03** | Bengali counterpart not authored; `PS-03` makes Bengali the default presentation, so the **Bengali text is what most customers will actually accept** | **Yes — `CM-R6`** | Localisation Lead |
| **O-04** | §4.4 pricing indication depends on `MD-029` rate-card publication rules; the customer-facing status of an indicative price is not settled | No — drafted as indicative | CCO with Legal |

---

## 2. Scope and Parties

| Party | Identity |
|---|---|
| **The Company** | 1000FiX Services Limited, a company incorporated in Bangladesh. Hotline 16743 · info@1000fix.com |
| **The Customer** | A natural person aged 18 or over who registers a `P01` account, or who transacts at a branch and is issued an account |

**These terms cover:** registration and use of the `P01` portal and mobile application; ordering,
tracking, approving and paying for services; purchases from the `P01` shop; trade-in and recycling
requests; loyalty membership; reviews and complaints; and use of the in-product AI assistant.

**These terms do not cover, and are subordinate to, the following where a conflict arises:**

| Subject | Governed by | Precedence |
|---|---|---|
| Repair warranty scope, exclusions and liability limits | [`LG-013_Service_Terms_Warranty_Terms_and_Exclusions.md`](LG-013_Service_Terms_Warranty_Terms_and_Exclusions.md) | **`LG-013` prevails** on warranty |
| Refunds, cancellation and compensation | [`LG-014_Refund_Cancellation_and_Compensation_Policy.md`](LG-014_Refund_Cancellation_and_Compensation_Policy.md) | **`LG-014` prevails** |
| Personal data | [`LG-008_Privacy_Notice_and_Consent_Copy.md`](LG-008_Privacy_Notice_and_Consent_Copy.md) · [`LG-009_Data_Retention_and_Deletion_Schedule.md`](LG-009_Data_Retention_and_Deletion_Schedule.md) · [`LG-012_Cross_Border_Data_Transfer_and_Residency_Statement.md`](LG-012_Cross_Border_Data_Transfer_and_Residency_Statement.md) | **They prevail** — check **F6** requires zero contradiction |
| Cookies and tracking | [`LG-011_Cookie_and_Tracking_Policy.md`](LG-011_Cookie_and_Tracking_Policy.md) | `LG-011` prevails |
| Data recovery and secure destruction | [`LG-017_Data_Recovery_and_Secure_Destruction_Terms.md`](LG-017_Data_Recovery_and_Secure_Destruction_Terms.md) | `LG-017` prevails |
| An AMC, RAMC or corporate contract | [`LG-015_AMC_SLA_Master_Terms_and_Service_Credit_Rules.md`](LG-015_AMC_SLA_Master_Terms_and_Service_Credit_Rules.md) and the executed contract | **The contract prevails** |
| A corporate portal user acting for an employer | [`LG-003_Portal_Terms_of_Use_Corporate.md`](LG-003_Portal_Terms_of_Use_Corporate.md) | `LG-003` applies instead |

> **`CL-01`. The precedence table is the whole point of §2.** Nine documents touch one customer.
> A customer reading a warranty exclusion here and a different one in `LG-013` has found a defect
> the company will lose on. **This document therefore states the precedence and does not restate
> the substance** (`CP-01`).

---

## 3. Definitions

| Term | Meaning |
|---|---|
| **Account** | The registered `P01` identity, authenticated through `M29` single sign-on (`PS-01`) |
| **Service order** | A request for service accepted by the Company, identified by a service order reference (`fix.service.order`, `CG-004`) |
| **Estimate** | The priced diagnosis presented for the Customer's approval before chargeable work begins (`DT-005`) |
| **Indicative price** | A price shown before diagnosis. **Not an estimate and not binding** (§4.4) |
| **Device** | The item the Customer delivers or presents for service, identified by serial or IMEI |
| **Repair warranty** | The Company's warranty on its own workmanship and parts, defined in `LG-013` |
| **Marketplace fulfilment** | Performance of a job by an approved third-party seller through `P07` (§4.13) |
| **Uncollected device** | A device not collected within the period stated in §4.11 after the Customer is notified it is ready |
| **Business day** | A day on which the Company's branches are open, per the `MD-041` Bangladesh calendar |
| **Governing text** | The **English** version of these terms (`LG-001` `LR-03`). The Bengali version is the presented default on `P01` and is of equal operative intent (`LR-04`) |

---

## 4. Terms

### 4.1 Eligibility and account

| # | Clause |
|---|---|
| **4.1.1** | The Customer must be 18 or over. Where a person under 18 requires service, the account and the order are held by a parent or guardian. Personal data of a person under 18 is processed only with verifiable parental consent (`LG-008` §4.6; `BRU-CPM-16`) |
| **4.1.2** | The Customer gives accurate registration details and keeps them current. A rectification right exists at all times (`LG-010`) |
| **4.1.3** | The Account is personal. Credentials are not shared. The Customer is responsible for activity under the Account except where the Company is at fault |
| **4.1.4** | The Company may require identity verification before releasing a device, disclosing service history, or acting on a data-subject request (`LG-010` §4.2) |
| **4.1.5** | Where a cash payment reaches or exceeds **BDT 50,000**, the Company is required to record the Customer's National ID before the receipt can be completed (`BRU-ARB-07`, `BRU-TAX-18`). That identifier is used **only** for that statutory purpose, is encrypted, and every access to it is logged (`BRU-TAX-19`) |

### 4.2 Acceptable use

The Customer must not: attempt unauthorised access; interfere with the platform's operation;
scrape or bulk-extract data; submit false service requests, false reviews or false claims; upload
malware; impersonate another person; or use the platform to infringe another's rights. **Every
file uploaded is malware-scanned before it is stored or served** (`BRU-SEC-22`).

### 4.3 Ordering a service

| # | Clause |
|---|---|
| **4.3.1** | A service order is created when the Company accepts the request. Submitting a request is not acceptance |
| **4.3.2** | A warranty-type order can be created only where warranty is active at the request date (`BRU-SRM-02`, `BRU-WTY-01`) |
| **4.3.3** | Delivery mode — walk-in, on-site, pick-and-drop, or remote — is agreed at booking and is part of what is priced |
| **4.3.4** | Where the Customer hands over a device, the Company issues an intake receipt recording the device, its stated condition and accessories (`DT-002`). **The intake receipt is the custody record.** The Customer should check it before leaving |

### 4.4 Price, estimate and approval

| # | Clause |
|---|---|
| **4.4.1** | An **indicative price** may be shown at booking. It is based on the described fault before inspection and **does not bind either party** |
| **4.4.2** | Chargeable work begins only after the Customer approves an **estimate** (`DT-005`). Approval may be given in the portal, on the technician's device, or at the counter, and is recorded (`UI-038`, `LG-019`) |
| **4.4.3** | If the required work changes, a **revised estimate** is presented and approved before the additional work proceeds (`DT-006`). Work outside an approved estimate is not chargeable |
| **4.4.4** | Prices are in Bangladesh Taka and include VAT at the rate determined by the Company's tax engine. A tax invoice (Mushak 6.3) is issued for every taxable supply (`DT-010`, `BRU-TAX-04`) |
| **4.4.5** | Where a diagnosis is performed and the Customer declines the repair, a diagnostic charge applies **only if** it was disclosed before the diagnosis began |

### 4.5 Payment

Payment methods are those offered in the portal — bKash, Nagad, card and bank transfer — and at
the counter. **The Company does not store card details; only a gateway token and the last four
digits are retained** (`BRU-ARB-25`). Payment is due as stated on the invoice. Where payment is
overdue, the Company may withhold release of a device until payment is made, subject to §4.11.

### 4.6 Warranty on the repair

The Company warrants its own workmanship and the parts it supplies **on the terms in `LG-013`**,
which state the period, the scope, the exclusions and the claim route. Those terms are presented
at intake and reproduced on the warranty document (`DT-032`). Nothing in this document extends,
reduces or reinterprets them.

### 4.7 Cancellation, refund and compensation

Governed entirely by `LG-014`. **This document creates no separate refund right and no separate
exclusion.**

### 4.8 Loyalty, points and vouchers

Membership tiers, point accrual, expiry, redemption and voucher conditions are those published in
the portal and held in `MD-034`. Points have no cash value, are not transferable, and are
forfeited where an account is terminated for a breach of §4.2. **A change that reduces an accrued
benefit is a MAJOR change under §9.**

### 4.9 Data on the Customer's device

| # | Clause |
|---|---|
| **4.9.1** | **The Customer is responsible for backing up their own data before handing over a device.** The Company will say so at intake, on `DT-002`, and in the portal |
| **4.9.2** | Repair may require access to data on the device. Where it does, the Company does not copy or retain it (`UI-042` §3.2) |
| **4.9.3** | Some repairs — board-level work, storage replacement, factory reset, software reinstallation — **carry a real risk of data loss that cannot be eliminated**. Where the Company knows a procedure carries that risk, it will say so before the Customer approves it |
| **4.9.4** | Data recovery is a separate service on separate terms (`LG-017`). It is not part of a repair |
| **4.9.5** | The Company's liability for data loss is limited as stated in §5, **subject to `CU2`** |

> **`CL-02`. §4.9.1 is a disclosure, not a defence.** A term that tells the Customer to take a
> backup does not answer a claim that the Company lost data it should not have lost. The
> substantive position is §5 and it must survive `CU2`.

### 4.10 Device collection and release

The device is released to the Customer, or to a person the Customer authorises, on identity
verification and against a release receipt (`DT-009`). Where delivery is arranged, custody
transfers on recorded handover (`DT-028`).

### 4.11 Uncollected devices

| # | Clause |
|---|---|
| **4.11.1** | The Company notifies the Customer when the device is ready, and repeats the notification on the schedule in `NT-020` |
| **4.11.2** | A storage charge may apply after a stated free period. The period and the charge are published and are not varied case by case |
| **4.11.3** | After a longer stated period, and **after notice to the last known contact details**, the Company may dispose of the device and apply proceeds against unpaid charges |
| **4.11.4** | Any device disposed of under §4.11.3 passes through the same certified data-destruction gate as any other outbound device (`BRU-ESG-01`, `LG-017` §4.6). **A device is never disposed of with the Customer's data still on it** |

> **`CL-03`. §4.11.3 is the highest-risk clause in this document.** It authorises the Company to
> dispose of property it does not own. The periods, the notice content and the notice method are
> deliberately left to `CU3` rather than drafted and then defended.

### 4.12 Reviews, ratings and complaints

The Customer may rate a service and write a review. **A review is published only with the
Customer's explicit consent** (`BRU-CXM-13`). The Company may decline to publish content that is
unlawful, abusive or identifies a third party. A complaint is acknowledged immediately with a
reference and an expected timescale (`BRU-CXM-01`), is owned by a named person (`BRU-CXM-02`), and
is closed only on the Customer's confirmation (`BRU-QMS-04`, `BRU-CXM-04`). The complaint process
is `SP-028`; the escalation and compensation authority is `LG-014` §4.7.

### 4.13 Marketplace fulfilment

| # | Clause |
|---|---|
| **4.13.1** | Some jobs may be performed by an approved third-party seller. **This happens only where the Customer has explicitly consented, with the implications stated, before the job is broadcast** (`BRU-MKP-07`) |
| **4.13.2** | Quality, evidence and warranty standards for a marketplace-fulfilled job are **identical** to a job performed by the Company (`BRU-MKP-02`, `BRU-ECM-03`) |
| **4.13.3** | Where the customer experience requires it, the Company remedies the Customer first and recovers from the seller separately (`BRU-MKP-20`) |
| **4.13.4** | A seller receives the Customer's name, contact and address **only for an awarded job**, and only until a defined period after completion (`EA-04`, `BRU-MKP-04`) |

### 4.14 The AI assistant

The in-product assistant is disclosed as automated, states what it cannot do, and hands over to a
person on request or when it cannot answer. **It does not commit the Company to a price, a
timescale or a legal position**, and an answer it gives is not a term of this agreement
(`LG-008` §4.8; `HC-019`).

### 4.15 Notifications and marketing

Service notifications are part of providing the service and continue while a service is active.
Marketing messages require separate, freely given consent that may be withdrawn at any time, and
withdrawal takes effect immediately across every channel (`BRU-CPM-09`, `UI-042` §3.3). **The two
are never bundled** (`LG-001` `LR-07`).

### 4.16 Suspension

The Company may suspend or restrict an Account for a breach of §4.2, for suspected fraud, or where
required by law. **Suspension is notified with a reason and a route to challenge it**, except where
notice would prejudice an investigation or breach a legal duty.

---

## 5. Liability, Exclusions and Limits

> **Every clause in this section is subject to `CU1` and `CU2` and is marked provisional under
> `CG-012` `PR-01`. A provisional term may not be relied on for a contractual commitment
> (`PR-03`).**

| # | Clause |
|---|---|
| **5.1** | The Company is liable for loss it causes by failing to exercise reasonable skill and care |
| **5.2** | The Company is **not** liable for: loss arising from information the Customer gave that was wrong or incomplete; a pre-existing fault or condition disclosed at intake and recorded on `DT-002`; loss caused by the Customer's own act after release; or a delay caused by a third party outside the Company's control and notified to the Customer |
| **5.3** | **Data loss.** Where data is lost in the course of a repair, the Company's liability is limited to re-performing the service and to attempting recovery at no charge where recovery is technically possible. **This clause is provisional pending `CU2`** |
| **5.4** | **Cap.** The Company's aggregate liability for a service order is limited to the amount paid for that service order, or to the reasonable cost of repairing or replacing the device with an equivalent, whichever the parties agree — **provisional pending `CU1`** |
| **5.5** | **Nothing in this section limits liability that cannot lawfully be limited**, including liability for death or personal injury caused by negligence, for fraud, or for a right a consumer-protection instrument makes non-excludable |
| **5.6** | The Company does not exclude or limit the Customer's statutory right to complain to the Directorate of National Consumer Rights Protection, or to any other lawful remedy |

> **`CL-04`. §5.5 and §5.6 are what make §5.3 and §5.4 arguable at all.** A liability section with
> no carve-out for non-excludable rights is more likely to be struck down in its entirety than a
> section that states its own limits honestly.

---

## 6. Data Protection

> Must reconcile with `LG-008` privacy notice, `LG-009` retention schedule and `LG-012` residency
> statement. **Contradiction between them is a compliance defect** — audit check **F6**.

| # | Clause |
|---|---|
| **6.1** | The Company processes personal data as set out in `LG-008`, which states the categories, the purposes, the lawful basis for each purpose, retention, recipients, the Customer's rights and how to exercise them |
| **6.2** | Processing is on **consent or a stated legitimate ground, recorded per purpose** before it begins (`NFR-090`, `BRU-CPM-07`, `BRU-GRC-16`) |
| **6.3** | Consent is **clear, explicit, specific and freely given**, and is recorded together with the version of the notice presented (`NFR-091`, `BRU-CPM-08`) |
| **6.4** | The Customer may **access, port, rectify and erase** their data, and withdraw consent through a simplified route. Rectification is notified within **30 days** (`NFR-093`, `BRU-CPM-10`). Requests are handled per `LG-010` |
| **6.5** | Erasure is honoured **except where a statutory retention obligation overrides it**. Where it does, the override and its basis are stated to the Customer (`BRU-CPM-11`). The schedule is `LG-009` |
| **6.6** | Certain identifiers — National ID, passport number, TIN and biometric data — are held in a **Bangladesh-resident** store and are not replicated outside Bangladesh (`NFR-086`, `BRU-CPM-06`, `BRU-SEC-13`). `LG-012` is the statement of what may and may not leave |
| **6.7** | Accepting these terms is **not** consent to processing. Consent is a separate act captured separately (`LG-001` `LR-08`) |
| **6.8** | Cookies and similar technologies are governed by `LG-011`, with consent captured per category |

---

## 7. Termination and Consequences

| Event | Consequence |
|---|---|
| **Customer closes the account** | Open service orders continue to completion; invoices remain payable; loyalty points lapse; personal data is handled per §6.4 and `LG-009` |
| **Company terminates for breach of §4.2** | Access ends; points are forfeited; open orders are completed or refunded per `LG-014`; the device is returned |
| **Company withdraws the portal** | Not less than the notice period in §9; service continues through branch and hotline channels; account data is exportable before closure (`NFR-093` portability) |
| **In every case** | **Warranties already given survive.** Statutory retention survives account closure. Records held under a legal hold are not deleted (`BRU-SEC-23`, `BRU-DMS-02`) |

---

## 8. Dispute Resolution

| Step | Route |
|---|---|
| **1 — Complaint** | The `SP-028` complaint process. Acknowledged immediately with a reference and a timescale; owned by a named person; closed only on the Customer's confirmation |
| **2 — Escalation** | Branch Manager, then Customer Service Manager, per the `SP-005` escalation matrix. Compensation authority is `LG-014` §4.7 |
| **3 — Consumer authority** | **The Customer's right to complain to the Directorate of National Consumer Rights Protection is preserved and is not conditional on steps 1 and 2** |
| **4 — Courts** | The courts of Dhaka, Bangladesh, have jurisdiction. Bangladesh law governs |

> **§8 deliberately does not impose arbitration on a consumer** pending `CU6`. Commercial
> counterparty documents (`LG-003`…`LG-007`, `LG-015`) do provide for arbitration, and the
> difference is intentional.

---

## 9. Change Control

| Version | Date | Change | Notice given to users | Re-acceptance required |
|---|---|---|---|:--:|
| 1.0 | 2026-08-18 | Initial issue — draft for G5 | n/a — not yet published | n/a |

| # | Rule |
|---|---|
| **9.1** | A **MAJOR** change — to an obligation, a right, a charge, an exclusion, a liability limit or a data use — requires advance notice to every accepting Customer and **affirmative re-acceptance** (`LG-001` `LR-19`) |
| **9.2** | A MINOR change is published with a change note and does not require re-acceptance |
| **9.3** | **A MAJOR change is not retrospective.** A service order already in progress continues under the version accepted for it (`LG-001` `LR-17`) |
| **9.4** | Every version, its effective date, its hash and its acceptance record are held in `LG-001` |
| **9.5** | A change driven by a statutory instrument is published immediately and re-opens the gates in `CG-007` §7 |

---

## 10. Cross-References

| Document | Relationship | Must not contradict |
|---|---|---|
| [`LG-001_Legal_Content_Register_and_Signoff_Log.md`](LG-001_Legal_Content_Register_and_Signoff_Log.md) | Version, acceptance ledger, approval evidence | Acceptance mechanism `AC-1` |
| [`LG-013_Service_Terms_Warranty_Terms_and_Exclusions.md`](LG-013_Service_Terms_Warranty_Terms_and_Exclusions.md) | **Prevails on warranty** | Warranty scope, exclusions, liability |
| [`LG-014_Refund_Cancellation_and_Compensation_Policy.md`](LG-014_Refund_Cancellation_and_Compensation_Policy.md) | **Prevails on refunds** | Refund eligibility and timelines |
| [`LG-008_Privacy_Notice_and_Consent_Copy.md`](LG-008_Privacy_Notice_and_Consent_Copy.md) | Prevails on personal data | §6 in full — check **F6** |
| [`LG-009_Data_Retention_and_Deletion_Schedule.md`](LG-009_Data_Retention_and_Deletion_Schedule.md) | Retention behind §6.5 and §7 | Erasure override basis |
| [`LG-012_Cross_Border_Data_Transfer_and_Residency_Statement.md`](LG-012_Cross_Border_Data_Transfer_and_Residency_Statement.md) | Residency behind §6.6 | Which data may leave Bangladesh |
| [`LG-011_Cookie_and_Tracking_Policy.md`](LG-011_Cookie_and_Tracking_Policy.md) | Prevails on cookies | Consent categories |
| [`LG-017_Data_Recovery_and_Secure_Destruction_Terms.md`](LG-017_Data_Recovery_and_Secure_Destruction_Terms.md) | Separate service, separate terms (§4.9.4) | Destruction standard behind §4.11.4 |
| [`LG-019_ESignature_Legal_Notice_and_Evidence_Statement.md`](LG-019_ESignature_Legal_Notice_and_Evidence_Statement.md) | Evidentiary basis for §4.4.2 approval and `AC-1` | Assurance level per document class |
| [`../03_UI_Copy_and_Microcopy/03D_Critical_Flows/UI-042_Consent_Privacy_and_Preference_Centre_Copy.md`](../03_UI_Copy_and_Microcopy/03D_Critical_Flows/UI-042_Consent_Privacy_and_Preference_Centre_Copy.md) | The in-product consent and rights copy | §6.3, §6.4, §4.15 |
| [`../05_Document_and_Print_Templates/05A_Service_and_Operations/DT-002_Service_Intake_Receipt_and_Device_Handover_Form.md`](../05_Document_and_Print_Templates/05A_Service_and_Operations/DT-002_Service_Intake_Receipt_and_Device_Handover_Form.md) | Where §4.3.4 and §4.9.1 are actually presented | Stated condition; backup warning |
| [`../05_Document_and_Print_Templates/05A_Service_and_Operations/DT-005_Repair_Estimate_and_Quotation.md`](../05_Document_and_Print_Templates/05A_Service_and_Operations/DT-005_Repair_Estimate_and_Quotation.md) | The estimate in §4.4.2 | What an estimate commits |
| [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-028_SOP_Complaint_Escalation_and_Compensation.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-028_SOP_Complaint_Escalation_and_Compensation.md) | Operates §4.12 and §8 | Escalation timings |
| `HC-003` Help Set `P01` · `HC-019` AI Guardrail and Disclosure | Explain these terms to the Customer; §4.14 | Nothing in help may state a term these do not |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Legal_Document.md` — all ten sections in order; additions declared in the conformance note
- [x] Precedence table present, so nine overlapping documents cannot contradict each other silently (`CL-01`)
- [x] Every clause with statutory exposure carries a G5 question rather than an invented answer
- [x] Liability clauses **marked provisional** under `CG-012` `PR-01`, with the non-excludable carve-out stated (`CL-04`)
- [x] Data-protection section reconciles clause by clause with `LG-008`, `LG-009`, `LG-012` — check **F6**
- [x] Consumer complaint route to the DNCRP explicitly preserved (§5.6, §8 step 3)
- [x] Terminology matches `CG-004`
- [x] All internal links resolve
- [x] Accessibility standard `CG-011` applied — reading level, structure, no colour-only meaning
- [ ] **Bengali counterpart authored and signed off in context (`BN-018`)** — outstanding, `O-03`; Bengali is the default presentation
- [ ] **Named approver recorded (`CG-007`, `LG-001`)** — pending
- [ ] **G5 answers `CU1`–`CU7` obtained** — outstanding, blocks `Approved`
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)
- [ ] Decisions logged in `RF-006` — outstanding, `RF-006` does not exist

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
