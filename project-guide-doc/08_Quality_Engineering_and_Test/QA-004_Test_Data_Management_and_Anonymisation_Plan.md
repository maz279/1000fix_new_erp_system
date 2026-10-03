---
id: QA-004
title: Test Data Management and Anonymisation Plan
category: 08 — Quality Engineering & Test
code: QA
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: QA Lead with the Data Protection Officer
approver: Chief Data Officer with Legal Counsel
standards_basis: >
  Personal Data Protection Act 2026 (Bangladesh) · ISO/IEC 27001:2022 A.8.10, A.8.11, A.8.33 ·
  ISO/IEC 20889:2018 (privacy-enhancing de-identification terminology and techniques) ·
  ISO/IEC/IEEE 29119-3:2021 §8.8 (test data requirements) · NIST SP 800-188 (de-identification)
traces_to: >
  PGD-000 QA-004 · NFR-071 (masked data only in non-production) · NFR-086c (no unmasked
  residency-classified data in any region) · GV-009 SG-3 · SC-002 TH-092 (re-identifiable corpus) ·
  SC-003 O-1, O-2 · DA-005 §S-class handling matrix · AUDIT-014 TS-05 (38 role accounts absent)
depends_on: QA-001 (environments, MTS-R4) · QA-003 (data_requirement per case) · DA-005 (classification) · SC-003 (DPIA) · SC-004 (roles)
verified_on: 2026-08-18
enumeration_timestamp: 2026-08-18 22:01 (+06)
priority: P0
needed_by: W1
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# QA-004 — Test Data Management and Anonymisation Plan

### Category 08 · Code `QA` · PDPA 2026 · ISO/IEC 20889:2018 · ISO/IEC 27001:2022 A.8.10–A.8.11

---

> **Before writing, read this.**
>
> 1. **`PG-01` Register-first.** Row `QA-004` exists in `PGD-000` Category 08, status ◐ `P0` `W1`.
> 2. **`PG-03` Count, do not consult.** Persona, role, environment and volume figures counted at
>    **2026-08-18 22:01 (+06)**.
> 3. **`PG-06` Cite standards.** §2.1, including why ISO/IEC 20889's vocabulary is used in preference
>    to the estate's loose use of *"anonymised"*.
> 4. **`PG-M4` Verify citations.** PDPA 2026 status inherited from `SC-008`; standards verified
>    2026-08-18.

---

## 1. Purpose

**Using production-derived customer data in a test environment is a processing act under the
Personal Data Protection Act 2026.** It requires a lawful basis, a purpose, a retention position and
a security design — none of which exists today, and all of which this document supplies.

`PGD-000` marks `QA-004` as ◐ citing `TS-002`, and the marking is exact: `TS-002` is an excellent
**persona pack** — eleven personas mapped to eleven registered audiences, Bangladeshi names with
transliteration variants and deliberate near-duplicates, addresses to upazila, valid-format phone
numbers, reserved synthetic statutory identifiers, amounts crossing every approval threshold, and a
Bengali text stress set. **It supplies data. It does not supply a lawful basis, a masking design, a
provisioning mechanism, a refresh policy or a destruction rule**, and it says so.

Three obligations converge on this document:

| Obligation | Source | What it demands |
|---|---|---|
| `NFR-071` | `05-06` §4 | Masked data only in non-production |
| `NFR-086c` | `05-06` §6.4 | **No unmasked residency-classified data in any region** |
| `SG-3` | `GV-009` §9.1 | **Standing gate criterion, `P0`, every gate:** no production personal data in a non-production environment without masking **and a lawful basis** — evidence class `E2` |

> **`SG-3` is the sharpest of the three**, because it is assessed at every one of the nine gates and
> requires system-generated evidence. A programme that cannot produce that evidence fails every gate
> from `G1`, on a criterion that has nothing to do with feature delivery.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | **The provisioning decision** — synthetic-first, and the three narrow cases where it does not hold (§3) |
| 2 | **The lawful basis** for every test-data processing act, per environment (§4) |
| 3 | **The de-identification design** — techniques per `DA-005` class, in ISO/IEC 20889 vocabulary (§5) |
| 4 | **Referential and semantic integrity** — the property that makes masked data testable (§6) |
| 5 | **Provisioning per environment**, with volumes, refresh cadence and freeze rules (§7) |
| 6 | **Volume generation** — how `PERF` reaches 5M orders without any real record (§8) |
| 7 | **The 38 role accounts** — the dependency that blocks four packs (§9) |
| 8 | **Retention, destruction and evidence** (§10) |
| 9 | **Controls, and the eight rules that are absolute** (§11) |

**Explicitly out of scope**

| Topic | Owned by | Why |
|---|---|---|
| The persona content itself — names, addresses, amounts | `TS-002` | This document governs how it is provisioned, secured and refreshed |
| The classification scheme | `DA-005` | Consumed: three axes, `S0`–`S3`, personal-data category, residency class |
| Lawful basis for **production** processing | `SC-003` DPIA | This document covers **testing** as a processing purpose |
| Encryption algorithms, key lifecycle | `SC-006` | This document says what must be protected |
| Access control implementation | `SC-004` | This document says which accounts must exist and what they must hold |
| The **analytics corpus** anonymisation standard (`TH-092`) | `SC-003` `SC-003-A-07` | Different purpose, different lawful basis, different risk. §5.7 states the boundary |
| Migration data quality and profiling | `MG-002`, `MG-003` ⛔ | §7.6 states the interface |
| Environment build | `PE-002` ⛔ | |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| **QA engineers and test analysts** | §7 — what data exists where, and how to get it refreshed |
| **Data Protection Officer and Legal Counsel** | §4 — the lawful basis position, and the one place it is not synthetic |
| Chief Data Officer | §5, §10 — the de-identification design and the destruction rule |
| Platform Engineering | §7, §8 — provisioning, refresh and volume generation |
| Wave-gate assessors | §10.3 — the `SG-3` evidence, `E2`, produced per gate |
| Security Lead | §9 — the 38 role accounts, and their SoD constraints |
| Implementation vendor | §11 — the eight absolute rules, which apply to them identically |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Conformance | Departure and rationale |
|---|---|---|
| **PDPA 2026 (Bangladesh)** | §4 records testing as a processing purpose with a stated basis per environment; §10 sets retention and destruction | None. Status and citation inherited from `SC-008` |
| **ISO/IEC 20889:2018** | §5 uses its **vocabulary and technique taxonomy** — pseudonymisation, generalisation, suppression, randomisation, synthesis — and its distinction between de-identified and anonymised data | **Adopted specifically to stop the estate's loose use of "anonymised."** `SC-002` `TH-092` found a corpus described as *"anonymised"* that is re-identifiable through order references, device serials and rare fault text. **Asserted anonymisation is not demonstrated anonymisation** |
| **ISO/IEC 27001:2022 A.8.10** | §10.2 — information deletion, applied to test datasets | None |
| **A.8.11** | §5 — data masking | None |
| **A.8.33** | §3, §7 — **test information protection** | This is the control this document primarily discharges |
| **ISO/IEC/IEEE 29119-3:2021 §8.8** | §7 supplies the test data requirements each level plan references | None |
| **NIST SP 800-188** | §5.6 — the re-identification risk assessment method | Applied proportionately; a full formal disclosure-risk model is not run on synthetic data |

### 2.2 Source material relied on

| Source | What it establishes |
|---|---|
| `TS-002` | **11 personas** mapped to 11 registered audiences; Bangladeshi names with transliteration variants and deliberate near-duplicates; addresses to upazila; valid-format phone numbers; **reserved synthetic statutory identifiers**; device identities; amounts crossing every approval threshold; a Bengali text stress set |
| `DA-005` | The three classification axes; the `S0`–`S3` scale; **the non-production handling rules: `S0`/`S1` may be copied, `S2` masked, `S3` masked or synthetic — never real values** |
| `SC-003` | The DPIA: 20 purposes, 19 with a stated basis; `DS-3` employees at the weakest power position; the `P-14` hard stop |
| `SC-002` `TH-092` | **A corpus asserted as anonymised and found re-identifiable** — the failure mode §5 is designed against |
| `SC-004` | The **38 roles**, their record rules, field restrictions and SoD constraints |
| `05-04` §2 | **456 portal-matrix cells, 77 granted, 379 denied** — the negative-test population needing accounts |
| `05-06` `NFR-053`, `NFR-054` | **5M service orders/year, 5M assets** — the volumes `PERF` must reach |
| `QA-001` §7 | Seven environments, **0 provisioned**, with their data classes |
| `QA-003` §6.1 attr. 12 | Every case's `data_requirement` — the demand signal this document supplies |
| `AUDIT-014` `TS-05` | **38 role accounts do not exist**, recorded independently by six files |

### 2.3 Audit findings this document closes

| Finding | Source | How | Residual |
|---|---|---|---|
| `TS-05` | `AUDIT-014` | §9 specifies the 38 accounts per environment as a **dataset**, with their permissions, SoD constraints, lifecycle and owner, and makes their existence a `SG-3`-adjacent gate check | Provisioning is `M29` configuration work — `Q-02` |
| `SG-3` unevidenced | `GV-009` §9.1 | §10.3 defines the `E2` evidence: a per-environment scan asserting zero production-derived personal data, generated, not attested | — |
| `TS-002` `O-04` | `AUDIT-014` | §9.1 states the distinction `TS-002` identified: **11 personas describe whom the data is about; 38 roles describe who executes.** Both datasets are required and they are different things | — |
| `QA-004` register row | `PGD-000` | *"Using real customer data in a test environment without masking is a PDPA 2026 processing act with no legal basis"* — §4 supplies the basis and §3 removes most of the need for one | — |

---

## 3. The Provisioning Decision

### 3.1 Synthetic-first

> **`TDM-01`. Test data on this programme is synthetic by default.** Production-derived data is used
> only in the three cases of §3.3, each of which requires the §4 lawful basis, the §5
> de-identification design and a recorded authorisation.

This is a stronger position than `NFR-071` requires — `NFR-071` permits masked production data
generally — and it is chosen deliberately.

| Reason | Detail |
|---|---|
| **`BE-001` already set the precedent** | The development environment is *"synthetic-only, with **no path by which real data reaches a workstation**"*. A weaker rule for `SIT` and `UAT` than for `DEV` would be incoherent |
| **De-identification is a risk, not a control** | Every masked dataset is a re-identification risk that must be re-assessed on every refresh. Synthetic data has none. `TH-092` is the estate's own demonstration |
| **`TS-002` already exists and is better than masked data for testing** | It contains *deliberate* near-duplicates, boundary amounts, a Bengali stress set and reserved statutory identifiers — properties a production extract has only by accident |
| **`SG-3` becomes trivially evidenced** | A synthetic environment's `SG-3` evidence is *"no production data was ever loaded"*, which is far cheaper to produce and far harder to get wrong than *"all production data was masked"* |
| **PDPA exposure falls to near zero** | Synthetic data is not personal data. The processing act largely disappears rather than being justified |

### 3.2 What "synthetic" must mean to be usable

Synthetic data that does not behave like real data finds no defects. `TS-002` already sets this
standard and it is adopted:

| Property | Requirement | Why |
|---|---|---|
| **Shape** | Bangladeshi names with real transliteration variants; addresses to upazila; valid-format phone numbers and NIDs (**reserved synthetic ranges**) | Testing on `test1@test.com` never surfaces a Bengali rendering fault, an address-parsing failure or a name-matching false negative |
| **Distribution** | Realistic skew — a few large corporate customers, many small; seasonal peaks; a long tail of rare device models | Uniform data hides the performance and pagination defects that matter |
| **Adversarial content** | Deliberate near-duplicates; Bengali text at expansion extremes; amounts at every approval threshold; expired and hazardous stock | These are the boundary cases `QA-003` §9.4 requires and a production extract supplies only by luck |
| **Referential integrity** | Every foreign key resolves across all 67 modules | §6 |
| **Statutory identifiers** | **Reserved synthetic ranges, never a valid real value** | A test Mushak challan carrying a real BIN is a live document |

### 3.3 The three cases where synthetic does not hold

| # | Case | Why synthetic fails | Data used | Control |
|:--:|---|---|---|---|
| **`TDM-C1`** | **Migration rehearsal** (L13, `MG-005`) | The purpose is to prove *the real data* migrates. Synthetic data proves the transformation runs, not that it is correct | **Production-derived, de-identified per §5** | Named authorisation; time-limited; destroyed per §10.2 |
| **`TDM-C2`** | **Volume and distribution realism for `PERF`** (L8) | 5M orders must have production-*shaped* distribution | **Synthesised from production *statistics*, never from production *records*** — §8 | The statistics are aggregates and are not personal data |
| **`TDM-C3`** | **Defect reproduction** where a production case cannot be reproduced synthetically | A live defect on a specific record | **The minimum records needed, de-identified, in a time-boxed enclave** | §4.4; destroyed on defect closure; recorded in the defect |

> **`TDM-02`.** Any use outside these three is a **change request** to this plan approved by the
> Chief Data Officer with Legal Counsel. *"It was easier"* is not one of the three.

---

## 4. Lawful Basis

### 4.1 Testing as a processing purpose

`SC-003` registers 20 processing purposes. **Testing is not among them**, because until this document
existed there was no statement of what testing does with personal data.

> **`TDM-03`.** This plan registers **one new purpose** into `SC-003`:
>
> | Field | Value |
> |---|---|
> | **Purpose** | `P-21` — Verification of the system prior to and during live operation |
> | **Categories** | Only those in §3.3's three cases. **In the default synthetic case, none — no personal data is processed** |
> | **Basis** | **Legitimate interest / legal obligation**: a controller is obliged to implement appropriate technical measures, and verifying that a system enforces access control, retention and accuracy is such a measure. Consent is **not** relied on, for the reason `SC-003` `DS-3` gives — it is not freely given where refusal has consequences |
> | **Data subjects** | `DS-1` customers, `DS-3` employees, and partner categories, **only under `TDM-C1` and `TDM-C3`** |
> | **Retention** | §10 — bounded by rehearsal or defect closure |
> | **Transfers** | **None outside Bangladesh** for residency-classified data (`NFR-086c`, `SC-007`) |

### 4.2 Basis per environment

| Environment | Data | Personal data processed? | Basis needed |
|---|---|:--:|---|
| `DEV` | Synthetic subset | **No** | None — `BE-001` forbids any path for real data |
| `CI` | Fixtures | **No** | None |
| `SIT` | Full `TS-002` set | **No** | None |
| `UAT` | Full `TS-002` set, frozen | **No** | None |
| `TRAIN` | Full `TS-002` set, resettable | **No** | None |
| `SANDBOX` | Masked, representative (`IN-008`) | **No** — synthetic satisfies *"representative"* | None. §7.5 rules this |
| `PERF` | Synthesised at volume from **statistics** | **No** | None — §8 |
| **Migration rehearsal enclave** | **Production-derived, de-identified** | **Yes** | `P-21`, `TDM-C1`, named authorisation |
| **Defect enclave** | **Production-derived, minimum records** | **Yes** | `P-21`, `TDM-C3`, recorded in the defect |

> **Seven of nine contexts process no personal data at all.** That is the point of the
> synthetic-first decision: the lawful-basis question narrows from *"the whole test estate"* to
> **two bounded, authorised, time-limited enclaves.**

### 4.3 Employees are the harder case

`SC-003` `DS-3` records employees at the **weakest power position**, and that consent *"is generally
not a valid basis in an employment relationship."*

| # | Rule |
|---|---|
| `TDM-04` | **Employee personal data is never used for testing, in any environment, in any form** — including in `TDM-C1` and `TDM-C3`. Payroll rehearsal (`G5-01`, `TS-010`) uses synthetic employees with synthetic salaries |
| `TDM-05` | **`TS-010`'s payroll parallel run is the sole exception**, and it is not a test-data act: it is a comparison of two live calculations over the same real population, performed **inside** the HR system's own controls by HR, with no extract leaving it. §7.7 |
| `TDM-06` | **Biometric templates are never copied to any non-production environment**, under any de-identification. `SC-003` `DPIA-04` records the harm as **irreversible** — a compromised template cannot be reissued |

### 4.4 The two enclaves

| Property | Migration rehearsal (`TDM-C1`) | Defect reproduction (`TDM-C3`) |
|---|---|---|
| Authorised by | Chief Data Officer with the Data Migration Lead | Chief Data Officer, per defect |
| Duration | The rehearsal window, extended only by re-authorisation | Until the defect closes |
| Location | **Bangladesh-resident infrastructure only** (`SC-007`) | Same |
| Access | Named individuals, MFA, session-recorded (`SC-010`) | Same, plus the assigned engineer |
| De-identification | §5, applied **before** the data enters the enclave | Same |
| Egress | **None.** No extract, no screenshot of unmasked data, no export | Same |
| Destruction | §10.2, evidenced | §10.2, evidenced, referenced in the defect record |
| Register | Recorded in `SC-003`'s processing register with dates | Same |

---

## 5. The De-identification Design

### 5.1 Vocabulary — and why it matters here

ISO/IEC 20889:2018 distinguishes terms the estate has been using interchangeably. Getting this wrong
is exactly what `TH-092` found.

| Term | Meaning | Still personal data? |
|---|---|:--:|
| **Pseudonymisation** | Identifiers replaced with tokens; re-identification possible with the mapping | **Yes** |
| **De-identified** | Direct identifiers removed or transformed; re-identification possible with effort or auxiliary data | **Usually yes** |
| **Anonymised** | Re-identification not reasonably possible **by any party, with any auxiliary data** | **No** — and this is a high bar |
| **Synthetic** | Generated; no correspondence to any real individual | **No** |

> **`TDM-07`.** No dataset in this programme is described as *"anonymised"* unless a §5.6
> re-identification risk assessment has been performed and recorded. **`SC-002` `TH-092` is the
> estate's own worked example of the failure**: a corpus called anonymised, re-identifiable through
> order references, device serials and rare fault text.

### 5.2 Technique per `DA-005` sensitivity class

`DA-005` sets the non-production rule; this table gives it a mechanism.

| `S` class | `DA-005` non-production rule | Technique applied here |
|:--:|---|---|
| `S0` Public | May be copied | Copy |
| `S1` Internal | May be copied | Copy |
| `S2` Confidential | **Masked** (`NFR-071`) | **Substitution** from the `TS-002` value pools, format-preserving, referentially consistent (§6) |
| `S3` Restricted | **Masked or synthetic. Never real values** | **Synthesis only.** No transformation of a real `S3` value is permitted, because a reversible transformation of a restricted value is a restricted value |

### 5.3 Technique per personal-data category

| Category | Examples | Technique | Note |
|---|---|---|---|
| **Direct identifier** | Name, phone, email, NID, TIN, BIN | **Substitution** from `TS-002` pools | Bengali and English name pools with transliteration variants preserved |
| **Statutory identifier** | NID, TIN, BIN, Mushak sequences | **Synthesis from reserved ranges** | `TDM-08`: a test statutory identifier must be **invalid in the real world by construction**, not merely unused |
| **Quasi-identifier** | Date of birth, upazila, device serial, job reference | **Generalisation** — DoB to month, address to district for `S2` | The `TH-092` failure mode: quasi-identifiers left intact re-identify without any direct identifier |
| **Free text** | Fault descriptions, chat transcripts, notes | **Suppression or synthesis. Never substitution** | `TDM-09`: free text cannot be reliably masked, because a rare fault description is itself identifying |
| **Special category** | Biometric template, health, criminal record | **Never present** (`TDM-06`) | Not a masking question |
| **Financial** | Card PAN, account number, MFS wallet | **Synthesis** from test ranges | PCI-DSS scope: a masked real PAN is still in scope; a synthetic one is not |
| **Location** | GPS traces | **Randomisation within a plausible envelope** | A real technician's trace reveals a real person's movements |
| **Media** | Photographs, signatures, documents | **Synthesis or suppression** | A photo cannot be masked |

### 5.4 The rules that make masking hold

| # | Rule |
|---|---|
| `TDM-10` | **Masking is applied at extract, before the data leaves production.** Copy-then-mask means unmasked production data existed in a non-production store, which is the breach `SG-3` tests for |
| `TDM-11` | **The mapping between real and substituted values is destroyed after extract**, unless a rehearsal reconciliation requires it — in which case it is held **inside production's controls**, never with the dataset |
| `TDM-12` | **Masking is deterministic within a dataset and non-deterministic across datasets.** Determinism preserves joins (§6); cross-dataset variation prevents accumulating a mapping from repeated refreshes |
| `TDM-13` | **Masked data is `S2` in its destination**, not `S0`. De-identified is not public |
| `TDM-14` | **Residency-classified fields are never de-identified out of their residency class.** A masked NID is still residency-restricted — `NFR-086c` is about the *field*, not the *value* |

### 5.5 Format-preserving substitution

Substitution must preserve the properties the system validates against, or masked data fails
validation and hides real defects.

| Property preserved | Why |
|---|---|
| Length and character class | Field validation, column widths, layout |
| **Script** — Bengali stays Bengali | Rendering, sorting, search and `UX-007` expansion behaviour |
| Format and checksum validity | An NID that fails its own format check tests the validator, not the feature |
| Cardinality and duplication pattern | Deduplication and matching logic depends on it |
| Referential consistency | §6 |
| Null and blank distribution | Empty-state handling |

### 5.6 The re-identification risk assessment

Required for `TDM-C1` and `TDM-C3` only. Proportionate, not a formal disclosure-risk model.

| Step | Action |
|:--:|---|
| 1 | Enumerate quasi-identifiers remaining after §5.3 |
| 2 | Compute the smallest equivalence-class size across the quasi-identifier set — **target k ≥ 10** |
| 3 | Test against the auxiliary data an attacker plausibly holds: **the customer's own records, a device serial, a public directory** — the `TH-092` vectors |
| 4 | Test **free-text** columns for identifying content by sampling |
| 5 | Record the result, the residual risk and the accepter |
| 6 | **Re-run on every refresh.** A dataset that was safe at one extract is not automatically safe at the next |

> **`TDM-15`.** k < 10 on any quasi-identifier combination **blocks the extract**. The response is
> further generalisation or suppression, not acceptance.

### 5.7 The boundary with `SC-003` `SC-003-A-07`

`SC-003` requires an **anonymisation standard** for the analytics corpus, published and tested, as
one of three conditions before any transcript-derived work begins at W2. **That is a different
standard from this one** and this document does not discharge it.

| | This document | `SC-003-A-07` |
|---|---|---|
| Purpose | Verification (`P-21`) | Product improvement, model training (`P-14`) |
| Data | Bounded, short-lived, enclave-held | A growing corpus, retained |
| Bar | De-identified to k ≥ 10, destroyed after use | **Anonymised** — re-identification not reasonably possible, permanently |
| Determination | Proceed under §4.4 controls | ⛔ **Do not proceed** until all three conditions complete |

**Recorded so that §5 is not later cited as satisfying `SC-003-A-07`.** It does not: a technique set
adequate for a destroyed, enclave-held rehearsal dataset is not adequate for a retained corpus used
to train models, and `PR-23` records why — the remedy for an unlawfully trained model may be
retraining or retirement.

---

## 6. Referential and Semantic Integrity

### 6.1 Why this is the hard part

A masked dataset that breaks joins is worse than no dataset: every failure is a data artefact, and
the team learns to ignore failures. With **67 modules, ~1,335 entities and 1,187 API operations**,
integrity is the property that decides whether the data is usable at all.

| # | Rule |
|---|---|
| `TDM-16` | **A value substituted in one place is substituted identically everywhere** — the customer's name in `M02`, on the invoice in `M19`, in the notification in `M28` and in the warehouse in `M62` |
| `TDM-17` | **Every foreign key resolves.** An extract that breaks a relationship is rejected, not patched |
| `TDM-18` | **Semantic relationships survive.** A customer's district matches their branch's district; a technician's skill matches their assigned jobs; an invoice's total equals its lines |
| `TDM-19` | **Time relationships survive.** A closure is after its creation; an SLA breach is genuinely late; a warranty is inside its term. **Dates are shifted by a constant per dataset, never randomised per row** |
| `TDM-20` | **State machines are consistent.** An order in `closed` has all its prior transitions, or the state model tests nothing |

### 6.2 The date-shift rule, stated separately

> `TDM-19`'s constant shift is the rule most often got wrong. **Randomising dates per row destroys
> every interval in the dataset** — SLA measurement, ageing, warranty windows, retention triggers,
> month-end boundaries. A single constant shift per dataset preserves every interval while moving
> the absolute dates. **The shift value is part of the dataset's metadata and is regenerated per
> refresh** (`TDM-12`).

### 6.3 Coverage of the case demand

`QA-003` §6.1 attribute 12 requires every case to state a `data_requirement` — *what the data must be
like*, not values. This document is the demand's supply side.

| # | Rule |
|---|---|
| `TDM-21` | **Every `data_requirement` in the case repository resolves to a fixture, persona or generated set**, and the resolution is generated, not maintained by hand |
| `TDM-22` | **An unresolvable `data_requirement` blocks the case**, and is reported as a data gap against the dataset owner — not worked around by the tester inventing a record |
| `TDM-23` | **Test data is versioned with the case set.** A case that passed against v3 of the dataset and fails against v4 has a data change, not a defect, and the version makes that visible |

---

## 7. Provisioning Per Environment

### 7.1 The matrix

| Env | Dataset | Volume | Refresh | Freeze | Owner |
|---|---|---|---|---|---|
| `DEV` | `TS-002` subset | ~1k customers, ~5k orders | On demand, self-service | No | Engineering |
| `CI` | Fixtures only, in-repository | Per test | Per commit | No | Platform Engineering |
| `SIT` | **Full `TS-002` set** + 38 role accounts | ~50k customers, ~250k orders | **Per release** | No | QA Lead |
| `UAT` | Full set + role accounts | Same as `SIT` | **Per wave** | **Yes — for the whole window** | QA Lead with Business Owners |
| `PERF` | **Generated at volume** (§8) | **5M orders, 5M assets** (`NFR-053`, `NFR-054`) | **Per wave gate** | Yes, during a run | Platform Engineering |
| `TRAIN` | Full set, per-cohort copy | Same as `SIT` | **Per cohort** | No — reset instead | L&D Lead |
| `SANDBOX` | Full set, partner-visible subset | ~5k customers | Per release | No | Integration Lead |

**All seven are 0-provisioned at issue** (`QA-001` §7.1). This matrix is the requirement `PE-002`
builds against.

### 7.2 Refresh

| # | Rule |
|---|---|
| `TDM-24` | **Refresh is automated and repeatable.** A hand-built dataset cannot be rebuilt after corruption, so it is never rebuilt, so it drifts |
| `TDM-25` | **Refresh is idempotent** — the same generator inputs produce the same dataset, so a defect is reproducible |
| `TDM-26` | **`UAT` is never refreshed inside a window** (`MTS-U5`; `LVP-A2`). A refresh during a cycle suspends the level |
| `TDM-27` | **A refresh publishes its dataset version**, and open defects are re-checked against the new version before being closed as *not reproducible* |
| `TDM-28` | **`TRAIN` is reset per cohort, not refreshed**, because trainees destroy data by design and the next cohort needs the same starting state |

### 7.3 The `UAT` freeze mechanism

`LVP-A2` requires frozen data for the window and `MTS-U5` suspends the level if it moves. The
mechanism:

| Element | Provision |
|---|---|
| Snapshot | Taken at window open, retained until window close + 30 days for evidence |
| Write access | Only the UAT executors' role accounts. **No engineering write access during the window** |
| Configuration | Frozen with the data; a configuration change is a `MTS-U4` build change |
| Exception | An `S1` fix may require a data correction; it is authorised by the QA Lead, recorded, and **re-triggers the affected scripts** |
| Evidence | The snapshot identifier appears in every signed script set, so a signature is attributable to a known state |

### 7.4 Self-service, because the alternative does not scale

> **`TDM-29`.** Environment refresh and dataset selection are **self-service for QA and
> engineering**, through a documented command. With 62 QA FTE-months total, a provisioning process
> requiring a ticket to Platform Engineering consumes the capacity `QA-001` §10 shows does not
> exist. This mirrors `BE-001`'s six Compose profiles: the supported path is the easy path.

### 7.5 `SANDBOX` — synthetic satisfies "representative"

`IN-008` cites `FR-IPF-019`'s requirement for *"a sandbox with representative masked data for
external consumers."*

> **Ruled: `TS-002`'s synthetic set satisfies "representative", and no masked production data is
> placed in `SANDBOX`.** The sandbox is **internet-facing and consumed by external parties** —
> 500–2,000 marketplace sellers, courier partners, brand partners. It is the single worst destination
> for de-identified production data in the estate, and synthetic data meets the actual requirement:
> a partner needs data that is *shaped* like production, not data that *is* production.
> Recorded as `QA-004-D-03`.

### 7.6 Migration data — the interface

`MG-001`…`MG-003` are ⛔ and `MG-002` records **all 48 legacy sources unprofiled**.

| # | Rule |
|---|---|
| `TDM-30` | **`TDM-C1` rehearsal data is de-identified by the migration ETL itself**, not by a separate pass, so the rehearsal exercises the real pipeline |
| `TDM-31` | **Legacy profiling (`MG-002`) is a prerequisite of any rehearsal extract.** Extracting from a source nobody has looked inside cannot be de-identified reliably, because the identifying content is unknown |
| `TDM-32` | Reconciliation between rehearsal and source is by **control totals**, not by record inspection — `E7`. This is what allows the data to stay in the enclave |

### 7.7 Payroll parallel run — not a test-data act

`TS-010` requires a parallel-run comparison before the first live payroll, and `G5-01` requires zero
errors.

> **`TDM-05` restated:** the parallel run is **not** an extract. Two calculations are performed over
> the same real population **inside the HR system's own controls**, by HR, and only the **variance
> report** — differences, not personal data — leaves that boundary. No employee record is copied to
> `SIT` or `UAT`. This is the design that lets `G5-01` be evidenced without `TDM-04` being breached.

---

## 8. Volume Generation for `PERF`

### 8.1 The requirement

`NFR-053` requires 5 million service orders per year and `NFR-054` a 5-million-asset registry;
`NFR-003` and `NFR-004` require 800 concurrent internal and 75,000 concurrent portal users, tested at
**1.5×** (`05-06` §11). **No production system exists to extract from** — the programme is
greenfield — so volume must be generated regardless.

### 8.2 Statistics, not records *(`TDM-C2`)*

| # | Rule |
|---|---|
| `TDM-33` | **`PERF` data is generated from a distribution model**, parameterised by aggregate statistics: order volume by branch by month, device model frequency, customer order-count distribution, payment-method mix, fault-code frequency |
| `TDM-34` | **Aggregate statistics of this kind are not personal data**, provided no cell is small enough to identify — **minimum cell size 20**, below which the cell is merged |
| `TDM-35` | **The generator is deterministic from a seed**, so a performance result is reproducible and a regression is attributable |
| `TDM-36` | **Volume without distribution is not a performance test.** Five million identical orders exercise no index, no partition and no cache-miss path. The model carries the skew |

### 8.3 What the model must reproduce

| Dimension | Why it changes the result |
|---|---|
| Branch skew — Dhaka ~20 of 51+ centres | Partition hot-spotting |
| Temporal skew — daily peaks, seasonal peaks, month-end close | Concurrency and lock contention |
| Customer order-count long tail | Pagination, `M02` customer-360 load (`NFR-031` ≤ 2 s) |
| Device model frequency | `NFR-054` registry lookup and search (`NFR-035` ≤ 600 ms **including Bengali text**) |
| Text-length distribution, both scripts | Index size and Bengali search performance |
| Attachment size distribution | `NFR-060` 50 TB document store with sub-10-second retrieval |
| Open vs closed ratio | `NFR-033` dispatch board at 500 open jobs ≤ 1 s |

---

## 9. The 38 Role Accounts

### 9.1 Personas and roles are different datasets

`TS-002` `O-04` identified this and could not resolve it: **eleven personas describe *whom the data
is about*; thirty-eight roles describe *who executes*.** A persona is a customer record; a role
account is an authenticated principal with record rules, field restrictions and SoD constraints
applied. **Six files record the absence independently**, which `AUDIT-014` `TS-05` treats as evidence
that the constraint is real rather than an authoring artefact.

### 9.2 The dataset

| Property | Requirement |
|---|---|
| Count | **38**, `R01`…`R38` per `SC-004` and `05-04` |
| Per environment | `SIT`, `UAT`, `TRAIN`, `SANDBOX` (partner roles only), `PERF` (load-generating subset) |
| Permissions | **Exactly** the role's permissions — no more, and critically **no less** |
| Record rules | Applied, so branch and party scoping is genuinely enforced |
| Field restrictions | Applied, so field-level denial is testable |
| SoD constraints | `SOD-01`…`SOD-12` applied, so a segregation violation is detectable |
| Credentials | Managed as secrets (`SC-006`), never in a repository, rotated per refresh |
| MFA | Configured as production configures it, or the login path is untested |
| Lifecycle | Created with the environment; destroyed with it |
| Owner | `M29` owner with the Security Lead |

> **`TDM-37`.** An account with *more* permission than its role is the more dangerous error: it makes
> **every one of the 379 denial cases pass falsely**. `QA-007` §5 requires each account's effective
> permission set to be **asserted before the negative suite runs**.

### 9.3 What this unblocks

| Blocked today | Unblocked by §9 |
|---|---|
| `TS-017` — *"not a precondition but the entire pack"*, ~734 derived cases | Executable |
| `TS-003` `O-02`, `TS-004` `O-03` — SIT preconditions | L5 entry criterion satisfiable |
| `TS-006` precondition 7, `TS-011` precondition 9 | L7 entry criterion satisfiable |
| `G1-06` role framework operating for all delivered roles; `G1-09` zero critical or high | Evidenceable |
| `05-04` §10 criterion 6 — negative testing as a role-release condition | Satisfiable |

### 9.4 The unregistered roles

`RQ-004` §6.1 measured `T-12` and found **`R39`–`R50` used across 15 files but unregistered**, and
**`SOD-13`–`SOD-30` used but unregistered**.

> **`TDM-38`.** The role-account dataset covers **`R01`–`R38` only**, because those are the roles that
> exist. **`R39`–`R50` are a requirements defect, not a test-data gap**, and are routed to `RQ-005`
> change control under `TR-06`. Provisioning accounts for unregistered roles would give a defective
> requirement set a working implementation, which is the wrong direction of fix. Raised as `Q-04`.

---

## 10. Retention, Destruction and Evidence

### 10.1 Retention

| Dataset | Retention | Basis |
|---|---|---|
| Synthetic sets | Programme life | Not personal data |
| Generator seeds and parameters | Programme life + 5 years | Reproducibility of test evidence (`GA-08`) |
| `UAT` snapshots | Window + 30 days | Attributability of signatures |
| Test evidence — logs, screenshots, reports | **Programme life + 5 years minimum** | `GA-08`; PDPA 2026 retention |
| **`TDM-C1` rehearsal data** | **The rehearsal window only** | `P-21`; minimisation |
| **`TDM-C3` defect data** | **Until the defect closes** | `P-21`; minimisation |
| Real↔substitute mappings | **Destroyed at extract** unless §5.4 `TDM-11` applies | Minimisation |

### 10.2 Destruction

| # | Rule |
|---|---|
| `TDM-39` | **Destruction is evidenced, not asserted** — a dated record naming the dataset, the method and the person, retained per `GA-08` |
| `TDM-40` | **Destruction covers backups, snapshots and derived extracts**, not only the primary store. A destroyed dataset present in a nightly backup is not destroyed |
| `TDM-41` | **An enclave is destroyed on its authorisation expiring**, whether or not the work finished. Extension is re-authorisation |
| `TDM-42` | Method follows `DA-006` and `SC-006`; **`H-01` records that NIST SP 800-88 r1 is withdrawn**, so the method is cited from the current source `RR-005` registers |

### 10.3 `SG-3` evidence — generated, not attested

`GV-009` `SG-3` is a `P0` standing criterion at **every** gate, evidence class **`E2` — a
system-generated report**, not a signature.

| Element | Provision |
|---|---|
| **Check** | An automated scan of every non-production environment for production-derived personal data |
| **Method** | (a) provenance — every dataset carries its generator identity and seed, and a dataset with no generator identity **fails**; (b) content — sampling for values in production identifier ranges; (c) statutory identifiers validated against the **reserved synthetic ranges** (`TDM-08`) |
| **Frequency** | **Nightly**, and immediately before each gate |
| **Output** | Per environment: dataset inventory, generator identity, last refresh, scan result, exceptions |
| **Failure** | **Suspends all testing in that environment immediately** (`MTS-U3`), triggers `SC-011` incident response, and requires the data destroyed and the DPIA reviewed |

> **This is the single most valuable control in this document.** It converts *"we believe the test
> environments are clean"* into a nightly, falsifiable, `E2` assertion — and it is only cheap because
> §3.1 made the environments synthetic, so the expected result is *zero* rather than *all masked*.

---

## 11. The Eight Absolute Rules

Consolidated so they can be cited singly. Each restates a rule above, and each has a named source.

| # | Rule | Source |
|:--:|---|---|
| **`TDM-A1`** | **No production personal data in any non-production environment**, except in the two authorised enclaves of §4.4 | `NFR-071`; `SG-3`; `MTS-R4` |
| **`TDM-A2`** | **No employee personal data used for testing, anywhere, in any form** | `TDM-04`; `SC-003` `DS-3` |
| **`TDM-A3`** | **No biometric template leaves production, under any de-identification** | `TDM-06`; `DPIA-04` — the harm is irreversible |
| **`TDM-A4`** | **No unmasked residency-classified data outside its permitted store, in any environment, in any region** | `NFR-086c`; `SC-007` |
| **`TDM-A5`** | **No real statutory identifier in any test dataset** — reserved synthetic ranges only | `TDM-08`. A test Mushak challan with a real BIN is a live document |
| **`TDM-A6`** | **No dataset called "anonymised" without a recorded §5.6 assessment** | `TDM-07`; `TH-092` |
| **`TDM-A7`** | **No test data outside version control and configuration management** | `TDM-23`; `GV-011` |
| **`TDM-A8`** | **No `UAT` data change inside a frozen window** without recorded authorisation and script re-trigger | `LVP-A2`; `MTS-U5` |

---

## 12. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `QA-004-D-01` | Default provisioning | (a) masked production data per `NFR-071`; (b) **synthetic-first, three narrow exceptions**; (c) mixed by environment | **(b)** | Seven of nine contexts then process **no personal data at all**; `SG-3` evidence becomes *"never loaded"* rather than *"all masked"*; and `TS-002` is better test data than a production extract | `TDM-01`; the lawful-basis question narrows to two bounded enclaves |
| `QA-004-D-02` | Statutory identifiers | (a) mask real ones; (b) **synthesise from reserved invalid ranges** | **(b)** | A masked-but-valid BIN on a test challan is a live document | `TDM-08`; `TDM-A5` |
| `QA-004-D-03` | `SANDBOX` data | (a) masked production per `FR-IPF-019`'s *"masked"*; (b) **synthetic** | **(b)** | The sandbox is internet-facing and consumed by 500–2,000 external sellers — the worst destination for de-identified production data. *"Representative"* is satisfied by shape | §7.5 |
| `QA-004-D-04` | Date handling in masked sets | (a) randomise per row; (b) **constant shift per dataset** | **(b)** | Per-row randomisation destroys every interval — SLA, ageing, warranty, retention, month-end | `TDM-19`; §6.2 |
| `QA-004-D-05` | `PERF` volume source | (a) production extract at volume; (b) **generation from aggregate statistics with min cell size 20** | **(b)** | No production system exists to extract from, and aggregates above the cell floor are not personal data | `TDM-33`…`TDM-36` |
| `QA-004-D-06` | Role accounts for `R39`–`R50` | (a) provision them; (b) **do not — route to `RQ-005`** | **(b)** | Provisioning accounts for unregistered roles gives a defective requirement set a working implementation | `TDM-38`; `Q-04` |
| `QA-004-D-07` | Provisioning model | (a) ticket to Platform Engineering; (b) **self-service through a documented command** | **(b)** | 62 QA FTE-months cannot absorb a ticket queue; `BE-001`'s precedent — the supported path is the easy path | `TDM-29` |

---

## 13. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | Is `P-21` accepted into `SC-003`'s processing register, with legitimate interest / legal obligation as its basis? | Data Protection Officer with Legal Counsel | **W1** | §4; every enclave use; `SG-3` |
| `Q-02` | Who provisions the 38 role accounts per environment, and when? | `M29` owner with Security Lead | **W1, before SIT entry** | `TS-017` entirely; `G1-06`, `G1-09`; L5, L7, L9 entry |
| `Q-03` | Who builds and owns the synthetic data generator, and is it funded? | Platform Engineering with QA Lead | **W1** | Every environment; `TDM-24`, `TDM-33` |
| `Q-04` | Are `R39`–`R50` and `SOD-13`–`SOD-30` registered or withdrawn? | Enterprise Architecture | **W2** | `TDM-38`; `RQ-004` `T-12`; role coverage measure |
| `Q-05` | Is the nightly `SG-3` scan funded, and where does it run given 0 of 7 environments exist? | CTO with Platform Engineering | **W1** | §10.3; every gate's `SG-3` |
| `Q-06` | Does the payroll parallel-run design in §7.7 satisfy HR and Legal? | HR Director with Legal Counsel | **W4**, ahead of W5 | `G5-01`; `TS-010`; `TDM-A2` |

---

## 14. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | A provisioning default is stated, with every exception enumerated and controlled | §3 — synthetic-first, 3 exceptions |
| `AC-02` | A lawful basis exists for every context in which personal data is processed | §4.2 — 9 contexts, **7 processing none** |
| `AC-03` | A de-identification technique is stated per `DA-005` class and per personal-data category | §5.2, §5.3 — 4 classes, 8 categories |
| `AC-04` | ISO/IEC 20889 vocabulary is used, and *"anonymised"* is gated on an assessment | §5.1, §5.6; `TDM-07` |
| `AC-05` | Referential, semantic and temporal integrity rules are specified | §6 — 5 rules + the date-shift rule |
| `AC-06` | Every environment has a dataset, volume, refresh cadence and owner | §7.1 — 7 of 7 |
| `AC-07` | `PERF` volume is achievable without any production record | §8 |
| `AC-08` | The 38 role accounts are specified as a dataset with permissions, SoD and lifecycle | §9.2 |
| `AC-09` | Retention and destruction are specified and evidenced | §10.1, §10.2 |
| `AC-10` | `SG-3` evidence is system-generated, nightly, and falsifiable | §10.3 |
| `AC-11` | The absolute rules are consolidated and individually sourced | §11 — 8 rules |

**Definition of done.** Complete when every criterion is met, `P-21` is registered in `SC-003`, the
generator produces the `SIT` dataset, the 38 role accounts exist in `SIT`, the nightly `SG-3` scan
runs, and the approver has signed. Approval carries the `PGD-A1-09` qualification.

---

## 15. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `DA-005` | The three classification axes and the non-production handling rules |
| Upstream | `SC-003` | The DPIA; `P-21` is registered into it |
| Upstream | `SC-004`, `05-04` | The 38 roles, their permissions, record rules and SoD constraints |
| Upstream | `SC-006`, `SC-007` | Encryption, key management, residency |
| Upstream | `QA-001` §7 | The seven environments and their data classes |
| Upstream | `QA-003` §6.1 | Every case's `data_requirement` |
| Downstream | `QA-002` §12.3 | The test data requirement per level plan |
| Downstream | `QA-006` | `PERF` volume generation |
| Downstream | `QA-007` | Role accounts for the 379 denial cases |
| Downstream | `QA-009` | The `UAT` freeze mechanism supporting business sign-off |
| Downstream | `MG-005` | Rehearsal data de-identified by the migration ETL |
| Downstream | `PE-002` | §7.1 is its provisioning requirement |
| Lateral | `../../project_content/13_Test_and_Acceptance_Content/TS-002` | The persona pack this document provisions |

---

## 16. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` · `./_CATEGORY_OVERVIEW.md` ·
`./QA-001_Master_Test_Strategy.md` · `./QA-002_Test_Plans_per_Level.md` ·
`./QA-003_Test_Design_Specification_and_Case_Repository.md` · `./QA-006_Performance_and_Load_Test_Plan.md` ·
`./QA-007_Security_Test_Plan.md` · `./QA-009_UAT_Plan_and_Business_Sign_off_Protocol.md` ·
`../00_Programme_Governance_and_Control/GV-009_Wave_Gate_and_Phase_Exit_Criteria_Handbook.md` ·
`../03_Data_and_Information_Architecture/DA-005_Data_Classification_and_Handling_Standard.md` ·
`../03_Data_and_Information_Architecture/DA-006_Data_Retention_Archival_and_Deletion_Design.md` ·
`../05_Security_Privacy_and_Compliance/SC-002_Threat_Model_STRIDE_and_Abuse_Case_Register.md` ·
`../05_Security_Privacy_and_Compliance/SC-003_Data_Protection_Impact_Assessment_PDPA_2026.md` ·
`../05_Security_Privacy_and_Compliance/SC-004_Identity_Authentication_and_Authorisation_Design.md` ·
`../05_Security_Privacy_and_Compliance/SC-007_Data_Residency_and_Cross_Border_Transfer_Design.md` ·
`../07_Build_Engineering_and_Development_Standards/BE-001_Development_Environment_Setup_Guide.md`

**Workspace**
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md` ·
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md` ·
`../../project_content/13_Test_and_Acceptance_Content/TS-002_Test_Data_Pack_and_Persona_Set.md` ·
`../../project_content/_AUDIT/AUDIT-014_Category_13_TS_Content_Audit.md`

**External standards — verified 2026-08-18**
Personal Data Protection Act 2026 (Bangladesh), status per `SC-008` §4 ·
ISO/IEC 20889:2018 · ISO/IEC 27001:2022 A.8.10, A.8.11, A.8.33 ·
ISO/IEC/IEEE 29119-3:2021 §8.8 · NIST SP 800-188

---

## 17. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Quality Engineering with the Data Protection Officer | Initial issue. **Synthetic-first provisioning**, reducing the personal-data question from the whole test estate to **two bounded, authorised enclaves**; processing purpose `P-21` registered into `SC-003` with a basis that is explicitly not consent; de-identification technique per `DA-005` class and per personal-data category, in **ISO/IEC 20889 vocabulary**, with *"anonymised"* gated on a recorded k ≥ 10 assessment; referential, semantic and **constant-shift temporal** integrity rules; provisioning, refresh and freeze per environment for all seven; volume generation for `PERF` from **statistics, not records**; the **38 role accounts** specified as a dataset, closing `TS-05`'s test-data half; retention and evidenced destruction; and the **nightly, system-generated `SG-3` evidence** that converts a belief into a falsifiable assertion. Eight absolute rules `TDM-A1`…`TDM-A8` | *Pending — `GV-002`* |

---

*`QA-004` · Category 08 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
