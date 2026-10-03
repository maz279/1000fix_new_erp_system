---
id: LG-020
title: Acceptable Use and Internal Access Policy
project: 1000FiX ERP System v2.0
content_type: Legal / policy
template: TPL_Legal_Document.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Legal & Compliance with the CTO
author: Legal & Compliance with the CTO, HR, Security and the Chief Data Officer
reviewers: [Legal Counsel, CTO, HR Director, Chief Data Officer, Security lead, Quality Manager, Localisation Lead, Accessibility reviewer]
approver: Legal Counsel with the CTO
content_class: B
purpose: >
  What 800+ internal users may and may not do with company systems and the customer data in them, what
  the company monitors and discloses that it monitors, and the consequences of breach. Access to the
  personal data of 250,000+ customers a month needs a stated boundary and a stated consequence;
  without both, a data misuse case has no policy to be a breach of and no disciplinary route.
traces_to: [M29, M60, M21, M55, M66, M24, P02, P03, P09, P11, LG-001, LG-008, LG-009, LG-010, LG-011, LG-012, LG-016, LG-019, LG-021, LG-023, DT-042, MD-009, MD-012, SP-006, SP-023, SP-031, TR-021, EA-10, BRU-SEC-01, BRU-SEC-02, BRU-SEC-05, BRU-SEC-06, BRU-SEC-07, BRU-SEC-08, BRU-SEC-11, BRU-SEC-16, BRU-SEC-17, BRU-SEC-18, BRU-SEC-19, BRU-SEC-20, BRU-SEC-22, BRU-SEC-24, BRU-SEC-25, BRU-GRC-10, BRU-GRC-20, BRU-DTS-02, BRU-DTS-12, BRU-MKP-19, FR-GRC-029, FR-GRC-030, FR-GRC-031, NFR-097]
priority: P1
wave: W1
bilingual: yes
bn_counterpart: LG-020_Acceptable_Use_and_Internal_Access_Policy_BN.md
sources:
  - source: 1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M29 §9 BRU-SEC-01 MFA on admin, finance and HR access at every login; BRU-SEC-02 step-up authentication for payouts, payroll finalisation, data-case access and bulk export; BRU-SEC-05 personal data cannot be exported in bulk without approval and every export is logged; BRU-SEC-06 leaver access revoked within one hour; BRU-SEC-07 incompatible duties cannot be assigned, exceptions time-boxed, mitigated and reported quarterly; BRU-SEC-11 audit entries insert-only and undeletable by anyone including administrators; BRU-SEC-16 access unconfirmed at the close of a certification cycle is revoked automatically; BRU-SEC-17 no account without an active accountable owner for more than 24 hours; BRU-SEC-18 a user may not administer their own access; BRU-SEC-19 privileged access is time-boxed with no standing administrative rights; BRU-SEC-20 break-glass notifies multiple parties, expires automatically and requires post-hoc justification; BRU-SEC-25 a revoked token or leaver event takes effect estate-wide within 60 seconds
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04 §4 data isolation tiers T0 to T5; §5 field-level permissions including nid_number, bank_account, salary, recovered_data_index, call_recording_url and seller_kyc_document; §6 segregation of duties SOD-01 to SOD-12; §9 access lifecycle
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M60 §5.3 FR-GRC-029 policy library controlled through M24, FR-GRC-030 policy attestation with escalation for non-acknowledgement, FR-GRC-031 policy exception management; §9 BRU-GRC-20 whistleblowing, legal matter and breach records are tier T5
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 P02 capability set — shift clock-in and clock-out with geofence, turn-by-turn navigation with automatic arrival detection, panic and safety alert; P09 custody with GPS at every handover; P11 offline audit execution
    verified: 2026-08-18
    class: P1
  - source: Bangladesh Labour Act 2006 and Bangladesh Labour Rules 2015 — the framework for disciplinary process, and the limits on employer action. **Instrument-level citation from secondary sources; clause-level content unverified and pending G5 with HR and Legal**
    verified: 2026-08-18
    class: P2
supersedes: none
review_due: 2027-02-18
---

# LG-020 — Acceptable Use and Internal Access Policy

| Item | Value |
|---|---|
| Document class | **Policy** — internal, binding on employees and contractors |
| Counterparty | Every employee, contractor, temporary worker and third-party engineer with system access |
| Governing law | **Bangladesh** |
| Effective date | On publication of version 1.0 — *pending approval*. **`W1`, with `P03` go-live** |
| Acceptance capture method | **`AC-4` attestation at induction and annually**, tracked with escalation for non-acknowledgement (`FR-GRC-030`), captured at `AL-2` (`LG-019` §4.5) |
| Version accepted by users | Recorded in `LG-001`; **attestation is per person per version** |
| External counsel review | **Required** — the §4.6 monitoring disclosure and the §7 disciplinary consequences under the Labour Act |
| Bengali version | **Required and operative.** 200–400 field technicians, 51+ branches of counter staff and 50–200 riders will read the Bengali version or none |

> ⚠ **Class B, `W1`. This is the file that makes data misuse a disciplinary matter rather than a
> disappointment.**
>
> 800+ internal users can reach the records of 250,000+ customers a month. The platform enforces
> **twenty-five `BRU-SEC-*` rules**, `T0`–`T5` isolation and twelve segregation-of-duties blocks — but
> **a control stops what it can see. It does not stop an agent looking up a neighbour's repair
> history, which is technically permitted access and a serious misuse.**
>
> **§4.4 is therefore the heart of the file: legitimate business need as the test, not permission as
> the test.**
>
> **§4.6 also carries the most intrusive disclosure in the register — continuous location tracking of
> a field workforce.** It is stated plainly, in Bengali, because the alternative is monitoring people
> who were never told.
>
> **Conformance note.** All ten template sections retained in order. Acceptable use is §4.3, the data
> access rule §4.4, monitoring §4.6, within §4 Terms. Gate questions and open items are §1.2 and §1.3
> (`CP-09`).

---

## 1. Approval Record

| Role | Name | Date | Evidence |
|---|---|---|---|
| Drafted by | Legal & Compliance with the CTO and HR | 2026-08-18 | Draft issue v1.0 |
| G1 Editorial — Content Design | *pending* | | |
| G2 Factual — CTO with HR Director and Security lead | *pending* | | |
| G4 Linguistic — independent reviewer, in context (`BN-018`) | *pending* | | |
| **G5 Legal — Legal Counsel** | *pending* | | **Required** |
| Approved by — Legal Counsel with the CTO | *pending* | | |

### 1.2 Questions for Legal Counsel and HR (G5)

| # | Question | Why it matters |
|---|---|---|
| **AU1** | **What monitoring is lawful and what must be disclosed**, under the Labour Act framework and the data-protection regime? §4.6 discloses everything the company can technically see | Monitoring an employee is processing their personal data. Undisclosed monitoring is both an employment and a data-protection failure |
| **AU2** | **Is continuous location tracking of a field technician during a shift lawful and proportionate**, and does it need to stop outside shift hours? `P02` has geofenced clock-in, turn-by-turn navigation and automatic arrival detection | **The most intrusive processing in the estate, on the least-consulted workforce** |
| **AU3** | **Is biometric attendance lawful**, and can an employee refuse it and be offered an alternative? | `LG-008` `PN7`; `M55` |
| **AU4** | **What disciplinary process must precede dismissal** for a §4.3 or §4.4 breach, and what evidence standard applies? | `LG-023` and `DT-042` supply the letters; the process must be lawful before the letters matter |
| **AU5** | **May the company inspect a personal device** used for work, and to what extent? | §4.8 takes a restrictive position |
| **AU6** | **Is an employee's own data-subject request over monitoring data answerable in full**, or is any of it exempt? | `LG-010` `DR7` |
| **AU7** | **What may be said in a reference or to a future employer** about a dismissal for data misuse? | Not addressed in this draft; raised because it will be asked |
| **AU8** | **May the company monitor a company-issued device outside working hours**, and what happens to what it sees? | §4.6.7 prohibits it as policy; confirmation makes it a position |

### 1.3 Open items

| # | Open item | Blocking? | Owner |
|---|---|:--:|---|
| **O-01** | `AU1`–`AU8` unanswered | **Yes — blocks `Approved`** | Legal Counsel with HR Director |
| **O-02** | **`AU2` cannot wait.** `P02` is `W2` and its geofence, navigation and arrival detection are non-negotiable requirements. **The technician workforce is 200–400 people with high turnover and mixed literacy, and the disclosure has to be Bengali-native, not translated** (`BN-016` applies the same logic to training) | **Yes — blocks `P02` go-live disclosure** | Legal Counsel with HR |
| **O-03** | **`LG-021` ISMS is `W2` and this file is `W1`.** §4.5 and §4.9 reference security controls whose policy set arrives a wave later. **The same sequencing shape as `LG-006`/`LG-018`** | **Yes — sequencing** | Programme Content Lead |
| **O-04** | **`TR-025` does not exist.** `AUDIT-009` TR-01 found that the **Layer 1 statutory induction curriculum for 800+ employees has no owning file**. **This policy is attested at induction — the induction it is attested at is unregistered** | **Yes — the attestation has no delivery vehicle** | L&D with Programme Content Lead |
| **O-05** | **No disciplinary sanction ladder exists.** §7 states consequences by severity; `DT-042` holds HR letter templates; **nothing maps a breach class to a sanction** | **Yes — blocks §7** | HR Director with Legal |
| **O-06** | **`FR-GRC-030` attestation tracking is in `M60`, which is not delivered at `W1`.** At `W1` attestation is manual, for 800+ people | **Yes** | CTO with HR |
| **O-07** | **Three roles are unregistered in `MD-009`** (`AUDIT-009`). A policy addressed to "every role" cannot be allocated to a role that does not exist in the register | Yes | HR with Master Data Owner |
| **O-08** | **Contractor and third-party engineer access is not distinguished from employee access anywhere.** §2 states the position; **`MD-012` covers employees, and there is no equivalent standard for a contractor** | Yes | HR with CTO |

---

## 2. Scope and Parties

| Party | Identity |
|---|---|
| **The Company** | 1000FiX Services Limited |
| **The User** | Any employee, contractor, temporary worker, intern, or third-party engineer granted access to a company system |

**In scope:** use of company systems, devices, networks, accounts and data; the rule governing access
to customer and colleague personal data; monitoring and its disclosure; personal-device use; and the
consequences of breach.

**Applies equally to a contractor and to an employee**, except that a contractor's consequence is
contractual termination rather than a disciplinary sanction — **`O-08`**.

**Out of scope:**

| Subject | Owned by |
|---|---|
| **The security controls themselves** | [`LG-021_ISMS_Policy_Set.md`](LG-021_ISMS_Policy_Set.md) — **`O-03`** |
| Ethics, gifts, conflicts and the speak-up channel | [`LG-023_Anti_Bribery_Ethics_and_Whistleblowing_Content.md`](LG-023_Anti_Bribery_Ethics_and_Whistleblowing_Content.md) |
| What the company does with customer data | [`LG-008_Privacy_Notice_and_Consent_Copy.md`](LG-008_Privacy_Notice_and_Consent_Copy.md) |
| Retention of monitoring records | [`LG-009_Data_Retention_and_Deletion_Schedule.md`](LG-009_Data_Retention_and_Deletion_Schedule.md) `RC-12`, `RC-22`, `RC-24` |
| Remote access to a **client's** systems | [`LG-016_Managed_Services_and_Remote_Access_Consent_Terms.md`](LG-016_Managed_Services_and_Remote_Access_Consent_Terms.md) |
| Employment terms, pay and leave | The employment contract and `DT-042` |
| Role definitions and permissions | `05-04`; `MD-009` — **`O-07`** |
| Segregation-of-duties register | [`../06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-006_Segregation_of_Duties_Register.md`](../06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-006_Segregation_of_Duties_Register.md) |

---

## 3. Definitions

| Term | Meaning |
|---|---|
| **Company system** | Any platform, portal, application, device, network or account the company provides or controls |
| **Customer data** | Any data about a customer, including their identity, device, service history, payments and communications |
| **Legitimate business need** | A specific task the User is assigned that requires this record. **§4.4's test** |
| **Isolation tier** | `T0` global to `T5` restricted (`05-04` §4). **`T5` requires explicit grant, logged access and step-up authentication** |
| **Privileged access** | Administrative rights. **Time-boxed; no standing rights** (`BRU-SEC-19`) |
| **Break-glass** | Emergency access; multi-party notified, auto-expiring, justified after the fact (`BRU-SEC-20`) |
| **Bulk export** | Any extract of multiple records. **Requires approval and is logged** (`BRU-SEC-05`) |
| **Monitoring** | Any recording or observation of a User's activity, location or communications on a company system |
| **Attestation** | The User's recorded acknowledgement of this policy (`FR-GRC-030`) |

---

## 4. Terms

### 4.1 The basis

| # | Clause |
|---|---|
| **4.1.1** | Company systems are provided for company business |
| **4.1.2** | **Access is granted by role and is the minimum the role needs** (`05-04`) |
| **4.1.3** | **A User is accountable for everything done under their account.** Credentials are not shared, not written down, not lent |
| **4.1.4** | **Every access to customer personal data is logged**, and the log is insert-only and undeletable by anyone, including administrators (`BRU-SEC-11`, `EA-10`) |
| **4.1.5** | This policy is attested at induction and annually. **Non-acknowledgement escalates** (`FR-GRC-030`) |

### 4.2 What the company provides and what it expects

| # | Clause |
|---|---|
| **4.2.1** | **MFA is required at every login** for admin, finance and HR access (`BRU-SEC-01`) |
| **4.2.2** | **Sensitive actions require step-up authentication** — payouts, payroll finalisation, data-case access, bulk export (`BRU-SEC-02`) |
| **4.2.3** | **Privileged access is time-boxed. There are no standing administrative rights** (`BRU-SEC-19`) |
| **4.2.4** | **A User may not administer their own access or approve their own access request** (`BRU-SEC-18`, `SOD-09`) |
| **4.2.5** | **Access unconfirmed at the close of a certification cycle is revoked automatically** (`BRU-SEC-16`). **A User who does not respond loses access — that is the control, not an error** |
| **4.2.6** | **Every account has an active accountable owner**; none may exist without one for more than 24 hours (`BRU-SEC-17`) |
| **4.2.7** | **Incompatible duties cannot be assigned.** An exception is time-boxed, mitigated, approved by the CFO or CTO, and appears on a standing quarterly report (`BRU-SEC-07`, `BRU-GRC-10`, `SP-006`) |
| **4.2.8** | **Break-glass access notifies multiple parties immediately, expires automatically, and requires post-hoc justification** (`BRU-SEC-20`). **Using it is not a fault; failing to justify it is** |
| **4.2.9** | **Every file upload is malware-scanned before it is stored or served** (`BRU-SEC-22`) |
| **4.2.10** | **Production data used in non-production must be masked** (`BRU-SEC-08`), and never contains unmasked residency-classified data in any region (`NFR-086c`) |

### 4.3 Acceptable use

**A User must not:**

| # | Prohibition |
|---|---|
| **AU-01** | Share, lend or transfer credentials, or use another person's account |
| **AU-02** | Attempt to access data or a system they are not authorised to reach |
| **AU-03** | Circumvent, disable or test a security control without written authorisation |
| **AU-04** | **Export customer or employee personal data in bulk without approval** (`BRU-SEC-05`) |
| **AU-05** | **Copy customer data to a personal device, personal email, personal cloud storage or a messaging application** |
| **AU-06** | Photograph or screenshot a screen containing customer or employee personal data, except as a task requires and a control permits |
| **AU-07** | Install unauthorised software, or connect an unauthorised device to a company network |
| **AU-08** | Use a company system to store or transmit unlawful, harassing, discriminatory or obscene material |
| **AU-09** | Use a company system for private commercial gain, or to compete with the company |
| **AU-10** | Send a communication that appears to be from the company without authority |
| **AU-11** | **Discuss a customer, a colleague or a case outside the company**, including on social media, including without naming them, where they could be identified |
| **AU-12** | **Delete, alter or conceal a record**, or attempt to alter an audit entry (`BRU-SEC-11`) |
| **AU-13** | **Record credentials in a ticket, a note or an email** (`BRU-RMS-03`) |
| **AU-14** | Leave a session unlocked, or a device unattended in a public place |
| **AU-15** | Use a company system after their access should have been removed |
| **AU-16** | **Retaliate against a person who raised a concern** (`LG-023`) |

**A User must:**

| # | Obligation |
|---|---|
| **AU-17** | Report a suspected security incident, a lost device or a suspected data breach **immediately** |
| **AU-18** | Report a colleague's suspected misuse of data (`LG-023` channel available) |
| **AU-19** | Complete required training and attest to this policy |
| **AU-20** | Return every device, credential and record on leaving |

### 4.4 The customer-data rule — **the clause the file exists for**

> **`CL-01`. Technical permission is not authorisation.** A service centre agent can open any customer
> record, because their job requires it. **Nothing in `05-04` prevents them opening their neighbour's,
> their former partner's, or a public figure's — and every one of those is a serious misuse that the
> platform will happily permit and faithfully log.**

| # | Rule |
|---|---|
| **DA-01** | **A User may access a customer, employee or counterparty record only where a legitimate business need requires it** — a task assigned to them, on a case they are working |
| **DA-02** | **Curiosity is not a legitimate business need.** Neither is concern, familiarity, a favour, or checking on someone |
| **DA-03** | **A User must not access the record of a person they know personally.** Where a task requires it, they hand it to a colleague and record that they did |
| **DA-04** | **A User must not access their own record** through an operational route. There is a self-service route for that |
| **DA-05** | **A User must not look up a public figure, a celebrity or a person in the news** |
| **DA-06** | **What is seen is used only for the task**, is not repeated, and is not remembered aloud |
| **DA-07** | **`T5` restricted data — payroll, National ID, bank details, data-recovery case content, call recordings, audit logs, biometric templates, seller KYC documents — is accessed only on explicit grant, with step-up authentication, and every access is logged** (`05-04` §4, `BRU-SEC-02`) |
| **DA-08** | **A data-recovery case is accessible only to the assigned team, with a confidentiality undertaking recorded per case before access** (`BRU-DTS-02`, `BRU-DTS-12`) |
| **DA-09** | **Every access is logged and the log is reviewed.** A User should assume that any access they make can be seen, because it can |
| **DA-10** | **Accessing without need is a disciplinary matter even where nothing is done with what was seen.** The access is the breach |

> **`DA-10` is the sentence that makes the policy work.** Without it, an agent argues that no harm was
> done. With it, the question is only whether the access had a business need — which the ticket either
> shows or does not.

### 4.5 Devices, networks and offline data

| # | Clause |
|---|---|
| **4.5.1** | A company device is used for company business, kept secure, and returned on leaving |
| **4.5.2** | **`P02`, `P09` and `P11` hold customer data offline by design** (`PS-08`). A User must not extract it, and must report a lost device immediately (`AU-17`) |
| **4.5.3** | **A lost or stolen device is a potential data breach**, assessed under `LG-008` §4.8 |
| **4.5.4** | Offline caches are cleared per `LG-009`; a User must not attempt to preserve one |
| **4.5.5** | Company networks are not used to bypass a control, and personal hotspots are not used to avoid one |

### 4.6 Monitoring — what the company sees, stated plainly

> **`CL-02`. This section discloses everything the platform can technically observe about a User.**
> `AU1` and `AU2` will determine what is **lawful**; disclosing it is a precondition either way, and
> **an undisclosed capability is the failure — not the capability.**

| # | What is monitored | Where | Why | Notes |
|---|---|---|---|---|
| **MO-01** | **Every access to customer personal data** | All systems | Accountability, breach investigation, `EA-10` | Insert-only, undeletable (`BRU-SEC-11`) |
| **MO-02** | **Every action on a controlled object** — create, change, delete, approve | All systems | Audit trail | `BRU-SEC-12` |
| **MO-03** | **Login, logout, MFA, failed attempts, session and device** | `M29` | Security | |
| **MO-04** | **Bulk exports, with approval and requester** | All | `BRU-SEC-05` | |
| **MO-05** | **Privileged and break-glass use, with justification** | All | `BRU-SEC-19`, `BRU-SEC-20` | |
| **MO-06** | **Shift clock-in and clock-out, with geofence** | `P02` | Attendance, pay | **`AU2`** |
| **MO-07** | **Location during a shift** — turn-by-turn navigation, automatic arrival detection, GPS on every custody handover and evidence photograph | `P02`, `P09`, `P11` | Dispatch, custody, evidence, safety | **The most intrusive processing in the estate. `AU2`, `O-02`** |
| **MO-08** | **Biometric attendance template** | `M55` | Attendance | **Irreversible template, never exported; deleted at termination** (`LG-009` `RC-13`). **`AU3`** |
| **MO-09** | **Call recordings on customer calls** | `M27`, `P10` | Quality, training, dispute | The customer is told at the start of the call |
| **MO-10** | **Job timings, documentation time, QC outcomes, rework** | `P02`, `M23` | Performance | Feeds the technician scorecard |
| **MO-11** | **Company email and messaging on company systems** | Internal IT | Security, legal hold, investigation | **Not read routinely; accessed on a defined authority** |
| **MO-12** | **Remote-session records and, where enabled, recordings** | `LG-016` | Client assurance | `LG-016` §4.7.6 — **not used for performance management without telling the User** |
| **MO-13** | **Device compliance state** on company devices | Internal IT | Security | Not content |

| # | Rule |
|---|---|
| **MO-R1** | **Monitoring is proportionate to a stated purpose.** Data collected for one purpose is not repurposed silently |
| **MO-R2** | **Monitoring output is not used for a disciplinary decision without a process** — `AU4` |
| **MO-R3** | **A User may make a data-subject request over their own monitoring data** (`LG-010`, `AU6`) |
| **MO-R4** | **Monitoring records are retained per `LG-009`** — `RC-12` attendance, `RC-22` logs, `RC-24` location history at 90 days full granularity |
| **MO-R5** | **The company does not monitor a company device outside working hours**, and where technical capability exists it is not used — `AU8`, §4.6.7 |
| **MO-R6** | **This section is disclosed in Bengali before a technician's first shift**, not buried in an English handbook (`O-02`) |
| **MO-R7** | **A panic or safety alert is a protection, not a monitoring feature**, and location taken during one is used for that purpose |

### 4.7 Personal devices

The company does not require a personal device for work. Where a User is permitted to use one,
**company data is not stored on it**, access is through a controlled route, and **the company does not
inspect the personal contents of a personal device** — `AU5`. A User who has stored company data on a
personal device must say so, and it is removed.

### 4.8 Joining, changing role and leaving

| # | Clause |
|---|---|
| **4.8.1** | Access is granted on the role, approved by the line manager, and for a privileged role by the line manager, IT Administrator and CTO (`05-04` §7) |
| **4.8.2** | **A role change removes the old access as well as granting the new.** Accumulated access is the most common cause of a segregation-of-duties breach |
| **4.8.3** | **A leaver's access is revoked within one hour of the leaver event** (`BRU-SEC-06`), and **takes effect estate-wide within 60 seconds of revocation** (`BRU-SEC-25`) |
| **4.8.4** | **Access is recertified periodically; unconfirmed access is revoked automatically** (`BRU-SEC-16`) |
| **4.8.5** | Devices, credentials and records are returned on leaving (`AU-20`) |
| **4.8.6** | **Confidentiality survives employment.** A former User remains bound in respect of what they learned |

---

## 5. Liability, Exclusions and Limits

| # | Clause |
|---|---|
| **5.1** | This is an internal policy and creates no third-party rights |
| **5.2** | **A breach of §4.3 or §4.4 is a disciplinary matter**, up to and including dismissal, and may be a criminal matter |
| **5.3** | **A data misuse by a User is the company's liability to the affected person.** The company's recourse against the User does not reduce it, which is why §4.4 is a policy rather than guidance |
| **5.4** | The company may recover a loss it suffers from a User's deliberate misuse, to the extent the law permits |
| **5.5** | Nothing here reduces a User's own statutory employment or data-protection rights |
| **5.6** | **A User who reports a breach in good faith — including their own — is protected** (`LG-023`), and `AU-16` prohibits retaliation |

---

## 6. Data Protection

> Must reconcile with `LG-008`, `LG-009`, `LG-012`. Check **F6**.

| # | Clause |
|---|---|
| **6.1** | The company processes User personal data for employment, payroll, attendance, performance, security and access control — `LG-008` `P-10` and `P-19` |
| **6.2** | **§4.6 is the transparency notice for that processing**, as `NFR-092` requires. **A monitoring capability not listed there is not disclosed, and therefore should not be used** |
| **6.3** | **TIN and biometric template are Bangladesh-resident** (`LG-012` §4.3, `BRU-CPM-06`); **bank details and individual payroll are `S3`** and proposed as resident additions (`LG-012` §4.3) |
| **6.4** | Monitoring data is retained per `LG-009` `RC-10`…`RC-13`, `RC-22`, `RC-24` |
| **6.5** | **A User's own data-subject request is handled under `LG-010`**, with `DR7` open on whether employment context changes any answer |
| **6.6** | **A User must not use their access to satisfy their own curiosity about their own record** (`DA-04`). The self-service route exists precisely so `DA-04` can be absolute |
| **6.7** | **Whistleblowing, legal-matter and breach records are `T5`** — allow-list, step-up, every access logged (`BRU-GRC-20`). **A User cannot look up who reported what** |

---

## 7. Termination and Consequences — **pending `AU4`, `O-05`**

| Breach class | Examples | Consequence |
|---|---|---|
| **Class 1 — Careless** | Unlocked session, unattended device, a late incident report | Coaching, retraining, recorded |
| **Class 2 — Negligent** | Credentials written down, data emailed to a personal address, unapproved software | Formal warning; access review |
| **Class 3 — Deliberate misuse of access** | **Looking up a person with no business need** (`DA-01`…`DA-05`) | **Final warning or dismissal.** The access is the breach (`DA-10`) |
| **Class 4 — Serious misuse** | Disclosing customer data outside the company; bulk extract without approval; altering or concealing a record; retaliation | **Dismissal; referred for legal action** |
| **Class 5 — Criminal** | Data theft, fraud, unauthorised access to a third party's systems | **Dismissal and referral to the authorities** |

| # | Rule |
|---|---|
| **7.1** | **A consequence follows a process** — `AU4`, and the Labour Act framework governs it |
| **7.2** | **A sanction ladder mapping a breach class to a sanction does not exist** — `O-05`. Until it does, §7 is a classification, not a tariff |
| **7.3** | A contractor's consequence is contractual — suspension and termination of engagement — and is reported to their employer where one exists |
| **7.4** | **A breach affecting personal data is assessed for notification** to the Authority and to the affected person (`LG-008` §4.8), **independently of the disciplinary outcome** |
| **7.5** | **Access is revoked at suspension, not at the conclusion of a process** |
| **7.6** | Letters are `DT-042`; **the letter is not the process** |

---

## 8. Dispute Resolution

| Step | Route |
|---|---|
| **1 — Access query** | The line manager, then the IT Administrator |
| **2 — Disciplinary appeal** | The HR process, per the employment contract and the Labour Act framework |
| **3 — A concern about the policy itself, or about monitoring** | The Chief Data Officer; or the `LG-023` channel where the User prefers confidentiality |
| **4 — A data-subject request about monitoring data** | `LG-010` |
| **5 — Courts and labour authorities** | As the Labour Act framework provides |

---

## 9. Change Control

| Version | Date | Change | Notice given to users | Re-acceptance required |
|---|---|---|---|:--:|
| 1.0 | 2026-08-18 | Initial issue — draft for G5. Twenty acceptable-use rules, ten data-access rules, thirteen disclosed monitoring capabilities, five breach classes | n/a | n/a |

| # | Rule |
|---|---|
| **9.1** | A change to §4.3, §4.4, §4.6 or §7 is **MAJOR**: notice and **re-attestation** |
| **9.2** | **Adding a monitoring capability requires §4.6 to be updated and re-disclosed before it is switched on.** Not after |
| **9.3** | Attestation is per person per version, tracked, with escalation for non-acknowledgement (`FR-GRC-030`) |
| **9.4** | **A policy exception is recorded, approved, time-boxed and reviewed** (`FR-GRC-031`) |
| **9.5** | Every version retained permanently (`LG-009` `DC-23`), because a disciplinary decision is judged against the version in force |

---

## 10. Cross-References

| Document | Relationship | Must not contradict |
|---|---|---|
| [`LG-021_ISMS_Policy_Set.md`](LG-021_ISMS_Policy_Set.md) | **The controls behind §4.2 and §4.5 — `W2`, after this file (`O-03`)** | Access, cryptography, incident policy |
| [`LG-023_Anti_Bribery_Ethics_and_Whistleblowing_Content.md`](LG-023_Anti_Bribery_Ethics_and_Whistleblowing_Content.md) | `AU-16`, `AU-18`, §5.6, §8 step 3 | Reporting channel and protection |
| [`LG-008_Privacy_Notice_and_Consent_Copy.md`](LG-008_Privacy_Notice_and_Consent_Copy.md) | **§4.6 is the employee transparency notice** | `P-10`, `P-19`; check **F6** |
| [`LG-009_Data_Retention_and_Deletion_Schedule.md`](LG-009_Data_Retention_and_Deletion_Schedule.md) | `MO-R4` | `RC-10`…`RC-13`, `RC-22`, `RC-24` |
| [`LG-010_Data_Subject_Request_Handling_Content.md`](LG-010_Data_Subject_Request_Handling_Content.md) | `MO-R3`, §6.5 | `DR7` employment context |
| [`LG-011_Cookie_and_Tracking_Policy.md`](LG-011_Cookie_and_Tracking_Policy.md) | **§4.2 and §4.7.3 there route work-app telemetry to this file** | Internal-portal position |
| [`LG-016_Managed_Services_and_Remote_Access_Consent_Terms.md`](LG-016_Managed_Services_and_Remote_Access_Consent_Terms.md) | `MO-12`; §7 disciplinary route for a §4.2 breach there | Session recording use |
| [`LG-019_ESignature_Legal_Notice_and_Evidence_Statement.md`](LG-019_ESignature_Legal_Notice_and_Evidence_Statement.md) | Attestation at `AL-2` | Attestation evidence |
| [`../06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-006_Segregation_of_Duties_Register.md`](../06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-006_Segregation_of_Duties_Register.md) | §4.2.7 | The twelve SoD rules |
| [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-031_SOP_IT_Service_Desk_and_Change_Management.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-031_SOP_IT_Service_Desk_and_Change_Management.md) · [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-023_SOP_Recruitment_and_Onboarding.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-023_SOP_Recruitment_and_Onboarding.md) | Access request, joiner and leaver operation | §4.8 |
| [`../05_Document_and_Print_Templates/05E_People_Quality_and_Labelling/DT-042_HR_Letter_Template_Set.md`](../05_Document_and_Print_Templates/05E_People_Quality_and_Labelling/DT-042_HR_Letter_Template_Set.md) | §7.6 letters | **The letter is not the process** |
| `TR-021` System Administrator course · **`TR-025` statutory induction — unregistered (`O-04`)** | Where this policy is taught and attested | The attestation vehicle |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Legal_Document.md` — ten sections in order; additions declared
- [x] **Twenty acceptable-use rules and ten customer-data rules**, with `DA-10` making unnecessary access itself the breach (`CL-01`)
- [x] **Thirteen monitoring capabilities disclosed, including continuous shift location as the most intrusive** (`CL-02`)
- [x] All 25 relevant `BRU-SEC-*` rules reflected in a term or a monitoring disclosure
- [x] Five breach classes with consequences, and the missing sanction ladder named (`O-05`)
- [x] Personal-device position stated restrictively (§4.7)
- [x] **Bengali disclosure before a technician's first shift stated as a rule** (`MO-R6`)
- [x] All internal links resolve
- [x] Accessibility standard `CG-011` applied
- [ ] **`AU1`–`AU8` answered at G5** — outstanding, blocks `Approved`
- [ ] **`AU2` location-tracking lawfulness confirmed and the Bengali disclosure prepared** — outstanding, `O-02`; blocks `P02` go-live
- [ ] **Sanction ladder created** — outstanding, `O-05`
- [ ] **`TR-025` induction registered** — outstanding, `O-04`; the attestation has no delivery vehicle
- [ ] **Contractor access standard created** — outstanding, `O-08`
- [ ] **Bengali counterpart authored and signed off in context** — outstanding; **this is the version most Users will read**
- [ ] Named approver recorded — pending
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
