---
id: PGD-CAT-08
category: 08 — Quality Engineering & Test
code: QA
project: 1000FiX ERP System v2.0
version: 2.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
owner: Head of Quality Engineering
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
audit: ../_AUDIT/PGD-AUDIT-CAT-08_Category_08_Quality_Engineering_and_Test_Audit.md
enumeration_timestamp: 2026-08-18 22:01 (+06)
revision_note: >
  v2.0 — Category 08 authored. Eleven QA documents issued 2026-08-18 and audited by
  PGD-AUDIT-CAT-08. Standards basis corrected: three of the four standards this overview
  previously named were cited at a superseded or undated edition (§Standards).
---

# Category 08 — Quality Engineering & Test (`QA`)

> ### ✅ CATEGORY 08 IS AUTHORED — 11 of 11 issued 2026-08-18
>
> All eleven documents exist in `08_Quality_Engineering_and_Test/` and are audited by
> [`PGD-AUDIT-CAT-08`](../_AUDIT/PGD-AUDIT-CAT-08_Category_08_Quality_Engineering_and_Test_Audit.md).
>
> **On the ✅ status.** `PGD-000` §0.3 tests (a) named file, (b) complete front matter and (c) ≥90%
> of the governing standard's section set are met by all eleven and verified in the audit. Test (d)
> requires a named owner **and an approval record**. Owners are named; **no approval record exists
> because no constituted body can create one** (`PGD-A1-09`, `PGD-A2-25`) — true of every file in
> this estate.
>
> **`QA-011` closes the estate's only open CRITICAL finding.** `AUDIT-014` `TS-01` ruled that **no
> coverage percentage may be quoted at all**, because three denominators were in circulation.
> `QA-011` fixes one — **3,389** — with its provenance, its reproduction command and its timestamp,
> and records all five superseded figures so they cannot return. **`TS-01` closes on the first
> published coverage report at the Wave 1 gate**, not on this issue.

## Purpose

`project_content/13_Test_and_Acceptance_Content/` holds **18 test content files** — SIT scenario
libraries, six UAT script packs, persona-based test data, regression packs, performance scenarios.
That content is genuinely good.

What it was not is a **strategy**: the levels of testing, entry and exit criteria, environments,
automation approach, coverage standard and sign-off authority.
`06-04_Testing_and_Quality_Strategy.md` was planned in `FOLDER_STRUCTURE.md` and never written.
**These eleven documents are that layer.**

## Documents

| ID | Document | What it delivered | Status | Pri | Needed by |
|---|---|---|:--:|:--:|:--:|
| `QA-001` | **Master Test Strategy** — ISO/IEC/IEEE 29119-3:2021 §7 | **Thirteen test levels ruled**, reconciling `05-06` §11's twelve with `TS-001` §4.1's mis-titled thirteen. Four ordered quality goals; nine non-negotiable rules; a risk model with **eight pre-assigned `RC-A` populations**; automation ratio per level per wave; **seven environments, 0 provisioned**; entry and exit criteria for all thirteen; and **the capacity position measured — 62 QA FTE-months against ~1,700 executable items** — with three costed closure routes and **five unresourced execution dependencies** | ✅ [`QA-001`](QA-001_Master_Test_Strategy.md) | **P0** | **Now** |
| `QA-002` | **Test Plans per Level** — 29119-3 §8 | All twenty §8 clauses mapped. One master plan + six level plans × nine wave instances. **All 18 packs scheduled against their earliest consuming criterion by a reproducible derivation** — finding that `TS-02`'s nine mis-waved packs is a lower bound and **the true figure is twelve**. The `EN-03` pack readiness statement: **4 packs not executable, 1 partial**. The 62 FTE-months allocated, **leaving ~67 unfunded** | ✅ [`QA-002`](QA-002_Test_Plans_per_Level.md) | **P0** | **Now** |
| `QA-003` | **Test Design Specification & Case Repository** — 29119-4:2021 | Specifies the **missing `verification_method` attribute** — absent from **3,347 of 3,347** rows — with six values and a costed procedure of ~11 analyst-days. A technique catalogue from 29119-4 mapped to four risk classes and thirteen requirement classes. **One derivable identifier `TC-<LEVEL>-<SCOPE>-<nnn>` needing no allocator**, with a crosswalk that renumbers **none of the 620 existing cases**. **≥ 379 negative cases** before any positive testing | ✅ [`QA-003`](QA-003_Test_Design_Specification_and_Case_Repository.md) | **P1** | **W1** |
| `QA-004` | **Test Data Management & Anonymisation Plan** | **Synthetic-first**, reducing the personal-data question from the whole test estate to **two bounded enclaves**. Processing purpose `P-21` registered into `SC-003` on a basis that is explicitly **not consent**. De-identification in **ISO/IEC 20889** vocabulary, with *"anonymised"* gated on a recorded k ≥ 10 assessment. **The 38 role accounts specified as a dataset**, closing `TS-05`'s data half. **Nightly, system-generated `SG-3` evidence** | ✅ [`QA-004`](QA-004_Test_Data_Management_and_Anonymisation_Plan.md) | **P0** | **W1** |
| `QA-005` | **Test Automation Framework Specification** | Five layers with a placement rule; a tool per layer with versions and verification dates, and **three deliberate capability-class bindings** rather than 36-month product commitments (`BEA-16` rationale). **The `AR-007` `T-04` concurrency harness, required since `AR-007` and never supplied.** Coverage instrumentation making **both targets machine-decidable**. A flake policy with **no retry-until-green anywhere**. A costed build of **~11.5 person-months** | ✅ [`QA-005`](QA-005_Test_Automation_Framework_Specification.md) | **P0** | **W1** |
| `QA-006` | **Performance & Load Test Plan** | All **19 performance, 11 availability and 10 scalability** targets allocated to a verifier, including the eleven this plan explicitly cannot verify. **The estate's first volumetric derivation** — 250,000 customers/month to **~241 requests/s at 1.5× peak** — with all seven assumptions and sensitivities stated, and the finding that **`NFR-004`'s 75,000 concurrent portal users is ~3,000× the load those volumes support** (`QAA-11b`). Eight workload profiles including a **breakpoint profile with no pass condition**. Percentile-only reporting | ✅ [`QA-006`](QA-006_Performance_and_Load_Test_Plan.md) | **P1** | **Now** |
| `QA-007` | **Security Test Plan** | A ten-row boundary with `SC-005`, `SC-009` and `QA-005` in which **no activity is claimed twice**. Derivation from **`SC-002`'s 97 threats and 32 abuse cases**, replacing set-arithmetic-only derivation. **The 379-denial suite as one parameterised harness**, asserted through **both UI and API paths**, with the effective-permission assertion made the suite's *first* test. Closes ~734 cases per wave **by mechanism, refusing sampling** | ✅ [`QA-007`](QA-007_Security_Test_Plan.md) | **P0** | **Now** |
| `QA-008` | **Accessibility Test Plan** | **Rules the target at WCAG 2.2 AA** against the estate's 100-files-say-2.1 position, with four propagation changes including a **contractual restatement of `PS-04`**. An AT matrix **prioritised for NVDA and TalkBack in Bengali**. **Specifies the reviewer role that does not exist**, with three costed sourcing options — closing `TS-06`'s accessibility half. **546 manual assertions per round, ~18,000 if audited every release**, closed by six mechanisms | ✅ [`QA-008`](QA-008_Accessibility_Test_Plan.md) | **P1** | **Now** |
| `QA-009` | **UAT Plan & Business Sign-off Protocol** | Counts the participant commitment at **50–74 named individuals at 30% per wave**. Names **all nine roles that cannot satisfy `UA-03`**, with `R14` excluded from the interim option on security grounds. **Resources the three physical execution dependencies**, closing `TS-06`'s UAT half. Three signature levels each with the **statement** signed, satisfying **ISO 9001:2015 §8.6**. Conditional acceptance with **two absolute exclusions** | ✅ [`QA-009`](QA-009_UAT_Plan_and_Business_Sign_off_Protocol.md) | **P0** | **Now** |
| `QA-010` | **Defect Management & Quality Gate Standard** | **Supersedes `GV-009`'s interim `GA-12` with nine derived thresholds**, including the counted demonstration that a flat `S2` count is a **2.4× looser bar at `G1` than at `G8`**. Separates **severity from population**. Adds **the four gate checks `06-02` does not contain**, closing `TS-04`'s residual. `DDP` as the primary metric. **A stated limit on the Steering Committee's authority** | ✅ [`QA-010`](QA-010_Defect_Management_and_Quality_Gate_Standard.md) | **P1** | **W1** |
| `QA-011` | **Requirements-to-Test Coverage Standard & Report** | **Fixes one denominator — 3,389 — with provenance, reproduction and timestamp**, and records all five superseded figures. The measured baseline **published including its zeros**. `RQ-004`'s ten measures consumed unchanged and **eight non-requirement dimensions added**. **`G4-10` expressed as an executable query, reported from W1** rather than first attempted at Month 18. Six named anti-patterns | ✅ [`QA-011`](QA-011_Requirements_to_Test_Coverage_Standard_and_Report.md) | **P0** | **W1** |

## What `AUDIT-014` found, and the position now

| Finding | Severity | Closed by | Position at issue |
|---|---|---|---|
| Coverage has **three current denominators**, so `G4-10` is unanswerable and **no coverage percentage may be quoted** | **CRITICAL** | `RQ-004` + **`QA-011`** | **Resolved in specification.** One denominator — **3,389** — fixed with provenance. Closes on the first published report at the W1 gate |
| **Nine of eighteen test files are consumed a wave before they exist**, seven at gate `G1` | High | `QA-001` §4.5, **`QA-002` §4** | **Corrected once, register-wide** by rule `MTS-R6`. `QA-002` finds the true figure is **twelve**, not nine (`QAA-08`) |
| `TS-017` security pack **cannot be executed — no role accounts** | High | `SC-004` + **`QA-004` §9** + **`QA-007` §5** | Specified as a dataset with an owner. **Provisioning remains open** — `M29` work |
| `TS-015` offline/field pack **cannot be executed — no field logistics** | High | **`QA-009` §6.4** | Resourced as `MTS-D5` with specification, owner and date. **Funding remains open** |
| `TS-008` supply-chain UAT **cannot be executed — no staged stock** | High | **`QA-009` §6.3** | Resourced as `MTS-D4`. **Funding remains open** |
| `TS-016` accessibility pack **cannot be executed — no accessibility reviewer** | High | `UX-005` + **`QA-008` §6** | Role specified with competency and **three costed sourcing options**. **Appointment remains open** |

**Four of eighteen packs could not be executed at all, for resourcing reasons rather than technical
ones.** Each now has a specification, an owner, a date and the gate criteria it blocks. **That is
what a test strategy exists to do** — and the residual in every case is a funding decision, which is
where it belongs.

## The two findings this category raised against material outside it

| # | Finding | Against |
|---|---|---|
| **`QAA-08`** | **`TS-02`'s nine mis-waved packs is a lower bound; the true figure is twelve.** `TS-011`, `TS-013` and `TS-018` are also consumed before they exist — `TS-011` because `P03` ships in W1 and `G1-11` requires UAT sign-off on it, `TS-013` because the monthly production cadence begins at W1 go-live, and `TS-018` because triage begins with the first test cycle | Category 13 register |
| **`QAA-10`** | **The same defect exists in the *guiding* register.** `QA-006`, `QA-007`, `QA-008` and `QA-009` were registered at `W2`/`W3` while `G1` consumes all four at Month 4. A defect found in content sequencing was never checked against the guiding register itself | `PGD-000` |

## Standards — three corrections

`PG-M4` requires a verification date on every standard, statute or vendor claim. **Three of the four
standards this overview previously named were cited at a superseded or undated edition** — the
defect class behind critical findings `C-04`, `H-01` and `M-01`.

| Previously | **Current, verified 2026-08-18** |
|---|---|
| *"ISO/IEC/IEEE 29119-1…5"*, undated | **29119-1:2022 · 29119-2:2021 · 29119-3:2021 · 29119-4:2021 · 29119-5:2024** — 29119-5:2016 is **withdrawn** |
| *"ISO/IEC 25010"*, undated | **ISO/IEC 25010:2023** — adds *Safety*, restructures the characteristics |
| *"OWASP ASVS 4"* | **ASVS 5.0.0, 30 May 2025** — ~350 requirements in 17 chapters. 4.0.3 superseded |
| *"TMMi"*, undated | **TMMi 2.0 (2026)** — Release 1.3 assessments end **1 August 2027** |
| *"WCAG 2.2 AA"* ✔ | **WCAG 2.2**, W3C Rec. 5 Oct 2023, updated 12 Dec 2024; **ISO/IEC 40500:2025** since 21 Oct 2025 |

Registered for `RR-005` (Standards & Regulatory Currency Register, ⛔ `P0` `Now`).

## The automation argument

**3,389 requirements across 9 waves and ~80 sprints, released monthly to production within a wave,
cannot be regression-tested manually.**

`TS-013` defines a regression pack and a smoke checklist. **Nothing automates them.** `QA-005`
specifies the framework and costs it at **~11.5 person-months — roughly 19% of the programme's
entire 62 QA FTE-months**, spent before the surface it automates exists.

> **That is the actual shape of the Wave 1 decision.** It is not a request for more testers; it is a
> request to spend a fifth of the test budget on machinery, up front. **The alternative is not
> cheaper — it is the same money spent on manual re-execution, once per release, forever.**

## Test data is a legal problem, not only a logistics problem

`QA-004` is `P0` because using production-derived customer data in a test environment is a
processing act under the **Personal Data Protection Act 2026**. Its answer is **synthetic-first**:
seven of nine contexts then process **no personal data at all**, and `GV-009`'s `SG-3` standing gate
criterion becomes cheap to evidence — the nightly scan's expected result is *zero production
records* rather than *all production records correctly masked*.

## What "done" looks like for this category

| # | Criterion | Position at issue |
|:--:|---|---|
| 1 | One coverage denominator exists, published, derived from `RQ-004` | ✅ **3,389**, `QA-011` §3 |
| 2 | Every test level has entry criteria, exit criteria, an environment and an owner | ✅ 13 of 13, `QA-001` §4, §8 |
| 3 | Automated regression runs in `PE-004` CI on every pull request | ⛔ **`PE-004` is unwritten** — `QA-005` §11.1 states the eight requirements it must satisfy |
| 4 | `QA-010` states the defect thresholds that **block a wave gate** | ✅ Nine derived thresholds, superseding `GA-12` |
| 5 | No test pack is written before its execution dependencies are resourced | ◐ Specified and owned; **funding is the open decision** |

## Dependencies

| Direction | Category | Relationship |
|---|---|---|
| Upstream | `01_Requirements` | Every case derives from `RQ-001`; the denominator and `CV-M*` from `RQ-004` |
| Upstream | `02_Architecture` | `AR-007` §9 test gates; `AR-012` fitness functions share the pipeline |
| Upstream | `03_Data` | `QA-004` masking derives from `DA-005` |
| Upstream | `04_Integration` | `IN-008` owns the contract and event layers `QA-005` schedules |
| Upstream | `05_Security` | `QA-007` derives from `SC-002`; consumes `SC-005` gates and `SC-009`'s pen-test regime |
| Upstream | `06_Experience` | `QA-008` derives from `UX-005` |
| Upstream | `07_Build` | `BE-005` component identity; `BE-006` DoD; `BE-002` §8 test-code rules; `BE-008` sprint model |
| **Blocked on** | **`10_Infrastructure`** | **`PE-002` and `PE-004` — 0 of 7 environments provisioned; nine levels defined as running in a pipeline with no design** |
| Downstream | `09_Migration` | `MG-004`, `MG-005` inherit L13's exit criteria |
| Downstream | `12_Release` | `RL-003` go-live readiness consumes `QA-011` coverage and the level completion reports |
| Downstream | `15_Benefits` | `BM-002` consumes objective coverage |

## Audience and change frequency

| Attribute | Value |
|---|---|
| Primary audience | QA engineers, developers, business UAT participants, wave gate assessors |
| Change frequency | **Medium** — strategy stable, plans per wave |
| Standards basis | ISO/IEC/IEEE 29119-1:2022 · -2:2021 · -3:2021 · -4:2021 · -5:2024 · ISO/IEC 25010:2023 · ISO/IEC/IEEE 1044:2009 · ISO/IEC 20889:2018 · WCAG 2.2 AA (ISO/IEC 40500:2025) · OWASP ASVS 5.0.0 · TMMi 2.0 · ISO 9001:2015 §8.6, §10.2 |

## Existing material this category governs

`project_content/13_Test_and_Acceptance_Content/TS-001`…`TS-018` — all 18 files, **620 distinct case
identifiers in six incompatible schemes** ·
`project_content/_AUDIT/AUDIT-014` — 17 findings, 1 critical, 14 open ·
all 67 module files §17 · `05-06` §11 · `06-02` §4

---

*Category 08 · `QA` · 11 of 11 authored 2026-08-18 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
