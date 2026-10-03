---
id: QA-001
title: Master Test Strategy
category: 08 — Quality Engineering & Test
code: QA
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Head of Quality Engineering
approver: Chief Technology Officer with the Business Owners Forum
standards_basis: >
  ISO/IEC/IEEE 29119-1:2022 (general concepts) · ISO/IEC/IEEE 29119-2:2021 (test processes) ·
  ISO/IEC/IEEE 29119-3:2021 §7 (organizational test strategy) · ISO/IEC 25010:2023 (quality model) ·
  TMMi 2.0 (2026) · ISTQB risk-based testing
traces_to: >
  PGD-000 QA-001 · PGD-000 §2.1 item 17 · audit AUDIT-014 TS-01 (three coverage denominators) ·
  AUDIT-014 TS-02 (nine packs consumed a wave early) · AUDIT-014 TS-06 (three packs unexecutable) ·
  AUDIT-014 TS-07 (~1,700 items against 1 QA FTE) · 05-06 §11 · 06-02 §4 · 06-04 (planned, never written)
depends_on: >
  RQ-001 (denominator, requirement attributes) · RQ-004 (traceability model, coverage measures) ·
  GV-009 (gate evidence classes) · RQ-006 (NFR baseline) · BE-008 (sprint model)
verified_on: 2026-08-18
enumeration_timestamp: 2026-08-18 22:01 (+06)
priority: P0
needed_by: W1
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# QA-001 — Master Test Strategy

### Category 08 · Code `QA` · ISO/IEC/IEEE 29119-1:2022 · 29119-2:2021 · 29119-3:2021 §7 · TMMi 2.0

---

> **Before writing, read this.**
>
> 1. **`PG-01` Register-first.** Row `QA-001` exists in `PGD-000` Category 08, status ⛔ `P0` `W1`.
> 2. **`PG-03` Count, do not consult.** Every figure below was counted from the filesystem at
>    **2026-08-18 22:01 (+06)**. The estate at that moment is **621 source files** and
>    **121 files** in this repository.
> 3. **`PG-06` Cite standards.** §2.1 states conformance and every departure.
> 4. **`PG-M4` Verify citations.** Standard editions verified 2026-08-18 and listed in §18 with
>    their publication dates. **Three of the standards named in `_CATEGORY_OVERVIEW.md` were cited
>    at a superseded or undated edition** — corrected in §2.1.

---

## 1. Purpose

This document states **what "tested" means on this programme**: which levels of testing exist, who
owns each, what must be true before a level starts and before it may be declared finished, how much
of it is automated, in which environments it runs, who signs it off, and how much of it the
programme can actually afford.

`06-04_Testing_and_Quality_Strategy.md` was planned in `FOLDER_STRUCTURE.md` and never written.
In its absence the programme accumulated **18 test content packs** — genuinely good ones — with no
document above them. The consequence is measurable rather than theoretical:

| What the estate has | What it does not have | Consequence |
|---|---|---|
| 18 packs, ~1,700 executable items | A statement of how many QA people execute them | `AUDIT-014` `TS-07`: the arithmetic does not close, and nobody has said so at gate level |
| 12 test levels declared in `05-06` §11 | Entry and exit criteria for any of them | A level "finishes" when someone says it has |
| 70 gate criteria in `06-02` §4 | A rule binding each to the level that evidences it | `AUDIT-014` `TS-02`: nine packs are consumed a wave before they exist |
| Three coverage denominators in circulation | One | `AUDIT-014` `TS-01`, **Critical** — no coverage percentage may be quoted at all |
| Four packs that cannot be executed | A resourcing line for the accounts, stock, devices and people they need | `TS-05`, `TS-06`: the packs will be "passed" by being skipped |

**This document is not a re-write of `TS-001`.** `TS-001` is the *content* traceability standard and
it is sound; it defines script identifiers, evidence retention and the pack-to-gate mapping, and it
says so honestly where it cannot go further — *"This file can state the requirement. It cannot
provision it."* This document is the layer that provisions, resources, sequences and signs.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | The **test policy** — the four quality goals this programme tests against (§3) |
| 2 | **The thirteen test levels**, reconciled across `05-06` §11 and `TS-001` §4.1, with an owner each (§4) |
| 3 | **Risk-based prioritisation** — the risk model, and the depth each risk class buys (§5) |
| 4 | **The automation strategy** and the target ratio per level per wave (§6) |
| 5 | **Test environments** — seven, their data class, refresh policy and provisioning state (§7) |
| 6 | **Entry and exit criteria per level** (§8) |
| 7 | **Organisation, roles and sign-off authority** (§9) |
| 8 | **The capacity position** — counted demand against counted supply, and three costed closure routes (§10) |
| 9 | The **test process** aligned to ISO/IEC/IEEE 29119-2:2021 (§11) |
| 10 | **Suspension, resumption and truncation** — what happens when the arithmetic does not close (§12) |
| 11 | The **maturity target** and its assessment basis (§13) |

**Explicitly out of scope**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| The plan for each level — schedule, resources, deliverables | `QA-002` | 29119-3 separates the organizational test strategy (§7) from the test plan (§8). This is the strategy |
| Case derivation technique and the case repository | `QA-003` | This document says *which* levels exist; `QA-003` says how a case is derived for one |
| Test data provisioning, masking and lawful basis | `QA-004` | Named as a dependency in §7; specified there |
| Automation tooling, framework code, flake policy | `QA-005` | This document sets the **ratio** and the **layer strategy**; `QA-005` builds it |
| Performance workload models and volumetrics | `QA-006` | |
| Security case derivation and pen-test coordination | `QA-007`, `SC-009` | |
| Accessibility conformance testing | `QA-008` | |
| UAT participant selection and business sign-off protocol | `QA-009` | |
| Defect severity, triage and gate thresholds | `QA-010`, `TS-018` | |
| Coverage measurement and its published report | `QA-011` | |
| Test **content** — scenarios, scripts, personas | `project_content/13_TS` `TS-001`…`TS-018` | This document governs those packs; it does not restate them |
| The CI pipeline that runs the automated levels | `PE-004` ⛔ | **Unwritten.** §6.5 records the blockage rather than assuming the pipeline |
| Environment provisioning and sizing | `PE-002` ⛔ | **Unwritten.** §7 specifies what QA requires; `PE-002` builds it |
| Gate evidence classes and gate outcomes | `GV-009` | Consumed here, not redefined |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| **QA engineers** | The levels they own, the entry/exit criteria they enforce, the automation ratio they are measured against |
| **Developers** | Which levels they own outright — unit, integration, contract, event — and the coverage standard on each |
| Business owners and super-users | Where their signature is required (§9.3), and what it is a signature *on* |
| Wave-gate assessors (`GV-009`) | Which criterion is evidenced by which level, at which evidence class |
| Programme Manager and CFO | §10 — the measured gap between test demand and test supply, and the cost of each way of closing it |
| Implementation vendor | The quality obligations attaching to every delivered component |
| Security, Data Protection and Accessibility functions | The levels carrying their obligations, and the boundary with `SC-005`, `SC-009` and `UX-005` |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

> **Three of the standards named in `_CATEGORY_OVERVIEW.md` were cited at a superseded or undated
> edition.** This is the defect class behind critical findings `C-04` (DSA 2018 repealed twice),
> `H-01` (NIST SP 800-88 r1 withdrawn) and `M-01` (Odoo release date), and `PG-M4` exists to prevent
> it. Corrected here and registered for `RR-005`.

| Standard | Cited by the overview as | **Current edition, verified 2026-08-18** | How this document conforms | Departure and rationale |
|---|---|---|---|---|
| **ISO/IEC/IEEE 29119-1** | *"29119-1…5"*, undated | **29119-1:2022**, 2nd ed. — cancels 29119-1:2013 | §3–§4 use its concepts and vocabulary: test level, test type, test basis, test item, coverage item | None |
| **ISO/IEC/IEEE 29119-2** | undated | **29119-2:2021**, 2nd ed. | §11 maps the organizational, management and dynamic test processes to this programme's artefacts | **Departure:** the *organizational test process* is folded into this document rather than a separate policy, because the programme has no standing test function to hold one |
| **ISO/IEC/IEEE 29119-3** | **29119-3:2021** ✔ correctly dated in `PGD-000` §3 | 29119-3:2021, 2nd ed. | This document is the **organizational test strategy** of §7; `QA-002` supplies the §8 test plans; `QA-011` the §11 completion report | None |
| **ISO/IEC/IEEE 29119-4** | not cited | **29119-4:2021**, 2nd ed. | Consumed by `QA-003` for technique selection | Cited here for completeness; `QA-003` conforms |
| **ISO/IEC/IEEE 29119-5** | *"…5"*, undated | **29119-5:2024**, 2nd ed., December 2024 — **29119-5:2016 withdrawn** | Keyword-driven testing is **not adopted**; §6.3 states why | **Departure, declared:** keyword abstraction suits a large manual pack executed by non-programmers. This programme's automation is code-first (§6.2), and a keyword layer adds a translation surface with no owner |
| **ISO/IEC 25010** | *"ISO/IEC 25010"*, undated | **ISO/IEC 25010:2023** — adds *Safety*, restructures the characteristics | §3.2 maps the four quality goals to its characteristics | None |
| **TMMi** | *"TMMi"*, undated | **TMMi 2.0 (2026)**. Release 1.3 assessments end **1 August 2027** | §13 targets **Level 2 by the Wave 4 gate**, assessed against **v2.0** | **Departure:** no certification is sought. TMMi is used as a gap model |
| **OWASP ASVS** | *"OWASP ASVS 4"* | **ASVS 5.0.0, 30 May 2025** — ~350 requirements in 17 chapters | Delegated to `QA-007` and `SC-005` §5 `G-08`, both of which already cite 5.0.0 | *"ASVS 4"* is superseded and is corrected in this issue |
| **WCAG 2.2 AA** | *"WCAG 2.2 AA"* ✔ | **WCAG 2.2**, W3C Recommendation 5 October 2023, updated 12 December 2024; adopted as **ISO/IEC 40500:2025** on 21 October 2025 | Delegated to `QA-008` and `UX-005` | **`05-06` §11 and `TS-016` both say WCAG 2.1 AA.** The conflict is real, is ruled in `QA-008` §3, and is recorded here as `QAA-04` |

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| `05-06` §11 Testing Standards | `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md` | **12 test levels** with a coverage and tooling standard each; **15 critical journeys** |
| `05-06` §1–§3 | same | The performance, availability and scalability targets `QA-006` verifies |
| `06-02` §4 | `../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md` | **70 wave-gate acceptance criteria** across nine gates |
| `06-01` §4, §5 | `../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md` | The **QA staffing profile** and the sprint/release cadence |
| `TS-001` | `../../project_content/13_Test_and_Acceptance_Content/` | Script identifiers, traceability model, evidence retention, pack-to-gate mapping, **the 6-environment requirement** |
| `TS-002`…`TS-018` | same | 18 packs; **~1,700 executable items**, **620 distinct case identifiers**, counted in §4.4 |
| `AUDIT-014` | `../../project_content/_AUDIT/AUDIT-014_Category_13_TS_Content_Audit.md` | 17 findings, 1 critical, 14 open — the defect list this category exists to close |
| `RQ-001` §3.10.5 | `../01_Requirements_Engineering/` | **`CR-01`: 3,347 requirement rows**, with a reproduction command |
| `RQ-004` §5 | same | **`CV-01`: 3,347 + 42 `SWR` = 3,389**; ten coverage measures; `CV-04` |
| `GV-009` §4, §9 | `../00_Programme_Governance_and_Control/` | **Eight evidence classes `E1`–`E8`**; eleven standing criteria `SG-1`…`SG-11`; **interim rule `GA-12`** |
| `SC-002`, `SC-005`, `SC-009` | `../05_Security_Privacy_and_Compliance/` | **97 threats, 32 abuse cases**; gates `G-01`…`G-14`; the pen-test regime |
| `IN-008` | `../04_Integration_and_API_Engineering/` | **1,187 API operations · 988 domain events · ~800 pact pairs · 47 external integrations**; the **7th** environment |
| `BE-005`, `BE-006`, `BE-008` | `../07_Build_Engineering_and_Development_Standards/` | **331 components across 79 units**; the 23-criterion component DoD; the sprint model and DoR/DoD |
| `AR-012` | `../02_Architecture_and_Design/` | Fitness functions `FF-01`…`FF-100` — architectural checks that are **not** tests (§4.6) |

### 2.3 Audit findings this document closes

| Finding | Source | Severity | How this document closes it | Residual |
|---|---|:--:|---|---|
| `TS-01` | `AUDIT-014` | **CRITICAL** | §4.4 and §10.1 adopt the single denominator **3,389** fixed by `RQ-001` `CR-01` and `RQ-004` `CV-01`, and forbid any other. Measurement is specified in `QA-011` | Closes when `QA-011` publishes the first report at the Wave 1 gate |
| `TS-02` | `AUDIT-014` | High | §4.5 re-sequences all nine mis-waved packs **once, register-wide**, by rule `MTS-R6` — the correction `AUDIT-014` explicitly asked not to be done one file at a time | Needs a Category 13 register change; raised as `QAA-01` |
| `TS-05` | `AUDIT-014` | High | `MTS-D1` makes the 38 role accounts a named dependency with an owner, and `MTS-E5` makes them an environment rule rather than a test precondition | Provisioning is `M29` configuration work — `Q-02` |
| `TS-06` | `AUDIT-014` | High | §10.4 makes the physical dependencies of `TS-006`, `TS-008` and `TS-015` **named, costed lines** with owners, and `EN-03` blocks a gate without them | Cost approval sits with the CFO — `Q-02` |
| `TS-07` | `AUDIT-014` | High | §10 states demand and supply as counted figures and offers **three closure routes with costs**, rather than absorbing the gap silently | Decision required at W1 — `Q-01` |
| `TS-12` | `AUDIT-014` | Medium | §11.4 removes the `RF-003` dependency by ruling `QA-011` the consolidated coverage view | `RF-006` decision-log dependency remains, owned by Content |
| `PGD-000` §2.1 item 17 | Master register | — | *"`QA-001` unblocks all test execution; closes `TS-01`"* — discharged by this issue | — |
| `GA-12` | `GV-009` §9.3 | — | Recorded and **explicitly not adopted**. `QA-010` supersedes it with derived thresholds, per `GV-009`'s own instruction | Closes on `QA-010` issue |

---

## 3. Test Policy

### 3.1 The four quality goals

A test strategy that says "find defects" gives no basis for choosing what to test first. These four
goals are that basis, and every level, technique and priority in this document derives from one of
them. **They are ordered: where they conflict, the lower number wins.**

| # | Goal | What it means concretely here | Consequence of failure |
|:--:|---|---|---|
| **`MTS-G1`** | **Nothing the company must not do can happen** | Statutory outputs are correct (Mushak 6.3, 9.1, BEFTN, income tax); personal data stays inside its lawful boundary; no party reads data outside its scope; custody and destruction certificates cannot be bypassed | An unlawful act. Under the PDPA 2026 a scope breach is notifiable with a penalty; a non-compliant Mushak challan is an invalid invoice |
| **`MTS-G2`** | **Money and stock are right, and provably right** | Every posting reconciles to its source; stock cannot move without a valuation effect; three-way match blocks; payroll net pay is right first time | Silent and cumulative. `TS-004` records that these defects produce a ledger that *looks* reconciled |
| **`MTS-G3`** | **The 14 revenue streams transact end to end** | Each stream runs demand → delivery → cash → report with no shadow spreadsheet | The programme's own success criterion (`06-02` §5) is unproven |
| **`MTS-G4`** | **The people who use it can use it** | 500+ staff and 250,000+ customers/month can complete their primary task, in Bengali, on the device and connection they actually have | Adoption failure, which no defect count detects |

> **Why these and not ISO/IEC 25010's characteristics directly.** 25010:2023 is a *quality model* —
> it classifies attributes. A test strategy needs a *priority order*, and 25010 does not supply one.
> §3.2 maps the goals back to 25010 so nothing is lost.

### 3.2 Mapping to ISO/IEC 25010:2023

| Goal | 25010:2023 characteristics engaged | Primary levels (§4) | Primary gate criteria |
|---|---|---|---|
| `MTS-G1` | Security · compliance aspects of Functional suitability · **Safety** (new in 2023) | L9, L7, L4 | `G1-06`, `G1-07`, `G1-09`, `G3-04`, `G6-02`, `G6-03`, `SG-1`, `SG-2`, `SG-3` |
| `MTS-G2` | Functional correctness · Reliability | L1 (100% of financial calculations), L5, L7, L13 | `G3-01`, `G3-04`, `G3-05`, `G3-06`, `G3-08`, `G3-09`, `G5-01`, `G5-02`, `G7-02` |
| `MTS-G3` | Functional completeness · Interaction capability | L6, L5 | `G1-02`, `G4-10`, `G7-01`, `G8-03` |
| `MTS-G4` | Interaction capability (incl. accessibility) · Performance efficiency · Flexibility | L8, L10, L11, L12 | `G1-03`, `G1-08`, `G1-10`, `G2-01`, `G2-02`, `G2-03`, `G6-06` |

### 3.3 The nine rules that are not negotiable

| # | Rule | Why it is absolute |
|---|---|---|
| **`MTS-R1`** | **A coverage figure is published as a triple — numerator / denominator / enumeration timestamp — against the `CV-01` denominator and no other.** A bare percentage is not publishable | `TS-01`; `GA-04`. A figure on 2,930 and one on 3,389 differ by ~12 points at identical testing, which is enough to move a Go/No-Go |
| **`MTS-R2`** | **A test that did not run is not a test that passed.** Zero findings from an unexecuted scope is recorded as *not executed*, with the scope named | `GA-06`. Four of 18 packs cannot execute today; the failure mode is that they are quietly reported clean |
| **`MTS-R3`** | **Severity is never lowered to pass a gate**, and scope is never reduced without the reduction being logged at the gate it affects | `TS-018` `DF-04`, `TR-09`; `TS-013` `RS-13` |
| **`MTS-R4`** | **No production personal data reaches a non-production environment**, masked or otherwise, without a recorded lawful basis and the `QA-004` masking design | `NFR-071`; `SG-3`; PDPA 2026. This is `MTS-G1` applied to testing itself |
| **`MTS-R5`** | **Every level has a named human owner.** A level owned by "the team" has no entry criteria and no exit decision | `TS-001` §4.1 leaves L11 *"split — no single owner"* and records it as `O-05`. §4.3 assigns it |
| **`MTS-R6`** | **A test artefact's wave is `wave(earliest consuming gate) − 1`** — never the wave in which its subject matter matures | `TS-02`, and the same defect found in `KB`, `TR` and `HC` — 20 instances across four categories |
| **`MTS-R7`** | **Depth is bought with risk, not with enthusiasm** | §5.3. A team that tests everything to `RC-A` depth tests nothing to it by Wave 3 |
| **`MTS-R8`** | **The automation ratio is measured over the permanent regression core, never over all cases written** | §6.4. Otherwise writing more manual cases improves the ratio by shrinking its denominator |
| **`MTS-R9`** | **Reducing depth below what §5.3 buys requires a signed truncation with a named accepter, and it never applies to an `RC-A` population** | §12.3 |

---

## 4. The Test Levels

### 4.1 Reconciling two level sets

`05-06` §11 tables **12** levels. `TS-001` §4.1 is titled *"The twelve test levels and who owns
each"* and tables **13 numbered rows** — it correctly added **SIT**, which `05-06` omits, and did
not update its own heading.

> **Counted 2026-08-18 22:01 (+06).** `05-06` §11: 12 data rows. `TS-001` §4.1: 13 numbered rows.
> The discrepancy is in the heading, not the content, and `TS-001`'s reasoning for adding SIT is
> correct and is adopted verbatim below. Recorded as finding **`QAA-02`**, remediated by a heading
> correction in `TS-001` — **not** by deleting the row.

**This document rules: there are thirteen levels.** They are `TS-001` §4.1's set, renumbered
`L1`–`L13` so a level can be cited unambiguously, plus the two things `TS-001` could not supply —
an **owner for L11** and **entry and exit criteria for every level** (§8).

### 4.2 The thirteen levels

| # | Level | Test basis | Coverage standard (`05-06` §11) | Owner (`MTS-R5`) | Automated | Content pack |
|:--:|---|---|---|---|:--:|---|
| **L1** | **Unit** | Component design; `AR-003` SDD | ≥ 80% of custom code; **100% of financial and tax calculations** | Engineering Lead | **Full** | none — engineering-owned |
| **L2** | **Integration** | `IN-001`; module §12 interfaces | All module-to-module contracts; all external integrations against sandboxes | Engineering Lead | **Full** | none |
| **L3** | **Contract** | `IN-002` — **1,187 operations** | Every published API validated against its OpenAPI specification (`AS-07`) | Integration Lead | **Full** | `IN-008` §4 — ~800 pacts |
| **L4** | **Event** | `IN-003` — **988 events** | Every producer/consumer pair for schema compatibility and idempotency (`AS-08`, `DI-05`) | Integration Lead | **Full** | `IN-008` §5 |
| **L5** | **SIT** | Module category boundaries | Category-boundary business chains | **QA Lead** | Partial → 85% by W5 | `TS-003`, `TS-004`, `TS-005` |
| **L6** | **End-to-end** | The **15 critical journeys** + 14 revenue streams | Every critical business journey, automated, run nightly | **QA Lead** | **Full by W3** | `TS-012` — 18 scenarios, 20 executions |
| **L7** | **UAT** | `RQ-001` requirements at `P0`/`P1` | Every `P0` and `P1` requirement, by named business super-users | **Business Owners Forum** with QA | **Never** — §6.3 | `TS-006`…`TS-011` |
| **L8** | **Performance** | `05-06` §1–§3 | Every NFR performance target **at 1.5× expected peak**, before each wave gate | Platform Engineering with QA | **Full** | `TS-014` — 37 scenarios |
| **L9** | **Security** | `SC-002` — **97 threats, 32 abuse cases** | SAST, DAST, dependency scanning every build; penetration test per `SC-009` | Security Lead with QA | Partial — `QA-007` | `TS-017` |
| **L10** | **Accessibility** | `UX-005` — 55 A+AA criteria | Automated scan **plus manual audit per portal**, before each portal release | Content Design Lead with QA | ~30% ceiling — `QA-008` | `TS-016` |
| **L11** | **Localisation** | `UX-007`; `BN-*`; `05-06` §10 | Translation completeness, Bengali rendering, formatting, layout under text expansion | **Localisation Lead** — *assigned here* | Partial | `TS-002`, `TS-016`, `BN-018` |
| **L12** | **Offline** | `AR-010`; `UX-006` | 24-hour offline operation with a scripted conflict scenario set, before each mobile release | Mobile Lead with QA | Partial — the field half cannot be | `TS-015` — 33 scripts |
| **L13** | **Data migration** | `MG-001`…`MG-004` ⛔ | Reconciliation and control totals on every load, before every cutover | Data Migration Lead | Full for totals | `DM-013`; forms in `TS-018` |

### 4.3 The three assignments this document makes

`TS-001` identified three gaps in the ownership model and could not close them from the content
layer. They are closed here.

| Gap | `TS-001` record | Ruling |
|---|---|---|
| **L11 Localisation has no owner** — split across `TS-002` (data), `TS-016` (assistive technology) and `BN-018` (wording) | `O-05` | **The Localisation Lead owns L11 end to end**, including the layout-under-expansion test that `UX-007` specifies and no pack currently holds. QA supplies the harness; Content supplies the strings; the *decision* that a screen passes is the Localisation Lead's |
| **L1–L4 have no content pack, which could read as a coverage failure** | §4.1 note | **Correct and deliberate.** These four produce tool output, not content a business user signs. Their evidence class is `E5`, and their exit criterion is a CI result, not a signature (§8.3) |
| **SIT vs Integration** — `05-06` has no SIT row | §4.1 note | **Adopted verbatim from `TS-001`:** L2 proves a *contract* holds; L5 proves a *business chain crossing a category boundary* produces the right business outcome. The first is a schema question; only the second can be signed by an owner |

### 4.4 The measured size of the test estate

*Counted from the 18 packs at 2026-08-18 22:01 (+06), not quoted.*

| Pack | Distinct case identifiers in §3 | Identifier scheme |
|---|---:|---|
| `TS-003` SIT A–D | 56 | `SIT-<cat>-nnn` |
| `TS-004` SIT E–G | 42 | `SIT-<cat>-nnn` |
| `TS-005` SIT H–K | 56 | `SIT-<cat>-nnn` |
| `TS-006` UAT service ops | 83 | `UAT-R<nn>-nnn` |
| `TS-007` UAT commercial | 61 | `UAT-R<nn>-nnn` |
| `TS-008` UAT supply chain | 59 | `UAT-R<nn>-nnn` + `SIT-E-nnn` |
| `TS-009` UAT finance | 47 | `UAT-R<nn>-nnn` |
| `TS-010` UAT people | 37 | `UAT-R<nn>-nnn` |
| `TS-011` UAT portals | 72 | `UAT-R<nn>-P<nn>-nnn` |
| `TS-012` E2E | 17 | `E2E-nn` |
| **`TS-013` Regression** | **0** | **none — derived per release** |
| `TS-014` Performance | 38 | `PERF-NFR-nnn-nn` |
| `TS-015` Offline | 33 | `OFF-nnn` |
| **`TS-016` Accessibility** | **0** | **none — 21 checks × 9 portals, tabulated** |
| `TS-017` Security | 19 | `SEC-nnn`, `SEC-SOD-nn` |
| **Total identified** | **620** | **six incompatible schemes** |

**`AUDIT-014` `TS-07` enumerates ~1,700 executable items. This count finds 620 of them carry an
identifier.** The difference is not a discrepancy — `TS-013`'s regression set is derived per
release, `TS-016` is 189 checks in a matrix, and `TS-017` derives ~734 cases by set arithmetic over
`05-04`. **But an item with no identifier cannot be traced, reported, counted or declared covered**,
which places roughly **two-thirds of the test estate outside `MTS-R1`.** This is what `QA-003` §5
exists to fix. Registered as finding **`QAA-03`**.

### 4.5 The nine mis-waved packs — corrected once *(closes `TS-02`)*

`AUDIT-014` `TS-02` found nine packs registered a wave later than the gate that first consumes them,
and instructed: *"Do not correct them one at a time."* The single correction is below, and it
replaces the **basis**, not just the values, under rule `MTS-R6`.

| Pack | Registered | First consumed | Criterion | **Corrected to** |
|---|:--:|:--:|---|:--:|
| `TS-003` SIT A–D | W2 | W1 | `G1-02` | **`Now`** |
| `TS-004` SIT E–G | W3 | W1/W2 | `G1-05`, `G2-06` | **`Now`** |
| `TS-005` SIT H–K | W4 | W1 | `G1-06`, `G1-07` | **`Now`** |
| `TS-008` UAT supply chain | W3 | W2 | `G2-06`, `G2-07` | **W1** |
| `TS-012` E2E | W2 | W1 | `G1-02`, `G1-03` | **`Now`** |
| `TS-013` Regression + smoke | W2 | W1 | Monthly production cadence from `P03` go-live | **`Now`** |
| `TS-014` Performance | W2 | W1 | `G1-10` | **`Now`** |
| `TS-016` Accessibility | W2, **`P2`** | W1 | `05-06` §11 per-portal release; `P03` ships W1 | **`Now`, `P1`** |
| `TS-017` Security | W2 | W1 | `G1-06`, `G1-07`, **`G1-09`** | **`Now`** |

**`TS-016`'s priority is also corrected**, from `P2` to `P1`: `PS-04` WCAG conformance is
contractual and `NFR-073` is `P1`, so a `P2` on a contractual requirement is a scale error, not a
judgement. This requires a Category 13 register change, raised as **`QAA-01`** with the Programme
Content Lead.

### 4.6 What is *not* a test level

Recorded so a future reader does not add a fourteenth level by mistake.

| Activity | Where it lives | Why it is not a test level |
|---|---|---|
| **Fitness functions `FF-01`…`FF-100`** | `AR-012` | They assert *architectural* properties — layering, dependency direction, identifier issue. A violation is drift, not a defect against a requirement. Same pipeline, different owner |
| **`SC-005` gates `G-01`…`G-14`** | `SC-005` §5 | Secure-development gates on the *change*, not on the *system*. `QA-007` consumes their output; it does not own them |
| **Static analysis and linting** | `BE-002` | Style and rule conformance |
| **Usability research** | `UX-008` | Task-based research with real users; it produces design findings, not defects against requirements. §9.4 `MTS-S5` gives the routing rule when it produces both |
| **Non-conformances and incidents** | `M23`, `M66` | `TS-018` §4.2's three-record boundary. Three severity scales exist because three different questions are being asked |

---

## 5. Risk-Based Prioritisation

### 5.1 Why risk-based is not optional here

§10 shows demand far exceeding supply in the two waves that matter most. **When demand exceeds
supply, testing is prioritised whether or not anybody decides to prioritise it.** The only choice is
whether the prioritisation is *stated and signed*, or *improvised by whoever runs out of time
first*. This section states it.

### 5.2 The risk model

Risk = **impact × likelihood**, both assessed on the *business* consequence, not the technical one.

**Impact** — assessed by the module business owner, never by QA alone:

| Class | Definition | Anchored to |
|:--:|---|---|
| **I4 Statutory / irreversible** | An unlawful act, a notifiable breach, an irreversible physical or financial event | `MTS-G1`; PDPA 2026; VAT and SD Act 2012; Labour Act |
| **I3 Financial / custodial** | Money, stock or custody is wrong, and wrong silently | `MTS-G2` |
| **I2 Operational** | A core task cannot be completed, or only via a workaround | `MTS-G3` |
| **I1 Experience** | Degraded, inconvenient, cosmetic | `MTS-G4` |

**Likelihood** — assessed by engineering, from four measurable signals:

| Class | Signal |
|:--:|---|
| **P4 Very likely** | New custom code · a module-category boundary · a first-of-kind integration · a concurrency or offline path |
| **P3 Likely** | Custom code over standard Odoo · a changed contract · a migrated data domain |
| **P2 Possible** | Configuration of standard Odoo · a stable contract |
| **P1 Unlikely** | Unchanged OCA or core Odoo behaviour, covered upstream |

### 5.3 What each risk class buys *(`MTS-R7`)*

| Risk class | I × P | Depth purchased | Automated | Independent review |
|:--:|---|---|:--:|:--:|
| **`RC-A` Critical** | I4 any · I3 × P3–P4 | Every applicable `QA-003` §4 technique; **negative and boundary cases mandatory**; abuse cases where `SC-002` names a threat; **no sampling** | Mandatory, in the permanent regression core | **Required** — `E6` |
| **`RC-B` High** | I3 × P1–P2 · I2 × P3–P4 | Equivalence partitioning, boundary values, decision tables, state transitions; negative cases on every hard rule | Mandatory | On exception |
| **`RC-C` Medium** | I2 × P1–P2 · I1 × P4 | Positive path plus boundary values; sampling permitted **with the sample recorded** | Where cheap | No |
| **`RC-D` Low** | I1 × P1–P3 | Exploratory, time-boxed, charter-based; findings raised as defects | No | No |

### 5.4 The eight populations pre-assigned `RC-A`

Not assessed per item — `RC-A` by definition, because their failure mode is `MTS-G1` or `MTS-G2`.

| # | Population | Size | Source |
|:--:|---|---|---|
| 1 | Financial and tax calculation paths | 100% coverage mandated | `05-06` §11 L1; `DI-01` |
| 2 | Statutory outputs — Mushak 6.1/6.2/6.3/6.6/9.1, BEFTN, income tax | all | `SC-008`; `TS-009` |
| 3 | **Denied `role × portal` cells requiring a negative test** | **379 of 456** | `05-04` §2, enumerated by `AUDIT-014` `X8` |
| 4 | Class `H` hard business rules in wave scope | all | `05-05`; `RQ-009` |
| 5 | Residency-classified fields | all | `DA-005`; `SC-007`; `NFR-086c` |
| 6 | Offline conflict and sync paths | all | `AR-010`; `NFR-047` |
| 7 | Custody and destruction chains | all | `G6-02`, `G6-03` |
| 8 | `P0` requirements | **22.7% of the baseline ≈ 769** | `RQ-001`; `RQ-004` `CV-04` |

> **`CV-04` is a gate criterion, not a report.** A wave gate at which **any** `P0` requirement has
> no test case fails, regardless of the aggregate percentage. Aggregates hide exactly the
> requirements that matter, because `P0`s are 22.7% of the set and 100% of the regulatory exposure.

---

## 6. Automation Strategy

### 6.1 The argument, stated once

**3,389 requirements across 9 waves and ~80 sprints, released monthly to production within a wave**
(`06-01` §5), cannot be regression-tested by hand. The regression surface grows every wave and never
shrinks. By Wave 5 it exceeds any manual team, and the programme then chooses between slowing
releases and shipping untested. **The purpose of automation here is to prevent that choice from
arising**, not to save effort.

`TS-013` defines a regression pack and a smoke checklist. **Nothing automates them.**

### 6.2 The layer strategy

| Layer | Levels | Target share of automated cases | Rationale |
|---|---|---:|---|
| **Unit** | L1 | **~70%** | Fastest, most precise, no environment. The 100%-of-financial-calculations rule lives here |
| **API / contract / event** | L2, L3, L4 | **~25%** | 1,187 operations and 988 events are cheap to assert and stable across UI change |
| **UI / journey** | L5, L6 | **~5%** | Slowest and most brittle. Reserved for the 15 critical journeys and the category-boundary chains only a UI can prove |

> **Departure from the classic pyramid, declared.** Classic advice is 70/20/10. This programme sets
> UI lower and API higher because **twelve portals and four apps consume 1,187 operations**: a
> defect at the seam is far likelier than a defect in a widget, and the seam is testable without a
> browser. `IN-008` already owns the pact layer; `QA-005` must not duplicate it.

### 6.3 What is deliberately not automated

| Not automated | Why | Consequence accepted |
|---|---|---|
| **L7 UAT** | The point of UAT is a business judgement by the person who carries the consequence. An automated UAT is a system test with a signature attached | UAT stays the largest manual cost — 352 scripts |
| **The manual half of L10** | Automated scans find a minority of WCAG failures; most are content failures found only by using the product as an assisted user does | `QA-008` §6 resources it; `UX-005` names the 11 criteria no design and no build can discharge |
| **The field half of L12** | A lab test with aeroplane mode does not reproduce a technician in Gazipur whose signal came and went four times across a nine-hour shift | `TS-015` `L-01`…`L-08` — §10.4 `MTS-D5` |
| **Exploratory testing at `RC-D`** | Automating exploration removes what makes it valuable | Charter-based, time-boxed |
| **Keyword-driven abstraction (29119-5:2024)** | §2.1 — automation here is code-first; a keyword layer adds a translation surface with no owner | Declared departure |

### 6.4 The automation ratio, and how it is measured *(`MTS-R8`)*

> The ratio is **automated cases in the permanent regression core ÷ cases in the permanent
> regression core**, per level, published with its denominator (`MTS-R1`). It is **never** measured
> as a share of all cases written, because writing more manual cases would then improve the ratio by
> shrinking it.

| Level | W1 | W3 | W5 | W9 | Rationale |
|---|:--:|:--:|:--:|:--:|---|
| L1 unit, code coverage | ≥ 80% | ≥ 80% | ≥ 80% | ≥ 80% | `05-06` §11; a fixed standard, not a ramp |
| L1 financial paths | **100%** | **100%** | **100%** | **100%** | `DI-01`; no tolerance at any wave |
| L2–L4 | 100% | 100% | 100% | 100% | These levels exist only as automation |
| L5 SIT | 20% | 60% | 85% | 90% | Rises as the UI stabilises |
| L6 E2E | 40% | **100%** | 100% | 100% | `05-06` §11 requires nightly runs; nightly is unattainable manually |
| L8 Performance | 100% | 100% | 100% | 100% | |
| L9 Security | 60% | 80% | 85% | 85% | The pen-test and abuse-case halves stay human |
| L10 Accessibility | 30% | 30% | 35% | 35% | The ceiling is a property of WCAG, not of effort |
| L12 Offline | 40% | 60% | 70% | 70% | The field half cannot be automated |
| **Permanent regression core** | **50%** | **80%** | **90%** | **90%** | The number that decides whether monthly releases survive |

### 6.5 The dependency this strategy cannot discharge

> **⚠ `PE-004` CI/CD Pipeline Design does not exist.** Nine of thirteen levels are defined here as
> *automated, running in CI*. **There is no CI design**, and `PE-003` records **zero occurrences of
> "Terraform"** across the estate. `AR-012` carries the same dependency and states it the same way.
>
> This is not a reason to weaken the strategy. It is a reason to record that the strategy's
> mechanism is owned by an unwritten document in a category nobody has started, and that the Wave 1
> automation targets in §6.4 are **unachievable until `PE-002` and `PE-004` issue.**
> Raised as **`QAA-05`** and as `Q-03`.

---

## 7. Test Environments

### 7.1 The requirement

`TS-001` §4.7 specifies six environments and states plainly: *"no environment inventory exists
anywhere in the repository… This file can state the requirement. It cannot provision it."*
`IN-008` then found a **seventh** — the partner sandbox `FR-IPF-019` requires and `AUDIT-016`
`AP-12` records as missing. This document consolidates both.

| # | Env | Levels served | Data class (`DA-005`) | Refresh | Owner | **Provisioned?** |
|:--:|---|---|---|---|---|:--:|
| 1 | `DEV` | L1 during development | Synthetic subset | On demand | Engineering | **No** |
| 2 | `CI` | L1, L2, L3, L4 | Fixtures only | Per commit | Platform Engineering | **No** |
| 3 | `SIT` | L5, L9, L11, L13 | Full `TS-002` synthetic set | Per release | QA Lead | **No** |
| 4 | `UAT` | L6, L7, L10 | Full `TS-002` set, **frozen for the cycle** | Per wave | QA Lead with Business Owners | **No** |
| 5 | `PERF` | L8 | Production-*shaped* volumes (`NFR-053` 5M orders, `NFR-054` 5M assets) | Per wave gate | Platform Engineering | **No** |
| 6 | `TRAIN` | Training; `TR-003` `DS-14` screenshots | Full `TS-002` set, resettable per cohort | Per cohort | L&D Lead | **No** |
| 7 | **`SANDBOX`** | Partner certification (`IN-008` §7) | Masked, representative | Per release | Integration Lead | **No** |

**Provisioned: 0 of 7**, counted at 2026-08-18 22:01 (+06). The estate contains no environment
inventory, no IaC and no sizing beyond `02-05` §8's production compute table.

### 7.2 The three separations that cannot be collapsed

Recorded because each will be proposed as a saving, and each has a specific consequence.

| Proposed merge | Why it fails |
|---|---|
| `SIT` = `UAT` | A UAT cycle needs **frozen data and a stable release**; SIT needs a moving one. Merging means either UAT executes against changing data — voiding `TX-08` and every signature on it — or SIT stops for the 4–6 week UAT window each wave |
| `TRAIN` = `UAT` | Trainees destroy data by design, and `TR-003` `DS-14` requires reproducible screenshots. A cohort would invalidate a UAT signature |
| `PERF` = anything | `NFR-003` requires 800 concurrent internal users and `NFR-004` 75,000 concurrent portal users **at 1.5×**. A shared environment cannot host that, and a performance result from a shared environment is not evidence (`GA-02`) |

### 7.3 The six rules that bind every environment

| # | Rule | Source |
|---|---|---|
| `MTS-E1` | **No production personal data in any non-production environment**, in any form, without the `QA-004` masking design and a recorded lawful basis | `NFR-071`; `SG-3`; `MTS-R4` |
| `MTS-E2` | **No unmasked residency-classified data leaves its permitted store**, in any environment, in any region | `NFR-086c`; `SC-007`; `DA-005` |
| `MTS-E3` | **Configuration is promoted, never hand-edited.** An environment whose configuration diverged is one whose test results do not transfer | `OPS-02` |
| `MTS-E4` | **Evidence is produced in the environment the criterion names.** Evidence from `dev` does not discharge a production criterion | `GA-02` |
| `MTS-E5` | **Every environment holds the 38 role accounts** its levels require, with record rules, field restrictions and SoD constraints applied | `TS-05`; `05-04` §10 criterion 6; `MTS-D1` |
| `MTS-E6` | Environment readiness is an **entry criterion at T−6 weeks**, not a discovery at the gate | `EN-06`; `GA-11` |

---

## 8. Entry and Exit Criteria

### 8.1 Why these are stated per level

A single set across thirteen levels fits none of them. L1 exits on a CI result, L7 on a signature,
L8 on a distribution. Universal rules are in §8.4.

### 8.2 Entry criteria

| Level | May not start until… |
|---|---|
| **L1** | The component's `component.yaml` exists and declares its requirements (`BE-006`); the build compiles |
| **L2** | L1 exit met both sides; both contracts published in `IN-002`/`IN-003` |
| **L3** | The OpenAPI specification is published and versioned (`IN-005`); the consumer's pact exists (`CT-01`) |
| **L4** | The event schema is registered (`IN-003`); the consumer's message-shape pact exists (`CT-06`) |
| **L5 SIT** | L1–L4 exit met for every module in the chain; `SIT` provisioned with the `TS-002` set; **the 38 role accounts exist**; the chain's business rules are catalogued in `RQ-009` |
| **L6 E2E** | L5 exit met for every category the journey crosses; `UAT` holds a stable release |
| **L7 UAT** | L5 and L6 exit met; **super-users named and released** (`EN-04`); executors trained (`UA-03`); UAT data frozen; **the §10.4 physical dependencies are present** |
| **L8** | `PERF` provisioned at production-shaped volume; the `QA-006` workload model is approved |
| **L9** | `SC-002` current for the wave's scope; `SC-005` gates `G-01`…`G-10` green; **role accounts provisioned** |
| **L10** | `UX-005` conformance design issued for the surface; **an accessibility reviewer is engaged** |
| **L11** | Bengali strings complete for the surface; `UX-007` layout rules published |
| **L12** | The mobile build installs on the three floor-spec devices; **field logistics booked** |
| **L13** | `MG-002` profiling complete for the source; control totals agreed both sides |

### 8.3 Exit criteria

| Level | Exits when… | Evidence class |
|---|---|:--:|
| **L1** | ≥ 80% line coverage of custom code **and 100% of financial and tax calculation paths**, zero failing tests | `E5` |
| **L2** | Every module-to-module contract and every external integration exercised against a sandbox, zero failures | `E5` |
| **L3** | 100% of the wave's published operations verified against their specification; every pact verified | `E5` |
| **L4** | Every producer/consumer pair in the wave passes schema compatibility, idempotency and replay | `E5` |
| **L5** | Every scenario in the wave's SIT scope executed; **zero open `S1`; open `S2` within the `QA-010` threshold**; every class `H` rule has a passing negative case | `E5` + `E1` |
| **L6** | Every critical journey in scope passes end to end, nightly, for **five consecutive nights** | `E1` + `E5` |
| **L7** | Every `P0` and `P1` requirement in scope executed by a named super-user and **signed**; every defect triaged; conditional acceptances recorded with dated remediation | `E4` + `E1` |
| **L8** | Every applicable NFR target met **at 1.5× peak**, with the **distribution** published — not the mean | `E2` + `E5` |
| **L9** | Zero open critical or high findings in scope; **every denied `role × portal` cell in the wave has a passing negative test**; `SC-002` abuse cases executed | `E5` + `E6` |
| **L10** | Automated scan clean; **manual audit completed by a competent reviewer**; conformance statement updated | `E5` + `E6` |
| **L11** | 100% translation on delivered screens (`G1-08`); no layout failure under Bengali expansion; formatting and numerals correct | `E2` + `E1` |
| **L12** | 24-hour offline with **zero data loss**; sync ≤ 30 s on 3G; conflict scenario set passes; **measured in the field** | `E3` + `E5` |
| **L13** | Control totals tie both sides; every variance outside tolerance explained and signed | `E7` |

### 8.4 The four universal rules

| # | Rule |
|---|---|
| `MTS-X1` | **An exit criterion is met by evidence, not by assertion** (`GA-01`). The class in §8.3 is the minimum |
| `MTS-X2` | **A level may exit with a recorded, signed exception. It may not exit silently.** The exception names the scope not covered, the risk accepted, the accepter and the review date, and it is carried to the gate |
| `MTS-X3` | **Exiting a level does not close it.** Any change to the wave's scope re-opens every level below the change |
| `MTS-X4` | **A level whose entry criteria were never met cannot exit at all** — it is recorded as *not executed* (`MTS-R2`), a materially different gate input from *passed* |

---

## 9. Organisation, Roles and Sign-off

### 9.1 The test organisation

| Role | Filled? | Accountability |
|---|:--:|---|
| **Head of Quality Engineering** | **No** | Owns this strategy, the automation ratio and the gate quality opinion. **`06-01` §4's team model has no such role** — it has *QA Engineer* only |
| **QA Lead** | **No** | Owns L5, L6; runs triage (`TR-02`); owns the case repository |
| QA Engineers | **1 FTE at W1** | Execute L5, L6, L8, L9, L10, L12; build automation |
| Engineering Lead | Yes | Owns L1, L2 |
| Integration Lead | Yes | Owns L3, L4 |
| Security Lead | Yes | Owns L9 with QA |
| **Localisation Lead** | Yes | **Owns L11 — assigned by §4.3** |
| Content Design Lead | Yes | Owns L10 with QA |
| **Accessibility reviewer** | **No** | `TS-016` **cannot be executed without one** — `AUDIT-014` `TS-06` |
| Data Migration Lead | Yes | Owns L13 |
| Business Owners Forum | Yes | Owns L7 and its signature |

> **Two of the eleven roles this strategy depends on do not exist in the programme's own team
> model**, and a third — the accessibility reviewer — is the stated reason a pack cannot execute.
> `GV-009` §5.3 already records four *assessor* roles that do not exist; this is the same defect on
> the test side. Registered as **`QAA-06`**.

### 9.2 RACI by level

| Level | R | A | C | I |
|---|---|---|---|---|
| L1–L2 | Developers | Engineering Lead | QA Lead | Head of QE |
| L3–L4 | Developers | Integration Lead | QA Lead, Architect | Head of QE |
| L5 | QA Engineers | **QA Lead** | Module business owners, Architect | Business Owners Forum |
| L6 | QA Engineers | **QA Lead** | Programme Manager | Steering Committee |
| L7 | **Super-users** | **Business Owners Forum** | QA Lead, Content Design | Steering Committee |
| L8 | QA + Platform | Platform Engineering | Architect | CTO |
| L9 | QA + Security | **Security Lead** | CISO, external tester | CTO, Steering Committee |
| L10 | Accessibility reviewer | **Content Design Lead** | QA Lead, `UX-005` owner | CTO |
| L11 | Localisation testers | **Localisation Lead** | Content Design | Business Owners Forum |
| L12 | QA + technicians | Mobile Lead | Operations Director | CTO |
| L13 | Migration team | Data Migration Lead | CFO, module owners | Steering Committee |

### 9.3 Sign-off authority

> **Rule `MTS-S1`.** A signature is on a *statement*, not on a document. The signatory is accountable
> for the statement being true, and `GA-01` requires the evidence behind it to be dated, attributable
> and reproducible.

| What is signed | Statement being signed | Signatory | Class |
|---|---|---|:--:|
| Level exit, L1–L4 | *"The automated suite for this scope passed at the stated coverage"* | Engineering Lead / Integration Lead | `E5` |
| Level exit, L5 | *"Every business chain in scope produces the correct business outcome"* | QA Lead | `E5`+`E1` |
| Level exit, L6 | *"Every critical journey in scope runs end to end"* | QA Lead with Programme Manager | `E1` |
| **UAT acceptance** | *"I have executed these scripts myself and the system does what my role requires"* | **The super-user, by name** — never a delegate | `E4` |
| Wave UAT acceptance | *"My function accepts this wave's scope"* | Module business owner | `E4` |
| Security level exit | *"Zero open critical or high findings in this scope, and the scope is stated"* | Security Lead, **countersigned by an independent reviewer** | `E5`+`E6` |
| Statutory outputs | *"These outputs comply and I will file on them"* | **CFO** — `TS-009`'s position, adopted | `E4`+`E8` |
| Gate quality opinion | *"The wave's quality position is as described, including what was not tested"* | **Head of Quality Engineering** | `E6` |

### 9.4 Independence

| Rule | Provision |
|---|---|
| `MTS-S2` | **A developer does not sign the exit of a level testing their own change** at `RC-A` or `RC-B` |
| `MTS-S3` | **The penetration tester is external to 1000FiX and independent of the build vendor** (`SC-009` `IN-1`) |
| `MTS-S4` | **The gate quality opinion is independent of the delivery schedule.** Where the Head of QE's opinion and the Programme Manager's recommendation differ, **both go to the Steering Committee**; the difference is not resolved below it |
| `MTS-S5` | Where `UX-008` usability research produces a finding that is *also* a requirement defect, it is routed to **both** `UX-008` and `TS-018` triage under `TR-06`, and never converted into one to avoid the other |

---

## 10. The Capacity Position

> **This section is the reason a test strategy exists.** `AUDIT-014` `TS-07` states the problem;
> this section states its size in counted figures and the three ways it can be closed. It is written
> for the CFO and the Programme Manager, not for QA.

### 10.1 Demand — counted

| Population | Count | Repeats |
|---|---:|---|
| Requirement rows in the baseline (`CV-01`) | **3,389** | — |
| `P0` requirements needing a test case before any gate (`CV-04`) | **~769** (22.7%) | — |
| Executable items in the 18 packs (`TS-07`) | **~1,700** | several sets per release |
| Of which carry an identifier today (§4.4) | **620** | — |
| API operations requiring a contract test | **1,187** | every build |
| Domain events requiring a pair test | **988** | every build |
| Provider–consumer pacts | **~800** | every build |
| Components requiring the `BE-006` 23-criterion DoD | **331 across 79 units** | once each |
| **Denied `role × portal` cells requiring a negative test, no sampling permitted** | **379** | every wave |
| Accessibility checks | **189** (21 × 9 portals) | **per portal release** |
| Security cases derived from `05-04` | **~734** | per wave |
| Production releases across the programme | **~33** (monthly within a wave) | each needs regression + smoke |

### 10.2 Supply — counted

`06-01` §4 staffs *QA Engineer* at 1, 1, 2, 2, 2, 2, 2, 2, 1 FTE across W1–W9. Wave lengths from
`06-01` §3 are 4, 4, 5, 5, 4, 4, 4, 4, 2 months.

| Wave | FTE | Months | QA FTE-months |
|:--:|---:|---:|---:|
| W1 | 1 | 4 | 4 |
| W2 | 1 | 4 | 4 |
| W3 | 2 | 5 | 10 |
| W4 | 2 | 5 | 10 |
| W5 | 2 | 4 | 8 |
| W6 | 2 | 4 | 8 |
| W7 | 2 | 4 | 8 |
| W8 | 2 | 4 | 8 |
| W9 | 1 | 2 | 2 |
| **Total** | | **36** | **62** |

**62 QA FTE-months for the whole programme**, of which **8 fall in W1–W2** — the two waves carrying
`G1`'s twelve criteria, seven of the nine mis-waved packs, and the first production go-live.

### 10.3 The gap, stated plainly

At a conventional 12 manual executions per person-day with evidence capture, **8 FTE-months ≈ 170
person-days ≈ 2,040 executions** across W1–W2 — before any automation is written, any framework is
built, any defect is retested, any environment is provisioned, and any of the 38 role accounts is
specified.

**Demand in W1–W2 alone**, at `RC-A`/`RC-B` depth, is the `G1` and `G2` slice of ~1,700 items, plus
379 negative cells, plus 189 accessibility checks per portal release, plus the first regression core,
plus retest. **The arithmetic does not close, and no amount of prioritisation closes it**, because
§5.4's pre-assigned `RC-A` populations alone exceed the available days.

> **What this document will not do.** It will not silently scope down to fit. `AUDIT-014` `TS-07`
> records that *"the packs are honest about it rather than silently scoping down"*, and this strategy
> holds that line. §12.3 makes truncation a signed act with a named accepter.

### 10.4 The five unresourced execution dependencies

Each is a *physical* precondition, not a preference, and each blocks a named gate criterion. **None
appears in any programme plan.**

| # | Dependency | Blocks | Named in | Owner |
|:--:|---|---|---|---|
| **`MTS-D1`** | **38 role accounts per environment**, with record rules, field restrictions and SoD applied | `G1-06`, `G1-09`; **the whole of `TS-017`**; L5, L7, L9 entry | `TS-05`; six packs independently | `M29` owner with Security Lead |
| **`MTS-D2`** | **An accessibility reviewer** competent to run the manual WCAG audit, including with a Bengali screen reader | Every portal release; L10 | `TS-06`; `UX-005` | Content Design Lead |
| **`MTS-D3`** | **Physical UAT kit** — 1366×768 laptop, thermal receipt printer, barcode scanner, signature pad, mid-range Android 11 / 3 GB device | `G1-03` timed intake; `TS-006` | `TS-006` precondition 10 | Operations Director |
| **`MTS-D4`** | **40 labelled real parts across 3 locations** — one serialised, one expired-shelf-life, one hazardous — plus branch scanner, label printer and a vehicle | `G2-06`, `G2-07`; `TS-008` | `TS-008` `UA-23` | Inventory Manager |
| **`MTS-D5`** | **Field logistics** — six named locations including a no-signal basement and a moving vehicle, three mobile operators, three floor-spec devices, full-shift durations, real technicians as executors, a server-side observer, **and a safety briefing covering test personnel** | `G2-02`, `G2-03`; `NFR-036`, `NFR-037`; `TS-015` | `TS-015` §2.2 `L-01`…`L-08`, `O-06` | Programme Manager |

> **`MTS-D5` carries an unanswered safety question.** Testers will work at six locations, in a moving
> vehicle and on customer premises, **deliberately without connectivity and therefore without a means
> of contact**. `SP-030` governs technicians and does not mention test personnel. This is a duty-of-
> care matter before it is a test-logistics matter. Raised as **`QAA-07`** and `Q-04`.

### 10.5 The three closure routes

**One must be chosen at the Wave 1 gate.** Choosing none is choosing route C by default, without the
record that makes C acceptable.

| Route | What it means | Cost | Consequence |
|---|---|---|---|
| **A — Resource to demand** | Staff QA against the enumerated volume: a Head of QE, a QA Lead, ~4 FTE at W1–W2 rising to ~6, an accessibility reviewer, and `MTS-D1`…`D5` funded | Highest; quantifiable in `GV-007`'s model | The gates mean what they say |
| **B — Automate ahead of demand** | Fund `QA-005` and `PE-004` as **Wave 0** work, before feature delivery, so L1–L4, L6 and L8 are automated before the regression surface grows | Front-loaded; ~2 FTE for one wave | Delays W1 feature scope. **Recommended** — the alternative compounds |
| **C — Reduce scope with the reduction logged** | A documented risk-based reduction: sampling at `RC-C`/`RC-D`, L10 deferred to per-wave rather than per-release, `RC-A` protected absolutely | Lowest | Acceptable **only** if exclusions are logged at each gate under `TS-013` `RS-13` and `MTS-R3`. **Silent truncation reported as a full pass is the outcome this document exists to prevent** |

> **Recommendation, recorded as `QA-001-D-05`.** Route **B**, with Route **C** applied to `RC-C` and
> `RC-D` only, and `MTS-D1`…`D5` funded regardless — because they are preconditions of gate criteria
> already committed, not of testing depth.

---

## 11. The Test Process

### 11.1 Alignment to ISO/IEC/IEEE 29119-2:2021

| 29119-2 process | Where it lives here | Artefact produced |
|---|---|---|
| **Organizational test process** | This document | The strategy, the levels, the policy |
| **Test management — planning** | `QA-002` per level; `BE-008` per sprint | Level test plans; sprint test scope |
| **Test management — monitoring and control** | `QA-011` measures; `TS-018` triage | Coverage report; defect profile |
| **Test management — completion** | §11.3; `QA-011` §6 | Level completion report; gate evidence pack |
| **Dynamic test — design and implementation** | `QA-003` | Test conditions, cases, procedures, data requirements |
| **Dynamic test — environment set-up** | §7; `PE-002` ⛔ | Environment readiness record |
| **Dynamic test — execution** | The 18 packs; `QA-005` automation | Execution log, evidence per `TS-001` §4.6 |
| **Dynamic test — incident reporting** | `TS-018`; `QA-010` | Defect record with severity, priority, owner, target |

### 11.2 Cadence

| Activity | Frequency | Source |
|---|---|---|
| L1–L4 automated suites | **Every commit** | `05-06` §11 |
| L6 E2E suite | **Nightly** | `05-06` §11 |
| Regression core + smoke | **Every deployment** — fortnightly to staging, monthly to production | `06-01` §5; `TS-013` |
| Defect triage | **Daily during a test cycle**, weekly otherwise; `S1` on discovery | `TS-018` `TR-01` |
| Coverage report | **Fortnightly** for `CV-M1`, `CV-M5`, `CV-M9`; **per gate** for the rest | `RQ-004` §5.2 |
| L8 Performance | **Before each wave gate**, at 1.5× peak | `05-06` §11 |
| L10 Accessibility | **Before each portal release** | `05-06` §11 — see §10.3 on feasibility |
| L12 Offline | **Before each mobile release** | `05-06` §11 |
| Penetration test | Per `SC-009` §7 — more than annually; first at W1 and **not** a general test | `SC-009` |
| Strategy review | **At every wave gate**, and on any change to the level set | §13 |

### 11.3 The level completion report

Every level exit produces one, and it is the unit the gate evidence pack is assembled from
(`GA-07`, from T−6 weeks).

| Field | Content |
|---|---|
| Scope | The requirements, components and packs in scope, **with counts** |
| Executed / planned | Counted, with the denominator (`MTS-R1`) |
| **Not executed** | **Named, with the reason** — `MTS-R2` makes this mandatory |
| Pass / fail | Per case, per `GA-01` |
| Defects | Raised by severity; open by severity; deferred with the accepter |
| Coverage | Per `QA-011`, as a triple |
| Exceptions | Every `MTS-X2` exception, with accepter and review date |
| Evidence location | Under `GV-011` configuration control, retained per `GA-08` |
| Signature | Per §9.3 |

### 11.4 Consolidated coverage — and the dependency this removes

`AUDIT-014` `TS-12` records that **18 packs carry 18 local traceability tables with no consolidated
view**, and blocks that view on `RF-003`, an unwritten Category 99 *content* file.

> **Ruled: `QA-011` is the consolidated coverage view, not `RF-003`.** Coverage over 3,389
> engineering requirements is an engineering artefact generated from the `RQ-004` RTM, not a content
> register. `RF-003` remains useful for content-to-content traceability and is not cancelled. This
> removes one of the four W1 blockers `TS-12` lists.

---

## 12. Suspension, Resumption and Truncation

### 12.1 Suspension

Testing at a level is **suspended** — not merely slowed — when:

| # | Trigger | Level(s) |
|---|---|---|
| `MTS-U1` | An `S1` defect blocks more than 30% of the level's remaining cases | Any |
| `MTS-U2` | The environment diverges from its configuration baseline (`MTS-E3`) | Any |
| `MTS-U3` | Unmasked production personal data is found in a non-production environment | **All levels, immediately** — `MTS-R4`, `SG-3` |
| `MTS-U4` | The build under test changes mid-cycle without a re-baselined scope | L5, L6, L7 |
| `MTS-U5` | UAT data is modified during a frozen cycle | L7 |
| `MTS-U6` | An executor is untrained against `UA-03` | L7 |

### 12.2 Resumption

Resumption requires the trigger cleared, **the affected cases re-executed from the start of the
affected chain** — not resumed mid-chain — and the suspension recorded in the level completion
report. `MTS-U3` additionally requires the data destroyed, an incident raised under `SC-011`, and the
DPIA reviewed under `SC-003`.

### 12.3 Truncation — the signed act *(`MTS-R9`)*

> Testing may be reduced below the depth §5.3 buys **only** by a recorded truncation. A truncation
> states: the scope removed, the risk class of what was removed, the business risk accepted, **the
> named accepter**, and the gate at which it is reported. It is signed by the Head of Quality
> Engineering **and** the accountable business owner, and it is carried into every subsequent gate
> report until reversed.
>
> **A truncation is never applied to an `RC-A` population** (§5.4). Those exist because their failure
> mode is unlawful or irreversible, and no schedule pressure changes that.

---

## 13. Maturity Target

| Attribute | Position |
|---|---|
| Model | **TMMi 2.0 (2026)**. Release 1.3 assessments end 1 August 2027; adopting 1.3 now would buy an obsolete baseline |
| Current level, assessed against v2.0 | **Level 1 (Initial)** — no test policy, no test strategy, no test planning process, no test monitoring, no defined test environment. Test *design* is unusually strong for Level 1, which is this estate's characteristic shape |
| Target | **Level 2 (Managed) by the Wave 4 gate, Month 18** — test policy and strategy (this document), planning (`QA-002`), monitoring and control (`QA-011`, `TS-018`), design and execution (`QA-003`), test environment (§7 + `PE-002`) |
| Stretch | Level 3 (Defined) by Wave 8 — adds test organisation, test training, lifecycle integration and non-functional testing as defined process areas |
| Certification | **Not sought.** Recorded as `QA-001-D-06` |
| Assessment | Self-assessment at the W2 gate; independent assessment at W4 (`E6`) |

> **Honest reading of Level 1.** A TMMi Level 1 organisation is not one that tests badly — it is one
> whose testing outcome depends on who is doing it. This estate has excellent test *content* and no
> test *process*, which is exactly Level 1 with an unusually good ceiling. Level 2 is reachable in
> four documents and one hiring decision.

---

## 14. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `QA-001-D-01` | The number of test levels | (a) 12 per `05-06` §11; (b) 13 per `TS-001` §4.1's table; (c) a new taxonomy | **(b) — thirteen** | `05-06` omits SIT, and `TS-001`'s reasoning for adding it is correct. A third taxonomy is the drift `CP-01` prevents | `TS-001`'s heading is corrected; `05-06` §11 gains a cross-reference. `QAA-02` |
| `QA-001-D-02` | The coverage denominator | (a) 2,930; (b) 3,343; (c) **3,389** per `CV-01`; (d) defer | **(c)** | `RQ-001` `CR-01` counted it on disk with a reproduction command. The others state no provenance | Closes `TS-01`. Every QA document uses it and no other |
| `QA-001-D-03` | Automation shape | (a) classic 70/20/10 pyramid; (b) **70/25/5 with API weighted up**; (c) UI-led | **(b)** | 1,187 operations and 988 events across 12 consumers make the seam the likeliest defect site, and it is testable without a browser | `QA-005` builds to this; `IN-008` owns the pact layer and is not duplicated |
| `QA-001-D-04` | Keyword-driven testing (29119-5:2024) | (a) adopt; (b) **decline, declared** | **(b)** | Automation here is code-first; a keyword layer adds a translation surface with no owner | Declared departure in §2.1 |
| `QA-001-D-05` | Closing the capacity gap | (a) resource to demand; (b) **automate ahead as Wave 0**; (c) reduce scope with logging | **(b) primary, (c) for `RC-C`/`RC-D` only**, `MTS-D1`…`D5` funded regardless | The regression surface compounds; every wave that starts without automation makes the next worse. `MTS-D1`…`D5` are preconditions of already-committed criteria | W1 feature scope moves. Decision required at the W1 gate — `Q-01` |
| `QA-001-D-06` | TMMi | (a) certify at Level 2; (b) **gap model, no certification**; (c) ignore | **(b)** | Certification consumes budget §10 shows is needed for execution | Self-assessment W2, independent assessment W4 |
| `QA-001-D-07` | Owner of L11 Localisation | (a) QA; (b) Content Design; (c) **Localisation Lead** | **(c)** | The failing artefact is a Bengali rendering or layout decision, and only Localisation can rule on it | Closes `TS-001` `O-05` |
| `QA-001-D-08` | Whether to adopt `GA-12`'s defect thresholds | (a) adopt; (b) **decline and defer to `QA-010`** | **(b)** | `GV-009` §9.3 states its own numbers are *"conventional, not derived"* and asks `QA-010` not to simply adopt them | `GA-12` stays in force until `QA-010` issues |
| `QA-001-D-09` | Where the consolidated coverage view lives | (a) `RF-003` content register; (b) **`QA-011`** | **(b)** | Coverage over engineering requirements is generated from the RTM, not maintained as content | Removes one of `TS-12`'s four W1 blockers |

---

## 15. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | **Which closure route in §10.5 is taken, and is it funded?** | CFO with CTO and Programme Manager | **W1 gate** | Every level's achievability; `QA-002` scheduling |
| `Q-02` | Are `MTS-D1`…`D5` funded as named lines in the wave plan? | Programme Manager | **W1** | `G1-03`, `G1-06`, `G1-09`, `G2-02`, `G2-03`, `G2-06` |
| `Q-03` | When do `PE-002` and `PE-004` issue? Nine levels are defined as running in a pipeline that has no design | CTO with Platform Engineering | **W1** | §6.4 targets; §7 provisioning; `AR-012` shares this dependency |
| `Q-04` | Who owns duty of care for test personnel working off-site without connectivity? | HSE Lead with Programme Manager | **Before L12 field execution** | `TS-015`; `MTS-D5` |
| `Q-05` | Does the programme appoint a Head of Quality Engineering and a QA Lead, or does the QA Engineer role absorb both? | CTO | **W1** | §9.1; `MTS-S4` independence |
| `Q-06` | Is WCAG **2.2** AA the conformance target, superseding `05-06` §11 and `TS-016`'s 2.1? | CTO with Content Design Lead | **W1** | `QA-008`; `UX-005`; the `PS-04` contractual position |
| `Q-07` | Is the pen-test budget approved for more than one engagement a year? | CFO with CTO | W1 | `QA-007`; `SC-009` `Q-04` — the same question, recorded on both sides |

---

## 16. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | Exactly one coverage denominator is named, sourced and reproducible | §4.4, §10.1; `CV-01`; `RQ-001` §3.10.5 |
| `AC-02` | Every test level has a named owner, entry criteria and exit criteria | §4.2, §8.2, §8.3 — 13 of 13 |
| `AC-03` | Every level's exit carries an evidence class from `GV-009` §4.1 | §8.3 — 13 of 13 |
| `AC-04` | The automation ratio is defined, measurable and targeted per wave | §6.4; `MTS-R8` |
| `AC-05` | Every environment the levels require is specified with data class and provisioning state | §7.1 — 7 of 7, **0 provisioned** |
| `AC-06` | The capacity position is counted demand against counted supply, with costed closure routes | §10 |
| `AC-07` | Every unresourced execution dependency is named with the criterion it blocks and an owner | §10.4 — 5 of 5 |
| `AC-08` | Every standard cited carries its current edition and a verification date | §2.1, §18 — 9 of 9, **3 corrections** |
| `AC-09` | The nine mis-waved packs are corrected by a stated rule, once | §4.5; `MTS-R6` |
| `AC-10` | Truncation is defined as a signed act with a named accepter | §12.3; `MTS-R9` |

**Definition of done.** Complete when every criterion above is met, `PGD-000`'s Category 08 row is
updated with a fresh enumeration timestamp, `QA-002`…`QA-011` are issued against it, and the
approver has signed. **Under `PGD-A1-09` no approval record can exist until `GV-001` `CC-01`
completes**; this document carries the same qualified status as every other in the estate.

---

## 17. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `RQ-001` §3.10.5 | The denominator and the requirement attributes coverage is measured over |
| Upstream | `RQ-004` §5 | `CV-01`…`CV-04`; the ten coverage measures `QA-011` publishes |
| Upstream | `RQ-006` | The NFR baseline `QA-006` verifies |
| Upstream | `GV-009` §4, §9 | Evidence classes `E1`–`E8`; standing criteria; `GA-12` |
| Upstream | `SC-002`, `SC-005`, `SC-009` | The threat model, SSDLC gates and pen-test regime `QA-007` consumes |
| Upstream | `UX-005` | The conformance design `QA-008` tests against |
| Upstream | `IN-008` | The contract and event test layers L3, L4; the 7th environment |
| Upstream | `BE-006`, `BE-008` | The component DoD and the sprint model tests attach to |
| Downstream | `QA-002` … `QA-011` | Each derives its scope, levels and priorities from this document |
| Downstream | `MG-004`, `MG-005` | L13 reconciliation and rehearsal inherit these exit criteria |
| Downstream | `RL-003` | Go-live readiness consumes `QA-011` coverage evidence and the §11.3 completion reports |
| Downstream | `PE-002`, `PE-004` | §7 is their requirement input |
| Lateral | `../../project_content/13_Test_and_Acceptance_Content/TS-001`…`TS-018` | The content estate this strategy governs |
| Lateral | `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06` §11 | The level and coverage standards adopted verbatim |
| Lateral | `../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-02` §4 | The 70 gate criteria the levels evidence |

---

## 18. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` · `./_CATEGORY_OVERVIEW.md` ·
`./QA-002_Test_Plans_per_Level.md` … `./QA-011_Requirements_to_Test_Coverage_Standard_and_Report.md` ·
`../00_Programme_Governance_and_Control/GV-009_Wave_Gate_and_Phase_Exit_Criteria_Handbook.md` ·
`../01_Requirements_Engineering/RQ-001_Software_Requirements_Specification.md` ·
`../01_Requirements_Engineering/RQ-004_Requirements_Traceability_Matrix.md` ·
`../02_Architecture_and_Design/AR-012_Architecture_Compliance_and_Fitness_Function_Standard.md` ·
`../04_Integration_and_API_Engineering/IN-008_Integration_Test_Sandbox_and_Certification_Specification.md` ·
`../05_Security_Privacy_and_Compliance/SC-002_Threat_Model_STRIDE_and_Abuse_Case_Register.md` ·
`../05_Security_Privacy_and_Compliance/SC-005_Secure_Development_Lifecycle_Standard.md` ·
`../05_Security_Privacy_and_Compliance/SC-009_Vulnerability_Management_and_Penetration_Test_Plan.md` ·
`../06_Experience_and_Interface_Design/UX-005_Accessibility_Conformance_Design_WCAG_2_2_AA.md` ·
`../07_Build_Engineering_and_Development_Standards/BE-006_Component_Build_Specification_Standard.md`

**Workspace**
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md` ·
`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md` ·
`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md` ·
`../../project_content/13_Test_and_Acceptance_Content/` (18 files) ·
`../../project_content/_AUDIT/AUDIT-014_Category_13_TS_Content_Audit.md`

**External standards — editions verified 2026-08-18**

| Standard | Edition | Status |
|---|---|---|
| ISO/IEC/IEEE 29119-1 | **2022**, 2nd ed. | Current; cancels 29119-1:2013 |
| ISO/IEC/IEEE 29119-2 | **2021**, 2nd ed. | Current |
| ISO/IEC/IEEE 29119-3 | **2021**, 2nd ed. | Current |
| ISO/IEC/IEEE 29119-4 | **2021**, 2nd ed. | Current |
| ISO/IEC/IEEE 29119-5 | **2024**, 2nd ed., December 2024 | Current; **29119-5:2016 withdrawn** |
| ISO/IEC 25010 | **2023** | Current; adds *Safety*, restructures characteristics |
| TMMi | **2.0 (2026)** | Current; **R1.3 assessments end 1 August 2027** |
| OWASP ASVS | **5.0.0**, 30 May 2025 | Current; ~350 requirements, 17 chapters. *"ASVS 4"* superseded |
| WCAG | **2.2**, W3C Rec. 5 Oct 2023, updated 12 Dec 2024 | Current; **ISO/IEC 40500:2025** adopted 21 Oct 2025 |

> Registered for `RR-005` (Standards & Regulatory Currency Register, ⛔ `P0` `Now`).

---

## 19. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Quality Engineering | Initial issue. Thirteen levels ruled and reconciled; four quality goals; nine non-negotiable rules `MTS-R1`…`MTS-R9`; a risk model with four classes and eight pre-assigned `RC-A` populations; automation ratio per level per wave; seven environments, **0 provisioned**; entry and exit criteria for all thirteen levels; sign-off authority and four independence rules; **the capacity position measured — 62 QA FTE-months against ~1,700 items** — with three costed closure routes; five unresourced execution dependencies `MTS-D1`…`D5`; nine mis-waved packs corrected once by rule `MTS-R6`. Closes `TS-01`, `TS-02`, `TS-05`, `TS-06`, `TS-07`, `TS-12`. Raises `QAA-01`…`QAA-07`. Corrects three superseded or undated standard editions | *Pending — `GV-002`* |

---

*`QA-001` · Category 08 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
