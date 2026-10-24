---
id: QA-007
title: Security Test Plan
category: 08 — Quality Engineering & Test
code: QA
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Security Lead with the QA Lead
approver: Chief Information Security Officer with the Chief Technology Officer
standards_basis: >
  OWASP ASVS 5.0.0 (30 May 2025) · OWASP Testing Guide · ISO/IEC 27001:2022 A.8.29 (security testing
  in development and acceptance) · ISO/IEC/IEEE 29119-3:2021 §8 · NIST SP 800-115 · STRIDE
traces_to: >
  PGD-000 QA-007 · SC-002 (97 threats, 32 abuse cases) · SC-004 (38 roles, 67 access profiles) ·
  SC-005 §5 (gates G-01…G-14) · SC-009 (§6 pen test, §7 wave schedule) ·
  05-04 §2 (456 cells, 77 granted, 379 denied) · §10 criterion 6 · 06-02 G1-06, G1-07, G1-09 ·
  GV-009 SG-1 · AUDIT-014 TS-05 (TS-017 100% blocked on 38 absent accounts)
depends_on: SC-002 (threat basis) · SC-004 (roles) · QA-003 (derivation) · QA-004 §9 (role accounts) · QA-005 §12.2 (harness)
verified_on: 2026-08-18
enumeration_timestamp: 2026-08-18 22:01 (+06)
priority: P0
needed_by: W1
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# QA-007 — Security Test Plan

### Category 08 · Code `QA` · OWASP ASVS 5.0.0 · ISO/IEC 27001:2022 A.8.29 · STRIDE

---

> **Before writing, read this.**
>
> 1. **`PG-01` Register-first.** Row `QA-007` exists in `PGD-000` Category 08, status ◐ `P0` `W2`.
>    **Issued at `Now`** — `G1-09` consumes it at Month 4; see §1.3.
> 2. **`PG-03` Count, do not consult.** Threat, abuse-case, role and matrix figures counted at
>    **2026-08-18 22:01 (+06)** from `SC-002`, `SC-004` and `05-04`.
> 3. **`PG-06` Cite standards.** §2.1. **`_CATEGORY_OVERVIEW.md` cites "OWASP ASVS 4"; 4.0.3 is
>    superseded by 5.0.0 (30 May 2025)** — corrected, as `SC-005` §2.1 already corrected it.
> 4. **`PG-M4` Verify citations.** ASVS 5.0.0 verified 2026-08-18.

---

## 1. Purpose

`PGD-000` records the problem exactly: *"`TS-017` is a security/privacy case pack that audit **TS**
says **cannot be executed — no role accounts exist**. Testing derived from a threat model that does
not exist (`SC-002`) is testing against assumptions."*

**Both halves of that have now changed.** `SC-002` was issued and holds **97 threats and 32 abuse
cases**. `QA-004` §9 specifies the **38 role accounts** as a dataset with an owner. This document is
the plan that turns those two into executed, evidenced security testing — and it draws the boundary
with `SC-005` and `SC-009` so that three documents do not each claim the same activity.

> **The dominant risk class in this estate is not injection or misconfiguration. It is
> authorisation.** `05-04` §2's matrix has **456 `role × portal` cells: 77 granted and 379 denied**,
> and `05-04` §10 criterion 6 makes negative testing a **condition of releasing a role**. `SC-009`
> reaches the same conclusion independently and schedules **authorisation and isolation** as the
> first penetration test at W1 rather than a general engagement, because *"a record-rule defect found
> after go-live is fixed across live data."*
>
> **A denial that holds in the UI and not through the API is an automatic `S1`** (`TS-018`), and it
> produces no error, no alert and no complaint until an outsider notices.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | **The boundary** — what this plan owns against `SC-005`, `SC-009` and `QA-005` (§3) |
| 2 | **Derivation from the threat model** — 97 threats and 32 abuse cases into cases (§4) |
| 3 | **The authorisation suite** — the 379 denials, and why it is a harness and not 379 scripts (§5) |
| 4 | **Data-scope, residency and consent testing** (§6) |
| 5 | **Audit-log completeness testing** (§7) |
| 6 | **ASVS 5.0.0 verification** — which level applies where (§8) |
| 7 | **Pipeline security testing** — what QA does with `SC-005`'s gate output (§9) |
| 8 | **Penetration-test coordination** — QA's role, which is not to test (§10) |
| 9 | **The wave schedule and gate evidence** (§11) |
| 10 | **The volume problem** — ~734 derived cases against the QA budget, and how it is closed (§12) |

**Explicitly out of scope**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| The threat model itself | `SC-002` | Consumed as the test basis. `RC-4`: a finding with no matching threat **adds** a threat there |
| SAST, DAST, SCA, secret scanning, gates `G-01`…`G-14` | `SC-005` §5 | **Already specified with fail conditions, owners and override paths.** §9 states what QA does with the output |
| Vulnerability severity model, remediation SLAs, patch windows | `SC-009` §3–§5 | Consumed |
| **Penetration testing** — scope, rules of engagement, tester independence, schedule | `SC-009` §6, §7 | §10 covers **coordination only**. QA does not conduct it and does not scope it |
| Incident response | `SC-011` | |
| Identity and authorisation **design** | `SC-004` | This plan verifies the design; it does not set it |
| Cryptography and key management | `SC-006` | |
| Residency **design** | `SC-007` | Verified here, designed there |
| Test data and role-account **provisioning** | `QA-004` §9 | Consumed as a precondition |
| The negative-authorisation **harness code** | `QA-005` §12.2 | Built there, specified here |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| **Security Lead** | The plan they own, and the boundary with `SC-005` and `SC-009` |
| **QA engineers** | §5, §6, §7 — the suites they run and what each proves |
| CISO and Audit Committee | §11 — the gate evidence, and `SG-1`'s independence requirement |
| Developers | §5.4, §8 — what a denial must do, and the ASVS level applying to their component |
| Penetration testers | §10 — how their findings enter the estate's registers |
| Data Protection Officer | §6 — consent, scope and residency verification |

### 1.3 Why this is issued at `Now` and not `W2`

`PGD-000` registers `QA-007` at `W2`. **`G1-06`, `G1-07` and `G1-09` are Month 4 criteria** and all
three are evidenced by security testing; `G1-09` is *"zero critical or high security findings"*.
Under `QA-001` `MTS-R6` the plan is due `Now`. This is the guiding-register instance of
`AUDIT-014` `TS-02`, and it is recorded with `QAA-10`.

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Edition, verified 2026-08-18 | Conformance | Departure |
|---|---|---|---|
| **OWASP ASVS** | **5.0.0, 30 May 2025** — ~350 requirements across 17 chapters, up from 286 in 14 | §8 binds a verification level per surface class | **`_CATEGORY_OVERVIEW.md` cites "ASVS 4"**; 4.0.3 is superseded. Corrected here, consistent with `SC-005` §2.1's correction |
| **OWASP Testing Guide** | current | §4, §5 technique selection | None |
| **ISO/IEC 27001:2022 A.8.29** | 2022 | *Security testing in development and acceptance* — this plan is the acceptance half; `SC-005` is the development half | None |
| **ISO/IEC/IEEE 29119-3:2021** | 2021, 2nd ed. | A level plan under `QA-002` `LP-6`; §8 elements not restated are inherited | None |
| **NIST SP 800-115** | current | Referenced by `SC-009` for pen-test method; not re-specified | Delegated |
| **STRIDE** | — | The threat taxonomy `SC-002` used and this plan derives from | None |
| **OWASP Top 10:2025** | 2025 | `SC-002` §7 maps its coverage; §4.4 uses it as a completeness cross-check | None |

### 2.2 Source material relied on

| Source | What it establishes |
|---|---|
| `SC-002` §6 | **97 threats** across the six STRIDE classes plus a business-surface class, `TH-001`…`TH-097`, with **eleven rated Critical** |
| `SC-002` §8 | **32 abuse cases**, `AB-01`…`AB-32`, split marketplace/external and insider/privilege |
| `SC-002` §9.3, §12 | **4 untreated threat classes and 3 attack trees — the pen-test priority list** |
| `SC-004` | **38 roles**; **67 access profiles**, whose negative tests are `SC-005` gate `G-09` |
| `05-04` §2 | **456 portal-matrix cells: 77 granted, 379 denied** — enumerated exactly by `AUDIT-014` `X8` |
| `05-04` §10 criterion 6 | **Negative testing is a condition of releasing a role** |
| `SC-005` §5 | Gates `G-00`…`G-14` with fail conditions; `G-08` binds ASVS **L2 estate-wide, L3 for `Z4`-touching and payment paths** |
| `SC-009` §6, §7 | Pen-test types `PT-A`…`PT-I`, the wave schedule, independence rules `IN-1`…`IN-5`, closure rules `RC-1`…`RC-6` |
| `SC-007`, `DA-005` | Residency classes and the permitted-store rules `NFR-086c` verifies |
| `SC-010` | The audit-log specification §7 tests against |
| `TS-017` | The security and privacy case pack — ~734 derived cases, 19 identified |
| `AUDIT-014` `TS-05` | **`TS-017` is 100% blocked on 38 accounts that do not exist**, recorded independently by six files |
| `GV-009` `SG-1` | Standing criterion, every gate: **zero open critical or high findings**, evidence `E5` + `E6` |

### 2.3 What this document closes

| Finding | Source | How | Residual |
|---|---|---|---|
| `TS-05` | `AUDIT-014` | The test-side half: §5 specifies the suite, §5.2 makes the accounts a stated precondition with an assertion before use, and §12 makes the volume affordable. **`QA-004` §9 specifies the accounts themselves** | Provisioning is `M29` work — `Q-01` |
| `QA-007` register row ◐ | `PGD-000` | *"Testing derived from a threat model that does not exist is testing against assumptions"* — `SC-002` now exists and §4 derives from it | — |
| `SC-002` §9.3 untreated classes | `SC-002` | §4.5 routes them: four untreated classes become pen-test priorities under `SC-009`, and their abuse cases are still written so the gap is measured | `SC-009` scope |
| `G1-09` unevidenced | `06-02` | §11 defines the evidence, including the `E6` independent opinion `SG-1` requires | Independent reviewer — `Q-04` |

---

## 3. The Boundary

Three documents touch security testing. **Overlapping claims are the defect that produced five
identifier collisions in this repository**, so the split is stated before anything else.

| Activity | Owner | This plan's part |
|---|---|---|
| SAST, SCA, secret scanning, IaC policy, licence — gates `G-01`…`G-07` | **`SC-005` §5** | **None.** QA consumes the output as gate evidence (§9) |
| DAST, ASVS verification, abuse-case tests, profile negative tests — `G-08`…`G-10` | **`SC-005` §5 defines the gate; `QA-007` supplies the cases** | §4, §5, §8 |
| Vulnerability severity, SLAs, patching, exceptions | **`SC-009` §3–§5** | **None.** Consumed |
| Penetration testing — scope, RoE, independence, schedule | **`SC-009` §6, §7** | **Coordination only** (§10) |
| The threat model and abuse-case register | **`SC-002`** | Consumed as the test basis; §4 derives |
| Identity and authorisation design | **`SC-004`** | Verified, not designed |
| **The 379-denial authorisation suite** | **`QA-007`** | **Owned here** — §5 |
| **Data-scope, residency and consent verification** | **`QA-007`** | **Owned here** — §6 |
| **Audit-log completeness verification** | **`QA-007`** | **Owned here** — §7 |
| The harness code | `QA-005` §12.2 | Specified here, built there |

> **`STP-01`.** Where this plan and `SC-005` or `SC-009` appear to conflict, **the security document
> governs the control and this plan governs the test.** A control is not weakened by a test plan.

---

## 4. Derivation From the Threat Model

### 4.1 The rule

> **`STP-02`.** Every security case traces to a **`SC-002` threat identifier or abuse-case
> identifier**, and every threat rated High or Critical has at least one case. A threat with no case
> is visible in `QA-011`'s report as a coverage gap, not invisible.

This is the difference between the `TS-017` position and this one. `TS-017` derived ~734 cases by set
arithmetic over `05-04` — which is correct and necessary — but set arithmetic over an access matrix
does not cover spoofing, repudiation, denial of service or business-surface abuse. **The threat model
does.**

### 4.2 Cases per threat class

| STRIDE class | Threats | Case type | Level | Automated |
|---|---:|---|:--:|:--:|
| **Spoofing** `TH-001`…`TH-014` | 14 | Authentication bypass, session fixation, token replay, credential stuffing, OTP abuse | L9, L3 | Mostly |
| **Tampering** `TH-015`…`TH-040` | 25 | Parameter and payload tampering, mass assignment, integrity of statutory outputs, event tampering | L9, L3 | Yes |
| **Repudiation** `TH-041`…`TH-046` | 6 | **Audit-log completeness and immutability** — §7 | L9 | Yes |
| **Information disclosure** `TH-047`…`TH-062` | 16 | **Scope, residency, field-level exposure, error leakage, enumeration** — §5, §6 | L9 | Yes |
| **Denial of service** `TH-063`…`TH-074` | 12 | Rate-limit verification, resource exhaustion, expensive-query abuse | L9 + L8 | Partly — §4.3 |
| **Elevation of privilege** `TH-075`…`TH-083` | 9 | **Horizontal and vertical escalation, SoD bypass** — §5 | L9 | Yes |
| **Business-surface and privacy** `TH-084`…`TH-097` | 14 | Marketplace abuse, payout redirection, consent bypass, **re-identification (`TH-092`)** | L9 + L7 | Partly |
| **Total** | **97** | | | |

### 4.3 The class that is shared with `QA-006`

Denial-of-service threats `TH-063`…`TH-074` are verified in two halves, and neither alone is
sufficient:

| Half | Proves | Where |
|---|---|---|
| **Control present** | The rate limit exists, is configured, returns the declared error code, and cannot be bypassed by header, path or origin variation | **Here** — L9, automated |
| **Control effective under load** | The limit holds at 1.5× peak, and the resource it protects does not exhaust before it triggers | **`QA-006`** `WP-4`, `WP-8` |

> **`STP-03`.** A rate limit verified only at a single-user level has been verified to exist, not to
> work. The `WP-8` breakpoint run is where an expensive-query abuse threat becomes measurable.

### 4.4 Abuse cases

`SC-002` §8 registers **32 abuse cases**: `AB-01`…`AB-08` marketplace and external party,
`AB-09`…`AB-16` insider and privilege, and the remainder across the other surfaces.

| # | Rule |
|---|---|
| `STP-04` | **Every abuse case has at least one executable test**, typed `abuse` in the case repository (`TDS-31`) |
| `STP-05` | **An abuse case is written from the attacker's goal, not the system's function.** *"A seller redirects another seller's payout"* — not *"payout validation works"* |
| `STP-06` | **Abuse cases are `RC-A`** by definition and are never sampled (`QA-001` §5.3) |
| `STP-07` | **The insider set `AB-09`…`AB-16` runs with a real role account, not an administrator.** An insider abuse case executed as admin proves nothing about the insider |
| `STP-08` | **Coverage is cross-checked against OWASP Top 10:2025** using `SC-002` §7's mapping — a completeness check on the derivation, not a second taxonomy |

### 4.5 The four untreated threat classes

`SC-002` §9.3 records **four untreated threat classes and three attack trees**, and `SC-009` §6 makes
them the pen-test priority list.

> **`STP-09`.** An untreated threat is **still tested**. The test is expected to fail, and its
> failure is the measurement of the untreated risk rather than a surprise at a gate. A class marked
> untreated with no test is a risk nobody has sized.

---

## 5. The Authorisation Suite

### 5.1 The population

| Element | Count | Source |
|---|---:|---|
| Roles | **38** | `SC-004`; `05-04` |
| Access profiles | **67** | `SC-004` §8.4; `SC-005` `G-09` |
| Portal-matrix cells | **456** | `05-04` §2, enumerated `X8` |
| **Granted** | **77** | Positive cases |
| **Denied** | **379** | **Negative cases — `SC-01` forbids sampling** |
| Segregation-of-duties constraints | `SOD-01`…`SOD-12` registered | `05-04`; **`SOD-13`…`SOD-30` used but unregistered** — `RQ-004` `T-12` |

### 5.2 Preconditions — the reason `TS-017` cannot execute today

| # | Precondition | State | Owner |
|---|---|---|---|
| `STP-P1` | **38 role accounts exist per environment**, with record rules, field restrictions and SoD applied | **Absent** — `TS-05` | `M29` owner with Security Lead |
| `STP-P2` | **Each account's effective permission set is asserted before the suite runs** (`TDM-37`, `TAF-33`) | Specified in `QA-004` §9.2 | QA |
| `STP-P3` | `SIT` environment provisioned | **0 of 7** | Platform Engineering |
| `STP-P4` | `SC-004` profiles implemented for the wave's roles | Per wave | Engineering |

> **`STP-10`.** Without `STP-P2` the suite is worse than useless. **An over-permissioned test account
> makes every one of the 379 denial cases pass falsely**, and the result is a green report on a
> broken control. The assertion of effective permissions is therefore the suite's first test, not a
> setup step.

### 5.3 A harness, not 379 scripts

`AUDIT-014` `TS-07` counts ~734 derived cases and observes the arithmetic does not close against
1 QA FTE. **Writing 379 negative scripts by hand is the reason it does not close.**

| # | Design |
|---|---|
| `STP-11` | The suite is **one parameterised harness over a data file** — the `05-04` matrix, machine-readable — built by `QA-005` §12.2. Adding a role or a portal adds rows, not scripts |
| `STP-12` | **The matrix file is generated from `05-04`**, not transcribed. A hand-copied 456-cell matrix will diverge, and the divergence is invisible |
| `STP-13` | **Every cell is asserted through at least two paths: the UI route and the API route.** `TS-018` makes a UI-only denial an automatic `S1`, so a single-path assertion cannot detect the estate's own named `S1` condition |
| `STP-14` | **Field-level and record-level denials are separate assertions** from route-level denial. A user who can reach the page but must not see a column is a third case, and record rules are where Odoo authorisation defects concentrate |
| `STP-15` | **Every denial asserts the declared error code** (`XS-09`), not merely a non-200. A 500 where a 403 is declared is an information-disclosure defect wearing a denial's clothes |

### 5.4 Escalation testing

| Type | Test | Threats |
|---|---|---|
| **Horizontal** | Role `A` reaches another instance of the same object class it does not own — another branch's cash, another seller's payout, another company's assets | `TH-075`…`TH-083`; `AB-09`…`AB-16` |
| **Vertical** | Role `A` performs an action reserved to a higher role — approving beyond band, releasing quarantine, reopening a closed period | `TH-075`…`TH-083` |
| **SoD** | One principal completes both halves of a segregated pair — raising and approving, receiving and paying | `SOD-01`…`SOD-12` |
| **Delegation** | A delegated authority exceeds or outlives its grant | `SC-004` |
| **API-only** | An operation with no UI is reachable by a role the UI never offers it to | `PS-11`, `XS-14` |

### 5.5 The unregistered identifiers

`RQ-004` §6.1 measured **`R39`–`R50` used across 15 files but unregistered**, and **`SOD-13`–`SOD-30`
used but unregistered.**

> **`STP-16`.** The suite covers **`R01`–`R38` and `SOD-01`…`SOD-12`** — the registered sets.
> `QA-004` `TDM-38` rules that provisioning accounts for unregistered roles would give a defective
> requirement set a working implementation. **The gap is reported at every gate as a named coverage
> exclusion** (`MTS-R2`), so it is visible rather than absorbed. Raised as `Q-02`.

---

## 6. Data Scope, Residency and Consent

### 6.1 Scope verification

| Dimension | Assertion |
|---|---|
| **Branch scope** | A branch user reaches only their branch's records, through every route including search, export, report and API |
| **Party scope** | A corporate user reaches only their organisation's assets; a seller only their own listings, orders and payouts |
| **Tier scope** | `T0`–`T5` isolation holds; **`T5` restricted data is reachable only by `R14`**, the single role with that access |
| **Aggregate leakage** | A count, a total or a chart does not disclose what the detail view denies — the most-missed scope defect |
| **Search and export** | Scope holds in search results and in every export format. **An export is the commonest scope bypass**, because it is built after the view and rarely re-secured |

### 6.2 Residency verification

`NFR-086c` requires no unmasked residency-classified data in any region outside its permitted store.

| # | Test |
|---|---|
| `STP-17` | For every residency-classified field, assert the value is **written only to its permitted store** — verified at the storage layer, not by reading the application's claim |
| `STP-18` | Assert **no cross-border transfer** occurs on any path: API response, event payload, backup, log line, error message, analytics extract, notification |
| `STP-19` | **Log lines and error messages are in scope.** A residency-classified value in a log shipped to a non-resident aggregator is a transfer, and it is the route nobody tests |
| `STP-20` | Assert the **`DA-005` residency class survives de-identification** — a masked NID is still residency-restricted (`TDM-14`) |

### 6.3 Consent verification

| # | Test | Obligation |
|---|---|---|
| `STP-21` | Processing does not occur where consent is absent, for every purpose requiring it | `SC-003` `O-1` |
| `STP-22` | **Withdrawal is effective and propagates** — to downstream systems, caches, queues, and the analytics pipeline | `SC-003` `O-2` |
| `STP-23` | A purpose change requires fresh consent; bundled consent is rejected | `SC-003` `O-2` |
| `STP-24` | Erasure operates, with the **statutory-retention override applied correctly** — over-deletion is as much a defect as under-deletion | `SC-003` `O-6`; `DA-006` |
| `STP-25` | **The `P-14` transcript-mining path is asserted *inoperative*** until `SC-003-A-07`'s three conditions complete. `SC-003` determines ⛔ **DO NOT PROCEED**, and a test that proves the path is closed is how that determination is enforced rather than merely recorded | `SC-003` `P-14`, `SC-003-A-07`; `TH-092` |

> **`STP-25` is unusual and deliberate.** Most security tests prove a capability works. This one
> proves a capability **is not reachable**, because `SC-003` `PR-23` records that the remedy for an
> unlawfully trained model may be retraining or retirement — a harm that cannot be undone by deleting
> the corpus.

---

## 7. Audit-Log Completeness

`SC-002`'s repudiation class `TH-041`…`TH-046` and `06-02` `G1-07` — *"audit trail complete for all
delivered objects"* — both land here, and `SC-010` specifies what the log must contain.

| # | Test |
|---|---|
| `STP-26` | **For every delivered object and every state-changing action, an audit entry exists** — asserted by performing the action and querying the log, not by reading the code |
| `STP-27` | Every entry carries actor, role, timestamp with offset, object, before/after and source (`SC-010`) |
| `STP-28` | **The log cannot be modified or deleted by any application role**, including administrators. Immutability asserted, not assumed |
| `STP-29` | **Actions performed through the API produce the same entries as the UI.** An API-only path with no audit entry is a repudiation defect and a `G1-07` failure |
| `STP-30` | **Failed and denied actions are logged**, not only successful ones. A denial with no log entry means an attack leaves no trace — the `TH-041`…`TH-046` class in its purest form |
| `STP-31` | Log completeness is measured as a **ratio with its denominator** (`MTS-R1`): audited actions ÷ state-changing actions for the wave's objects. `G1-07` is otherwise unfalsifiable |

---

## 8. ASVS 5.0.0 Verification

### 8.1 Level per surface

`SC-005` §5 `G-08` already binds it: **L2 estate-wide, L3 for `Z4`-touching and payment paths**
(`SC-001-D-07`). This plan states how it is verified rather than re-deciding it.

| Surface class | ASVS level | Rationale |
|---|:--:|---|
| Internal ERP surfaces | **L2** | Standard for an application handling sensitive data |
| 12 internet-facing portals and applications | **L2** | |
| **`Z4`-touching paths** — restricted data | **L3** | `SC-001-D-07` |
| **Payment paths** | **L3** | Money and PCI-adjacent scope |
| Public webhook receiver | **L2**, plus the `IN-006` receiver rules | An unauthenticated ingress point |

### 8.2 How verification runs

| # | Rule |
|---|---|
| `STP-32` | **ASVS verification is a checklist against the component**, executed per surface per wave, and its result is `E5` + `E6` evidence |
| `STP-33` | **Automated where automatable, human where not.** ASVS 5.0.0's ~350 requirements across 17 chapters include many an automated scan cannot assess; a scan result is never reported as ASVS conformance |
| `STP-34` | **A failed ASVS requirement is a defect** with a severity from `QA-010`, not a note in a report |
| `STP-35` | The verification level and the version — **5.0.0** — appear on every conformance statement. *"ASVS compliant"* with no level and no version is not a claim |

---

## 9. Pipeline Security Testing

**`SC-005` §5 owns gates `G-00`…`G-14`.** This section states only what QA does with their output,
because a gate whose output nobody consumes is a gate that quietly degrades.

| # | Rule |
|---|---|
| `STP-36` | **Gate output is gate evidence.** The `SC-005` results for the wave's scope are attached to the `GV-009` evidence pack as `E5` |
| `STP-37` | **A suppressed or waived finding appears in the pack**, with its waiver, expiry and accepter. A clean report achieved by suppression is `GA-06`'s failure mode |
| `STP-38` | **QA re-runs the gates against the release candidate**, not only against the merge commit. A dependency vulnerability published between merge and release is a real finding |
| `STP-39` | **`SG-1` counts *open* findings in the wave's scope**, so the pack states scope explicitly. *"Zero findings"* from a scan that covered three of nine portals is not zero findings |

---

## 10. Penetration-Test Coordination

**QA does not conduct penetration testing and does not scope it.** `SC-009` §6 and §7 own both, and
`IN-1` requires the tester to be *"external to 1000FiX and independent of the build vendor"*.

| # | QA's part |
|---|---|
| `STP-40` | **Provide the environment and the accounts.** A pen test needs role accounts at every privilege level — the same `STP-P1` dependency |
| `STP-41` | **Provide the case set and the threat model as context**, so the tester does not re-derive what is known and spends the engagement on what is not |
| `STP-42` | **Receive findings into `TS-018` triage** with a severity from `QA-010`, alongside every other defect. A pen-test finding in a separate register is a finding with a separate, slower SLA |
| `STP-43` | **`RC-4`: a finding with no matching `SC-002` threat adds a threat *and* a case here.** The model was incomplete, and that is recorded rather than quietly patched |
| `STP-44` | **`RC-2`/`IN-5`: the retester is not the fixer.** QA does not close a pen-test finding by re-running its own suite |

> **`SC-009-F-02` is adopted, not re-argued:** the first test at W1 is **`PT-C` authorisation and
> isolation**, not a general engagement, because 13 threats sit in that class and *"a record-rule
> defect found after go-live is fixed across live data."* **This plan's §5 suite is the same
> hypothesis tested from the inside**, and the two together are why W1 is the right place for both.

---

## 11. Wave Schedule and Gate Evidence

### 11.1 Schedule

| Wave | Suite scope | `SC-009` engagement | Gate criteria |
|:--:|---|---|---|
| **W1** | Delivered roles' denial cells; `TH-001`…`TH-014` spoofing; `TH-041`…`TH-046` audit; `TH-075`…`TH-083` escalation; ASVS L2 on delivered surfaces | **`PT-C` + `PT-F`** | **`G1-06`, `G1-07`, `G1-09`, `SG-1`** |
| **W2** | + customer portal and technician app; `TH-047`…`TH-062` disclosure; residency (§6.2) | `PT-A`, `PT-B`, `PT-G` + first full annual | `SG-1`, `SG-2`, `SG-3` |
| **W3** | + payment paths at **ASVS L3**; `TH-015`…`TH-040` tampering on statutory outputs | `PT-I` business logic | `G3-04`, `SG-1` |
| **W4** | + full `05-04` matrix at v1.0 scope; consent (§6.3) as **PDPA enforcement activates** | `PT-E` assumed breach + annual | `G4-10`, `SG-1`, `SG-2` |
| **W5** | + `M05` remote support; `Z7` third-party reach | `PT-H` | `SG-1` |
| **W6** | + custody and destruction chains | — | `G6-02`, `G6-03` |
| **W7** | **+ marketplace at its widest** — 5,000 sellers, the largest denial surface in the estate | annual | `G7-02`, `G7-03` |
| **W8** | + analytics and model surfaces; `TH-092` re-identification | annual | `G8-05` |
| **W9** | Full regression of the entire matrix; multi-entity isolation | annual | `G9-01`, `G9-02` |

### 11.2 Gate evidence

`SG-1` requires **`E5` + `E6`** — a test report **and** a reviewer independent of the builder.

| Element | Content |
|---|---|
| **Scope** | Roles, portals, surfaces, threats and abuse cases in scope, **with counts** — `STP-39` |
| Denial coverage | Cells asserted ÷ cells denied in scope, as a triple (`MTS-R1`) |
| Threat coverage | Threats with ≥ 1 executed case ÷ threats applicable to scope |
| Abuse-case coverage | Executed ÷ 32 applicable |
| ASVS | Level, version **5.0.0**, requirements verified, failures |
| Pipeline gates | `SC-005` results, **including waivers** — `STP-37` |
| Pen test | `SC-009` report reference, findings, closure state |
| **Open findings** | Critical and high, **open**, in scope — the `SG-1` assertion |
| **Not executed** | Named, with the reason — `MTS-R2` |
| **Independent opinion** | `E6`, with the reviewer's independence statement |

---

## 12. The Volume Problem

### 12.1 The counted demand

| Population | Count | Repeats |
|---|---:|---|
| Denial cells, no sampling | **379** | per wave, as roles are delivered |
| Granted cells | 77 | per wave |
| Threats with ≥ 1 case | **97** | per applicable wave |
| Abuse cases | **32** | per applicable wave |
| Access profiles with negative sets (`G-09`) | **67** | per wave |
| ASVS L2/L3 requirements per surface | ~350 × surfaces | per wave |
| `TS-017` derived total | **~734** | per wave |

Against **~10 of the 62 QA FTE-months** allocated to `LP-6` in total, shared with performance,
accessibility, localisation and offline (`QA-002` §12.2) — a shortfall `QA-002` measures at ~35
FTE-months, **concentrated in this level and accessibility.**

### 12.2 How it is closed

| # | Mechanism | Effect |
|:--:|---|---|
| 1 | **`STP-11` harness over a generated matrix** | 379 cells become one harness and a data file. This is the single largest reduction available, and it is the reason the arithmetic can close at all |
| 2 | **`STP-12` matrix generated from `05-04`** | Zero maintenance cost as roles change |
| 3 | **`TAF-16` generated negative contract cases** | The API-path half of `STP-13` comes free from the OpenAPI schema |
| 4 | **ASVS automated where automatable** | ~40% of L2 requirements, honestly bounded by `STP-33` |
| 5 | **Abuse cases stay human** | 32 cases at `RC-A`, never sampled (`STP-06`) — this is where the human budget goes |
| 6 | **Pen test is external** | Funded separately under `SC-009`, not from the QA budget |

> **What is *not* used to close it: sampling.** `SC-01` forbids sampling the 379, and `05-04` §10
> criterion 6 makes negative testing a release condition for a role. **A sampled denial suite is a
> role released without the evidence its own standard requires**, and it would be a truncation of an
> `RC-A` population, which `QA-001` `MTS-R9` prohibits outright.

---

## 13. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `QA-007-D-01` | The 379 denial cases | (a) sample; (b) **full coverage via a harness**; (c) defer to pen test | **(b)** | `SC-01` forbids sampling and `05-04` §10 criterion 6 makes it a release condition. A harness makes full coverage affordable | §5.3; `STP-11`…`STP-15` |
| `QA-007-D-02` | Derivation basis | (a) `05-04` set arithmetic alone, as `TS-017` does; (b) **`SC-002` threat model + `05-04`** | **(b)** | Set arithmetic over an access matrix covers no spoofing, repudiation, DoS or business-surface abuse. The threat model does | §4; `STP-02` |
| `QA-007-D-03` | Pipeline gates | (a) re-specify here; (b) **consume `SC-005` output** | **(b)** | `SC-005` §5 already has fail conditions, owners and override paths. Two authorities is the collision defect | §9 |
| `QA-007-D-04` | Penetration testing | (a) QA conducts; (b) **`SC-009` owns; QA coordinates** | **(b)** | `IN-1` requires independence from the builder, and QA is inside the delivery boundary | §10 |
| `QA-007-D-05` | Untreated threat classes | (a) skip until treated; (b) **test them and expect failure** | **(b)** | A failing test measures the untreated risk; no test leaves it unsized | `STP-09` |
| `QA-007-D-06` | The `P-14` path | (a) no test, since it is not built; (b) **assert it is inoperative** | **(b)** | `SC-003` determines ⛔ do not proceed, and `PR-23` records the harm may be irremediable. A test enforces the determination rather than recording it | `STP-25` |
| `QA-007-D-07` | Unregistered `R39`–`R50` | (a) provision and test; (b) **exclude, report as a named gap** | **(b)** | Consistent with `QA-004` `TDM-38`: giving a defective requirement set a working implementation is the wrong direction of fix | `STP-16`; `Q-02` |

---

## 14. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | **When are the 38 role accounts provisioned in `SIT`?** | `M29` owner with Security Lead | **T−6 of `G1`** | **The entire plan.** `G1-06`, `G1-07`, `G1-09`; `TS-017` |
| `Q-02` | Are `R39`–`R50` and `SOD-13`–`SOD-30` registered or withdrawn? | Enterprise Architecture | **W2** | `STP-16`; the completeness of the denial suite |
| `Q-03` | Is the `05-04` matrix available in machine-readable form, or must it be generated from the Markdown? | Enterprise Architecture with QA | **W1** | `STP-12`; the harness's data file |
| `Q-04` | Who is the independent reviewer providing `SG-1`'s `E6` opinion, at every gate? | CISO | **T−6 of `G1`** | `SG-1`; `G1-09` |
| `Q-05` | Is the pen-test budget approved for more than one engagement a year? | CFO with CTO | **W1** | `SC-009` §7's schedule needs 5+ engagements. Recorded on both sides — `SC-009` `Q-04`, `QA-001` `Q-07` |
| `Q-06` | Who asserts that the `P-14` path is closed, and in which component does the assertion live? | Data Protection Officer with Engineering | **before W2** | `STP-25`; `SC-003-A-07` |

---

## 15. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | The boundary with `SC-005`, `SC-009` and `QA-005` is explicit, with no activity claimed twice | §3 — 10 rows |
| `AC-02` | Every `SC-002` threat class has a case type, a level and an automation position | §4.2 — **97 threats across 7 classes** |
| `AC-03` | Every abuse case has an executable test, typed and never sampled | §4.4 — **32**, `RC-A` |
| `AC-04` | All 379 denial cells are covered, with sampling explicitly refused | §5, §12.2 |
| `AC-05` | Every denial is asserted through the UI **and** the API path | `STP-13` |
| `AC-06` | The precondition that would falsify the suite is stated and tested first | `STP-10`, `STP-P2` |
| `AC-07` | Residency verification covers logs, errors, backups and events, not just APIs | §6.2 — `STP-17`…`STP-20` |
| `AC-08` | Audit-log completeness is measured as a ratio with a denominator | `STP-31` |
| `AC-09` | ASVS level, version and method are stated per surface class | §8 — **5.0.0**, L2/L3 |
| `AC-10` | The volume problem is closed by mechanism, not by sampling | §12.2 — 6 mechanisms |
| `AC-11` | Gate evidence satisfies `SG-1`'s `E5` + `E6` including scope and non-execution | §11.2 |

**Definition of done.** Complete when every criterion is met, the 38 role accounts exist in `SIT`,
the harness runs the W1 denial scope, and the approver has signed. Approval carries the `PGD-A1-09`
qualification.

---

## 16. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `SC-002` | 97 threats, 32 abuse cases — the derivation basis |
| Upstream | `SC-004`, `05-04` | 38 roles, 67 profiles, the 456-cell matrix |
| Upstream | `SC-005` §5 | Gates consumed as evidence |
| Upstream | `SC-009` §6, §7 | Pen-test regime, coordinated not owned |
| Upstream | `SC-003` | Consent obligations and the `P-14` determination |
| Upstream | `SC-007`, `DA-005` | Residency classes verified in §6.2 |
| Upstream | `SC-010` | The audit-log specification §7 tests against |
| Upstream | `QA-004` §9 | The 38 role accounts as a dataset |
| Upstream | `QA-005` §12.2 | The negative-authorisation harness |
| Downstream | `QA-010` | Security findings enter triage with a severity |
| Downstream | `QA-011` | Threat, abuse-case and denial coverage reported |
| Downstream | `RL-003` | Go-live readiness consumes `SG-1` evidence |
| Lateral | `../../project_content/13_Test_and_Acceptance_Content/TS-017` | The case pack this plan makes executable |

---

## 17. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` · `./_CATEGORY_OVERVIEW.md` ·
`./QA-001_Master_Test_Strategy.md` · `./QA-003_Test_Design_Specification_and_Case_Repository.md` ·
`./QA-004_Test_Data_Management_and_Anonymisation_Plan.md` · `./QA-005_Test_Automation_Framework_Specification.md` ·
`./QA-010_Defect_Management_and_Quality_Gate_Standard.md` · `./QA-011_Requirements_to_Test_Coverage_Standard_and_Report.md` ·
`../00_Programme_Governance_and_Control/GV-009_Wave_Gate_and_Phase_Exit_Criteria_Handbook.md` ·
`../05_Security_Privacy_and_Compliance/SC-002_Threat_Model_STRIDE_and_Abuse_Case_Register.md` ·
`../05_Security_Privacy_and_Compliance/SC-003_Data_Protection_Impact_Assessment_PDPA_2026.md` ·
`../05_Security_Privacy_and_Compliance/SC-004_Identity_Authentication_and_Authorisation_Design.md` ·
`../05_Security_Privacy_and_Compliance/SC-005_Secure_Development_Lifecycle_Standard.md` ·
`../05_Security_Privacy_and_Compliance/SC-007_Data_Residency_and_Cross_Border_Transfer_Design.md` ·
`../05_Security_Privacy_and_Compliance/SC-009_Vulnerability_Management_and_Penetration_Test_Plan.md` ·
`../05_Security_Privacy_and_Compliance/SC-010_Audit_Logging_and_Forensic_Readiness_Specification.md`

**Workspace**
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md` §2, §10 ·
`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md` §4 ·
`../../project_content/13_Test_and_Acceptance_Content/TS-017_Security_and_Privacy_Test_Case_Pack.md` ·
`../../project_content/_AUDIT/AUDIT-014_Category_13_TS_Content_Audit.md`

**External — verified 2026-08-18**
**OWASP ASVS 5.0.0, 30 May 2025** (~350 requirements, 17 chapters; supersedes 4.0.3) ·
OWASP Testing Guide · OWASP Top 10:2025 · ISO/IEC 27001:2022 A.8.29 ·
ISO/IEC/IEEE 29119-3:2021 §8 · NIST SP 800-115 · STRIDE

---

## 18. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Security with Quality Engineering | Initial issue. A ten-row boundary with `SC-005`, `SC-009` and `QA-005` in which **no activity is claimed twice**; derivation from **`SC-002`'s 97 threats and 32 abuse cases**, replacing set-arithmetic-only derivation; the **379-denial authorisation suite as one parameterised harness over a generated matrix**, asserted through **both UI and API paths**, with the effective-permission assertion made the suite's *first* test because an over-permissioned account makes all 379 pass falsely; data-scope, residency and consent verification including **logs, errors, backups and events**; audit-log completeness measured as a ratio with a denominator so `G1-07` becomes falsifiable; ASVS **5.0.0** levels per surface, correcting the overview's *"ASVS 4"*; and a volume position that closes ~734 cases per wave **by mechanism, refusing sampling**. Records `STP-25` — a test asserting the `P-14` transcript path is *inoperative*, enforcing `SC-003`'s ⛔ determination. Corrects the register's `W2` to `Now` (`QAA-10`) | *Pending — `GV-002`* |

---

*`QA-007` · Category 08 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
