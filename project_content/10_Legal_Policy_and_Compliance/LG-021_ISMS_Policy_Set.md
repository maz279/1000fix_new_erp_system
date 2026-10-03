---
id: LG-021
title: ISMS Policy Set
project: 1000FiX ERP System v2.0
content_type: Legal / policy
template: TPL_Legal_Document.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: CTO with Legal & Compliance
author: Security lead with the CTO, Legal & Compliance and Enterprise Architecture
reviewers: [CTO, Legal Counsel, Chief Data Officer, Quality Manager, CFO delegate, Enterprise Architect, Internal IT, external security assessor]
approver: CTO with Legal Counsel
content_class: B
purpose: >
  The human-facing information security policy suite — access, cryptography, supplier security,
  incident, continuity, classification and the rest — that sits opposite the NFRs in 05-06 and is the
  artefact a certification body, an enterprise client and an insurer actually ask to see. The platform
  enforces controls; a policy set is what states who owns them, what standard they meet, and how their
  operation is evidenced.
traces_to: [05-06 §4, NFR-025, NFR-089, NFR-094, NFR-097, NFR-098, M29, M60, M66, M24, M62, M28, LG-001, LG-008, LG-009, LG-010, LG-012, LG-016, LG-017, LG-019, LG-020, LG-022, LG-024, MD-002, SP-006, SP-031, TS-017, OP-004, BRU-SEC-01, BRU-SEC-02, BRU-SEC-03, BRU-SEC-04, BRU-SEC-05, BRU-SEC-06, BRU-SEC-07, BRU-SEC-08, BRU-SEC-09, BRU-SEC-10, BRU-SEC-11, BRU-SEC-12, BRU-SEC-13, BRU-SEC-14, BRU-SEC-15, BRU-SEC-16, BRU-SEC-17, BRU-SEC-18, BRU-SEC-19, BRU-SEC-20, BRU-SEC-21, BRU-SEC-22, BRU-SEC-23, BRU-SEC-24, BRU-SEC-25, BRU-GRC-11, BRU-GRC-13, FR-GRC-011, FR-GRC-029, FR-GRC-036, FR-GRC-043]
priority: P1
wave: W2
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M29 §9 BRU-SEC-01 … BRU-SEC-25 — the twenty-five platform security rules this policy set is the human-facing counterpart of
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 §4 Security, §6.2 NFR-025 ISO 27001 security control alignment and NFR-089 SOC 2 / ISO 27001 readiness for enterprise and multi-country expansion, §6.3 NFR-094 breach notification to the National Data Management Authority, NFR-097 technical and organisational measures proportionate to risk, NFR-098 processor and sub-processor flow-down
    verified: 2026-08-12
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M60 §5.2 FR-GRC-011 control register with objective, type, nature, frequency and owner; §5.3 FR-GRC-029 policy library controlled through M24; §5.4 FR-GRC-036 breach register and response, FR-GRC-043 continuity and disaster-recovery governance; §9 BRU-GRC-11 M60 defines and tests controls but never enforces them at runtime
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02 §10 data classification S0 public, S1 internal, S2 confidential, S3 restricted, with the S3 field inventory and per-class controls
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04 §4 isolation tiers T0 to T5, §5 field-level permissions, §6 segregation of duties SOD-01 to SOD-12, §9 access lifecycle
    verified: 2026-08-18
    class: P1
  - source: ISO/IEC 27001:2022 — the information security management system standard `05-06` NFR-025 and NFR-089 align to. Cited as a standard, not as a certification held; the company holds ISO 9001:2015 and no ISO 27001 certificate is recorded in the repository
    verified: 2026-08-18
    class: P2
  - source: Cyber Security Ordinance 2025 — in force 21 May 2025 per `05-06` §6.1, establishing critical-information-infrastructure provisions and a national incident-response structure. **Secondary source; whether the company is designated critical information infrastructure is unverified and is pending G5, and it is the same question as LG-012 RD3**
    verified: 2026-08-18
    class: P2
supersedes: none
review_due: 2027-02-18
---

# LG-021 — ISMS Policy Set

| Item | Value |
|---|---|
| Document class | **Policy suite** — twelve policies in one registered file |
| Counterparty | Employees and contractors; **shown to certification bodies, enterprise clients, brand partners and insurers** |
| Governing law | **Bangladesh** |
| Effective date | On publication of version 1.0 — *pending approval* |
| Acceptance capture method | **`AC-4` attestation by the named population** per policy (`FR-GRC-030`), at `AL-2` (`LG-019` §4.5) |
| Version accepted by users | Recorded in `LG-001`; attestation per person per policy version |
| External counsel review | **Required** — the `CS1` critical-infrastructure question and the §4.10 breach-notification position |
| Bengali version | **Not required** (`CG-010` §3.2 — internal policy set, audited in English) |

> ⚠ **Class B, and the file most often mistaken for paperwork.**
>
> `05-06` §4 and `M29` already give the platform **twenty-five hard security rules**. So what is this
> for? **Three things a control cannot do:**
>
> 1. **Name an owner.** `BRU-GRC-11` is explicit: *"`M60` defines and tests controls; it never enforces
>    them at runtime."* A control with no named owner is a control nobody maintains.
> 2. **Cover what no code enforces** — supplier security, physical access, continuity, awareness,
>    classification handling by people.
> 3. **Be the artefact that is audited.** `NFR-089` commits to **SOC 2 / ISO 27001 readiness for
>    enterprise and multi-country expansion**, and a readiness claim with no policy set is a claim
>    with nothing behind it.
>
> **Conformance note.** All ten template sections retained in order. The twelve policies are §4.2–§4.13
> within §4 Terms — a **declared adaptation**, because the register allocates one file to a suite.
> `AUDIT-008` KB-10, `AUDIT-009` TR-11 and `AUDIT-010` HC-11 each recorded a similar template
> adaptation; this is a fourth instance and is reported as such (`O-08`).

---

## 1. Approval Record

| Role | Name | Date | Evidence |
|---|---|---|---|
| Drafted by | Security lead with the CTO | 2026-08-18 | Draft issue v1.0 |
| G1 Editorial — Content Design | *pending* | | |
| G2 Factual — CTO with Enterprise Architecture and Internal IT | *pending* | | |
| **G5 Legal — Legal Counsel** | *pending* | | **Required** |
| Approved by — CTO with Legal Counsel | *pending* | | |

### 1.2 Questions for Legal Counsel and the external assessor (G5)

| # | Question | Why it matters |
|---|---|---|
| **CS1** | **Is the company designated critical information infrastructure** under the Cyber Security Ordinance 2025, or does it process for an entity that is? | It imports a distinct regulatory regime, incident-reporting duties, and **`LG-012` `RD2`'s synchronised in-country copy requirement.** Same question as `LG-012` `RD3` |
| **CS2** | **What incident must be reported, to whom, and how quickly** — to the national response structure, to the National Data Management Authority (`NFR-094`), to a client, to a brand partner, to an insurer? **Four different clocks** | §4.10; `LG-008` `PN3` asks the data-protection half |
| **CS3** | **Does the company claim ISO 27001 alignment, readiness, or certification?** `NFR-025` says alignment; `NFR-089` says readiness. **Neither is certification, and the difference matters in a tender** | §4.1.4; `CG-013` `T-A13` |
| **CS4** | **What must a supplier-security clause require** to satisfy `NFR-098` flow-down, and is the `LG-006` §6 wording sufficient? | §4.8 |
| **CS5** | **Is a mandatory disclosure of a vulnerability to an affected client contractually required**, and on what timescale? | §4.10.6 |
| **CS6** | **Can the company lawfully retain access logs for 5 years** where they contain employee personal data, and is that proportionate? | `LG-009` `RC-22`; `LG-020` `MO-R4` |

### 1.3 Open items

| # | Open item | Blocking? | Owner |
|---|---|:--:|---|
| **O-01** | `CS1`–`CS6` unanswered | **Yes — blocks `Approved`** | CTO with Legal Counsel |
| **O-02** | **`CS1` is unresolved in two files.** `LG-012` `RD3` asks it from the residency side; this file asks it from the security side. **It is one question with two consequences and needs one answer** | **Yes** | CTO |
| **O-03** | **No ISO 27001 certificate is recorded anywhere in the repository.** The company holds **ISO 9001:2015** (`LG-022`). **§4.1.4 must state alignment or readiness and not imply certification** — `CS3` | **Yes — a claim risk** | CTO with Brand lead |
| **O-04** | **No control register exists.** `FR-GRC-011` provides one in `M60`, undelivered. **§4.14 maps policies to controls and cannot name control identifiers that do not exist** | **Yes** | CTO |
| **O-05** | **No named security owner is recorded.** Every `BRU-SEC-*` rule names the **CTO** as owner, which is accountability rather than operational ownership for twenty-five controls plus twelve policies | **Yes** | CEO with CTO |
| **O-06** | **This file is `W2`; `LG-020` is `W1` and references these controls** (`LG-020` `O-03`). **The same wave-sequencing shape found in four consecutive audits** | **Yes — sequencing** | Programme Content Lead |
| **O-07** | **No continuity or disaster-recovery plan exists.** `FR-GRC-043` governs it at `P2`; §4.11 states the policy with **no plan, no recovery objectives and no test evidence behind it** | **Yes — an enterprise client will ask** | CTO |
| **O-08** | **Fourth template adaptation.** `TPL_Legal_Document.md` is designed for one instrument; this is a suite of twelve. **`AUDIT-008` R-05, `AUDIT-009` R-09 and `AUDIT-010` R-10 each recommended a specification variant, three times. This is a fourth category needing it** | No — contained by declaration | Content Design |
| **O-09** | **No penetration test, vulnerability scan or assessment evidence exists**, and `BRU-SEC-21` escalates a critical vulnerability open beyond 7 days to the CTO and the board. **The rule presumes a discovery mechanism** | **Yes** | CTO |

---

## 2. Scope and Parties

**In scope:** twelve information-security policies covering governance, classification, access,
cryptography, operations, development, supplier security, physical security, incident response,
continuity, awareness and compliance; their owners; and how their operation is evidenced.

**Out of scope:**

| Subject | Owned by |
|---|---|
| **The testable requirements** | `05-06` §4 and §6 — **this set is the human-facing counterpart, not a restatement** |
| The platform rules | `M29` §9 `BRU-SEC-01`…`BRU-SEC-25` — **referenced, never contradicted** |
| **What a User may and may not do** | [`LG-020_Acceptable_Use_and_Internal_Access_Policy.md`](LG-020_Acceptable_Use_and_Internal_Access_Policy.md) — **`O-06`** |
| Personal-data obligations | `LG-008`, `LG-009`, `LG-010`, `LG-012` |
| Client remote access | [`LG-016_Managed_Services_and_Remote_Access_Consent_Terms.md`](LG-016_Managed_Services_and_Remote_Access_Consent_Terms.md) |
| Data-services case controls | [`LG-017_Data_Recovery_and_Secure_Destruction_Terms.md`](LG-017_Data_Recovery_and_Secure_Destruction_Terms.md) §4.3 |
| Quality management system | [`LG-022_Quality_Policy_and_ISO_9001_Statement_Set.md`](LG-022_Quality_Policy_and_ISO_9001_Statement_Set.md) |
| Regulatory obligations register | [`LG-024_Regulatory_Disclosure_and_Statutory_Notice_Register.md`](LG-024_Regulatory_Disclosure_and_Statutory_Notice_Register.md) |
| Runbooks and operational procedure | `OP-*`; `SP-031` |
| Security test procedures | `TS-017` |

---

## 3. Definitions

| Term | Meaning |
|---|---|
| **ISMS** | The information security management system — the policies, controls, owners and evidence taken together |
| **Classification** | `S0` public, `S1` internal, `S2` confidential, `S3` restricted (`05-02` §10) |
| **Isolation tier** | `T0`…`T5` record visibility (`05-04` §4) |
| **Control** | A measure that reduces a risk, with an owner, a type, a frequency and evidence (`FR-GRC-011`) |
| **Incident** | An event that has or may have compromised confidentiality, integrity or availability |
| **Breach** | An incident involving personal data, assessed under `LG-008` §4.8 |
| **Recovery objective** | The maximum acceptable data loss and downtime for a service — **not yet set (`O-07`)** |
| **Alignment** | Designing to a standard's controls. **Not certification** — `CS3` |

---

## 4. Terms

### 4.1 IS-01 — Information Security Policy (the governing policy)

| # | Clause | Owner |
|---|---|---|
| **4.1.1** | The company protects the confidentiality, integrity and availability of the information it holds, **proportionate to risk** (`NFR-097`) | CTO |
| **4.1.2** | Security is designed in, not added. **No module implements its own authentication, session handling or permission engine** (`BRU-SEC-09`), and **every authorisation decision is evaluated server-side on every request; no client or gateway assertion is trusted** (`BRU-SEC-10`) |  |
| **4.1.3** | **`M60` defines and tests controls; it never enforces them at runtime** (`BRU-GRC-11`). **Enforcement is the platform's; ownership is a person's** |  |
| **4.1.4** | **The company designs to ISO/IEC 27001 control alignment** (`NFR-025`) and commits to **SOC 2 / ISO 27001 readiness** for enterprise and multi-country expansion (`NFR-089`). **It does not hold an ISO 27001 certificate, and no document may imply that it does** — `CS3`, `O-03` |  |
| **4.1.5** | Every policy in this set has a **named owner, a named population, an attestation cycle and a review date** |  |
| **4.1.6** | **A control asserted as operating without evidence is a deficiency, not a pass** (`BRU-GRC-07`) |  |

### 4.2 IS-02 — Information Classification and Handling

| # | Clause |
|---|---|
| **4.2.1** | Every field is classified `S0`…`S3` (`05-02` §10). **Classification drives encryption, masking, access logging and retention** |
| **4.2.2** | **`S3` restricted** — National ID, bank details, individual payroll, recovered customer data, call recordings, biometric templates, seller KYC documents, customer identity documents, integration credentials — requires **field-level encryption, explicit grant, step-up authentication, full access logging and retention enforcement** |
| **4.2.3** | **`S3` fields are encrypted at field level with key material separate from the database key** (`BRU-SEC-15`) |
| **4.2.4** | **Classified fields are redacted from logs at emission** (`BRU-SEC-24`). Not filtered later — at emission |
| **4.2.5** | **Residency-classified fields are written only to the Bangladesh-resident store; a write to the regional store fails** (`BRU-SEC-13`, `LG-012` `RD-R2`) |
| **4.2.6** | Handling by people follows `LG-020` §4.4; **the classification is what tells a person which rule applies** |
| **Owner** | Chief Data Officer with Enterprise Architecture |

### 4.3 IS-03 — Access Control

| # | Clause |
|---|---|
| **4.3.1** | Access is role-based, least-privilege, and granted through the `05-04` model with `T0`…`T5` isolation |
| **4.3.2** | **MFA at every login** for admin, finance and HR access (`BRU-SEC-01`); **step-up authentication for sensitive actions** (`BRU-SEC-02`) |
| **4.3.3** | **Privileged access is time-boxed; no standing administrative rights** (`BRU-SEC-19`) |
| **4.3.4** | **Break-glass notifies multiple parties, expires automatically, and requires post-hoc justification** (`BRU-SEC-20`) |
| **4.3.5** | **A user may not administer or approve their own access** (`BRU-SEC-18`, `SOD-09`) |
| **4.3.6** | **Incompatible duties cannot be assigned; an exception is time-boxed, approved by the CFO or CTO, and reported quarterly** (`BRU-SEC-07`, `BRU-GRC-10`, `SP-006`) |
| **4.3.7** | **Access is recertified; unconfirmed access is revoked automatically** (`BRU-SEC-16`) |
| **4.3.8** | **No account exists without an active accountable owner for more than 24 hours** (`BRU-SEC-17`) |
| **4.3.9** | **A leaver's access is revoked within one hour, and a revocation takes effect estate-wide within 60 seconds** (`BRU-SEC-06`, `BRU-SEC-25`) |
| **4.3.10** | **Data-recovery case access is limited to the assigned team and every access is logged** (`BRU-SEC-03`, `BRU-DTS-02`) |
| **Owner** | CTO, operationally the IT Administrator |

### 4.4 IS-04 — Cryptography and Key Management

| # | Clause |
|---|---|
| **4.4.1** | Data is encrypted in transit and at rest |
| **4.4.2** | **`S3` fields are encrypted at field level with separate key material** (`BRU-SEC-15`) |
| **4.4.3** | **Recovered customer data is encrypted with a case-specific key** (`BRU-DTS-05`), and **purge is by destruction of that key** (`LG-009` `DM-3`) |
| **4.4.4** | **Keys for residency-restricted data are held in Bangladesh** (`LG-012` `RD-R5`) — subject to `LG-012` `RD8` |
| **4.4.5** | Keys are rotated on a defined cycle, and key access is logged and separated from data access |
| **4.4.6** | **Algorithm agility is required.** A hash or cipher chosen today must be replaceable — **and `LG-019` `O-07` records that no re-sealing policy exists for signatures, which is the same problem** |
| **Owner** | CTO with Security lead |

### 4.5 IS-05 — Operations Security

| # | Clause |
|---|---|
| **4.5.1** | **Audit entries are insert-only and cannot be modified or deleted by any role, including administrators** (`BRU-SEC-11`); **every change to a controlled object is audited by the platform, not by module code** (`BRU-SEC-12`) |
| **4.5.2** | **Every file upload is malware-scanned before it is stored or served** (`BRU-SEC-22`) |
| **4.5.3** | **Production data in non-production must be masked** (`BRU-SEC-08`), and **no unmasked residency-classified data exists in non-production in any region** (`NFR-086c`) |
| **4.5.4** | **A critical vulnerability open for more than 7 days is escalated to the CTO and reported to the board** (`BRU-SEC-21`) — **`O-09`: the discovery mechanism the rule presumes does not exist** |
| **4.5.5** | **Bulk personal-data export requires approval and is logged** (`BRU-SEC-05`) |
| **4.5.6** | Change management follows `SP-031`; a production change has a rollback path |
| **Owner** | CTO with Internal IT |

### 4.6 IS-06 — Secure Development

| # | Clause |
|---|---|
| **4.6.1** | Security requirements are specified before build — `05-06` §4 and §6 are those requirements |
| **4.6.2** | **No business rule is implemented client-side; the client validates for convenience only** (`PS-11`) |
| **4.6.3** | Code is reviewed; **financial calculations carry 100% test coverage** (`05-06` §7) |
| **4.6.4** | Dependencies are inventoried and monitored for vulnerabilities |
| **4.6.5** | **`TS-017` verifies access control, data-scope isolation, consent enforcement, residency and audit-log completeness.** A residency rule not tested is a residency rule not enforced (`LG-012` `O-06`) |
| **4.6.6** | Secrets are vaulted, never in source, never in a ticket (`BRU-RMS-03`) |
| **Owner** | CTO with the delivery leads |

### 4.7 IS-07 — Physical and Environmental Security

| # | Clause |
|---|---|
| **4.7.1** | Branch, warehouse and office access is controlled, and visitors are recorded |
| **4.7.2** | **The data-services secure area requires two distinct authenticated signatures for media entering or leaving** (`BRU-DTS-01`) |
| **4.7.3** | **Batteries are stored only in designated locations within the quantity ceiling** (`BRU-ESG-07`) — a safety and a security control |
| **4.7.4** | Paper originals are registered with location, custody and condition (`FR-DMS-013`) |
| **4.7.5** | Devices in custody are the subject of `LG-013` §4.8, and custody is recorded at every handover |
| **4.7.6** | CCTV, where operated, is disclosed under `LG-020` §4.6 and retained per `LG-009` `RC-25` |
| **Owner** | Facilities with Quality Manager; secure area — Technical Services Head |

### 4.8 IS-08 — Supplier and Third-Party Security — **pending `CS4`**

| # | Clause |
|---|---|
| **4.8.1** | **Suppliers, sellers, partners and data processors are risk-rated, with due diligence proportionate to the rating and periodic reassessment** (`FR-GRC-042`) — **`LG-006` `O-04` records that the tiers are undefined** |
| **4.8.2** | **Equivalent obligations flow to every processor and sub-processor by contract** (`NFR-098`, `BRU-GRC-18`) |
| **4.8.3** | **A processor's processing is the company's own.** Contracting transfers no responsibility (`LG-012` `RD-R8`) |
| **4.8.4** | **A sub-processor that will not accept equivalent obligations is not engaged** (`LG-012` §4.6.3) |
| **4.8.5** | The sub-processor register is `LG-012` §4.6 — **`LG-012` `O-05`: it does not exist** |
| **4.8.6** | **A supplier incident affecting company or customer data must be reported immediately**, and the flow-down clauses in `LG-004` §4.7.5, `LG-005` §6.6, `LG-006` §6.5 and `LG-007` §6.4 all say so |
| **Owner** | CTO with Procurement Manager |

### 4.9 IS-09 — Communications and Network Security

| # | Clause |
|---|---|
| **4.9.1** | **All API traffic passes through the gateway with per-portal credentials and rate limits** (`PS-02`) |
| **4.9.2** | **External API scope is set by credential and cannot be widened by request parameter** (`EA-11`) |
| **4.9.3** | **External sessions time out after 30 minutes; MFA is mandatory for any external action with financial consequence** (`EA-08`, `EA-09`) |
| **4.9.4** | **Bulk export by an external party is limited, rate-controlled and logged** (`EA-12`) |
| **4.9.5** | Networks are segmented; branch networks do not reach production data stores directly |
| **Owner** | CTO with Internal IT |

### 4.10 IS-10 — Incident Response — **pending `CS2`**

| # | Clause |
|---|---|
| **4.10.1** | **A breach register records assessment, containment, notification decision and evidence — including contractual notifications where statute is silent** (`FR-GRC-036`) |
| **4.10.2** | **Four notification clocks may run at once**, and they are different: |
| | **(a)** the **National Data Management Authority**, where a breach is likely to cause significant damage (`NFR-094`) — **timeframe is `LG-008` `PN3`** |
| | **(b)** the **national cyber incident-response structure**, if the company is critical information infrastructure — **`CS1`** |
| | **(c)** **affected data subjects**, where the risk to them requires it (`LG-008` §4.8) |
| | **(d)** **clients, brand partners and insurers**, per contract |
| **4.10.3** | **The clock starts at detection**, and a decision not to notify is recorded with its reasoning |
| **4.10.4** | **A breach affecting a data-services case is assessed and notified where the threshold is met** (`BRU-DTS-17`) |
| **4.10.5** | **A breached obligation is recorded, assessed and escalated; it is never quietly closed** (`BRU-GRC-13`) |
| **4.10.6** | **A vulnerability affecting a client is disclosed to that client** — `CS5` |
| **4.10.7** | Incident templates are `OP-004`; **the template is not the process** |
| **4.10.8** | **A User must report a suspected incident immediately** (`LG-020` `AU-17`), and reporting one is never penalised |
| **Owner** | CTO with the Chief Data Officer for personal-data breaches |

### 4.11 IS-11 — Business Continuity and Disaster Recovery — **`O-07`: policy without a plan**

| # | Clause |
|---|---|
| **4.11.1** | **Continuity and disaster-recovery plans are maintained with dependencies, recovery objectives, a test schedule and test evidence** (`FR-GRC-043`) |
| **4.11.2** | **`O-07`: no plan, no recovery objectives and no test evidence exist.** This clause states the requirement and the gap together, as `CG-012` `EX-01` requires |
| **4.11.3** | **Availability is committed at ≥ 99.9% during Bangladesh business hours 09:00–22:00** (`NFR-006`) — **which is an availability target, not a recovery objective, and the two are routinely confused** |
| **4.11.4** | **A manual fallback exists for branch operations** (`OP-014` is registered for it). **51+ branches cannot stop because a system is down** |
| **4.11.5** | A plan is tested, and **an untested plan is not a plan** |
| **Owner** | CTO with the COO |

### 4.12 IS-12 — Security Awareness

| # | Clause |
|---|---|
| **4.12.1** | Every User completes security awareness training at induction and annually |
| **4.12.2** | **Role-specific training for administrators** is `TR-021`; administrators *"hold the most destructive permissions in the platform"* |
| **4.12.3** | Awareness covers phishing, credential handling, classification, incident reporting and the `LG-020` §4.4 data-access rule |
| **4.12.4** | **`LG-020` `O-04` applies here too: `TR-025` statutory induction is unregistered**, so the delivery vehicle for §4.12.1 does not exist |
| **Owner** | CTO with Learning & Development |

### 4.13 IS-13 — Compliance and Assurance

| # | Clause |
|---|---|
| **4.13.1** | Controls are registered with objective, type, nature, frequency and owner (`FR-GRC-011`) — **`O-04`: the register does not exist** |
| **4.13.2** | **Controls whose evidence is in the ERP are tested by query, continuously** (`FR-GRC-014`); manual controls are tested by sample (`FR-GRC-015`) |
| **4.13.3** | **A control owner cannot record the test conclusion for their own control** (`BRU-GRC-06`) |
| **4.13.4** | **A deficiency cannot be closed without a passed retest** (`BRU-GRC-08`) |
| **4.13.5** | **Every SoD rule is tested at least once per cycle, including by controlled violation attempt** (`BRU-GRC-09`) |
| **4.13.6** | **`O-09`: no vulnerability scanning, penetration testing or assessment evidence exists**, while `BRU-SEC-21` presumes discovery |
| **4.13.7** | Regulatory obligations are tracked in `LG-024`; **security obligations are a subset and are not separately registered** |
| **Owner** | CTO with the CFO for control testing |

### 4.14 Policy-to-control map

| Policy | Enforced by | Evidence | Owner |
|---|---|---|---|
| `IS-01` Governing | `BRU-SEC-09`, `BRU-SEC-10`, `BRU-GRC-11` | Policy attestation; control register | CTO |
| `IS-02` Classification | `BRU-SEC-13`, `BRU-SEC-15`, `BRU-SEC-24` | Field classification in the data model; `TS-017` | CDO |
| `IS-03` Access | `BRU-SEC-01`, `-02`, `-06`, `-07`, `-16`…`-20`, `-25` | Access logs; recertification records; SoD tests | CTO |
| `IS-04` Cryptography | `BRU-SEC-15`, `BRU-DTS-05` | Key-management records; rotation logs | CTO |
| `IS-05` Operations | `BRU-SEC-05`, `-08`, `-11`, `-12`, `-21`, `-22` | Audit entries; scan results; masking checks | CTO |
| `IS-06` Development | `PS-11`; `05-06` §7 | Code review; `TS-017` results | CTO |
| `IS-07` Physical | `BRU-DTS-01`, `BRU-ESG-07` | Access records; secure-area signatures | Facilities |
| `IS-08` Supplier | `NFR-098`, `BRU-GRC-18`, `FR-GRC-042` | Risk ratings; contracts; sub-processor register | CTO |
| `IS-09` Network | `PS-02`, `EA-08`…`EA-12` | Gateway logs; session policy | CTO |
| `IS-10` Incident | `FR-GRC-036`, `BRU-GRC-13`, `BRU-DTS-17` | Breach register; notification records | CTO / CDO |
| `IS-11` Continuity | `FR-GRC-043`, `NFR-006` | **None — `O-07`** | CTO |
| `IS-12` Awareness | `FR-GRC-030` | Attestation and training records | CTO / L&D |
| `IS-13` Compliance | `FR-GRC-011`…`FR-GRC-022` | Control tests; deficiency and retest records | CTO / CFO |

> **`CL-01`. The `IS-11` row says "None".** That is the honest entry, and it is the row an enterprise
> client or an insurer will look at first. `CG-012` `EX-01` prohibits claiming an artefact exists
> without checking; **§4.11.2 and this row are that check, recorded.**

---

## 5. Liability, Exclusions and Limits

| # | Clause |
|---|---|
| **5.1** | This is an internal policy suite and creates no third-party rights |
| **5.2** | **Nothing here is a warranty of security to a client.** A contractual security commitment is in the contract, and §4.1.4 limits what may be claimed |
| **5.3** | **An ISO 27001 or SOC 2 claim beyond alignment or readiness is a misrepresentation** (`CS3`, `O-03`), and `CG-013` `T-A13` escalates it |
| **5.4** | **A control asserted without evidence is a deficiency** (`BRU-GRC-07`), and an assurance given on it is an assurance given on nothing |
| **5.5** | **A processor's failure is the company's liability to the data subject** (`NFR-098`), whatever the supplier contract says |
| **5.6** | Nothing limits liability that cannot lawfully be limited |

---

## 6. Data Protection

> Must reconcile with `LG-008`, `LG-009`, `LG-012`. Check **F6**.

| # | Clause |
|---|---|
| **6.1** | This set is the *"technical and organisational measures"* `NFR-097` requires, and `LG-008` §4.6 summarises it to data subjects |
| **6.2** | `IS-02` classification and `IS-03` access are what make `LG-008`'s purpose limitation real; **a purpose limit with unrestricted access is a statement, not a control** |
| **6.3** | `IS-04` key management is what makes `LG-009` `DM-3` crypto-erase a deletion |
| **6.4** | `IS-02` §4.2.5 and `IS-08` are what make `LG-012` residency and transfer control enforceable |
| **6.5** | `IS-10` is the operational half of `LG-008` §4.8 breach notification |
| **6.6** | Security logs contain employee personal data, retained per `LG-009` `RC-22` and disclosed under `LG-020` §4.6 — **proportionality is `CS6`** |
| **6.7** | **Whistleblowing, legal-matter and breach records are `T5`** (`BRU-GRC-20`) |

---

## 7. Termination and Consequences

| Event | Consequence |
|---|---|
| **A control fails a test** | Rated as a deficiency, significant deficiency or material weakness; remediation assigned; **closure requires a passed retest** (`BRU-GRC-08`, `BRU-GRC-17`) |
| **A control operates without evidence** | **A deficiency, not a pass** (`BRU-GRC-07`) |
| **An incident occurs** | `IS-10`; four notification clocks assessed; the decision recorded |
| **A critical vulnerability passes 7 days** | **Escalated to the CTO and reported to the board** (`BRU-SEC-21`) |
| **A User breaches a policy** | `LG-020` §7 |
| **A supplier breaches `IS-08`** | `LG-006` §7 suspension or removal; the incident recorded |
| **A policy exception is needed** | **Recorded, approved, time-boxed and reviewed** (`FR-GRC-031`) |
| **This set is superseded** | Prior versions retained permanently (`LG-009` `DC-24`), because an audit samples the prior cycle |

---

## 8. Dispute Resolution

| Step | Route |
|---|---|
| **1 — Control or policy interpretation** | The policy owner, then the CTO |
| **2 — A deficiency dispute** | The CFO, since control testing reports to finance governance (`BRU-GRC-06`) |
| **3 — A client or auditor challenge** | CTO with Legal Counsel, producing control tests and the §4.14 map — **including the `IS-11` gap** |
| **4 — A regulator engagement** | Legal Counsel with the CTO; recorded in `LG-024` |
| **5 — Courts** | The courts of Dhaka, Bangladesh |

---

## 9. Change Control

| Version | Date | Change | Notice given to users | Re-acceptance required |
|---|---|---|---|:--:|
| 1.0 | 2026-08-18 | Initial issue — draft for G5. Thirteen policies, policy-to-control map, four gaps recorded honestly | n/a | n/a |

| # | Rule |
|---|---|
| **9.1** | A change to a policy's substance is **MAJOR**: notice and **re-attestation** by the named population |
| **9.2** | **A change may not weaken a `BRU-SEC-*` rule.** A rule change is `CG-013` `T-B03` to the rule owner in `05-05`, not a policy edit |
| **9.3** | **A `CS1` answer designating the company critical information infrastructure is MAJOR** and imports obligations into `IS-10` and `LG-012` |
| **9.4** | Every version retained permanently (`LG-009` `DC-24`) |
| **9.5** | **Annual review regardless of change** — a security policy set unreviewed for a year is stale by definition |

---

## 10. Cross-References

| Document | Relationship | Must not contradict |
|---|---|---|
| [`LG-020_Acceptable_Use_and_Internal_Access_Policy.md`](LG-020_Acceptable_Use_and_Internal_Access_Policy.md) | **The User-facing half — `W1`, before this file (`O-06`)** | Access rules, monitoring, consequences |
| [`LG-012_Cross_Border_Data_Transfer_and_Residency_Statement.md`](LG-012_Cross_Border_Data_Transfer_and_Residency_Statement.md) | `IS-02` §4.2.5, `IS-04` §4.4.4, `IS-08`; **`CS1` = `RD3`** | Residency enforcement; sub-processor register |
| [`LG-008_Privacy_Notice_and_Consent_Copy.md`](LG-008_Privacy_Notice_and_Consent_Copy.md) | **§4.6 there summarises this set**; `IS-10` = §4.8 there | Check **F6**; breach notification |
| [`LG-009_Data_Retention_and_Deletion_Schedule.md`](LG-009_Data_Retention_and_Deletion_Schedule.md) | `IS-04` enables `DM-3`; `RC-22` log retention | Deletion method; log periods |
| [`LG-017_Data_Recovery_and_Secure_Destruction_Terms.md`](LG-017_Data_Recovery_and_Secure_Destruction_Terms.md) | `IS-07` §4.7.2, `IS-04` §4.4.3 | Secure-area and case-key controls |
| [`LG-019_ESignature_Legal_Notice_and_Evidence_Statement.md`](LG-019_ESignature_Legal_Notice_and_Evidence_Statement.md) | **§4.4.6 algorithm agility = `LG-019` `O-07`**; §4.8.6 lawful-control evidence | Crypto-agility; system integrity |
| [`LG-016_Managed_Services_and_Remote_Access_Consent_Terms.md`](LG-016_Managed_Services_and_Remote_Access_Consent_Terms.md) | `IS-03` §4.3.3, `IS-05`; §4.6 vaulting | Privileged and break-glass access |
| [`LG-006_Vendor_Portal_Terms_and_Supplier_Code_of_Conduct.md`](LG-006_Vendor_Portal_Terms_and_Supplier_Code_of_Conduct.md) | `IS-08`; **`CS4`** | Supplier security flow-down |
| [`LG-022_Quality_Policy_and_ISO_9001_Statement_Set.md`](LG-022_Quality_Policy_and_ISO_9001_Statement_Set.md) | Management-system parallel; **ISO 9001 is held, ISO 27001 is not** (`O-03`) | Certification claims |
| [`LG-024_Regulatory_Disclosure_and_Statutory_Notice_Register.md`](LG-024_Regulatory_Disclosure_and_Statutory_Notice_Register.md) | §4.13.7; `IS-10` notifications as obligations | The obligation set |
| [`../06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-006_Segregation_of_Duties_Register.md`](../06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-006_Segregation_of_Duties_Register.md) · [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-031_SOP_IT_Service_Desk_and_Change_Management.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-031_SOP_IT_Service_Desk_and_Change_Management.md) | `IS-03` §4.3.6, `IS-05` §4.5.6 | SoD rules; change process |
| `TS-017` Security and Privacy Test Case Pack | **`IS-06` §4.6.5 and `IS-13` — where these policies are actually verified** | The tests |
| `OP-004` incident templates · `OP-014` manual fallback | `IS-10` §4.10.7, `IS-11` §4.11.4 | Incident and fallback content |
| `TR-021` System Administrator course | `IS-12` §4.12.2 | Administrator training |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Legal_Document.md` — ten sections in order; **the suite-in-§4 adaptation declared, and reported as a fourth instance of a known template gap** (`O-08`)
- [x] **Thirteen policies with a named owner each**, answering the `BRU-GRC-11` ownership gap
- [x] All 25 `BRU-SEC-*` rules mapped to a policy; none restated as a new requirement
- [x] **Policy-to-control map with evidence per policy**, including an honest "None" for continuity (`CL-01`)
- [x] **The ISO 27001 position stated as alignment and readiness, not certification** (§4.1.4, `O-03`)
- [x] **Four distinct breach-notification clocks distinguished** (§4.10.2)
- [x] Four gaps recorded rather than implied — continuity plan, control register, vulnerability discovery, security owner
- [x] All internal links resolve
- [x] Bengali counterpart — n/a per `CG-010` §3.2
- [ ] **`CS1`–`CS6` answered at G5** — outstanding, blocks `Approved`
- [ ] **`CS1` critical-infrastructure designation resolved once for this file and `LG-012`** — outstanding, `O-02`
- [ ] **Control register created** — outstanding, `O-04`; §4.14 cannot cite control identifiers
- [ ] **Continuity and disaster-recovery plan with recovery objectives and test evidence** — outstanding, `O-07`
- [ ] **Vulnerability discovery mechanism established** — outstanding, `O-09`; `BRU-SEC-21` presumes one
- [ ] **Operational security owner named** — outstanding, `O-05`
- [ ] Named approver recorded — pending
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
