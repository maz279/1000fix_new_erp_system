---
id: SC-004
title: Identity, Authentication and Authorisation Design
category: 05 — Security, Privacy & Compliance
code: SC
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Chief Technology Officer, delegated to the Security Lead
approver: Design Authority (constituted under GV-002)
standards_basis: >
  OAuth 2.1 (RFC 9700 best current practice) · OpenID Connect Core 1.0 · RFC 7662 token
  introspection · RFC 7636 PKCE · RFC 8705 mTLS client authentication · SAML 2.0 (federation) ·
  NIST SP 800-63-4 (digital identity, AAL) · ISO/IEC 27001:2022 A.5.15–A.5.18, A.8.2–A.8.5 ·
  OWASP ASVS 5.0.0 chapters on authentication, session management and authorization
traces_to: >
  PGD-000 SC-004 · M29 FR-SEC-001…036 · 05-04 §1…§9 · 05-06 NFR-011, NFR-012, NFR-015,
  NFR-064, NFR-065, NFR-069 · SC-001 §6, §7 · SC-002 TH-001…TH-014, TH-076…TH-083 ·
  audit findings OP-10, H2-07, A3-17, A3-20, PGD-A3-06, RQA-04
depends_on: SC-001 (enforcement model) · AR-001 (identity realisation) · GV-002 (approval body)
verified_on: 2026-08-18
priority: P0
needed_by: W1
enumeration_timestamp: 2026-08-18 13:40 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# SC-004 — Identity, Authentication and Authorisation Design

### Category 05 · Code `SC` · OAuth 2.1 / OIDC Core 1.0 · NIST SP 800-63-4 · ISO/IEC 27001:2022

---

> **Before writing, read this.**
>
> 1. **`PG-01` Register-first.** This document's row exists in `PGD-000` Category 05 as `SC-004`.
> 2. **`PG-03` Count, do not consult.** Role and identifier figures were counted from the module
>    files at **2026-08-18 13:40 (+06)**, not taken from `05-04`. The two disagree, and §2.4
>    records by how much.
> 3. **`PG-06` Cite standards.** §2.1.
> 4. **`PG-M4` Verify citations.** Vendor versions and RFC status verified 2026-08-18.

---

## 1. Purpose

This document specifies **who can be, and what they can do**: the Keycloak realm and client model,
the authentication policy per population, token lifetimes and claims, federation with corporate
clients, session management, service-to-service authentication, and — the largest single piece of
work — the **realisation of the role model from 38 registered roles to the 50 the estate actually
uses**, with a bound access profile for each.

It exists because of a specific, quantified gap. Audit `OP-10` (High) records two compounding
failures:

> *"`05-04` carries 38 roles. `OP-015` §4.2 makes the standard profile the mechanism that keeps 38
> roles administrable… **No profile has been authored for any role.** Until they exist, every W1
> grant is bespoke and justified by precedent — which is the exact failure mode `OP-015` §1 exists
> to prevent."*

and

> *"the segregation-of-duties register is not in a state that can be enforced… **nine numbers carry
> two different meanings**. Grant-time enforcement cannot be built against an identifier space in
> that condition."*

Audit `OP-17` puts it more bluntly: *"the 38 access profiles are all documented and none exists."*

**Counted at 13:40 (+06), the position is worse than 38.** Module files use `R39`…`R50` — twelve
roles that `05-04` does not register — plus `R54` and `R57`, which are used and **defined nowhere
at all**. `SC-002` `TH-082` rates the consequence High: *an unregistered role has no permission
set, so no SoD rule evaluates against it.* An unregistered role is not merely undocumented; it is
**invisible to the control that is supposed to constrain it**.

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | **The 50-role register** — `R01`…`R50` consolidated, with the three superseded-identifier rulings |
| 2 | **`R38` sub-typing** — 17 external party identities decomposed into `R38.1`…`R38.17` |
| 3 | **Access profiles `AP-R01`…`AP-R50`** — the bound triple (object permissions, isolation tier, field restrictions) |
| 4 | **Keycloak realm, client and role topology** — what lives in the IdP and what deliberately does not |
| 5 | **Authentication policy per population** — password, MFA, step-up, device trust, mapped to NIST SP 800-63-4 assurance levels |
| 6 | **Token design** — types, lifetimes, claims, audience, revocation, and the introspection contract |
| 7 | **Federation** with corporate client identity providers (`INT-046`) |
| 8 | **Session management** — idle, absolute, concurrency, and forced revocation |
| 9 | **Service-to-service and machine identity** |
| 10 | **The joiner–mover–leaver design**, including the one-hour rule and its 60-second propagation |
| 11 | **Access certification** design |
| 12 | **Privileged access management** — elevation, session recording, break-glass integration |
| 13 | **The SoD identifier ruling** and the enforcement contract against `SP-006` |

**Explicitly out of scope:**

| Topic | Owned by | Why |
|---|---|---|
| The enforcement-point architecture | `SC-001` §7 | This document configures the points; it does not decide where they are |
| Cryptographic algorithms, key lifetimes, signing keys | `SC-006` | Token signing algorithm and key rotation are `SC-006`'s |
| Audit log content and immutability | `SC-010` | This document names *what must be attributable*; `SC-010` specifies the record |
| SoD rule **definitions** | `SP-006`, `M60` | `M60` defines and tests; `M29` enforces (`BRU-GRC-11`). This document specifies the enforcement contract |
| Approval thresholds by value | `SP-004`, `05-04` §7 | Financial authority, not identity |
| Keycloak deployment, HA, sizing | `PE-001`, `PE-006` | Infrastructure |
| Identity runbook, on-call procedure | `OP-009`, `OP-015` | Operations content |
| Business meaning of a permission | The owning module | `M29` §3 boundary — identity owns *who may*, not *what it means* |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| **Platform Squad / `M29` developers** | §5 realm topology, §6 authentication, §7 tokens — the build specification |
| **Security Lead** | §4 role ruling, §12 privileged access |
| **Business owners of roles** | §8 access profiles — **the profile for your role is yours to sign off** (`05-04` §10 criterion 8) |
| **CFO / Internal Audit** | §11 SoD enforcement contract; §10 certification |
| **QA (`QA-007`)** | §8 profiles are the **negative-test basis**; §14 acceptance |
| **HR** | §9 joiner–mover–leaver triggers and the one-hour obligation |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | How this document conforms | Departure and rationale |
|---|---|---|
| **OAuth 2.1 / RFC 9700** *(OAuth 2.0 Security Best Current Practice; verified 2026-08-18)* | §7 adopts the current BCP: **PKCE for every authorization-code flow including confidential clients**, exact redirect-URI matching, **no implicit grant**, **no resource-owner password grant**, sender-constrained or short-lived refresh tokens with rotation | The estate's `05-03` §5.1 names *"OAuth 2.0"* generically and PKCE for the technician API only. **PKCE is applied to all six public clients here**, which is a tightening, not a departure |
| **OpenID Connect Core 1.0** | ID token for authentication; access token for authorisation; strict audience validation | — |
| **RFC 7662 Token Introspection** | `Z1` introspects rather than validating locally (`SC-001` `SEC-TK-1`) | Local JWT validation would be faster and is **deliberately rejected**: it makes 60-second revocation (`BRU-SEC-25`) impossible |
| **RFC 8705** | mTLS client authentication for service-to-service and for high-value external consumers | — |
| **SAML 2.0** | Corporate federation where a client's IdP does not support OIDC | Both protocols supported; OIDC preferred |
| **NIST SP 800-63-4** *(verified 2026-08-18)* | §6 maps each population to an **authenticator assurance level** rather than asserting "MFA where required" | 800-63-4 also defines identity- and federation-assurance levels. **IAL and FAL are assessed only for `P-CORP` federation**; full IAL proofing is disproportionate for a consumer repair service |
| **ISO/IEC 27001:2022** A.5.15–A.5.18, A.8.2–A.8.5 | Access control, identity management, authentication information, access rights, privileged access | `SC-001` §9.2 families 1–4 |
| **OWASP ASVS 5.0.0** | Authentication, session management and authorization chapters are the verification basis; `SC-005` binds them to the gate | Level 2 baseline; **Level 3 for the admin API and any `Z4`-touching path** (`SC-001-D-07`) |

### 2.2 Source material

| Source | What it supplies |
|---|---|
| `05-04` §1 | The **38-role register** — the baseline this document extends |
| `05-04` §2, §3 | Portal access matrix; module permission matrix with CRUDA and scope suffixes |
| `05-04` §4, §5 | Six isolation tiers; **13 restricted field groups** |
| `05-04` §6, §7, §8, §9 | `SOD-01`…`SOD-12`; approval authority; `EA-01`…`EA-12`; access lifecycle |
| `05-04` §10 | **Role definition-of-done — 8 criteria.** §8 of this document is built to satisfy them |
| `M29` §5.1–§5.4 | `FR-SEC-001`…`FR-SEC-036` |
| `M29` §8.1 | The identity lifecycle state model, adopted verbatim in §9 |
| `SP-006` §4.2–§4.6 | `SOD-01`…`SOD-60` and the nine-collision resolution |
| `00-07` H2-07 | Roles `R39`–`R46` unregistered; `R54`, `R57`, `R60` undefined |
| `_MODULE_SET_AUDIT_REPORT` A3-17, A3-20 | **Extend to `R50`**; `R38` carries **17** external identities |
| `AR-001` §9.1 | Identity realisation split — **and the "46 roles" figure this document corrects** |
| `OP-009`, `OP-015` | Identity runbook and JML content; break-glass `BG-10`, `BG-11` |
| `02-05` `TD-07` | Keycloak 26.x |

### 2.3 Audit findings this document closes

| Finding | Source | Disposition |
|---|---|---|
| **`OP-10`(a)** — no access profile authored for any role | `AUDIT-017` | **Closed.** §8 authors 50 profiles as a bound triple with a signing owner |
| **`OP-10`(b)** — SoD identifier space unenforceable | `AUDIT-017` | **Closed by ruling.** §11 makes `SP-006` the enforcement source of record and `05-04` §6 a derived view |
| **`H2-07`** — `R39`–`R46` unregistered; `R54`, `R57`, `R60` undefined | `00-07` | **Closed with correction.** The counted range is `R39`–`R50`, not `R39`–`R46`; `R60` is already retired to `R49`, so `00-07`'s remediation item 5 is **superseded** |
| **`A3-17`** — extend `05-04` to `R50` | `_MODULE_SET_AUDIT` | **Closed.** §4.2 |
| **`A3-20`** — `R38` carries 17 external identities | `_MODULE_SET_AUDIT` | **Closed.** §4.4 sub-types to `R38.1`…`R38.17` |
| **`PGD-A3-06`** — `AR-001` §9.1 states 46 roles | `PGD-AUDIT-003` | **Closed with correction.** 50. Raised to `AR-001` |
| **`RQA-04`** — `R39`–`R50` and `SOD-13`–`SOD-30` used and unregistered | `PGD-AUDIT-004` | **Closed.** §4.2 and §11 |
| `OP-15` — leaver revocation has two deadlines 23 hours apart | `AUDIT-017` | **Ruled.** §9.4: the **one-hour rule governs**; `KPI-090` is wrong and is escalated |
| `SC-002` `TH-080`, `TH-082`, `TH-083` | `SC-002` | Closed by §4 |

### 2.4 Enumeration — counted, and where it disagrees

Counted from `1000fix_ERP_Module/` at **2026-08-18 13:40 (+06)**.

| # | Figure | **Counted** | Published | Disposition |
|---|---|---:|---|---|
| 1 | Roles registered in `05-04` §1 | **38** | 38 | ✓ |
| 2 | Role identifiers **above `R38`** in use | **12** — `R39`…`R50` | `R39`–`R46` (`00-07`, `AR-001` §9.1) · `R39`–`R50` (`A3-17`) | **50 is the target.** `AR-001`'s 46 is superseded |
| 3 | Occurrence counts | `R39`:14 · `R40`:15 · `R41`:6 · `R42`:2 · `R43`:3 · `R44`:4 · `R45`:2 · `R46`:10 · `R47`:6 · `R48`:4 · `R49`:9 · `R50`:11 | — | **None is a one-off typo.** The lowest, `R42` and `R45`, appear twice each in different files |
| 4 | Identifiers used with **no definition anywhere** | **2** — `R54` (M39), `R57` (M46) | 3, incl. `R60` | **`R60` no longer appears in any module file.** It survives only in two audit reports |
| 5 | `R38` external sub-identities | **17** | 17 (`A3-20`) | ✓ |
| 6 | `SOD` identifiers in module files | **30** — `SOD-01`…`SOD-30` | 12 (`05-04` §6) · 60 (`SP-006`) | `05-04` §6 is **18 short of live usage** |
| 7 | Restricted field groups | **13** (`05-04` §5) | 13 | ✓ |
| 8 | Portals in the access matrix | **12** | 12 | ✓ |
| 9 | Access profiles authored before this document | **0** | *"all documented"* (`OP-10`) | **The gap `OP-10` names** |

---

## 3. Design Position

Six positions, stated first so the detail is arguable against them.

| # | Position | Because |
|---|---|---|
| `SC-004-P1` | **Keycloak holds identity and authentication. It does not hold business authorisation.** Realm roles map to Odoo groups; record scope and field visibility live with the data | `SC-001-D-02`. Business permissions depend on business data — this branch, this contract, this customer. Duplicating that into an IdP guarantees drift |
| `SC-004-P2` | **A role is not a permission set. A role is a *profile* — a bound triple of object permissions, an isolation tier and field restrictions** | This is the shape `OP-015` §4.2 requires and `OP-10` says does not exist. A role granted without a tier defaults to whatever the model's default rule is, which is the widest one |
| `SC-004-P3` | **50 roles, built in Wave 1, not 38 now and 12 later** | `AR-001` `TR-13`: adding roles after go-live means retrofitting record rules and field permissions **across live data**. The 12 are already in use in module specifications; they are not speculative |
| `SC-004-P4` | **`R38` is sub-typed before external onboarding, not after** | One identifier for 17 external party classes means a rule written for couriers applies to external auditors. `SC-002` `TH-083`, `AB-08` |
| `SC-004-P5` | **Authentication assurance is set per population and per action, not per role** | A customer performing a payout-affecting action needs stronger assurance than the same customer viewing an invoice. Step-up is an action property (`SC-001` `SEC-TK-4`) |
| `SC-004-P6` | **Revocation is the design centre, not an afterthought** | `BRU-SEC-06` (one hour) is unachievable without `BRU-SEC-25` (60-second propagation), and 60-second propagation is impossible with locally-validated long-lived JWTs. **This single requirement determines the token design** |

---

## 4. The Role Model

### 4.1 The ruling on three contested identifiers

Two audits gave **contradictory** remediations for the same defect. The later one already
executed. This is the ruling.

| Identifier | `00-07` H2-07 said | `_MODULE_SET_AUDIT` did | **Ruling** |
|---|---|---|---|
| **`R60`** | *"Eliminate `R60` in favour of `R32`"* — on the reading that GRC/Internal Audit **is** the Quality Manager's role | **Created `R49` GRC / Internal Audit** as a distinct role and migrated `R60`'s usages to it | **`R49` stands. `R60` is retired and permanently withdrawn.** The module-set audit is later, it is evidenced by 9 live `R49` usages against **0 live `R60` usages**, and it is substantively right: **ISO 9001 clause 9.2 requires audit independence, so the auditor of the quality system cannot be the quality manager** (`SOD-20`). Merging them would have created an SoD violation to fix an identifier collision |
| **`R54`** | Used in `M39` as *"R54-scope FP&A users"*; **no definition exists** | — | **Resolve to `R54` FP&A Analyst**, or delete the reference. §4.3 registers it provisionally; **`Q-02` decides** |
| **`R57`** | Used in `M46` in a data-restriction rule; **no definition exists** | — | **Resolve to `R57` Fleet Administrator**, or delete. §4.3 registers it provisionally; **`Q-02` decides** |

> **`SC-004-F-01`. `R60` is the most instructive defect in this estate, and it was nearly fixed the
> wrong way.** `00-07` correctly called a duplicate role identity *"a live security defect, not a
> documentation defect"* — and then proposed a remedy that would have merged an auditor with the
> auditee. **The identifier problem was real; the proposed merge would have created a control
> failure.** This is why §11 requires SoD evaluation over the *resolved* role set, and why the
> ruling is recorded here rather than left to whichever document is read first.

### 4.2 The 50-role register

`R01`…`R38` are **reproduced from `05-04` §1 without alteration** — this document extends the
register, it does not restate or renumber it (`CP-02`: identifiers are permanent). `R39`…`R50` are
registered here with the definitions already written in the module files that use them.

**Newly registered — `R39`…`R50`:**

| ID | Role | Introduced in | Definition | Headcount | Portals | MFA | Default tier |
|---|---|---|---|---:|---|:--:|:--:|
| `R39` | **Data Steward** | `M33` | Party, catalogue and master-data stewardship; merge and quality queue authority | 2–5 | P03 | **Yes** | `T0`/`T1` |
| `R40` | **Chief Data Officer** | `M33` + 8 modules | `NFR-096` statutory role; primary Authority contact; data-protection decisions | 1 | P03, P06 | **Yes** | `T1` + `T5` grant |
| `R41` | **Payroll Officer** | `M56` | **Prepare only — cannot approve or release** (`SOD-03`, `SOD-29`) | 2–4 | P03 | **Yes** | `T1` |
| `R42` | **Training Coordinator** | `M22` | Course, cohort and certification administration | 2–4 | P03 | No | `T1` |
| `R43` | **Competency Assessor** | `M22` | Scoped assessment authority; cannot assess own reports | 10–25 | P03 | No | `T3` |
| `R44` | **HSE Officer** | `M59` | Health, safety and incident management | 2–5 | P03, P11 | No | `T1` |
| `R45` | **Recruiter** | `M58` | Requisition and candidate management; **cannot approve an offer** | 2–4 | P03 | **Yes** | `T1` |
| `R46` | **Occupational Health** | `M59` | **Sole access to medical detail** — the narrowest field scope in the estate | 1–2 | P03 | **Yes** | `T5` |
| `R47` | **Team Leader** | operations modules | First-line supervision below Branch Manager | 40–80 | P03, P02 | No | `T3` |
| `R48` | **Service Head** | operations modules | Multi-branch service line ownership | 2–5 | P03, P06 | **Yes** | `T1` |
| `R49` | **GRC / Internal Audit** | `M60`, `M63`, `M10` + | **Independent** control testing and audit; **read-mostly by design** (`SOD-20`, `SOD-21`) | 2–4 | P03, P06, P11 | **Yes** | `T1` read + `T5` grant |
| `R50` | **Marketing Executive** | `M35` | Campaign build and content within approval limits | 3–6 | P03, P12 | No | `T1` |

**Provisionally registered pending `Q-02`:**

| ID | Proposed role | Used in | Status |
|---|---|---|---|
| `R54` | **FP&A Analyst** | `M39` §subscription analytics | **Provisional.** Define or delete before W1 |
| `R57` | **Fleet Administrator** | `M46` data-restriction rule | **Provisional.** Define or delete before W1 |

**Permanently withdrawn:**

| ID | Disposition |
|---|---|
| `R60` | **Withdrawn.** Superseded by `R49`. **Never reallocated** (`CP-02`) |

**Register total: 50 active (`R01`–`R50`), 2 provisional (`R54`, `R57`), 1 withdrawn (`R60`).**

### 4.3 The identifier rules this register operates under

| # | Rule |
|---|---|
| `RI-1` | **Identifiers are permanent.** Never reused, never renumbered — including a withdrawn one |
| `RI-2` | **A role in use must be registered before its first grant.** A module may not introduce a role identifier; it requests one. Sole allocating authority: this document |
| `RI-3` | **A registered role has a profile (§8) before it can be granted.** No profile, no grant — this is what closes `OP-10`(a) structurally rather than by writing 50 documents once |
| `RI-4` | **A role with no profile and no grants for two consecutive certification cycles is retired**, and its identifier withdrawn |
| `RI-5` | Where `05-04` §1 and this register disagree, **this register governs** for identity build; `05-04` is updated to match at its next revision |

### 4.4 `R38` sub-typing — 17 external party identities

`05-04` §1.7 defines `R38` as a deliberate multi-party role. **That was a reasonable modelling
choice at 38 roles and is not survivable at implementation**: `A3-20` records that eight modules
list `R38` twice in one permission table with different scopes, and `SC-002` `AB-08` shows what
that produces — a courier reading customer addresses beyond assigned consignments.

| Sub-type | External party | Portals | MFA | Scope | `EA` rules that bind |
|---|---|---|:--:|---|---|
| `R38.1` | Vendor / supplier | P05 | financial | Own POs, receipts, invoices | `EA-06` |
| `R38.2` | Marketplace seller | P07 | financial | Own listings, awarded jobs, payouts | `EA-01`, `EA-04`, `EA-12` |
| `R38.3` | Brand partner | P08 | financial | Own-brand claims and service data | `EA-05` |
| `R38.4` | Courier partner | P09 | No | Assigned consignments, **minimum data** | `EA-07` |
| `R38.5` | Recycling partner | P05 | No | Own batches | `EA-01` |
| `R38.6` | Referral / alliance partner | P12 | financial | Own referrals, conversions — **not the customer record** | `EA-01`, `EA-02` |
| `R38.7` | External auditor | P11 | **Yes** | **Read-only, time-boxed, scope-limited to the audit** | `EA-01`, `EA-10` |
| `R38.8` | Tax consultant | P05 | **Yes** | Statutory filing scope only | `EA-02` |
| `R38.9` | Calibration provider | P05 | No | Assigned equipment | `EA-01` |
| `R38.10` | Franchise partner | P12 | financial | Own territory | `EA-01`, `EA-03` |
| `R38.11` | Insurance assessor | P08 | **Yes** | Assigned claims | `EA-01` |
| `R38.12` | Legal counsel (external) | P03 restricted | **Yes** | **Named matter only**, `T5` | `EA-01`, `EA-10` |
| `R38.13` | Training provider | P03 restricted | No | Assigned cohorts | `EA-01` |
| `R38.14` | Logistics 3PL | P09 | No | Assigned manifests | `EA-07` |
| `R38.15` | Facility / maintenance contractor | P05 | No | Assigned work orders | `EA-01` |
| `R38.16` | Payment / financial institution | API only | mTLS | Settlement scope | `EA-11` |
| `R38.17` | Regulator or certification body | P03 restricted | **Yes** | **Read-only, time-boxed, evidence scope** | `EA-01`, `EA-10` |

> **`SC-004-F-02`. Three sub-types carry `T5` or near-`T5` reach and are external.** `R38.7`
> external auditor, `R38.12` external legal counsel and `R38.17` regulator each need access to
> restricted material by the nature of their engagement. **All three are time-boxed by default with
> automatic expiry** (`EA-12`), and all three require **step-up authentication per session**, not
> per login. This is a stricter position than `05-04` §8 takes, and it is the direct consequence of
> sub-typing: the risk was invisible while all seventeen shared one identifier.

---

## 5. Keycloak Topology

### 5.1 Realm design — three realms, and why not one

| Realm | Population | Rationale |
|---|---|---|
| **`fix-internal`** | `P-INT` — 800+ staff, `R01`–`R50` | Provisioned from `M21`; strong password policy; MFA per role; corporate federation **not** enabled |
| **`fix-external`** | `P-CUST`, `P-EXT` — customers and the 17 `R38` sub-types | Self-registration for customers, invitation for parties; **materially different lifecycle** — agreement expiry, not employment |
| **`fix-corporate`** | `P-CORP` — 500–2,000 corporate users | **Identity-provider brokering per client organisation.** Each client is a brokered IdP or a local sub-group |

| # | Rule | Because |
|---|---|---|
| `KR-1` | **A realm boundary is a blast-radius boundary.** A misconfiguration in `fix-external` cannot grant an internal role | A single realm with 250,000+ self-registered users and `R02` CTO in the same role space is one policy error from an estate-wide grant |
| `KR-2` | **Realms do not trust each other.** No cross-realm token is accepted anywhere | — |
| `KR-3` | **A person who is both** — a staff member who is also a customer — **holds two identities.** They are not linked | Linking them would make `T4` "own record" ambiguous, and would leak the employment relationship into the customer context |
| `KR-4` | `fix-corporate` brokering is **per client organisation**, never a shared broker | `SC-002` `TH-007`: 1000FiX must not inherit one client's authentication weakness into another's scope |

### 5.2 Client design

| Client | Type | Realm | Flow | Auth method |
|---|---|---|---|---|
| `p01-customer-web`, `p01-customer-app` | Public | `fix-external` | Authorization code + **PKCE** | — |
| `p02-technician-app` | Public | `fix-internal` | Authorization code + **PKCE** | — |
| `p03-admin-web` | Confidential | `fix-internal` | Authorization code + PKCE | Client secret from Vault |
| `p04-corporate-web` | Confidential | `fix-corporate` | Authorization code + PKCE, brokered | Client secret |
| `p05`…`p12` | Per portal | per realm | Authorization code + PKCE | Per type |
| `svc-*` (16 domain services) | Confidential | `fix-internal` | **Client credentials** | **mTLS (RFC 8705)** |
| `api-partner-*` | Confidential | `fix-external` | Client credentials | mTLS or secret + IP allow-list |
| `kong-introspect` | Confidential | all | — | Introspection-only, no token issue |

| # | Rule |
|---|---|
| `KC-1` | **No implicit grant. No resource-owner password grant.** Both are removed in OAuth 2.1 |
| `KC-2` | **PKCE on every authorization-code flow**, including confidential clients (RFC 9700) — the estate's `05-03` applies it to the technician API only; this is a tightening |
| `KC-3` | **Exact redirect-URI matching.** No wildcards, no path prefixes |
| `KC-4` | **One client per surface.** A shared client makes per-consumer quota and revocation meaningless (`EA-11`) |
| `KC-5` | **A client's scopes are a ceiling.** Scope is set by credential and **cannot be widened by request parameter** (`EA-11`, `SC-002` `AB-06`, `AB-07`) |

### 5.3 What lives in Keycloak, and what deliberately does not

| In Keycloak | In the record layer (Odoo) |
|---|---|
| Identity, credentials, MFA enrolment | **Record rules `T0`…`T5`** |
| Realm roles ↔ Odoo group mapping | **Field permissions** (13 restricted groups) |
| Sessions, tokens, revocation | **SoD evaluation** at assignment and transaction |
| Federation and brokering | **Approval authority** evaluation |
| Password policy, breach-list checking | **Delegation** scope and expiry |
| Step-up (`acr`) enforcement | **Access certification** state |
| Client registry and scopes | **The business meaning of every permission** |

> **`SC-004-F-03`.** Keycloak's authorization services are **not enabled**. This is `SC-001-D-02`
> and it is worth stating in the build specification too, because Keycloak makes it easy to do the
> opposite: a developer configuring fine-grained permissions in the IdP produces a second, partial,
> silently-diverging permission model. **`AR-012` should carry a fitness function asserting the
> authorization-services feature is off.**

---

## 6. Authentication Design

### 6.1 Assurance levels per population

Mapped to NIST SP 800-63-4 authenticator assurance levels rather than asserted as "MFA where
required" — which is what `SC-002` `TH-005` finds unenforceable, because the requirement currently
lives in a table (`05-04` §1) and not in a realm.

| Population | Baseline | Sensitive action | Rationale |
|---|---|---|---|
| `P-CUST` customers | **AAL1** — password, MFA optional | **AAL2** for payment, address change, DSR, account recovery | Mandatory MFA on 250,000 registrations/month is a service barrier; AAL2 at the point of consequence is proportionate |
| `P-CORP` corporate users | AAL1, **AAL2 mandatory for Approver and Finance sub-roles** | AAL2 | `05-04` §1.7 |
| `P-EXT` external parties | AAL1 | **AAL2 for any action with financial consequence** (`EA-09`) | `EA-09` |
| `P-INT` staff — non-MFA roles | AAL1 + device registration | **AAL2** for any `T5` read or restricted-field access | 22 of 50 roles carry no login-MFA requirement |
| `P-INT` staff — MFA roles | **AAL2 at every login** (`BRU-SEC-01`) | **AAL2 re-authenticated** (step-up) | Admin, finance, HR, all privileged |
| `P-SVC` services | **mTLS** | — | Certificate-bound; not a human factor |

**Roles requiring MFA at every login** — counted from `05-04` §1 plus §4.2 of this document:
`R01`–`R05`, `R06`, `R07`, `R13`, `R14`, `R19`, `R21`–`R24`, `R26`–`R28`, `R30`–`R33`, `R35`,
`R39`, `R40`, `R41`, `R45`, `R46`, `R48`, `R49` — **28 of 50**.

### 6.2 Authenticator policy

| # | Rule | Requirement |
|---|---|---|
| `AU-1` | **TOTP or WebAuthn preferred; SMS is a fallback, not a default** | `SC-002` `TH-006` — SIM swap is a live threat in the market |
| `AU-2` | **WebAuthn / passkey offered to all `P-INT` and to `R38.7`/`.12`/`.17`** | Phishing-resistant; the only authenticator class that is |
| `AU-3` | Password policy: minimum length over composition rules, **breach-list checking mandatory**, no forced periodic rotation without cause | `FR-SEC-003`; SP 800-63-4 position |
| `AU-4` | **Bilingual** reset and enrolment flows (Bengali and English) | `FR-SEC-003`; `BN-001` |
| `AU-5` | **No hard account lockout.** Rate-limiting and risk-based throttling instead | `SC-002` `TH-067`, `AB-29` — hard lockout is a denial-of-service primitive against 51+ branches |
| `AU-6` | **Step-up is a token claim (`acr`), verified server-side at the action**, never a UI flow | `SC-001` `SEC-TK-4`; `SC-002` `TH-021` |
| `AU-7` | Device registration for technician, rider and auditor apps; **deregistration on leaver or loss** | `FR-SEC-010` |
| `AU-8` | Anomaly defence: credential stuffing, brute force, **impossible travel** | `FR-SEC-011`, `NFR-068` |

### 6.3 Step-up — the action list

Actions requiring a fresh AAL2 claim, from `NFR-065`, `BRU-SEC-02` and the `T5` rule:

| # | Action | Population |
|---|---|---|
| 1 | Payout release or bank-detail change | `P-INT`, `R38.2` |
| 2 | Payroll finalisation | `R41`, `R30`, `R03` |
| 3 | **Any `T5` read** — payroll, NID, bank details, recovery-case content, call recordings, audit logs, biometric templates, seller KYC | all |
| 4 | **Any residency-classified field read** (`Z4` via `CD-233`) | all |
| 5 | Bulk personal-data export | all |
| 6 | Permission or role change; SoD exception grant | `R33`, `R02` |
| 7 | Privileged elevation; break-glass | `R33`, `R02` |
| 8 | DSR fulfilment — assembly, erasure, portability export | `R40`, DPO function |
| 9 | Destruction or purge certificate issue | `R14` |
| 10 | Customer address or payment-instrument change | `P-CUST` |

> **`SC-004-F-04`.** Item 3 makes **every `T5` read** a step-up event. At `R46` occupational health
> or `R14` data services, that is the whole job — a step-up on every record would be unworkable and
> would be defeated by users. **Resolution: step-up establishes a bounded elevated session
> (15 minutes, re-armed by activity, absolute 60 minutes) rather than a per-record challenge.** The
> access log records each read individually regardless; **elevation is amortised, logging is not.**

---

## 7. Token Design

### 7.1 Token types and lifetimes

| Token | Purpose | Lifetime | Audience | Notes |
|---|---|---|---|---|
| **Authorization code** | Exchange only | **60 s**, single use | — | PKCE-bound |
| **Access token** | Authorisation at `Z1` | **10 min** internal · **10 min** external · **5 min** admin/`Z4` paths | The specific API family | Introspected, never locally validated (`SEC-TK-1`) |
| **Refresh token** | Renewal | **60 min** internal · **30 min** external, **rotating** | — | One-time use; **reuse detection revokes the whole family** |
| **ID token** | Authentication assertion | 5 min | The client | Never used for authorisation |
| **Service token** | Service-to-service | 15 min | Named peer | mTLS sender-constrained (RFC 8705) |
| **Partner API token** | External consumer | 60 min | The partner's scope | Client credentials; per-consumer quota |

**Lifetimes derive from `SC-004-P6`, not from convenience.** A 10-minute access token with
introspection gives the 60-second revocation `BRU-SEC-25` requires; a 60-minute locally-validated
JWT would give 60-minute revocation latency, which makes the one-hour leaver rule
(`BRU-SEC-06`) arithmetically impossible to guarantee.

### 7.2 Claims

| Claim | Content | Consumed by |
|---|---|---|
| `sub` | Opaque subject id — **never an employee number, NID or email** | all |
| `aud` | The API family | `Z1` — strict validation |
| `realm` | `fix-internal` / `fix-external` / `fix-corporate` | `Z1` — `KR-2` |
| `roles` | Realm roles, mapping to Odoo groups | `EP-3` |
| `acr` | Authentication context — AAL and **timestamp of the elevation** | `AU-6`, step-up |
| `party_ref` | For `P-EXT`/`P-CUST`: the party the identity is bound to | **`EP-4` `T4` scope** |
| `org_ref` | For `P-CORP`: the client organisation | `EA-03` |
| `svc` | For `P-SVC`: service name and its accountable owner | `SEC-C-012` |
| `cnf` | mTLS certificate thumbprint where sender-constrained | RFC 8705 |
| **not present** | **Branch, zone, company, permission set** | **Deliberately.** These are record-layer facts that change without a new token (`SC-004-P1`) |

> **`SC-004-F-05`.** `party_ref` and `org_ref` are in the token because they are **identity facts**
> — which party this credential *is* — and `EA-11` requires scope to come from the credential and
> not from a request parameter. Branch and zone are **not**, because they are assignment facts that
> change during a session, and a token carrying a stale branch would out-live a transfer.

### 7.3 Introspection contract

| # | Requirement | Source |
|---|---|---|
| `IN-1` | **≥ 99.99% availability, ≤ 20 ms p95** — every request in the estate depends on it | `M29` `T-09` |
| `IN-2` | Short-TTL cache at `Z1` with **immediate revocation propagation**; TTL **≤ 30 s** so total revocation latency stays inside 60 s | `BRU-SEC-25` |
| `IN-3` | Introspection **fails closed** | `SC-001` §5.3 |
| `IN-4` | The introspection client may not issue tokens | `KC` client separation |
| `IN-5` | Revocation events are **pushed** to `Z1`, not only polled — the cache is invalidated, not merely expired | `SEC-TK-3` |

---

## 8. Access Profiles — Closing `OP-10`(a)

### 8.1 What a profile is

> **`AP-Rnn` = (object permissions per module) × (isolation tier) × (field restrictions) ×
> (portals) × (MFA/step-up policy) × (SoD exclusions) × (a named signing owner).**

`OP-015` §4.2 makes the standard profile *"the mechanism that keeps 38 roles administrable"*.
Without it, `OP-10` records, *"every W1 grant is bespoke and justified by precedent"* — which is
how an estate ends up with 800 users holding 800 different permission shapes and no way to certify
any of them.

### 8.2 The profile template

Every profile carries these fields. **`RI-3` prohibits granting a role whose profile is
incomplete.**

| Field | Content | Satisfies `05-04` §10 criterion |
|---|---|---|
| `AP-01` Role and identifier | `Rnn` / `R38.n` | — |
| `AP-02` Business owner | **A named role accountable for this profile** | **8** |
| `AP-03` Object permissions | CRUDA per module, from `05-04` §3 | **1** |
| `AP-04` Isolation tier | Exactly one default tier, with per-model exceptions listed | **2** |
| `AP-05` Field restrictions | Which of the 13 restricted groups are visible / editable | **3** |
| `AP-06` Portal access | From `05-04` §2 | **5** |
| `AP-07` Authentication policy | Login MFA yes/no; which step-up actions apply | — |
| `AP-08` SoD exclusions | Which `SOD-nn` rules this role participates in, and on which side | **4** |
| `AP-09` Approval authority | Bands from `SP-004` / `05-04` §7, or none | — |
| `AP-10` Provisioning trigger | Position profile in `M21`, or invitation, or request | — |
| `AP-11` Expiry | None (internal) / agreement date (external) / fixed window (`R38.7`, `.12`, `.17`) | — |
| `AP-12` **Negative tests** | The specific things this role **must not** be able to see or do | **6** |
| `AP-13` Training | Bengali and English material for the role | **7** |

### 8.3 Worked profiles — the four that set the pattern

The full set `AP-R01`…`AP-R50` plus `AP-R38.1`…`AP-R38.17` is a **W1 build deliverable** carried
in the identity configuration repository, not restated here. Four are worked in full because they
establish the pattern for the rest: the widest, the narrowest, the most external, and the one with
the sharpest SoD constraints.

**`AP-R08` — Service Centre Agent** *(headcount 150–250 — the largest internal population)*

| Field | Value |
|---|---|
| Owner | Operations Director |
| Objects | `M01` CRU(b) · `M02` R(b) · `M03` C,R(b) · `M04` CRU(b) · `M06` C,R(b) · `M07` CRU(b) · `M09` CR(b) · `M10` CRU(b) · `M11` CR(b) · `M12` CR(b) · `M13` CR(b) · `M14` CR(b) |
| **Tier** | **`T2` branch** — `operating_unit_id` |
| Fields | **No** cost, margin, salary, NID, bank account, recovery index, call recording, commission, KYC, incentive detail, credit limit, vendor price, model internals. **Internal notes: yes** |
| Portals | P03 |
| Auth | No login MFA. **Step-up for any `T5` read** |
| SoD | Party in `SOD-08` (create customer + approve credit limit) — **create side only** |
| Approval | Discount ≤ 10% |
| **Negative tests** | Zero rows from another branch · `unit_cost` absent from every payload · cannot approve a discount above 10% · cannot read a data-recovery case |

**`AP-R46` — Occupational Health** *(the narrowest scope in the estate)*

| Field | Value |
|---|---|
| Owner | HR Director |
| Objects | `M59` CRU(a) medical records only · `M21` R(a) minimal demographics |
| **Tier** | **`T5` restricted** — named allow-list |
| Fields | **Sole** access to medical detail. **No** salary, no performance, no discipline |
| Portals | P03 |
| Auth | **MFA at login + step-up per elevated session** (§6.3 `SC-004-F-04`) |
| SoD | Excluded from every HR approval path — clinical independence |
| **Negative tests** | **No other role, including `R30` HR Manager and `R02` CTO, returns a medical-detail field** · every access appears in the access log before the value returns |

**`AP-R38.2` — Marketplace Seller** *(500–2,000 external, financially active)*

| Field | Value |
|---|---|
| Owner | Marketplace Operations Officer (`R24`) |
| Objects | Own listings CRU · awarded jobs RU · own payouts R · own KYC C,R |
| **Tier** | **`T4` own record** — `party_ref` from the token, **never from a parameter** (`EA-11`) |
| Fields | **Never** cost, margin, internal notes, another seller's anything (`EA-02`). Customer contact **only for an awarded job, and only until the `EA-04` window closes** |
| Portals | P07 |
| Auth | **AAL2 for every financial action** (`EA-09`). **Bank-detail change: step-up + cooling period + notification to the previous contact point** (`SC-002` `AB-03`) |
| SoD | `SOD-06` — a seller can never hold the approver side |
| Expiry | Registration expiry (`EA-12`) |
| **Negative tests** | Seller A cannot retrieve seller B's payout **by direct id** (`AB-05`) · no aggregate endpoint returns cross-seller volumes (`AB-02`) · contact details disappear when the `EA-04` window closes · bulk export is rate-limited and logged (`EA-12`) |

**`AP-R49` — GRC / Internal Audit** *(the role the `R60` ruling created)*

| Field | Value |
|---|---|
| Owner | Audit Committee (`GV-002`) |
| Objects | **Read across all modules**; write **only** to `M60` control-test records |
| **Tier** | `T1` read, with `T5` by named grant per audit |
| Fields | Restricted fields readable **under a recorded audit purpose**; every read logged |
| Portals | P03, P06, P11 |
| Auth | **MFA at login + step-up for `T5`** |
| **SoD** | **`SOD-20`** — cannot audit an area they are responsible for. **`SOD-21`** — cannot record the test conclusion for a control they own. **Structurally excluded from `R32` Quality Manager** — this is the whole reason `R49` exists rather than merging into `R32` |
| **Negative tests** | Cannot write to any transactional module · cannot close a deficiency on their own control · **cannot hold `R32` simultaneously** |

### 8.4 Profile delivery

| # | Obligation |
|---|---|
| `PF-1` | **50 internal profiles + 17 `R38` sub-type profiles = 67 profiles**, all authored before W1 provisioning |
| `PF-2` | Each profile is **signed by its named business owner** (`05-04` §10 criterion 8) |
| `PF-3` | Profiles are **configuration, version-controlled and reviewed** — not a document. `PGD-A2-15` records that nothing in this estate is under version control; identity configuration is where that must stop being true first |
| `PF-4` | **`AP-12` negative tests are handed to `QA-007` as the access-control test suite** |
| `PF-5` | A change to a profile is a **change request**, evaluated for SoD impact before it applies |

> **`SC-004-F-06`. 67 profiles is the real size of `OP-10`.** The finding says "38 access
> profiles"; counted against the resolved role set it is **67**, and each requires a business owner
> to sign a permission shape they have never been asked about before. **This is the largest
> untracked W1 work package in Category 05**, and it is a business-side draw, not an engineering
> one — `GV-007` quantifies the business draw at 134–201 super-users, and this is part of it.

---

## 9. Joiner, Mover, Leaver

### 9.1 Lifecycle

The state model is **adopted verbatim from `M29` §8.1** — Requested → Provisioned → Active →
{Modified | Elevated | Suspended} → Deprovisioned → Archived. This document specifies the triggers
and the guarantees.

### 9.2 Joiner

| # | Step | Guarantee |
|---|---|---|
| `J-1` | `employee.joined` from `M21` | Identity created in `fix-internal` |
| `J-2` | Role assigned **from the position profile**, not by request | The position profile names the `AP-Rnn`; a joiner never gets a bespoke grant |
| `J-3` | **SoD evaluated before provisioning** | `BRU-SEC-07` — provisioning **blocks** on conflict |
| `J-4` | Portal access, MFA enrolment where required, onboarding training assigned | `FR-SEC-027` |
| `J-5` | Access active **day one** | `AR-001` §9.1 |

### 9.3 Mover — the case that silently accumulates privilege

| # | Requirement |
|---|---|
| `MV-1` | **Old role revoked and new role granted in one transaction. Never additive** |
| `MV-2` | Effective **on the effective date**, not on the date HR gets round to it |
| `MV-3` | **SoD re-evaluated on the resulting combination** — a mover can create a conflict that neither role created alone |
| `MV-4` | Delegations held under the old role are **reassigned or revoked**, never carried |
| `MV-5` | Failure **holds and alerts the manager** — it does not proceed with both roles |

> `SC-002` `TH-078` and `AB-13`: privilege accumulation through the mover path is the most common
> real-world route to an over-privileged account, and it is invisible to certification if the
> certifier only sees the current role list without its history.

### 9.4 Leaver — and the ruling on the two deadlines

| # | Requirement | Source |
|---|---|---|
| `LV-1` | **All access revoked within one hour** of `employee.left` | `BRU-SEC-06` |
| `LV-2` | Revocation takes effect **estate-wide within 60 seconds** of being issued | `BRU-SEC-25` |
| `LV-3` | Devices deregistered; sessions terminated; delegated authority reassigned | `FR-SEC-029` |
| `LV-4` | Failure **escalates to the CTO immediately**; manual revocation follows | `AUT-SEC-03` |
| `LV-5` | Identity **archived, never deleted** — retained for audit, cannot authenticate | `M29` §8.1 |

> **`SC-004-R-01` — the `OP-15` ruling.** `BRU-SEC-06` requires revocation **within one hour**.
> `KPI-090` measures orphaned accounts **beyond 24 hours**, target zero. They differ by a factor of
> **24**, and `OP-15` observes that *"an organisation operating to the KPI would breach the rule
> daily without the KPI ever reporting it."*
>
> **The one-hour rule governs.** It is achievable: `LV-2`'s 60-second propagation and event-driven
> revocation make it a system property, not a human one. **`KPI-090`'s tolerance is restated as one
> hour**, and the 24-hour figure is retained **only** for `BRU-SEC-17` orphaned-account detection,
> which is a different control answering a different question (*does this account have an owner?*
> rather than *has this leaver been revoked?*). Escalated to `GV-005` and to the KPI register.

### 9.5 External expiry

| # | Requirement |
|---|---|
| `EX-1` | External access **disabled automatically** at agreement or registration expiry (`EA-12`) |
| `EX-2` | `R38.7`, `R38.12`, `R38.17` carry a **fixed window** set at grant, not an open-ended agreement |
| `EX-3` | Records retained per `LG-009`; the identity is archived |
| `EX-4` | **Renewal is a new grant**, re-evaluated against the current profile — not an extension of the old one |

---

## 10. Access Certification

| # | Requirement | Source |
|---|---|---|
| `CT-1` | Quarterly cycle; **each manager confirms or revokes every report's access** | `05-04` §9, `FR-SEC-026` |
| `CT-2` | **Unconfirmed access is revoked automatically** at cycle close | `BRU-SEC-16` |
| `CT-3` | Privileged roles re-attested **by their owner**, additionally | `AR-001` §9.1 |
| `CT-4` | The certifier sees the **profile deviation**, not the raw permission list — "this person holds `AP-R08` plus three exceptions" is reviewable; a 200-row permission dump is not |
| `CT-5` | **A certification cycle with zero revocations across a manager's whole team is flagged as an anomaly** and sampled by `R49` | `SC-002` `AB-13` |
| `CT-6` | External party access is certified by its **sponsoring internal owner**, not by the external party |

> **`CT-4` and `CT-5` are the two that make certification a control rather than a ritual.**
> `AB-13` describes the failure mode precisely: rubber-stamping defeats the control **while
> reporting 100% compliance**. A control whose failure mode produces a perfect score needs a
> detector, and `CT-5` is it.

---

## 11. Segregation of Duties — the Enforcement Contract

### 11.1 The identifier ruling — closing `OP-10`(b)

| Source | Range | Status |
|---|---|---|
| `05-04` §6 | `SOD-01`…`SOD-12` | **Derived view.** Correct as far as it goes; 18 short of live module usage |
| Module files | `SOD-01`…`SOD-30` | In use |
| **`SP-006`** | **`SOD-01`…`SOD-60`**, with nine collisions resolved into `SOD-31`…`SOD-39` and 21 unnumbered controls registered as `SOD-40`…`SOD-60` | **The source of record for enforcement** |

> **`SC-004-R-02`.** **`SP-006` is the SoD register the engine is built against.** `05-04` §6 is a
> derived view maintained for the reader and updated at its next revision. **Grant-time enforcement
> may not be built until `SP-006`'s reallocation is ratified** — `OP-10`(b) is explicit that nine
> numbers carrying two meanings makes enforcement undefined, and `M60` would otherwise test a
> control whose number means two things. **Ratification is a `Q-03` blocker for W1.**

### 11.2 The enforcement contract

| # | Contract term | Source |
|---|---|---|
| `SD-1` | Evaluated at **role assignment** (preventive) — an incompatible assignment is **refused** | `FR-SEC-022` |
| `SD-2` | Re-evaluated **inside the transaction** — **the runtime evaluation is authoritative** | `FR-SEC-023`, `M29` `T-07` |
| `SD-3` | Evaluation is over **the same natural person**, not the same role or team (`SD-R1`) | `SP-006` |
| `SD-4` | Evaluation is **per transaction or record**, not per duty in general (`SD-R2`) | `SP-006` |
| `SD-5` | Modes: **hard block** · **threshold** · **warning + approval** · **detective**. A detective control **names its report, frequency and reviewer** or it is not a control (`SD-R4`) | `SP-006` |
| `SD-6` | An exception is **time-boxed, mitigated, CFO/CTO-approved and on a standing quarterly report** | `FR-SEC-024` |
| `SD-7` | **`M60` defines and tests; `M29` enforces.** `M60` holds no runtime enforcement path | `BRU-GRC-11`, `M60` `T-12` |
| `SD-8` | Every rule is tested **at least once per cycle, including by controlled violation attempt** | `BRU-GRC-09` |
| `SD-9` | **Evaluation covers the resolved 50-role set**, including `R38.n` sub-types | `SC-002` `TH-082`, `TH-083` |

> **`SC-004-F-07`.** `AR-001` §9.1 states SoD is *"evaluated at role-assignment time, **not**
> transaction time"*. **That is wrong and it matters**: `SC-002` §12.2 attack paths F, G and H —
> delegation, mover transition and unregistered role — are all invisible to assignment-time
> checking alone. `M29` `T-07` and `FR-SEC-023` require both, runtime authoritative. Raised to
> `AR-001` as `SC-001` `SCA-05`.

---

## 12. Privileged Access

| # | Requirement | Source |
|---|---|---|
| `PA-1` | Privileged role and action register with accountable owners | `FR-SEC-032` |
| `PA-2` | **Time-boxed elevation with automatic expiry. No standing administrative rights** | `BRU-SEC-19` |
| `PA-3` | Approval: **line manager + IT Administrator + CTO** for privileged roles | `05-04` §7 |
| `PA-4` | **Session recording for every privileged session; a recording failure terminates the session** | `NFR-070` |
| `PA-5` | **No self-administration and no self-approval** | `SOD-09`, `BRU-SEC-18` |
| `PA-6` | **Break-glass per `SC-001` §7.6 `BG-A1`…`BG-A5`** — independent, loud, time-boxed, recorded, rotated on use | `BRU-SEC-20`, `OP-08` |
| `PA-7` | Elevation is recorded **independently of the elevated session**, so the elevated identity cannot suppress the record of its own elevation | `SC-002` `AB-10` |

> **`PA-7` is not in any source document and is added here.** `AB-10` describes an administrator
> granting themselves a role, acting, and revoking it before review. If the record of the elevation
> is written by the elevated session, a sufficiently privileged actor can remove it. **The
> elevation record is written by the grant path, into the insert-only audit store, before the
> elevation takes effect.**

---

## 13. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | Are the 12 newly registered roles' definitions accepted by their business owners? | CTO with business owners | **W1** | §8 profile sign-off |
| `Q-02` | **`R54` and `R57`: define or delete?** | CTO with CFO (`R54`) and Operations (`R57`) | **W1** | §4.2; a role in a data-restriction rule that does not exist is an unenforceable rule |
| `Q-03` | **When is `SP-006`'s `SOD-31`…`SOD-39` reallocation ratified?** | CFO with Enterprise Architecture | **W1 — blocks SoD build** | §11.1; `NFR-064` |
| `Q-04` | Who signs the 67 access profiles, and is that resource allocated? | Operations Director with HR | **W1** | `SC-004-F-06`; `GV-007` business draw |
| `Q-05` | Do corporate clients federate at W1 or W4? `INT-046` is `FR-SEC-009` **P2** | CCO with CTO | W1 scope decision | §5.1 `fix-corporate` realm scope |
| `Q-06` | Is WebAuthn/passkey rollout funded for `P-INT`? | CTO | W2 | `AU-2`; the only phishing-resistant option |
| `Q-07` | Is `KPI-090`'s tolerance restated to one hour, per `SC-004-R-01`? | CTO with Internal Audit | W1 | `OP-15`; KPI register |

---

## 14. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | Every role identifier in use is registered or explicitly withdrawn | §4.2 — 50 active, 2 provisional, 1 withdrawn |
| `AC-02` | The `R60` contradiction between two audits is ruled, with reasoning | §4.1 |
| `AC-03` | `R38` is sub-typed before external onboarding | §4.4 — 17 sub-types |
| `AC-04` | A profile template exists and satisfies all 8 of `05-04` §10 | §8.2 |
| `AC-05` | Profile count is counted, not asserted | §8.4 — **67**, not 38 |
| `AC-06` | Every profile carries negative tests `QA-007` can execute | `AP-12`; four worked examples |
| `AC-07` | Token lifetimes are derived from the revocation requirement, not chosen | §7.1 |
| `AC-08` | Authentication is mapped to assurance levels, not asserted as "MFA where required" | §6.1 |
| `AC-09` | The leaver deadline contradiction is ruled | `SC-004-R-01` |
| `AC-10` | The SoD enforcement source of record is named | `SC-004-R-02` |
| `AC-11` | No permission decision is placed in Keycloak | §5.3; `SC-004-F-03` |
| `AC-12` | Elevation records cannot be suppressed by the elevated session | `PA-7` |

---

## 15. Decisions Recorded

| # | Decision | Options | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `SC-004-D-01` | Realm count | One · Two · **Three** | **Three** | A realm boundary is a blast-radius boundary; 250,000 self-registered users must not share a role space with `R02` | Three configurations to maintain; `KR-3` dual identities |
| `SC-004-D-02` | Token validation | Local JWT · **Introspection** | **Introspection** | 60-second revocation is impossible with local validation, and it is what makes the one-hour leaver rule real | Keycloak becomes availability-critical: `IN-1` ≥ 99.99% |
| `SC-004-D-03` | Role target | 38 now + 12 later · **50 in W1** | **50 in W1** | Retrofitting record rules across live data (`TR-13`) | 67 profiles is a W1 work package |
| `SC-004-D-04` | `R60` | Merge into `R32` (`00-07`) · **Keep `R49`** | **`R49`** | Merging auditor and auditee would create an `SOD-20` violation to fix an identifier collision | `00-07` remediation item 5 superseded |
| `SC-004-D-05` | `R38` | Keep as one · **Sub-type to 17** | **Sub-type** | One identifier for 17 party classes makes `EA-01`…`EA-12` unenforceable | 17 extra profiles; three carry `T5` reach |
| `SC-004-D-06` | Step-up granularity | Per record · **Bounded elevated session** | **Bounded session (15 min, absolute 60)** | Per-record challenge at `R14`/`R46` is the whole job and would be defeated by users | **Logging stays per-record**; elevation is amortised, attribution is not |
| `SC-004-D-07` | Account lockout | Hard lockout · **Rate-limit + risk-based** | **Rate-limit** | Hard lockout is a DoS primitive against 51+ branches (`AB-29`) | Requires anomaly detection to carry the load |
| `SC-004-D-08` | Leaver deadline | Average the two · Adopt 24 h · **Adopt 1 h** | **1 hour** | Achievable as a system property via 60-second propagation; 24 h would let a daily breach go unreported | `KPI-090` must be restated (`Q-07`) |

---

## 16. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `SC-001` §6, §7 | Enforcement points this document configures |
| Upstream | `AR-001` §9.1 | Identity realisation — **corrected on role count and SoD timing** |
| Upstream | `SP-006` | The SoD register enforcement is built against |
| Downstream | `SC-005` | ASVS auth/session/authorization chapters at the gate |
| Downstream | `SC-006` | Token signing algorithm, key rotation |
| Downstream | `SC-010` | What must be attributable, and to whom |
| Downstream | `SC-011` | Break-glass operation; incident-driven revocation |
| Downstream | `QA-007` | **`AP-12` negative tests are the access-control suite** |
| Downstream | `M29` | The module that builds this |
| Lateral | `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04_*.md` | The 38-role baseline this extends |
| Lateral | `../../project_content/17_Operations_Support_and_Runbooks/OP-009_*.md`, `OP-015_*.md` | Identity runbook and JML content |

---

## 17. References

**Within this repository**
`../PGD-000_*.md` · `./_CATEGORY_OVERVIEW.md` · `./SC-001`, `./SC-002`, `./SC-006`, `./SC-010`, `./SC-011` ·
`../02_Architecture_and_Design/AR-001_*.md`, `AR-012_*.md`

**Workspace**
`../../1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M29_*.md` ·
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04_*.md` ·
`../../1000fix_ERP_Module/00_Governance_and_Charter/00-07_*.md` ·
`../../1000fix_ERP_Module/03_Modules/_MODULE_SET_AUDIT_REPORT.md` ·
`../../project_content/06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-006_*.md`, `SP-004_*.md` ·
`../../project_content/17_Operations_Support_and_Runbooks/OP-009_*.md`, `OP-015_*.md` ·
`../../project_content/_AUDIT/AUDIT-017_*.md`

**External standards** *(all verified 2026-08-18)*

| Source | Version | Used for |
|---|---|---|
| OAuth 2.0 Security BCP | **RFC 9700** | §7 — PKCE everywhere, no implicit, no password grant |
| OpenID Connect Core | 1.0 | ID vs access token separation |
| RFC 7662 | Token introspection | `IN-1`…`IN-5` |
| RFC 7636 | PKCE | `KC-2` |
| RFC 8705 | mTLS client auth / sender-constrained tokens | `P-SVC`, `cnf` claim |
| SAML 2.0 | — | Corporate federation fallback |
| **NIST SP 800-63-4** | Digital Identity Guidelines | §6.1 assurance levels |
| ISO/IEC 27001 | :2022 + Amd 1:2024 — A.5.15–A.5.18, A.8.2–A.8.5 | Control basis |
| **OWASP ASVS** | **5.0.0 (30 May 2025)** | Verification chapters |
| Keycloak | **26.x** (`TD-07`) | Realm, client, token configuration |

---

## 18. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. Extends the role register from 38 to **50**, sub-types `R38` into 17, rules on `R60`/`R54`/`R57`, closes `OP-10`(a) with a 67-profile template and (b) with the `SP-006` ruling, rules the `OP-15` leaver-deadline contradiction, and corrects `AR-001` on role count and SoD timing | *Pending — no constituted body (`PGD-A2-25`)* |

---

*`SC-004` · Category 05 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
