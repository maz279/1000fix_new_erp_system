---
id: LG-016
title: Managed Services and Remote Access Consent Terms
project: 1000FiX ERP System v2.0
content_type: Legal / policy
template: TPL_Legal_Document.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Legal & Compliance with Corporate Services
author: Legal & Compliance with Corporate Services, Security and Content Design
reviewers: [Legal Counsel, Chief Data Officer, CTO, Corporate Services Head, Security lead, Localisation Lead, Accessibility reviewer]
approver: Legal Counsel with Corporate Services Head
content_class: B
purpose: >
  The scope of remote access the company takes to a client's or a customer's systems, how consent is
  captured for each session, what is recorded, who may see it, and what the client remains
  responsible for. Remote access to someone else's estate without documented consent is both a legal
  exposure and an insurance exposure, and BRU-RMS-01 makes explicit logged consent a hard rule the
  platform enforces — so the wording that consent is given against has to exist.
traces_to: [M05, M29, M24, M60, M66, P01, P02, P04, LG-001, LG-003, LG-008, LG-009, LG-012, LG-015, LG-017, LG-020, LG-021, DT-030, DT-031, SP-011, UI-042, HC-006, BRU-RMS-01, BRU-RMS-02, BRU-RMS-03, BRU-RMS-04, BRU-RMS-08, BRU-RMS-09, BRU-RMS-10, BRU-RMS-11, BRU-RMS-12, BRU-RMS-13, BRU-SEC-02, BRU-SEC-03, BRU-SEC-11, BRU-SEC-19, BRU-SEC-20, BRU-DTS-14, NFR-097, NFR-098]
priority: P1
wave: W4
bilingual: yes
bn_counterpart: LG-016_Managed_Services_and_Remote_Access_Consent_Terms_BN.md
sources:
  - source: 1000fix_ERP_Module/03_Modules/A_Service_Delivery_and_Operations/M05 §9 BRU-RMS-01 no remote connection without explicit logged customer consent; BRU-RMS-02 unattended access only on assets covered by a contract granting it; BRU-RMS-03 client credentials vaulted and never in a ticket, note or email; BRU-RMS-08 change record with rollback plan; BRU-RMS-09 patching outside an agreed window needs client approval; BRU-RMS-11 offboarding incomplete until agents removed and access revoked, evidenced; BRU-RMS-12 session recordings retained per contract and schedule with access logged; BRU-RMS-13 client portal users see only their own estate
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 P04 managed-services capability set — estate health dashboard, open incidents, alert history, patch compliance, SLA attainment, service reports, scheduled service reviews; P01 booking includes a remote delivery mode; P02 allows a technician to launch a remote support session for eligible jobs
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-SEC-02 sensitive actions require step-up authentication; BRU-SEC-19 privileged access is time-boxed with no standing administrative rights; BRU-SEC-20 break-glass access notifies multiple parties, expires automatically and requires post-hoc justification; BRU-SEC-11 audit entries are insert-only
    verified: 2026-08-18
    class: P1
  - source: project_content/06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-011_SOP_Remote_Support_and_Managed_Services.md — the operating procedure this document supplies the consent basis for
    verified: 2026-08-18
    class: P1
  - source: Personal Data Protection Act 2026 — consent for processing personal data encountered during remote access, and the processor position where the company acts on a client's instruction. **Secondary source; clause-level content unverified, pending G5**
    verified: 2026-08-18
    class: P2
supersedes: none
review_due: 2027-02-18
---

# LG-016 — Managed Services and Remote Access Consent Terms

| Item | Value |
|---|---|
| Document class | **Terms + consent wording** |
| Counterparty | A corporate client under a managed-service contract, **and an individual customer who accepts a remote support session** |
| Governing law | **Bangladesh** |
| Effective date | On publication of version 1.0 — *pending approval* |
| Acceptance capture method | **`AC-5` per-session consent, logged** (`BRU-RMS-01`). **Standing consent for unattended access exists only where a contract grants it** (`BRU-RMS-02`) |
| Version accepted by users | Recorded in `LG-001` per session, with the consent-text version shown |
| External counsel review | **Required** — the §4.3 consent model, the §4.7 recording position and the §5 allocation |
| Bengali version | **Required.** A consumer accepting a remote session on `P01` reads it in Bengali |

> ⚠ **Class B. Two very different counterparties accept this document, and conflating them is the
> mistake to avoid.**
>
> A corporate client grants **standing, unattended, privileged access to an estate** under a
> negotiated contract. An individual customer grants **one attended session on one device** while a
> technician is talking to them. `BRU-RMS-01` covers both with the same hard rule — *"no remote
> connection may be established without explicit, logged customer consent"* — but the consent they
> can meaningfully give is not the same thing.
>
> **§4.3 therefore defines three consent tiers, and §4.4 states what each one does and does not
> authorise.**
>
> **Conformance note.** All ten template sections retained in order. The consent tiers are §4.3 and
> the consent wording §4.4, within §4 Terms. Gate questions and open items are §1.2 and §1.3
> (`CP-09`).

---

## 1. Approval Record

| Role | Name | Date | Evidence |
|---|---|---|---|
| Drafted by | Legal & Compliance with Corporate Services | 2026-08-18 | Draft issue v1.0 |
| G1 Editorial — Content Design | *pending* | | |
| G2 Factual — Corporate Services Head with Security lead | *pending* | | |
| G4 Linguistic — independent reviewer, in context (`BN-018`) | *pending* | | |
| **G5 Legal — Legal Counsel** | *pending* | | **Required** |
| Approved by — Legal Counsel with Corporate Services Head | *pending* | | |

### 1.2 Questions for Legal Counsel (G5)

| # | Question | Why it matters |
|---|---|---|
| **RA1** | Is **standing contractual consent** for unattended access sufficient, or must each session still be individually authorised? `BRU-RMS-02` permits contract-granted unattended access; `BRU-RMS-01` requires explicit logged consent per connection | The two rules can be read as being in tension, and the automation depends on which reading is right |
| **RA2** | May a **client administrator** consent on behalf of the client's employees whose devices are accessed and whose data may be seen? | This is the corporate equivalent of `LG-003` `CO1` delegated authority, applied to something more intrusive than an approval |
| **RA3** | Is **session recording** lawful, and does it require separate consent from access consent? | §4.7. A recording of a client's screen is a copy of the client's data |
| **RA4** | Where a technician **sees personal data** on a client's system during a session, is the company a controller, a processor, or neither? | Determines the §6.2 position and whether a data-subject request can reach the company |
| **RA5** | May the company **refuse** to act on a client instruction it considers unsafe or unlawful, and is it obliged to? | §4.8.5 asserts the right |
| **RA6** | What is the company's exposure where a **change it made** breaks a client's system, and is the §5.4 allocation enforceable? | The core managed-services exposure |
| **RA7** | Is the **§4.9 insurance requirement** on the client enforceable, and does the company's own cover require it? | The register's justification names insurance explicitly |
| **RA8** | For a **consumer** remote session on `P01`, is the §4.4 consumer consent text sufficient, and may a session be recorded at all? | A consumer's device may contain anything |

### 1.3 Open items

| # | Open item | Blocking? | Owner |
|---|---|:--:|---|
| **O-01** | `RA1`–`RA8` unanswered | **Yes — blocks `Approved`** | Legal Counsel |
| **O-02** | **`RA1` is a rule-level tension between `BRU-RMS-01` and `BRU-RMS-02`** and should be resolved in `05-05`, not only here. `CG-013` `T-B03` routes a business-rule question to the rule owner | **Yes — upstream** | CTO with Corporate Services Head |
| **O-03** | **`LG-003` is `W4`, the same wave as this file, and a client administrator grants remote access *through* `P04`.** The two must be reviewed together, or the authority to grant access will rest on a clause in a document that has not been read against this one (`LG-003` `O-04`) | **Yes — sequencing** | Legal Counsel |
| **O-04** | **Session-recording retention is "per the contract and the retention schedule"** (`BRU-RMS-12`). `LG-009` `RC-15` sets 6 months for call recordings; **no row covers a remote-session recording specifically** | **Yes — blocks §4.7** | CDO with Legal |
| **O-05** | **A consumer remote session on `P01` is a booking delivery mode** (`04-00` P01) and a `P02` technician can launch one. **Neither surface has consent copy** — `UI-042` covers privacy and preferences, not session consent | **Yes — blocks the `P01`/`P02` remote path** | Content Design with Legal |
| **O-06** | **`M66` internal IT service management also performs remote support, on employee devices.** That is `LG-020`, not this file, and **the boundary is stated in §2 but not built** | No — boundary declared | CTO |
| **O-07** | **No client-offboarding evidence template exists.** `BRU-RMS-11` requires agents removed and access revoked, **evidenced**; §7 states the requirement with nothing to record it on | Yes | Corporate Services Head |

---

## 2. Scope and Parties

| Party | Identity |
|---|---|
| **The Company** | 1000FiX Services Limited |
| **The Client** | A corporate or government client under a managed-service contract |
| **The Customer** | An individual who accepts a remote support session for their own device |
| **Authorised User** | A named Company technician or engineer permitted to perform remote access |

**In scope:** remote access to a Client's or Customer's systems for support, monitoring,
administration, patching and change; the consent model; monitoring agents; credentials; change
control; recording; and the responsibility boundary.

**Out of scope:**

| Subject | Owned by |
|---|---|
| Service levels, measurement and credits | [`LG-015_AMC_SLA_Master_Terms_and_Service_Credit_Rules.md`](LG-015_AMC_SLA_Master_Terms_and_Service_Credit_Rules.md) |
| Portal access and delegated authority | [`LG-003_Portal_Terms_of_Use_Corporate.md`](LG-003_Portal_Terms_of_Use_Corporate.md) — **`O-03`** |
| **Data recovery from media the Company holds** | [`LG-017_Data_Recovery_and_Secure_Destruction_Terms.md`](LG-017_Data_Recovery_and_Secure_Destruction_Terms.md) — a different service with a different consent |
| **Remote access to the Company's own employees' devices** | [`LG-020_Acceptable_Use_and_Internal_Access_Policy.md`](LG-020_Acceptable_Use_and_Internal_Access_Policy.md) and `M66` — **`O-06`** |
| The Company's own security controls | [`LG-021_ISMS_Policy_Set.md`](LG-021_ISMS_Policy_Set.md) |
| Personal data generally | `LG-008`, `LG-009`, `LG-012` |
| The operating procedure | [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-011_SOP_Remote_Support_and_Managed_Services.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-011_SOP_Remote_Support_and_Managed_Services.md) |

---

## 3. Definitions

| Term | Meaning |
|---|---|
| **Remote access** | Any connection from a Company system to a Client's or Customer's system, whether to view, control, transfer or configure |
| **Attended session** | Access while the Client's or Customer's user is present and watching |
| **Unattended access** | Access without a user present. **Permitted only on assets a contract covers for it** (`BRU-RMS-02`) |
| **Monitoring agent** | Software installed on a Client asset to report health and alerts |
| **Privileged access** | Access with administrative rights. **Time-boxed; no standing administrative rights** (`BRU-SEC-19`) |
| **Break-glass** | Emergency access outside the normal path. **Notifies multiple parties, expires automatically, requires post-hoc justification** (`BRU-SEC-20`) |
| **Change** | Any alteration to a Client environment. **Requires a recorded change record with a rollback plan** (`BRU-RMS-08`) |
| **Session record** | The log of who connected, to what, when, for how long, and what was done |
| **Session recording** | A screen or input capture of the session itself — **distinct from a session record** (§4.7) |
| **Governing text** | The **English** version (`LG-001` `LR-03`) |

---

## 4. Terms

### 4.1 The undertaking

| # | Clause |
|---|---|
| **4.1.1** | The Company accesses a Client's or Customer's systems **only for the purpose the consent covers**, and only to the extent the purpose needs |
| **4.1.2** | Access is by a **named Authorised User**. Shared accounts are not used, and a session is always attributable to a person |
| **4.1.3** | **Privileged access is time-boxed** (`BRU-SEC-19`) and **sensitive actions require step-up authentication** (`BRU-SEC-02`) |
| **4.1.4** | **Every session is logged, and the log is insert-only** (`BRU-SEC-11`) |
| **4.1.5** | The Client or Customer may end a session at any time, and an attended session ends when they say so |

### 4.2 What the Company will not do

| # | Clause |
|---|---|
| **4.2.1** | **Access a system outside the consented scope**, even where it is technically reachable |
| **4.2.2** | **Copy, download or retain Client or Customer data** except as the purpose requires and the consent covers |
| **4.2.3** | **Read personal or private content that is not necessary to the work.** Where it is unavoidably visible, it is not recorded, discussed or repeated |
| **4.2.4** | **Record credentials in a ticket, a note or an email** (`BRU-RMS-03`). Credentials are vaulted |
| **4.2.5** | **Use anything encountered during a session as training data for a model** (compare `BRU-DTS-14`) |
| **4.2.6** | **Make a change outside an agreed window without approval** (`BRU-RMS-09`) |
| **4.2.7** | **Continue a session after consent is withdrawn** |

### 4.3 The three consent tiers

> **`CL-01`. `BRU-RMS-01` requires explicit logged consent for every connection. `BRU-RMS-02` permits
> unattended access where a contract grants it. The tiers below are how both hold at once — subject to
> `RA1` and `O-02`.**

| Tier | Who consents | How | Authorises | Does not authorise |
|---|---|---|---|---|
| **RC-T1 — Session consent** | The **individual present at the device** — a Customer on `P01`, or a Client user | **In-session, affirmative, immediately before connection**, with the session recorded | One attended session, on the named device, for the stated purpose, for its duration | Any later session · unattended access · access to another device |
| **RC-T2 — Contract consent** | The **Client**, through its authorised signatory | The executed managed-service contract, naming the covered estate and the access it grants | **Unattended access to the named covered assets** for monitoring, alerting, patching and support | Access to an asset not in the covered estate · a change outside §4.8 · recording where the contract excludes it |
| **RC-T3 — Emergency access** | Pre-authorised in the contract; **triggered by the Company** | **Break-glass** — multi-party notification, automatic expiry, post-hoc justification (`BRU-SEC-20`) | Access to contain an incident where waiting for a person would cause harm | Anything beyond containment · routine work · use where a person is reachable |

| # | Rule |
|---|---|
| **RC-R1** | **A connection with no tier applying does not happen.** The platform gate is `BRU-RMS-01` |
| **RC-R2** | **`RC-T2` does not remove the log.** Every unattended session is still logged and attributable (§4.1.4) |
| **RC-R3** | **`RC-T2` is scoped to the covered estate register.** An asset added to a Client's estate is not automatically consented — the contract's amendment terms apply |
| **RC-R4** | **`RC-T3` is exceptional and is reported.** Repeated break-glass use is a planning defect, and is raised as one (compare `CG-013` `UR-06`) |
| **RC-R5** | **A Client administrator consenting under `RC-T2` does so on the Client's authority, not the affected employees'** — `RA2`. The Client is responsible for telling its own people |
| **RC-R6** | **Consent is withdrawable.** Withdrawal ends current access and stops future access under that tier |
| **RC-R7** | **The consent-text version shown is recorded with the consent** (`LG-001` `LR-06`, `BRU-CPM-08`) |

### 4.4 The consent wording

> **This is the operative meaning. The in-product strings are `UI-042`'s to hold — `O-05` records
> that they do not yet exist** (`LG-008` `UB-01`…`UB-04` boundary).

**`RC-T1` — attended session, consumer or Client user. Must convey:**

| # | Element |
|---|---|
| 1 | **Who** is connecting — the named technician and that they work for 1000FiX |
| 2 | **What** they will be able to see and do — view the screen, control the device, or both |
| 3 | **Why** — the specific purpose, tied to the service order |
| 4 | **That the session is logged**, and whether it is recorded (§4.7) |
| 5 | **That the person can end it at any time**, and how |
| 6 | **That they should close anything private before agreeing** — the single most useful sentence in the whole consent |
| 7 | **That the technician will not copy or keep their data** (§4.2.2) |
| 8 | An affirmative action to agree. **Not a countdown, not a default** |

**`RC-T2` — contract consent. Must state in the contract:**

| # | Element |
|---|---|
| 1 | The **covered estate** — by site, asset class or named asset |
| 2 | Whether **unattended** access is granted, and to what |
| 3 | Whether **privileged** access is granted, and its time-boxing |
| 4 | The **purposes** — monitoring, alerting, patching, incident response, change |
| 5 | The **maintenance windows** agreed (§4.8.2) |
| 6 | Whether sessions are **recorded**, and the retention |
| 7 | The **named Client contacts** who may vary scope |
| 8 | The **offboarding** obligation (§7) |

### 4.5 Monitoring agents

| # | Clause |
|---|---|
| **4.5.1** | Agents are installed only on covered assets, with the Client's knowledge, and report health, configuration and alert data |
| **4.5.2** | **An agent does not capture user content**, keystrokes or screen contents |
| **4.5.3** | **A covered asset without a healthy agent is reported to the Client as a coverage gap within 24 hours** (`BRU-RMS-04`). **A gap is the Client's risk to accept, not the Company's to absorb silently** |
| **4.5.4** | Agent data is used for the service, for capacity and for problem management, and **is not used to profile the Client's staff** |
| **4.5.5** | Agents are removed at offboarding, evidenced (`BRU-RMS-11`) |

### 4.6 Credentials

| # | Clause |
|---|---|
| **4.6.1** | **Client credentials are vaulted. They are never recorded in a ticket, a note or an email** (`BRU-RMS-03`) |
| **4.6.2** | The Company uses a **dedicated service account** where the Client's environment permits, so activity is attributable |
| **4.6.3** | **The Client is told immediately** if a credential is suspected compromised |
| **4.6.4** | Credentials are removed at offboarding, and the Client is asked to rotate anything the Company held (§7) |

### 4.7 Recording — **pending `RA3`, `RA8`, `O-04`**

| # | Clause |
|---|---|
| **4.7.1** | A **session record** — who, what, when, how long, what was done — is always kept (§4.1.4) |
| **4.7.2** | A **session recording** — screen or input capture — is taken only where the contract provides for it, or where a Customer is told and agrees under `RC-T1` element 4 |
| **4.7.3** | **A recording of a Client's screen is a copy of the Client's data.** It is stored with the same controls as the underlying data, access is logged, and it is retained per the contract and the retention schedule (`BRU-RMS-12`) |
| **4.7.4** | **`O-04`: `LG-009` has no row for a remote-session recording.** Until it does, recording is not switched on by default |
| **4.7.5** | A recording is produced on request to the Client, and to a Customer for their own session, subject to redaction of a third party's data |
| **4.7.6** | **A recording is never used for performance management of the Company's own technician without telling them** — that is `LG-020` |

### 4.8 Change and patching

| # | Clause |
|---|---|
| **4.8.1** | **A change to a Client environment requires a recorded change record with a rollback plan** (`BRU-RMS-08`). No exceptions for small changes |
| **4.8.2** | **Patching outside an agreed maintenance window requires the Client's approval** (`BRU-RMS-09`) |
| **4.8.3** | Emergency change under `RC-T3` is made to contain harm, recorded, and reported to the Client at the earliest opportunity |
| **4.8.4** | **A recurring incident occurring three or more times in a rolling period is linked to a problem record** (`BRU-RMS-10`). **The Client is entitled to be told that the same thing keeps happening** |
| **4.8.5** | **The Company may decline an instruction it considers unsafe, unlawful, or outside the consented scope**, and will say so in writing — `RA5` |
| **4.8.6** | **Entitlement over-consumption is billed or escalated for uplift; it is never absorbed silently** (`BRU-RMS-07`) |

### 4.9 What the Client remains responsible for

| # | Clause |
|---|---|
| **4.9.1** | **Its own backups.** The Company's access does not make the Company the Client's backup |
| **4.9.2** | Licensing of the Client's own software, and the lawfulness of what is on its systems |
| **4.9.3** | **Telling its own staff** that the estate is monitored and may be accessed remotely — `RA2`, `RC-R5` |
| **4.9.4** | Keeping the covered estate register accurate (`LG-003` §4.4) |
| **4.9.5** | **Its own insurance** for its systems and data — `RA7` |
| **4.9.6** | Acting on a coverage gap the Company reports under §4.5.3 |
| **4.9.7** | Not sharing Company-issued access with a third party |

### 4.10 Client visibility

**A Client portal user sees only their own organisation's estate, tickets and reports**
(`BRU-RMS-13`, `EA-03`). Estate health, open incidents, alert history, patch compliance and SLA
attainment are visible in `P04`. **The Client can see the session log for its own estate**, which is
the transparency that makes standing consent tolerable.

---

## 5. Liability, Exclusions and Limits

| # | Clause |
|---|---|
| **5.1** | The Company is liable for loss caused by its failure to exercise reasonable skill and care during remote access |
| **5.2** | **The Company is not liable for loss arising from access it was instructed to make within the consented scope**, where it followed §4.8 |
| **5.3** | The Company is not liable for a pre-existing fault, an unsupported configuration, or a system the Client has not maintained |
| **5.4** | **Where a change the Company made causes loss, liability is limited to reversing the change under its rollback plan and re-performing the work** — provisional pending `RA6`, and superseded by the executed contract's liability regime (`LG-003` §2.2) |
| **5.5** | **The Company is not the Client's backup** (§4.9.1). Liability for data the Client did not back up is limited accordingly — provisional pending `RA6` |
| **5.6** | For a **consumer** remote session, `LG-013` §5 and `LG-014` apply, and **nothing here reduces a consumer right** |
| **5.7** | Nothing limits liability that cannot lawfully be limited, including for a statutory data-protection liability |
| **5.8** | **Break-glass access under `RC-T3` is not a liability shelter.** The Company remains accountable for what it did during it |

---

## 6. Data Protection

> Must reconcile with `LG-008`, `LG-009`, `LG-012`. Check **F6**.

| # | Clause |
|---|---|
| **6.1** | Session consent, session records and recordings are processed under `LG-008` `CN-05` and `P-08`, and for a consumer session under `P-01` |
| **6.2** | **Where the Company encounters personal data on a Client's system, it does so as the Client's processor**, on the Client's instruction, with equivalent obligations flowing by `LG-003` §6.2 and `NFR-098` — **subject to `RA4`** |
| **6.3** | **The Company does not copy or retain what it sees** (§4.2.2, §4.2.3). The less it holds, the less there is to answer for |
| **6.4** | Session records are retained per `LG-009` `RC-22` — 5 years, aligned to the processing-record minimum. **Session recordings need their own row — `O-04`** |
| **6.5** | **Access to a session recording is logged** (`BRU-RMS-12`), and recordings are restricted data |
| **6.6** | **Remote access performed from outside Bangladesh is a cross-border transfer** even where nothing is copied (`LG-012` `RD-R9`, `TR-07`), and requires a registered basis before it occurs |
| **6.7** | A breach affecting a Client's data encountered during a session is reported to the Client immediately, and to the Authority where the threshold is met (`NFR-094`) |
| **6.8** | **Nothing encountered during a session is used as model training or retrieval data** (§4.2.5) |

---

## 7. Termination and Consequences

| Event | Consequence |
|---|---|
| **A session ends** | Access closes; the session record is retained; a recording is retained per §4.7 |
| **Consent is withdrawn** | Access stops immediately; no further session under that tier |
| **Contract ends** | **Offboarding is not complete until every agent is removed and every access revoked, evidenced** (`BRU-RMS-11`) — **`O-07`: nothing exists to record that evidence on** |
| **Offboarding** | Credentials removed; the Client asked to rotate anything the Company held (§4.6.4); session records and recordings retained per `LG-009` |
| **Breach of §4.2 by an Authorised User** | Access revoked; investigated as a security incident under `LG-021`; **disciplinary consequences under `LG-020`** |
| **Suspicion of unlawful content on a Client system** | Handled per `LG-017` §4.8, which sets the position for unlawful content the Company encounters |
| **In every case** | §4.2 obligations, §6 and the retention position survive |

---

## 8. Dispute Resolution

| Step | Route |
|---|---|
| **1 — Session dispute** | The account manager, **with the session log produced**. The log governs |
| **2 — Change dispute** | The change record and its rollback plan (`BRU-RMS-08`); then the Corporate Services Head |
| **3 — Security concern** | Handled as an incident under `LG-021`, not as a commercial dispute |
| **4 — Consumer route** | `SP-028` complaint, then the DNCRP — unconditional |
| **5 — Formal** | Per the executed contract; where silent, arbitration in Dhaka under the Arbitration Act 2001 |
| **6 — Courts** | The courts of Dhaka, Bangladesh |

---

## 9. Change Control

| Version | Date | Change | Notice given to users | Re-acceptance required |
|---|---|---|---|:--:|
| 1.0 | 2026-08-18 | Initial issue — draft for G5. Three consent tiers established | n/a | n/a |

| # | Rule |
|---|---|
| **9.1** | A change to a consent tier, to §4.2, to §4.7 recording or to §5 is **MAJOR** |
| **9.2** | **A change to `RC-T1` wording requires the `UI-042` strings to change in the same release**, and the consent-text version is recorded with each new consent |
| **9.3** | A change to `RC-T2` requires a contract amendment, not a policy republication |
| **9.4** | **`RA1`'s answer is MAJOR and may be resolved in `05-05` rather than here** (`O-02`) |

---

## 10. Cross-References

| Document | Relationship | Must not contradict |
|---|---|---|
| [`LG-003_Portal_Terms_of_Use_Corporate.md`](LG-003_Portal_Terms_of_Use_Corporate.md) | §4.8 refers here; **`RC-T2` authority rests on its §4.3** | **`O-03` — review together** |
| [`LG-015_AMC_SLA_Master_Terms_and_Service_Credit_Rules.md`](LG-015_AMC_SLA_Master_Terms_and_Service_Credit_Rules.md) | Managed-service SLA, coverage window, entitlement | `BRU-RMS-05`, `BRU-RMS-07` |
| [`LG-017_Data_Recovery_and_Secure_Destruction_Terms.md`](LG-017_Data_Recovery_and_Secure_Destruction_Terms.md) | §7 unlawful content; a different service | The confidentiality and unlawful-content position |
| [`LG-020_Acceptable_Use_and_Internal_Access_Policy.md`](LG-020_Acceptable_Use_and_Internal_Access_Policy.md) | §4.7.6, §7 disciplinary route; **`O-06` internal remote support** | Monitoring of Company staff |
| [`LG-021_ISMS_Policy_Set.md`](LG-021_ISMS_Policy_Set.md) | §4.6 vaulting, §8 step 3 incidents | Credential and incident policy |
| [`LG-008_Privacy_Notice_and_Consent_Copy.md`](LG-008_Privacy_Notice_and_Consent_Copy.md) · [`LG-009_Data_Retention_and_Deletion_Schedule.md`](LG-009_Data_Retention_and_Deletion_Schedule.md) · [`LG-012_Cross_Border_Data_Transfer_and_Residency_Statement.md`](LG-012_Cross_Border_Data_Transfer_and_Residency_Statement.md) | §6 | Check **F6**; `TR-07` remote access as a transfer |
| [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-011_SOP_Remote_Support_and_Managed_Services.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-011_SOP_Remote_Support_and_Managed_Services.md) | **Operates every clause here** | Consent capture at the point of connection |
| [`../03_UI_Copy_and_Microcopy/03D_Critical_Flows/UI-042_Consent_Privacy_and_Preference_Centre_Copy.md`](../03_UI_Copy_and_Microcopy/03D_Critical_Flows/UI-042_Consent_Privacy_and_Preference_Centre_Copy.md) | **Should hold the `RC-T1` strings — `O-05`: it does not yet** | §4.4 meaning |
| `HC-006` Help Set `P04` · `HC-003` Help Set `P01` · `TR-021` administrator course | Explain the consent and the session | No help may imply access wider than the tier grants |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Legal_Document.md` — ten sections in order; additions declared
- [x] **Three consent tiers defined, reconciling `BRU-RMS-01` with `BRU-RMS-02`** (`CL-01`), with the tension raised upstream (`O-02`)
- [x] **Consent wording specified as required elements rather than drafted strings**, respecting the `UI-042` boundary
- [x] Seven explicit prohibitions in §4.2, including no model training and no credentials in tickets
- [x] Session record and session recording **distinguished**, with recording off by default pending a retention row
- [x] Client responsibilities stated, including that the Company is not the Client's backup
- [x] Remote access from outside Bangladesh identified as a cross-border transfer (§6.6)
- [x] All internal links resolve
- [ ] **`RA1`–`RA8` answered at G5** — outstanding, blocks `Approved`
- [ ] **`BRU-RMS-01`/`BRU-RMS-02` tension resolved in `05-05`** — outstanding, `O-02`
- [ ] **Session-recording retention row added to `LG-009`** — outstanding, `O-04`
- [ ] **`RC-T1` consent copy authored in `UI-042`** — outstanding, `O-05`; the `P01`/`P02` remote path has no consent text
- [ ] **Offboarding evidence template created** — outstanding, `O-07`
- [ ] **Bengali counterpart authored and signed off in context** — outstanding
- [ ] Named approver recorded — pending
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
