---
id: FIX-ERP2-M29
module_id: M29
module_code: SEC
module_name: Identity, Access & Information Security
category: K — Platform & Technology
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Chief Technology Officer
system_owner: Platform Squad
priority: P0
wave: W1
---

# M29 — Identity, Access & Information Security
### Category K · Code `SEC` · Existing (retained, extended for PDPA 2026)

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M29 |
| **Module code** | `SEC` |
| **Category** | K — Platform & Technology |
| **Status** | Existing (retained from v1.0; **materially extended in v2.1** for the Personal Data Protection Act 2026 and the split-residency architecture) |
| **Priority** | **P0** — one of the three modules built first |
| **Delivery wave** | W1 (Months 1–4), with PDPA enforcement readiness by W4 |
| **Business owner** | Chief Technology Officer |
| **System owner** | Platform Squad |
| **Delivery layers** | L4 Keycloak · L2 OCA `server-tools` audit · L5 custom permission, SoD, audit, residency and security-operations modules |
| **Custom modules** | `cd_rbac_ext`, `cd_audit_ext`, `cd_sod`, `cd_identity_ext`, `cd_data_protection` |
| **Requirement range** | FR-SEC-001 … FR-SEC-052 |
| **Requirement count** | **52** *(measured — exceeds the 044 range allocated in `05-01` §1.3; extension into the 045–065 headroom, see §16)* |
| **Effort estimate** | **31 person-weeks** *(measured — supersedes the 24 PW estimate in `02-02`)* |
| **Depends on** | M28 Integration (gateway edge) · M30 Platform Admin (org structure) · M21 Core HR (joiner/leaver events, from W5) |
| **Depended on by** | **All 66 other modules and all 12 portals** |

---

## 2. Purpose

M29 answers three questions for every request the estate ever handles: **who is this, what
are they allowed to do, and what did they actually do?**

It is the module that makes it structurally impossible for a Mirpur branch agent to read a
Chittagong customer's record, for a technician to see a colleague's salary, for a marketplace
seller to see another seller's payout, or for anyone at all to raise a purchase order, receive
the goods and approve the invoice.

It also owns the Company's obligations under the **Personal Data Protection Act 2026**, which
came into force in April 2026 with enforcement mechanisms activating around **13 May 2027 —
inside Wave 4**. 1000FiX holds the personal data of more than 250,000 customers a month,
alongside national identity numbers, biometric attendance templates and recovered customer data
from data-recovery cases. The penalty exposure is up to **BDT 25 lakh**, rising to **BDT 50
lakh** for a significant data fiduciary.

The category overview states the promises: *no module implements its own authentication,
session handling or permission engine*, and *every data change is audited without the module
writing audit code*. Both are absolute.

### Why It Exists

**Because the alternative is 67 implementations of the same control.** If each module handles
its own authentication, then a defect in one is a breach in one, and there is no single place
to fix it, test it or prove it.

**Because branch isolation is a legal and contractual obligation, not a preference.** A
corporate client's data must not be visible to a branch that does not serve them. A brand
partner must see only its own claims. These are tender commitments.

**Because the regulator arrives in Wave 4.** PDPA enforcement, the National Data Management
Authority, the breach-notification duty, data-subject rights and the restriction on
large-scale transfer of Sensitive Personally Identifiable Data all become live obligations
during the programme, not after it.

**Because segregation of duties cannot be a policy document.** `05-04` §6 lists twelve
incompatible duty combinations. A rule that is written down but not enforced by the permission
engine is a rule that will be broken and only discovered by an auditor.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| `_CATEGORY_OVERVIEW.md` §7 promises 3, 4 | No module implements its own auth, session or permission engine; every data change is audited without module-level audit code |
| `_CATEGORY_OVERVIEW.md` §6 | M29 owns identity, authentication, MFA, SSO, federation, roles, permissions, record rules, field permissions, SoD **enforcement**, encryption, key management, data classification and the audit trail. **M60 defines and tests the SoD rules; M29 enforces them** |
| `_CATEGORY_OVERVIEW.md` §9 | MFA on privileged accounts 100%; zero orphaned accounts beyond 24 h; access certification 100% per cycle; zero critical vulnerabilities open > 7 days; 100% audit coverage of financial transactions |
| `_CATEGORY_OVERVIEW.md` §11 | Risk: "Identity or permission defect exposes data across branches or customers — **Critical**, legal and contractual" |
| `05-04` §1 | The full register of **38 roles** across 12 portals |
| `05-04` §2, §3 | Portal access matrix and module permission matrix with CRUDA and scope suffixes |
| `05-04` §4 | The **six data isolation tiers** T0–T5 and the objects at each |
| `05-04` §5 | Field-level permissions — thirteen restricted field groups |
| `05-04` §6 | **SOD-01 … SOD-12** — twelve incompatible duty combinations, all hard-blocked |
| `05-04` §8 | **EA-01 … EA-12** external party access rules |
| `05-04` §9 | The access lifecycle: provision, modify, elevate, review, suspend, deprovision, external expiry |
| `05-05` §11 | BRU-SEC-01 … BRU-SEC-08 |
| `05-06` §4 | NFR-011 … NFR-015 and NFR-061 … NFR-072 — the full security requirement set |
| `05-06` §6.1 | Regulatory currency: **Cyber Security Ordinance 2025 in force**; Digital Security Act 2018 and Cyber Security Act 2023 both repealed |
| `05-06` §6.3 | **NFR-090 … NFR-099** — the PDPA 2026 statutory obligations, and the BDT 25/50 lakh penalty exposure |
| `05-06` §6.4 | **NFR-086, 086a, 086b, 086c** — the split-residency data architecture and the residency-classified field list |
| `05-06` AS-14 | S3-classified data encrypted at field level with access logging |

---

## 3. Scope Boundary

> **The rule:** M29 owns **who may do what, and the proof of what was done**. It does not own
> the business meaning of any permission, and it does not own the personal data itself — only
> its protection.

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | Identity lifecycle: creation, activation, suspension, deprovision, across internal and external populations |
| 2 | Authentication: password policy, MFA, step-up authentication, device trust, session management |
| 3 | Single sign-on and federation, including corporate-client SSO for the B2B portal |
| 4 | OAuth 2.0 / OIDC token issue, introspection, refresh and revocation for all 12 API families |
| 5 | Role definition, role hierarchy and permission-set composition |
| 6 | Permission model: create, read, update, delete, approve — per module per role |
| 7 | **Record rules** implementing the six data isolation tiers T0–T5 |
| 8 | **Field-level permissions** — which roles may see which fields |
| 9 | Delegation of authority with time limits and audit |
| 10 | **Segregation-of-duties enforcement** at role assignment and at transaction time |
| 11 | Access request, approval and provisioning workflow |
| 12 | **Access certification** — periodic manager review with automatic revocation of unconfirmed access |
| 13 | Privileged access management: elevation, time-boxing, session recording, break-glass |
| 14 | Joiner–mover–leaver automation driven by M21 events |
| 15 | **The immutable audit trail** — who, what, when, before, after — for every controlled object |
| 16 | Data access logging for sensitive and personal data, including bulk export |
| 17 | Encryption at rest and in transit; field-level encryption for S3-classified data |
| 18 | Key management: generation, storage, rotation, escrow and access control |
| 19 | **Data classification** — the sensitivity and residency label on every field |
| 20 | **Residency enforcement at write time** for the split-residency architecture (NFR-086a) |
| 21 | **Cross-border transfer control**: safeguard record, Authority notification, pre-transfer gate (NFR-086b, NFR-099) |
| 22 | Security event detection, correlation and alerting |
| 23 | Vulnerability management: scanning, triage, remediation tracking, closure |
| 24 | Security incident response with severity, containment and **breach-notification assessment** (NFR-094) |
| 25 | Data masking for non-production environments |
| 26 | Malware scanning on file upload |
| 27 | Bot protection, brute-force defence and anomalous-access detection |
| 28 | Penetration-test finding management to closure |
| 29 | External party access control implementing EA-01 … EA-12 |
| 30 | The technical execution of data-subject rights: identity verification, access assembly, erasure and portability (with M33) |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| **Definition and testing of the SoD rules** | **M60** GRC | M60 decides which duty combinations are incompatible and tests the control; **M29 enforces**. Separating definition from enforcement is itself a control |
| Consent, transparency notice, lawful basis, processing purpose | **M33** Party Master | Consent is a property of the relationship with the data subject (NFR-090…092). M29 protects the data; M33 governs why it is held |
| Data-subject rights *process* — receipt, decision, response | **M33** (with M29 executing) | M33 owns the request lifecycle; M29 assembles, erases and proves |
| Breach *notification to the Authority* | **M60** GRC (with M29 detecting) | NFR-094 assigns the notification obligation to M60; M29 detects and assesses |
| Chief Data Officer appointment and data-fiduciary classification | **M60** | An organisational obligation (NFR-096) |
| Processor and sub-processor contractual flow-down | **M42** / **M60** | NFR-098 — a contract obligation |
| The API gateway, rate limiting, bot protection at the edge | **M28** | M28 *enforces* at the edge using M29's decisions; M29 issues and validates the token |
| Organisation structure: entity, branch, zone, cost centre | **M30** | M29 uses them as record-rule dimensions; it does not define them |
| Master data governance and stewardship | **M64** | M64 does not define access; M29 does not govern data quality |
| Country pack, jurisdiction rules, translation | **M65** | M65 supplies the jurisdiction; M29 enforces residency |
| Internal IT incident and change management process | **M66** | A security incident *is* an incident; M66 runs the process, M29 owns the security judgement |
| Employee record, contract, roster, payroll | **M21** / **M55** / **M56** | M29 consumes joiner and leaver events |
| Physical security, CCTV, premises access | **M47** Facility | — |
| Document retention schedule and legal hold | **M24** | M29 audits access to documents; M24 governs their life |
| Quality management system and ISO certification | **M23** | M29 supplies evidence; M23 owns the standard |

### 3.3 Shared Concepts

| Concept | M29's Role | Owning Module |
|---|---|---|
| Identity | **Owns** the credential and the session; M21 owns the employee, M33 owns the party | M29 / M21 / M33 |
| Role and permission | **Owns** | M29 |
| Segregation of duties | **Enforces**; M60 defines and tests | M29 / M60 |
| Audit trail | **Owns** | M29 |
| Data classification | **Owns** the classification and its enforcement; each module classifies its own fields | M29 / module |
| Residency | **Owns** enforcement; M65 owns the jurisdiction definition | M29 / M65 |
| Consent | Reads as an access precondition; M33 owns it | M33 |
| Data-subject right | Executes the technical action; M33 owns the request | M29 / M33 |
| Security incident | Owns detection and assessment; M66 runs the incident process; M60 notifies the Authority | M29 / M66 / M60 |
| Vulnerability | **Owns** | M29 |
| Encryption key | **Owns** the reference and the policy; the vault holds the material | M29 / M30 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **SAP Cloud Identity Access Governance (IAG)** | Access Analysis, **Access Certification**, Access Request, **Privileged Access Management**, Role Design — with SoD risk analysis and role mining | **The five-service decomposition is the structural model for M29's access governance.** Adopted directly: SoD *risk analysis* as a preventive check at assignment rather than a detective report; **access certification as a recurring cycle with automatic revocation of unconfirmed access**; and PAM as a distinct discipline from ordinary role assignment | Role mining; at 38 defined roles the value is negligible and the roles are already designed |
| **SAP GRC Access Control** | Rule-set-driven SoD with mitigating controls and time-boxed exceptions | **Mitigating controls and time-boxed exceptions with a standing quarterly review** (`05-04` §6). A hard block with no exception path produces shadow workarounds; a documented, expiring, reviewed exception does not | The full risk-terminator ruleset complexity |
| **Identity Governance & Administration practice (IGA)** | Consistent processes for password management, access review, access request and approval; controls mapped to regulatory obligations | **Access review as a scheduled business process owned by line managers**, not an IT task — because the manager is the only person who knows whether the access is still needed | Automated risk scoring of every identity; disproportionate at 800 internal users |
| **Keycloak (L4, TD-07)** | OIDC/OAuth 2.0 provider, federation, MFA, brokering, fine-grained authorisation services | Token issue and introspection, MFA enforcement, **corporate-client SSO federation (INT-046)** for the B2B portal | Keycloak's authorisation services as the permission engine. Business permissions live with the business data; Keycloak issues identity, Odoo record rules enforce scope |
| **NIST-aligned zero-trust posture** | Never trust the network; authorise every request; assume breach | **Authorisation is evaluated server-side on every request** (API-10). No portal, no gateway route and no internal caller is trusted to have filtered correctly | A full zero-trust network overlay; the cost is not justified at current scale |
| **ISO 27001 Annex A** | Control framework for access, cryptography, operations, incident and supplier security | The control set is the backbone of §5.6 and §5.7; 1000FiX's ISO posture is a stated competitive advantage and NFR-025 requires alignment | Certification as a Wave 1 goal; readiness is targeted at NFR-089 for the expansion waves |
| **Bangladesh PDPA 2026 practice** | Consent, transparency, data-subject rights, breach notification, processing records, restriction on large-scale transfer of sensitive identifiers, data localisation narrowed to restricted and CII data by Ordinance No. 23 of 2026 | **Residency as a field-level classification enforced at write time**, and cross-border transfer as a gated action with a safeguard record — rather than a policy statement in a document nobody reads | Full data localisation of all personal data. The February 2026 amendment narrowed localisation to *restricted* and CII data, which materially reduces the scope of NFR-086 — see the design position and Q-01 |

**Design position.** Five deliberate differences.

First, **the permission engine is one engine, and it lives with the data**. Keycloak issues
identity; Odoo record rules and field permissions enforce scope inside the transaction. This
splits authentication from authorisation deliberately: a token proves who you are, and the
database row rule proves what you may see. A permission decision made only at the API edge is
one crafted request away from being wrong (AC-11 in M28 tests exactly this).

Second, **SoD is enforced twice — at assignment and at transaction**. Checking only at role
assignment misses the case where a user legitimately holds two roles across time, or where
delegation grants an incompatible combination temporarily. `05-04` SOD-02 in particular — raise
PO, receive goods, approve invoice — is a runtime condition, not a static one.

Third, **audit is inherited, never written**. Promise 4 of the platform contract is that a
module gets audit without writing audit code. It is delivered by base-model inheritance and ORM
interception, so a developer cannot forget it and cannot opt out. Modules that write their own
audit produce inconsistent, incomplete and unqueryable trails.

Fourth, **residency is a field property enforced by the platform, not an operational
convention**. NFR-086a is explicit that the model carries a residency classification on every
field and the platform enforces it at write time. This is the single most consequential
technical decision in M29 and it must be made before the Wave 1 architecture is fixed —
dependency **DEP-31** and decision **D-13** in `00-04` both hang on the pending legal opinion.

Fifth, **the regulatory position is dated and re-verified, not assumed**. `05-06` §6.1 already
corrects two errors of exactly this kind: the Digital Security Act 2018 was cited long after it
was repealed. M29 therefore holds the statutory basis as **versioned, dated reference data with
a named owner and a review cycle**, not as text in a specification. Research for this
specification surfaced a further material refinement — the February 2026 amendment narrowing
localisation — which is raised as Q-01 and as an audit finding.

---

## 5. Functional Areas & Features

### 5.1 Identity & Authentication

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-SEC-001 | Identity lifecycle | Create, activate, suspend and deprovision identities for internal staff, external parties and service accounts, each with an owner and a status | **P0** | L4/L5 |
| FR-SEC-002 | Authentication | Authenticate every user against the identity provider; **no module implements its own authentication or session handling** | **P0** | L4 |
| FR-SEC-003 | Password policy | Enforce length, complexity, history, breach-list checking and reset flows, in Bengali and English | **P0** | L4 |
| FR-SEC-004 | **Multi-factor authentication** | Require MFA for admin, finance, HR and all privileged roles at every login, and for any external action with financial consequence (NFR-012, BRU-SEC-01, EA-09) | **P0** | L4 |
| FR-SEC-005 | **Step-up authentication** | Require re-authentication for sensitive actions: payouts, payroll finalisation, data-case access, bulk export, permission change, residency-classified field access (NFR-065, BRU-SEC-02) | **P0** | L4/L5 |
| FR-SEC-006 | Session management | Enforce 30-minute idle timeout for external users, 60-minute for internal, 12-hour absolute maximum, with concurrent-session limits and forced revocation (NFR-069, EA-08) | **P0** | L4 |
| FR-SEC-007 | Token services | Issue, introspect, refresh and revoke OAuth 2.0 / OIDC tokens for all 12 API families, scoped per consumer | **P0** | L4 |
| FR-SEC-008 | Single sign-on | Provide SSO across all internal portals and applications from one authentication | **P0** | L4 |
| FR-SEC-009 | **Corporate client federation** | Federate authentication with corporate clients' own identity providers over SAML or OIDC, so B2B portal users sign in with their employer's credentials (INT-046) | P2 | L4 |
| FR-SEC-010 | Device trust and registration | Register and identify devices for technician, rider and auditor applications; deregister on leaver or loss | P1 | L5 |
| FR-SEC-011 | Brute-force and anomaly defence | Detect and block credential stuffing, brute force, impossible-travel and anomalous access patterns | **P0** | L4/L5 |
| FR-SEC-012 | Service accounts | Manage non-human identities with scoped credentials, rotation and an accountable human owner | **P0** | L5 |

### 5.2 Authorisation, Roles & Isolation

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-SEC-013 | Role register | Maintain the **38 roles** in `05-04` §1 with headcount, portals, MFA requirement and data scope | **P0** | L5 |
| FR-SEC-014 | Permission sets | Compose permissions as create, read, update, delete and approve per module per role, matching the `05-04` §3 matrix | **P0** | L1/L5 |
| FR-SEC-015 | **Record rules — six isolation tiers** | Enforce T0 global, T1 entity, T2 branch, T3 zone, T4 own-record and T5 restricted, by `company_id`, `operating_unit_id`, `zone_id`, `partner_id`/`user_id` and named allow-list respectively (`05-04` §4, NFR-015) | **P0** | L1/L5 |
| FR-SEC-016 | **Field-level permissions** | Restrict named fields to named roles — cost and margin, salary, NID, bank account, recovered-data index, call recordings, commission rate, KYC documents, incentive detail, credit limit, vendor price, model internals, internal notes (`05-04` §5, NFR-011) | **P0** | L5 |
| FR-SEC-017 | Portal access control | Enforce the `05-04` §2 portal access matrix so that a role reaches only its permitted portals | **P0** | L5 |
| FR-SEC-018 | **External party rules** | Enforce EA-01 … EA-12: a party sees only records where they are named; never cost, margin, internal notes or another party's data; scope bound to the credential and not widenable by parameter; bulk export limited, rate-controlled and logged | **P0** | L5 |
| FR-SEC-019 | Delegation | Delegate authority for a bounded period with an explicit scope, full audit, and automatic expiry | P1 | L5 |
| FR-SEC-020 | Approval authority | Evaluate the `05-04` §7 approval authority matrix so that an approval outside a role's band is rejected | **P0** | L5 |
| FR-SEC-021 | Server-side enforcement | Evaluate every authorisation server-side on every request; no client, portal or gateway assertion is trusted (API-10) | **P0** | L5 |

### 5.3 Segregation of Duties & Access Governance

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-SEC-022 | **SoD enforcement at assignment** | Evaluate the SOD-01 … SOD-12 rule set at role assignment and block an incompatible combination (NFR-064, BRU-SEC-07) | **P0** | L5 |
| FR-SEC-023 | **SoD enforcement at transaction** | Re-evaluate SoD at transaction time, so that a combination acquired through delegation, role change or elevation is caught in the act | **P0** | L5 |
| FR-SEC-024 | SoD exception management | Permit a time-boxed, CFO- or CTO-approved exception with a mitigating control, and present all live exceptions on a standing quarterly report | **P0** | L5 |
| FR-SEC-025 | Access request workflow | Request, justify, approve and provision access, with line-manager approval for standard roles and line manager plus IT Administrator plus CTO for privileged roles (`05-04` §7) | **P0** | L5 |
| FR-SEC-026 | **Access certification** | Run a scheduled certification cycle in which each manager confirms or revokes every report's access; **unconfirmed access is revoked automatically** (`05-04` §9) | **P0** | L5 |
| FR-SEC-027 | Joiner automation | Create the identity, assign the role from the position profile, grant portal access and assign onboarding training on the `employee.joined` event from M21 | **P0** | L5 |
| FR-SEC-028 | Mover automation | On transfer or promotion, revoke old permissions and grant new ones on the effective date, with **no accumulation** | **P0** | L5 |
| FR-SEC-029 | **Leaver automation** | Revoke all access within one hour of the `employee.left` event, deregister devices and reassign delegated authority (BRU-SEC-06) | **P0** | L5 |
| FR-SEC-030 | Orphaned account detection | Detect and report any account without an active owner; **zero tolerance beyond 24 hours** | **P0** | L5 |
| FR-SEC-031 | External access expiry | Disable external access automatically at agreement or registration expiry, retaining records per the retention schedule (EA-12, `05-04` §9) | **P0** | L5 |

### 5.4 Privileged Access Management

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-SEC-032 | Privileged role register | Identify every privileged role and privileged action across the estate, with an accountable owner | **P0** | L5 |
| FR-SEC-033 | Time-boxed elevation | Grant privileged access for a bounded period with automatic expiry and no standing administrative rights (`05-04` §9) | **P0** | L5 |
| FR-SEC-034 | Privileged session recording | Record every privileged session with the actions taken, retained and reviewable (NFR-070) | P1 | L5 |
| FR-SEC-035 | Break-glass access | Provide an emergency access path that is loud rather than quiet — immediate multi-party notification, mandatory post-hoc justification and automatic expiry | P1 | L5 |
| FR-SEC-036 | Self-approval prohibition | Prevent any user administering their own access or approving their own access request (SOD-09) | **P0** | L5 |

### 5.5 Audit Trail & Access Logging

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-SEC-037 | **Immutable audit trail** | Record who, what, when, before and after for every change to a controlled object, **inherited by every module without module-level audit code** (NFR-014, promise 4) | **P0** | L2/L5 |
| FR-SEC-038 | Audit immutability | Make audit entries insert-only, tamper-evident and undeletable by any role including administrators | **P0** | L5 |
| FR-SEC-039 | Financial audit coverage | Guarantee 100% audit coverage of financial transactions, reconcilable to source (DI-02) | **P0** | L5 |
| FR-SEC-040 | **Data access logging** | Log every access to personal, S3-classified and residency-classified data, including reads, with actor, purpose and record identity (AS-14, EA-10) | **P0** | L5 |
| FR-SEC-041 | Bulk export control | Require approval for bulk personal-data export, log every export with its scope and requester, and rate-limit it (BRU-SEC-05, EA-12) | **P0** | L5 |
| FR-SEC-042 | Audit search and retention | Make the audit trail searchable by actor, object, field, time and correlation id, retained for at least five years (NFR-095) | **P0** | L5 |
| FR-SEC-043 | Processing records | Maintain records of processing activity sufficient to satisfy NFR-095, retained a minimum of five years | **P0** | L5 |

### 5.6 Data Protection, Classification & Residency

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-SEC-044 | Encryption | Encrypt data at rest with AES-256 and in transit with TLS 1.2+ (1.3 preferred) (NFR-013) | **P0** | L4/L5 |
| FR-SEC-045 | **Field-level encryption** | Encrypt S3-classified fields at field level with separate key material and access logging (NFR-061, AS-14) | **P0** | L5 |
| FR-SEC-046 | Key management | Generate, store, rotate, escrow and control access to key material through the vault, with rotation scheduled and access audited | **P0** | L4/L5 |
| FR-SEC-047 | **Data classification** | Carry a sensitivity classification and a **residency classification on every field**, maintained as part of the data model rather than as documentation (NFR-086a) | **P0** | L5 |
| FR-SEC-048 | **Residency enforcement at write time** | Enforce the split-residency architecture in the platform: residency-classified fields are written to the Bangladesh-resident store, joined to the regional record by a resident key, **never duplicated into the regional store** (NFR-086) | **P0** | L5 |
| FR-SEC-049 | **Cross-border transfer control** | Block transfer of a residency-classified field across a border until an Authority notification record and a documented safeguard exist; log every transfer that proceeds (NFR-086b, NFR-099) | **P0** | L5 |
| FR-SEC-050 | Non-production masking | Guarantee that no unmasked residency-classified or S3-classified data exists in any non-production environment in any region (NFR-071, NFR-086c, BRU-SEC-08) | **P0** | L5 |
| FR-SEC-051 | **Data-subject right execution** | Execute the technical actions behind data-subject rights: verify the requester's identity, assemble a portable export, apply rectification with controller notification within 30 days, and perform verifiable erasure — under M33's request lifecycle (NFR-093) | **P0** | L5 |
| FR-SEC-052 | Retention and purge enforcement | Enforce the retention schedule technically, purge on expiry, and refuse to purge anything under legal hold (NFR-088, BRU-SEC-04) | **P0** | L5 |

### 5.7 Security Operations

> Security operations requirements are delivered within the FR-SEC range above and are grouped
> here for readability: **FR-SEC-011** (anomaly defence), **FR-SEC-034** (session recording),
> **FR-SEC-040/041** (access and export logging) plus the operational capabilities below, which
> are specified as automations and technical functions rather than as separate requirements
> because they are continuous processes rather than discrete features.

| Capability | Delivered By | Requirement Basis |
|---|---|---|
| Vulnerability scanning — dependency, container, infrastructure, in CI and in production | AUT-SEC-14, T-11 | NFR-066 |
| Critical vulnerability remediation within 7 days | AUT-SEC-15, KPI | Category KPI |
| Annual penetration test with findings tracked to closure | AUT-SEC-16 | NFR-067 |
| Malware scanning on every file upload before storage or serving | AUT-SEC-17 | NFR-063 |
| Security event correlation and alerting | AUT-SEC-12 | NFR-072 |
| Security incident response with severity and containment | §8.3 state model | NFR-072 |
| **Breach-notification assessment** and hand-off to M60 | AUT-SEC-13 | NFR-094 |

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Authorisation is transactional, not edge-only** | Record rules and field permissions execute inside the database transaction. An API-edge check alone is insufficient and is treated as a defect |
| T-02 | **Audit by inheritance** | Audit is delivered by base-model inheritance and ORM interception. A module cannot opt out, and a developer cannot forget. Verified by a model-registry check in CI |
| T-03 | **Audit immutability** | Audit entries are insert-only at the database privilege level; the application role has no `UPDATE` or `DELETE` grant on the audit tables. Tamper evidence by hash chaining per partition |
| T-04 | **Residency enforced at write time** | The ORM layer routes residency-classified fields to the resident store. A write that would place such a field in the regional store fails — it does not warn (NFR-086a) |
| T-05 | **Resident-key join** | Regional and resident records are joined by an opaque resident key that carries no personal information and cannot be reversed to a natural identifier |
| T-06 | **Field-level key separation** | S3-classified fields use key material distinct from the database-level encryption key, so a database compromise does not yield the sensitive fields |
| T-07 | **SoD evaluated twice** | Once at role assignment (preventive) and once inside the transaction (detective-preventive). The runtime evaluation is authoritative |
| T-08 | **Permission decision latency** | Authorisation adds ≤ 15 ms at p95 to a request, inside the NFR-002 400 ms budget. A slow permission engine gets bypassed |
| T-09 | **Token introspection availability** | The introspection endpoint used by M28 must sustain ≥ 99.99% availability with ≤ 20 ms p95, because every request depends on it. Cached introspection with short TTL and immediate revocation propagation |
| T-10 | **Revocation propagation** | A revoked token, suspended identity or leaver event takes effect estate-wide within 60 seconds, not at next token expiry |
| T-11 | **Continuous scanning** | SAST, DAST, dependency and container scanning run on every build and continuously in production; findings flow to the vulnerability register automatically |
| T-12 | **Masking determinism** | Non-production masking is deterministic and referentially consistent, so masked data remains testable while being irreversible |
| T-13 | **No personal data in logs** | Structured logging redacts classified fields at emission, not at ingestion (OPS-04) |
| T-14 | **Scale envelope** | 800+ internal users, 250,000+ customer identities per month, 5,000 sellers, 3,000 external party users; audit volume of ~50M entries per year at Wave 8 with sub-second search on the working window |
| T-15 | **Break-glass loudness** | Emergency access notifies multiple parties immediately and cannot be used silently; the notification path is independent of the systems it grants access to |
| T-16 | **Statutory reference data** | The regulatory basis is versioned, dated reference data with a named owner and a review cycle — never text embedded in code or specification (see §4 design position five) |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M29 |
|---|---|---|
| **Branch agent** | Can see more than they should, because the system has no branch isolation | Sees their branch, and only their branch — enforced at the row, not by convention |
| **Technician** | Shares logins in practice | Own identity, own device, own jobs; actions attributable to a person |
| **Line manager** | Never asked whether a report still needs their access | Confirms or revokes each report's access every cycle; unconfirmed access lapses |
| **HR** | Tells IT about a leaver and hopes | The leaver event revokes access within an hour, automatically |
| **IT administrator** | Holds standing administrative rights | Elevates when needed, time-boxed and recorded; no standing privilege |
| **Finance / CFO** | Trusts that SoD is being followed | SoD is enforced by the engine; exceptions are visible, approved and expiring |
| **Corporate client** | Manages another set of credentials | Signs in with their own company's identity provider |
| **Customer** | No visibility of what is held about them | Data-subject rights actually executable — access, portability, rectification, erasure |
| **Auditor / regulator** | Asks for evidence; receives assembled screenshots | Queries an immutable trail |
| **Module developer** | Would build auth, permissions and audit per module | Inherits all three; cannot opt out |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Regulatory penalty avoidance** | PDPA 2026 obligations implemented before enforcement activates around **13 May 2027, inside Wave 4** | Exposure is up to **BDT 25 lakh** per security or rights failure, and up to **BDT 50 lakh** for a significant data fiduciary, with additional fines for repetition. Registered as **RSK-032** in `00-04` |
| **Breach cost avoidance** | Least privilege, branch isolation, field-level encryption, anomaly detection, and a leaver revoked in an hour | The category rates an identity or permission defect as **Critical — legal and contractual**. A single exposure of corporate client data ends the contract and the reference |
| **Fraud loss avoidance** | Twelve SoD combinations enforced mechanically rather than procedurally | Directly protects the controls behind purchase fraud (SOD-02), payroll fraud (SOD-03), revenue leakage (SOD-04), inventory theft concealment (SOD-05) and cash misappropriation (SOD-12) |
| **Corporate and government tender qualification** | ISO 27001 alignment, demonstrable access control, audit trail and data protection | Enterprise and government clients require this as a bid precondition. Supports **BO-11 (MSP ≥ 12% of revenue)** and the corporate segment generally |
| **Brand partner assurance** | Brands audit their authorised service partners' handling of warranty and customer data | Protects **17+ brand authorisations** |
| **Audit and close efficiency** | 100% audit coverage of financial transactions, queryable | Supports **BO-10 (zero compliance findings)** and the KPI-050 three-day close |
| **Administrative saving** | Joiner–mover–leaver automation across 800+ staff with high turnover | Removes a recurring manual IT and HR workload and the errors that come with it |
| **Data-recovery business enablement** | T5 restricted tier, case-scoped access, full logging, purge enforcement | **M06 Data Services cannot operate without it** — the business line depends on provable custody of recovered customer data |
| **Marketplace and expansion enablement** | External party rules EA-01…EA-12, seller isolation, KYC document protection | Precondition for **BO-12 (marketplace ≥ 25% of job volume)** |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **ISO 27001 and ISO 9001 evidence** | Access control, cryptography, audit and incident management are the substance of both standards. 1000FiX's ISO status is a stated competitive advantage |
| **Legal defensibility** | In a dispute over who saw or changed what, the answer is a query with a hash-chained trail behind it |
| **Ethical duty to customers** | 250,000+ customers a month entrust their devices, and often their data. Protection is an obligation before it is a compliance requirement |
| **Employee fairness** | Salary, incentive and performance data restricted by field. Staff trust in the system depends on it |
| **Institutional discipline** | Named, attributable action changes behaviour more reliably than policy |
| **Multi-country readiness** | Residency classification and jurisdiction-aware enforcement mean a second country is a configuration exercise, supporting **BO-18** |
| **Insurability** | Documented security controls materially affect cyber-insurance availability and premium |

---

## 8. Lifecycle & State Models

### 8.1 Identity Lifecycle

```
   M21 employee.joined · external party registration · service account request
              │
        ┌─────▼──────┐
        │ REQUESTED  │
        └─────┬──────┘
              │ approved: line manager (standard) ·
              │ line manager + IT Admin + CTO (privileged) — `05-04` §7
        ┌─────▼──────┐
        │ PROVISIONED│  role from the position profile · portal access ·
        └─────┬──────┘  training assigned · ✖ blocked on SoD conflict
              │ first login, MFA enrolled where required
        ┌─────▼──────┐
        │   ACTIVE   │◄──────────────────────┐
        └──┬──┬──┬───┘                       │
           │  │  │                           │ certification confirms
           │  │  │ transfer / promotion      │ · remediation complete
           │  │  ▼                           │ · return from leave
           │  │ ┌──────────┐                 │
           │  │ │ MODIFIED │ old revoked +   │
           │  │ │          │ new granted,    │
           │  │ └────┬─────┘ no accumulation │
           │  │      └──────────────────────►│
           │  │                              │
           │  │ approved elevation           │
           │  ▼                              │
           │ ┌──────────┐ time-boxed,        │
           │ │ ELEVATED │ session recorded,  │
           │ │          │ auto-expiring      │
           │ └────┬─────┘                    │
           │      └───────────────────────►──┤
           │                                 │
           │ leave · investigation ·         │
           │ certification not confirmed     │
           ▼                                 │
        ┌────────────┐                       │
        │ SUSPENDED  │ access disabled,      │
        │            │ records preserved ────┘
        └─────┬──────┘
              │ M21 employee.left · agreement expiry · termination
        ┌─────▼──────────┐
        │ DEPROVISIONED  │ ◄── **all access revoked within 1 hour**;
        └─────┬──────────┘     devices deregistered;
              │                delegated authority reassigned
        ┌─────▼──────┐
        │  ARCHIVED  │ identity retained for audit; cannot authenticate
        └────────────┘
```

| From | To | Guard | Actor |
|---|---|---|---|
| — | Requested | Joiner event, registration, or a justified access request | M21 / self / manager |
| Requested | Provisioned | Approved at the right authority; **no SoD conflict** (BRU-SEC-07) | Approver per `05-04` §7 |
| Provisioned | Active | First successful authentication; MFA enrolled where the role requires it | User |
| Active | Modified | Transfer or role change; old permissions revoked on the effective date | M21 / manager |
| Active | Elevated | Approved privileged access request; time-boxed | IT Admin + CTO |
| Elevated | Active | Elevation window expires — automatic, no action needed | System |
| Active | Suspended | Leave, investigation, or access certification not confirmed | Manager / CTO |
| Suspended | Active | Return, or remediation confirmed | Manager |
| Any | Deprovisioned | `employee.left`, agreement expiry, or termination | M21 / system |
| Deprovisioned | Archived | Retention period applies; identity kept for audit only | System |

### 8.2 Access Certification Cycle

```
   Cycle opens (quarterly)
        │
        ▼
   Every manager receives their reports' current access
        │
        ├──► CONFIRMED ──► access continues; decision recorded
        │
        ├──► REVOKED ────► access removed on decision; user notified
        │
        └──► NOT ACTIONED by the deadline
                  │
                  ▼
             **ACCESS REVOKED AUTOMATICALLY** (`05-04` §9)
                  │
                  ▼
             Manager and user notified; re-request available
        │
        ▼
   Cycle closes ──► completion reported; **KPI target 100% per cycle**
```

### 8.3 Security Incident & Breach Assessment

```
   Detection: anomaly · alert · vulnerability · report · third-party notice
        │
   ┌────▼─────┐
   │ TRIAGED  │  severity assigned (S1–S4); owner named
   └────┬─────┘
        │
   ┌────▼──────────┐
   │  CONTAINED    │  access revoked · sessions killed · systems isolated
   └────┬──────────┘
        │
   ┌────▼──────────────────────┐
   │ **BREACH ASSESSMENT**     │  Is personal data involved?
   │ (NFR-094)                 │  Is significant damage likely?
   └────┬──────────────┬───────┘
        │ no           │ yes
        │         ┌────▼──────────────────────┐
        │         │ NOTIFIABLE                │
        │         │ ──► **M60 notifies the    │
        │         │      Authority within the │
        │         │      prescribed period**  │
        │         │ ──► data subjects informed│
        │         └────┬──────────────────────┘
        │              │
   ┌────▼──────────────▼───┐
   │      REMEDIATED       │  root cause fixed; control added
   └────┬──────────────────┘
        │
   ┌────▼──────┐
   │  CLOSED   │  post-incident review; M23 CAPA where systemic;
   └───────────┘  M66 records the incident process
```

---

## 9. Business Rules

Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-SEC-01 | Admin, finance and HR portal access requires MFA at every login | **H** | CTO |
| BRU-SEC-02 | Sensitive actions — payouts, payroll finalisation, data-case access, bulk export — require step-up authentication | **H** | CTO |
| BRU-SEC-03 | Access to a data-recovery case is limited to the assigned team; every access is logged | **H** | CTO |
| BRU-SEC-04 | Recovered customer data is purged at the agreed date unless a documented hold applies | **H** | CTO |
| BRU-SEC-05 | Personal data cannot be exported in bulk without approval, and every export is logged | **H** | CTO |
| BRU-SEC-06 | A leaver's access is revoked within one hour of the leaver event | **H** | HR Director / CTO |
| BRU-SEC-07 | Incompatible duty combinations cannot be assigned; exceptions are time-boxed, mitigated and reported quarterly | **H** | CFO / CTO |
| BRU-SEC-08 | Production data used in non-production environments must be masked | **H** | CTO |
| BRU-SEC-09 | **No module implements its own authentication, session handling or permission engine** | **H** | CTO |
| BRU-SEC-10 | Every authorisation decision is evaluated server-side on every request; no client or gateway assertion is trusted | **H** | CTO |
| BRU-SEC-11 | Audit entries are insert-only and cannot be modified or deleted by any role, including administrators | **H** | CTO |
| BRU-SEC-12 | Every change to a controlled object is audited, inherited by the platform without module-level audit code | **H** | CTO |
| BRU-SEC-13 | **A residency-classified field is written only to the Bangladesh-resident store; a write to the regional store fails** | **H** | CTO / CFO |
| BRU-SEC-14 | Cross-border transfer of a residency-classified field is blocked until an Authority notification record and a documented safeguard exist | **H** | CTO / Legal |
| BRU-SEC-15 | S3-classified fields are encrypted at field level with key material separate from the database key | **H** | CTO |
| BRU-SEC-16 | Access unconfirmed at the close of a certification cycle is revoked automatically | **C** | CTO |
| BRU-SEC-17 | No account may exist without an active accountable owner for more than 24 hours | **H** | CTO |
| BRU-SEC-18 | A user may not administer their own access or approve their own access request (SOD-09) | **H** | CTO |
| BRU-SEC-19 | Privileged access is time-boxed; standing administrative rights are not granted | **H** | CTO |
| BRU-SEC-20 | Break-glass access notifies multiple parties immediately, expires automatically, and requires post-hoc justification | **H** | CTO |
| BRU-SEC-21 | A critical vulnerability open for more than 7 days is escalated to the CTO and reported to the board | **H** | CTO |
| BRU-SEC-22 | Every file upload is malware-scanned before it is stored or served | **H** | CTO |
| BRU-SEC-23 | Data under legal hold is never purged, regardless of retention schedule or erasure request | **H** | Quality Manager / Legal |
| BRU-SEC-24 | Classified fields are redacted from logs at emission | **H** | CTO |
| BRU-SEC-25 | A revoked token, suspended identity or leaver event takes effect estate-wide within 60 seconds | **H** | CTO |

---

## 10. Data Entities

### 10.1 Owned Entities

Aligned to the 14 entities allocated to M29 in `05-02` §M29, extended for PDPA 2026 and
residency.

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.identity` | `fix_identity` | The authenticating subject | subject_id, type (employee/external/service), party_id, employee_id, status, mfa_enrolled, last_login, failed_attempts, owner_user_id, provisioned_at, deprovisioned_at |
| `fix.role` | `fix_role` | The 38 roles | code (R01–R38), name, category, headcount_expected, mfa_required, default_scope_tier, portals, business_owner, active |
| `fix.permission.set` | `fix_permission_set` | Permissions per role per module | role_id, module_id, create, read, update, delete, approve, scope (own/branch/zone/entity/all) |
| `fix.record.rule` | `fix_record_rule` | Isolation tier enforcement | model, tier (T0–T5), domain_expression, applies_to_roles, company_scoped, operating_unit_scoped, zone_scoped, active |
| `fix.field.permission` | `fix_field_permission` | Field-level restriction | model, field, classification, visible_to_roles, editable_by_roles, masked_representation |
| `fix.delegation` | `fix_delegation` | Bounded authority transfer | from_user_id, to_user_id, scope, reason, valid_from, valid_to, approved_by, revoked_at |
| `fix.sod.rule` | `fix_sod_rule` | SOD-01 … SOD-12 | code, description, incompatible_permissions, risk, enforcement (block/warn), defined_by (M60), active |
| `fix.sod.exception` | `fix_sod_exception` | Time-boxed approved conflict | sod_rule_id, user_id, justification, mitigating_control, approved_by, valid_from, valid_to, reviewed_at |
| `fix.access.request` | `fix_access_request` | Request and approval | requester_id, subject_user_id, role_id, justification, approvers, decisions, state, provisioned_at, sod_evaluation |
| `fix.access.certification` | `fix_access_certification` | Periodic review | cycle, manager_id, subject_user_id, current_access_snapshot, decision (confirm/revoke/not_actioned), decided_at, auto_revoked |
| `fix.privileged.session` | `fix_privileged_session` | Elevation and recording | user_id, role_id, granted_by, reason, valid_from, valid_to, recording_ref, actions_summary, break_glass |
| `fix.audit.entry` | `fix_audit_entry` | **The immutable trail** | model, res_id, field, operation, old_value, new_value, actor_id, occurred_at, correlation_id, company_id, operating_unit_id, hash_chain_ref |
| `fix.data.access.log` | `fix_data_access_log` | Sensitive-data read log | model, res_id, classification, actor_id, purpose, occurred_at, portal, ip_hash, export_flag, record_count |
| `fix.data.classification` | `fix_data_classification` | The field label register | model, field, sensitivity (S0–S3), residency_class, lawful_basis_ref, retention_class, owning_module, classified_by |
| `fix.residency.transfer` | `fix_residency_transfer` | Cross-border transfer control | classification_id, res_id, from_region, to_region, purpose, safeguard_ref, authority_notification_ref, approved_by, executed_at, blocked_reason |
| `fix.encryption.key.ref` | `fix_encryption_key_ref` | Key material references | key_id, purpose, scope, vault_ref, algorithm, created_at, rotates_at, rotated_at, retired_at, access_roles |
| `fix.security.event` | `fix_security_event` | Detected signals | type, severity, source, subject_user_id, detail_json, occurred_at, correlated_incident_id, alerted_at |
| `fix.security.incident` | `fix_security_incident` | Incident lifecycle | number, severity (S1–S4), detected_at, owner_id, containment_at, personal_data_involved, breach_assessment, notifiable, m60_notification_ref, remediated_at, closed_at, capa_ref |
| `fix.vulnerability` | `fix_vulnerability` | Vulnerability register | source (SAST/DAST/dependency/container/pentest), identifier, severity, component, discovered_at, sla_due, remediated_at, verified_at, exception_ref |
| `fix.masking.rule` | `fix_masking_rule` | Non-production masking | model, field, strategy, deterministic, referential_key, environments |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.employee`, joiner and leaver events | M21 | Event-driven |
| `fix.party`, `fix.party.role` | M33 | Read for external identity |
| `fix.consent.record`, transparency notice, lawful basis | M33 | Read as an access precondition |
| `fix.entity`, `fix.branch`, `fix.zone`, `fix.cost.center` | M02 / M30 / M54 | Read as record-rule dimensions |
| `fix.country.pack` (jurisdiction rules) | M65 | Read for residency and transfer rules |
| `fix.sod.rule` definitions and control tests | M60 | **M60 defines; M29 enforces** |
| `fix.document`, retention class, legal hold | M24 | Read before purge |
| Vault key material | M30 platform infrastructure | Reference only; never stored here |
| `fix.api.consumer`, `fix.api.credential` | M28 | Read; M29 issues the underlying tokens |
| `fix.it.major.incident` (IT process) | M66 | Security incidents raised into the ITSM process |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-SEC-01 | `employee.joined` from M21 | Create the identity, assign the role from the position profile, grant portal access, enrol MFA where required, assign onboarding training | Queue for IT Administrator; alert |
| AUT-SEC-02 | Transfer or promotion effective date | Revoke old permissions and grant new ones atomically; no accumulation | Hold and alert the manager |
| AUT-SEC-03 | **`employee.left` from M21** | **Revoke all access within one hour**, deregister devices, terminate sessions, reassign delegated authority, notify the manager | Escalate to CTO immediately; manual revocation |
| AUT-SEC-04 | Access request submitted | Evaluate SoD, route to the right approval authority, provision on approval | **Hard block on SoD conflict**; offer the exception path |
| AUT-SEC-05 | Role assignment attempted with an incompatible combination | Block and explain which SoD rule applies and what the exception path is | Hard block |
| AUT-SEC-06 | Transaction attempted that would complete an incompatible duty combination | Block at transaction time and record the attempt | Hard block; security event raised |
| AUT-SEC-07 | Certification cycle opens | Present each manager their reports' current access with usage evidence; remind at intervals | Escalate to the manager's manager |
| AUT-SEC-08 | **Certification cycle closes with access unconfirmed** | **Revoke automatically**; notify the user and the manager; log the revocation | Hard revocation |
| AUT-SEC-09 | Privileged elevation window expires | Revoke automatically; close and retain the session recording | Hard revocation |
| AUT-SEC-10 | Break-glass access used | Notify CTO, CFO and IT Administrator immediately through an independent channel; start the justification clock | Escalate; never silent |
| AUT-SEC-11 | Orphaned account detected (no active owner) | Suspend at 24 hours; notify the last known manager and the CTO | Hard suspension |
| AUT-SEC-12 | Anomalous access detected — impossible travel, unusual volume, out-of-pattern time, bulk read | Raise a security event, correlate, alert, and step-up or suspend by severity | Alert; escalate |
| AUT-SEC-13 | Security incident triaged with personal data involved | **Run the breach assessment; if notifiable, hand off to M60 with the evidence pack and start the statutory clock** (NFR-094) | Escalate to CTO and Legal immediately |
| AUT-SEC-14 | Every build, and continuously in production | Run SAST, DAST, dependency and container scanning; load findings into the vulnerability register | Fail the build on critical findings |
| AUT-SEC-15 | Critical vulnerability open at 7 days | Escalate to CTO; report to the board; block related deployments | Hard escalation |
| AUT-SEC-16 | Penetration test report received | Load findings, assign owners and SLAs, track to verified closure | Report as open risk |
| AUT-SEC-17 | File uploaded on any portal | Malware-scan before storage or serving; quarantine on detection | Reject the upload; alert |
| AUT-SEC-18 | Bulk personal-data export requested | Require approval and step-up; log scope, requester, purpose and record count; rate-limit | Block |
| AUT-SEC-19 | Write attempted placing a residency-classified field in the regional store | **Fail the write**; raise a security event; alert the owning module team | Hard block |
| AUT-SEC-20 | Cross-border transfer of a classified field requested | Verify the safeguard and Authority notification exist; block if absent; log if permitted | Hard block |
| AUT-SEC-21 | Non-production refresh from production | Apply deterministic masking; verify no unmasked classified data remains before the environment is released | Block the refresh |
| AUT-SEC-22 | Retention period expires | Purge per the schedule unless a legal hold applies; record the purge | Retain and alert |
| AUT-SEC-23 | Data-subject right request received from M33 | Verify identity, assemble the portable export, apply rectification with 30-day controller notification, or perform verifiable erasure | Escalate to the Data Protection owner |
| AUT-SEC-24 | Token revoked or identity suspended | Propagate revocation estate-wide within 60 seconds | Alert; force session termination |
| AUT-SEC-25 | Credential or key approaching rotation date | Alert the owner; schedule rotation; escalate at expiry | Escalate |

---

## 12. Interfaces

### 12.1 Upstream — M29 Consumes

| Source | What | Mechanism |
|---|---|---|
| **M21 Core HR** | `employee.joined`, `employee.left`, transfers, position profiles | Events |
| **M60 GRC** | SoD rule definitions, control tests, risk appetite, breach-notification process | REST |
| **M33 Party Master** | External party identity, consent state, lawful basis, data-subject requests | REST + events |
| **M30 Platform Admin** | Entity, branch, zone and cost-centre structure; vault; environment definitions | REST |
| **M65 Localisation** | Jurisdiction rules driving residency and transfer control | REST |
| **M28 Integration** | API access logs, rate-limit breaches, gateway telemetry | Events |
| **M24 Documents** | Retention class and legal-hold status before purge | REST |
| M22 Learning | Security awareness training completion as an access condition | Events |
| External identity providers (corporate clients) | Federated assertions | SAML / OIDC (INT-046) |

### 12.2 Downstream — M29 Provides

| Consumer | What | Mechanism |
|---|---|---|
| **Every module (all 66)** | Authentication, authorisation decision, record rules, field permissions, inherited audit | Framework + REST |
| **All 12 portals** | Session, SSO, MFA, step-up, scope | REST |
| **M28 Integration** | Token introspection and scope resolution at the gateway edge | REST (synchronous, high availability) |
| M60 GRC | Security incidents, breach assessments, SoD violations, control evidence | Events |
| M66 ITSM | Security incidents entering the IT incident process | Events |
| M23 Quality | Security and access evidence for ISO 27001 and ISO 9001 audits | REST |
| M19 / M20 / M52 | Audit coverage of financial transactions | REST |
| M33 Party Master | Executed data-subject rights outcomes | Events |
| M25 BI / M62 | Access, audit and security telemetry | Warehouse extract |
| M06 Data Services | T5 case-scoped access enforcement and purge proof | REST + events |
| P03 Admin Portal | Security console: identities, roles, certifications, incidents, vulnerabilities | REST |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `identity.provisioned` | identity, roles, portals, provisioned by | M21, M30, M66 |
| `identity.modified` | identity, roles added, roles removed, effective date | M21, M30 |
| `identity.deprovisioned` | identity, revoked at, devices deregistered, delegations reassigned | M21, M30, M02, M15 |
| `identity.suspended` | identity, reason, suspended by | M21, M66 |
| `access.requested` | requester, subject, role, justification | approvers |
| `access.granted` | subject, role, approver, SoD evaluation | M60, M66 |
| `access.revoked` | subject, role, reason (manual/certification/leaver) | M21, M60 |
| `certification.cycle_completed` | cycle, confirmed, revoked, auto-revoked, completion rate | M60, M23 |
| `sod.violation_blocked` | user, rule, attempted combination, context | **M60**, M23, CFO |
| `sod.exception_granted` | user, rule, mitigating control, expiry, approver | **M60**, CFO |
| `privileged.session_started` | user, role, reason, expiry, break-glass flag | CTO, M66 |
| `privileged.break_glass_used` | user, systems, notified parties, justification due | CTO, CFO, M60 |
| `security.event_detected` | type, severity, subject, detail | M66, M60 |
| `security.incident_raised` | incident, severity, personal data involved | **M66**, M60, M23 |
| `security.breach_assessed` | incident, notifiable, statutory clock start, evidence pack | **M60** (Authority notification) |
| `vulnerability.critical_open` | vulnerability, component, age, owner | CTO, M66 |
| `residency.write_blocked` | model, field, attempted region, module | M30, owning module team |
| `residency.transfer_executed` | classification, purpose, safeguard, notification ref | M60, M65 |
| `data.bulk_export_performed` | requester, scope, record count, purpose, approver | M60, M23 |
| `data.purged` | model, scope, record count, retention basis | M24, M60 |
| `data_subject.right_executed` | request, right, outcome, completed at | **M33**, M60 |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| **INT-046** | Corporate client SSO (SAML / OIDC per client) | Bidirectional | B2B portal access using the client's own credentials (`05-03` §2.7, W6) |
| INT-SEC-01 | **Keycloak 26.x** | Internal | Identity provider: OIDC, MFA, federation, brokering (TD-07) |
| INT-SEC-02 | **HashiCorp Vault** (or equivalent) | Internal | Key and secret material, rotation, access audit |
| INT-SEC-03 | SAST / DAST / dependency / container scanners in CI | Inbound | Vulnerability findings into the register |
| INT-SEC-04 | Malware scanning engine | Internal | Upload scanning before storage or serving (NFR-063) |
| INT-SEC-05 | Breached-password corpus | Outbound | Password policy enforcement against known-compromised credentials |
| INT-SEC-06 | Penetration-test provider | Inbound | Annual findings into the register (NFR-067) |
| INT-SEC-07 | **National Data Management Authority** notification channel | Outbound | Breach and cross-border transfer notification — **executed by M60**, evidence supplied by M29 |

### 12.5 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/auth/token` | POST | Issue a token | All portals |
| `/api/v1/auth/introspect` | POST | **Validate and resolve scope — called on every gateway request** | **M28** |
| `/api/v1/auth/revoke` | POST | Revoke a token or session | M28, P03 |
| `/api/v1/auth/step-up` | POST | Step-up challenge for a sensitive action | All portals |
| `/api/v1/auth/mfa/enrol` | POST | Enrol or reset MFA | All portals |
| `/api/v1/authz/decision` | POST | Authorisation decision for a subject, action and resource | All modules |
| `/api/v1/identities` | GET/POST | Identity register and provisioning | P03 |
| `/api/v1/identities/{id}/suspend` | POST | Suspend an identity | P03 |
| `/api/v1/roles` | GET | The 38-role register with permission sets | P03, M60 |
| `/api/v1/access-requests` | GET/POST | Raise and track an access request | P03, all portals |
| `/api/v1/access-requests/{id}/approve` | POST | Approve within authority | P03 |
| `/api/v1/certifications/{cycle}` | GET | A manager's certification worklist | P03 |
| `/api/v1/certifications/{cycle}/decide` | POST | Confirm or revoke a report's access | P03 |
| `/api/v1/sod/evaluate` | POST | Evaluate a proposed role combination | P03, M60 |
| `/api/v1/sod/exceptions` | GET/POST | Manage time-boxed exceptions | P03, CFO |
| `/api/v1/privileged/elevate` | POST | Request time-boxed elevation | P03 |
| `/api/v1/audit` | GET | Search the audit trail by actor, object, field, time or correlation id | P03, auditors |
| `/api/v1/audit/{model}/{id}` | GET | Full change history for one record | P03, all modules |
| `/api/v1/data-access-log` | GET | Sensitive-data access log | P03, M60 |
| `/api/v1/classification` | GET/POST | Field classification register | Module teams, M64 |
| `/api/v1/residency/transfer` | POST | Request a cross-border transfer (gated) | Module teams |
| `/api/v1/security/incidents` | GET/POST | Security incident lifecycle | P03, M66, M60 |
| `/api/v1/security/vulnerabilities` | GET | Vulnerability register with SLA status | P03, CTO |
| `/api/v1/data-subject/execute` | POST | Execute an access, portability, rectification or erasure action | **M33** |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R02 Chief Technology Officer | C R U D A | All; sole approver (with CFO) of SoD exceptions and residency exceptions |
| R33 IT / System Administrator | C R U D A | All identity and access operations; **cannot approve their own access** (SOD-09) |
| R03 Chief Financial Officer | R A | SoD exceptions, financial audit coverage, breach cost assessment |
| R30 HR Manager | R | Joiner–mover–leaver status for own population; no permission-granting rights |
| R32 Quality Manager / ISO Coordinator | R | Audit evidence, security incidents, ISO control evidence |
| R05 Operations Director | R | Access certification for own reporting line |
| R06 Branch Manager | R A | Access certification for own branch staff |
| All line managers *(via their business role)* | R A | Certification and access approval for their own direct reports only |
| R01 Chief Executive Officer | R | Security posture summary; breach notifications |
| All internal users | R | **Own** identity, own sessions, own access, own audit of self |
| R36 / R37 / R38 External parties | R U | Own credentials and own MFA only |

**Separation from business roles.** M29 grants no business permission to itself. The CTO can
configure the permission engine and cannot approve a purchase order, raise an invoice or view a
payslip — the engine constrains its own administrators.

**Field-level restrictions inside M29.** Audit and data-access-log views **mask the values of
S3-classified and residency-classified fields by default**; an administrator investigating an
access anomaly sees that a field was read, not what it contained. Unmasked inspection requires
CTO approval, step-up authentication, and is itself logged as a data access.

**Segregation of duties.**
- **SOD-09 enforced here:** administering users and approving one's own access request — hard block.
- The definer of an SoD rule (M60) cannot be its approver of exceptions (CFO/CTO).
- The person who triages a security incident cannot be the sole approver that it is non-notifiable.
- Key rotation and key-access approval are separate actors.
- A manager cannot certify their own access.

---

## 14. Reports & Analytics

| Report / Dashboard | Audience | Frequency | Key Content |
|---|---|---|---|
| **Security posture dashboard** | CTO, CEO, board | Monthly | MFA coverage, orphaned accounts, open critical vulnerabilities, incidents by severity, certification completion |
| **Access certification status** | CTO, all managers | Per cycle | Completion by manager, access confirmed, revoked, auto-revoked — **target 100% per cycle** |
| **Orphaned and stale accounts** | IT Administrator, CTO | Daily | Accounts without an active owner, dormant accounts, leavers with residual access — **target zero beyond 24 h** |
| **SoD violation and exception register** | CFO, CTO, Internal Audit, M60 | Monthly | Blocked attempts by rule, live exceptions with mitigating controls and expiry, exceptions overdue for review |
| **Vulnerability register** | CTO, IT Administrator | Weekly | Open by severity and age; **critical open > 7 days — target zero**; remediation SLA attainment |
| Security incident register | CTO, Quality Manager, M60 | Monthly | Incidents by severity, containment time, breach assessments, notifications made |
| **Audit coverage** | CFO, Quality Manager, external auditor | Quarterly | Coverage of financial transactions — **target 100%**; controlled objects without audit |
| Privileged access report | CTO, Internal Audit | Monthly | Elevations granted, duration, break-glass uses, sessions recorded and reviewed |
| **Data access and export log** | CTO, M60, Quality Manager | Monthly | Access to personal and S3 data by actor and purpose; bulk exports with approver |
| **Residency compliance** | CTO, CFO, Legal | Monthly | Blocked writes, executed cross-border transfers with safeguards, classification coverage |
| Data-subject rights execution | M60, Legal, CTO | Monthly | Requests by type, execution time against the 30-day rectification duty, outcomes |
| Joiner–mover–leaver performance | HR Director, CTO | Monthly | Time to provision, time to revoke — **target ≤ 1 hour for leavers** |
| Authentication and anomaly report | IT Administrator, CTO | Weekly | Failed logins, brute-force attempts, impossible travel, blocked anomalies |
| Non-production masking assurance | CTO, Internal Audit | Per refresh | Confirmation that no unmasked classified data exists in any non-production environment |
| Regulatory currency review | CTO, Legal | Quarterly | Statutory basis re-verified with dates and owners (see §4 design position five) |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W4 Target | W8 Target |
|---|---|---|---|---|
| — | **MFA coverage on privileged accounts** | 0% | **100%** | **100%** |
| — | **Orphaned accounts after a leaver** | unknown | **Zero beyond 24 h** | **Zero beyond 24 h** |
| — | **Access certification completion** | n/a | **100% per cycle** | **100% per cycle** |
| — | **Critical vulnerabilities open > 7 days** | unknown | **Zero** | **Zero** |
| — | **Audit coverage of financial transactions** | partial | **100%** | **100%** |
| — | Leaver access revoked within 1 hour | unknown | 98% | **100%** |
| — | SoD violations reaching production data | unknown | **Zero** | **Zero** |
| — | Live SoD exceptions overdue for review | n/a | **Zero** | **Zero** |
| — | Cross-branch or cross-customer data exposure incidents | unknown | **Zero** | **Zero** |
| — | Residency-classified fields written to the wrong store | n/a | **Zero** | **Zero** |
| — | Fields with a completed classification | 0% | 95% | **100%** |
| — | Cross-border transfers with a safeguard and notification record | n/a | **100%** | **100%** |
| — | Data-subject rectifications completed within 30 days | n/a | **100%** | **100%** |
| — | Non-production environments containing unmasked classified data | unknown | **Zero** | **Zero** |
| — | Privileged sessions recorded | 0% | 100% | **100%** |
| — | Authorisation decision latency p95 | n/a | < 25 ms | **< 15 ms** |
| — | Token introspection availability | n/a | 99.95% | **≥ 99.99%** |
| — | Security incidents with breach assessment completed within SLA | n/a | **100%** | **100%** |

> **Register note.** `_CATEGORY_OVERVIEW.md` §9 names five of these as the category KPIs owned
> by M29. **None has a canonical `KPI-0nn` identifier** — `06-02` §2.6 ends at KPI-049 with no
> security or platform section. Allocation for all eighteen metrics is an audit action.

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo `base` security model — groups, ACLs, record rules as the substrate | 12% |
| L2 | OCA `server-tools` (audit log, technical utilities), OCA `web` (Keycloak authentication) | 14% |
| L4 | **Keycloak 26.x**, **Vault**, SAST/DAST/dependency/container scanners, malware scanning engine | 24% |
| L5 | `cd_rbac_ext`, `cd_audit_ext`, `cd_sod`, `cd_identity_ext`, `cd_data_protection` | 50% |

### 16.2 Custom Development

> ⚠ **CD identifiers in this table are PROVISIONAL and currently collide.** 2 of 5 identifiers below are claimed by another module: **CD-157** also claimed by M17, M19; **CD-158** also claimed by M17, M19. `CD-` is a programme-wide identifier space; under RG-01 (extended) it must be allocated by `02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md`, which is the sole allocating authority. **Do not create a build backlog item, repository or work package from any identifier in this table until `02-05` has reissued it.** *(Audit finding H2-05; re-verified 2026-08-13 as A3-05.)*

| CD ID | Component | Type | Effort |
|---|---|---|---|
| CD-130 | `cd_rbac_ext` — role register, permission sets, six-tier record rules, field permissions, delegation, approval authority, server-side decision service | Odoo module + service | 8 PW |
| CD-131 | `cd_audit_ext` — inherited immutable audit, hash chaining, data-access logging, bulk-export control, audit search and retention, processing records | Odoo module | 6 PW |
| CD-132 | `cd_sod` — SoD evaluation at assignment and at transaction, exception lifecycle, access request, **access certification with auto-revocation**, privileged access and break-glass | Odoo module | 6 PW |
| **CD-157** | `cd_identity_ext` — identity lifecycle, Keycloak integration, MFA and step-up, session policy, corporate SSO federation, device trust, service accounts, anomaly defence, joiner–mover–leaver automation | Odoo module + service | 6 PW |
| **CD-158** | `cd_data_protection` — **field classification, residency enforcement at write time, resident-key join, cross-border transfer gate**, field-level encryption, key references, masking, retention and purge, data-subject right execution, vulnerability and incident register | Odoo module + service | 5 PW |

> CD-130…132 retain their `02-05` §5.2 allocation. **CD-157 and CD-158 are claimed from the
> extension block** for modules M31–M67 and reflect the v2.1 extension of M29 for PDPA 2026 and
> split residency, which did not exist in the v1.0 scope. **All CD IDs remain provisional**
> pending the unified CD register required by audit finding M-01 in `02-05`.

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| **M28 Integration** | The gateway calls introspection on every request. M28 and M29 bootstrap each other in W1 — see M28 Q-01 |
| **M30 Platform Admin** | Entity, branch, zone and cost-centre structure are the record-rule dimensions. Also W1 |
| Infrastructure: Keycloak, Vault | Provisioned before any module is built |
| **DEP-31 legal opinion on split residency** | **Blocking.** `05-06` §6.4 states the legal opinion is required **before the Wave 1 architecture is fixed**. NFR-086a puts residency enforcement in the platform, so the answer changes the data model, not just a configuration |
| M21 Core HR (W5) | Joiner–mover–leaver automation. Until W5, identity lifecycle is manual with the same controls |
| M60 GRC (W6) | SoD rule *definition* and control testing. **Until W6, the twelve `05-04` §6 rules are configured directly in M29 and ownership transfers to M60 on delivery** |
| M33 Party Master (W1) | Consent and data-subject request lifecycle; external party identity |
| M65 Localisation (W9) | Jurisdiction rules; until W9, Bangladesh is the only jurisdiction and its rules are configured directly |

> **PDPA readiness is a Wave 4 gate, not a Wave 9 one.** Enforcement activates around
> **13 May 2027**, which falls inside Wave 4. FR-SEC-047 through FR-SEC-052 — classification,
> residency, transfer control, masking, rights execution and purge — must be **complete and
> tested by the Wave 4 gate**, not deferred to the expansion waves. This is the single most
> time-critical commitment in Category K.

### 16.4 Data Migration

| Source | Volume | Target Entity | Wave |
|---|---|---|---|
| Existing user accounts | ~150–250 internal | `fix.identity` | W1, **all credentials reset on migration** |
| Existing customer portal accounts | 250,000+ | `fix.identity` (external) | W2, with forced re-authentication |
| Role definitions | Authored from `05-04` §1 | `fix.role`, `fix.permission.set` | W1, authored not migrated |
| Field classification | **Authored per module as each is built** | `fix.data.classification` | W1 onward |
| SoD rules | Authored from `05-04` §6 | `fix.sod.rule` | W1, authored |
| Historical audit | None exists | — | **Not migrated** |

> **Position on credentials.** Every migrated internal account has its credential **reset**, not
> carried across. Existing passwords were set under an unknown policy in a system with no MFA;
> importing them would import the weakness. Customer accounts force re-authentication on first
> use rather than a mass reset, to avoid a support incident at scale.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | No module implements its own authentication, session handling or permission engine | Code review and dependency analysis across all modules at each wave gate |
| AC-02 | Every controlled object change is audited without module-level audit code | Model-registry check in CI plus coverage report |
| AC-03 | Audit entries cannot be modified or deleted by any role, including database administrators | Negative test plus database privilege review |
| AC-04 | A branch user cannot read another branch's records through the UI, the API, a report or an export | Negative test suite across all six isolation tiers and all 12 portals |
| AC-05 | Every field-level restriction in `05-04` §5 is enforced, including in exports and API responses | Negative test per restricted field group |
| AC-06 | All twelve SOD combinations are blocked at role assignment **and** at transaction time | Negative test per rule, both paths |
| AC-07 | An SoD exception expires automatically and appears on the quarterly review | Time-shifted scenario |
| AC-08 | A leaver's access is fully revoked within one hour of the leaver event | Twelve weeks of measured leaver events |
| AC-09 | Access unconfirmed at certification close is revoked automatically | Full cycle executed with a deliberate non-response |
| AC-10 | MFA is enforced on 100% of privileged accounts at every login | Configuration audit plus login log review |
| AC-11 | Privileged access is time-boxed with no standing administrative rights, and every session is recorded | Configuration audit plus recording sample |
| AC-12 | Break-glass access notifies multiple parties within one minute through an independent channel | Drill |
| AC-13 | **A write placing a residency-classified field in the regional store fails** | Negative test per classified field |
| AC-14 | **A cross-border transfer of a classified field is blocked without a safeguard and Authority notification record** | Negative test |
| AC-15 | 100% of fields carry a sensitivity and residency classification | Coverage assertion at each wave gate |
| AC-16 | S3-classified fields are encrypted with key material separate from the database key | Cryptographic review |
| AC-17 | No non-production environment in any region contains unmasked classified data | Automated scan per refresh |
| AC-18 | Data-subject access, portability, rectification and erasure execute end to end, with rectification notified within 30 days | Scripted scenario per right |
| AC-19 | Data under legal hold survives a retention purge and an erasure request | Negative test |
| AC-20 | Authorisation adds ≤ 15 ms at p95 and introspection sustains ≥ 99.99% availability | Performance test at production load |
| AC-21 | A revoked token or suspended identity takes effect estate-wide within 60 seconds | Propagation test |
| AC-22 | A security incident involving personal data completes a breach assessment and hands off to M60 within SLA | Scripted incident exercise |
| AC-23 | No critical vulnerability remains open beyond 7 days | Twelve weeks of register measurement |
| AC-24 | Every file upload is malware-scanned before storage or serving | Negative test with a test payload |
| AC-25 | Classified field values are absent from all logs | Log inspection across all services |
| AC-26 | Annual penetration test findings are tracked to verified closure | Findings register |
| AC-27 | CTO and CFO sign off UAT; external security review confirms the control set | Signed UAT record plus review report |

**Definition of done:** all 15 criteria in `02_Architecture/02-02` §7 plus the 27 criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | **Does the February 2026 amendment (Ordinance No. 23 of 2026), which narrowed data localisation to restricted and critical-information-infrastructure data, change the scope of NFR-086?** The current residency-classified field list may be broader than the statute now requires. Narrowing it would materially reduce cost and architectural complexity. | **Legal / CTO** | **W1 minus 2 months — blocking, with DEP-31** |
| Q-02 | **DEP-31: when does the legal opinion on split residency arrive?** `05-06` §6.4 states it is required before the Wave 1 architecture is fixed. It is on the critical path for the data model. | Legal / CTO | **W1 minus 2 months — blocking** |
| Q-03 | Is 1000FiX a *significant data fiduciary* under the PDPA? The answer determines the BDT 50 lakh exposure ceiling and whether a Chief Data Officer must be appointed (NFR-096). | Legal / CEO | W2 |
| Q-04 | Is the regulator the **National Data Management Authority** (as `05-06` §6.3 states) or the **Data Protection Office/Board** (as external sources describe)? The notification channel and its format depend on the answer. | Legal / M60 owner | W3 |
| Q-05 | Where is the Bangladesh-resident store physically hosted, who operates it, and what is its availability and DR posture? A resident store with weaker availability than the regional one becomes the system's weakest link. | CTO / CFO | W1 build |
| Q-06 | What is the access certification cadence — quarterly for all roles, or risk-tiered with privileged roles monthly? | CTO / CFO | W1 build |
| Q-07 | Are privileged session recordings retained, for how long, and who may review them? This is itself sensitive personal data about employees. | CTO / HR Director / Legal | W2 |
| Q-08 | Which corporate clients will federate their identity providers, and what is the onboarding effort per client (INT-046)? | Corporate Services Head / CTO | W6 |
| Q-09 | Until M60 lands in W6, who owns SoD rule *definition* and control testing? M29 will hold both definition and enforcement for five waves, which is itself a segregation weakness. | CFO / CTO | W1 build |
| Q-10 | What is the breach-notification timeframe prescribed by the Authority, and does 1000FiX have a tested process capable of meeting it? | Legal / M60 owner | W3 |
| Q-11 | Is device trust mandatory for technician and rider apps, or advisory? Mandatory device binding is stronger but creates a field support burden when a device is lost or replaced. | CTO / Operations Director | W2 |

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` §6 (boundary map — **M60 defines SoD, M29 enforces**), §7 (promises 3
and 4), §9 (category KPIs), §11 (critical identity/permission risk) ·
`M28_Integration_API_and_Event_Platform.md` (gateway edge, token introspection) ·
`M30_Platform_Administration_and_Configuration.md` (org structure, vault, environments) ·
`M65_Multi_Entity_Multi_Country_and_Localisation.md` (jurisdiction rules driving residency) ·
`M66_Internal_IT_Service_Management.md` (security incidents in the IT incident process) ·
`M60` Governance, Risk & Compliance *(Category I — SoD definition, Authority notification, CDO)* ·
`M33` Customer & Party Master Management *(Category B — consent, transparency, data-subject request lifecycle)* ·
`05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md` §1 (38 roles),
§2 (portal matrix), §3 (module matrix), §4 (T0–T5 isolation tiers), §5 (field permissions),
§6 (SOD-01…SOD-12), §7 (approval authority), §8 (EA-01…EA-12), §9 (access lifecycle), §10 ·
`05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md`
§4 (NFR-011…015, NFR-061…072), §6.1 (regulatory currency), §6.3 (**NFR-090…099 PDPA 2026**),
§6.4 (**NFR-086, 086a–c split residency**), AS-14, DI-08, OPS-04 ·
`05_Cross_Cutting_Specifications/05-05_Business_Rules_and_Automation_Catalogue.md` §11 (BRU-SEC-01…08) ·
`05_Cross_Cutting_Specifications/05-02_Data_Model_and_Entity_Catalogue.md` §M29 (14 entities), DM-05 ·
`02_Architecture/02-01_ERP_Module_Architecture_and_System_Map.md` §8 (isolation tiers), §10 (AS-14) ·
`02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md` §5.2 (CD-130…132), TD-07 ·
`00_Governance_and_Charter/00-04_Risks_Assumptions_Dependencies_and_Governance.md`
**DEP-31** (split-residency legal opinion), **D-13**, **RSK-032** (PDPA penalty exposure)

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` (security and access requirements) ·
`1000FiX_Services_Company_Profile.md` §Quality & Certification (ISO), §Competitive Advantages
("100% Secure device and data handling")

**External benchmark and regulatory basis**
[SAP Cloud Identity Access Governance — Access Analysis, Certification, Request, PAM, Role Design](https://sapinsider.org/sap-cloud-identity-access-governance/) ·
[SAP IAG overview and product updates](https://community.sap.com/t5/financial-management-blog-posts-by-sap/sap-cloud-identity-access-governance-iag-overview-and-product-updates/ba-p/13447679) ·
[Identity governance and administration practice — access review, request, approval, SoD detection](https://pathlock.com/learn/identity-governance-administration-iam-data-security/) ·
[SAP IAG for access governance — SoD risk analysis, recertification, PAM](https://togglenow.com/blog/sap-iag-for-enhanced-access-governance/) ·
[Bangladesh Personal Data Protection Act 2026 — overview](https://securiti.ai/bangladesh-personal-data-protection-act-overview/) ·
[Bangladesh data protection: PDPO 2025, Amendment Ordinance No. 23 of 2026 narrowing localisation to restricted and CII data, enforcement from ~13 May 2027](https://www.security.land/bangladesh-data-protection-law-localization/) ·
[Bangladesh cross-border data transfer regulation — ITIF](https://itif.org/publications/2025/05/16/bangladesh-cross-border-data-transfer-regulation/) ·
[Bangladesh data protection law — complete guide](https://tahmidurrahman.com/bangladesh-data-protection-law-2/) ·
ISO/IEC 27001:2022 Annex A · Keycloak, HashiCorp Vault documentation ·
Bangladesh Cyber Security Ordinance 2025 · ICT Act 2006

---

*Module M29 · Category K · 1000FiX ERP System v2.0 · CONFIDENTIAL*
