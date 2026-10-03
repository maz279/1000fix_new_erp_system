---
id: RQ-006
title: Non-Functional Requirements Specification
category: 01 — Requirements Engineering
code: RQ
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: ERP Solution Architect
approver: ERP Design Authority
standards_basis: ISO/IEC 25010:2023 (product quality model, 9 characteristics) · ISO/IEC 25012 (data quality) · ISO/IEC/IEEE 29148:2018 §9.6.13, §9.6.14, §9.6.18 · ISO/IEC 25023 (measurement)
traces_to: PGD-000 RQ-006 row · audit AP-02 (NFR-090/091/092 double-allocated) · RQ-001 §3.12.4 (PDPA obligations reallocated) · 05-06 (the NFR set being re-based)
depends_on: RQ-001 (requirement set, verification methods, SWR reallocation) · RQ-005 (NFR allocation authority)
verified_on: 2026-08-18
priority: P0
needed_by: W1
enumerated_on: 2026-08-18 02:15 (+06)
supersedes: 05_Cross_Cutting_Specifications/05-06 as the allocating authority for NFR-nnn
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# RQ-006 — Non-Functional Requirements Specification

### Category 01 · Code `RQ` · ISO/IEC 25010:2023

---

> **This document re-bases an NFR set that is good and is drifting.** `05-06` is one of the
> stronger artefacts in the estate: 104 quality requirements, most with a numeric target and a
> named measurement instrument, corrected under audit for Bangladeshi regulatory currency. It has
> three defects that make it unsafe to build against, and one gap it does not know it has.
>
> **Defect 1 — five identifiers denote two things each.** `NFR-090`, `NFR-091` and `NFR-092`
> denote both a PDPA obligation (§6.3) and a maintainability requirement (§7). `NFR-088` and
> `NFR-089` appear twice as whole rows. Audit `AP-02` found three of these five.
>
> **Defect 2 — the quality model is the superseded one.** `05-06` is organised around performance,
> availability, scalability, security, usability, compliance, maintainability and data integrity —
> the ISO/IEC 25010:**2011** shape. The 2011 product quality model was revised in **2023**:
> *Usability* became *Interaction capability*, *Portability* became *Flexibility*, *Scalability*
> moved under Flexibility, and a ninth characteristic — **Safety** — was added.
>
> **Defect 3 — quality requirements are unbound.** No NFR in the estate names the functional
> requirements it constrains. "Satisfy `NFR-002`" is therefore an instruction with no addressee.
>
> **The gap — Safety.** A programme that destroys customer data as a commercial product, moves
> lithium batteries by motorcycle, sends technicians into customer premises to work on mains
> electricity, and executes brand product recalls has **no safety quality requirements at all**,
> because the model it used had no place to put them.

---

## 1. Purpose

Non-functional requirements decide whether a correct system is usable. A service order screen
that returns the right answer in nine seconds has failed; a payment path that is right 99.5% of
the time is a reconciliation department. This document specifies every quality requirement the
1000FiX platform shall meet, organised by the current international quality model, each with a
target, a measurement method, a verification method and — the addition that makes them
enforceable — the functional requirements each one constrains.

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | The **re-basing** of `05-06`'s 104 NFRs onto ISO/IEC 25010:2023's nine characteristics (§4) |
| 2 | **Resolution of the five duplicate identifiers**, with a stated resolution rule (§3.3) |
| 3 | The **retirement** of `NFR-093`–`NFR-099`, reallocated to `SWR-021`–`SWR-029` (§3.4) |
| 4 | A **measurement method** per requirement — instrument, sample, frequency, threshold (§3.5) |
| 5 | The **binding** of each NFR to the functional requirements it constrains — link `T-05` (§3.6) |
| 6 | The **Safety** characteristic, new to this programme: `NFR-102`–`NFR-113` (§4.9) |
| 7 | **Allocation authority** for the `NFR-nnn` space, transferred from `05-06` to this document (§3.2) |

**Explicitly out of scope:**

| Topic | Owned by | Why |
|---|---|---|
| Functional requirements | `RQ-001` | Including the ten PDPA obligations reallocated out of the NFR space |
| System-level requirements — power, connectivity, devices, climate | `RQ-002` | Above the software boundary |
| Localisation standards, architecture standards `AS-01`–`AS-15`, data integrity `DI-01`–`DI-08`, operability `OPS-01`–`OPS-08` | `05-06` §8–§12, `AR-012` | Retained where they sit; §5 states how they are treated |
| How the targets are met | `AR-001`, `PE-*` | Design |
| How the targets are tested | `QA-006`, `QA-007`, `QA-008` | Test plans consuming §3.5 |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| Architects | The quality-attribute scenarios `AR-001` must design against |
| Developers | The envelope a component must stay inside |
| QA | The measurement method and threshold each test asserts |
| SRE / Platform | The production measures that must exist to prove them |
| CISO, DPO, HSE | The security and safety requirements they own |
| Business owners | What "fast enough", "available enough" and "safe enough" mean, numerically |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause | Conformance | Departure |
|---|---|---|---|
| **ISO/IEC 25010:2023** | Product quality model | §4 is organised as the nine characteristics and their sub-characteristics, in the standard's names | None |
| ISO/IEC 25012 | Data quality model | Data quality requirements are cross-referenced to `DA-008`, not restated | Delegated |
| ISO/IEC 25023 | Measurement of system and software product quality | §3.5 requires an instrument, a sample and a frequency per requirement, in the spirit of 25023's measurement functions | Measures are programme-specific, not 25023's catalogue |
| ISO/IEC/IEEE 29148:2018 | §9.6.13, §9.6.14, §9.6.18 | This document **is** the content of those three SRS clauses; `RQ-001` §2.1.2 records the tailoring | None |
| ISO/IEC/IEEE 29148:2018 | §5.2.4, §5.2.7 | Every NFR statement uses the mandated construct and language criteria | None |

**Currency — verified 2026-08-18**

| Citation | Status | Consequence |
|---|---|---|
| **ISO/IEC 25010:2023** | **Current.** Revises the product quality model of ISO/IEC 25010:2011 | Nine characteristics; *Usability* → *Interaction capability*; *Portability* → *Flexibility*; *Scalability* moved under Flexibility; **Safety added** |
| ISO/IEC 25010:2011 | **Superseded** | `05-06`'s implicit model. Citing it is the same defect class as `H-01` (NIST SP 800-88 r1) and `C-04` (Digital Security Act 2018) |
| WCAG 2.2 | Current (W3C Recommendation) | `NFR-073` currently specifies 2.1 AA; `UX-005` specifies 2.2 AA. Resolved in §3.7 |

### 2.2 Source material relied on

| Source | What it provides | Measured 02:15 (+06) |
|---|---|---|
| `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06` | The NFR set being re-based | **104 unique identifiers across 109 rows** |
| `RQ-001` §3.12.4 | The ten PDPA obligations reallocated to `SWR-018`–`SWR-029` | 10 identifiers released |
| `RQ-001` §3.19 | The four verification methods | — |
| `RQ-004` §3.2 | Link type `T-05`, reciprocal | — |
| `RQ-002` §4.7, §4.12 | System-level performance and environmental requirements, which these must not duplicate | 71 `SYR` |
| `../../1000fix_ERP_Module/02_Architecture/02-05` §8 | Production sizing, from which capacity targets must be derivable | — |
| `../../project_content/13_Test_and_Acceptance_Content/TS-014` | Performance and load scenario pack consuming these targets | — |

### 2.3 Audit findings this document closes

| Finding | Source | How | Residual |
|---|---|---|---|
| `AP-02` | `00-07` | `NFR-090`/`091`/`092` no longer denote two requirements: the PDPA meanings move to `SWR-018`–`SWR-020` (`RQ-001` §3.12.4) and the maintainability meanings retain the identifiers | **Closed** |
| **`RQA-13`** | `RQ-001` §3.12.4 | `NFR-088` and `NFR-089` are duplicated as whole rows, and two NFR rows contaminate the residency-field table in `05-06` §6.4. Both corrected in §3.3 | **Closed** |
| **`RQA-05`** | `RQ-001` §2.1.3 | The quality model is re-based from 25010:2011 to 25010:2023 | **Closed** |
| **`RQA-12`** | `RQ-001` §3.11.1 | Two WCAG targets in force. §3.7 rules | **Closed** |
| **`RQA-20`** *(raised here)* | This document | **No NFR in the estate names the functional requirements it constrains.** `T-05` is unpopulated for all 104 | Open until binding completes |
| **`RQA-21`** *(raised here)* | This document | **The estate has no safety quality requirements**, because 25010:2011 had no Safety characteristic. `NFR-102`–`NFR-113` fill it | Open until `SC-002` threat model and `M59` HSE reconcile them |

---

# 3. Re-basing Rules

## 3.1 What re-basing does and does not do

| Does | Does not |
|---|---|
| Reorganise the set under the 2023 quality model | Change any target the programme has agreed |
| Resolve five identifier collisions | Renumber requirements that are not in collision |
| Retire identifiers reallocated to the functional space | Reissue any retired identifier |
| Add a measurement method to every requirement | Add measurement where the target is already instrumented — those are carried forward verbatim |
| Add the missing Safety characteristic | Import safety obligations that belong to `M59` HSE as operational content |
| Bind every NFR to the requirements it constrains | Bind at module granularity; the binding is per requirement |

**Rule `NF-01` — targets are carried forward unchanged.** Where `05-06` states a numeric target,
this document restates it exactly. Re-basing that also revises targets is indistinguishable from
scope movement, and would need a CR under `RQ-005` §6.

## 3.2 Allocation authority

**Rule `NF-02`.** The allocating authority for the `NFR-nnn` space transfers from `05-06` to this
document, per `RQ-005` §7.2. `05-06` remains the module estate's reference; where the two
disagree on a *target*, `05-06` wins (it is a module-estate artefact and the cross-repository rule
in `FOLDER_STRUCTURE.md` §9 gives it precedence on *what the system does*). Where they disagree on
*identifier allocation or classification*, this document wins.

**Rule `NF-03`.** No module may allocate an `NFR-nnn`. The rule already existed
(`_MODULE_TEMPLATE` §0: *"Cite, do not invent"*) and was breached five times; check `CT-09`
(`RQ-004` §7.3) now detects it.

## 3.3 Duplicate resolution

**Rule `NF-04` — the resolution rule.** Where one identifier denotes two requirements, the
**earlier-allocated meaning retains the identifier** and the later meaning is reallocated. Where
the two are the same requirement rendered twice, the duplicate row is deleted and the identifier
is untouched.

| ID | Meaning A | Meaning B | Resolution |
|---|---|---|---|
| `NFR-088` | Records retention per the statutory schedule (§6.2) | *Identical row repeated in §6.4* | **Duplicate row deleted.** `NFR-088` unchanged. The §6.4 occurrence was a table-contamination defect: two NFR rows had been pasted inside the residency-field table |
| `NFR-089` | SOC 2 / ISO 27001 readiness (§6.2) | *Identical row repeated in §6.4* | As above |
| `NFR-090` | *(§6.3)* Process personal data only on consent or a stated legitimate ground | *(§7)* Unit test coverage ≥ 80% on custom code; 100% on financial calculations | **Meaning B retains `NFR-090`** — the maintainability requirement is carried from the v1.0 baseline. Meaning A becomes **`SWR-018`** |
| `NFR-091` | *(§6.3)* Consent clear, explicit, specific, freely given | *(§7)* Every module ships with an operational runbook | **Meaning B retains `NFR-091`.** Meaning A becomes **`SWR-019`** |
| `NFR-092` | *(§6.3)* Transparency notice before or during processing | *(§7)* Distributed tracing with a single correlation id | **Meaning B retains `NFR-092`.** Meaning A becomes **`SWR-020`** |

> **Why the PDPA meanings move rather than the maintainability ones.** Both are defensible on
> seniority; the deciding argument is classification. "Capture consent", "issue a notice" and
> "execute an erasure" are **system functions** — things the software does — and belong in the
> functional space (`RQ-001` decision `D-08`). They were only ever in the NFR space because
> "compliance" was a section heading there. Moving them fixes the classification and the collision
> in one act.

## 3.4 Retirements

**Rule `NF-05`.** Identifiers reallocated to the functional space are **retired, never reissued**
(`PG-05`, `RQ-005` `RM-13`).

| Retired | Denoted | Now | Tombstone |
|---|---|---|---|
| `NFR-093` | Data-subject rights: access, portability, rectification, erasure, withdrawal | `SWR-021`, `SWR-022`, `SWR-023`, `SWR-024` — split, because it was four requirements in one identifier (characteristic W-05 *Singular*) | Retired 2026-08-18 |
| `NFR-094` | Breach notification to the National Data Management Authority | `SWR-025` | Retired 2026-08-18 |
| `NFR-095` | Processing records retained ≥ 5 years | `SWR-026` | Retired 2026-08-18 |
| `NFR-096` | Chief Data Officer appointment where a significant data fiduciary | `SWR-027` | Retired 2026-08-18 |
| `NFR-097` | Technical and organisational measures proportionate to risk | **Retained as `NFR-097`** — this one genuinely is a quality requirement, not a function. Re-classified under Security | Not retired |
| `NFR-098` | Flow controller obligations to processors by contract | `SWR-028` | Retired 2026-08-18 |
| `NFR-099` | Restrict large-scale transfer of sensitive PII; notify the Authority | `SWR-029` | Retired 2026-08-18 |

**Citation-update task.** `NFR-093`–`NFR-096`, `NFR-098` and `NFR-099` are cited in `05-06` §6.3
and in module files. Under `RQ-005` `RM-17` the retirement is not closed until check `CT-08`
returns zero live citations. Tracked as open item `OI-01`.

## 3.5 Measurement method — mandatory

**Rule `NF-06`.** Every quality requirement carries five fields. A target without them is an
aspiration.

| Field | Rule |
|---|---|
| `target` | The numeric or categorical value to be met |
| `instrument` | What measures it — named tool, dashboard, report or procedure |
| `sample` | What population and over what window (e.g. *p95 over a rolling 7 days, business hours only*) |
| `frequency` | How often it is measured, and whether continuously in production or at a gate |
| `threshold_action` | What happens on breach — alert, gate failure, incident, release block |

**Rule `NF-07`.** A percentile target states its percentile and its window. `≤ 400 ms` is not a
target; `≤ 400 ms at p95 over a rolling 7-day business-hours window` is.

## 3.6 Binding — link `T-05`

**Rule `NF-08`.** Every NFR names the functional requirements it constrains, and every constrained
requirement names the NFRs constraining it. The link is reciprocal (`RQ-004` `T-05`), and check
`CT-09` enforces it.

**Rule `NF-09`.** An NFR that constrains *every* requirement is declared **global** and is bound to
the requirement set rather than enumerated. Global NFRs are listed in §4.10. This prevents the
binding degenerating into 104 × 3,389 assertions.

**Rule `NF-10`.** An NFR constraining **no** requirement is an orphan and is either bound or
retired. `RQ-004` `CV-M10` counts them.

## 3.7 The WCAG ruling *(closes `RQA-12`)*

`NFR-073` specifies WCAG 2.1 AA; `UX-005` specifies WCAG 2.2 AA. Two live conformance targets is
itself a defect, because a portal can be released against either.

**Ruling.** **WCAG 2.2 Level AA governs.** It is the later W3C Recommendation and a superset of
2.1 AA — a product conforming to 2.2 AA conforms to 2.1 AA, so nothing already built is
invalidated. `NFR-073` is restated in §4.4 at 2.2 AA. The nine additional 2.2 success criteria —
notably target size, focus appearance, dragging movements and accessible authentication — are
material for a technician application used with gloves, and for a customer base with low digital
literacy.

---

# 4. The Quality Requirements

*Organised per ISO/IEC 25010:2023. Identifiers are carried forward from `05-06` unchanged except
where §3.3 or §3.4 states otherwise. Targets are carried forward verbatim under `NF-01`.*

## 4.1 Functional suitability

*Sub-characteristics: functional completeness · functional correctness · functional
appropriateness.*

| ID | Requirement | Target | Instrument | Verif. | Binds |
|---|---|---|---|:--:|---|
| `NFR-114` *(new)* | The delivered system shall satisfy every `P0` and `P1` requirement allocated to the wave being gated. | 100% of wave `P0`+`P1` at `Accepted` | `RQ-004` `CV-M8` | Inspection | Global |
| `NFR-115` *(new)* | Financial calculations shall produce results identical to the independently computed control figure. | Zero variance | Reconciliation suite | Test | `FR-FIN-*`, `FR-ARB-*`, `FR-TAX-*`, `FR-PAY-*` |
| `NFR-116` *(new)* | Statutory outputs — Mushak 6.3, Mushak 9.1, BEFTN files, payslips — shall be accepted by the receiving authority without exception. | Zero exceptions | Submission log | Demonstration | `FR-TAX-*`, `FR-PAY-*`, `FR-ARB-*` |

> Three new identifiers. `05-06` had no functional-suitability requirements because the 2011 model
> placed them in a characteristic the document did not use. Gate criterion `G3` already implies
> `NFR-116` (*"zero NBR exceptions"*) without stating it as a requirement.

## 4.2 Performance efficiency

*Sub-characteristics: time behaviour · resource utilisation · capacity.*

### 4.2.1 Time behaviour

| ID | Requirement | Target | Instrument | Verif. | Binds |
|---|---|---|---|:--:|---|
| `NFR-001` | ERP screen load under normal load | ≤ 2 s p95 | Synthetic monitoring | Test | Global — all UI |
| `NFR-002` | API response | ≤ 400 ms p95 | Gateway metrics | Test | Global — all API |
| `NFR-005` | Standard report generation | ≤ 20 s | Report timing log | Test | `FR-BID-*` |
| `NFR-031` | Customer 360 view load | ≤ 2 s | Instrumentation | Test | `FR-CPM-*`, `FR-CRM-*` |
| `NFR-032` | Booking availability calculation | ≤ 800 ms p95 | API metrics | Test | `FR-SRM-*`, `FR-FSM-*` |
| `NFR-033` | Dispatch board refresh | ≤ 1 s for 500 open jobs | Instrumentation | Test | `FR-FSM-*` |
| `NFR-034` | Live map update latency | ≤ 5 s from GPS emission | End-to-end trace | Test | `FR-FSM-*`, `FR-LOG-*` |
| `NFR-035` | Search results, any entity, including Bengali text | ≤ 600 ms p95 | Instrumentation | Test | Global — search |
| `NFR-036` | Technician app job list load on 3G | ≤ 8 s cold, ≤ 2 s warm | Field test | Test | `FR-POR-041…078` |
| `NFR-037` | Offline sync completion after 24 h offline | ≤ 30 s on 3G | Field test | Test | `SWR-031`, `FR-POR-041…078` |
| `NFR-038` | Executive dashboard load | ≤ 5 s | Instrumentation | Test | `FR-POR-171…194` |
| `NFR-039` | Warehouse analytical query | ≤ 10 s p95 | Warehouse metrics | Test | `FR-DAT-*`, `FR-BID-*` |
| `NFR-040` | Invoice generation from job closure | ≤ 5 s | Instrumentation | Test | `FR-ARB-*`, `FR-SRM-*` |
| `NFR-041` | Bulk operation, 1,000 records | ≤ 60 s with progress feedback | Load test | Test | Global — bulk |
| `NFR-042` | Payment confirmation round trip | ≤ 3 s p95 | Gateway metrics | Test | `FR-ARB-*`, `FR-REV-*` |
| `NFR-043` | Event delivery to consumer | ≤ 5 s p95 | Event platform metrics | Test | `SWR-035` |
| `NFR-044` | Nightly route optimisation, all technicians | ≤ 20 minutes | Job monitor | Test | `FR-FSM-*` |

### 4.2.2 Capacity

| ID | Requirement | Target | Instrument | Verif. | Binds |
|---|---|---|---|:--:|---|
| `NFR-003` | Concurrent internal users without degradation | 800+ | Load test | Test | Global |
| `NFR-004` | Concurrent customer portal users | 75,000+ | Load test | Test | `FR-POR-001…040` |
| `NFR-053` | Service order volume | 5 million/year by year 5 | Volume projection + load test | Test | `FR-SRM-*` |
| `NFR-054` | Device registry | 5 million assets | Load test | Test | `FR-AST-*` |
| `NFR-055` | Telemetry ingestion | 50,000 points/minute | Ingestion metrics | Test | `FR-IOT-*` |
| `NFR-056` | GPS ingestion | 400 technicians at 30-second intervals sustained | Ingestion metrics | Test | `FR-FSM-*` |
| `NFR-057` | Marketplace scale | 5,000 sellers, 50,000 listings | Load test | Test | `FR-MKP-*` |
| `NFR-060` | Document store | 50 TB with sub-10-second retrieval | Storage metrics | Test | `FR-DMS-*` |

### 4.2.3 Resource utilisation

| ID | Requirement | Target | Instrument | Verif. | Binds |
|---|---|---|---|:--:|---|
| `NFR-081` | Critical customer paths first load | ≤ 400 KB | Bundle analysis in CI | Test | `FR-POR-001…040` |
| `NFR-082` | Technician app battery consumption | ≤ 12% per 8-hour shift, excluding navigation | Field test | Test | `FR-POR-041…078` |

## 4.3 Compatibility

*Sub-characteristics: co-existence · interoperability.*

| ID | Requirement | Target | Instrument | Verif. | Binds |
|---|---|---|---|:--:|---|
| `NFR-026` | Every integration shall be served by a documented REST API | 100% of integrations have an OpenAPI 3.1 contract | CI contract validation | Inspection | Global — `IN-002` |
| `NFR-117` *(new)* | The platform shall co-exist with the pre-existing 1000FiX portal platform without requiring its replacement. | `CON-03` satisfied | Architecture review | Analysis | Global |
| `NFR-118` *(new)* | Every published API shall remain backward-compatible for the deprecation period defined in `IN-005`. | Zero breaking changes inside the notice period | Contract test suite | Test | Global — API |

## 4.4 Interaction capability

*Renamed from Usability in 25010:2023. Sub-characteristics: appropriateness recognisability ·
learnability · operability · user error protection · user engagement · **inclusivity** · user
assistance · self-descriptiveness.*

| ID | Requirement | Target | Instrument | Verif. | Binds |
|---|---|---|---|:--:|---|
| `NFR-016` | Full Bengali and English support in interfaces, notifications, reports and data entry | 100% string coverage | Translation coverage report | Test | Global — `SWR-013` |
| `NFR-017` | Technician app supported on Android 11+, 3 GB RAM, intermittent 4G | Runs on the minimum device | Device matrix test | Test | `FR-POR-041…078` |
| `NFR-018` | Offline mode with automatic sync on reconnection | Per `SWR-030`–`SWR-032` | Offline test suite | Test | `SWR-030`–`SWR-032` |
| `NFR-019` | Responsive design across mobile, tablet and desktop on all portals | No horizontal scroll from 320 px | Automated viewport test | Test | Global — portals |
| `NFR-020` | Low-bandwidth mode for field and rural operation | Functional on 3G | Field test | Test | `FR-POR-041…078`, `FR-POR-255…282` |
| **`NFR-073`** | **Every web portal shall meet WCAG 2.2 Level AA** *(restated from 2.1 — §3.7)* | Zero Level A or AA failures | Automated scan + manual audit | Test | Global — web portals |
| `NFR-074` | Bengali input including phonetic typing and voice-to-text on mobile | Both available | Demonstration | Demonstration | Global — mobile |
| `NFR-075` | New service agent reaches competence | ≤ 4 hours of training | Training assessment | Demonstration | `FR-FRD-*`, `FR-SRM-*` |
| `NFR-076` | Walk-in intake completion | ≤ 3 minutes | Timed observation, 20 samples | Test | `FR-FRD-*` |
| `NFR-077` | Any record reachable from any starting point | ≤ 4 clicks | Navigation audit | Inspection | Global — UI |
| `NFR-078` | Every error message states what happened and what to do next, in the user's language | 100% of messages | Content review | Inspection | `SWR-008` |
| `NFR-079` | Destructive actions require confirmation and are reversible where the action permits | 100% of destructive actions | UI review | Inspection | Global — `SWR-033` |
| `NFR-080` | Consistent design system across all 12 portals — one component library, one token set | One library | Component inventory audit | Inspection | `SWR-006` |

> **Inclusivity** is a 2023 sub-characteristic with no counterpart in the estate. `NFR-073` at
> 2.2 AA and `NFR-016` carry most of it; the residual — designing for low digital literacy and for
> users whose first written language is Bengali — is `UX-005` and `UX-007`'s to specify.

## 4.5 Reliability

*Sub-characteristics: faultlessness · availability · fault tolerance · recoverability.*

| ID | Requirement | Target | Instrument | Verif. | Binds |
|---|---|---|---|:--:|---|
| `NFR-006` | Uptime during Bangladesh business hours 09:00–22:00 BST | ≥ 99.9% | Availability monitor | Test | Global |
| `NFR-045` | Uptime 24×7 for managed services | ≥ 99.7% | Availability monitor | Test | `FR-RMS-*` |
| `NFR-046` | Customer portal availability | ≥ 99.9% | Availability monitor | Test | `FR-POR-001…040` |
| `NFR-048` | Payment path availability | ≥ 99.95% with multi-gateway failover | Gateway monitor | Test | `FR-ARB-*`, `IN-007` |
| `NFR-007` | Disaster recovery objectives | RPO ≤ 15 min, RTO ≤ 2 h | DR drill record | Test | Global — `SYR-045` |
| `NFR-008` | Zero-downtime deployment for planned changes | Standard for all releases | Deployment record | Demonstration | Global |
| `NFR-049` | Planned maintenance window | Outside 08:00–23:00 BST; ≤ 4 h/month; 72 h notice | Change record | Inspection | Global |
| `NFR-050` | Graceful degradation | Every P0 integration has a documented, tested manual fallback | Fallback test record | Demonstration | Global — `SYR-035` |
| `NFR-051` | DR drill | Full failover exercised twice yearly, results documented | Drill report | Demonstration | Global |
| `NFR-052` | Backup verification | Automated restore test weekly | Restore test log | Test | Global |
| `NFR-029` | Transactions ACID-compliant with full rollback | 100% | Transaction test suite | Test | Global |
| `NFR-030` | Automated backups | Daily/30-day, weekly/1-year, monthly/7-year | Backup catalogue | Inspection | Global |
| `NFR-047` | Technician app functional without connectivity | 24 hours | Offline test | Test | `SWR-030` |

## 4.6 Security

*Sub-characteristics: confidentiality · integrity · non-repudiation · accountability ·
authenticity · resistance.*

| ID | Requirement | Target | Instrument | Verif. | Binds |
|---|---|---|---|:--:|---|
| `NFR-011` | Role-based access control with field-level granularity | 100% of entities | Permission audit | Test | Global — `SWR-039` |
| `NFR-012` | MFA mandatory for admin, finance, HR and all privileged roles | 100% of privileged accounts | IdP configuration audit | Inspection | `SWR-010` |
| `NFR-013` | AES-256 at rest; TLS 1.2+ (1.3 preferred) in transit | 100% | Configuration scan | Inspection | Global |
| `NFR-014` | Complete immutable audit trail — who, what, when, before, after | 100% of business objects | Audit sample review | Test | `SWR-011`, `SWR-012` |
| `NFR-015` | Branch-level data isolation enforced at record level | Zero cross-branch leakage | Isolation test suite | Test | `SWR-039` |
| `NFR-061` | Field-level encryption for S3-classified data with separate key material | 100% of S3 fields | Key management audit | Inspection | `SWR-015`, `DA-005` |
| `NFR-062` | Secrets in a vault; never in code, configuration or logs | Zero findings | Secret scanning in CI | Test | Global |
| `NFR-063` | Malware scanning on every file upload before storage or serving | 100% of uploads | Scan log | Test | Global — upload |
| `NFR-064` | Segregation of duties enforced by the permission engine | 100% of `SOD-nn` | SOD test suite | Test | `SC-004` |
| `NFR-065` | Step-up authentication for sensitive actions | 100% of the declared sensitive set | Auth test suite | Test | `SWR-010` |
| `NFR-066` | Automated dependency, container and infrastructure vulnerability scanning in CI and production | Continuous | Scan reports | Test | Global |
| `NFR-067` | Annual penetration test with findings tracked to closure | Annual, zero unclosed critical | Pen-test report | Demonstration | Global |
| `NFR-068` | Rate limiting and bot protection on all public endpoints | 100% of public endpoints | Gateway configuration audit | Inspection | Global — public API |
| `NFR-069` | Session policy: 30-min idle external, 60-min internal, 12-h absolute | 100% of sessions | Session configuration audit | Test | `SWR-010` |
| `NFR-070` | All privileged sessions recorded | 100% | Session recording log | Inspection | Global |
| `NFR-071` | Non-production environments use masked data only | Zero unmasked personal data | Environment scan | Test | `SWR-017` |
| `NFR-072` | Security incident response with defined severities and breach-notification assessment | Per `SC-011` | Incident record | Demonstration | `SWR-025` |
| `NFR-097` | Technical and organisational measures for security, integrity and confidentiality proportionate to risk | Per the DPIA residual risk | DPIA review | Analysis | Global — PDPA |

## 4.7 Maintainability

*Sub-characteristics: modularity · reusability · analysability · modifiability · testability.*

| ID | Requirement | Target | Instrument | Verif. | Binds |
|---|---|---|---|:--:|---|
| `NFR-027` | No-code configuration for workflows, forms, thresholds and business rules | Per `SWR-037` | Configuration demonstration | Demonstration | `SWR-037` |
| `NFR-028` | Customisation without modifying core product code | Zero core modifications | Repository scan | Inspection | `CN-02`, `AS-05` |
| **`NFR-090`** | Unit test coverage ≥ 80% on custom code; 100% on financial calculations | 80% / 100% | Coverage report in CI | Test | Global — `L5` |
| **`NFR-091`** | Every module ships with an operational runbook | 100% of modules | Document register | Inspection | Global |
| **`NFR-092`** | Distributed tracing across all services with a single correlation id | 100% of service calls | Trace sampling | Test | Global — services |
| `NFR-119` *(new)* | No module shall read another module's tables directly. | Zero violations | Static analysis in CI | Analysis | `AS-01`, `CN-09` |
| `NFR-120` *(new)* | Every custom Odoo module shall conform to the anatomy defined in `AR-007`. | 100% of `cd_*` | Structure lint in CI | Inspection | Global — `L5` |

## 4.8 Flexibility

*Renamed from Portability in 25010:2023, with **scalability** moved here. Sub-characteristics:
adaptability · scalability · installability · replaceability.*

| ID | Requirement | Target | Instrument | Verif. | Binds |
|---|---|---|---|:--:|---|
| `NFR-009` | Growth headroom without re-architecture | 5× users and 10× data over 5 years | Capacity model | Analysis | Global |
| `NFR-010` | Elastic capacity for demand peaks | Automatic scaling for seasonal and promotional peaks | Autoscaling record | Test | Global |
| `NFR-058` | Branch scale | 200 branches without configuration redesign | Configuration model review | Analysis | `SWR-037` |
| `NFR-059` | Multi-entity scale | 10 legal entities across 5 countries | Entity model review | Analysis | `SWR-041`, `FR-GLO-*` |
| `NFR-121` *(new)* | A country pack shall be installable without modification to any module's code. | ≤ 12 weeks to stand up a country, per `BO-18` | Installation demonstration | Demonstration | `SWR-041` |
| `NFR-122` *(new)* | Any L6 commercial component shall be replaceable by an alternative without a change to any module's code. | Adapter boundary in place per component | Architecture review | Analysis | `02-05` §6 |

## 4.9 Safety *(new characteristic — closes `RQA-21`)*

*Sub-characteristics: operational constraint · risk identification · fail safe · hazard warning ·
safe integration. **The estate has no requirements under this characteristic**, because
ISO/IEC 25010:2011 did not contain it.*

| ID | Requirement | Target | Instrument | Verif. | Binds |
|---|---|---|---|:--:|---|
| `NFR-102` | The system shall block the creation of a consignment containing a restricted item — lithium battery, damaged cell, pressurised or flammable component — where the applicable carriage conditions are not recorded as met. | Zero non-compliant consignments | Consignment validation test | Test | `FR-LOG-037`, `SYR-069` |
| `NFR-103` | The system shall block assignment of a work order requiring a safety certification to a technician whose certification is not current at the scheduled date. | Zero uncertified assignments | Assignment test suite | Test | `FR-FSM-*`, `FR-LMS-*`, `BO-15` |
| `NFR-104` | The system shall record a lone-working status for any field visit outside declared safe hours or to a location flagged as elevated risk, and shall escalate on a missed check-in. | 100% of qualifying visits | Field session log | Test | `FR-FSM-*`, `FR-HSE-*` |
| `NFR-105` | The system shall present the hazard warnings applicable to a device class, a chemical or a procedure at the point of work, in the technician's language, before the step may be marked started. | 100% of hazard-classified steps | Workflow demonstration | Demonstration | `FR-FSM-*`, `FR-WSR-*`, `FR-HSE-*` |
| `NFR-106` | On failure of any safety-relevant control, the system shall fail to the state that blocks the unsafe action rather than the state that permits it. | 100% of safety controls fail closed | Fault-injection test | Test | Global — safety controls |
| `NFR-107` | The system shall make an executed data-destruction irreversible, and shall not present any interface that suggests recovery is possible after a destruction certificate has issued. | Zero recovery paths post-certificate | Design review + test | Test | `FR-DTS-008`, `FR-DTS-020`, `SWR-023` |
| `NFR-108` | The system shall require a second authorised approval before executing any irreversible action on customer property or customer data — destruction, disposal, recycling or purge. | 100% of irreversible actions | Approval audit | Test | `FR-DTS-*`, `FR-ESG-*`, `FR-TRF-*` |
| `NFR-109` | The system shall propagate a brand product-recall instruction to every affected serial within the interval agreed with the brand partner, and shall report the propagation completion state. | Per the partner SLA in `M09` | Recall execution report | Test | `FR-WTY-*`, `FR-SRM-073`, `FR-AST-*` |
| `NFR-110` | The system shall block release of a repaired device to a customer where a safety-critical quality check is unrecorded or failed. | Zero releases with an open safety check | QC gate test | Test | `FR-WSR-*`, `FR-QMS-*` |
| `NFR-111` | The system shall record the disposal route of every hazardous component it takes into custody, and shall block closure of a collection record without one. | 100% of hazardous components | Disposal record audit | Test | `FR-ESG-*`, `SYR-062` |
| `NFR-112` | The system shall warn a rider before dispatch where the planned load exceeds the vehicle's declared weight, volume or value limit. | 100% of overload conditions warned | Load planning test | Test | `FR-LOG-029` |
| `NFR-113` | The system shall identify, and present for review, every workflow whose failure could cause physical harm, financial irreversibility or statutory breach, and shall record the mitigating control for each. | 100% identified and reviewed at each wave gate | Safety review record | Analysis | Global — `SC-002` |

> **`NFR-113` is the risk-identification sub-characteristic and it has a dependency.** It cannot be
> discharged without the STRIDE threat model (`SC-002`), which does not exist — the phrase "threat
> model" occurs **zero** times in the 601-file estate. Safety and security risk identification
> share a method; running them separately duplicates effort and produces two different registers.

## 4.10 Global requirements

Declared global under `NF-09` — they constrain the requirement set as a whole and are not
enumerated per requirement:

`NFR-001` · `NFR-002` · `NFR-003` · `NFR-006` · `NFR-007` · `NFR-008` · `NFR-011` · `NFR-013` ·
`NFR-014` · `NFR-016` · `NFR-026` · `NFR-028` · `NFR-029` · `NFR-030` · `NFR-062` · `NFR-066` ·
`NFR-068` · `NFR-070` · `NFR-077` · `NFR-090` · `NFR-091` · `NFR-092` · `NFR-106` · `NFR-113` ·
`NFR-114` · `NFR-117` · `NFR-118` · `NFR-119` · `NFR-120`

## 4.11 Compliance requirements *(retained, re-classified)*

25010:2023 has no *Compliance* characteristic; compliance obligations distribute across Security,
Safety and Functional suitability, and the statutory register is `SC-008`. These are retained with
their identifiers and re-classified:

| ID | Requirement | Now classified under | Binds |
|---|---|---|---|
| `NFR-021` | Bangladesh VAT (Mushak) invoice format — Mushak 6.3 per the VAT and SD Act 2012 | Functional suitability | `FR-TAX-*`, `FR-ARB-*` |
| `NFR-022` | Bangladesh NBR income tax computation | Functional suitability | `FR-TAX-*`, `FR-PAY-*` |
| `NFR-023` | ICT Act 2006 and Cyber Security Ordinance 2025 | Security | Global |
| `NFR-024` | ISO 9001:2015 audit trail and documentation | Security (accountability) | `SWR-011` |
| `NFR-025` | ISO 27001 security control alignment | Security | Global |
| `NFR-083` | Bangladesh Labour Act compliance in HR and payroll | Functional suitability | `FR-PAY-*`, `FR-WFM-*` |
| `NFR-084` | Bangladesh e-waste and environmental handling rules | **Safety** | `FR-ESG-*`, `NFR-111` |
| `NFR-085` | Consumer protection obligations on marketplace transactions | Functional suitability | `FR-MKP-*` |
| `NFR-086` + `a`/`b`/`c` | Split-residency data architecture and its enforcement | Security (confidentiality) | `SWR-015`–`SWR-017`, `SYR-041`–`SYR-044` |
| `NFR-087` | Data-subject rights supportable within legal constraints | Functional suitability | `SWR-021`–`SWR-024` |
| `NFR-088` | Records retention per the statutory schedule, enforced by the system | Security (accountability) | `SWR-026`, `DA-006` |
| `NFR-089` | SOC 2 / ISO 27001 readiness for enterprise and multi-country expansion | Security | Global |
| `NFR-100` | Mushak 9.1 monthly VAT return by the 15th via the NBR VAT Online portal | Functional suitability | `FR-TAX-*` |
| `NFR-101` | Input VAT credit claimable only against a valid Mushak 6.3; the system blocks otherwise | Functional suitability | `FR-TAX-*`, `FR-APE-*` |

---

# 5. Requirements Retained in `05-06`

Four sets in `05-06` are **not** quality requirements and are not re-based here. Their treatment is
stated so that nobody concludes they were dropped:

| Set | Content | Treatment | Owner |
|---|---|---|---|
| `AS-01`–`AS-15` | Architecture standards restated as testable rules | **Retained in `05-06`.** They are architecture fitness functions, not quality requirements | `AR-012` |
| `DI-01`–`DI-08` | Data integrity rules | **Retained.** Several are reissued as functional requirements in `RQ-001` §3.12.2 (`SWR-033`–`SWR-036`) | `DA-001`, `RQ-001` |
| `OPS-01`–`OPS-08` | Operability standards | **Retained.** They are operating standards, owned by service operations | `SV-001`, `SV-003` |
| §9 Localisation standards | Bengali collation, numerals, dates, address hierarchy, fiscal year | **Retained.** These are design constraints (`RQ-001` §3.16 `CN-11`, `CN-12`) and interface standards (`UX-007`) | `UX-007` |
| §10 Environmental and device support | Browsers, OS versions, device minimums, peripherals | **Moved.** These are system requirements — `RQ-002` §4.11, §4.12 | `RQ-002` |
| §11 Testing standards | Coverage per level, critical journeys | **Moved.** These belong to the test strategy | `QA-001` |

---

# 6. Reconciliation and Counts

*Regenerated by counting the rows in §4 immediately before issue, per `PG-M10`.*

| Movement | Count |
|---|---:|
| Unique identifiers in `05-06` at 02:15 (+06) | **104** |
| Rows in `05-06` (including 5 duplicated) | 109 |
| Duplicate rows deleted (`NFR-088`, `NFR-089`) | −2 rows, 0 identifiers |
| Identifiers reallocated to `SWR` and retired (`NFR-093`, `094`, `095`, `096`, `098`, `099`) | **−6** |
| Identifiers whose PDPA meaning moved, retaining their maintainability meaning (`NFR-090`, `091`, `092`) | 0 net |
| Identifiers retained and re-classified (`NFR-097` and all compliance NFRs) | 0 net |
| **New identifiers — functional suitability** (`NFR-114`–`NFR-116`) | **+3** |
| **New identifiers — compatibility** (`NFR-117`, `NFR-118`) | **+2** |
| **New identifiers — maintainability** (`NFR-119`, `NFR-120`) | **+2** |
| **New identifiers — flexibility** (`NFR-121`, `NFR-122`) | **+2** |
| **New identifiers — safety** (`NFR-102`–`NFR-113`) | **+12** |
| **Total in this specification** | **104 − 6 + 21 = 119** |

**Distribution by 25010:2023 characteristic**

Regenerated by counting the identifier in every §4 row immediately before issue, per `PG-M10`.
§4 contains **116 rows**; row `NFR-086 + a/b/c` in §4.11 carries **four** identifiers, giving
**119**. The 14 rows of §4.11 are re-classified compliance requirements and are distributed into
the characteristics below according to the *"Now classified under"* column of that table — they
are **not** a tenth characteristic.

| Characteristic | From §4.1–§4.9 | From §4.11 re-classification | **Total** | New in this issue |
|---|---:|---:|---:|---:|
| Functional suitability | 3 | 7 | **10** | 3 |
| Performance efficiency | 27 | 0 | **27** | 0 |
| Compatibility | 3 | 0 | **3** | 2 |
| Interaction capability | 13 | 0 | **13** | 0 |
| Reliability | 13 | 0 | **13** | 0 |
| Security | 18 | 9 | **27** | 0 |
| Maintainability | 7 | 0 | **7** | 2 |
| Flexibility | 6 | 0 | **6** | 2 |
| **Safety** | 12 | 1 | **13** | **12** |
| **Total** | **102** | **17** | **119** | **21** |

*§4.11 distribution: Functional suitability — `NFR-021`, `022`, `083`, `085`, `087`, `100`, `101`
(7) · Security — `NFR-023`, `024`, `025`, `086`, `086a`, `086b`, `086c`, `088`, `089` (9) ·
Safety — `NFR-084` (1).*

> **This table was wrong at first drafting and is corrected here rather than silently.** The first
> version gave Security as 19 and listed the 14 compliance rows as a separate line marked *"counted
> above"* when they had not been — the roll-up was written from the section structure before the
> rows were finished. That is `PGD-A1-02` reproduced in miniature, by a document issued in the same
> repository that published `PG-M10` in response to it. Recorded as finding `RQA-32` in
> `_AUDIT/PGD-AUDIT-004`.

---

# 7. Decisions Recorded

| # | Decision | Options | Chosen | Rationale |
|---|---|---|---|---|
| D-01 | Which ISO 25010 edition | (a) 2011, matching `05-06`'s shape; (b) **2023** | **(b)** | 2011 is superseded. Citing a superseded model is the `H-01` defect class, and it is why Safety was missing |
| D-02 | Which meaning keeps `NFR-090`/`091`/`092` | (a) The PDPA obligations; (b) the maintainability requirements | **(b)** | The PDPA items are system functions and were misclassified; moving them fixes classification and collision together |
| D-03 | Whether to renumber the whole NFR set for a clean 25010:2023 layout | (a) Renumber; (b) retain identifiers, re-classify | **(b)** | `PG-05`: identifiers are permanent. A tidy numbering scheme is not worth invalidating every existing citation |
| D-04 | Whether re-basing may revise targets | (a) Yes, while we are here; (b) no — `NF-01` | **(b)** | Re-basing that revises targets is indistinguishable from scope movement |
| D-05 | WCAG 2.1 vs 2.2 | (a) 2.1 per `NFR-073`; (b) **2.2 per `UX-005`** | **(b)** | Later Recommendation and a superset; nothing already built is invalidated. Target size and dragging criteria matter for gloved field use |
| D-06 | Whether to add Safety requirements with no threat model in existence | (a) Wait for `SC-002`; (b) specify now, declare the dependency | **(b)** | Twelve safety obligations already exist in the business — batteries, certifications, recalls, destruction. They were unstated, not absent |
| D-07 | Binding granularity | (a) Per module; (b) per requirement, with a global class | **(b)** with `NF-09` | Per-module binding cannot answer "which requirements does `NFR-042` constrain"; the global class stops 104 × 3,389 assertions |
| D-08 | What happens to `AS-*`, `DI-*`, `OPS-*` | (a) Absorb into this document; (b) leave, and state where they live | **(b)** | They are fitness functions, data rules and operating standards. Absorbing them would make this document the home of everything non-functional-ish |

---

# 8. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| Q-01 | Who owns the safety review that `NFR-113` requires, and does it merge with `SC-002`? | CISO / HSE Manager | W1 | `NFR-113`, `SC-002` |
| Q-02 | What is the brand-agreed recall propagation interval for `NFR-109`? | Warranty Manager | W4 | `NFR-109` |
| Q-03 | Which actions are in the declared "sensitive set" requiring step-up authentication (`NFR-065`)? | CISO | W1 | `NFR-065`, `SWR-010` |
| Q-04 | Is `NFR-004` (75,000 concurrent portal users) derived from a volumetric model or asserted? | Solution Architect | W2 | `PE-006` capacity plan |
| Q-05 | Does the 2.2 AA ruling require re-testing anything already built? | UX Lead | W2 | Nothing yet — no portal is built |
| Q-06 | When do `NFR-093`–`NFR-099` citations get updated so the retirements can close? | Requirements Manager | W1 | `OI-01`, `CT-08` |
| Q-07 | Which instrument measures `NFR-082` battery consumption, and on which reference device? | Mobile Lead | W2 | `NFR-082` |

---

# 9. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | All nine ISO/IEC 25010:2023 characteristics are represented, with sub-characteristics named | §4.1–§4.9 |
| AC-02 | Every duplicate identifier is resolved by a stated rule, not by preference | §3.3, `NF-04` |
| AC-03 | Every reallocated identifier is retired with a tombstone and a citation-update task | §3.4, `NF-05`, `OI-01` |
| AC-04 | Every requirement carries a target, an instrument and a verification method | §4 tables |
| AC-05 | Every requirement is bound to what it constrains, or declared global | §4, §4.10, `NF-08`–`NF-10` |
| AC-06 | Targets are carried forward unchanged from `05-06` | `NF-01`; spot-check against `05-06` |
| AC-07 | The Safety characteristic is populated, with its dependency on `SC-002` stated | §4.9 |
| AC-08 | The WCAG conflict is ruled on with a stated rationale | §3.7 |
| AC-09 | Counts reconcile: 104 − 6 + 21 = 119 | §6, regenerated before issue |
| AC-10 | Content not re-based is accounted for, not silently dropped | §5 |

---

# 10. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `05-06` | The NFR set re-based here; retains precedence on targets |
| Upstream | `RQ-001` §3.12.4 | The ten PDPA obligations reallocated out of this space |
| Upstream | `RQ-005` §7.2 | The allocation authority transferred to this document |
| Lateral | `RQ-002` §4.7, §4.11, §4.12 | System-level performance and environment; not duplicated here |
| Lateral | `RQ-004` `T-05` | The reciprocal binding this document populates |
| Downstream | `AR-001` | Quality-attribute scenarios derived from these requirements |
| Downstream | `SC-001`, `SC-002` | Security architecture and threat model; `NFR-113` depends on `SC-002` |
| Downstream | `PE-006`, `PE-007`, `PE-008` | Capacity, DR and observability designs realising §4.2, §4.5 |
| Downstream | `QA-006`, `QA-007`, `QA-008` | Performance, security and accessibility test plans consuming §3.5 |
| Downstream | `UX-005`, `UX-007` | Accessibility and bilingual design realising §4.4 |
| Downstream | `AR-012` | Fitness functions enforcing `NFR-119`, `NFR-120` |
| Downstream | `M59` HSE | Operational safety procedures paired with §4.9 system controls |

---

# 11. References

**Within this repository**
[`RQ-001`](RQ-001_Software_Requirements_Specification.md) ·
[`RQ-002`](RQ-002_System_Requirements_Specification.md) ·
[`RQ-004`](RQ-004_Requirements_Traceability_Matrix.md) ·
[`RQ-005`](RQ-005_Requirements_Management_Plan.md) ·
[`RQ-009`](RQ-009_Business_Rules_Specification.md) ·
[`../PGD-000_Master_Register_of_Project_Guiding_Documents.md`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md)

**Workspace**
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md` ·
`../../1000fix_ERP_Module/02_Architecture/02-05` §8 ·
`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-02` §4 ·
`../../project_content/13_Test_and_Acceptance_Content/TS-014`, `TS-016`, `TS-017`

**External**

| Reference | Verified on |
|---|---|
| **ISO/IEC 25010:2023**, *SQuaRE — Product quality model* (2nd edition; revises the product quality model of 25010:2011) | 2026-08-18 |
| ISO/IEC 25012, *Data quality model* | 2026-08-18 |
| ISO/IEC 25023, *Measurement of system and software product quality* | 2026-08-18 |
| ISO/IEC/IEEE 29148:2018 §9.6.13, §9.6.14, §9.6.18 | 2026-08-18 |
| W3C WCAG 2.2, Level AA | 2026-08-18 |
| Personal Data Protection Act 2026 (Law 63 of 2026) | 2026-08-12 |
| VAT and Supplementary Duty Act 2012 — Mushak 6.3, 9.1 | 2026-08-12 |

---

# 12. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. Re-based onto ISO/IEC 25010:2023; five duplicate identifiers resolved (closes `AP-02`, `RQA-13`); six identifiers retired to the `SWR` space; measurement method and binding made mandatory; Safety characteristic populated with `NFR-102`–`NFR-113`; WCAG ruled at 2.2 AA. Total 119 | *Pending — `GV-002`* |

---

*`RQ-006` · Category 01 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
