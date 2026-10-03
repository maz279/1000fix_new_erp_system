---
id: RQ-009
title: Business Rules Specification
category: 01 — Requirements Engineering
code: RQ
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Lead Business Analyst / Requirements Manager, with the Business Rule Owners named per rule
approver: ERP Design Authority
standards_basis: OMG SBVR (business vocabulary and rules concepts) · OMG DMN 1.4 (decision tables) · ISO/IEC/IEEE 29148:2018 §5.2.4–§5.2.7 · ISO 9001:2015 §4.4
traces_to: PGD-000 RQ-009 row · audit EO-02 (05-05 carries no rule for M40 or M42; six M12 rules duplicated) · 05-05 (140 rules) · module §9 (1,330 rules)
depends_on: RQ-001 (requirement set) · RQ-004 (link T-11) · RQ-005 (identifier authority) · RR-002
verified_on: 2026-08-18
priority: P0
needed_by: W1
enumerated_on: 2026-08-18 02:15 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# RQ-009 — Business Rules Specification

### Category 01 · Code `RQ` · OMG SBVR · OMG DMN 1.4 · ISO 9001:2015 §4.4

---

> **There are two business rule populations in this programme, and they are not the same
> population.** Measured at 2026-08-18 02:15 (+06):
>
> | Population | Location | Rules | Module codes covered |
> |---|---|---:|---:|
> | **The catalogue** | `05-05` Business Rules & Automation Catalogue, and BRD §10 | **140** | **20 of 67** |
> | **The estate** | Module §9 tables across 67 modules and 12 portals | **1,330** | **67 of 67** |
> | Overlap | Identifiers present in both | **122** | |
>
> The catalogue is the 30-module baseline. It still uses four module codes that no module uses —
> `BIL`, `HRM`, `SCM` and `ECM` — and it is the version the BRD and the URD cite. The estate is
> current, complete and ten times larger.
>
> **The consequence is worse than staleness.** `BRU-ECM-01` denotes *"a seller cannot transact
> until documents are verified, the agreement is digitally signed, and an administrator has
> approved"* in the catalogue, and *"on M38 the seller is always 1000FiX"* in `M38`. **Ten
> `BRU-ECM-nn` identifiers are double-allocated this way.** The first of them is the hard block
> that keeps an unverified marketplace seller out of the transaction path — a control on 500–2,000
> external parties, resolvable to two different rules depending on which document is open.

---

## 1. Purpose

A business rule is the part of a specification that says *no*. It is where the money, the
compliance exposure and the operational safety live: an invoice that cannot be raised against an
uncompleted order, a warranty job that cannot be created without active cover, a payout that
cannot be released to an unverified seller. Requirements describe capability; rules describe the
constraints that make the capability safe.

This document specifies the rule set: how a rule is written, classified, owned, implemented and
tested; how the two populations are reconciled into one; and what the classification imbalance in
the current estate implies for a system that 500+ staff will use under time pressure.

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | The **rule definition and construct** — what a rule is and how it is stated (§3) |
| 2 | The **classification scheme** `H` / `A` / `S` / `C`, with the rule that decides which applies (§4) |
| 3 | **Ownership, implementation point and enforcement layer** per rule (§5) |
| 4 | **Reconciliation** of the 140-rule catalogue and the 1,330-rule estate into one register (§6) |
| 5 | The **decision table standard** for rules too complex for a single statement (§7) |
| 6 | **Testing** — how each classification is verified, and the override audit (§8) |
| 7 | The **classification imbalance analysis** and what it implies for adoption (§9) |
| 8 | **Traceability** — link `T-11`, and the automation interface (§10) |

**Explicitly out of scope:**

| Topic | Owned by | Why |
|---|---|---|
| The rule statements themselves | Module §9 tables | The estate is authoritative on *what the rules are*. This document specifies form, classification and reconciliation |
| Automations `AUT-<CODE>-nn` | Module §11 | Related but distinct — §10.2 states the interface |
| Reference values behind rule thresholds | `MD-*` master data content | A rule cites a threshold; it does not own the value |
| Approval and delegation authority | `SP-004` | A rule's `A` classification cites it |
| Segregation of duties | `05-04`, `SP-006` | `SOD-nn` constrains role combinations, not transactions |
| Rule implementation in code | `AR-003`, `AR-007` | Design |
| Data validation rules | `DA-002` data dictionary | A field's valid-value set is a dictionary property, not a business rule |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| Business rule owners | The rules they own, and what an override costs them |
| Developers | The enforcement layer, the classification and the failure behaviour |
| QA | The test obligation per classification, including the override audit |
| Branch and operations managers | Which blocks are absolute and which have an approval path |
| Auditors, DPO, CFO | The rules that carry statutory and financial exposure |
| Change and training | The blocks staff will meet, and the reason each exists |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | How applied | Departure |
|---|---|---|
| **OMG SBVR** | Rule statements use SBVR's obligation/prohibition/permission modalities, mapped onto the programme's existing `H`/`A`/`S`/`C` classification (§4.2) | The full SBVR vocabulary formalism is **not** adopted — it is heavier than this programme can maintain. The concepts are; the notation is not |
| **OMG DMN 1.4** | Decision tables for multi-condition rules, with hit policy declared (§7) | Decision *models* are not built; tables are |
| ISO/IEC/IEEE 29148:2018 §5.2.4–5.2.7 | Rule statements use the same construct and language criteria as requirements | None |
| ISO 9001:2015 §4.4 | Rules are the "criteria and methods" element of the process approach (`RQ-007` `EX-5`) | None |

**Verified 2026-08-18.**

### 2.2 Source material relied on

| Source | Provides | Measured 02:15 (+06) |
|---|---|---|
| `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05` | The programme-wide catalogue | **140 `BRU` identifiers across 20 module codes** |
| `../../primary-doc/…BRD.md` §10 | The same 140 rules, same 20 codes | 140 |
| `.../…URD.md` | Story criteria citing rules | **132 distinct `BRU-` citations across 20 prefixes** |
| Module §9 tables, 79 specifications | The current rule estate | **1,330 unique identifiers; 67 of 67 module codes** |
| Module §11 tables | Automations | **1,373 `AUT-` rows** |
| `_MODULE_TEMPLATE` §9 | The classification scheme `H`/`A`/`S`/`C` and the owner column | Retained |
| `../../project_content/06_Process_SOP_and_Workflow/06A/SP-004` | Approval matrix and delegation of authority | Cited by every `A` rule |
| `.../SP-006` | Segregation-of-duties register | Distinguished from rules in §5.4 |

### 2.3 Audit findings this document addresses

| Finding | Source | Treatment |
|---|---|---|
| `EO-02` | Category audit | *"`05-05` carries no business rule at all for M40 or M42, and duplicates six M12 rules under a second identifier — including the hard block preventing an unverified seller from transacting."* **Confirmed and extended**: `05-05` covers 20 of 67 module codes; M40 (`PCM`, 41 rules) and M42 (`SRM2`, 27 rules) are among the 47 absent; the `BRU-ECM` collision spans **ten** identifiers, not six | §6 |
| **`RQA-27`** *(raised here)* | This document | **`BRU-ECM-01`…`BRU-ECM-10` are double-allocated** between the catalogue's M12 marketplace rules and `M38`'s e-commerce rules. A `D-3` ambiguous-link defect on a seller-verification hard block | Open — §6.3 |
| **`RQA-28`** *(raised here)* | This document | **`BRU-BIL-*` (7) and `BRU-SCM-*` (5) exist only in the catalogue** and are used by no module. They are orphaned rules under retired codes | Open — §6.4 |
| **`RQA-29`** *(raised here)* | This document | **85% of the rule estate is classified `H` hard block** — 1,134 of 1,330 — against 39 `A` approved-override rules. §9 analyses the consequence | Open — §9 |

---

# 3. What a Business Rule Is

## 3.1 Definition

**A business rule is a constraint on system behaviour that the business owns.** It states what may
not happen, what must happen first, or how a value is derived — and it does so independently of
any one requirement, because it typically constrains many.

## 3.2 What is not a business rule

| Not a rule | It is | Owner |
|---|---|---|
| *"The system shall allow a customer to book a service"* | A requirement | `RQ-001` |
| *"Phone number must be 11 digits starting 01"* | A field validation | `DA-002` data dictionary |
| *"An invoice is generated within 5 seconds of closure"* | A quality requirement | `RQ-006` |
| *"On job closure, generate the invoice"* | An automation | Module §11 `AUT-` |
| *"A finance officer may not both create and approve a payment"* | A segregation-of-duties constraint | `05-04` `SOD-nn` |
| *"Managers approve up to BDT 25,000"* | An approval threshold | `SP-004`, cited *by* rules |

**Rule `BR-01` — the ownership test.** If the constraint would still be true if the software were
replaced, it is a business rule. If it exists only because of how this system is built, it is a
design decision and belongs in `AR-004`.

## 3.3 Rule statement construct

**Rule `BR-02`.** A rule is stated in one of three forms, matching its classification:

| Form | Pattern | Use for |
|---|---|---|
| **Prohibition** | *A `<subject>` may not `<action>` `<object>` `<condition>`.* | `H`, `A` |
| **Obligation** | *A `<subject>` shall `<action>` `<object>` before `<event>`.* | `H`, `A` |
| **Derivation** | *`<value>` is computed as `<expression>` from `<inputs>`.* | `C` |

**Rule `BR-03`.** A rule states **one** constraint. A rule containing "and" joining two prohibitions
is two rules — the same singularity test the requirements carry (`RQ-001` `W-05`).

**Rule `BR-04`.** A rule's threshold is **never embedded in the statement**. It cites the `MD-nnn`
reference value or the `SP-004` matrix entry that supplies it. A rule with a number in its text
becomes wrong the first time the business changes the number, and nobody will find it.

| Not acceptable | Acceptable |
|---|---|
| *An estimate above BDT 25,000 requires branch manager approval.* | *An estimate above the branch approval threshold recorded in `MD-021` requires the approval named for that threshold in `SP-004`.* |

## 3.4 Rule record schema

```yaml
rule_id:        BRU-SRM-13
module:         M01
statement: >
  An estimate that has not received a customer decision by its expiry interval
  may not be extended; it is closed as expired and re-issued as a new estimate
  at the price current at re-issue.
classification: H                       # H | A | S | C  — §4
owner:          Service Operations Manager        # role, never a person
rationale: >
  Extending an expired estimate silently re-prices at a stale rate and is the
  largest source of margin leakage in the current operation.
enforcement:    server                  # server | database | integration | procedure
implementation: M01 state machine, transition guard estimate:sent → expired
threshold_ref:  MD-021                  # where the interval comes from
override:       none                    # H rules have none — see §4.3
requirements:   [FR-SRM-014, FR-SRM-015]          # link T-11, reciprocal
processes:      [BPM-016]
automations:    [AUT-SRM-04]
statutory:      false
test:           [TC-M01-041, TC-M01-043]
status:         Active | Superseded | Retired
```

---

# 4. Classification

## 4.1 The scheme *(retained from `_MODULE_TEMPLATE` §9)*

| Class | Name | Behaviour | Override | User experience |
|:--:|---|---|---|---|
| **`H`** | **Hard block** | The action is prevented. No role, including administrators, may complete it | **None** | An explanatory block naming the rule and the path forward |
| **`A`** | **Approved override** | Prevented for the acting role; completable by an authorised role, with a recorded reason | Named authority from `SP-004` | A request-approval flow |
| **`S`** | **Soft warning** | Permitted; the user is warned and the acknowledgement is recorded | Self, acknowledged | A warning the user may proceed past |
| **`C`** | **Computed** | The system derives the value; it is not a decision anyone makes | Not applicable | The value appears; it is not editable |

**Rule `BR-05`.** Exactly one class per rule. The estate contains four rules classified `C/A` or
`C/H`; each is two rules (a derivation and a constraint on it) and is split during reconciliation.

## 4.2 Mapping to SBVR modalities

| Class | SBVR modality | Enforcement |
|:--:|---|---|
| `H` | Necessity / impossibility | Structural — the state is unreachable |
| `A` | Obligation with dispensation | Operative, with an authorised exception |
| `S` | Advice | Guidance, recorded |
| `C` | Derivation | Definitional |

## 4.3 The classification decision

**Rule `BR-06`.** A rule is classified `H` **only** when at least one of the following holds:

| # | Test | Example |
|---|---|---|
| `CL-1` | Overriding it would breach a statute | Input VAT credit without a compliant Mushak 6.3 (`NFR-101`) |
| `CL-2` | Overriding it would create an unrecoverable financial position | Payment recorded against a cancelled invoice |
| `CL-3` | Overriding it would create a safety exposure | Uncertified technician assigned to a certification-required job (`NFR-103`) |
| `CL-4` | Overriding it would break referential or accounting integrity | Invoice raised for an order that is not Completed |
| `CL-5` | Overriding it would breach a contractual commitment to a third party | Claim submitted after the brand's window |

**Rule `BR-07` — the burden is on `H`.** A rule that meets none of `CL-1`–`CL-5` is classified `A`,
not `H`. **`H` is the exception, not the default.** §9 shows the estate has this inverted.

**Rule `BR-08` — every `A` names its authority.** An `A` rule with no named approving role is an
`H` rule that nobody has admitted to, because there is no one who can release it.

## 4.4 The override record

**Rule `BR-09`.** Every `A` override and every `S` acknowledgement writes an audit record carrying
the rule, the actor, the authorising role, the recorded reason, the timestamp and the affected
object. Override volume per rule is a **published measure** (§8.3).

**Rule `BR-10`.** A rule whose override rate exceeds the threshold in §8.3 is **reviewed, not
enforced harder**. A rule overridden in most cases is describing a business the business does not
actually run.

---

# 5. Ownership and Enforcement

## 5.1 Ownership

**Rule `BR-11`.** Every rule has exactly one owning **role**. The owner decides whether the rule
still expresses the business's intent, approves changes to it, and answers for its override rate.
The module §9 template already carries an Owner column; it is retained and made mandatory.

**Rule `BR-12`.** A rule with statutory consequence carries a **second** owner — the DPO for
personal data, the CFO for tax and financial integrity, the HSE Manager for safety. The second
owner holds a veto on relaxation.

## 5.2 Enforcement layer

**Rule `BR-13`.** Every rule declares where it is enforced.

| Layer | Use when | Caution |
|---|---|---|
| **Database** | The constraint is structural and absolute | Cannot produce a helpful message; pair with a server-layer check |
| **Server** *(default)* | Almost always | The single enforcement point that portals, apps, APIs and imports all pass through |
| **Integration** | The constraint applies at a partner boundary | Must also be enforced server-side; a partner can send anything |
| **Procedure** | The constraint cannot be systematised | **Requires a compensating detective control.** A procedural rule with no detection is an aspiration |

**Rule `BR-14` — no client-side rule enforcement.** A rule is never enforced only in a portal or a
mobile application. `SWR-009` states this as a requirement; it is repeated here because it is the
rule most often broken under delivery pressure, and because a client-enforced rule is invisible to
the API, the import path and the integration path.

## 5.3 Rules and offline operation

**Rule `BR-15`.** A field application operating offline (`SWR-030`) may **advise** on any rule but
may **enforce** none. On synchronisation the server evaluates every rule, and a rejected offline
action is returned to the technician with the rule cited.

**Rule `BR-16`.** For each `H` rule reachable from an offline workflow, the module states the
offline behaviour: warn-and-queue, or block-locally-as-advice. A rule with no stated offline
behaviour will be discovered at the first synchronisation conflict, in the field.

## 5.4 Rules distinguished from segregation of duties

A rule constrains a **transaction**; a segregation-of-duties constraint (`SOD-nn`) constrains a
**role combination**. `SOD-13`–`SOD-30` are in use and unregistered (`RQ-004` §6.1); until
`SC-004` registers them, a rule citing one cannot be verified.

---

# 6. Reconciliation

## 6.1 The two populations

| | Catalogue (`05-05`, BRD §10) | Estate (module §9) |
|---|---|---|
| Rules | **140** | **1,330** |
| Module codes | **20** | **67** |
| Baseline | 30-module (superseded) | 67-module (current) |
| Cited by | BRD, URD, BRD §13 use cases | Module specifications, `_MODULE_TEMPLATE` |
| Stale codes | `BIL`, `HRM`, `SCM`, `ECM` | none |
| Overlapping identifiers | 122 | 122 |

## 6.2 The reconciliation rule

**Rule `BR-17`.** The **module §9 estate governs**. `FOLDER_STRUCTURE.md` §9 gives the module
specifications precedence on *what the system does*, and a business rule is a statement about what
the system does. `05-05` is re-based to the estate, not the reverse.

**Rule `BR-18`.** Re-basing does **not** discard catalogue rules absent from the estate. Each is
individually dispositioned: adopted into its correct module, superseded by an estate rule, or
retired with a tombstone. A rule that quietly disappears in a re-base is a control that quietly
disappears.

## 6.3 The `BRU-ECM` collision *(finding `RQA-27`)*

**Ten identifiers denote two different rules each.**

| ID | Catalogue meaning (M12 Marketplace) | `M38` meaning (E-Commerce) |
|---|---|---|
| `BRU-ECM-01` | **A seller cannot transact until documents are verified, the agreement is digitally signed, and an administrator has approved** *(H)* | On M38 the seller is always 1000FiX; a third-party item can only be sold through M12 *(H)* |
| `BRU-ECM-02` | Only customers with a completed transaction may leave a review *(H)* | No price is computed by the storefront; every price comes from M11 *(H)* |
| `BRU-ECM-03` | Marketplace jobs are held to the same evidence, QC and warranty standards as owned jobs *(H)* | Stock is reserved at order placement, never at cart addition *(C)* |
| `BRU-ECM-04` … `-10` | Further M12 marketplace rules | Further M38 storefront rules |

**Why this is the most serious defect in the rule estate.** `BRU-ECM-01` in the catalogue is the
control that keeps an unverified seller out of the transaction path — the gate on 500–2,000
external commercial parties. It is cited by the BRD, by the URD's story criteria, and by audit
`EO-02` by name. A developer implementing "`BRU-ECM-01`" from the module estate implements a
storefront ownership rule instead. Both are real rules; only one is what the citation meant.

**Resolution — `BR-19`.** `M38` holds the `ECM` module code in the current architecture
(`05-01` §1.3 allocating `ECM` to M12 is itself superseded — `RQ-001` `RQA-08`). Therefore:

| Step | Action |
|---|---|
| 1 | **`M38` retains `BRU-ECM-nn`.** The code follows the module that owns it |
| 2 | Each catalogue `BRU-ECM-nn` marketplace rule is checked against `M12`'s 22 `BRU-MKP-nn` rules and dispositioned individually: **superseded** where an equivalent exists, **adopted** into the `BRU-MKP` space where none does |
| 3 | `BRU-ECM-01`…`-10` in their **marketplace meaning are retired** with tombstones naming their successor or their adoption identifier |
| 4 | Every citation in the BRD §10, the URD story criteria, BRD §13 use cases and `05-05` is updated. **The retirement does not close until `CT-08` returns zero live citations** (`RQ-005` `RM-17`) |

**Step 2, executed at 2026-08-18 02:15 (+06).** Each catalogue rule was compared against `M12`'s
current rule set rather than presumed absent:

| Catalogue rule | `M12` equivalent | Disposition |
|---|---|---|
| `BRU-ECM-01` seller cannot transact until verified, signed, approved | **`BRU-MKP-01`** — *"A seller cannot transact until KYC is verified, the agreement is signed and approval is granted"* | **Superseded.** The control exists |
| `BRU-ECM-02` only customers with a completed transaction may leave a review | **none found** | **Adopt** — allocate a new `BRU-MKP-nn` |
| `BRU-ECM-03` marketplace jobs held to owned-job evidence, QC and warranty standards | `BRU-MKP-02` | Superseded |
| `BRU-ECM-04` performance below threshold reduces visibility, then suspends | `BRU-MKP-06` | Superseded |
| `BRU-ECM-05` contact data limited to awarded jobs, expires after completion | `BRU-MKP-04` | Superseded |
| `BRU-ECM-06` paid boost never overrides promoted disclosure | `BRU-MKP-12`, `BRU-MKP-13` | Superseded — by two rules, correctly split |
| `BRU-ECM-07` cannot list in a category without a verified qualification | `BRU-MKP-08` addresses **broadcast**, not **listing** | **Partial — confirm or adopt** |
| `BRU-ECM-08` registration expiry suspends the seller | `BRU-MKP-21` | Superseded |
| `BRU-ECM-09` disputes decided by 1000FiX, decision and evidence recorded | `BRU-MKP-18` addresses **appeal** independence, not dispute **authority** | **Partial — confirm or adopt** |
| `BRU-ECM-10` stock cannot be sold below available quantity | `BRU-MKP-10` addresses **commingling**, not **oversell** | **Partial — confirm or adopt** |

> **Correction recorded.** The first draft of this section asserted that the seller-verification
> hard block was *"stated in the catalogue and in the BRD, and not in the module that would
> implement it"*, on the evidence that `M12` contains zero occurrences of `BRU-ECM`. **That
> conclusion was wrong**: the control exists as `BRU-MKP-01`. The search was for the identifier,
> not for the rule, and an identifier collision was mistaken for a missing control. Recorded as
> finding `RQA-33` in `_AUDIT/PGD-AUDIT-004` rather than silently corrected, because it is the
> same failure mode as `PGD-A1-03` — an absence asserted from an incomplete search.
>
> **The finding that survives is narrower and firmer:** ten identifiers are double-allocated;
> **one catalogue rule (`BRU-ECM-02`, review eligibility) has no `M12` counterpart**; and three
> more are only partially covered. Those four require disposition. The remaining six are
> superseded and their retirement is clerical.

## 6.4 Orphaned catalogue rules *(finding `RQA-28`)*

| Prefix | Rules in the catalogue | Module files using it | Disposition |
|---|---:|---:|---|
| `BRU-BIL-` | 7 | **0** | M20's code is `ARB`. Re-base to `BRU-ARB-nn`; retire `BIL` |
| `BRU-SCM-` | 5 | **0** | M16's code is `PRO`. Re-base to `BRU-PRO-nn`; retire `SCM` |
| `BRU-HRM-` | 7 | 2 files | M21's code is `HCM`. Re-base to `BRU-HCM-nn`; investigate the 2 residual citations |

These twelve-plus rules are cited by the BRD, the URD and the use cases, and are enforced by no
module. **They are controls that exist only in documents.**

## 6.5 Modules absent from the catalogue

The catalogue covers 20 of 67 module codes. Forty-seven modules — including `M40` `PCM`
(41 rules in its specification) and `M42` `SRM2` (27 rules), the two audit `EO-02` names — have no
catalogue entry at all.

**Rule `BR-20`.** Re-basing is complete when the catalogue's coverage equals the estate's: 67 of
67 module codes, 1,330 rules plus any adopted from the catalogue, with a single classification
per rule and a named owner.

## 6.6 Reconciliation sequence

| Step | Activity | Output |
|---|---|---|
| 1 | Generate the estate register from the 79 module §9 tables | 1,330 rules with module, class, owner |
| 2 | Diff the catalogue against it | 122 overlapping · 18 catalogue-only · 1,208 estate-only |
| 3 | Disposition each catalogue-only rule (`BR-18`) | Adopt / supersede / retire, each recorded |
| 4 | Resolve the `BRU-ECM` collision (`BR-19`) | 10 tombstones, 10 new `BRU-MKP-nn` |
| 5 | Re-base the orphaned prefixes (`BIL`, `SCM`, `HRM`) | Tombstones and successors |
| 6 | Split the four `C/A` and `C/H` rules | 4 → 8 |
| 7 | Populate owner, enforcement layer, threshold reference and `T-11` links | Complete records |
| 8 | Update every citation; run `CT-08` | Zero dangling references |
| 9 | Re-classify against `CL-1`–`CL-5` (§9) | A defensible `H`/`A` split |
| 10 | Publish the single register | One population |

---

# 7. Decision Tables

**Rule `BR-21`.** A rule whose outcome depends on **three or more conditions** is expressed as a
DMN 1.4 decision table, not as prose. Prose with three conditions has eight cases and states four.

| Element | Requirement |
|---|---|
| Inputs | Each named, with its data type and its source entity or `MD-nnn` |
| Output | Named, typed, with its full permitted value set |
| **Hit policy** | Declared — `U` unique, `F` first, `P` priority, `C` collect. **An undeclared hit policy is the defect that makes decision tables untrustworthy** |
| Completeness | Every input combination yields exactly one outcome under the hit policy, or a declared default |
| Reference | The table carries a `BRU-` identifier like any other rule |

**Rule `BR-22`.** `SP-033` (Diagnostic and Triage Decision Tree Library) content is expressed as
decision tables under this standard rather than as trees. A tree with an unlabelled branch is
`SP-003`'s most-cited real-world defect, and a table cannot have one.

---

# 8. Testing and Monitoring

## 8.1 Test obligation by classification

| Class | Must be tested for | Method | Level |
|:--:|---|---|---|
| `H` | The block fires; the message names the rule and the path forward; **no role can bypass it, including administrator**; it is enforced at the API and the import path, not only in the UI | Test | Integration + API |
| `A` | The block fires for the unauthorised role; the authorised role can release it; the override record is written with reason and authority | Test | Integration |
| `S` | The warning appears; the user can proceed; the acknowledgement is recorded | Test | UI |
| `C` | The derived value is correct across the boundary cases and the full input domain | Test | Unit |

**Rule `BR-23`.** Every `H` rule carries a test that attempts the prohibited action **as an
administrator**. A hard block that an administrator can bypass is an `A` rule that has not been
classified honestly.

**Rule `BR-24`.** Every `H` rule reachable through an API or a bulk import carries a test at that
entry point. UI-only tests are how client-enforced rules survive review.

## 8.2 Coverage

**Rule `BR-25`.** 100% of `H` rules are tested before their wave gate. `RQ-004` `CV-M6` treats an
untested `H` rule as an untested P0 requirement — a gate failure, not a percentage.

## 8.3 Override monitoring

| Measure | Formula | Threshold | Action on breach |
|---|---|---|---|
| Override rate per `A` rule | overrides ÷ transactions where the rule evaluated | **> 20%** | Rule owner reviews; the rule is probably wrong (`BR-10`) |
| Warning-proceed rate per `S` rule | proceeds ÷ warnings shown | **> 80%** | The warning is noise; retire it or reclassify |
| Override concentration | overrides by one role or one branch ÷ total | **> 50%** | Investigate: local practice, training gap, or an unworkable rule |
| Blocked-attempt rate per `H` rule | blocks ÷ attempts | **> 10%** | Users are routinely attempting a prohibited action — a process or training gap |

**Rule `BR-26`.** These four measures are reported to the rule owners monthly from first go-live.
A rule estate nobody monitors becomes a rule estate people route around.

---

# 9. The Classification Imbalance *(finding `RQA-29`)*

## 9.1 What was measured

| Class | Rules | % |
|:--:|---:|---:|
| **`H` hard block** | **1,134** | **85.3%** |
| `C` computed | 144 | 10.8% |
| `A` approved override | **39** | **2.9%** |
| `S` soft warning | 9 | 0.7% |
| `C/A`, `C/H` (invalid — two classes) | 4 | 0.3% |
| **Total** | **1,330** | 100% |

## 9.2 Why this matters

A system enforcing **1,134 absolute prohibitions** with only **39 approved-override paths** and
**9 warnings** is a system in which almost every constraint is unconditional and almost none has a
legitimate exception route.

Real operations generate exceptions. A customer arrives with no NID and a broken phone. A part is
in the wrong branch. A brand's claim window closed yesterday because their portal was down. In a
system where 85% of constraints are absolute and 3% have an approval path, staff facing a genuine
exception have three options: abandon the transaction, find a workaround outside the system, or
escalate to someone who also cannot release it.

**The second option is the one that happens**, and it produces exactly the shadow operation —
spreadsheets, phone calls, WhatsApp — that this ERP exists to eliminate.

## 9.3 What the imbalance probably is

Not a design decision. `H` is the first value in the template's classification list
(`H` hard block · `A` approved override · `S` soft warning · `C` computed), the strictest, and
the one that requires no further thought: choosing `A` obliges the author to name an approving
authority (`BR-08`), and choosing `S` obliges them to justify permitting the action.

**`H` is the path of least authoring resistance**, and 1,134 of 1,330 took it.

## 9.4 The re-classification pass

**Rule `BR-27`.** Every `H` rule is tested against `CL-1`–`CL-5` during reconciliation step 9. A
rule meeting none of the five is reclassified `A`, and its approving authority is named from
`SP-004`.

**Rule `BR-28`.** The re-classification result is published as a before/after distribution. If the
`H` population does not fall materially, either the estate genuinely is that constrained — which
is a finding for the operating model, not for the software — or the pass was not performed.

**Rule `BR-29` — the design position.** Where a constraint is genuinely absolute, the system's
obligation does not end at blocking. **An `H` rule shall present the path forward**: the block
message names the rule, states why it exists, and states what the user can do instead. `NFR-078`
already requires every error message to state what happened and what to do next; for hard blocks
that is not a usability nicety, it is the difference between a control and an obstacle.

---

# 10. Traceability

## 10.1 Link `T-11`

**Rule `BR-30`.** Every rule names the requirements it constrains, and every constrained
requirement names the rules constraining it. Reciprocal, per `RQ-004` `T-11`; enforced by `CT-08`.

## 10.2 Rules and automations

They are related and are not the same artefact:

| | Business rule `BRU-` | Automation `AUT-` |
|---|---|---|
| Answers | *What may not happen* | *What happens without being asked* |
| Fires | On an attempted action | On a trigger |
| Failure | Blocks, or warns | Must have a **declared failure behaviour** |
| Owner | Business rule owner | Module owner |
| Count | 1,330 | 1,373 |

**Rule `BR-31`.** An automation that enforces a rule cites it. A rule enforced only by an
automation is enforced only when the automation runs — and every automation has a failure mode.
Where a rule is safety- or statute-critical (`CL-1`, `CL-3`), it is enforced **structurally**, not
by automation.

## 10.3 Rules and process models

**Rule `BR-32`.** Every gateway condition in a `BPM` model cites the rule that supplies it
(`RQ-007` `PM-11`). A gateway with a condition and no rule is a rule someone invented while
drawing.

## 10.4 Rules and reference data

**Rule `BR-33`.** Every threshold cites its `MD-nnn` reference value (`BR-04`). `DA-009` (Reference
Data & Code List Register) owns the identity of those values; a rule citing a value that register
does not carry is a `D-2` defect.

---

# 11. Decisions Recorded

| # | Decision | Options | Chosen | Rationale |
|---|---|---|---|---|
| D-01 | Which population governs | (a) `05-05` catalogue; (b) module §9 estate | **(b)** | Cross-repository rule: modules govern *what the system does*. The estate is also current and 10× larger |
| D-02 | What happens to catalogue-only rules | (a) Discard as stale; (b) disposition each individually | **(b)** | A control that disappears in a re-base disappears silently. `BRU-ECM-01` is the example |
| D-03 | Who keeps `BRU-ECM-nn` | (a) M12 marketplace, by seniority; (b) **M38**, which holds the `ECM` code | **(b)** | The code follows the module. `05-01` §1.3's allocation of `ECM` to M12 is itself superseded |
| D-04 | Whether to adopt SBVR formally | (a) Full SBVR vocabulary and notation; (b) SBVR concepts, existing classification | **(b)** | Full SBVR is heavier than this programme can maintain; the modality concepts are what matter |
| D-05 | Complex rules | (a) Prose; (b) DMN 1.4 decision tables above three conditions | **(b)** | Prose with three conditions has eight cases and states four |
| D-06 | Whether to reclassify the 1,134 `H` rules | (a) Accept as authored; (b) test each against `CL-1`–`CL-5` | **(b)** | 85% hard blocks with 3% override paths produces workarounds outside the system |
| D-07 | Offline rule enforcement | (a) Enforce locally; (b) advise locally, enforce on sync | **(b)** | A locally-enforced rule diverges from the server the moment the rule changes |
| D-08 | Hard-block user experience | (a) Block; (b) block **and** state the path forward | **(b)** | `NFR-078` requires it, and for `H` rules it is the difference between a control and an obstacle |

---

# 12. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| Q-01 | Four catalogue rules need disposition against `M12`: `BRU-ECM-02` (review eligibility — **no counterpart**), and `-07`, `-09`, `-10` (partially covered). Adopt or confirm each? | Marketplace Operations / Lead BA | W1 | W7 marketplace go-live; `BR-19` step 2 |
| Q-02 | Who owns the re-classification pass, and is the `SP-004` approval matrix complete enough to supply authorities for the reclassified `A` rules? | Business Process Owners | W1 | `BR-27`, `BR-08` |
| Q-03 | Do the BRD §10 and URD citations get corrected by erratum or by reissue? | Requirements Manager | W1 | `BR-19` step 4, `CT-08` |
| Q-04 | Which rules are statute-critical and therefore need a second owner under `BR-12`? | DPO / CFO / HSE | W1 | Statutory veto rights |
| Q-05 | Where do the override and warning-proceed measures get reported from before `M25` BI exists in W4? | PMO | W2 | `BR-26` from first go-live |
| Q-06 | Are the 47 modules absent from the catalogue absent because they were not re-based, or because their rules were never reviewed centrally? | Lead BA | W1 | `BR-20` scope |

---

# 13. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | A rule is defined, with six worked examples of what is not one | §3.1, §3.2 |
| AC-02 | The statement construct forbids embedded thresholds, with a worked example | `BR-04` |
| AC-03 | The classification scheme is retained and given a decision test | §4.1, `CL-1`–`CL-5` |
| AC-04 | Enforcement layer is mandatory, and client-only enforcement is forbidden | `BR-13`, `BR-14` |
| AC-05 | Offline rule behaviour is specified | `BR-15`, `BR-16` |
| AC-06 | Both populations are measured, and a governing rule is stated | §6.1, `BR-17` |
| AC-07 | The `BRU-ECM` collision is resolved by a stated procedure, with the residual risk escalated | §6.3, `BR-19`, `Q-01` |
| AC-08 | Orphaned prefixes are identified and dispositioned | §6.4 |
| AC-09 | Test obligations differ by classification, including the administrator-bypass test | §8.1, `BR-23` |
| AC-10 | The classification imbalance is measured, explained and given a corrective pass | §9 |

---

# 14. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | Module §9 tables, 79 specifications | The governing rule estate |
| Upstream | `05-05`, BRD §10 | The catalogue being re-based |
| Upstream | `SP-004`, `SP-006` | Approval authority and segregation of duties |
| Upstream | `MD-*`, `DA-009` | Reference values behind thresholds |
| Lateral | `RQ-001` | Requirements the rules constrain (`T-11`) |
| Lateral | `RQ-004` | Link `T-11` and the defect taxonomy |
| Lateral | `RQ-007` | Gateway conditions citing rules (`PM-11`) |
| Lateral | `RQ-008` | Story criteria citing rules (`AC-07`) |
| Downstream | `AR-003`, `AR-007` | Rule implementation in design |
| Downstream | `QA-003` | Rule test cases by classification |
| Downstream | `SC-004` | `SOD-nn` registration |
| Downstream | `CH-002`, `TR-*` | Training on the blocks staff will meet |
| Downstream | `M63` | Workflow engine enforcing rules at transitions |

---

# 15. References

**Within this repository**
[`RQ-001`](RQ-001_Software_Requirements_Specification.md) ·
[`RQ-004`](RQ-004_Requirements_Traceability_Matrix.md) ·
[`RQ-005`](RQ-005_Requirements_Management_Plan.md) ·
[`RQ-006`](RQ-006_Non_Functional_Requirements_Specification.md) ·
[`RQ-007`](RQ-007_Business_Process_Model_Repository.md) ·
[`RQ-008`](RQ-008_Use_Case_and_User_Story_Specification.md) ·
[`../PGD-000_Master_Register_of_Project_Guiding_Documents.md`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md)

**Workspace**
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05_Business_Rules_and_Automation_Catalogue.md` ·
`../../1000fix_ERP_Module/03_Modules/*/[MP]*.md` §9, §11 ·
`../../1000fix_ERP_Module/03_Modules/_MODULE_TEMPLATE.md` §9 ·
`../../primary-doc/1000FiX_ERP_System_Comprehensive_BRD.md` §10 ·
`../../project_content/06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-004`, `SP-006` ·
`../../project_content/06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-033`

**External**

| Reference | Verified on |
|---|---|
| OMG SBVR — Semantics of Business Vocabulary and Business Rules | 2026-08-18 |
| OMG DMN 1.4 — Decision Model and Notation | 2026-08-18 |
| ISO/IEC/IEEE 29148:2018 §5.2.4–§5.2.7 | 2026-08-18 |
| ISO 9001:2015 §4.4 | 2026-08-18 |

---

# 16. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. Two populations measured and a governing rule set; `BRU-ECM` ten-identifier collision resolved rule by rule against `M12`; orphaned prefixes dispositioned; classification decision test published; override monitoring specified; findings `RQA-27`, `RQA-28`, `RQA-29` raised. §6.3 carries a recorded self-correction (`RQA-33`): a first-draft assertion that `M12` lacked the seller-verification control was wrong — it exists as `BRU-MKP-01` | *Pending — `GV-002`* |

---

*`RQ-009` · Category 01 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
