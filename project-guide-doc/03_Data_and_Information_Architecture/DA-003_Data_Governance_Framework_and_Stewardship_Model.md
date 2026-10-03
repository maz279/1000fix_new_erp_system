---
id: DA-003
title: Data Governance Framework & Stewardship Model
category: 03 — Data & Information Architecture
code: DA
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Chief Data Officer (unappointed — see §5)
approver: Chief Technology Officer
standards_basis: >
  DAMA-DMBOK 2.0 (2024 maintenance revision) — Data Governance knowledge area ·
  ISO/IEC 38505-1:2017 (governance of data) · ISO/IEC 11179-6:2023 (registration authority) ·
  Bangladesh Personal Data Protection Act 2026
traces_to: >
  PGD-000 DA-003 · MD-001 (master-data charter) · audit C-04 (PDPA absent) ·
  NFR-096 (Chief Data Officer) · NFR-090…NFR-099 · GV-002 (governance framework)
depends_on: GV-002 · DA-005 · DA-002
verified_on: 2026-08-18
priority: P0
needed_by: W1
enumeration_timestamp: 2026-08-18 14:30 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# DA-003 — Data Governance Framework & Stewardship Model

### Category 03 · Code `DA` · DAMA-DMBOK 2.0 · ISO/IEC 38505-1:2017 · PDPA 2026

---

## 1. Purpose

`MD-001` is a **charter for master-data content**: seven domains, three roles, five golden-record
rules, a code-format standard. It is good, it is enforced by hard validation rules, and it governs 45
of the estate's datasets.

**It is not governance of the data estate.** It says nothing about the other 1,335 tables, nothing
about personal data, nothing about who may approve a residency classification, nothing about who
answers the National Data Management Authority, and nothing about the **Chief Data Officer that PDPA
2026 requires if 1000FiX is a significant data fiduciary** — which, at 250,000+ customers a month, it
almost certainly is.

This document is that governance: the domains, the decision rights, the accountability model, the
Chief Data Officer's mandate, and the escalation path when two owners disagree.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | The data-domain model across the whole estate, not only master data |
| 2 | Roles: owner, steward, custodian, Registration Authority, CDO |
| 3 | **Decision rights** — who may decide what, and who may not |
| 4 | The **Chief Data Officer** mandate, statutory basis and reporting line |
| 5 | The Data Governance Council: composition, quorum, cadence, authority |
| 6 | Personal-data accountability — controller/processor, purpose, lawful basis |
| 7 | Escalation and arbitration |
| 8 | Measurement — how governance is known to be working |
| 9 | The **unowned datasets** and the gap they represent |

**Explicitly out of scope**

| Topic | Owned by | Why |
|---|---|---|
| Programme governance, Steering Committee, Design Authority | `GV-002` | This specialises it for data; it does not replace it |
| Master-data content rules | `MD-001` | Retained and extended, not superseded |
| Classification scheme | `DA-005` | This document says who *approves* a classification |
| The DPIA | `SC-003` | This document names its owner |
| Quality metrics and thresholds | `DA-008` | This document names accountability for them |
| Security controls | `SC-001`, `SC-004` | Governance decides; security implements |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| **CTO / Board** | §5 — the CDO decision, its statutory basis and its exposure |
| Domain owners | §3 — what they are accountable for |
| Stewards | §4 — the work |
| DPO / Legal | §7 — the PDPA accountability model |
| `DA-002` Registration Authority | §6 — the approval path for attributes 21–24 |
| Auditors | §9 — how governance is measured |

---

## 2. Basis and Findings

### 2.1 Standards conformance

| Standard | Conformance | Departure |
|---|---|---|
| **DAMA-DMBOK 2.0** (2024 maintenance revision) | Data Governance knowledge area — organisation, roles, policy, escalation | **DMBOK 3.0 is in development, not released** (verified 2026-08-18) |
| **ISO/IEC 38505-1:2017** | Governance of data — the EDM (evaluate, direct, monitor) model applied in §9 | Not a certification target |
| **ISO/IEC 11179-6:2023** | Registration Authority and Submitting Organisation roles | Adopted directly into §4 |
| **PDPA 2026** | §5 CDO; §7 controller/processor and purpose accountability | Statutory; not optional |

### 2.2 Source material

| Source | Contribution |
|---|---|
| `../../project_content/02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-001_Master_Data_Governance_Charter.md` | The 7-domain register, 3 roles, `GR-01`…`GR-05`, `CF-01`…`CF-04`, `GOV-01`…`GOV-06` |
| The 48 `MD-*` files §1 "Purpose and ownership" | Per-dataset owner, steward, golden source, refresh cadence |
| `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md` §6.3 | NFR-090…NFR-099, including **NFR-096 Chief Data Officer** |
| `../../project_content/10_Legal_Policy_and_Compliance/LG-008`, `LG-009`, `LG-012` | Purposes `P-01`…`P-20`; retention; transfer |
| `../../project_content/14_Reporting_Analytics_and_KPI/RP-016_Data_Quality_Scorecard_Definition.md` §4.3 | **12 scored domains aligned to `M64` entity ownership** — the better domain model |
| `./DA-002_Data_Dictionary.md` §4 | Registration Authority and the CDO approval requirement |

### 2.3 Findings this document raises

> **`PGD-A5-06` — two master-data datasets have no owner, no steward and no approver, and one of them
> is payroll.**
>
> `MD-001` §2.1's domain register assigns `MD-002`…`MD-042` and `MD-044`…`MD-047`. Enumerating the
> folder at 2026-08-18 14:30 returns **48 files**. `MD-001` governs itself; that leaves two
> unassigned:
>
> | Dataset | What it is | Consequence |
> |---|---|---|
> | **`MD-043` Payroll Element and Statutory Deduction Register** | Income tax slabs, provident fund, gratuity, statutory deductions | **The most statutorily exposed dataset in the estate has no accountable owner.** A wrong deduction is a Labour Act and income-tax exposure, not a data-quality score |
> | **`MD-048` Master Data Seed Load Workbook Index** | The load-sequence index for **all 47 other datasets** | **`GOV-02`** — *"a record may not be created in a dataset whose load dependencies are unloaded"* — depends on it |
>
> **`MD-001`'s own rule `GOV-01` is a hard block:** *"A dataset without a named owner, steward and
> approver may not be loaded to production."* **By its own rule, neither `MD-043` nor `MD-048` can be
> loaded**, and `MD-048` is what sequences everything else.
>
> **Also measured:** `MD-001` §7 states *"7 domains, 47 datasets"*; the §2.1 register assigns **45**.
> A two-dataset arithmetic gap that is exactly the two unowned files — the count was taken from intent
> rather than from the rows, which is the estate's recurring defect class (`PGD-A1-02`, `PGD-A1-13`,
> `PGD-A3-16`).
>
> **Remediation:** assign `MD-043` to the **HR Director** (owner) / HR systems analyst (steward) /
> HR Director with CFO countersignature (approver), given its tax content; assign `MD-048` to the
> **MDM Lead**, who already owns the load sequence under `MD-001` §2.2. Correct §7's count to 47.

> **`PGD-A5-07` — no Chief Data Officer exists, and four documents already depend on one.**
>
> `NFR-096` requires a CDO **if 1000FiX is classified a significant data fiduciary**. `DA-002` §4.1
> names the CDO as approver for classification, personal-data and residency attributes. `LG-009`
> `OV-06` names *"CDO with Legal"* as the authority that refuses an erasure. `MD-001` §8.1 records
> that **domain owner roles name offices, not people**, and `RF-010` must name individuals before W1
> load. The role `R40 Chief Data Officer` is **in use in module specifications and unregistered in
> `05-04`** (`AR-001` §9.1).
>
> **Four dependencies on a post nobody holds.** §5 states the decision.

### 2.4 A regulatory currency finding

> **`PGD-A5-08` — the recorded penalty basis may be wrong. Verified against public sources
> 2026-08-18; requires legal confirmation.**
>
> `05-06` §6.3 records penalty exposure as *"up to **BDT 25 lakh** for security failures or rights
> violations, and up to **BDT 50 lakh** for significant data fiduciaries"*, registered as risk
> `RSK-032`.
>
> Public reporting on the PDPA 2026 describes a **turnover-based** regime: *"general contraventions
> attract fines of **1–2% of annual turnover**, while significant data fiduciaries face **2–5% of
> annual turnover**."*
>
> The two may coexist — a fixed cap alongside a turnover percentage is a common construction — but
> **the estate has recorded only the fixed figures, and a turnover percentage on a company of
> 1000FiX's scale is a materially different number.** `RSK-032`'s quantification, and the `CO-005`
> TCO line that carries it, both rest on the fixed figure.
>
> **Evidentiary standing:** secondary sources, not the statute. Referred to Legal and to `RR-005`
> (Standards & Regulatory Currency Register). **This is the third time in this category that a
> statutory position in the estate has not matched public reporting** — see also `DA-001` §10.4 and
> `DA-005` §3.4.

---

## 3. The Domain Model

### 3.1 Why `MD-001`'s seven domains are not enough

`MD-001` has **seven domains covering 45 master-data datasets**. The estate has **1,335 tables**.
Master data is roughly 5% of it; transactional, analytical and operational data have no domain, no
owner and no steward.

**`RP-016` §4.3 already solved half of this** with **12 scored domains aligned to `M64` entity
ownership rather than to the 48 `MD` files**, and its reasoning is right: *"Scoring 48 files would
produce 48 scores with no single owner per score."*

### 3.2 The estate domain model

**Twelve domains**, extending `RP-016`'s twelve to cover the whole estate rather than only the scored
master data. Each has exactly one **accountable executive owner**.

| # | Domain | Covers | Data owner | Steward | `MD-001` / `RP-016` link |
|:--:|---|---|---|---|---|
| **DD-01** | **Party & customer** | `fix_party`, roles, hierarchy, addresses, consent, identity documents, segments | **Chief Commercial Officer** | MDM Lead | `MD-013`…`MD-018`; `RP-016` D1, D2 |
| **DD-02** | **Device & asset** | Asset registry, brand/model, ownership, custody, telemetry, fixed assets | **Service Operations Director** | Technical Director's analyst | `MD-021`; `RP-016` D3 |
| **DD-03** | **Catalogue & pricing** | Services, products, parts, kits, price books, rate cards, discounts | **Chief Commercial Officer** | Catalogue analyst | `MD-019`…`MD-034`; `RP-016` D4, D9 |
| **DD-04** | **Service & work** | Service orders, work orders, diagnostics, QC, SLA, custody events | **Service Operations Director** | Service Ops analyst | — *(no `MD` coverage: transactional)* |
| **DD-05** | **Supply & inventory** | Stock, movements, warehouses, procurement, vendors, imports | **Supply Chain Director** | Inventory Manager | `MD-016`, `MD-022`, `MD-023` |
| **DD-06** | **Finance & tax** | Ledger, AR, AP, treasury, tax codes, Mushak, dimensions, revenue | **Chief Financial Officer** | Finance systems analyst | `MD-035`…`MD-041`; `RP-016` D11 |
| **DD-07** | **Workforce** | Employee, contract, attendance, payroll, competency, certification, safety | **HR Director** | HR systems analyst | `MD-009`…`MD-012`, **`MD-043`**, `MD-042`; `RP-016` D5, D6 |
| **DD-08** | **Commercial agreement** | Contracts, entitlements, warranty, claims, subscriptions, marketplace seller | **Chief Commercial Officer** | Account Management analyst | `MD-031`, `MD-032`; `RP-016` D10 |
| **DD-09** | **Organisation & network** | Entity, branch, zone, warehouse location, geography, calendar | **Operations Director** | Operations MDM analyst | `MD-002`…`MD-008`; `RP-016` D7, D8 |
| **DD-10** | **Governance & evidence** | Documents, e-signature, quality records, risk, compliance, audit entries | **Quality Manager** | Document controller | — |
| **DD-11** | **Codes & reference** | Fault, resolution, reason, status, priority, UoM, and **all 348 state machines** | **Technical Director** | Enterprise Architecture analyst | `MD-024`…`MD-028`; `RP-016` D12; **`DA-009`** |
| **DD-12** | **Analytical & derived** | Warehouse datasets, metrics, ML features, model outputs | **Chief Technology Officer** | Data platform steward | `RP-001`, `RP-006` |

> **DD-04 is the one with no `MD` coverage and the highest volume.** Service and work data is
> transactional, so `MD-001` correctly does not govern it — and consequently **the estate's
> highest-volume data domain has never had a named owner**. DD-04 fixes that.

### 3.3 Domain assignment rules

| # | Rule |
|---|---|
| **DM-01** | **Every table in `DA-001` belongs to exactly one domain.** A table in two domains is a defect; a table in none is worse |
| **DM-02** | Domain assignment follows the **owning module** from `AR-005`, not the physical schema |
| **DM-03** | A domain has **one accountable executive owner**. Shared accountability is no accountability |
| **DM-04** | A cross-domain concept (the shared kernel) is owned by the domain of its **owning module** — party by DD-01, catalogue by DD-03, document by DD-10 |
| **DM-05** | `MD-001`'s seven master-data domains **map into** these twelve and remain the authority for master-data *content* |

---

## 4. Roles

### 4.1 The five roles

| Role | Accountable for | Held by |
|---|---|---|
| **Data owner** | The **meaning and correctness** of a domain's data. Approves definitions, classifications and quality thresholds. Answers for a defect | One named executive per domain (§3.2) |
| **Data steward** | Day-to-day quality, additions, corrections, exception handling, the remediation queue | One named individual per domain |
| **Data custodian** | The **technical** care of the data — storage, backup, access enforcement, performance | Platform Engineering |
| **Registration Authority** | Accepts a `DA-002` registration as complete (ISO/IEC 11179-6) | **Data Architect** |
| **Chief Data Officer** | **Statutory accountability for personal data**; approves classification, residency and personal-data attributes; represents the company to the Authority | **Unappointed — §5** |

> **Owner and custodian are deliberately separate.** The CFO owns the meaning of a tax code; Platform
> Engineering owns the disk it sits on. Merging them puts a business judgement in an engineer's hands
> or a storage decision in an accountant's.

### 4.2 What a data owner may and may not decide

| May decide | May **not** decide |
|---|---|
| The business definition of a field | The **classification** of personal data — CDO (§6) |
| Valid values and code list membership | The **residency** class — CDO with Legal |
| Quality thresholds for their domain | The **retention period** — `LG-009`, Legal |
| Who the steward is | Whether an erasure is refused — CDO with Legal (`OV-06`) |
| Whether a bulk change proceeds (`GOV-05`) | Whether a **cross-domain** boundary moves — Council (§8) |
| Their domain's contribution to the seed load | The physical schema — Data Architect (`DA-001`) |

### 4.3 Steward workload — stated because it is routinely underestimated

`DM-011` `DQ-16` makes the point precisely: *"If profiling shows a 15% duplicate rate on 100,000
customers, and the review band captures a third of the candidate pairs, the stewardship queue is in
the **thousands of decisions**. At two minutes each that is weeks of work by someone who can recognise
a customer."*

| # | Rule |
|---|---|
| **SW-01** | **A steward role is a named time allocation, not a title.** The allocation is stated per domain per wave |
| **SW-02** | The remediation queue has a **declared drain rate** (`DQ-22`); a queue with no drain rate is a bin |
| **SW-03** | Queue depth at a wave gate is **reported, not carried silently** (`DQ-23`) |
| **SW-04** | A steward with no allocated time is an **unresourced control**, and is reported as one to the Council |

---

## 5. The Chief Data Officer

### 5.1 The statutory basis

| Source | Requirement |
|---|---|
| **NFR-096** | *"Appoint a Chief Data Officer if the Company is classified a significant data fiduciary, with the role, authority and reporting line defined"* — **P0** |
| PDPA 2026 | Significant data fiduciaries **must appoint a qualified Chief Data Officer** responsible for representing the business before the Authority, submitting reports, facilitating data-subject rights and handling complaints |
| Designation basis | The Authority designates by **classification and volume of data processed, and potential impact** |
| Timing | **Enforcement, including the CDO appointment obligation, activates around 13 May 2027 — inside Wave 4** |

### 5.2 Is 1000FiX a significant data fiduciary?

**Not formally determined. The indicators are strong.**

| Indicator | 1000FiX position |
|---|---|
| Volume of personal data | **250,000+ customers/month**; ~3 M party records at year 5 |
| Sensitive categories | NID, passport, TIN, **biometric attendance templates**, KYC, criminal-record checks |
| Special processing | **Recovered customer data** held as processor (`AR-002` §5.4) |
| External actors | 500–2,000 marketplace sellers; 17+ brand partners |
| Critical infrastructure adjacency | Payment rails; a national service hotline |

> **The prudent position is to assume the designation applies.** The cost of appointing a CDO and not
> needing one is a role; the cost of needing one and not having it is a statutory contravention at a
> **turnover-based** penalty (`PGD-A5-08`) with enforcement inside Wave 4.

### 5.3 The mandate

| # | The CDO |
|---|---|
| **CDO-01** | Is **accountable to the Board**, with a reporting line that does not run through the CTO — the function must be able to say no to delivery |
| **CDO-02** | **Approves** classification, personal-data category and residency for every data element (`DA-002` attributes 21–23) |
| **CDO-03** | **Owns `SC-003`** (DPIA) and the record of processing activities |
| **CDO-04** | **Represents the company to the National Data Management Authority** — reports, breach notification (NFR-094), transfer notification (NFR-086b) |
| **CDO-05** | Adjudicates a **refusal to erase** with Legal (`LG-009` `OV-06`) |
| **CDO-06** | Chairs the Data Governance Council (§8) |
| **CDO-07** | Holds a **veto** on any processing without a recorded lawful basis (NFR-090) |
| **CDO-08** | Reports personal-data risk to the Board at least quarterly |

### 5.4 The decision required now

| Option | Assessment |
|---|---|
| Appoint now | **Recommended.** Four documents already depend on the role (`PGD-A5-07`); classification decisions begin in W0 |
| Appoint at the W4 enforcement date | **Rejected.** Every classification made in W0–W3 would be made without the accountable approver, and `SC-003` cannot be written |
| Interim: assign the mandate to an existing executive | **Acceptable as a bridge only**, with a named date to appoint. The mandate must be written down whoever holds it |
| Do not appoint | **Only defensible if a formal determination establishes 1000FiX is not a significant data fiduciary** — and that determination does not exist |

**Escalated to `GV-005` RAID and to the Board via `GV-002`.**

---

## 6. Decision Rights

The RACI the estate does not have. **A = accountable, one only.**

| Decision | Data owner | Steward | Data Architect | **CDO** | Legal | Council |
|---|:--:|:--:|:--:|:--:|:--:|:--:|
| Business definition of a field | **A** | R | C | I | — | — |
| Valid values / code list membership | **A** | R | C | — | — | I |
| Physical schema, types, constraints | C | — | **A** | — | — | I |
| **Classification `S0`–`S3`** | C | — | C | **A** | C | I |
| **Personal-data category** | C | — | — | **A** | C | I |
| **Residency class** | C | — | C | **A** | **R** | I |
| Retention period | C | — | — | R | **A** | I |
| Quality threshold for a domain | **A** | R | C | I | — | I |
| Golden-record survivorship rule | **A** | R | C | C | — | I |
| Approve a merge above threshold | C | **A** | — | — | — | — |
| Refuse an erasure request | C | — | — | **A** | **R** | I |
| Cross-domain boundary change | C | — | R | C | — | **A** |
| New domain / owner reassignment | C | — | R | C | — | **A** |
| Bulk change > 500 records (`GOV-05`) | **A** | R | — | — | — | — |
| Breach notification to the Authority | I | — | I | **A** | R | I |

> **The three rows where the CDO is accountable and the data owner is only consulted are the point of
> this table.** Classification, personal-data category and residency are **statutory judgements**, not
> business preferences. A commercial owner who wants a field visible in a report may not reclassify it.

---

## 7. Personal-Data Accountability

### 7.1 Controller and processor

`AR-002` §5.4 establishes the positions. This document assigns the accountability.

| Personal data | Role | Accountable |
|---|---|---|
| Customer identity, contact, service history | **Controller** | CDO |
| NID / passport / TIN / biometric | **Controller** | CDO |
| Employee records, payroll, biometric templates | **Controller** | CDO with HR Director |
| Marketplace seller KYC | **Controller** | CDO with CCO |
| **Recovered customer data (M06)** | **Processor** — the customer is controller | **CDO with Technical Services Head** |
| Corporate client end-user identity (federated) | The **client** is controller | CDO ensures flow-down (NFR-098) |
| Portal behavioural analytics | Controller | CDO |

> **The M06 row is the one the estate has never stated.** As **processor**, 1000FiX must act only on
> the controller's instructions, flow equivalent obligations to sub-processors (NFR-098), and cannot
> decide the purpose. That is a different — in some respects stricter — obligation set, and it must
> reach the M06 customer contract (`LG-017`).

### 7.2 Purpose and lawful basis

| # | Rule |
|---|---|
| **PB-01** | **Every processing purpose is registered** — `LG-008` `P-01`…`P-20` is the register |
| **PB-02** | Every purpose has a **lawful basis** and a **retention row** — `LG-009` maps `RC-01`…`RC-23` one-to-one to purposes |
| **PB-03** | **A new purpose requires CDO approval before processing begins** (CDO-07) |
| **PB-04** | Consent for one purpose is **not** consent for another. Model training is a distinct purpose from service delivery (`AR-011` §10.1 DP-01) |
| **PB-05** | The record of processing activities is retained **5 years minimum** (NFR-095) |

### 7.3 The transcript-mining control

`AR-011` §10.2 records audit finding `HC` (critical): **customer-transcript mining is scheduled at W2
with no confirmed legal basis.** The governance position:

| # | Rule |
|---|---|
| **TM-01** | **No transcript mining begins until `SC-003` records a lawful basis for that purpose**, and, if consent-based, until the consent mechanism exists in M33 |
| **TM-02** | The control is **technical** — CD-243 must not load conversation content into a training-accessible dataset until a purpose flag is set by M33. **A policy statement is not a control** |
| **TM-03** | The **CDO holds the flag**. Nobody else may set it |

---

## 8. The Data Governance Council

| Attribute | Value |
|---|---|
| **Chair** | Chief Data Officer (CDO-06) |
| **Members** | The 12 domain owners (§3.2), Data Architect, DPO, Legal, Head of InfoSec, MDM Lead |
| **Quorum** | Chair + 5 domain owners + Legal or DPO |
| **Cadence** | Monthly through W1–W5; quarterly thereafter; **plus any wave gate** |
| **Authority** | Cross-domain boundary changes; new domains; owner reassignment; escalated arbitration; accepting the quality scorecard |
| **Cannot decide** | Anything reserved to the CDO alone (§6), or to Legal (retention, refusal to erase) |
| **Reports to** | ERP Steering Committee via `GV-002`; personal-data risk to the Board quarterly |
| **Minuted in** | `GV-003` Decision Log |

### 8.1 Escalation and arbitration

| Step | Action | Time limit |
|:--:|---|---|
| 1 | Two owners disagree on a definition, boundary or threshold → **stewards attempt resolution** | 5 working days |
| 2 | Unresolved → **Data Architect proposes a ruling** on the evidence | 5 working days |
| 3 | Unresolved → **Council rules** | Next meeting, or an extraordinary session within 10 working days |
| 4 | A ruling with architectural consequence → **ADR in `AR-004`**; with boundary consequence → `AR-005` | With the ruling |

> **The time limits exist because an unresolved data dispute blocks a build.** A definition nobody
> will rule on becomes two implementations.

---

## 9. Measurement

Governance that is not measured is an org chart. **ISO/IEC 38505-1's evaluate–direct–monitor** applied.

| # | Metric | Target | Cadence | Source |
|---|---|---|---|---|
| **GM-01** | Domains with a **named individual** owner and steward | **12 of 12** | Monthly | This document; `RF-010` |
| **GM-02** | Datasets with owner, steward **and approver** (`GOV-01`) | **48 of 48** | Monthly | **Currently 46 — `PGD-A5-06`** |
| **GM-03** | `DA-002` elements with classification, personal-data and residency assigned | 100% before each wave gate | Wave gate | `DA-002` `RC-3` |
| **GM-04** | Elements carrying personal data with a resolving retention class | 100% | Wave gate | `DA-002` `RC-4` |
| **GM-05** | **Data-quality scorecard** — 12 domains | Per `RP-016` §4.4 thresholds | Monthly | `DA-008` |
| **GM-06** | Steward remediation queue depth and drain rate | Declared per domain per wave | Monthly | `DQ-22` |
| **GM-07** | Processing purposes with a recorded lawful basis | **100%** | Quarterly | `LG-008`; CDO |
| **GM-08** | Data-subject requests closed within the statutory window | 100% | Monthly | `LG-010`; CDO |
| **GM-09** | Retention violations — **both directions** (`RS-07`) | Zero | Monthly | `DA-006` |
| **GM-10** | Open cross-domain arbitrations beyond their time limit | Zero | Monthly | §8.1 |

> **GM-09 measures both directions deliberately.** `LG-009` `RS-07`: *"A record retained beyond its
> schedule and a record missing before its schedule expires are equally reportable."* Most retention
> programmes measure only the first.

---

## 10. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| **Q-01** | **Is a Chief Data Officer appointed, and when?** (`PGD-A5-07`) Four documents depend on the role | CTO / Board | **W0 — blocking** | `DA-002` attributes 21–23; `SC-003`; `LG-009` `OV-06` |
| **Q-02** | **Is 1000FiX a significant data fiduciary?** No formal determination exists | Legal / DPO | **W1** | CDO obligation; penalty basis |
| **Q-03** | **Who owns `MD-043` and `MD-048`?** (`PGD-A5-06`) By `GOV-01` neither can be loaded | MDM Lead / HR Director | **W0 — blocking the seed load** | Every master-data load, via `MD-048` |
| **Q-04** | **Is the penalty basis fixed or turnover-based?** (`PGD-A5-08`) `RSK-032` and `CO-005` rest on the fixed figure | Legal / CFO | W1 | Risk quantification; TCO |
| **Q-05** | Are the 12 domains and their named executive owners accepted? | Steering / `GV-002` | W1 | §6 decision rights |
| **Q-06** | Is steward time allocated per domain per wave (`SW-01`)? | Domain owners / Programme Manager | W1 | `SW-04`; the remediation queue |
| **Q-07** | Does the M06 processor position require an amendment to `LG-017`? | Legal / DPO | W6 | M06 go-live |

---

## 11. Decisions Recorded

| # | Decision | Options | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| D-D3-01 | Domain granularity | `MD-001`'s 7 master-data domains; per-module (67); **12 estate domains** | **12 (§3.2)** | 7 covers 5% of the estate; 67 reproduces the module list. `RP-016` already proved 12 works | DD-04 gives the highest-volume domain its first owner |
| D-D3-02 | `MD-001` disposition | Supersede; **retain and extend** | **Retain** | It is good, it is enforced by hard rules, and it governs master-data *content* well | `DM-05` maps 7 into 12 |
| D-D3-03 | Classification authority | Data owner; **CDO** | **CDO** | Classification is a statutory judgement, not a business preference | A commercial owner cannot reclassify to make a report easier |
| D-D3-04 | CDO reporting line | Through CTO; **to the Board** | **To the Board** | The function must be able to say no to delivery | CDO-01 |
| D-D3-05 | CDO timing | At W4 enforcement; **now** | **Now** | Classification decisions begin in W0; `SC-003` cannot be written without the approver | An appointment, or a written interim mandate with a date |
| D-D3-06 | Owner/custodian | Merged; **separate** | **Separate** | Business meaning and technical care are different competences | §4.1 |
| D-D3-07 | Arbitration | Best endeavours; **time-limited escalation** | **Time-limited (§8.1)** | An unresolved data dispute becomes two implementations | 20 working days end to end |

---

## 12. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | Every table in `DA-001` belongs to exactly one domain with one executive owner | §3.2, `DM-01`…`DM-05` |
| AC-02 | Five roles are defined, including the ISO/IEC 11179-6 Registration Authority | §4.1 |
| AC-03 | Decision rights are stated as a RACI with a single accountable party per decision | §6 |
| AC-04 | The CDO mandate, statutory basis and reporting line are defined (NFR-096) | §5 |
| AC-05 | Controller/processor is assigned per personal-data class, including the M06 processor position | §7.1 |
| AC-06 | The Council has composition, quorum, cadence, authority and stated limits | §8 |
| AC-07 | Escalation is time-limited | §8.1 |
| AC-08 | Governance is measured, both directions where the rule is bidirectional | §9 — 10 metrics |
| AC-09 | Unowned datasets are identified and remediated, not described | §2.3 `PGD-A5-06` |

**Definition of done.** Complete when every criterion is met, Q-01 and Q-03 are resolved, and
`PGD-000`'s `DA-003` row is updated. **`GM-02` reads 46 of 48 on issue, and this document says so.**

---

## 13. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `GV-002` | Programme governance this specialises |
| Upstream | `GV-003` | Council rulings are minuted there |
| Downstream | `DA-002` | Registration Authority; CDO approval for attributes 21–23 |
| Downstream | `DA-005` | This document says who approves a classification |
| Downstream | `DA-008` | Domain owners are accountable for quality thresholds |
| Downstream | `DA-009` | DD-11 owns every code list and all 348 state machines |
| Downstream | **`SC-003`** | The CDO owns the DPIA |
| Downstream | `SC-007` | Residency approval sits with the CDO |
| Downstream | `GV-005` | The CDO gap and the penalty-basis finding are escalated as risks |
| Lateral | `MD-001` | Retained and extended (`DM-05`); its `GOV-01` gap is `PGD-A5-06` |
| Lateral | `RP-016` §4.3 | The 12-domain model this extends estate-wide |

---

## 14. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` · `./_CATEGORY_OVERVIEW.md` ·
`./DA-001_Logical_and_Physical_Data_Model_and_Database_Schema_Specification.md` ·
`./DA-002_Data_Dictionary.md` · `./DA-005_Data_Classification_and_Handling_Standard.md` ·
`./DA-006_Data_Retention_Archival_and_Deletion_Design.md` · `./DA-008_Data_Quality_Management_Plan.md` ·
`./DA-009_Reference_Data_and_Code_List_Register.md` ·
`../02_Architecture_and_Design/AR-002_Enterprise_and_Solution_Architecture_Blueprint.md` §5.4 ·
`../02_Architecture_and_Design/AR-011_AI_ML_Architecture_and_Model_Specification.md` §10.2

**Workspace**
`../../project_content/02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-001_Master_Data_Governance_Charter.md` ·
`../../project_content/02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-043_Payroll_Element_and_Statutory_Deduction_Register.md` ·
`../../project_content/02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-048_Master_Data_Seed_Load_Workbook_Index.md` ·
`../../project_content/14_Reporting_Analytics_and_KPI/RP-016_Data_Quality_Scorecard_Definition.md` §4.3 ·
`../../project_content/10_Legal_Policy_and_Compliance/LG-008_Privacy_Notice_and_Consent_Copy.md`, `LG-009_Data_Retention_and_Deletion_Schedule.md` ·
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md` §6.3

**External standards and sources**

| Source | Version / date | Verified |
|---|---|---|
| [DAMA-DMBOK](https://www.damadmbok.org/) — Data Governance knowledge area | 2.0 (2024 maintenance revision) | 2026-08-18 |
| ISO/IEC 38505-1 — Governance of data | 2017 | 2026-08-18 |
| [ISO/IEC 11179-6:2023 — Registration](https://www.iso.org/standard/78916.html) | 2023 | 2026-08-18 |
| [Bangladesh PDPA 2026 — significant data fiduciary, CDO, penalties](https://securiti.ai/bangladesh-personal-data-protection-act-overview/) | Enforcement ~13 May 2027 | 2026-08-18 |
| [Personal Data Protection (Amendment) Ordinance 2026, No. 23 of 2026](https://digitalpolicyalert.org/event/38601-president-implemented-personal-data-protection-amendment-ordinance-2026-ordinance-no-23-of-2026) | 5 February 2026 | 2026-08-18 |

---

## 15. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. Extends `MD-001`'s 7 master-data domains to **12 estate domains** covering all 1,335 tables. Defines the CDO mandate against NFR-096. Raises `PGD-A5-06` (`MD-043` and `MD-048` unowned — `GOV-01` blocks their load), `PGD-A5-07` (no CDO; four dependencies) and `PGD-A5-08` (penalty basis may be turnover-based) | *Pending — CTO* |

---

*`DA-003` · Category 03 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
