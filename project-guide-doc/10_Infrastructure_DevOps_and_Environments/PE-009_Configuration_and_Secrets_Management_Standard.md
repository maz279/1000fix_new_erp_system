---
id: PE-009
title: Configuration & Secrets Management Standard
category: 10 — Infrastructure, DevOps & Environments
code: PE
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-19
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Platform Engineering Lead
approver: CTO with Security Lead and Design Authority (constituted under GV-002)
standards_basis: >
  Twelve-Factor App §3 config · NIST SP 800-57 key management · NIST SP 800-63B ·
  OWASP Secrets Management Cheat Sheet · CIS Controls v8 (5, 6, 16) ·
  ISO/IEC 27001:2022 A.5.15–A.5.18, A.8.24
traces_to: >
  PGD-000 PE-009 · 02-05 §9 · Technology Stack §18.4 · PE-002 · PE-003 §9, §10.3 ·
  PE-004 §11.2 · PE-005 CS-07 · PE-007 §4.7 · SC-004 · SC-006 · IN-001 EG-05 ·
  audit OP-08, OP-10, OP-15 · NFR-062, NFR-070, OPS-02, OPS-06, IP-07
depends_on: PE-002 · PE-003 · PE-005 · SC-004 · SC-006
verified_on: 2026-08-19
priority: P0
needed_by: W1
enumeration_timestamp: 2026-08-19 01:45 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# PE-009 — Configuration & Secrets Management Standard

### Category 10 · Code `PE` · Twelve-Factor §3 · NIST SP 800-57 · ISO/IEC 27001:2022

---

> **`PGD-000`'s `PE-009` row:** *"`02-05` §9 says 'Vault-managed; never in the repository; rotation
> scheduled.' Audit **`OP-08`**: **'break-glass, the on-call rota and the 38 access profiles are all
> documented and none exists.'**"*
>
> **That sentence is the whole problem.** Eleven words of standard, and an audit finding that the
> emergency access path the estate's entire "no standing access" model depends on **has never been
> built**.
>
> **State at 2026-08-19 01:45 (+06):**
>
> | Element | State |
> |---|---|
> | Secret store named | ✔ Vault (`02-05` §9, Technology Stack §18.4) |
> | Secret store **specified** — engine, policy model, auth methods, unseal | **✘** |
> | **Break-glass procedure** | **✘ — `OP-08`** |
> | Rotation schedule per secret class | **✘ — *"rotation scheduled"* names no schedule** |
> | Configuration hierarchy across **twelve** environments | **✘** |
> | Feature-flag model | Named as `CD-135` (`OPS-06`); **undesigned** |
> | **38 access profiles** | **✘ — `OP-10`**, and the register they check against is ambiguous |

---

## 1. Purpose

Configuration and secrets are the two things that differ between environments running identical
artefacts (`PE-004` `PE-004-D-01`). They are therefore the mechanism by which a correct build
behaves incorrectly in production — and the mechanism by which a credential reaches a place it
should never be.

This document specifies both: the configuration hierarchy and its precedence, what may be
configuration and what may not, the feature-flag model, the secret store and its policy model, secret
classes with their rotation cadences, injection into workloads, the **break-glass procedure `OP-08`
found missing**, key management's boundary with `SC-006`, and the audit trail that makes secret use
reviewable.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | The **configuration hierarchy** and precedence across `PE-002`'s twelve environments |
| 2 | What is configuration, what is code, what is a secret — with a decision test |
| 3 | Configuration promotion, and `OPS-02`'s *"never hand-edited in production"* |
| 4 | **Feature flags** — `CD-135`, `OPS-06`, and the discipline that stops them accumulating |
| 5 | The **secret store**: engine, auth methods, policy model, unseal, HA |
| 6 | **Secret classes and rotation cadence** — replacing *"rotation scheduled"* |
| 7 | **Injection** into workloads, pipelines and IaC |
| 8 | **Break-glass** — the procedure `OP-08` records as absent |
| 9 | The boundary with `SC-006` key management and `SC-004` identity |
| 10 | **`Z4` secret separation** and in-country key custody |
| 11 | Audit, detection and response to exposure |
| 12 | Fitness functions `FF-175`…`FF-184` |

**Explicitly out of scope**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| **Cryptographic algorithms, key lengths, key ceremonies** | **`SC-006`** | This document stores and delivers; `SC-006` decides the cryptography |
| Human identity, roles, authentication, the 38 access profiles | **`SC-004`**, `05-04` | §9.2 states the interface; `OP-10` is `SC-004`'s |
| Infrastructure resource configuration | **`PE-003`** §10.3 | The boundary test is restated in §3.3 |
| Which environments exist | **`PE-002`** | |
| Pipeline stages and credentials model | **`PE-004`** §11.2 | This document supplies what it injects |
| Container runtime secret mounting | **`PE-005`** `CS-07` | §7.2 specifies the interface |
| Secret **backup and escrow** | **`PE-007`** §4.7 | Recovery, not operation |
| On-call rota and escalation | `SV-*`, `OP-013` | `OP-08` bundles them; only break-glass is here |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| Platform engineers | The whole document |
| Every developer | §3's decision test and §5's flag discipline |
| **Security Lead** | §6, §8, §11 |
| **CTO** | §8 — break-glass authority is a named-person decision |
| Auditors | §11's trail |
| DPO | §10 — `Z4` key custody |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Concept | Conformance | Departure and rationale |
|---|---|---|---|
| **Twelve-Factor App §3** | Config in the environment, strictly separated from code | §3, §4 | **Departure on mechanism:** the estate uses a **hierarchical configuration service**, not environment variables alone — §3.4 says why |
| **NIST SP 800-57** | Key management lifecycle; cryptoperiods | §6.3's rotation cadences | Cryptographic parameters are `SC-006`'s |
| **NIST SP 800-63B** | Authenticator lifecycle | §6, §8 | Human authentication is `SC-004`'s |
| **OWASP Secrets Management** | Storage, distribution, rotation, detection | §6, §7, §11 | None |
| **CIS Controls v8** (5 account, 6 access, 16 application security) | Account and access management | §8, §9.2 | None |
| **ISO/IEC 27001:2022 A.5.15–A.5.18, A.8.24** | Access control, privileged rights, authentication, cryptography use | §8, §9 | None |

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| **`AUDIT-017` `OP-08`** | `../../project_content/_AUDIT/AUDIT-017_*.md` | **"Break-glass access is documented and does not exist"** |
| `AUDIT-017` `OP-10`, `OP-15` | Ibid. | 38 access profiles do not exist; leaver revocation has two deadlines 23 hours apart |
| `02-05` §9 | `../../1000fix_ERP_Module/02_Architecture/02-05_*.md` | *"Vault-managed; never in the repository; rotation scheduled"* |
| Technology Stack §18.4 | `../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` | `OPS-02` promotion; `OPS-06` feature flags (`CD-135`); expiry alerted 30 days ahead |
| **`PE-002`** | `./PE-002_*.md` | Twelve environments; `LC-06`'s banner |
| **`PE-003`** §9, §10.3 | `./PE-003_*.md` | `SI-01`…`SI-06`; the infrastructure/application configuration boundary |
| `PE-004` §11.2 | `./PE-004_*.md` | `CR-01`…`CR-05`; the pull-request trust boundary |
| `PE-005` `CS-07` | `./PE-005_*.md` | Runtime secret mounting |
| `PE-007` §4.7 | `./PE-007_*.md` | Snapshot, **unseal-key escrow**, `SB-05` |
| `SC-004`, `SC-006` | `../05_Security_Privacy_and_Compliance/` | Identity and authorisation; cryptography and key management |
| `IN-001` `EG-05` | `../04_Integration_and_API_Engineering/IN-001_*.md` | Credential injection at the `Z6` egress proxy |
| `05-06` | `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_*.md` | `NFR-062`, `NFR-070` |

### 2.3 Audit findings this document closes or contributes to

| Finding | Source | Disposition |
|---|---|---|
| **`OP-08` (high)** — *"break-glass access is documented and does not exist"* | `AUDIT-017` | **The break-glass half is designed** — §8. **Closes on implementation and the first rehearsal.** The rota and access profiles are `SV-*` and `SC-004`'s |
| `PGD-000` `PE-009` — eleven words of standard | `PGD-000` | **Closed as a standard** |
| `OPS-02` — configuration promoted, never hand-edited in production | Technology Stack §18.4 | §4.3; `FF-176` |
| `OPS-06` — any new capability disableable without a deployment (`CD-135`) | Ibid. | §5 |
| `NFR-062`, `IP-07` — secrets vaulted, never in code, configuration or logs | `05-06` | §6, §11.2; `FF-175` |
| **`OP-10`** — 38 access profiles do not exist; the register is ambiguous | `AUDIT-017` | **Not this document's.** §9.2 states the dependency; **`SC-004` owns it**, and `IN-005` §5.6 records the same gap from the scope side |
| `OP-15` — leaver revocation has two deadlines 23 hours apart | `AUDIT-017` | §9.3 — **machine credentials are revoked immediately**; the human deadline is `SC-004`'s to reconcile |

---

## 3. Configuration

### 3.1 The three categories

| Category | Definition | Where it lives | Changes by |
|---|---|---|---|
| **Code** | Behaviour | The artefact | A release |
| **Configuration** | Values that differ by environment or that operations tunes | The configuration service, **versioned in Git** | A promoted configuration change |
| **Secret** | A value whose disclosure causes harm | **The secret store only** | Rotation |

### 3.2 The decision test

> **`PE-009-D-01`. Three questions, in order.**
>
> 1. **Does its disclosure cause harm?** → **Secret** (§6)
> 2. **Does it differ between environments, or does operations need to change it without a
>    release?** → **Configuration** (§4)
> 3. **Otherwise** → **Code**

**Worked examples**, because this is where the estate will disagree with itself:

| Value | Category | Note |
|---|---|---|
| A counterparty's API base URL | **Configuration** | Differs per environment (sandbox vs production) |
| A counterparty's API key | **Secret** | |
| A rate-limit class threshold (`IN-005` §9.2) | **Configuration** | Tuned without a release |
| The **scope vocabulary** (`IN-005` §5.5) | **Code** | It is a contract; changing it is a breaking change |
| A feature flag | **Configuration** | §5 |
| A database connection string | **Split** — host and database name are configuration; the password is a **secret** |
| A webhook signing secret (`IN-006` `SIG-08`) | **Secret** | Returned once, never retrievable |
| Log level | **Configuration** | Raisable during an incident |
| **Trace sampling rate** (`PE-008` `SM-06`) | **Configuration** | Deliberately, so it can be raised mid-incident |
| A business rule threshold | **Neither** | It is **master data or a business rule** — `RQ-009`, `MD-*`. §3.5 |

### 3.3 The boundary with `PE-003`

`PE-003` §10.3 states it; restated because it is the boundary most often crossed:

> **If changing it requires a resource to change, it is `PE-003`'s. If it can change while
> everything keeps running, it is `PE-009`'s.**

| Concern | Owner |
|---|---|
| A subnet CIDR, an instance type, a security-group rule | `PE-003` |
| A database's **existence**, size, backup schedule | `PE-003` |
| A secret's **existence and policy** | `PE-003` |
| A secret's **value** | **`PE-009`** |
| Which feature flags are on; a rate limit; an endpoint URL | **`PE-009`** |

### 3.4 Why not environment variables alone

Twelve-Factor §3 argues for configuration in the environment. **The estate departs on mechanism and
keeps the principle:**

| Problem with environment variables alone | Consequence |
|---|---|
| **Changing one requires a restart** | A log-level or sampling change during an incident becomes a deployment (`PE-008` `SM-06`) |
| **They are flat** | Twelve environments × many components produces an unmanageable matrix without a hierarchy |
| **They leak** | Into process listings, crash dumps and child processes — which is why `PE-005` `IM-04` forbids secrets in them |
| **No audit trail** | Who changed what, when, and why |

> **`PE-009-D-02`. Configuration is served from a hierarchical, versioned configuration service, and
> resolved values may be materialised as environment variables at process start.** The principle —
> configuration is not in the artefact — is preserved; the mechanism is one that supports twelve
> environments, hot reload and an audit trail.

### 3.5 What configuration is not

| # | Rule |
|---|---|
| **CF-01** | **Business rules are not configuration.** A rule has an owner, a classification and a test (`RQ-009`, `AP-006` `rule_class`). Putting it in configuration removes all three |
| **CF-02** | **Master data is not configuration.** `MD-*` registers are data with a change authority (`DA-009`) |
| **CF-03** | **Schema is not configuration.** It is a migration (`PE-004` §7) |
| **CF-04** | **Scope names, error codes and event names are not configuration.** They are contracts (`IN-005` `AM-03`, `AP-006` `CG-01`, `AR-009` `N-06`) |

> **`CF-01` is the one that will be argued.** Making a business rule configurable looks like
> flexibility. **It converts a tested, owned, classified rule into an untested value that anyone
> with configuration access can change** — and `AP-006`'s `rule_class` distinction between a hard
> block and an approved override becomes meaningless.

---

## 4. The Configuration Hierarchy

### 4.1 Precedence

Later overrides earlier. **Five layers, no more** — each adds a place to look when a value is wrong:

```
1. Component default        in the artefact; the safe fallback
2. Environment              per PE-002 environment (twelve)
3. Site                     RGN-P · RGN-S · BD-R           ← only where they must differ
4. Instance                 rare; recorded with a reason
5. Runtime override         incident use only; time-boxed and audited (§4.5)
```

### 4.2 Rules

| # | Rule |
|---|---|
| **CH-01** | **Every configuration key has a component default.** A component that cannot start without external configuration cannot start in `local` |
| **CH-02** | **Keys are declared with a type, a description and whether they are required** — an undeclared key fails `FF-177` |
| **CH-03** | **A component validates its configuration at startup and fails fast** with a clear message. Discovering a missing value at first use is discovering it in production |
| **CH-04** | **Resolved configuration is observable** — a component exposes its effective values, **with secrets redacted**, so *"which value is actually in force"* is answerable |
| **CH-05** | **Site layer is used only where a value must differ by site**, which is almost only endpoints and residency-related settings |
| **CH-06** | **Instance-layer configuration is a smell** and carries a recorded reason and a review date |

### 4.3 Promotion — `OPS-02`

> ***"Configuration is versioned and promoted through environments, never hand-edited in
> production."***

| # | Rule |
|---|---|
| **CP-01** | **Configuration lives in Git**, reviewed like code (`BE-003`) |
| **CP-02** | It **promotes along `PE-004` §9's path**, with the same environments and gates |
| **CP-03** | **A production configuration change is a change record** (`GV-003`), not a support action |
| **CP-04** | **Direct edits in production are detected and reverted** — the same drift discipline as `PE-003` §8. `FF-176` |
| **CP-05** | **Configuration and artefact are promoted together as a release** (Twelve-Factor §5) |
| **CP-06** | **A rollback rolls back configuration too** — `PE-004` §8.4's previous digest is paired with the configuration that was in force |

> **`CP-06` is the one that gets missed.** Rolling back the artefact while leaving new configuration
> in place produces a combination that has never been tested anywhere.

### 4.4 Environment identity

| # | Rule |
|---|---|
| **EI-01** | **Every environment carries an identity value** driving `PE-002` `LC-06`'s visible banner |
| **EI-02** | **A component refuses to start if its environment identity does not match the account or cluster it is running in.** `FF-178` |

> **`EI-02` prevents the specific accident twelve environments make likely**: `staging`
> configuration deployed to `prod`, or worse, `prod` configuration — including production
> counterparty endpoints — deployed to `sandbox`, which is **externally reachable** (`PE-002` §5.10).

### 4.5 Runtime overrides

| # | Rule |
|---|---|
| **RO-01** | Permitted **only** for diagnostic settings: log level, sampling rate, timeout, circuit-breaker threshold |
| **RO-02** | **Never** for business behaviour, security settings or feature flags |
| **RO-03** | **Time-boxed with a maximum of 24 hours**, then automatically reverted |
| **RO-04** | **Audited**: who, what, why, when, and when it reverted |
| **RO-05** | **Reconciled into Git within one working day** if it should persist — the same rule as `PE-003` `EM-03` |

---

## 5. Feature Flags

### 5.1 The requirement

`OPS-06`: *"Any new capability disableable without a deployment"* — implemented as `CD-135`.

### 5.2 Four kinds, with different lifetimes

> **`PE-009-D-03`. A flag declares its kind and its expiry at creation.**

| Kind | Purpose | Lifetime | Expires |
|---|---|---|---|
| **Release** | Decouple deploy from release; dark-launch a capability | **Weeks** | **Yes — removed after full rollout** |
| **Operational** | Kill-switch for a capability or an integration | **Permanent** | No — but **reviewed per wave gate** |
| **Permission** | Capability available to some audiences | Long | No — but §5.4 |
| **Experiment** | A/B or staged rollout | **Weeks** | **Yes — removed when the experiment ends** |

### 5.3 Rules

| # | Rule |
|---|---|
| **FL-01** | **Every flag declares kind, owner, creation date and expiry** (permanent kinds declare a review date) |
| **FL-02** | **Every flag has a safe default** — the behaviour if the flag service is unreachable. **A flag whose failure mode is undefined is an outage vector** |
| **FL-03** | **A release or experiment flag past its expiry fails `FF-179`** |
| **FL-04** | Flags are **evaluated server-side** (`PS-11` — no business rule client-side) |
| **FL-05** | **Flag state is observable and audited** — a behaviour change with no deployment must still be attributable |
| **FL-06** | **Nested flags are forbidden.** Two flags gating one path produce four states, of which at most one was tested |
| **FL-07** | **Every P0 integration has an operational kill-switch** — the mechanism by which `NFR-050`'s manual fallback is engaged deliberately rather than by breaker alone |
| **FL-08** | **Flag count is reported at every wave gate.** Growth without removal is the failure mode |

> **`FL-07` connects to `IN-001-D-02`.** The circuit breaker engages a fallback **automatically** on
> failure. **The kill-switch engages it deliberately** — for a planned counterparty maintenance
> window, or a suspected data-quality problem the breaker cannot detect.

### 5.4 The flag that becomes permanent

The characteristic failure: a release flag survives, and after a year nobody knows whether the false
branch still works.

| # | Rule |
|---|---|
| **FP-01** | **A release flag past expiry is removed, and the losing branch is deleted** |
| **FP-02** | **Both branches of a live flag are tested** while it exists (`QA-005`) |
| **FP-03** | **A flag surviving two wave gates is reclassified or removed** — a decision, not a drift |

---

## 6. The Secret Store

### 6.1 What is specified beyond the name

`02-05` §9 names Vault. This section specifies what "Vault-managed" must mean.

| Element | Specification |
|---|---|
| **Engines** | Key-value v2 (versioned) for static secrets; **dynamic credentials** for databases; PKI for internal mTLS (`PE-001` `CT-03`); transit for application-level encryption where `SC-006` requires |
| **Auth methods** | Workload identity for services (`PE-005`); OIDC via `M29` for humans; **short-lived tokens only** |
| **Policy model** | **Deny by default**; least privilege; **path-scoped per component and environment** |
| **HA** | **Clustered from W1** — it becomes a total-outage dependency the moment it holds a secret (`PE-001` `HA-01`) |
| **Unseal** | Split-key, escrowed per `PE-007` §4.7; **auto-unseal via a cloud KMS where available**, with the manual path rehearsed |
| **Audit device** | **Enabled from the first write**, shipped to `PE-008`'s store — §11.1 |
| **`Z4`** | **A separate instance in country**, separate key material, separate escrow — §10 |

### 6.2 Access rules

| # | Rule |
|---|---|
| **SA-01** | **A secret path is scoped to one component and one environment.** A `staging` credential path is unreadable by a `prod` identity and vice versa |
| **SA-02** | **No human has standing read access to a production secret value.** Humans manage policy; workloads read values |
| **SA-03** | **Where a human must read a production secret, it is break-glass** (§8) |
| **SA-04** | **Every read is audited**, including the identity, the path and the time |
| **SA-05** | **Dynamic credentials are preferred to static ones** wherever the backend supports them — a credential that expires in an hour cannot be exfiltrated usefully |
| **SA-06** | **A secret is never returned to a pull-request build** (`PE-004` `CR-03`) |

### 6.3 Secret classes and rotation — replacing *"rotation scheduled"*

> **`PE-009-D-04`. Every secret has a class, and every class has a cadence, a mechanism and an
> owner.**

| Class | Examples | Cadence | Mechanism | Overlap needed |
|---|---|---|---|---|
| **Dynamic database credentials** | Service → PostgreSQL | **Hourly** | Automatic, per lease | n/a |
| **Internal mTLS certificates** | Service identity | **Hours** | Automatic, PKI engine | n/a |
| **Counterparty API credentials** | bKash, Nagad, SSLCOMMERZ, SMS, Maps | **Per counterparty; ≤ 12 months** | **Manual or semi-automatic** — the counterparty's portal | **Yes** — §6.4 |
| **Webhook signing secrets** | Outbound endpoints | **≤ 12 months** (`IN-006` `SIG-12`) | Self-service rotation with **multi-signature overlap** (`SIG-07`) | **Yes** |
| **Partner API credentials** (issued by us) | Brand, corporate, seller | **≤ 12 months**, or on contract change | `IN-005` §6 self-service | Yes |
| **Pipeline identities** | CI/CD | Federated; **no long-lived credential** (`PE-004` `CR-01`) | n/a | n/a |
| **Break-glass credentials** | §8 | **Immediately after every use** | Manual | No |
| **Encryption keys** | At rest, `Z4` | **`SC-006`'s cryptoperiod** | `SC-006` | `SC-006` |
| **Vault unseal shares** | The store itself | On holder change; **≤ 24 months** | Ceremony, rehearsed (`PE-007` `SB-04`) | n/a |

| # | Rule |
|---|---|
| **RT-01** | **Every secret has an expiry**, and expiry is alerted at **30 and 7 days** (Technology Stack §18.4, `IN-001` `OB-06`) |
| **RT-02** | **A rotation that requires an outage is a design defect**, not a maintenance window |
| **RT-03** | **Rotation is rehearsed in a non-production environment first** |
| **RT-04** | **A secret past expiry fails `FF-180`** |

### 6.4 Rotation with a counterparty in the loop

The hardest case, and the one that produces outages:

| # | Rule |
|---|---|
| **CR-01** | **An overlap window is required**: both the old and new credentials valid simultaneously |
| **CR-02** | **Where a counterparty does not support overlap, the rotation is a planned change** in the `NFR-049` window, with the counterparty notified |
| **CR-03** | **Nagad's RSA key rotation requires a portal upload** (`IN-004` §5.2, `IN-A-14`) — **an out-of-band manual step**, and the overlap behaviour must be agreed with Nagad **before** the first rotation, not at it |
| **CR-04** | Every counterparty's rotation procedure and overlap behaviour is recorded in **its ICD** (`IN-004` §2.4 section 5) |

> **`CR-03` is a live gap.** `IN-A-14` records that Nagad's rotation is *"the hardest rotation in the
> estate"* and that overlap must be agreed in advance. **Twelve months after the first credential is
> issued, that agreement either exists or the rotation is an outage.**

---

## 7. Injection

### 7.1 The principle

> **`PE-009-D-05`. A secret reaches a process at runtime, from the store, scoped to that process, and
> is never written to durable storage on the way.**

### 7.2 Per surface

| Surface | Mechanism | Rules |
|---|---|---|
| **Containers** | Store-backed injection at start; **memory-backed volume or in-process client** | Never a plain Kubernetes Secret alone (`PE-005` `CS-07`); never an environment variable for a high-value secret (§7.3) |
| **Pipelines** | **Per-job, from the store**, short-lived (`PE-004` `CR-02`, `TAF-56`) | Never in pipeline configuration; **never available to a fork build** |
| **IaC** | **By vault path reference**, injected at apply (`PE-003` `SI-02`) | Never in source; the `SI-04` exception is quarantined |
| **`Z6` egress proxy** | **Injected at the proxy** (`IN-001` `EG-05`) | The application node never holds a counterparty credential longer than the call |
| **Humans** | **Break-glass only** (§8) | |

### 7.3 Environment variables

| # | Rule |
|---|---|
| **EV-01** | Environment variables are acceptable for **low-sensitivity** secrets where the platform provides no better mechanism |
| **EV-02** | **Not acceptable** for counterparty credentials, signing keys or database passwords where a better mechanism exists |
| **EV-03** | **Never** materialised into an image layer or a build argument (`PE-005` `IM-04`) |
| **EV-04** | **Crash dumps and error reporters are configured to exclude the environment** — the commonest accidental disclosure of an environment-variable secret |

### 7.4 Application obligations

| # | Rule |
|---|---|
| **AP-01** | **Read the secret at use, or hold it in memory only** — never write it to disk, a log or a cache |
| **AP-02** | **Handle rotation without a restart** where the mechanism supports it |
| **AP-03** | **Never include a secret in an error message, a trace attribute or a metric label** (`PE-008` `LG-02`) |
| **AP-04** | **Fail closed** if a required secret is unavailable. A component that starts without its credentials and fails later is harder to diagnose than one that refuses to start |

---

## 8. Break-Glass — Closing `OP-08`

### 8.1 What `OP-08` found

> *"Break-glass access is documented and does not exist."*

**This matters more than it sounds**, because the estate's entire access model depends on it.
`PE-001` `MA-01` states **no standing administrative access**; `PE-003` `CP-07` states **no human
holds standing apply credentials for `prod`**; `SA-02` states **no human has standing read access to
a production secret**.

> **`PE-009-F-01`. Three documents forbid standing access on the assumption that an emergency path
> exists. `OP-08` records that it does not. Without break-glass, either the "no standing access"
> rules are unenforceable in an incident, or they are quietly ignored — and the second is what
> actually happens.**

### 8.2 The procedure

| # | Step | Control |
|---|---|---|
| **1** | **Trigger** — an incident requiring access no standing credential provides | The incident is declared (`SV-*`); break-glass is not used for convenience |
| **2** | **Request** — the requester names the incident, the access needed and why | Recorded before access, not after |
| **3** | **Authorise** — a **second named person** approves | §8.3. **The requester never self-approves** |
| **4** | **Issue** — a **time-boxed, scoped** credential from the store | **Maximum 4 hours**, scoped to the least access that resolves the incident |
| **5** | **Announce** — automatic notification to the CTO, the Security Lead and the on-call channel **at issue**, not afterwards | **A silent break-glass is an unauthorised access with paperwork** |
| **6** | **Record** — the session is recorded (`NFR-070`) | `PE-001` `MA-03` |
| **7** | **Expire** — the credential expires automatically. **No extension; a new request instead** | |
| **8** | **Rotate** — every secret the credential could read is **rotated immediately after** | `RT-01`'s class cadences are superseded by use |
| **9** | **Review** — a mandatory post-incident review within **five working days** | `OP-016`; **`FF-183`** |

### 8.3 Authority

| # | Rule |
|---|---|
| **BG-01** | **At least three people hold break-glass authority**, so two are reachable at any hour |
| **BG-02** | **Two-person rule**: requester and approver are different people. **Always** |
| **BG-03** | **The CTO and the Security Lead are notified at issue**, and neither can be the sole approver of their own request |
| **BG-04** | Holders are **named individuals**, not roles, and the list is reviewed at every wave gate |
| **BG-05** | **`Z4` break-glass is separately authorised** and requires an approver from the DPO or Security Lead (`PE-003` `RS-04` parity) — §10.3 |
| **BG-06** | **`BKP-3` restore credentials are break-glass** (`PE-007` `IM-04`) |

### 8.4 The failure mode this design guards against

| # | Rule |
|---|---|
| **BF-01** | **Break-glass must not depend on the system being available.** If the identity provider is down, break-glass that authenticates through it is unusable |
| **BF-02** | A **fully offline path** exists: sealed credentials, physically held, with the out-of-band record (`PE-007` §9.3) |
| **BF-03** | The offline path is **rehearsed annually**, with the actual holders |
| **BF-04** | **Using the offline path invalidates those credentials**; they are regenerated and re-sealed afterwards |

> **`BF-01` is the reason `OP-08` matters at 02:00.** An estate with no standing access, whose
> emergency access depends on the identity provider, has **no access at all** when the identity
> provider is the outage — and `PE-001` §9.2 records Keycloak as *"a total-outage dependency."*

### 8.5 Frequency as a signal

| # | Rule |
|---|---|
| **BS-01** | **Break-glass use is counted and reported at every wave gate** |
| **BS-02** | **Repeated use for the same cause is a process defect**, not an emergency — the access model or the automation is wrong |
| **BS-03** | **Zero uses over a long period is also a signal** — it may mean the path is untested. `BF-03`'s annual rehearsal ensures it is exercised regardless |

---

## 9. Boundaries

### 9.1 With `SC-006` — cryptography

| Concern | Owner |
|---|---|
| Algorithms, key lengths, cryptoperiods, ceremonies | **`SC-006`** |
| Where keys are stored, how they are delivered, who may retrieve them | **`PE-009`** |
| **`Z4` key custody in country** | **Both** — `SC-006` `ES-3` requires it; §10 implements it |

### 9.2 With `SC-004` — identity

| Concern | Owner |
|---|---|
| Human identity, authentication, MFA, the 38 access profiles | **`SC-004`**, `05-04` |
| Workload identity and its authentication to the secret store | **`PE-009`** |
| **Break-glass** | **`PE-009`** designs it; **`SC-004`** provides the human identities it authenticates |

> **`PE-009-F-02`. §8's break-glass depends on `SC-004`'s human identity model, and `OP-10` records
> that the 38 access profiles do not exist and the register they check against is ambiguous.**
> `IN-005` §5.6 found the same gap from the scope side — R39–R46 unregistered, R60 duplicating R32,
> R54/R57 undefined. **Break-glass can be designed against an identity model that does not exist; it
> cannot be *implemented* against one.** `Q-03`.

### 9.3 Leavers

`OP-15` records that leaver revocation has **two deadlines, 23 hours apart**.

| # | Rule |
|---|---|
| **LV-01** | **Machine credentials associated with a leaver are revoked immediately** on the leaver event (`employee.left`) |
| **LV-02** | **Break-glass authority is revoked immediately**, and if the leaver held an unseal share, **the shares are regenerated** |
| **LV-03** | **The human access deadline is `SC-004`'s to reconcile** — this document does not adopt either of the two conflicting deadlines |
| **LV-04** | **A leaver who held any secret with a manual rotation path triggers that rotation** |

> **`LV-02` is the one that gets forgotten.** Revoking a leaver's account does nothing about an
> unseal share they hold, and `PE-007` `SB-02` splits those shares among named holders.

---

## 10. `Z4` — Separation in Country

### 10.1 Why secrets are a residency question

`Z4`'s data may not leave Bangladesh (`SC-007-DR-1`). **A key that decrypts `Z4` is not `Z4` data —
but a key held regionally that decrypts in-country data defeats the boundary in every practical
sense.**

### 10.2 Rules

| # | Rule |
|---|---|
| **ZS-01** | **A separate secret-store instance runs in `BD-R`** (§6.1) |
| **ZS-02** | **`Z4` key material never leaves Bangladesh** (`SC-006` `ES-3`, `PE-007` `SB-03`) |
| **ZS-03** | **Unseal shares for the `BD-R` instance are held in country**, by in-country holders |
| **ZS-04** | **Regional secret-store access grants nothing in `BD-R`** (`PE-001` `MA-04`) |
| **ZS-05** | **`CD-233` is the only workload with a `Z4` credential** (`PE-005` `RP-02`) |
| **ZS-06** | **`Z4` audit logs stay in country** (`PE-008` `RB-02`, `AC-02`) |

### 10.3 `Z4` break-glass

| # | Rule |
|---|---|
| **ZB-01** | **Separately authorised**, with an approver from the DPO or Security Lead (`BG-05`) |
| **ZB-02** | **The offline path is held in country** |
| **ZB-03** | **Every `Z4` break-glass use is a `SC-008` reportable event**, because it is privileged access to residency-classified data |
| **ZB-04** | The post-incident review includes the **DPO** |

---

## 11. Audit, Detection and Response

### 11.1 The trail

| Recorded | Where | Retention |
|---|---|---|
| Every secret read — identity, path, time | Vault audit device → `PE-008` | Per `SC-008` |
| Every secret write and rotation | As above | Per `SC-008` |
| Every policy change | As above | Per `SC-008` |
| **Every break-glass issue, use and expiry** | As above **plus** the incident record | **Per `SC-008`; never purged early** |
| Every configuration change | Git history + the change record | Indefinite |
| Every runtime override | Configuration service audit | 1 year |
| **Every `Z4` secret access** | **In country** (`ZS-06`) | Per `SC-008` |

### 11.2 Detection

| # | Rule |
|---|---|
| **DT-01** | **Secret scanning pre-commit and in CI** (`PE-003` `SI-06`, `SC-005` `G-01`). Pre-commit alone is bypassable |
| **DT-02** | **The repository history is scanned**, not only the working tree — a secret removed in a later commit is still in history |
| **DT-03** | **Log and trace stores are sampled for secret patterns** (`PE-008` `FF-170`) |
| **DT-04** | **Container images are scanned for secrets in layers and history** (`PE-005` §3.6) |
| **DT-05** | **Anomalous secret access alerts** — unusual volume, unusual hour, unusual path for that identity |

### 11.3 Response to exposure

> **`PE-009-D-06`. An exposed secret is rotated first and investigated second.**

| # | Step |
|---|---|
| **1** | **Rotate immediately.** Every minute of investigation is a minute the credential is valid |
| **2** | **Revoke the old value** where the mechanism permits |
| **3** | **Assess the exposure window** — how long, who could have seen it |
| **4** | **Search for use** — the audit trail and counterparty logs |
| **5** | **Notify** — Security Lead always; the counterparty if theirs; `SC-008`'s assessment if personal data could have been reached |
| **6** | **Post-incident review**, including how it escaped `DT-01`…`DT-04` |
| **7** | **Purge from history** where feasible, **and treat the secret as compromised regardless** — a rewritten history does not un-clone a repository |

---

## 12. Fitness Functions

Allocation confirmed by enumerating every `FF-nn` definition across all authored categories at
**2026-08-19 01:45 (+06)**, per `PGD-AUDIT-007` `PGD-A7-01`.

| # | Check | Scope | Timing | Enforcement |
|---|---|---|---|---|
| **FF-175** | **No secret value appears in source, configuration, image layer, log, trace or IaC plan** | All | Pre-commit + CI + daily scan | **Fail** |
| **FF-176** | **No production configuration differs from the promoted, versioned value** (`OPS-02`) | 12 environments | Daily | **Fail** |
| **FF-177** | Every configuration key a component reads is **declared with a type and a description** | All | CI | **Fail** |
| **FF-178** | **A component's environment identity matches the account and cluster it runs in** | All | Startup + runtime | **Fail — refuses to start** |
| **FF-179** | **No release or experiment flag is past its expiry** | All flags | Weekly | **Fail** |
| **FF-180** | **No secret is past its rotation cadence**, and expiry alerting fired at 30 and 7 days | All secrets | Daily | **Fail** |
| **FF-181** | **No human identity holds standing read access to a production secret value** (`SA-02`) | All policies | Weekly | **Fail** |
| **FF-182** | **Every break-glass issue has a request, a distinct approver, a notification and a recorded session** | Per event | Per event | **Fail** |
| **FF-183** | **Every break-glass use has a post-incident review within five working days** | Per event | Weekly | **Fail** |
| **FF-184** | **`Z4` secret material and audit logs exist only in country** | `BD-R` | Daily | **Fail** |

---

## 13. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `PE-009-D-01` | Classifying a value | Case by case · **three ordered questions** | **The test** | *"Is it config or a secret?"* must be answerable by a developer without a meeting | §3.2; worked examples including the ones the estate will dispute |
| `PE-009-D-02` | Configuration mechanism | Environment variables only · **hierarchical service, materialised as needed** | **Service** | Twelve environments, hot reload for incident settings, and an audit trail | §3.4, §4.1 — five layers |
| `PE-009-D-03` | Feature flags | Untyped, permanent · **four kinds with declared expiry** | **Four kinds** | The failure mode is accumulation; a flag with no expiry never has one applied later | `FL-01`…`FL-08`; `FF-179` |
| `PE-009-D-04` | Rotation | *"Rotation scheduled"* · **class, cadence, mechanism and owner per secret** | **Per class** | Eleven words is not a standard, and the hard cases are the counterparty ones | §6.3, §6.4; `FF-180` |
| `PE-009-D-05` | Injection | Baked · environment variables · **runtime from the store, scoped, never durable** | **Runtime from the store** | A secret written to durable storage is a secret in a backup, an image and a crash dump | §7; `PE-005` `CS-07` |
| `PE-009-D-06` | Exposure response | Investigate then rotate · **rotate then investigate** | **Rotate first** | Every minute of investigation is a minute the credential is valid | §11.3 |
| `PE-009-D-07` | Break-glass authentication | Through the identity provider · **plus a fully offline path** | **Both** | Keycloak is *"a total-outage dependency"*; break-glass that depends on it is unusable in the outage it exists for | `BF-01`…`BF-04` |
| `PE-009-D-08` | Business rules in configuration | Configurable for flexibility · **never** | **Never** | It converts a tested, owned, classified rule into an untested value, and voids `AP-006`'s `rule_class` distinction | `CF-01` |

---

## 14. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| **Q-01** | **Who holds break-glass authority?** `BG-01` requires at least three named individuals; **none is named anywhere** (`OP-08`) | **CTO + Security Lead** | **W1 — blocking** | Every "no standing access" rule in `PE-001`, `PE-003` and this document |
| **Q-02** | **Is the offline break-glass path built and held?** (`BF-02`, `PE-007` §9.3) | CTO + Head of Service | **W1** | Recovery when the identity provider is the outage |
| **Q-03** | **When do the 38 access profiles exist?** Break-glass can be designed against an absent identity model; it cannot be implemented against one (`OP-10`, `PE-009-F-02`) | `SC-004` owner + CTO | **W1** | §8's implementation |
| **Q-04** | **Which configuration service?** §4's hierarchy is mechanism-independent; hot reload, audit and Git-backing are not | Platform Engineering Lead | **W1** | §4, `FF-176` |
| **Q-05** | **Has Nagad's key-rotation overlap been agreed?** (`CR-03`, `IN-A-14`) Twelve months after issue it is either agreed or it is an outage | Integration Architect + Treasury | **W3** | `INT-002` rotation |
| **Q-06** | Who are the **in-country unseal-share holders** for the `BD-R` instance? (`ZS-03`) | CTO + DPO | **W1** | `Z4` recovery, `PE-007` `SB-05` |
| Q-07 | Does the estate accept **dynamic database credentials** (`SA-05`), given Odoo's connection model and the §5.5 pooler? | Chief Architect + Platform | W1 | §6.3, `PE-006` §5.5 |

---

## 15. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | Configuration, code and secret are distinguished by a **test a developer can apply** | §3.2 |
| AC-02 | The boundary with `PE-003` is restated in one sentence | §3.3 |
| AC-03 | The hierarchy has **five layers with precedence**, and every layer has a rule | §4.1, §4.2 |
| AC-04 | `OPS-02` is mechanical, **including on rollback** | §4.3, `CP-06`; `FF-176` |
| AC-05 | Feature flags declare **kind and expiry**, and the accumulation failure mode is addressed | §5.2, §5.4 |
| AC-06 | *"Rotation scheduled"* is replaced by **class, cadence, mechanism and owner** | §6.3 |
| AC-07 | The **counterparty rotation case** is specified, including the one that is a live gap | §6.4, `CR-03` |
| AC-08 | Injection is specified **per surface** | §7.2 |
| AC-09 | **`OP-08`'s break-glass is designed** — nine steps, two-person rule, notification at issue, mandatory rotation and review | §8.2, §8.3 |
| AC-10 | **Break-glass works when the identity provider is the outage** | `BF-01`…`BF-04`, `PE-009-D-07` |
| AC-11 | `Z4` secret separation is specified, including its own break-glass | §10 |
| AC-12 | Exposure response **rotates first** | §11.3, `PE-009-D-06` |

**Definition of done.** Complete when every criterion is met, **Q-01…Q-04 are answered**, the secret
store is clustered and audited, break-glass is **implemented and rehearsed**, `FF-175`…`FF-184` are
enabled, and `PGD-000`'s `PE-009` row carries a fresh enumeration timestamp. **`OP-08` closes on
implementation and the first rehearsal — not on issue of this document**, and its rota and
access-profile halves belong to `SV-*` and `SC-004`.

---

## 16. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | **`PE-002`** | Twelve environments — the configuration hierarchy's second layer |
| Upstream | **`PE-003`** §9, §10.3 | `SI-01`…`SI-06`; the boundary test |
| Upstream | **`PE-005`** `CS-07` | Runtime secret mounting |
| Upstream | **`SC-004`**, **`SC-006`** | Identity for break-glass; cryptography and key custody |
| Downstream | **`PE-004`** §11.2 | Per-job injection; `TAF-56` |
| Downstream | **`PE-007`** §4.7 | Snapshot and **unseal-key escrow** |
| Downstream | **`PE-008`** | The audit device ships to its store; `LG-02` forbids secrets in logs |
| Downstream | **`IN-001`** `EG-05` | Credential injection at the `Z6` proxy |
| Downstream | `IN-005` §6, `IN-006` §7 | Partner credential and webhook-secret rotation |
| Downstream | `SV-*`, `OP-013` | Break-glass sits inside incident response |
| Downstream | `SC-008` | `ZB-03`'s reportable events |
| Lateral | `../../project_content/_AUDIT/AUDIT-017_*.md` | **`OP-08`, `OP-10`, `OP-15`** |
| Lateral | `../../1000fix_ERP_Module/02_Architecture/02-05_*.md` §9 | The eleven words this document replaces |

---

## 17. References

**Within this repository**
[`../PGD-000_Master_Register_of_Project_Guiding_Documents.md`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md) ·
[`./_CATEGORY_OVERVIEW.md`](./_CATEGORY_OVERVIEW.md) ·
[`./PE-002_Environment_Strategy_and_Specification.md`](./PE-002_Environment_Strategy_and_Specification.md) ·
[`./PE-003_Infrastructure_as_Code_Standard.md`](./PE-003_Infrastructure_as_Code_Standard.md) ·
[`./PE-004_CI_CD_Pipeline_Design_Specification.md`](./PE-004_CI_CD_Pipeline_Design_Specification.md) ·
[`./PE-005_Containerisation_and_Orchestration_Design.md`](./PE-005_Containerisation_and_Orchestration_Design.md) ·
[`./PE-007_Backup_Disaster_Recovery_and_Business_Continuity_Design.md`](./PE-007_Backup_Disaster_Recovery_and_Business_Continuity_Design.md) ·
[`./PE-008_Observability_and_Monitoring_Design.md`](./PE-008_Observability_and_Monitoring_Design.md) ·
[`../04_Integration_and_API_Engineering/IN-006_Webhook_Callback_and_Partner_Push_Specification.md`](../04_Integration_and_API_Engineering/IN-006_Webhook_Callback_and_Partner_Push_Specification.md)

**Workspace**
`../../project_content/_AUDIT/AUDIT-017_*.md` `OP-08`, `OP-10`, `OP-15` ·
`../../1000fix_ERP_Module/02_Architecture/02-05_*.md` §9 ·
`../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §18.4 ·
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_*.md`

**External sources**

| Source | Verified |
|---|---|
| Twelve-Factor App §3, §5 — config, and build/release/run | 2026-08-19 |
| NIST SP 800-57 — key management lifecycle and cryptoperiods | 2026-08-19 |
| NIST SP 800-63B — authenticator lifecycle | 2026-08-19 |
| OWASP Secrets Management Cheat Sheet | 2026-08-19 |
| CIS Controls v8 — controls 5, 6, 16 | 2026-08-19 |
| ISO/IEC 27001:2022 Annex A.5.15–A.5.18, A.8.24 | 2026-08-19 |

---

## 18. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-19 | Platform Engineering | Initial issue, replacing `02-05` §9's eleven words. **Designs the break-glass procedure `OP-08` records as absent** — nine steps, a two-person rule, notification at issue, mandatory post-use rotation and review — and records that **three documents forbid standing access on the assumption it exists** (`PE-009-F-01`). Specifies a **fully offline break-glass path**, because Keycloak is a total-outage dependency and break-glass that authenticates through it is unusable in the outage it exists for (`PE-009-D-07`). Replaces *"rotation scheduled"* with **class, cadence, mechanism and owner**, and names the live counterparty gap (`CR-03`). Establishes a five-layer configuration hierarchy with environment-identity enforcement, a four-kind feature-flag model with declared expiry, and records that break-glass **cannot be implemented** until `SC-004`'s access profiles exist (`PE-009-F-02`) | *Pending — CTO, Security Lead; `GV-002` not constituted* |

---

*`PE-009` · Category 10 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
