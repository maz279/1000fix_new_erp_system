---
id: LG-010
title: Data Subject Request Handling Content
project: 1000FiX ERP System v2.0
content_type: Legal / policy
template: TPL_Legal_Document.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Chief Data Officer
author: Chief Data Officer with Legal & Compliance and Content Design
reviewers: [Legal Counsel, CTO delegate, Customer Service Manager, HR Director, Content Design Lead, Localisation Lead, Accessibility reviewer]
approver: Legal Counsel with the Chief Data Officer
content_class: B
purpose: >
  The process and the response wording for a data-subject request — intake channels, identity
  verification, scope determination across every module holding the subject's data, the response
  templates, the refusal grounds and the timelines. A rights request arriving with no process becomes
  a regulatory incident within days, because the statutory clock starts when the request arrives and
  not when someone notices it.
traces_to: [05-06 NFR-093, NFR-094, NFR-095, M33, M60, M24, M29, M27, M06, LG-001, LG-008, LG-009, LG-011, LG-012, LG-020, UI-042, HC-003, SP-028, BRU-CPM-09, BRU-CPM-10, BRU-CPM-11, BRU-CPM-15, BRU-GRC-19, BRU-GRC-20, BRU-SEC-05, BRU-SEC-23, BRU-DMS-02, FR-GRC-035, FR-DMS-041]
priority: P1
wave: W2
bilingual: yes
bn_counterpart: LG-010_Data_Subject_Request_Handling_Content_BN.md
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 §6.3 NFR-093 — access and portability, rectification with controller notification within 30 days, erasure on purpose cessation, consent withdrawal, unlawful processing or legal requirement, and withdrawal of consent through a simplified procedure
    verified: 2026-08-12
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M60 §5.4 FR-GRC-035 — receive, verify, route, fulfil and evidence data-subject requests within the statutory period, across every module holding personal data; §9 BRU-GRC-19
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/B_Customer_Engagement_and_Experience/M33 §9 BRU-CPM-09 immediate withdrawal across every channel and module; BRU-CPM-10 rectification notified within 30 days; BRU-CPM-11 erasure honoured except where a statutory retention obligation overrides, with the override and its basis stated
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M24 §5.4 FR-DMS-041 — a complete, sealed, hashed evidence pack assembled in under five minutes with a manifest and completeness check
    verified: 2026-08-18
    class: P1
  - source: project_content/03_UI_Copy_and_Microcopy/03D_Critical_Flows/UI-042_Consent_Privacy_and_Preference_Centre_Copy.md §3.4 flow.dsr.* rights copy and §5 error messages including flow.dsr.error.retention and flow.dsr.error.identity
    verified: 2026-08-18
    class: P1
  - source: Personal Data Protection Act 2026 — data-subject rights and the response expectations, as summarised by published legal analysis. **Secondary source; the statutory response period is unverified and is pending G5 with the external adviser who verifies LG-008**
    verified: 2026-08-18
    class: P2
supersedes: none
review_due: 2027-02-18
---

# LG-010 — Data Subject Request Handling Content

| Item | Value |
|---|---|
| Document class | **Policy + response templates** |
| Counterparty | Any data subject — customer, employee, technician, seller, rider, partner contact, applicant |
| Governing law | **Bangladesh** |
| Effective date | On publication of version 1.0 — *pending approval* |
| Acceptance capture method | **`AC-6` publication.** The templates are used, not agreed |
| Version accepted by users | n/a. **The version used to answer a request is recorded with the request** (`RQ-14`) |
| External counsel review | **Required** — the refusal grounds and the statutory period |
| Bengali version | **Required.** A request may arrive in Bengali and **must be answered in the language it was made in** (`RQ-04`) |

> ⚠ **Class B, and the file most likely to be needed before anyone expects it.**
>
> The first data-subject request will arrive from a customer who read `LG-008`. The statutory clock
> starts when it arrives — **not when it is recognised as a request**. A request written as *"delete
> my account"* in a chat message is a request. So is *"why do you have my phone number"*.
>
> **§4.2 exists to make recognition mechanical**, the same way `CG-013` §2 makes legal escalation
> mechanical for content authors. An agent who cannot recognise a request cannot route it, and an
> unrouted request runs the clock down silently.
>
> **Conformance note.** All ten template sections retained in order. The response templates are §4.6
> within §4 Terms. Gate questions and open items are §1.2 and §1.3 (`CP-09`).

---

## 1. Approval Record

| Role | Name | Date | Evidence |
|---|---|---|---|
| Drafted by | Chief Data Officer with Legal & Compliance | 2026-08-18 | Draft issue v1.0 |
| G1 Editorial — Content Design | *pending* | | |
| G2 Factual — CDO with Customer Service Manager and HR Director | *pending* | | |
| G4 Linguistic — independent reviewer, in context (`BN-018`) | *pending* | | |
| **G5 Legal — Legal Counsel** | *pending* | | **Required** |
| Approved by — Legal Counsel with CDO | *pending* | | |

### 1.2 Questions for Legal Counsel (G5)

| # | Question | Why it matters |
|---|---|---|
| **DR1** | **What is the statutory response period** for each right, and does it differ by right? §4.4 uses **30 days** throughout, taken from the one period `NFR-093` states explicitly — for rectification notification | The clock is the whole control. A wrong period is a systematic breach, not a one-off |
| **DR2** | May the period be **extended** for a complex request, and what notice does an extension require? | §4.4.4 assumes an extension is possible with notice |
| **DR3** | What **identity verification** is proportionate, and is it lawful to refuse a request where identity cannot be established? | Over-verification is itself a barrier to a right; under-verification discloses one person's data to another |
| **DR4** | Are the §4.5 **refusal grounds** complete and correctly stated? | A refusal on a ground that does not exist is a breach with a penalty |
| **DR5** | Does the **access** right extend to internal notes, technician observations, call recordings and fraud scores about the subject? | §4.3 takes a position; it needs confirming |
| **DR6** | Is a **fee** permitted for a repeat or manifestly excessive request? | §4.4.6 assumes no fee |
| **DR7** | Where a request comes from an **employee**, does the employment context change the answer on monitoring data, disciplinary records or manager correspondence? | `LG-020` covers monitoring; the request route is here |
| **DR8** | Where a request comes through a **third party** — a family member, a lawyer, a corporate administrator — what authority evidence is required? | §4.2.5 |

### 1.3 Open items

| # | Open item | Blocking? | Owner |
|---|---|:--:|---|
| **O-01** | `DR1`–`DR8` unanswered | **Yes — blocks `Approved`** | Legal Counsel |
| **O-02** | **`DR1` is the sharpest.** `NFR-093` states 30 days only for rectification notification. §4.4 applies 30 days to every right **as a stated working assumption**, marked provisional. If the statutory period is shorter, the process is already too slow | **Yes** | Legal Counsel with CDO |
| **O-03** | **`FR-GRC-035` requires fulfilment "across every module holding personal data" — 67 modules.** No module inventory of personal-data locations exists. §4.3.2 lists the locations known from `05-02` and `LG-008`; **it is not proven complete** | **Yes — an incomplete response is a breach** | CTO with CDO |
| **O-04** | **`M60` delivers the request workflow (`FR-GRC-035`) and is not delivered at `W2`.** Until then the process is manual, and a manual process across 67 modules will miss locations | **Yes** | CTO |
| **O-05** | **No Chief Data Officer is appointed** (`LG-008` `O-05`), and this file's owner is that role | **Yes — the process has no owner** | CEO |
| **O-06** | **Requests arriving through the contact centre are not yet routed.** `M27` dispositions have no data-request category, so a request in a chat or call is invisible to the process | **Yes — blocks `RQ-02`** | Customer Service Manager with CTO |
| **O-07** | Whether a **withdrawal of consent** is logged as a data-subject request or handled purely in the preference centre. §4.2.3 treats it as both: self-service where possible, logged always | No — position taken | CDO |

---

## 2. Scope and Parties

**In scope:** recognition and intake of a request through every channel; identity verification;
scope determination; the response templates in both languages; refusal grounds and how a refusal is
worded; timelines and the clock; evidencing fulfilment; and reporting.

**Out of scope:**

| Subject | Owned by |
|---|---|
| **What the rights are, and their statutory basis** | [`LG-008_Privacy_Notice_and_Consent_Copy.md`](LG-008_Privacy_Notice_and_Consent_Copy.md) §4.4 |
| **What may lawfully be refused, and for how long** | [`LG-009_Data_Retention_and_Deletion_Schedule.md`](LG-009_Data_Retention_and_Deletion_Schedule.md) §4.5 — **the override table is quoted, never re-derived** |
| Residency and transfer disclosure in an access response | [`LG-012_Cross_Border_Data_Transfer_and_Residency_Statement.md`](LG-012_Cross_Border_Data_Transfer_and_Residency_Statement.md) |
| Cookie preferences | [`LG-011_Cookie_and_Tracking_Policy.md`](LG-011_Cookie_and_Tracking_Policy.md) |
| **In-product rights copy, keys and Bengali strings** | [`../03_UI_Copy_and_Microcopy/03D_Critical_Flows/UI-042_Consent_Privacy_and_Preference_Centre_Copy.md`](../03_UI_Copy_and_Microcopy/03D_Critical_Flows/UI-042_Consent_Privacy_and_Preference_Centre_Copy.md) §3.4 — the `LG-008` §4.7 boundary applies here too |
| Complaint handling where the request is also a complaint | `SP-028` |
| The technical workflow | `M60` `FR-GRC-035` |

---

## 3. Definitions

| Term | Meaning |
|---|---|
| **Request** | Any communication in which a data subject seeks to exercise a right, **however it is worded and through whatever channel it arrives** |
| **Requester** | The person making the request, who may or may not be the data subject |
| **The clock** | The statutory response period, running from **receipt**, not from recognition (`RQ-01`) |
| **Scope determination** | Identifying every location holding the subject's data (`FR-GRC-035`) |
| **Override** | A statutory obligation defeating erasure, from `LG-009` §4.5 |
| **Partial fulfilment** | Fulfilling what can be fulfilled and refusing the rest, **with the refusal reasoned** |
| **Evidence of fulfilment** | The record that the request was answered, what was done, by whom and when (`BRU-GRC-19`) |

---

## 4. Terms

### 4.1 The rights and who handles them

| Right | Handled by | Self-service route | Assisted route |
|---|---|---|---|
| **Access** | DPO function | Portal download where scope allows | Full response under §4.6 `T-2` |
| **Portability** | DPO function | Portal export | `T-2` with a machine-readable file |
| **Rectification** | The owning data steward, then DPO confirms | Profile edit in the portal | `T-3`; **notification within 30 days** (`BRU-CPM-10`) |
| **Erasure** | DPO function with Legal | Account closure request | `T-4` or `T-5` where an override applies |
| **Withdraw consent** | Self-service, always available | **Preference centre — immediate** (`BRU-CPM-09`) | `T-6` where the subject cannot reach it |
| **Object to a legitimate-ground purpose** | DPO function with the purpose owner | — | `T-7` |
| **Complain** | DPO function; also `SP-028` where it is a service complaint | — | `T-8`, **and the route to the Authority is stated** |

### 4.2 Recognition and intake — making it mechanical

| # | Rule |
|---|---|
| **RQ-01** | **The clock starts on receipt by the company, through any channel.** Not on recognition, not on routing, not on the DPO seeing it |
| **RQ-02** | **Every channel is an intake channel:** the preference centre, email to the `LG-008` §4.9 contact, the contact centre by phone or chat, a branch counter, a letter, a portal message, or a social-media message. **`O-06`: the contact-centre route is not yet built** |
| **RQ-03** | **Any front-line role that receives one of the following logs it as a request within the same working day**, without judging whether it qualifies: |
| | *"Delete my account / my data"* · *"Send me my data / what do you have on me"* · *"Correct my …"* · *"Stop messaging me / unsubscribe"* · *"Who did you give my data to"* · *"Why do you have my …"* · *"I withdraw my consent"* · *"I want to complain about how you use my data"* |
| **RQ-04** | **A request is answered in the language it was made in.** A Bengali request receives a Bengali answer |
| **RQ-05** | **An agent never answers a request themselves.** They acknowledge, log and route. `CG-013` §4's discipline applies: the front line recognises, the accountable function decides |
| **RQ-06** | Acknowledgement is immediate, with a reference and the expected timescale — the same standard `BRU-CXM-01` sets for complaints |
| **RQ-07** | A request that is **also a complaint** runs both processes. Neither absorbs the other |
| **RQ-08** | **A request from a third party requires authority evidence** — `DR8`. Until it is provided, the clock is acknowledged as running and the company says what it needs |

### 4.3 Identity verification and scope

| # | Rule |
|---|---|
| **4.3.1** | **Identity is verified before any data is disclosed or deleted** (`UI-042` `flow.dsr.error.identity`). Verification is proportionate to what is being asked for — subject to `DR3` |
| **4.3.2** | **Scope determination covers every location holding the subject's data.** Known locations, from `05-02` and `LG-008` §4.2: party master, service orders and work orders, devices, invoices and receipts, payments, contracts and entitlements, warranty claims, loyalty, notifications and delivery logs, contact records and call recordings, complaints, documents in `M24`, access and audit logs, data-services cases, employee records where applicable, seller or partner records where applicable, and analytics datasets. **`O-03`: this list is the best known and is not proven complete** |
| **4.3.3** | Identity evidence collected for the request is **deleted on closure** (`LG-009` `RC-20`). Verifying identity must not create a new store of identity documents |
| **4.3.4** | **An evidence pack for the response is assembled through `M24`** with a manifest and completeness check (`FR-DMS-041`) |
| **4.3.5** | **Bulk export requires approval and is logged** (`BRU-SEC-05`). A subject-access response is an export |
| **4.3.6** | Data about **other people** — another customer on a shared address, a technician's notes, another party to a dispute — is redacted from the response (`FR-DMS-024`), and the redaction is stated |

### 4.4 Timelines — **provisional pending `DR1`**

| Stage | Target | Basis |
|---|---|---|
| Acknowledgement | **Immediate**, automated where the channel allows | `RQ-06` |
| Logged in the register | **Same working day** | `RQ-03` |
| Identity verification requested | **Within 2 working days** | Process |
| Scope determination complete | **Within 10 working days** | Process |
| **Substantive response** | **Within 30 days of receipt** — **provisional; `DR1`** | `NFR-093` states 30 days for rectification notification; applied across all rights as a working assumption |
| **Rectification notification to the subject** | **Within 30 days** | **`BRU-CPM-10` — this one is fixed** |
| **Consent withdrawal effect** | **Immediate, every channel, every module** | **`BRU-CPM-09` — this one is fixed** |
| Extension where permitted | With notice before the original period expires | **`DR2`** |
| No fee | Assumed | **`DR6`** |

| # | Rule |
|---|---|
| **4.4.1** | **A missed period is a breach, and is recorded as a control failure** (`BRU-GRC-12`), not as a service-level miss |
| **4.4.2** | **Consent withdrawal and rectification notification are not subject to `DR1`.** Their periods are fixed by `BRU-CPM-09` and `BRU-CPM-10` and are already operative |
| **4.4.3** | The register reports open requests, days elapsed and days remaining, daily |
| **4.4.4** | An extension is used for genuine complexity, never for queue management, and requires the DPO's decision — `DR2` |
| **4.4.5** | Where the company cannot complete in the period, it says so **before** the period expires, with what remains and when |
| **4.4.6** | **No fee is charged** — `DR6` |

### 4.5 Refusal grounds

**`RQ-09`: the only permitted refusal grounds are those below.** A refusal on any other basis is
escalated to Legal before it is sent — subject to `DR4`.

| # | Ground | Applies to | What the subject is told |
|---|---|---|---|
| **RF-01** | **Identity not established** | Any right | What is needed, and that the request stays open |
| **RF-02** | **Authority not evidenced** for a third-party requester | Any right | What authority evidence is required (`DR8`) |
| **RF-03** | **A statutory retention obligation overrides erasure** | Erasure | **The override and its basis, from `LG-009` §4.5 — and the date it expires** (`BRU-CPM-11`) |
| **RF-04** | **A legal hold is in force** | Erasure | That records relating to a matter are preserved, without prejudicing the matter (`BRU-SEC-23`) |
| **RF-05** | **The data is another person's** | Access, portability | That third-party data has been redacted (§4.3.6) |
| **RF-06** | **The request would prejudice a live investigation** — fraud, whistleblowing, disciplinary | Access | The minimum consistent with not prejudicing it; `BRU-GRC-20` restricts these records |
| **RF-07** | **The company does not hold the data** | Any right | That it is not held, and where the subject might look instead |
| **RF-08** | **The right does not apply to this processing** | Objection, erasure | Which basis the processing rests on and why the right does not reach it |

| # | Rule |
|---|---|
| **RF-R1** | **A refusal is never silent and never partial-by-omission.** What is refused, on which ground, and until when |
| **RF-R2** | **Every refusal states the route to the Authority** and to the courts |
| **RF-R3** | A refusal is approved by the DPO, and an `RF-03`/`RF-04` refusal is approved with Legal |
| **RF-R4** | **`RF-03` wording is taken from `LG-009` §4.5 verbatim.** Two different explanations of the same override is the F6 defect this rule prevents |

### 4.6 Response templates

> Bilingual pairs. English governs (`LG-001` `LR-03`); the Bengali is the version most subjects will
> read. **Wording here is the operative meaning; the in-product strings are `UI-042` §3.4** (the
> `LG-008` §4.7 boundary applies).

| # | Template | Sent when | Must contain |
|---|---|---|---|
| **T-1** | **Acknowledgement** | Immediately on receipt | The reference, what was understood as the request, the expected response date, what the company needs from the subject, and the contact for questions |
| **T-2** | **Access / portability response** | On fulfilment | The data, in a concise and intelligible form; **the recipients it was disclosed to**; the purposes; the retention; **the residency and any transfer** (`LG-012`); the rights that remain; the redaction statement where §4.3.6 applied |
| **T-3** | **Rectification confirmation** | Within 30 days | What was corrected, when, **and which recipients were notified** (`BRU-CPM-10`) |
| **T-4** | **Erasure completed** | On fulfilment | What was deleted, when, the method in plain words, and **what was retained under `RF-03` with its expiry date** |
| **T-5** | **Erasure partially refused** | On decision | The `LG-009` §4.5 override, its basis, **its expiry date**, what *was* deleted, and the route to the Authority |
| **T-6** | **Consent withdrawal confirmation** | Immediately | What stopped, **what continues and why** — the `UI-042` `flow.preference.withdrawn` position: *"Stopped. You will still get service updates"* |
| **T-7** | **Objection outcome** | On decision | The basis relied on, the assessment made, the outcome, and the route to challenge it |
| **T-8** | **Complaint response** | On decision | The finding, the remedy where any, **and the route to the Authority stated unconditionally** |
| **T-9** | **Identity or authority request** | Within 2 working days | Exactly what is needed and why; that the request remains open; no more than is necessary |
| **T-10** | **Extension notice** | Before the period expires | What remains, why, and the new date — `DR2` |
| **T-11** | **Breach notification to an affected subject** | Where the risk requires it (`NFR-094`) | What happened, what data, what the company has done, what the subject should do, and the contact |

| # | Rule |
|---|---|
| **T-R1** | **Plain language, at the `CG-011` reading level.** A response a subject cannot understand has not discharged a transparency obligation |
| **T-R2** | **No template blames the subject for the request, and none discourages a further one** |
| **T-R3** | **Every template names a human contact.** A no-reply address on a rights response is a barrier to a right |
| **T-R4** | Templates are versioned, and **the version used is recorded with the request** (`RQ-14`) |

### 4.7 Evidencing fulfilment

| # | Rule |
|---|---|
| **RQ-10** | **A request is fulfilled and evidenced within the statutory period, across every module holding that subject's data** (`BRU-GRC-19`) |
| **RQ-11** | The register records: receipt date and channel, requester, subject, rights sought, verification method and date, scope searched, actions taken per location, refusals with grounds, template version, decision-maker, dispatch date |
| **RQ-12** | **A request record is a processing record and is retained 5 years** (`LG-009` `RC-20`) |
| **RQ-13** | Volumes, timeliness, refusal grounds and breaches are reported monthly to the CDO and to the audit committee cadence |
| **RQ-14** | The template version used is recorded, so a past response can be reconstructed exactly |
| **RQ-15** | **A pattern of requests about one processing purpose is a signal about that purpose**, and is raised to the purpose owner, not just answered |

---

## 5. Liability, Exclusions and Limits

| # | Clause |
|---|---|
| **5.1** | This file creates no contractual limitation |
| **5.2** | **A missed period, an unfounded refusal, or a response disclosing another person's data are each a statutory failure** exposed to the penalties in `LG-008` §5.2 |
| **5.3** | **Disclosing to the wrong person is the more damaging failure.** It is a breach in itself, potentially notifiable under `NFR-094`, and is why §4.3.1 precedes everything |
| **5.4** | Fulfilling a request incompletely because a data location was unknown is **not a defence** — `O-03` is therefore a compliance risk and not a documentation gap |

---

## 6. Data Protection

> Must reconcile with `LG-008`, `LG-009`, `LG-012`. Check **F6**.

| Axis | This file | Reconciles with |
|---|---|---|
| The rights and their scope | §4.1 | **`LG-008` §4.4** — same rights, same names |
| Refusal grounds for erasure | `RF-03`, `RF-04` | **`LG-009` §4.5 override table — quoted verbatim** (`RF-R4`) |
| Rectification notification period | 30 days, fixed | **`BRU-CPM-10`, `NFR-093`, `LG-008` §4.4** |
| Withdrawal effect | Immediate, every channel and module | **`BRU-CPM-09`, `LG-008` `CN-R3`** |
| Transfers disclosed in an access response | `T-2` | **`LG-012` §4.5 and §4.6** |
| Identity-evidence retention | Deleted on closure | **`LG-009` `RC-20`** |
| Request-record retention | 5 years | **`LG-009` `RC-20`, `BRU-CPM-15`** |
| In-product wording | §4.6 meaning | **`UI-042` §3.4 wording** — `LG-008` `UB-01`…`UB-04` |

---

## 7. Termination and Consequences

| Event | Consequence |
|---|---|
| **Request fulfilled** | Evidence retained 5 years; identity evidence deleted; the subject may make a further request at any time |
| **Request refused** | The ground, its basis and its expiry are recorded; **the subject is told the route to the Authority** |
| **Override expires** | **The data becomes erasable.** `RF-03` states an expiry date so the subject can return, and so the schedule can act without a new request |
| **Requester goes silent after `T-9`** | The request is closed after a stated period, with a final notice, and **may be reopened** |
| **A legal hold is released** | Any erasure previously refused under `RF-04` is reassessed **without requiring a new request** |

---

## 8. Dispute Resolution

| Step | Route |
|---|---|
| **1 — Reconsideration** | The Chief Data Officer, on the subject's written objection |
| **2 — Internal escalation** | Legal Counsel, then the CFO (`CG-013` §3) |
| **3 — The Authority** | **The National Data Management Authority. Stated in every refusal (`RF-R2`) and in `T-8` unconditionally** |
| **4 — Courts** | The courts of Dhaka, Bangladesh |

---

## 9. Change Control

| Version | Date | Change | Notice given to users | Re-acceptance required |
|---|---|---|---|:--:|
| 1.0 | 2026-08-18 | Initial issue — draft for G5 | n/a | n/a |

| # | Rule |
|---|---|
| **9.1** | A change to a period, a refusal ground or a template's meaning is MAJOR and re-opens G5 |
| **9.2** | **A change to `LG-009` §4.5 automatically changes `RF-03`** — the wording is quoted, not authored here (`RF-R4`) |
| **9.3** | Every template version is retained, because a past response is defended by the template it used |
| **9.4** | **`DR1`'s answer is a MAJOR change by definition** and may make §4.4 already-breaching |

---

## 10. Cross-References

| Document | Relationship | Must not contradict |
|---|---|---|
| [`LG-008_Privacy_Notice_and_Consent_Copy.md`](LG-008_Privacy_Notice_and_Consent_Copy.md) | The rights this file operates | §4.4; check **F6** |
| [`LG-009_Data_Retention_and_Deletion_Schedule.md`](LG-009_Data_Retention_and_Deletion_Schedule.md) | **`RF-03` quotes its §4.5 verbatim** | The override set and expiry dates |
| [`LG-012_Cross_Border_Data_Transfer_and_Residency_Statement.md`](LG-012_Cross_Border_Data_Transfer_and_Residency_Statement.md) | `T-2` recipient and transfer disclosure | The transfer register |
| [`LG-011_Cookie_and_Tracking_Policy.md`](LG-011_Cookie_and_Tracking_Policy.md) | Cookie preference withdrawal | Consent categories |
| [`LG-020_Acceptable_Use_and_Internal_Access_Policy.md`](LG-020_Acceptable_Use_and_Internal_Access_Policy.md) | An employee request about monitoring data (`DR7`) | Monitoring notice |
| [`../03_UI_Copy_and_Microcopy/03D_Critical_Flows/UI-042_Consent_Privacy_and_Preference_Centre_Copy.md`](../03_UI_Copy_and_Microcopy/03D_Critical_Flows/UI-042_Consent_Privacy_and_Preference_Centre_Copy.md) | The in-product rights copy | `flow.dsr.*` wording versus §4.6 meaning |
| [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-028_SOP_Complaint_Escalation_and_Compensation.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-028_SOP_Complaint_Escalation_and_Compensation.md) | `RQ-07` dual running | Acknowledgement standards |
| `HC-003` Help Set `P01` · `TR-007` agent course · `TR-017` contact-centre course | **Where `RQ-03` recognition is actually taught** | The recognition list |
| `TS-017` Security and Privacy Test Case Pack | Verifies consent enforcement and rights fulfilment | The process as specified |
| `OP-004` incident templates | `T-11` breach notification | Breach wording |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Legal_Document.md` — ten sections in order; additions declared
- [x] **Recognition made mechanical with a verbatim phrase list** (`RQ-03`), following the `CG-013` §2 pattern
- [x] **Clock starts on receipt, not recognition** (`RQ-01`) — stated as the first rule
- [x] Eight refusal grounds, closed set, with `RF-03` quoting `LG-009` §4.5 verbatim rather than paraphrasing
- [x] **Eleven response templates** with mandatory content, including the expiry date on an override refusal
- [x] Two fixed periods (`BRU-CPM-09`, `BRU-CPM-10`) distinguished from the provisional 30 days
- [x] All internal links resolve
- [x] Accessibility standard `CG-011` applied to template wording (`T-R1`)
- [ ] **`DR1`–`DR8` answered at G5** — outstanding, blocks `Approved`
- [ ] **The personal-data location inventory proven complete** — outstanding, `O-03`; an incomplete response is a breach
- [ ] **Contact-centre intake routing built** — outstanding, `O-06`
- [ ] **Chief Data Officer appointed** — outstanding, `O-05`
- [ ] **Bengali counterpart authored and signed off in context** — outstanding
- [ ] Named approver recorded — pending
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
