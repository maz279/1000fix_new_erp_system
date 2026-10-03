---
id: SC-005
title: Secure Development Lifecycle (SSDLC) Standard
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
  ISO/IEC 27001:2022 Annex A.8.25–A.8.31 (secure development) · NIST SP 800-218 SSDF v1.1
  (with SP 800-218A for generative-AI components) · OWASP ASVS 5.0.0 · OWASP SAMM 2.0 ·
  OWASP Top 10:2025 · SLSA build-integrity levels · ISO/IEC 5230 (OpenChain) for licence and
  component provenance
traces_to: >
  PGD-000 SC-005 · SC-001 SEC-C-055, SEC-C-056 · SC-002 §8 abuse cases, §7 Top 10 map ·
  05-06 §4 NFR-062, NFR-066, NFR-071 · 05-06 §7 unit-test coverage · 02-05 §9 ·
  LG-021 IS-06 · audit findings PGD-A2-15, LG-021 O-09, OP-16
depends_on: SC-001 · SC-002 · SC-004 · AR-007 (Odoo module standard) · AR-012 (fitness functions)
verified_on: 2026-08-18
priority: P0
needed_by: W1
enumeration_timestamp: 2026-08-18 13:55 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# SC-005 — Secure Development Lifecycle (SSDLC) Standard

### Category 05 · Code `SC` · ISO/IEC 27001:2022 A.8.25–A.8.31 · NIST SP 800-218 SSDF v1.1 · OWASP ASVS 5.0.0

---

> **Before writing, read this.**
>
> 1. **`PG-01` Register-first.** This document's row exists in `PGD-000` Category 05 as `SC-005`.
> 2. **`PG-03` Count, do not consult.** Estate figures counted at **2026-08-18 13:55 (+06)**.
> 3. **`PG-06` Cite standards.** §2.1, including the **SSDF v1.2 draft position**.
> 4. **`PG-M4` Verify citations.** Standards versions verified 2026-08-18.

---

## 1. Purpose

This document states **how security is built in rather than tested for**: the security activities
required at each stage of development, the automated gates that enforce them, the rules a developer
follows, and the evidence each produces.

`PGD-000` marks `SC-005` as **◐ partial**, citing `LG-021`. That marking is correct and precise:
**`LG-021` is an ISMS policy set with no engineering standard beneath it.** `LG-021` `IS-06` states
six clauses — *"security requirements are specified before build"*, *"code is reviewed"*,
*"dependencies are inventoried"*, *"secrets are vaulted"*. Every one is true and none is
executable. A developer cannot run `IS-06`.

The gap below it is quantified. `02-05` §9 covers the entire security position of the build
pipeline in **two table cells**: *"Pre-commit: formatting, linting, Odoo-specific checks, secret
scanning"* and *"CI: … security scan …"*. **Counted at 13:55 (+06), the estate contains no
specification of what that security scan is, what it fails on, or what happens when it fails.**

Three findings make this a W1 document rather than a W2 one:

| Finding | Statement |
|---|---|
| **`PGD-A2-15`** | **644+ files, zero under version control.** There is no baseline to gate against |
| **`LG-021` `O-09`** | *"No vulnerability scanning, penetration testing or assessment evidence exists"* — while `BRU-SEC-21` presumes discovery |
| **`SC-002` `TH-075`, `TH-094`** | CI/CD compromise and supply-chain compromise are both **Critical**, and `A03:2025` is a new OWASP top-ten category the estate has never referenced |

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | **Security activities by stage** — requirements, design, implementation, verification, release, operate |
| 2 | The **SSDF practice mapping** — every activity traced to a `PO`/`PS`/`PW`/`RV` practice |
| 3 | **Automated gates `G-01`…`G-14`** with fail conditions, owners and override paths |
| 4 | **Secure coding rules `SR-01`…`SR-31`** — Odoo/Python, TypeScript/Next.js, Flutter, SQL, and the four estate-specific rule families |
| 5 | **Dependency, container and supply-chain integrity** — SBOM, pinning, provenance, `A03:2025` |
| 6 | **Secret management in the pipeline** |
| 7 | **Security review checkpoints** — when a human looks, and at what |
| 8 | **Abuse-case testing** — turning `SC-002` §8 into executable obligations |
| 9 | **Non-production data rules** |
| 10 | **Evidence** each activity produces, and where it is retained |
| 11 | **Exception handling** — how a gate is bypassed, by whom, and with what expiry |
| 12 | **AI-assisted and AI-component development** — `SP 800-218A` and the `M26`/`M32` surface |

**Explicitly out of scope:**

| Topic | Owned by | Why |
|---|---|---|
| Pipeline implementation, runners, IaC | `PE-004` | This document is the requirement; `PE-004` builds it |
| Vulnerability triage, SLA, pen-test schedule | `SC-009` | This document gates the **build**; `SC-009` governs the **finding** |
| Cryptographic algorithm choice | `SC-006` | `SR-14` says "use the approved suite"; `SC-006` names it |
| General code quality, style, architecture fitness | `BD-00x`, `AR-012` | Security gates only. `AR-012` fitness functions are the neighbour, not the same thing |
| Test strategy, coverage targets generally | `QA-001`, `QA-007` | `QA-007` executes the security tests this document requires to exist |
| Branching, commit convention, review process generally | `BD-00x`, `02-05` §9 | Referenced; not restated |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| **Every developer on the programme** | §5 gates and §6 rules. **This is the document you are held to** |
| **Platform / DevOps (`PE-004`)** | §5 — the gates to build |
| **Delivery leads** | §7 review checkpoints; §9 exceptions |
| **QA (`QA-007`)** | §8 abuse-case obligations |
| **Vendor development teams** | §11 — this standard is a contractual obligation under `CO-003` |
| **Auditor / certification body** | §10 evidence; A.8.25–A.8.31 crosswalk |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | How this document conforms | Departure and rationale |
|---|---|---|
| **ISO/IEC 27001:2022 A.8.25–A.8.31** *(verified 2026-08-18)* | §3 maps each stage to A.8.25 secure development lifecycle, A.8.26 application security requirements, A.8.27 secure architecture principles, A.8.28 secure coding, A.8.29 security testing, A.8.30 outsourced development, A.8.31 separation of environments | §11 covers A.8.30 explicitly, because the build is expected to be vendor-delivered (`CO-003`) |
| **NIST SP 800-218 SSDF v1.1** *(February 2022 — **the current final version**; verified 2026-08-18)* | §4 maps every activity to `PO` prepare, `PS` protect the software, `PW` produce well-secured software, `RV` respond to vulnerabilities | **SSDF v1.2 exists only as an initial public draft (SP 800-218r1, released 17 December 2025) and is in public comment.** v1.1 is used as the obligation; v1.2 is a `RM` re-verification trigger, not a current requirement. Stating this prevents the `H-01` failure mode — building on a version whose status was never checked |
| **NIST SP 800-218A** *(July 2024)* | §12 applies the generative-AI SSDF community profile to `M26` and `M32` | Applies only to AI components; the rest of the estate uses v1.1 |
| **OWASP ASVS 5.0.0** *(30 May 2025)* | §5 `G-08` binds ASVS verification to the gate: **L2 estate-wide, L3 for `Z4`-touching and payment paths** (`SC-001-D-07`) | The estate cites *"ASVS 4"*; 4.0.3 is superseded. Corrected |
| **OWASP SAMM 2.0** | §13 maturity model — used to state where the programme is, not to claim a level | Assessment only; no certification claim |
| **OWASP Top 10:2025** *(6 Nov 2025; finalised Jan 2026)* | §6 rules are organised so that every 2025 category has at least one enforceable rule | — |
| **SLSA** | §5 `G-11`, `G-12` adopt **build provenance and signed artefacts** — SLSA Build Level 2 as the W1 target, Level 3 at W4 | Full Level 3 requires a hardened, isolated build service; `SEC-CON-03` (no commercial licence) makes that a W4 item |
| **ISO/IEC 5230 / OpenChain** | §5 `G-06` SBOM and licence provenance | Licence compliance matters here beyond security: the estate is built on Odoo CE (LGPL-3) and OCA modules, and `TD-01` depends on that position holding |

### 2.2 Source material

| Source | What it supplies |
|---|---|
| `SC-001` §9.2 | `SEC-C-055`, `SEC-C-056` — the controls this document realises |
| `SC-002` §8 | **32 abuse cases**, each with a test obligation |
| `SC-002` §7 | The Top 10:2025 map that §6 rules must cover |
| `SC-004` §8 | 67 access profiles, whose `AP-12` negative tests are gate `G-09` |
| `02-05` §9 | Repository, branching, commit convention, pre-commit, CI, CD, secrets, dependency management |
| `05-06` §7 | **Unit test coverage ≥ 80%; 100% on financial calculations** — note the `NFR-090`/`091`/`092` collision (`OP-19`), so this is cited as **`05-06` §7 `NFR-090`**, disambiguated |
| `LG-021` `IS-06` | The six policy clauses this document makes executable |
| `AR-007` | Odoo module architecture and code-structure standard |
| `AR-012` | Architecture fitness functions — the neighbouring gate family |

### 2.3 Enumeration

| # | Figure | **Counted 2026-08-18 13:55 (+06)** | Note |
|---|---|---:|---|
| 1 | Files in the workspace under version control | **0** | `PGD-A2-15`. **The precondition of every gate in §5** |
| 2 | Specification of the CI "security scan" | **0 documents** | `02-05` §9 names it in one table cell |
| 3 | Abuse cases requiring a test | **32** (`SC-002` §8) | `G-10` |
| 4 | Access-profile negative-test sets | **67** (`SC-004` §8.4) | `G-09` |
| 5 | Custom modules to be built | `CD-` identifiers in use to **`CD-248`**; register of 138 (`RQA-10`: 31 collide) | Every one passes these gates |
| 6 | Portal surfaces with independent front-end builds | **12** — 6 Next.js, 4 Flutter, 2 Odoo-native | Each needs its own gate set |
| 7 | External integration destinations | **47** | `G-13` egress allow-list is build-time enforced |
| 8 | Security tooling with a commercial licence budgeted | **0** | `SEC-CON-03`. §5 selects open-source tooling accordingly |

---

## 3. Security Activities by Stage

| Stage | Activity | Output | A.8.2x | SSDF |
|---|---|---|---|---|
| **Requirements** | Security and privacy requirements stated **before build**; `05-06` §4/§6 are those requirements; new features state their `S`-classification and residency impact | Classified requirement set | A.8.26 | `PO.1` |
| | Abuse cases identified for any new external surface | Abuse-case entries | A.8.26 | `PW.1` |
| **Design** | **Threat model updated** per `SC-002` §13 triggers; a new trust boundary is a mandatory re-model | `SC-002` delta | A.8.27 | `PW.1` |
| | Design review against `SC-001` §7 enforcement points — **where is authorisation decided for this feature?** | Review record | A.8.27 | `PW.1` |
| | **Data classification decided at design time**, not at implementation | Field classification entries | A.8.26 | `PO.5` |
| **Implementation** | §6 secure coding rules; pre-commit gates `G-01`…`G-03` | Clean commit | A.8.28 | `PW.5` |
| | **Security-relevant code reviewed by a second developer with a security checklist** | Review record | A.8.28 | `PW.7` |
| **Verification** | Gates `G-04`…`G-10`; abuse-case tests; profile negative tests | Gate evidence | A.8.29 | `PW.8`, `RV.1` |
| | ASVS verification at the bound level | ASVS checklist | A.8.29 | `PW.8` |
| **Release** | Gates `G-11`…`G-14`; provenance; SBOM; approval | Signed artefact + SBOM | A.8.31 | `PS.1`–`PS.3` |
| **Operate** | Continuous scanning; `SC-009` triage; feedback into `SC-002` | Vulnerability records | A.8.8 | `RV.1`–`RV.3` |
| **Outsourced** | §11 — vendor obligations and evidence | Contractual evidence | **A.8.30** | `PO.3` |

---

## 4. SSDF Practice Coverage

| SSDF group | Practices | Where realised | State |
|---|---|---|---|
| **`PO` Prepare the Organization** | `PO.1` define requirements · `PO.2` roles and responsibilities · `PO.3` supporting toolchains · `PO.4` criteria and evidence · `PO.5` **secure environments** | §3, §5, §10, `PE-004` | ◐ `PO.2` blocked — **no Security Lead appointed** |
| **`PS` Protect the Software** | `PS.1` protect code from unauthorised change · `PS.2` **provide verification mechanism** · `PS.3` archive and protect each release | `G-11`, `G-12`, `G-14` | ✖ **`PS.1` cannot be met — nothing is under version control** |
| **`PW` Produce Well-Secured Software** | `PW.1` design to meet requirements · `PW.2` review design · `PW.4` **reuse well-secured software** · `PW.5` secure coding · `PW.6` build with hardened settings · `PW.7` review code · `PW.8` **test executable code** | §3, §5, §6, §8 | ◐ Specified here; none built |
| **`RV` Respond to Vulnerabilities** | `RV.1` identify · `RV.2` assess and remediate · `RV.3` root-cause analysis | `SC-009` | ✖ **`LG-021` `O-09` — no discovery mechanism exists** |

> **`SC-005-F-01`. `PS.1` is the finding that gates everything else.** SSDF `PS.1` — *protect all
> forms of code from unauthorised access and tampering* — is the practice every other build control
> rests on. **With 644+ files and zero version control (`PGD-A2-15`), there is no baseline, no
> attributable change history and no way to detect tampering.** Signed artefacts, provenance and
> four-eyes review are all meaningless without it. **Establishing version control is therefore
> `G-00` — a precondition, not a gate**, and it is the single cheapest high-value action in
> Category 05 after break-glass.

---

## 5. The Gates

**Gate semantics.** ● **blocking** — the pipeline stops · ◐ **warning** — recorded, does not stop ·
Every blocking gate has an **exception path** (§9). A gate with no exception path is bypassed by
disabling it, which is worse.

### 5.0 `G-00` — the precondition

| | |
|---|---|
| **Requirement** | **All source, configuration, IaC and identity profiles are held in version control**, with protected branches and attributable history |
| **Why it is `G-00`** | SSDF `PS.1`. Nothing in §5 can be enforced without it |
| **Owner** | CTO with Platform Engineering |
| **Needed by** | **Before any other gate is meaningful. W1, first week** |
| **State** | ✖ **Not met.** `PGD-A2-15` |

### 5.1 Pre-commit — `G-01` … `G-03`

| Gate | Checks | Fails on | Tooling class | Sem |
|---|---|---|---|:--:|
| `G-01` **Secret scanning** | Credentials, tokens, private keys, connection strings, high-entropy strings in the diff **and in history** | **Any** finding | Open-source secret scanner, pre-commit hook | ● |
| `G-02` **Lint and static rules** | Language linters plus the §6 security rule set encoded as lint rules | Any security-classified rule | Language-native + Odoo-specific | ● |
| `G-03` **Classification check** | A new model field must carry `S`-class and residency-class metadata | A field with neither | Custom check against `AR-007` conventions | ● |

> **`G-01` scans history, not only the diff.** A secret removed in a later commit is still in the
> repository and still valid. `NFR-062` says secrets are *"never in code, configuration files or
> logs"*; a secret in git history is in the code.

> **`G-03` is the gate that makes `SEC-DC-1` real.** `SC-001` requires classification to be data,
> not documentation. A field added without a classification defaults to unclassified, and an
> unclassified NID field is `SC-002` `TH-047` — the highest-rated tampering threat in the estate,
> committed by an ordinary developer with no hostile intent (`AB-21`).

### 5.2 Pull request — `G-04` … `G-10`

| Gate | Checks | Fails on | Sem |
|---|---|---|:--:|
| `G-04` **SAST** | Static analysis across Python/Odoo, TypeScript, Dart | **High or Critical** finding | ● |
| `G-05` **SCA — dependency vulnerabilities** | Direct **and transitive** dependencies, Python/npm/pub/container base images | **Critical**, or High with a fix available | ● |
| `G-06` **SBOM and licence** | SBOM generated; licence compatibility with LGPL-3/Apache-2.0 distribution position | Missing SBOM; **incompatible licence** | ● |
| `G-07` **IaC and configuration policy** | Zone flow matrix (`SC-001` §5.2), storage exposure, TLS config, egress allow-list membership | Any deviation from `SC-001` §5.2 | ● |
| `G-08` **ASVS verification** | The bound level for the touched path — **L2 default, L3 for `Z4`-touching, admin API and payment paths** | Any unmet applicable requirement | ● |
| `G-09` **Access-profile negative tests** | `SC-004` `AP-12` sets for every profile touching a changed model | **Any** negative test passing when it should fail | ● |
| `G-10` **Abuse-case tests** | The `SC-002` §8 cases mapped to the changed surface | Any abuse case succeeding | ● |

> **`G-09` and `G-10` are the two gates this estate would not otherwise have.** A conventional
> pipeline has SAST, SCA and IaC scanning. **Neither of those would catch `AB-05`** — an
> authenticated customer reading another customer's invoice by id substitution — because it is not
> a code defect, it is a missing record rule. `G-09` executes the negative test; `G-10` executes
> the abuse case. **They are what convert `SC-002` from a document into a control.**

### 5.3 Build and release — `G-11` … `G-14`

| Gate | Checks | Fails on | Sem |
|---|---|---|:--:|
| `G-11` **Container and image scan** | Base image and layers; hardened settings (`PW.6`); non-root; no shell where avoidable | Critical CVE; root user | ● |
| `G-12` **Build provenance and signing** | Artefact signed; provenance attestation recorded (SLSA L2 → L3 at W4) | Unsigned or unattested artefact | ● |
| `G-13` **Egress allow-list conformance** | Any new outbound destination in code or config exists in the `Z6` allow-list **and has a `LG-012` §4.5 transfer row** | An unlisted destination, or one with no transfer row | ● |
| `G-14` **DAST on staging** | Dynamic scan of the deployed surface, authenticated and unauthenticated | High or Critical | ◐ **at W1**, ● **from W2** |

> **`G-13` is unusually strict and deliberately so.** It refuses a build that would call a
> destination with **no registered data-transfer row** — implementing `RD-R4` (*the gate precedes
> the transfer*) at build time rather than at runtime. It is also the gate that will fail first and
> most often, because `LG-012` §4.5 currently registers **zero of eight** anticipated transfers.
> **That failure is correct behaviour**, and it converts a governance gap into a visible build
> blocker rather than a silent runtime one.

### 5.4 Continuous — post-release

| Activity | Cadence | Feeds |
|---|---|---|
| Dependency and container re-scan against new advisories | Daily | `SC-009` `RV.1` |
| Runtime configuration drift detection | Continuous | `SC-002` `TH-038` |
| Secret rotation verification | Per `SC-006` schedule | `SC-006` |
| SBOM re-evaluation on new CVE publication | Daily | `A03:2025` |

---

## 6. Secure Coding Rules

31 rules. Every rule is **encoded as a lint rule, a test, or a gate** wherever mechanisable — an
unenforceable coding rule is a preference. Rules marked ⚙ are machine-checked at `G-02`.

### 6.1 Authorisation and isolation — the estate's dominant risk class

| # | Rule | Enforces |
|---|---|---|
| `SR-01` ⚙ | **No module implements its own authentication, session handling or permission engine** | `BRU-SEC-09` |
| `SR-02` | **Every authorisation decision is evaluated server-side, in-transaction, on every request.** A gateway, BFF or client filter is never the control | `BRU-SEC-10`, `SC-001` `SEC-EP-1` |
| `SR-03` | **Scope comes from the credential, never from a request parameter** | `EA-11`, `AB-06` |
| `SR-04` ⚙ | A new model carries a record rule for its isolation tier **in the same commit** | `NFR-015`, `TH-035` |
| `SR-05` | **Field permissions apply on write as well as read.** Mass assignment is the default failure | `TH-015` |
| `SR-06` | **No business rule is implemented client-side.** The client validates for convenience only | `PS-11` |
| `SR-07` | A list endpoint returns the same rows with and without any presentation filter | `AB-05`, `G-09` |

### 6.2 Data protection and residency

| # | Rule | Enforces |
|---|---|---|
| `SR-08` ⚙ | **Every new field declares `S`-class and residency class** | `G-03`, `SEC-DC-1` |
| `SR-09` | **A residency-classified field is accessed only through the residency service.** Direct ORM access is a build error | `SEC-ZR-2`, `TH-047` |
| `SR-10` | **No cache, replica, materialised view or search index over a residency-classified field** | `SEC-DC-2`, `SEC-DC-3` |
| `SR-11` ⚙ | **Classified fields are redacted at emission** by the logging library, configured from the classification — never by a per-call decision | `SEC-DC-4`, `BRU-SEC-24` |
| `SR-12` | **`S3` fields use the field-level key, never the database key** | `BRU-SEC-15` |
| `SR-13` | A migration or data-fix script is subject to the same residency and classification checks as application code | `TH-036` |

### 6.3 Cryptography, secrets and integrity

| # | Rule | Enforces |
|---|---|---|
| `SR-14` | **Use the approved cryptographic suite from `SC-006`. Never implement a primitive** | `SC-006` |
| `SR-15` ⚙ | **No secret in source, configuration, container image, manifest, log, ticket or CI output.** Vault only | `NFR-062`, `G-01` |
| `SR-16` | **The application holds a key reference, never key material** | `SEC-KM-2` |
| `SR-17` | **Egress credentials are injected at the proxy.** Application code never possesses them | `SEC-KM-5` |
| `SR-18` | Randomness for security purposes uses a cryptographic source | ASVS |
| `SR-19` | **Algorithm agility**: a cipher or hash is referenced through a configurable suite, never hard-coded | `LG-021` §4.4.6 |

### 6.4 Input, output and exceptional conditions

| # | Rule | Enforces |
|---|---|---|
| `SR-20` ⚙ | Parameterised queries only; no string-built SQL | `A05:2025` |
| `SR-21` | Output encoding contextual to the sink; **CSP on every portal surface** | `TH-003`, `TH-059` |
| `SR-22` | **Every uploaded file is malware-scanned before storage or serving**, and served with a non-executing content type | `BRU-SEC-22`, `TH-020` |
| `SR-23` | **Errors never disclose personal data, stack traces or internal identifiers to a client** | **`A10:2025`**, `TH-053` |
| `SR-24` | **A failure in a security control fails closed**, per `SC-001` §12. A `try/except` that swallows an authorisation error is a defect | `A10:2025` |
| `SR-25` | **Idempotency keys enforced on every write endpoint** | `TH-018` |

### 6.5 Audit, attribution and supply chain

| # | Rule | Enforces |
|---|---|---|
| `SR-26` ⚙ | **A module never writes its own audit code.** Audit is inherited | `BRU-SEC-12`, `SEC-SD-4` |
| `SR-27` | **A `T5` or `S3` read writes its access log entry before the value is returned** | `TH-043` |
| `SR-28` ⚙ | Dependencies are **pinned by version and digest**; no floating tags | **`A03:2025`**, `TH-094` |
| `SR-29` | A **new dependency requires review** — provenance, maintenance, licence, transitive footprint (`PW.4`) | `A03:2025` |
| `SR-30` | **A new outbound destination requires an allow-list entry and a transfer row before merge** | `G-13`, `RD-R4` |
| `SR-31` | **Test fixtures are synthetic.** Production data never enters `local` or `dev` in any form | `SEC-NP-1`, `AB-14` |

### 6.6 Rule-to-Top-10 coverage

| `A01` | `A02` | `A03` | `A04` | `A05` | `A06` | `A07` | `A08` | `A09` | `A10` |
|---|---|---|---|---|---|---|---|---|---|
| `SR-01`…`SR-07` | `SR-11`, `SR-21`, `G-07` | `SR-28`…`SR-30`, `G-05`, `G-06`, `G-12` | `SR-12`, `SR-14`, `SR-19` | `SR-20`…`SR-22` | `SC-002`, `G-10` | `SR-01`, `SC-004` §6 | `SR-26`, `G-12`, `G-11` | `SR-11`, `SR-26`, `SR-27` | **`SR-23`, `SR-24`** |

**Every 2025 category has at least one enforceable rule.** ✓

---

## 7. Security Review Checkpoints

Automation catches the mechanisable. Four checkpoints require a human, and each has a defined
trigger so *"a security review"* is not a matter of judgement about whether one is needed.

| # | Checkpoint | Trigger | Reviewer | Output |
|---|---|---|---|---|
| `RC-1` | **Design review** | Any new external surface, trust boundary, integration, or model holding `S3` data | Security Lead + Chief Architect | Recorded decision; `SC-002` delta |
| `RC-2` | **Security code review** | Any change to authentication, authorisation, record rules, field permissions, the residency service, the audit path, cryptography, or file upload | A second developer using the §6 checklist; Security Lead for `Z4` paths | Review record on the PR |
| `RC-3` | **Pre-release review** | Every release to `prod` | Delivery lead + Security Lead | Gate evidence pack (§10) |
| `RC-4` | **Post-incident code review** | Any security incident with a code root cause | Security Lead | `SC-002` `RM-05` update; `RV.3` root-cause record |

> **`SC-005-F-02`. `RC-2`'s trigger list is deliberately concrete.** *"Security-relevant changes are
> reviewed"* is unactionable — every developer believes their change is not security-relevant. The
> eight named areas cover every enforcement point in `SC-001` §7.1 plus the two components whose
> compromise is a statutory event.

---

## 8. Abuse-Case and Negative Testing

The obligation that distinguishes this standard from a generic one.

| # | Obligation |
|---|---|
| `AT-1` | **Every abuse case in `SC-002` §8 has an automated test.** 32 cases; 32 tests. A case with no test is an open finding |
| `AT-2` | **Every access profile's `AP-12` negative tests are automated.** 67 profiles |
| `AT-3` | A negative test **asserts failure**: *"seller A requesting seller B's payout by id receives zero rows"*, not *"the UI does not show it"* |
| `AT-4` | **`SR-07` is tested by removing the presentation filter**, not by inspecting it |
| `AT-5` | **Residency tests attempt the prohibited write and assert the transaction aborts** (`AB-21`). A warning is a failure |
| `AT-6` | SoD tests include a **controlled violation attempt** per rule, per cycle | `BRU-GRC-09` |
| `AT-7` | New abuse cases arising from an incident or a pen-test finding are added within the remediation, not after |

**Counted obligation: 32 abuse-case tests + 67 profile negative-test sets = 99 security test
artefacts**, all before W1 go-live. This is `QA-007`'s work package and it is sized here so it is
not discovered late.

---

## 9. Gate Exceptions

A blocking gate with no exception path gets disabled. This is the path.

| # | Rule |
|---|---|
| `EXC-1` | An exception is **requested, not taken**. Bypassing a gate by disabling it is a disciplinary matter and a `RC-4` trigger |
| `EXC-2` | Approver: **Security Lead** for High; **CTO** for Critical; **never the requesting developer** (`SOD-09` by analogy) |
| `EXC-3` | Every exception is **time-boxed** with an automatic expiry. Default 14 days; maximum 90 |
| `EXC-4` | Every exception carries a **compensating control** and a remediation owner |
| `EXC-5` | Live exceptions appear on a **standing report reviewed at each wave gate** and in `GV-009` gate evidence |
| `EXC-6` | **`G-01` secret scanning and `G-13` egress conformance admit no exception.** A secret in the repository and an unregistered transfer are not risks to be accepted at build time — the first is remediated by rotation, the second by registration |
| `EXC-7` | An expired exception **re-blocks the pipeline**. It does not lapse into permission |

---

## 10. Evidence

ISO/IEC 27001 A.8.29 and SSDF `PO.4` require the evidence, not merely the activity. `LG-021`
§4.1.6: *a control asserted as operating without evidence is a deficiency, not a pass*.

| Activity | Evidence | Retention | Consumer |
|---|---|---|---|
| `G-01`…`G-14` execution | Gate result with commit, timestamp, actor | Per `LG-009` | `GV-009`, auditor |
| `RC-1`…`RC-4` | Review record naming the reviewer and the decision | Per `LG-009` | `M60` control test |
| ASVS verification | Completed checklist per level per path | Per release | Certification body |
| SBOM | Per artefact, per release | Life of the release + 5 years | `A03:2025`, licence |
| Provenance attestation | Per artefact | Life of the release | `PS.2` |
| Exceptions | Request, approval, compensating control, expiry, closure | 5 years | `GV-009`, Internal Audit |
| Abuse-case and negative-test results | Per pipeline run | Per `LG-009` | `QA-007`, `SC-002` `RM-06` |

> **The gate evidence pack is a `GV-009` wave-gate evidence class.** `GV-009` supplies eight
> evidence classes and named assessors; this is the security one, and without it a wave gate
> assesses build security on assertion.

---

## 11. Outsourced Development — A.8.30

The build is expected to be vendor-delivered (`CO-003`). A.8.30 requires the organisation to
direct, monitor and review outsourced development.

| # | Obligation |
|---|---|
| `OD-1` | **This standard is a contractual obligation**, incorporated by reference into `CO-003` |
| `OD-2` | The vendor uses **1000FiX's pipeline and gates**, not their own. A vendor-side gate produces evidence 1000FiX cannot verify |
| `OD-3` | **Vendor personnel are provisioned identities under `SC-004`**, subject to the same JML, certification and SoD rules |
| `OD-4` | **No production or unmasked data reaches a vendor environment** (`SEC-NP-1`) |
| `OD-5` | Source is held in **1000FiX's** version control (`G-00`), not the vendor's |
| `OD-6` | The vendor supplies SBOM and provenance for anything it introduces |
| `OD-7` | **Right to audit the vendor's development practice**, exercised at least once per wave |
| `OD-8` | Security defects found post-acceptance are remediated under the warranty, at the vendor's cost, to `SC-009` SLAs |

---

## 12. AI Components — SP 800-218A

`M26` AI/ML services and `M32` conversational AI introduce a development surface v1.1 does not
address. SP 800-218A augments the SSDF for generative AI and dual-use foundation models.

| # | Obligation | Source |
|---|---|---|
| `AI-1` | **Training and retrieval data provenance is recorded.** What went in, from where, on what basis | `PO.5`, `SP 800-218A` |
| `AI-2` | **`BRU-DTS-14` is a build-time control: recovered customer data is never training or retrieval data** | `M06`, `DPIA-02` |
| `AI-3` | **`P-14` transcript-derived corpora may not be ingested** while `SC-003` `DPIA-06` stands | **`SC-003` `A-07`** |
| `AI-4` | Model inputs and outputs are treated as untrusted; prompt-injection and output-handling tests are abuse cases | `A05:2025`, `SC-002` |
| `AI-5` | The model service is a `Z6` egress destination with an allow-list entry and a transfer row (`TR-06`) | `G-13` |
| `AI-6` | Model artefacts are versioned, signed and provenance-attested like any other artefact | `PS.2` |
| `AI-7` | **AI-assisted code generation is subject to every gate in §5 without exception**, and generated dependencies are subject to `SR-29` review | `PW.4` |

> **`AI-7` deserves its own line.** Code suggested by an assistant is code the organisation ships.
> `A03:2025` supply-chain failures include dependencies introduced without review, and a generated
> import is exactly that.

---

## 13. Maturity Position — OWASP SAMM 2.0

Stated so the programme knows where it is, not to claim a level.

| SAMM business function | Current | W4 target | Gap |
|---|:--:|:--:|---|
| **Governance** — strategy, policy, education | **1** | 2 | `LG-021` exists; **no security education vehicle** (`TR-025` unregistered) |
| **Design** — threat assessment, security requirements, architecture | **1** | **2** | `SC-001`, `SC-002` issued today. Was **0** yesterday |
| **Implementation** — secure build, deployment, defect management | **0** | 2 | **No version control, no pipeline, no defect management** |
| **Verification** — architecture assessment, requirements testing, security testing | **0** | 2 | `AR-012` and `QA-007` specified, not built |
| **Operations** — incident management, environment management, operational management | **0** | 2 | `SC-011` issued today; no environments |

> **`SC-005-F-03`. Three of five functions are at maturity 0, and the reason is uniform: nothing is
> built yet.** That is the correct and expected state for a programme at W0 — **provided the
> documents that define maturity 1 and 2 exist before the build starts, which is what Category 05
> is doing.** The finding is not that maturity is low; it is that `Implementation` cannot move off
> 0 until `G-00` is met.

---

## 14. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | **When is version control established?** (`G-00`) | CTO | **W1, week 1** | Every gate; SSDF `PS.1` |
| `Q-02` | Who is the **Security Lead**? `RC-1`…`RC-4` and `EXC-2` all name the role | CTO | **W1** | SSDF `PO.2` |
| `Q-03` | Is the open-source tool selection accepted, or is a commercial SAST/SCA licence funded? | CTO with CFO | W1 | §5 tooling; `SEC-CON-03` |
| `Q-04` | Is SLSA Build Level 3 a W4 commitment, or does L2 stand? | CTO | W4 | `G-12` |
| `Q-05` | Does the vendor accept `OD-2` — building in 1000FiX's pipeline? | CCO with CTO | Before `CO-003` signature | §11 |
| `Q-06` | Is `QA-007`'s **99-artefact** security test package resourced? | Delivery lead | W1 | `AT-1`, `AT-2` |
| `Q-07` | Does the programme adopt SSDF v1.2 when finalised, or hold v1.1 to the end of the build? | Security Lead | W4 | §2.1; `RM` trigger |

---

## 15. Decisions Recorded

| # | Decision | Options | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `SC-005-D-01` | SSDF version | v1.1 final · v1.2 draft | **v1.1** | v1.2 is an initial public draft in comment (Dec 2025). Building on a draft repeats the `H-01` failure mode | `Q-07` re-verification trigger |
| `SC-005-D-02` | ASVS level | L1 · L2 · L3 · **mixed** | **L2 baseline, L3 for `Z4`, admin and payment paths** | L3 estate-wide is not proportionate under `SEC-CON-03`; L1 is insufficient for the `SC-001` §3.1 consequences | `G-08` binds per path, which requires path classification |
| `SC-005-D-03` | Gate severity | Warn first, block later · **Block from W1** | **Block, with an exception path** | A warning gate is a metric, not a control. `EXC-1`…`EXC-7` makes blocking survivable | Pipeline friction at W1; `G-13` will fail immediately and correctly |
| `SC-005-D-04` | `G-01`/`G-13` exceptions | Allow · **Refuse** | **Refuse** | A secret in the repo is remediated by rotation, not by acceptance; an unregistered transfer is remediated by registration | `EXC-6`; `G-13` becomes a governance forcing function |
| `SC-005-D-05` | Where the vendor builds | Vendor pipeline · **1000FiX pipeline** | **1000FiX pipeline** | Vendor-side gate evidence cannot be verified by the party accountable for it (A.8.30) | `OD-2`; contractual, `Q-05` |
| `SC-005-D-06` | Abuse-case testing | Manual at pen-test · **Automated in CI** | **Automated** | 32 cases executed once a year is a report; executed per PR it is a control | `AT-1`; `QA-007` resourcing (`Q-06`) |

---

## 16. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | Every stage has named security activities with outputs | §3 |
| `AC-02` | Every SSDF practice group is addressed, **including those that cannot be met** | §4 — `PS.1` ✖ stated |
| `AC-03` | Every gate has a fail condition, semantics and an owner | §5 — 15 gates incl. `G-00` |
| `AC-04` | Every coding rule is enforceable, and machine-checked where mechanisable | §6 — 31 rules, 11 marked ⚙ |
| `AC-05` | Every OWASP Top 10:2025 category has an enforceable rule | §6.6 |
| `AC-06` | Human review checkpoints have concrete triggers | §7 — 4 checkpoints, 8 named trigger areas |
| `AC-07` | Abuse cases and profile negative tests are counted and assigned | §8 — **99 artefacts** |
| `AC-08` | An exception path exists, is time-boxed, and has non-exceptable gates | §9 |
| `AC-09` | Evidence is defined per activity with a consumer | §10 |
| `AC-10` | Outsourced development obligations are stated (A.8.30) | §11 — 8 obligations |
| `AC-11` | AI components are covered by SP 800-218A | §12 — 7 obligations |
| `AC-12` | Standards versions are verified and draft status is stated | §2.1; `SC-005-D-01` |

---

## 17. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `SC-001` | `SEC-C-055`, `SEC-C-056`; the zone rules `G-07` enforces |
| Upstream | `SC-002` | 32 abuse cases → `G-10`; Top 10 map → §6.6 |
| Upstream | `SC-004` | 67 profiles → `G-09` |
| Upstream | `AR-007`, `AR-012` | Code structure; fitness functions |
| Downstream | `SC-006` | `SR-14`, `SR-19` reference the approved suite |
| Downstream | `SC-009` | `RV.1`…`RV.3`; findings flow from §5.4 |
| Downstream | `PE-004` | Builds the gates |
| Downstream | `QA-007` | Executes the 99 security test artefacts |
| Downstream | `CO-003` | §11 becomes a contractual obligation |
| Lateral | `../../1000fix_ERP_Module/02_Architecture/02-05_*.md` §9 | The two table cells this document expands |
| Lateral | `../../project_content/10_Legal_Policy_and_Compliance/LG-021_*.md` `IS-06` | The policy this makes executable |

---

## 18. References

**Within this repository**
`../PGD-000_*.md` · `./_CATEGORY_OVERVIEW.md` · `./SC-001`, `./SC-002`, `./SC-004`, `./SC-006`, `./SC-009` ·
`../02_Architecture_and_Design/AR-007_*.md`, `AR-012_*.md`

**Workspace**
`../../1000fix_ERP_Module/02_Architecture/02-05_*.md` ·
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_*.md` §4, §7 ·
`../../project_content/10_Legal_Policy_and_Compliance/LG-021_*.md`

**External standards** *(all verified 2026-08-18)*

| Source | Version / status | Used for |
|---|---|---|
| ISO/IEC 27001 | :2022 + Amd 1:2024 — **A.8.25–A.8.31** | Stage obligations |
| **NIST SP 800-218 SSDF** | **v1.1, February 2022 — current final.** SP 800-218r1 (v1.2) is an **initial public draft released 17 December 2025**, in public comment — **not adopted** | §4 practice mapping |
| **NIST SP 800-218A** | July 2024 — generative-AI SSDF community profile | §12 |
| **OWASP ASVS** | **5.0.0 (30 May 2025)** — 17 chapters, ~350 requirements, 3 levels. **Supersedes 4.0.3** | `G-08` |
| **OWASP Top 10** | **2025 (6 Nov 2025; finalised Jan 2026)** — new `A03`, `A10` | §6.6 |
| OWASP SAMM | 2.0 | §13 |
| SLSA | Build levels | `G-12` |
| ISO/IEC 5230 | OpenChain | `G-06` |

---

## 19. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. Converts `LG-021` `IS-06` from six policy clauses into 15 gates, 31 rules, 4 review checkpoints and 99 security test artefacts. Raises `G-00`: **version control is a precondition, and SSDF `PS.1` cannot be met without it**. Corrects the estate's ASVS 4 citation to 5.0.0 | *Pending — no constituted body (`PGD-A2-25`)* |

---

*`SC-005` · Category 05 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
