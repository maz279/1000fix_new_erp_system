---
id: MG-004
title: Reconciliation and Validation Plan
category: 09 — Data Migration & Cutover
code: MG
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: QA Lead with the Data Migration Lead
approver: Chief Financial Officer with the Chief Technology Officer
standards_basis: >
  ISO 8000-61:2016 — data quality assurance (7.4) · ISO/IEC/IEEE 29119-3:2021 — test completion
  reporting structure, applied to migration validation · ISA 500 / ISA 530 (audit evidence and
  audit sampling) as the basis for the attribute-sampling method in §7 · DAMA-DMBOK 2.0 Ch. 8 §2.5
traces_to: >
  PGD-000 MG-004 · BRD MIG-004, MIG-006, MIG-013 · 05-02 §12 MIG-04 · DM-013 RV-01…RV-12 ·
  06-02 gates G1-05, G2-06, G2-07, G3-08, G5-01 · GV-009 evidence classes E4, E7 ·
  AUDIT-011 DM-09 · M19, M20, M51, M56 §16.4
depends_on: MG-001 · MG-002 · MG-003 · DM-011 · DM-013 · DA-006 · GV-009 · SC-010
verified_on: 2026-08-18
priority: P0
needed_by: W1
enumeration_timestamp: 2026-08-18 22:45 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# MG-004 — Reconciliation and Validation Plan

### Category 09 · Code `MG` · ISO 8000-61:2016 · ISO/IEC/IEEE 29119-3:2021 · ISA 530

---

> **Local rule prefix: `RVP-nn`.** Verified unused workspace-wide at 2026-08-18 22:45 (+06).

---

## 1. Purpose

`DM-013` is a strong 32 KB specification of a **reconciliation report** — five classes `R1`–`R5`,
nine exception categories `E1`–`E9`, per-domain control totals, acceptance thresholds, a report
structure and a sign-off form. Its register status is ◐: *"specifies the reconciliation report
format. Financial migration without a reconciliation plan is an unauditable opening balance."*

**The distinction the register draws is the right one.** A report format tells you what a
reconciliation looks like. It does not tell you:

| Question | Answered by `DM-013`? |
|---|:--:|
| Who **prepares** a reconciliation and who **approves** it, and may they be the same person? | ✘ |
| Where a control total **comes from**, and when it is frozen so it cannot be reverse-engineered from the result | ✘ |
| **How large** an `R5` sample must be for its result to mean anything | ✘ |
| Who checks the checker — what is **independently verified**, by whom | ✘ |
| What the **evidence pack** contains, where it lives, how long it is kept | ✘ |
| How the evidence reaches a **wave gate**, and in what form | ✘ |
| What happens when a reconciliation **fails at 03:00** | ✘ |
| Who **drains** the exception queues, at what rate, before which date | ✘ |

This document answers those eight questions. It changes nothing in `DM-013` (`MST-01`).

### 1.1 Why the register calls this P0

`06-02` makes migration reconciliation a gate criterion at **four of nine gates**, and `G3-08`
carries the CFO's **non-delegable** signature. BRD `MIG-013` requires financial history reconciled
**to the trial balance** before Gate 3. `M19` §16.4 requires one full parallel month-end close
reconciled line by line and signed before the legacy accounting system is retired.

> **An opening balance that cannot be evidenced is an opening balance that cannot be audited**, and
> 1000FiX carries statutory VAT obligations and an ISO 9001:2015 certification that both assume
> record integrity. This is the document that makes the evidence exist.

### 1.2 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | The reconciliation operating model and **segregation of duties** (§3) |
| 2 | Control-total derivation, declaration and freezing (§4) |
| 3 | The execution schedule — what is reconciled, when, per tier and wave (§5) |
| 4 | **The evidence pack**: composition, integrity, retention, gate submission (§6) |
| 5 | The `R5` semantic sampling method and sample sizes (§7) |
| 6 | Independent verification: external auditor, tax consultant, second-person check (§8) |
| 7 | Exception-queue governance and drain rates (§9) |
| 8 | Gate binding and the conditional-pass procedure (§10) |
| 9 | Failure handling and the interface to fallback (§11) |
| 10 | Rules `RVP-01`…`RVP-33` (§12) |

**Explicitly out of scope**

| Topic | Owned by |
|---|---|
| The report **format**, classes `R1`–`R5`, exceptions `E1`–`E9`, the sign-off wording | **`DM-013`** — adopted whole |
| Per-domain control totals and their tolerances | **`DM-013`** §2.3, §2.5 — adopted; §4 states how they are *derived* |
| Quality rules that produce `R4` results | `DM-011` |
| Pipeline execution and `ctl_xref` | **`MG-003`** |
| Rehearsal-time reconciliation | **`MG-005`** — same plan, different environment |
| Post-go-live quality scorecard | `RP-016`, `DA-008` |
| Gate procedure generally | `GV-009` |

### 1.3 Intended audience

| Audience | Use |
|---|---|
| **CFO** | §4 finance control totals; §8 the auditor's role; §10 `G3-08` |
| **Domain signatories** (CCO, Service Ops Director, Warehouse Manager, HR Director, Finance Director) | §3.2 what they are signing; §7 what inspection they must personally do |
| **QA Lead** | The whole document — the S4 assurance stream |
| **Data Migration Lead** | §5 schedule; §11 failure interface |
| **External auditor / tax consultant** | §8 |
| **Wave gate assessors** (`GV-009`) | §6 evidence pack; §10 |

---

## 2. Basis

### 2.1 Standards conformance

| Standard | Clause | Conformance | Departure |
|---|---|---|---|
| **ISO 8000-61:2016** | 7.4 Data quality **assurance** | This document is the assurance process for migration; `MG-003` §9/§12 is the control process | — |
| **ISO/IEC/IEEE 29119-3:2021** | Test completion report structure | §6 evidence pack borrows the completion-report discipline: what was executed, what passed, what remains, who accepted | 29119 governs testing. Migration reconciliation is not testing, and the departure is that **the signatory is a business owner, not a test manager** |
| **ISA 530** — audit sampling | Attribute sampling; sample size as a function of population, expected deviation and required confidence | §7 sample sizes are derived on this basis and the basis is stated | ISA 530 governs statutory audit. Used here as a **defensible method**, not a claim of audit compliance |
| **ISA 500** — audit evidence | Sufficiency, relevance, reliability; evidence from an independent external source is more reliable | §8 — why the bank statement outranks the book balance, and why the auditor countersigns the TB | — |
| **DAMA-DMBOK 2.0** | Ch. 8 §2.5 — validating data after integration | §5 schedule | — |
| `05-02` `MIG-04`; BRD `MIG-006` | Control totals signed by the business owner before cutover | §3.2, §6 | — |

### 2.2 Why an audit-sampling basis, and what it is not

`DM-013` `RV-03` correctly makes `R5` semantic inspection **mandatory** and notes that it *"cannot be
fully automated"*. It does not state a sample size.

**A sample of unstated size is not evidence.** "The business owner looked at some records and they
seemed fine" cannot be submitted to a gate, cannot be repeated, and cannot be compared between
waves. ISA 530's attribute-sampling logic gives a defensible, explainable basis: **for a population
of this size, a sample of this size with zero defects supports a statement that the defect rate is
below this level, at this confidence.**

> **`RVP-01` — this is a method, not a compliance claim.** 1000FiX is not conducting a statutory
> audit of its own migration. It is borrowing a well-understood sampling method so that a sample
> size is a decision with a rationale rather than a number someone liked. The external auditor's
> own procedures at `G3-08` are theirs to determine (§8.2).

---

## 3. The Reconciliation Operating Model

### 3.1 Four roles, and why they cannot collapse into two

| Role | Does | May **not** also be |
|---|---|---|
| **Preparer** | Runs the reconciliation, produces the `DM-013` report | The Approver |
| **Reviewer** | Checks the report is complete, arithmetically sound, and that no class is silently absent | The Preparer |
| **Approver** (domain signatory) | Signs the `RV-11` statement, accepting the data | The Preparer |
| **Independent verifier** | External auditor, tax consultant, or a named second person outside the migration team | Any of the above |

> **`RVP-02` — the person who ran the load may not approve its reconciliation.** This is the most
> commonly waived control in migration work, always for the same reason: at 03:00 on a cutover
> night the only person awake who understands the numbers is the one who produced them. §11.2 makes
> that situation a **planned** one rather than an improvised one.

### 3.2 Who signs what

Adopted unchanged from `DM-013` §2.7 under `MST-01`, with the preparer/reviewer split added.

| Domain | Preparer | Reviewer | **Approver** | Countersignatory |
|---|---|---|---|---|
| Party, address, contracts, claims | Migration analyst | QA Lead | **Chief Commercial Officer** | Master Data Owner |
| Asset, service history, archive | Migration analyst | QA Lead | **Service Ops Director** | Master Data Owner |
| Inventory | Migration analyst | QA Lead | **Warehouse Manager** | CFO *(valuation)* |
| Finance — all | Migration analyst | **Financial Controller** | **CFO** | **External auditor** *(trial balance)* |
| Tax | Migration analyst | Financial Controller | **CFO** | **Tax consultant** |
| People and payroll | Migration analyst | HR Manager | **HR Director** | **CFO** |
| Configuration, credentials | Migration analyst | Security Lead | **CTO** | — |

> **`RVP-03` — an approver who cannot explain what they are signing has not approved it.** The
> `RV-11` statement is deliberately written in the first person and in business language for this
> reason. §7.4 requires the approver, or a nominee they name, to have **personally inspected** the
> `R5` sample.

### 3.3 Cadence

| When | What | Environment |
|---|---|---|
| Every pipeline run | `R1`, `R3`, `R4` computed automatically | Any |
| Every rehearsal | **Full `R1`–`R5`, identical format to production** (`RV-10`) | Rehearsal |
| Every production tier load | Full `R1`–`R5`; report per tier | Production |
| Before the go decision | **All applicable sign-offs complete** — checkpoint `C6` | Production |
| Daily through the parallel run | Comparison reconciliation between the two systems | Both |
| At parallel-run exit | Finance: **one full parallel close reconciled line by line** | Production |
| At the wave gate | Evidence pack submitted (§6) | — |

---

## 4. Control Totals

### 4.1 The derivation rule

**`RVP-04`: a control total is derived from the source, independently of the pipeline, before the
first load, and frozen.**

Four properties, each preventing a specific failure:

| Property | Prevents |
|---|---|
| **From the source** | A total computed from the load's own output, which reconciles to itself by construction |
| **Independently of the pipeline** | A total computed by the same code that did the transformation, which cannot detect that code being wrong |
| **Before the first load** | A total chosen after the result is known — the defect `DQ-05` and `MST-10` forbid |
| **Frozen** | A total quietly adjusted to make a variance disappear |

> **`RVP-05` — "independently" means a different code path, not a different person running the same
> script.** The preferred implementation is a **direct query against Z1/Z2** (the landed and raw
> zones) written separately from the transformation, and where the source permits it, a
> **custodian-supplied figure** — the branch's own stock count, the bank's own statement, the
> accountant's own trial balance.

### 4.2 Where each domain's totals come from

| Domain | Authoritative source of the total | Why not our record |
|---|---|---|
| **GL / trial balance** | The **CFO-signed, auditor-agreed** trial balance | `M19` §16.4; a book balance is our assertion, the agreed TB is evidence |
| **Bank balances** | **The bank's own statement** | `M50` §16.4: *"bank balances come from the bank's statement, never the legacy book balance"* |
| **Cash** | The **witnessed physical count** | `M50`; disposition `C` |
| **Inventory** | The **witnessed physical count**, not the spreadsheet | `M15`; the spreadsheet is 75% accurate and its variance is the reported baseline |
| **Consignment stock** | **Written brand confirmation**, 17+ brands | `M15`, `DM-007` `IV-05` |
| **AR open items** | Control account **plus** written confirmation of the **top 50 customer balances** | `M20` §16.4 |
| **Tax — input credit** | The **last filed Mushak 9.1** | `M51`; `FO-13` |
| **Tax — Mushak 6.3 sequence** | The last issued number, **agreed with the tax consultant** | `M51`: *"cannot be corrected afterwards"* |
| **Payroll YTD** | Payslips and statutory returns, **per employee** | `M56`; exact per employee |
| **Leave balances** | **Agreed with each employee** before cutover | `M55` |
| **Fixed assets** | Physical verification, with **tax-book WDV agreed with the tax consultant** | `M49`, `DM-003` W5 step 9 |
| **Party, asset, service history, contracts** | Z1/Z2 counts from the `MG-002` extract manifests | The manifest `record_count` is the R1 denominator |

> **`RVP-06`.** Eight of the twelve authoritative totals above come from **outside the programme** —
> a bank, a brand, a customer, an employee, an auditor, a tax consultant, or a physical count.
> Obtaining them has a **lead time measured in weeks**, and none of them is currently scheduled.
> This is the same shape as `AUDIT-011` `DM-05` and it is recorded here as `Q-01`.

### 4.3 The control register

**`RVP-07`: every control total is registered before its first load** in
`MG-004_Reconciliation_Control_Register.csv` — the register `DM-013` `RV-05` names and nobody has
created.

| Column | Purpose |
|---|---|
| `control_id` | `CT-<domain>-<nn>` |
| `domain`, `wave`, `tier` | Scope |
| `measure` | What is being totalled |
| `authoritative_source` | §4.2 |
| `source_obtained_by`, `obtained_on` | Provenance and date |
| `declared_value` | The frozen figure |
| `tolerance_tier` | `MG-001` §8.2: T-EXACT / T-ZERO-UNACCOUNTED / T-DECLARED / T-REPORTED / T-NONE |
| `tolerance_value` | Where T-DECLARED |
| `set_by`, `set_on` | The accountable owner and date (`RV-08`) |
| `frozen` | Boolean; **once true, changes require a recorded change, not an edit** |

---

## 5. The Reconciliation Schedule

### 5.1 Per tier — what applies

`RV-01` requires all five classes that apply, with non-application stated. This table settles
applicability once so it is not re-argued per load.

| Tier | `R1` | `R2` | `R3` | `R4` | `R5` | Notes |
|:--:|:--:|:--:|:--:|:--:|:--:|---|
| `X0` control | ✔ | — | ✔ | ✔ | — | `R2` n/a — no value column; `R5` n/a — control data |
| `X1` party | ✔ | ✔ *(counts)* | ✔ | ✔ | ✔ | `R2` on counts by type/segment, not on money |
| `X2` party dependants | ✔ | ✔ | ✔ | ✔ | ✔ | Includes the **residency hold count** (`E4`) |
| `X3` asset | ✔ | ✔ | ✔ | ✔ | ✔ | `R2` includes the **confidence split**, never summarised |
| `X4` commercial | ✔ | ✔ | ✔ | ✔ | ✔ | `R2` includes the evidence-rung split |
| `X5` service | ✔ | ✔ | ✔ | ✔ | ✔ | |
| `X6` inventory | ✔ | ✔ | ✔ | ✔ | ✔ | `R2` from the **count**, plus the spreadsheet variance |
| `X7` finance | ✔ | **✔ T-EXACT** | ✔ | ✔ | ✔ | Debits = credits; control accounts; **no tolerance** |
| `X8` people | ✔ | **✔ T-EXACT** | ✔ | ✔ | ✔ | YTD **per employee** |
| `X9` archive | ✔ | ✔ *(counts)* | ✔ | — | ✔ *(retrievability sample)* | `R4` n/a — archive records are excluded from operational rules by design |

### 5.2 Per wave — the additional cross-workbook reconciliations

`DM-013` §2.8 declares seven cross-workbook reconciliations (`X1`–`X7`) that *"belong to neither
workbook alone"*. **`RVP-08`: each is scheduled explicitly in the wave it becomes computable**, with
a named owner, because a reconciliation that is nobody's is nobody's.

| # | Reconciliation | Computable at | Owner |
|:--:|---|:--:|---|
| `X1` | Opening stock value → stock control account | **W3** (needs both W2 stock and W3 GL) | Financial Controller |
| `X2` | Live claims → AR open items | W4 | Finance Director |
| `X3` | Consignment balances ↔ claim-side consignment | W2/W4 | Warehouse Manager |
| `X4` | Deferred revenue → contract population | W4 | Financial Controller |
| `X5` | Employee party ↔ employee record — **one party, added role** | W5 | Master Data Owner |
| `X6` | Asset ↔ order — provisional share reported | W1/W2 | Service Ops Director |
| `X7` | Physically verified asset register ↔ accounting opening values | W5 | CFO |

> **`X1`, `X2` and `X7` cross a wave boundary.** They cannot be completed at the wave that produces
> their first half. `RVP-09`: **a cross-wave reconciliation is an open item on the earlier wave's
> gate**, listed by name with its completion wave — not silently deferred.

### 5.3 The parallel-run comparison

| Element | Specification |
|---|---|
| Frequency | **Daily**, through the two-week parallel run (`CV-19`) |
| Measures | A declared set per domain — transaction counts, values, state distributions |
| Primacy | **The new system is the system of record from the go decision.** The comparison detects divergence; it does not arbitrate |
| Divergence handling | Every difference is explained or raised; **an unexplained difference blocks `C8` parallel-run exit** |
| Finance addition | **One full parallel month-end close**, reconciled line by line and signed (`M19`) |
| Reported to | Change Lead daily; CFO for finance |

> **`RVP-10` — a parallel run with no daily comparison is two systems running, not a parallel run.**
> `DM-014` §4.8 already requires the comparison; this document makes the divergence-blocks-exit rule
> explicit, because "we ran both for two weeks" is otherwise the whole of the evidence.

---

## 6. The Evidence Pack

### 6.1 Why it exists

`GV-009` classes migration gate evidence as **`E7`** (control totals / reconciliation) and **`E4`**
(signature). `MG-001` `MST-18` states that a gate criterion is satisfied by an evidence pack, not by
a status report. **`RVP-11`: the evidence pack is a defined, versioned, retained artefact with a
manifest**, assembled per domain per wave.

### 6.2 Composition

| # | Item | Source |
|:--:|---|---|
| 1 | The signed `DM-013` reconciliation report, all ten sections | `MG-003` run + this plan |
| 2 | The **frozen control register extract** for that domain and wave | §4.3 |
| 3 | The **extract manifests** for every source contributing (`extract_id`, count, hash) | `MG-002` §7.2 |
| 4 | The **batch and run records** (`ctl_batch`, `ctl_run`) | `MG-003` §8.2 |
| 5 | The **`R5` sample**: sample list, inspector, findings, Bengali render result | §7 |
| 6 | The **exception schedule**: `E1`–`E9` counts with owners and dates | §9 |
| 7 | **Independent verification evidence** where applicable — auditor letter, tax consultant confirmation, bank statement, brand confirmation, customer confirmations | §8 |
| 8 | The **rehearsal report** for the same tier, with measured durations | `MG-005` |
| 9 | The **signed `RV-11` form**, with countersignature | §3.2 |
| 10 | A **manifest hash** over items 1–9 | §6.3 |

### 6.3 Integrity and retention

| # | Rule |
|---|---|
| `RVP-12` | The pack is assembled once, hashed, and filed as an `M24` document. Items are not added afterwards; a correction produces **pack version 2** with both retained |
| `RVP-13` | Retention: **seven years for finance, tax, payroll and statutory domains** (`FO-15`, `NFR-088`, `DA-006`); the domain's retention class otherwise. `RV-12` already requires this for the signed form; it extends to the whole pack |
| `RVP-14` | The pack is retained **independently of the staging schema**, which is destroyed at parallel-run exit (`ETR-09`). Evidence must outlive the environment that produced it |
| `RVP-15` | Access to packs containing personal data is controlled and logged (`SC-010`); `R5` sample listings carry **record identifiers, not record contents** |

> **`RVP-14` is easy to get wrong and expensive to discover.** If the evidence for the W1 opening
> position lives in the W1 staging database, and that database is destroyed at parallel-run exit as
> `MST-16` requires, then in year three there is a trial balance nobody can substantiate.

### 6.4 Gate submission

**`RVP-16`: the pack is submitted to the wave gate as a single referenced artefact**, and the gate
assessor's check is that (a) the pack exists, (b) its manifest hash verifies, (c) every applicable
class is present or its non-application stated, and (d) the signatures are the ones §3.2 requires.
**The assessor does not re-perform the reconciliation.**

---

## 7. The `R5` Semantic Sample

### 7.1 Why the sample size has to be stated

`DM-013` `RV-03` names `R5` as *"the class that catches the errors the others cannot"* — every record
loading against the wrong parent, every date shifting by a month, every status mapping to the wrong
state — and notes it is *"the class most often dropped, because it cannot be fully automated"*.

An unstated sample size is how it gets dropped in practice: the owner looks at ten records, they are
fine, and the load is accepted.

### 7.2 The method

Attribute sampling on the ISA 530 basis. **The question the sample answers is: *"if the true defect
rate were above X%, how likely is it that a sample of size n would contain zero defects?"***

For zero expected deviations, the sample size for a given confidence and tolerable rate follows the
Poisson approximation `n ≈ −ln(1 − confidence) / tolerable_rate`. At 95% confidence, `−ln(0.05) ≈ 3`,
giving `n ≈ 3 / tolerable_rate`.

| Tolerable defect rate | Confidence | Sample size (zero defects expected) |
|---:|---:|---:|
| 10% | 95% | **30** |
| 5% | 95% | **59** |
| 2% | 95% | **149** |
| 1% | 95% | **299** |
| 5% | 90% | **45** |
| 2% | 99% | **228** |

> **`RVP-17` — the sample size is derived from the tolerable rate the owner chooses, and the owner
> is told what the number means.** Not *"inspect 60 records"* but *"inspecting 59 records and
> finding no defect supports a statement that fewer than 5% of records carry a semantic defect, at
> 95% confidence."* An owner who understands that will sometimes ask for a bigger sample, which is
> the point.

### 7.3 Sample sizes by domain

**`RVP-18`: these are the minima. A domain owner may increase them; nobody may decrease them.**

| Domain | Tolerable rate | Confidence | Minimum sample | Rationale |
|---|---:|---:|---:|---|
| **Finance — GL, AR/AP, cash, bank, tax** | **1%** | 95% | **299**, or **100% where the population is below 299** | T-EXACT domains; `M51` — uncorrectable afterwards |
| **Payroll YTD** | — | — | **100% of employees** | `M56`: exact **per employee**. There is no sampling of a per-employee exactness requirement |
| Party / customer | 2% | 95% | **149** | 100,000+ population; the PDPA merge exposure |
| Asset / device | 2% | 95% | **149** | Population unknown to a factor of two |
| Service history — live | 5% | 95% | **59** | |
| Contracts, warranty, claims | 2% | 95% | **149** | Entitlement errors are money |
| Inventory | 5% | 95% | **59** | Backed by a physical count, which is itself the control |
| Archive (`X9`) | 10% | 95% | **30** | Retrievability check only; excluded from operational logic |
| Configuration / credentials | — | — | **100%** | Small populations; security-bearing |

### 7.4 Stratification and who inspects

| # | Rule |
|---|---|
| `RVP-19` | The sample is **stratified**: by source, by transformation-rule class, by target state, and **by exception-adjacent population** — records that *nearly* failed a rule are over-represented deliberately |
| `RVP-20` | The sample is **drawn by the Reviewer, not the Preparer**, from `ctl_xref`, and the draw is recorded with its seed so it is reproducible |
| `RVP-21` | Inspection is **end-to-end**: the inspector reads the target record and its source record and states whether it still means the same thing. Not a field-by-field diff — that is `R1`–`R4`'s job |
| `RVP-22` | The inspector is **the domain owner or a nominee they name in writing** (`RV-04`). Never the migration team |
| `RVP-23` | A **Bengali render check** on a sample of Bengali-bearing fields is performed by a **native speaker**; zero mojibake tolerated (`RV-03`) |
| `RVP-24` | **Any semantic defect fails the load** (`RV-03`, `E9`), whatever the sample size. There is no "one in fifty-nine is acceptable" — the sample size bounds the *unobserved* rate, it does not license observed defects |
| `RVP-25` | A **round-trip check** on 10% of the sample: take the loaded record, find its source by `legacy_record_id`, compare field by field. 100% match required on mapped fields |

> **`RVP-24` is the rule most likely to be argued with at 03:00.** The sample exists to detect a
> systematic defect. One observed semantic defect in a stratified sample is evidence of a class of
> defect, not of one unlucky record, and `E9` triggers fallback `T3` for that reason.

---

## 8. Independent Verification

### 8.1 What must be verified by someone outside the programme

ISA 500's reliability hierarchy is the reasoning: evidence from an independent external source is
more reliable than evidence generated internally.

| # | Item | Verifier | State today |
|:--:|---|---|---|
| 1 | The **opening trial balance** | **External auditor** — countersigns (`DM-013` §2.7) | **Not engaged** |
| 2 | **Bank balances and reconciling items** | The **bank's own statement** | Obtainable; not scheduled |
| 3 | **Mushak 6.3 sequence position** and opening input VAT credit | **Tax consultant**, agreed and recorded | **Not engaged** — `AUDIT-011` `DM-09` |
| 4 | **Payroll tax slabs** (`MD-043`) and **VAT rates** (`MD-037`) | **Tax adviser**, `verified_by`/`verified_on` at gate `G6` | **Not engaged** — `AUDIT-011` `DM-09` |
| 5 | **Consignment balances** | **17+ brand partners**, in writing | Not scheduled |
| 6 | **Top-50 AR customer balances** | **The customers**, in writing (`M20`) | Not scheduled |
| 7 | **Leave balances** | **Each employee**, agreed before cutover (`M55`) | Not scheduled |
| 8 | **Fixed-asset tax-book WDV** | **Tax consultant** | **Not engaged** |
| 9 | **Physical counts** (stock, cash, assets) | **Witnessed and signed** by two counters plus the branch manager | Count programme unresourced (`MG-001` `Q-02`) |

> **`RVP-26` — every item above has a lead time and none of them is scheduled.** Items 3, 4 and 8
> depend on a tax adviser `AUDIT-011` `DM-09` records as unengaged, with a **three-month lead time**,
> against a W3 load and a W5 payroll. Item 1 depends on an auditor whose engagement letter must
> cover a migration opening balance, which is not a standard engagement scope. **This is the single
> largest schedule exposure in this document** and it is recorded as `Q-01`.

### 8.2 What the auditor is and is not being asked

Stating this prevents a late and expensive misunderstanding.

| The auditor **is** asked to | The auditor is **not** asked to |
|---|---|
| Agree the opening trial balance figures used as the migration input | Audit the migration |
| Countersign that the loaded GL agrees to that trial balance | Certify the ERP |
| Confirm the basis is consistent with the prior period's audited position | Take responsibility for data quality in non-financial domains |

> **`RVP-27`.** The auditor's engagement for this purpose is agreed **in writing, in advance**, with
> its scope stated as above. `G3-08` is a CFO signature countersigned by the auditor; an auditor
> asked to countersign at the gate without a prior engagement will decline, correctly, and `G3-08`
> will fail on a procedural point after all the technical work is done.

---

## 9. Exception Governance

### 9.1 Each category has an owner, a queue and a drain rate

`DM-013` `RV-06` requires every non-loading record to be in exactly one category with an owner and a
disposition. **`RVP-28` adds the missing element: a drain rate and a date.**

| Cat | Owner of the queue | Drain expectation | Blocks the gate? |
|:--:|---|---|:--:|
| `E1` blocking rule | Domain owner with the migration analyst | Cleared or accepted **before the gate** | **Yes, above tolerance** |
| `E2` referential | Migration Engineering | Usually a sequencing defect — **fixed, then re-run**, not accepted | **Yes** |
| `E3` evidence hold | Domain owner | A dated business follow-up with a **published burn-down** | No — count reported |
| `E4` residency hold | Head of InfoSec with the domain owner | Cleared by the pass-2 load once `CD-233` is verified | No — count reported |
| `E5` excluded by disposition | — | Nothing to drain; **reported so absence is visible** (`RV-07`) | No |
| `E6` quarantine | Warehouse Manager (stewardship) | Burn-down with a rate | No — reported |
| `E7` merged | Master Data Owner | Reversible through the burn-down window only (`ETR-39`) | No — headline figure |
| `E8` unresolved duplicate | Master Data Owner | **Zero at the wave gate** — the queue must be drained (`DQ-22`) | **Yes** |
| `E9` semantic defect | QA Lead | **Not drained — rollback** (`RV-03`, `T3`) | **Yes, always** |

### 9.2 The queue nobody has sized

**`E8` must reach zero at the wave gate**, and its size is unknown because the match thresholds are
unset and their queue was never computed (`AUDIT-011` `DM-04`; `DQ-16`).

> `DM-011` §7 states the arithmetic without inventing the input: a 15% duplicate rate on 100,000
> parties, with a third of candidate pairs in the review band, is **thousands of human decisions,
> each requiring someone who can recognise a customer**.

**`RVP-29`: the `E8` queue is sized from `MG-002`'s P3 candidate count at three candidate thresholds,
priced in reviewer-days, and accepted by the CCO before a threshold is set** (`DQ-16`). A threshold
chosen without pricing its queue is a threshold that will be raised at the last minute to make the
queue disappear — which is a decision to accept false merges, taken silently, on a population of
100,000 people, under a statute that treats a false merge as a personal-data incident.

---

## 10. Gate Binding

### 10.1 The four migration gate criteria and their evidence

| Gate | Criterion | Evidence pack contents that satisfy it |
|:--:|---|---|
| `G1-05` | Customer and device data migrated and reconciled | Party + asset packs: `R1` zero-unaccounted, `R2` counts, `R5` sample (149 each), CCO and Service Ops Director signatures |
| `G2-06` | Inventory accuracy ≥ 95% at migrated locations, verified by count | Inventory pack: witnessed count sheets, count-vs-spreadsheet variance, Warehouse Manager signature, CFO countersignature |
| `G2-07` | Van stock reconciling daily, variance < 2% | Parallel-run daily comparison record over the declared period |
| `G3-08` | Financial history migrated and reconciled to the trial balance | Finance pack: T-EXACT `R2`, auditor-agreed TB, bank statements, **CFO signature (non-delegable) + auditor countersignature** |
| `G5-01` | First payroll run processed, validated and paid with zero errors | People pack: 100% YTD verification, HR Director + CFO signatures, first-run payslip agreement |

### 10.2 Conditional pass — when it is available and when it is not

`DM-013` `RV-09` gives three outcomes: pass, conditional pass with a dated remediation plan, or
fail. `MG-001` `MST-20` restricts where a conditional pass is available.

| Tolerance tier | Conditional pass available? |
|---|:--:|
| T-EXACT | **No** |
| T-ZERO-UNACCOUNTED | **No** |
| T-DECLARED | Yes, with a dated remediation plan and a named owner |
| T-REPORTED | Yes |
| T-NONE | n/a |

> **`RVP-30`.** A conditional pass carries a **date, an owner and a specific remediation**, and is
> reviewed at the next gate. A conditional pass with no closure date is a fail that has been
> described politely. `GV-009`'s partial-pass convention applies.

---

## 11. When a Reconciliation Fails

### 11.1 The interface to fallback

Four of `DM-014`'s seven fallback triggers read this document's output:

| Trigger | Fires when | This document's role |
|:--:|---|---|
| `T1` | `R1` cannot balance — records unaccounted | §5.1; `ctl_xref` makes it computable |
| `T2` | A finance T-EXACT control does not tie | §4.2, §5.1 |
| `T3` | An `E9` semantic defect is found | §7 — the sample that finds it |
| `T5` | A domain owner **declines to sign** | §3.2, §6 |

> **`RVP-31` — a trigger fires on the finding, not on a judgement about the finding.** `MG-001`
> `MST-09` establishes that the go/no-go authority may not override a trigger. This document adds
> the operational corollary: **the Preparer reports the finding as found**, and the assessment of
> what it means happens afterwards, in the fallback process, not before, in the report.

### 11.2 The 03:00 problem, planned rather than improvised

The failure mode `RVP-02` guards against is real and predictable: at the moment a reconciliation
fails, the people qualified to interpret it are tired, few, and have just done the work being
questioned.

| # | Provision |
|:--:|---|
| 1 | Every cutover names a **Reviewer on shift** who did not run the load (`MG-006` §4 command roles) |
| 2 | Every domain names an **approver and a nominated deputy**, both briefed, before the freeze |
| 3 | `RVP-24` and `RVP-31` are stated in the runsheet at the checkpoint, not only in this document |
| 4 | The `C6` checkpoint has a **declared minimum duration** so that "sign here" is not the last item before a deadline |

### 11.3 Re-run and re-reconcile

| Situation | Action |
|---|---|
| `E2` referential rejects from a sequencing defect | Fix, re-run the tier, **produce a new report with a new run id**. The prior report is retained, not replaced |
| `E1` above tolerance | Remediate at source or in Z3, re-run |
| `E9` semantic defect | **Roll back the tier** (`MG-007`), fix the transformation rule and its test, re-rehearse, re-run |
| A control total was wrong | **A recorded change to the frozen register**, with the reason and the approver — never a silent edit (`RVP-04`) |

---

## 12. Governing Rules

> Class: **H** hard block · **A** approved override · **S** soft warning · **C** computed.

| # | Rule | Class |
|---|---|:--:|
| `RVP-01` | The sampling basis is a stated method, not a compliance claim | **C** |
| `RVP-02` | The person who ran the load may not approve its reconciliation | **H** |
| `RVP-03` | An approver signs a statement they can explain; the `R5` inspection is theirs or a named nominee's | **H** |
| `RVP-04` | A control total is derived from the source, independently of the pipeline, before the first load, and frozen | **H** |
| `RVP-05` | "Independently" means a different code path or an external supplier of the figure | **H** |
| `RVP-06` | External control totals are obtained on a scheduled lead time, not requested at cutover | **H** |
| `RVP-07` | Every control total is registered before its first load in the control register | **H** |
| `RVP-08` | Each `DM-013` §2.8 cross-workbook reconciliation is scheduled with a named owner | **H** |
| `RVP-09` | A cross-wave reconciliation is a named open item on the earlier gate | **H** |
| `RVP-10` | The parallel run has a daily comparison; unexplained divergence blocks `C8` | **H** |
| `RVP-11` | The evidence pack is a defined, versioned, retained artefact with a manifest | **H** |
| `RVP-12` | A pack is assembled once and hashed; corrections produce a new version | **H** |
| `RVP-13` | Seven-year retention for finance, tax, payroll and statutory packs | **H** |
| `RVP-14` | Packs are retained independently of the staging schema | **H** |
| `RVP-15` | Sample listings carry identifiers, not contents; pack access is logged | **H** |
| `RVP-16` | The gate assessor verifies the pack; they do not re-perform the reconciliation | **C** |
| `RVP-17` | Sample size is derived from a tolerable rate the owner chooses and understands | **H** |
| `RVP-18` | The §7.3 sample minima may be increased, never decreased | **H** |
| `RVP-19` | Samples are stratified, including deliberate over-representation of near-failures | **H** |
| `RVP-20` | The sample is drawn by the Reviewer, reproducibly, with a recorded seed | **H** |
| `RVP-21` | Inspection is end-to-end meaning, not a field diff | **H** |
| `RVP-22` | The inspector is the domain owner or a written nominee, never the migration team | **H** |
| `RVP-23` | A native Bengali speaker performs the render check; zero mojibake | **H** |
| `RVP-24` | Any observed semantic defect fails the load, whatever the sample size | **H** |
| `RVP-25` | A round-trip check covers 10% of the sample at 100% field match | **H** |
| `RVP-26` | Every external verification has a scheduled lead time and a named engagement | **H** |
| `RVP-27` | The auditor's scope for the opening balance is agreed in writing in advance | **H** |
| `RVP-28` | Every exception category has an owner, a queue, a drain rate and a date | **H** |
| `RVP-29` | The `E8` queue is sized and priced before a match threshold is set | **H** |
| `RVP-30` | A conditional pass carries a date, an owner and a specific remediation | **H** |
| `RVP-31` | A trigger fires on the finding; interpretation happens afterwards | **H** |
| `RVP-32` | Every reconciliation, in every environment, uses this plan and the `DM-013` format unchanged | **H** |
| `RVP-33` | A re-run produces a new report with a new run id; prior reports are retained | **H** |

---

## 13. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | **Who engages the external auditor and the tax consultant, and when?** Nine external verifications (§8.1), none scheduled; the tax adviser carries a three-month lead time against a W3 load | **CFO** | **W3 minus 4 months** | `G3-04`, `G3-08`, `G5-01` |
| `Q-02` | **Who obtains the 17+ brand confirmations and the top-50 customer confirmations?** Both are written external confirmations with no owner | CCO with Finance Director | **W2 / W3 minus 2 months** | `X3`; AR reconciliation |
| `Q-03` | **What is the `E8` review-queue size, and who staffs it?** Unsized since `AUDIT-011` `DM-04`; must reach **zero** at the gate | Master Data Owner with CCO | **W1 minus 2 months** | `G1-05`; every threshold decision |
| `Q-04` | **Who are the nominated deputy approvers per domain?** §11.2 requires two briefed people per domain per cutover | Data Migration Lead with each domain owner | **W1 minus 1 month** | `C6` at every cutover |
| `Q-05` | **Where do evidence packs live for seven years?** `M24` is the document module and arrives at **W3**; the first pack is needed at **W1** | Quality Manager with CTO | **W1** | `RVP-13`, `RVP-14` |

---

## 14. Decisions Recorded

| # | Decision | Options | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `MG-004-D-01` | `R5` sample sizing | Fixed count · percentage of population · **attribute sampling from a tolerable rate** | **Attribute sampling** | Gives the owner a statement they can understand and defend; scales sensibly across populations from 50 to 600,000 | Finance samples are large (299 or 100%); this is deliberate |
| `MG-004-D-02` | Payroll YTD sampling | Sample · **100% verification** | **100%** | `M56` requires exactness **per employee**; a sample cannot evidence a per-record exactness requirement | 500+ verifications at W5, which must be resourced |
| `MG-004-D-03` | Segregation of duties | Preparer may approve in exceptional circumstances · **never** | **Never** | The exception would be invoked exactly when the control matters most | A deputy approver must exist per domain (`Q-04`) |
| `MG-004-D-04` | Control-total independence | Same pipeline, different query · **separate code path or external supplier** | **Separate/external** | A total computed by the transformation cannot detect the transformation being wrong | A second, simpler implementation must be written and maintained |
| `MG-004-D-05` | Evidence pack storage | In the staging schema · in `M24` from W3 · **an interim controlled store from W1** | **Interim store from W1, migrating into `M24`** | `M24` arrives at W3; W1 evidence must be retained for seven years from W1 | An interim controlled document store is needed at W1 (`Q-05`) |

---

## 15. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | All eight questions of §1 are answered | §3–§11 |
| `AC-02` | Segregation of duties is specified and the exception path removed | §3.1; `MG-004-D-03` |
| `AC-03` | Control totals have a derivation rule and a named authoritative source per domain | §4.1, §4.2 |
| `AC-04` | The `R5` sample size has a stated statistical basis and per-domain minima | §7.2, §7.3 |
| `AC-05` | The evidence pack is enumerated, hashed and retention-bound | §6 |
| `AC-06` | Every external verification is named with its current engagement state | §8.1 |
| `AC-07` | Every exception category has an owner and a drain expectation | §9.1 |
| `AC-08` | Gate binding maps each criterion to specific pack contents | §10.1 |
| `AC-09` | The fallback interface is specified, including the authority rule | §11.1 |
| `AC-10` | No `DM-013` rule is restated | Verified at issue (`MST-01`) |

---

## 16. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `MG-001` | Tolerance hierarchy, gate binding, authority model |
| Upstream | `MG-002` | Extract manifests supply the `R1` denominator; P3 sizes the `E8` queue |
| Upstream | `MG-003` | `ctl_xref`, `ctl_batch`, `ctl_run` are the reconciliation's raw material |
| Upstream | `DM-011`, `DM-013` | Rules and report format, adopted unchanged |
| Upstream | `DA-006` | Retention classes for the evidence pack |
| Downstream | **`MG-005`** | Rehearsal produces an identical report (`RV-10`) and a measured reconciliation duration |
| Downstream | **`MG-006`** | Checkpoints `C5`, `C6` consume this plan's output |
| Downstream | **`MG-007`** | Triggers `T1`, `T2`, `T3`, `T5` read this document's findings |
| Downstream | `GV-009` | Gate evidence classes `E4` and `E7` |
| Downstream | `RL-003` ⛔ | Go-live readiness assessment consumes the evidence packs |

---

## 17. References

**Within this repository**
[`MG-001`](MG-001_Data_Migration_Strategy.md) · [`MG-002`](MG-002_Legacy_System_Profiling_and_Extract_Specification.md) ·
[`MG-003`](MG-003_ETL_Design_and_Transformation_Rules_Specification.md) · [`MG-005`](MG-005_Mock_Migration_and_Dress_Rehearsal_Plan.md) ·
[`MG-006`](MG-006_Cutover_Plan_and_Runbook.md) · [`MG-007`](MG-007_Rollback_and_Fallback_Plan.md) ·
[`../00_Programme_Governance_and_Control/GV-009_Wave_Gate_and_Phase_Exit_Criteria_Handbook.md`](../00_Programme_Governance_and_Control/GV-009_Wave_Gate_and_Phase_Exit_Criteria_Handbook.md) ·
[`../03_Data_and_Information_Architecture/DA-006_Data_Retention_Archival_and_Deletion_Design.md`](../03_Data_and_Information_Architecture/DA-006_Data_Retention_Archival_and_Deletion_Design.md)

**Workspace**
`../../project_content/12_Data_Migration_Content/DM-013_Reconciliation_and_Validation_Report_Specification.md` ·
`../../project_content/_AUDIT/AUDIT-011_Category_12_DM_Content_Audit.md` ·
`../../primary-doc/1000FiX_ERP_System_Comprehensive_BRD.md` §11.6

**External standards**

| Source | Used for | Verified |
|---|---|---|
| ISO 8000-61:2016 §7.4 | Assurance process framing | 2026-08-18 |
| ISO/IEC/IEEE 29119-3:2021 | Completion-report discipline | 2026-08-18 |
| ISA 530 — Audit Sampling | §7.2 attribute-sampling method | 2026-08-18 |
| ISA 500 — Audit Evidence | §8 reliability hierarchy | 2026-08-18 |
| DAMA-DMBOK 2.0 Ch. 8 §2.5 | Post-integration validation | 2026-08-18 |

---

## 18. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | QA Lead with the Data Migration Lead | Initial issue. Adds the governance `DM-013` could not carry: segregation of duties, control-total derivation and freezing, a stated sampling basis, the evidence pack, external verification scheduling, exception drain rates and gate binding | CFO with CTO *(pending — `GV-001` `CC-01`)* |

---

*`MG-004` · Category 09 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
