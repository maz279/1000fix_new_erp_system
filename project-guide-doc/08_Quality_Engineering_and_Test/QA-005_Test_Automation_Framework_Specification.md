---
id: QA-005
title: Test Automation Framework Specification
category: 08 — Quality Engineering & Test
code: QA
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: QA Lead with the Engineering Lead
approver: Chief Architect with the Head of Quality Engineering
standards_basis: >
  ISO/IEC/IEEE 29119-2:2021 (dynamic test processes) · Odoo 19.0 test framework
  (TransactionCase, HttpCase, test tags) · consumer-driven contract testing · OpenAPI 3.1 ·
  AsyncAPI 3.0 · WCAG-ACT rules format
traces_to: >
  PGD-000 QA-005 · 05-06 §11 (unit ≥80%, 100% financial; E2E nightly) · NFR-090 §7 ·
  AR-007 §9 T-01…T-04 · BE-002 §8 XS-16, XS-17 · AR-012 (fitness functions, same pipeline) ·
  QA-001 §6 (layer strategy and ratio) · AUDIT-014 TS-07
depends_on: QA-001 (ratio, levels) · QA-003 (cases) · QA-004 (data) · IN-008 (pacts) · PE-004 (pipeline, unwritten)
verified_on: 2026-08-18
enumeration_timestamp: 2026-08-18 22:01 (+06)
priority: P0
needed_by: W1
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# QA-005 — Test Automation Framework Specification

### Category 08 · Code `QA` · Odoo 19.0 test framework · OpenAPI 3.1 · AsyncAPI 3.0

---

> **Before writing, read this.**
>
> 1. **`PG-01` Register-first.** Row `QA-005` exists in `PGD-000` Category 08, status ⛔ `P0` `W1`.
> 2. **`PG-03` Count, do not consult.** Surface counts taken from `IN-002`, `IN-003`, `BE-005` and the
>    18 packs at **2026-08-18 22:01 (+06)**.
> 3. **`PG-06` Cite standards.** §2.1, including the tool-version position and why tool *classes* are
>    specified in preference to products in three places.
> 4. **`PG-M4` Verify citations.** Every tool and runtime version below carries a verification date;
>    `verified_on: 2026-08-18`. **`BEA-16` — MinIO archived upstream on 25 April 2026 — is the
>    estate's own reminder that an unverified vendor claim is a live risk.**

---

## 1. Purpose

`QA-001` §6 sets the automation **ratio**: 70/25/5 across unit, API and UI, rising to **90% of the
permanent regression core by Wave 5**. This document specifies **the thing that achieves it** — the
framework's layers, the tool per layer, the code structure, the fixtures, the flake policy, the
coverage instrumentation and the CI wiring.

It exists because of an arithmetic the programme cannot avoid:

> **3,389 requirements · 331 components · 1,187 API operations · 988 domain events · ~800
> provider–consumer pacts · ~33 production releases · 62 QA FTE-months.**
>
> `TS-013` defines a regression pack and a smoke checklist. **Nothing automates them.** By Wave 5 the
> regression surface exceeds what any manual team can re-run per release, and the programme then
> chooses between slowing releases and shipping untested. **This document is what prevents that
> choice from arising.**

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | **The five automation layers** and what belongs in each (§3) |
| 2 | **The tool per layer**, with version, verification date and the reason it was chosen (§4) |
| 3 | **The Odoo test harness** — `TransactionCase`, `HttpCase`, tags, and the three traps (§5) |
| 4 | **The API, contract and event layer**, and its boundary with `IN-008` (§6) |
| 5 | **The UI layer** — web and mobile — and why it is deliberately small (§7) |
| 6 | **Framework code structure, fixtures and the page-object rule** (§8) |
| 7 | **Coverage instrumentation** — how ≥ 80% and 100%-of-financial-paths are measured, and gamed-proofed (§9) |
| 8 | **The flake policy** — `BE-002` `XS-16` made operational (§10) |
| 9 | **CI wiring, execution profiles and runtimes** (§11) |
| 10 | **Non-functional automation** — the interfaces to `QA-006`, `QA-007`, `QA-008` (§12) |
| 11 | **Build sequence and effort** — what is built when, and by whom (§13) |

**Explicitly out of scope**

| Topic | Owned by | Why |
|---|---|---|
| The ratio and the layer strategy | `QA-001` §6 | Consumed; this document implements it |
| Which cases exist | `QA-003` | This document implements cases; it does not derive them |
| Test data content and provisioning | `QA-004` | §8.3 states the fixture interface |
| The pact lifecycle, broker semantics, `CT-01`…`CT-07` | `IN-008` §4 | §6.2 states the boundary; two authorities on one subject is the defect behind five identifier collisions here |
| **The pipeline itself** — stages, gates, promotion, runners | `PE-004` ⛔ | **Unwritten.** §11 specifies what the framework needs *from* a pipeline |
| Code style in test code | `BE-002` §8 | Consumed: `XS-16`, `XS-17`, `PYS-26`, `PYS-27` |
| Architectural fitness functions `FF-01`…`FF-100` | `AR-012` | Same pipeline, different purpose — `QA-001` §4.6 |
| SAST/DAST/SCA gates `G-01`…`G-14` | `SC-005` §5 | `QA-007` consumes their output |
| Workload models | `QA-006` | §12.1 states the interface |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| **Developers** | §5, §8, §9, §10 — how to write a test that passes review and does not become a flake |
| **QA engineers** | §3, §6, §7 — the layers they own and the tools they build in |
| Platform Engineering | §11 — what the pipeline must provide, and the execution profiles |
| Chief Architect | §4, §13 — tool selection, and the build sequence and its cost |
| Implementation vendor | The framework they must deliver into and be measured against |

---

## 2. Basis and Inputs

### 2.1 Standards and tool-currency position

| Item | Version / edition | Verified | Position |
|---|---|:--:|---|
| **Odoo** | **19.0**, released 18 September 2025 | 2026-08-18 | The test framework is Odoo's own — `TransactionCase`, `HttpCase`, `--test-tags`, `at_install`/`post_install`. **`BEA-13` records that Odoo 19.0's "LTS" class is not a vendor classification**; the framework does not depend on that claim |
| **Python** | **3.12** | 2026-08-18 | `BE-001` pin; Odoo 19.0's supported runtime |
| **PostgreSQL** | **16** | 2026-08-18 | Supported to November 2029 |
| **Node.js** | **20 LTS** | 2026-08-18 | `BE-001` pin, `.nvmrc` |
| **Flutter / Dart** | Pinned via `fvm` in `.fvmrc` | 2026-08-18 | `BE-001`; subject to `D-027` |
| **k6** | **2.0**, released 11 May 2026 | 2026-08-18 | `QA-006` owns the load layer; recorded here because §12.1 shares its runner |
| **OpenAPI** | **3.1** | 2026-08-18 | `IN-002` |
| **AsyncAPI** | **3.0** | 2026-08-18 | `IN-003` |
| **ISO/IEC/IEEE 29119-2** | **2021**, 2nd ed. | 2026-08-18 | Dynamic test processes |

> **`TAF-01` — tool *classes*, not products, in three places.** For the **browser driver**, the
> **contract-test broker** and the **accessibility scan engine**, this document specifies the
> *capability required* and names a current reference implementation, rather than binding the
> programme to a product for 36 months. **Rationale: `TR-09` materialised as `BEA-16` — MinIO, the
> Wave 1 object store, was archived upstream on 25 April 2026 and the estate had not recorded it.**
> A 36-month programme that hard-binds a tool inherits that risk in every layer. `BE-007` §5's
> dependency-currency mechanism applies to test tooling identically.

### 2.2 Source material relied on

| Source | What it establishes |
|---|---|
| `05-06` §11 | Unit ≥ 80% custom code, **100% of financial and tax calculations**; contract, event, E2E **nightly**; the tooling standard per level |
| `NFR-090` §7 | Restates the unit coverage gate — **and `AUDIT-014` `TS-04` records `NFR-090` is double-allocated**, §9.4 |
| `AR-007` §9 | Test gates per level and rules `T-01`…`T-04`, including **`T-04` concurrency contention tests** |
| `BE-002` §8 | `XS-16` a flaky test is a defect; `XS-17` H-class negative tests through UI **and** API; `PYS-26` naming; `PYS-27` no inter-test residue |
| `AR-012` | 37+ fitness functions sharing the pipeline; `FF-57` contract coverage; `FF-95` pact verification |
| `IN-002`, `IN-003`, `IN-008` | **1,187 operations · 988 events · ~800 pacts**; the pact lifecycle |
| `BE-005`, `BE-006` | **331 components across 79 units**; `component.yaml`, which declares what a component's tests must prove |
| `QA-001` §6 | The ratio per level per wave this framework must deliver |
| `QA-003` | The case set; `automated: yes` must resolve to a real suite (`TDS-Q6`) |
| `QA-004` | Fixtures, generators, the 38 role accounts |

### 2.3 What this document closes

| Finding | Source | How |
|---|---|---|
| `QA-005` register row ⛔ | `PGD-000` | *"2,930 requirements across 9 waves cannot be regression-tested manually. `TS-013` defines a regression pack; nothing automates it."* — §3–§11 specify the automation |
| `TS-07` (partial) | `AUDIT-014` | §13's build sequence is `QA-001` §10.5 route B made concrete: what is built, when, by whom, and at what cost |
| `TDS-Q6` | `QA-003` §10 | §8.5 makes `automated: yes` machine-verifiable rather than self-reported |
| `AR-007` `T-04` | `AR-007` §9 | §5.4 specifies the concurrency-contention harness, which `T-04` requires and nothing supplies |

---

## 3. The Five Layers

### 3.1 The layer map

| Layer | Levels | Runs | Target duration | Share of automated cases |
|:--:|---|---|---|---:|
| **`A1` Unit** | L1 | Every commit, per component | **< 3 min** per component | ~70% |
| **`A2` Service / integration** | L2 | Every commit | < 10 min | included in A2–A3 ~25% |
| **`A3` Contract & event** | L3, L4 | Every commit; provider verification on every provider build | < 10 min | |
| **`A4` Journey (web + mobile)** | L5, L6 | Per release into `SIT`; **nightly** for L6 | < 45 min nightly | ~5% |
| **`A5` Non-functional** | L8, L9, L10, L12 | Per gate / per release | varies | delegated |

### 3.2 The placement rule

> **`TAF-02`.** A test belongs to the **lowest layer that can prove its assertion**. A rule provable
> in `A1` is never written in `A4`.

This rule does most of the work in keeping the pyramid the right shape. Its practical form:

| If the assertion is about… | Layer |
|---|---|
| A calculation, a validation, a guard, a compute field | `A1` |
| A model interaction, an ORM constraint, a workflow transition inside one module | `A1` |
| Two modules exchanging data inside one Odoo instance | `A2` |
| A published API's shape or a consumer's expectation | `A3` |
| An event's schema, idempotency, ordering or replay | `A3` |
| A business chain crossing a **category** boundary and producing a business outcome | `A4` |
| A screen the user actually sees, in a browser or on a device | `A4` |
| A number under load, an attack, a WCAG criterion, offline behaviour | `A5` |

### 3.3 The anti-pattern this rule prevents

**UI tests written because the UI is where the tester looked.** A pricing rule tested through six
browser steps takes 40 seconds, breaks when a label changes, and proves less than a three-line unit
test. At 331 components across 36 months, the accumulated cost of that choice is the difference
between a suite that runs in 45 minutes and one nobody runs.

| # | Rule |
|---|---|
| `TAF-03` | **A new `A4` test requires a stated reason why `A1`–`A3` cannot prove the assertion.** The reason is recorded on the case (`QA-003` §6.1) |
| `TAF-04` | **An `A4` test that fails for a reason `A1` could have caught adds the `A1` test**, and the `A4` test is reviewed for removal |

---

## 4. Tool Per Layer

| Layer | Capability required | Reference implementation | Version | Why |
|:--:|---|---|---|---|
| `A1` Python/Odoo | Odoo-native transactional unit testing with tag-based selection | **Odoo's own framework** — `TransactionCase`, tags, `odoo-bin --test-tags` | Odoo 19.0 | §5. A third-party runner over Odoo re-implements the ORM's transaction and registry handling badly |
| `A1` Python services | Plain unit testing for non-ORM business logic (`PYS-25`) | **pytest** | current at pin | `services/` code is testable **without a database**, which is why `PYS-25` puts it there |
| `A1` TypeScript | Component and unit testing for 12 Next.js portals | **Vitest** + Testing Library | current at pin | Node 20 LTS |
| `A1` Dart | Unit and widget testing for 4 Flutter apps | **`flutter test`** | pinned via `fvm` | Framework-native, per `05-06` §11 |
| `A1` SQL | Assertions over migration and view logic | **pgTAP** | current at pin | PostgreSQL 16 |
| `A2` | HTTP-level integration inside an Odoo instance | **`HttpCase`** + `pytest` | Odoo 19.0 | §5.2 |
| `A3` contract | OpenAPI 3.1 conformance + consumer-driven pacts with a broker | **Pact-style broker** *(class — `TAF-01`)*, wired per `IN-008` §4 | — | `IN-008` owns it; `FF-57`, `FF-95` enforce it |
| `A3` event | AsyncAPI 3.0 schema compatibility, idempotency, ordering, replay | **Schema registry + a replay harness** *(class)* | — | `IN-003`; `IN-008` §5 |
| `A4` web | Cross-browser browser automation with tracing, video and auto-wait | **Playwright** *(reference implementation — `TAF-01`)* | current at pin | Auto-wait removes the largest single source of flake; trace-on-failure is what makes a nightly failure diagnosable the next morning |
| `A4` mobile | On-device integration testing for Flutter | **`integration_test`** + a device farm or lab devices | pinned via `fvm` | Framework-native; §7.3 |
| `A5` performance | Scriptable load with a browser mode | **k6 2.0** *(11 May 2026)* | 2.0 | `QA-006` owns it |
| `A5` accessibility | WCAG-ACT-rules-conformant automated scanning | **An ACT-rules engine** *(class — `TAF-01`)* | — | `QA-008` owns it; §12.3 |
| `A5` security | SAST/DAST/SCA | Per **`SC-005` §5 gates `G-01`…`G-14`** | — | Not re-specified here |

> **`TAF-05`.** Every tool version is **pinned by digest or lockfile** and upgraded under `BE-007`'s
> dependency policy. A test framework that floats produces failures nobody can attribute to a change.

---

## 5. The Odoo Test Harness

### 5.1 Base classes

| Class | Use | Transaction behaviour |
|---|---|---|
| **`TransactionCase`** | The default for `A1`. Model logic, business rules, computes, constraints, workflow guards | Runs inside a transaction that is **rolled back** |
| **`HttpCase`** | `A2` — controllers, JSON-2 endpoints, portal routes, and browser tours | **Commits**, because the HTTP server runs in a separate thread that must read the data |
| **`SavepointCase`-style patterns** | Shared expensive setup across a class | Class-level setup, per-test savepoint |

### 5.2 Tags and selection

Odoo tags tests automatically with `standard` and `at_install`. Three rules make selection
predictable across 331 components:

| # | Rule |
|---|---|
| `TAF-06` | **Every test class carries an explicit tag naming its CD identifier** — `@tagged('cd_service_order')` — so a component's suite is selectable without knowing its file layout (`BE-005`, `XS-13`) |
| `TAF-07` | **`HttpCase` tests are `post_install`**, because they need the full registry. An `at_install` `HttpCase` fails intermittently depending on module order — the first flake class a new Odoo team meets |
| `TAF-08` | **Slow tests carry `@tagged('slow')`** and are excluded from the pre-merge profile, included in the nightly (§11.2) |

### 5.3 The three traps

Recorded because each produces a flake that looks like a product defect, and each will otherwise be
discovered independently 331 times.

| # | Trap | Rule |
|:--:|---|---|
| 1 | **`HttpCase` commits.** Data it writes survives the test and leaks into the next | `TAF-09`: an `HttpCase` test cleans up explicitly, or runs against data it created with a unique key. This is `AR-007` `T-02` and `BE-002` `PYS-27` in their Odoo-specific form |
| 2 | **Timezones.** Bangladesh is **UTC+06 with no DST**, so a naive-datetime defect is invisible locally and appears only in cross-border data | `TAF-10`: every date assertion uses an explicit timezone, and the suite runs a **second nightly pass with the runner's TZ set to UTC** — the cheapest possible detector for `XS-04` violations |
| 3 | **`demo/` data drift.** Tests written against demo records break when demo data changes | `TAF-11`: `A1` tests use **explicit factories**, not `demo/` data, wherever the record's content matters. `AR-007` `T-01` permits either; this document narrows it, because factories make the precondition visible in the test |

### 5.4 The concurrency harness *(`AR-007` `T-04`)*

> `AR-007` `T-04` requires that *"concurrency behaviour declared in the SDD has a test that exercises
> the contention"*, and observes it is **the rule most often skipped and most valuable**: a
> reservation race, a duplicate webhook, or two dispatchers assigning the same technician are all
> reproducible in a test and all invisible in a single-user manual test.

**Nothing in the estate supplies the harness.** This document does:

| Element | Provision |
|---|---|
| Mechanism | A fixture that opens **N real database sessions** and releases them onto the same operation at a barrier |
| Assertions | Exactly one succeeds where the rule is exclusive; the losers receive the declared error code (`XS-09`), not a stack trace; no partial write survives |
| Required for | Every operation `AR-003` `DP-03` declares concurrent — stock reservation, dispatch assignment, sequence allocation, payment capture, webhook receipt, offline sync merge |
| Runs in | The nightly profile — these tests are slow by construction (`TAF-08`) |
| Determinism | Barrier-synchronised, not sleep-based. **A sleep-based concurrency test is a flake generator** (`TAF-12`) |

---

## 6. The API, Contract and Event Layer

### 6.1 What `A3` proves

| Sub-layer | Proves | Against |
|---|---|---|
| **OpenAPI conformance** | Every response matches the published schema; **an invalid payload posted directly to the API is rejected** (`PS-11`, `XS-14`) | `IN-002` — 1,187 operations |
| **Consumer-driven pacts** | Each provider satisfies what its consumers actually need | ~800 pairs |
| **Event schema compatibility** | Every producer/consumer pair is compatible | `IN-003` — 988 events |
| **Idempotency** | Re-delivering an event produces no second effect | `DI-05` |
| **Ordering and replay** | Out-of-order and replayed events behave as declared | `AS-08` |

### 6.2 The boundary with `IN-008`

> **`IN-008` §4 is the authority on contract testing.** It defines the pact lifecycle, the broker, and
> rules `CT-01`…`CT-07`, including `CT-07` — a new consumer's pact that no provider satisfies fails
> the *consumer's* build. **None of that is restated here.**

`QA-005` adds only what a framework specification must add:

| # | Addition |
|---|---|
| `TAF-13` | **The pact-emitting fixture** is part of this framework and is shared across Python, TypeScript and Dart consumers, so a pact looks the same whichever stack produced it |
| `TAF-14` | **Schema conformance runs on every response in every `A2` test**, not only in dedicated contract tests. A response that drifts from its schema fails wherever it is observed — the cheapest possible coverage of 1,187 operations |
| `TAF-15` | **The replay harness** — re-delivering a captured event N times and asserting a single effect — is framework code, because every one of 988 events needs it |
| `TAF-16` | **Negative contract cases are generated, not hand-written**: for each operation, a case per required field omitted, per type violated, per enum breached. 1,187 operations hand-written is not affordable; generated it is one harness |

### 6.3 The dependency

`A3` requires a **broker** and a **schema registry**, both of which live in `CI`, which is **0 of 7
provisioned**. Until then `A3` runs schema conformance locally and cannot run cross-build pact
verification. Recorded against `LVP-R1`; this is `QA-001` `QAA-05`.

---

## 7. The Journey Layer

### 7.1 Deliberately small

`A4` is ~5% of automated cases and carries **L5's category-boundary chains and L6's 18 journeys in 20
executions**. It is small because it is slow, brittle and expensive to diagnose — and it is
*necessary* because a business outcome across a category boundary cannot be proven anywhere else.

### 7.2 Web

| # | Rule |
|---|---|
| `TAF-17` | **Page objects, not selectors in tests.** A test names intent — `dispatchBoard.assign(job, technician)` — never a CSS path. With 900–1,400 screens (`UX-003`) the alternative is unmaintainable |
| `TAF-18` | **Selectors use stable test identifiers**, added to the component library by `UX-001` and treated as an API. A test bound to a class name breaks on a style change |
| `TAF-19` | **No arbitrary waits.** Auto-wait on state, never `sleep`. A sleep-based UI suite is a flake factory, and `XS-16` makes each flake a defect |
| `TAF-20` | **Trace, video and DOM snapshot on failure**, retained with the run. A nightly failure with no trace is a nightly failure nobody diagnoses |
| `TAF-21` | **Every `A4` journey runs in both languages** where the surface is bilingual (`TX-10`), because Bengali expansion breaks layouts that pass in English (`UX-007`) |
| `TAF-22` | **`A4` asserts business outcomes, not screens** (`LVP-S1`): the ledger moved by the right amount, not that a toast appeared |

### 7.3 Mobile

Four Flutter applications — technician, rider, field auditor, customer — of which three are
offline-capable.

| # | Rule |
|---|---|
| `TAF-23` | **`integration_test` runs on real devices at the floor spec** — mid-range Android 11, 3 GB RAM — not only on an emulator. `NFR-036` is a 3G field target and an emulator on a workstation cannot falsify it |
| `TAF-24` | **The offline harness controls connectivity programmatically** — airplane mode, 3G throttling, packet loss — so a conflict scenario is reproducible in CI |
| `TAF-25` | **CI offline tests are the *conflict* half of L12, never the *field* half.** `G2-02` and `G2-03` are field criteria; `LVP-O1` records that a lab result does not discharge them |
| `TAF-26` | **Sync assertions are server-observed as well as client-observed.** *"Sync reported complete while queued"* is an automatic `S1` (`TS-015`, `TS-018`), and only a server-side observer can catch it |

---

## 8. Framework Code Structure

### 8.1 Placement

Test code lives **with the code it tests**, per `BE-004`. The framework's shared parts are a library.

```text
addons/cd_<unit>/tests/            # A1, A2 — Odoo, per component
services/<svc>/tests/              # A1 — pytest, no database
apps/<portal>/src/**/*.test.ts     # A1 — Vitest
apps/<app>/test/                   # A1 — flutter test
apps/<app>/integration_test/       # A4 mobile
tests/
├── framework/                     # the shared library — QA-005 owns this
│   ├── fixtures/                  # factories, role-account fixtures, dataset selection
│   ├── pages/                     # page objects, one per screen family
│   ├── contract/                  # pact emitters, schema conformance, negative generator
│   ├── events/                    # replay and idempotency harness
│   ├── concurrency/               # the T-04 barrier harness
│   └── reporting/                 # result normalisation into the QA-011 shape
├── journeys/                      # A4 web — L5 chains and L6 journeys
└── suites/                        # profile definitions (§11.2)
```

### 8.2 Rules on framework code

> **`TAF-27`. Framework code is production code**, and `BE-002` applies to it in full — including
> review, typing, docstrings and the prohibition on secrets. A framework nobody reviews becomes the
> least reliable code in the repository and undermines every result it produces.

| # | Rule |
|---|---|
| `TAF-28` | **No business logic in the framework.** A helper that computes an expected VAT amount duplicates the system under test and will agree with it while both are wrong |
| `TAF-29` | **No conditional assertions.** `if (x) expect(a) else expect(b)` is two cases; write two |
| `TAF-30` | **A test asserts one behaviour.** Multiple assertions on one behaviour are fine; multiple behaviours in one test hide the second failure |
| `TAF-31` | **Framework changes go through `BE-003` risk-based review** at the class that matches their blast radius — a change to the role-account fixture affects every negative test in the estate |

### 8.3 Fixtures — the interface with `QA-004`

| # | Rule |
|---|---|
| `TAF-32` | **A fixture states what the data must be like, and resolves it from `QA-004`'s generator** — never hard-codes values (`TDM-13`, `TDS-13`) |
| `TAF-33` | **Role-account fixtures resolve the 38 accounts by role identifier**, and **assert the account's effective permission set before use** (`TDM-37`). An over-permissioned account makes all 379 denial cases pass falsely |
| `TAF-34` | **Fixtures are composable and idempotent**; a test may run twice with no residue (`PYS-27`, `T-02`) |
| `TAF-35` | **The dataset version is recorded in every run's result** (`TDM-23`), so a failure after a refresh is attributable to the data, not to the build |

### 8.4 Test naming

`BE-002` `PYS-26` requires `test_<condition>_<expected>`. Extended across stacks:

| Stack | Form | Example |
|---|---|---|
| Python/Odoo | `test_<condition>_<expected>` | `test_unverified_seller_cannot_transact` |
| TypeScript | `describe(<unit>) / it(<condition>, <expected>)` | `it('rejects a booking outside the service window')` |
| Dart | `test('<condition>, <expected>')` | |
| `A4` journey | `journey_<Jnn>_<name>` | `journey_J04_warranty_claim_to_reimbursement` |

> **`TAF-36`.** Every test declares the `tc_id` it implements (`QA-003` §5.2), as a tag, an annotation
> or a decorator. This is what makes `TDS-Q6` machine-checkable and what feeds `QA-011`'s numerator.

### 8.5 Closing the self-reported-automation loop

> **`TAF-37`.** The build emits, for every test, the `tc_id` it declares. `QA-003`'s repository is
> then reconciled against that list: **a case marked `automated: yes` whose `tc_id` appears in no
> suite fails the build.** This is `BE-006`'s `component.yaml` mechanism applied to cases — a claim a
> case makes about itself can be contradicted by CI, so `QA-001` `MTS-R8`'s ratio is measured rather
> than asserted.

---

## 9. Coverage Instrumentation

### 9.1 The two targets

| Target | Measure | Scope | Gate |
|---|---|---|---|
| **≥ 80% of custom code** | **Line coverage** | The component's own modules; vendored, generated and migration code excluded | CI blocks merge (`AR-007` §9) |
| **100% of financial and tax calculation paths** | **Branch coverage** (`QA-002-D-02`) | Every function on a `DI-01` decimal/money path | CI blocks merge, **no tolerance at any wave** |

### 9.2 Identifying the financial paths

100%-of-financial-calculations is unenforceable until "financial calculation" is a machine-decidable
set. It is made one:

| # | Rule |
|---|---|
| `TAF-38` | **A function on a money or tax path is annotated** — `@financial_path` in Python, an equivalent marker in TypeScript and Dart — and the annotation is part of the code, reviewed with it |
| `TAF-39` | **The annotated set is cross-checked against `DI-01`'s decimal-arithmetic classification and `DA-002`'s monetary fields.** A monetary field whose writer is unannotated fails the check — this is what stops the set being quietly small |
| `TAF-40` | **Branch coverage of the annotated set is reported separately** from overall line coverage, so a strong overall number cannot conceal a gap in the set that matters |

### 9.3 Anti-gaming

`QA-002` `LVP-U4` makes coverage a floor, not a goal. Three mechanisms:

| # | Mechanism |
|---|---|
| `TAF-41` | **The exclusion list is committed, reviewed and monotonically shrinking.** A pull request that adds an exclusion requires a stated reason and an expiry (`LVP-U5`) |
| `TAF-42` | **Coverage delta is reported per pull request.** A change that reduces coverage in the files it touches is flagged in review |
| `TAF-43` | **Assertion-free tests are detected** — a test with no assertion, or one whose assertions do not reference the unit under test, is reported. Coverage bought without behaviour is visible rather than invisible |

### 9.4 The `NFR-090` collision

> **`AUDIT-014` `TS-04` records that `NFR-090`, `NFR-091` and `NFR-092` are each used twice for
> unrelated requirements.** `05-06` §6.3 assigns them to PDPA obligations — consent basis, consent
> standard, transparency notice, all `P0`. §7 assigns the same three to maintainability — **unit-test
> coverage ≥ 80% and 100% of financial calculations**, module runbook, distributed tracing.
>
> **A gate claim of the form *"`NFR-090` met"* is therefore unfalsifiable**: it could mean unit-test
> coverage passed or that consent processing is lawful.

| # | Position |
|---|---|
| `TAF-44` | **This document never cites a bare `NFR-090`.** The coverage gate is cited as **`NFR-090` §7** and the consent obligation as **`NFR-090` §6.3**, until `RQ-006` renumbers |
| — | `TS-04` also found the §7 coverage gate is **the only `05-06` §11 coverage standard with no gate criterion in `06-02` §4** — nothing verifies it at `G1`–`G9`. **`QA-010` §6 adds it as a gate check**, and `QA-011` reports it |

---

## 10. The Flake Policy

### 10.1 The rule

> **`BE-002` `XS-16` and `AR-007` `T-03`: a flaky test is a defect. It is fixed or deleted, never
> re-run until green.** This document makes that operational, because a policy with no mechanism is
> a policy that loses to a deadline.

### 10.2 Mechanism

| # | Provision |
|---|---|
| `TAF-45` | **Every run's results are retained**, so flake rate is measurable per test rather than felt |
| `TAF-46` | **A test failing intermittently across ≥ 2 runs of the same commit is auto-quarantined** — moved to a quarantine suite that runs but does not block — **and a defect is raised automatically**, owned by the test's author |
| `TAF-47` | **A quarantined test has a 10-working-day clock.** At expiry it is fixed or **deleted**. It is never quietly retained, because a permanently quarantined test is a coverage claim with no coverage |
| `TAF-48` | **Quarantine size is a published metric** in the `QA-011` report. A growing quarantine is a suite losing credibility, and it is visible before it is terminal |
| `TAF-49` | **No retry-until-green in any pipeline stage.** A retry configured to hide flake hides real intermittent product defects — race conditions, exactly the class `T-04` exists to find |
| `TAF-50` | **A quarantined test covering an `RC-A` case blocks the gate** unless a manual execution covers it. `RC-A` populations are statutory or irreversible; a quarantined test there is an untested `RC-A` case |

### 10.3 The common causes, pre-empted

| Cause | Prevention |
|---|---|
| Sleep-based waits | `TAF-19`, `TAF-12` |
| Test order dependence | `PYS-27`, `T-02`, `TAF-34`; the nightly profile **runs in randomised order** |
| Shared mutable data | `TAF-09`'s `HttpCase` cleanup; per-test data keys |
| Timezone assumptions | `TAF-10`'s UTC second pass |
| Real network calls | `TAF-51`: **no `A1`–`A3` test makes an outbound call to a third party.** External integrations are stubbed; the real call is exercised in `SANDBOX` certification (`IN-008` §7) |
| Clock and date rollover | Time is injected, never read from the system clock, in any test asserting on a date boundary |

---

## 11. CI Wiring and Execution Profiles

### 11.1 What the framework requires from a pipeline

**`PE-004` does not exist.** This section states the requirement it must satisfy, so that when
`PE-004` is written the framework's needs are already specified rather than negotiated.

| # | Requirement on `PE-004` |
|---|---|
| `TAF-52` | Ephemeral PostgreSQL 16 per run, seeded from a `QA-004` generator snapshot |
| `TAF-53` | Parallel execution across components, with results aggregated into one report |
| `TAF-54` | Artefact retention — traces, videos, coverage, results — for **at least the gate window** (T−6 to T+2) |
| `TAF-55` | A **nightly** trigger, and a **pre-merge** trigger with different profiles (§11.2) |
| `TAF-56` | Secret injection for role-account credentials, never in the repository (`XS-06`) |
| `TAF-57` | The pact broker and schema registry reachable from every build (`CT-02`, `FF-95`) |
| `TAF-58` | Device access for `A4` mobile — a lab or a farm (`TAF-23`) |
| `TAF-59` | **Results emitted in one normalised shape** that `QA-011` consumes without per-tool parsing |

### 11.2 Profiles

| Profile | Trigger | Contents | Budget | Blocks? |
|---|---|---|---|:--:|
| **`pre-commit`** | Local hook | Lint, format, secret scan (`G-01`), affected `A1` | < 30 s | Yes, locally |
| **`pre-merge`** | Pull request | Full `A1` for changed components + dependents · `A2` · `A3` schema + pact verification · affected `A4` smoke · `AR-012` blocking fitness functions · `SC-005` `G-01`…`G-10` | **< 20 min** | **Yes** |
| **`nightly`** | Schedule | Everything: full `A1`–`A4`, `slow`-tagged, concurrency harness, **randomised order**, **UTC second pass**, `A5` accessibility scan | < 3 h | Reports; blocks the next release |
| **`release`** | Release candidate | `nightly` + full regression core + smoke per portal + `A5` performance smoke | < 4 h | **Yes** |
| **`gate`** | T−4 weeks | `release` + full `A5` — performance at 1.5×, security suite, accessibility manual coordination, offline field coordination | days | **Yes** |

> **`TAF-60`. The `pre-merge` budget is 20 minutes and is a design constraint, not an aspiration.**
> A pull-request suite slower than that gets bypassed, and a bypassed gate is not a gate. When the
> budget is exceeded the response is to **move tests down a layer** (`TAF-02`) or into `nightly` —
> never to reduce what is checked before merge.

### 11.3 Result normalisation

| # | Rule |
|---|---|
| `TAF-61` | Every runner emits results in **one normalised shape** carrying: `tc_id`, level, component, result, duration, dataset version, environment, and artefact links |
| `TAF-62` | **`QA-011` consumes only that shape.** Per-tool parsing in the reporting layer is where coverage figures drift from execution reality |

---

## 12. Non-Functional Automation Interfaces

### 12.1 Performance — `QA-006`

| Element | Provision |
|---|---|
| Runner | **k6 2.0** (11 May 2026), with its browser mode for the journey-level scenarios |
| Shared with this framework | Fixtures, dataset selection, result normalisation (`TAF-61`) |
| Not shared | Workload models, volumetrics, think-time distributions — `QA-006` owns them |
| Environment | `PERF` only (`QA-001` §7.2) |
| Assertion model | Thresholds asserted **in the script**, so a run fails on its own criteria rather than on a human reading a chart |

### 12.2 Security — `QA-007`

| Element | Provision |
|---|---|
| SAST, DAST, SCA | **`SC-005` §5 gates `G-01`…`G-14`.** Not re-specified |
| What this framework supplies | The **negative-authorisation harness**: a parameterised suite that walks the `05-04` matrix and asserts each of the **379 denied cells** is denied **through the API as well as the UI** |
| Why it is framework code | 379 cells × per wave, hand-written, is not affordable. As a parameterised harness over a matrix it is one piece of code and a data file |
| Precondition | The 38 role accounts, with effective permissions asserted first (`TAF-33`) |

### 12.3 Accessibility — `QA-008`

| Element | Provision |
|---|---|
| Engine | An **ACT-rules-conformant** scan engine *(class — `TAF-01`)*, run in the `nightly` and `release` profiles |
| Ceiling | **~30%** of WCAG 2.2 AA criteria are automatable (`QA-001` §6.4). The remainder is human |
| Rule | `TAF-63`: **a clean automated scan is never reported as conformance.** `QA-008` §4 states what it does and does not prove |

### 12.4 Offline — L12

Per §7.3. The **conflict half** is automated in CI; the **field half** cannot be (`TAF-25`).

---

## 13. Build Sequence and Effort

### 13.1 The sequence

`QA-001` §10.5 route B recommends funding this framework as **Wave 0** work, before feature delivery.
This is what that means concretely.

| # | Stage | Contents | Effort | Prerequisite |
|:--:|---|---|---:|---|
| **0** | **Foundations** | Repository structure, result normalisation, fixture core, `QA-004` generator integration, role-account fixture | **~1.5 person-months** | `BE-004`, `QA-004` generator |
| **1** | **`A1` harness** | Odoo base classes and tags, pytest for services, Vitest, `flutter test`, pgTAP; coverage instrumentation incl. `@financial_path` | **~1.5 pm** | Stage 0 |
| **2** | **`A3` contract & event** | Pact emitters, schema conformance in `A2`, **negative-case generator**, replay/idempotency harness | **~2 pm** | `IN-002`, `IN-003`; **broker in `CI`** |
| **3** | **`A4` web** | Page-object base, bilingual runner, trace capture, the L6 journey suite | **~2.5 pm** | Stage 0; `UX-001` test identifiers |
| **4** | **Concurrency harness** | The `T-04` barrier fixture and its assertions | **~0.5 pm** | Stage 1 |
| **5** | **`A4` mobile** | `integration_test` harness, connectivity control, server-side sync observer | **~1.5 pm** | Device access |
| **6** | **Security harness** | The 379-cell parameterised negative suite | **~1 pm** | 38 role accounts |
| **7** | **Hardening** | Flake detection, quarantine automation, `TAF-37` reconciliation, anti-gaming checks | **~1 pm** | Stages 1–6 |
| | **Total** | | **~11.5 person-months** | |

### 13.2 Reading the number honestly

**~11.5 person-months** is roughly **two engineers for six months**, or **~19% of the programme's
entire 62 QA FTE-months** — and it must be spent **before** the surface it automates exists.

> **That is the actual shape of `QA-001` `Q-01`.** It is not a request for more testers; it is a
> request to spend a fifth of the test budget on machinery, up front, so that the remaining
> four-fifths can cover ~1,700 items across ~33 releases. **The alternative is not cheaper — it is
> the same money spent on manual re-execution, once per release, forever.** Stated in these terms so
> the decision at the W1 gate is between two costs rather than between a cost and nothing.

### 13.3 Who builds it

| Stage | Built by |
|---|---|
| 0, 1, 4 | Engineering, with the QA Lead — these are developer-facing and must be owned by developers to be used |
| 2 | Integration Lead with Engineering (`IN-008` co-owns) |
| 3, 5, 6, 7 | **QA Engineers** — and this is the work the 1 FTE at W1 cannot do while also executing `G1`'s scope |

---

## 14. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `QA-005-D-01` | Odoo unit-test runner | (a) a third-party runner over Odoo; (b) **Odoo's own framework** | **(b)** | A third-party runner re-implements the ORM's transaction and registry handling, badly, and breaks on every Odoo upgrade | §5; `TransactionCase`/`HttpCase` |
| `QA-005-D-02` | Tool binding | (a) name a product per layer for 36 months; (b) **name a capability class with a reference implementation, for browser, broker and accessibility engine** | **(b)** | `BEA-16` — MinIO was archived upstream on 25 April 2026 and the estate had not recorded it. A 36-month hard binding inherits that risk in every layer | `TAF-01`; `BE-007` currency policy applies to test tooling |
| `QA-005-D-03` | Negative contract cases | (a) hand-write per operation; (b) **generate from the OpenAPI schema** | **(b)** | 1,187 operations hand-written is unaffordable; generated it is one harness | `TAF-16` |
| `QA-005-D-04` | Flake handling | (a) retry until green; (b) **auto-quarantine + defect + 10-day clock + delete** | **(b)** | `XS-16` and `T-03` already make a flake a defect; retry hides real race conditions, which is the class `T-04` exists to find | `TAF-45`…`TAF-50`; no retry in any stage |
| `QA-005-D-05` | Financial-path identification | (a) reviewer judgement; (b) **code annotation cross-checked against `DI-01` and `DA-002`** | **(b)** | 100%-of-financial-calculations is unenforceable until the set is machine-decidable, and a judgement-based set is quietly small | `TAF-38`…`TAF-40` |
| `QA-005-D-06` | Pre-merge budget | (a) run everything; (b) **20-minute ceiling, overflow moves down a layer or to nightly** | **(b)** | A pull-request suite slower than ~20 minutes gets bypassed, and a bypassed gate is not a gate | `TAF-60` |
| `QA-005-D-07` | `demo/` data vs factories at `A1` | (a) `demo/` data per `AR-007` `T-01`; (b) **factories where content matters** | **(b)** — narrowing `T-01`, not contradicting it | Factories make the precondition visible in the test and immune to demo-data drift | `TAF-11` |

---

## 15. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | **Is the ~11.5 person-month framework build funded as Wave 0 work?** | CTO with CFO | **W1 gate** | Every automation target in `QA-001` §6.4; the whole of §13 |
| `Q-02` | When are the pact broker and schema registry available in `CI`? | Platform Engineering with Integration Lead | **W1** | `A3`; `CT-02`, `CT-07`, `FF-95` |
| `Q-03` | Does `UX-001` add stable test identifiers to the component library, and are they treated as an API? | Content Design Lead with Engineering | **W1** | `TAF-18`; the maintainability of every `A4` test |
| `Q-04` | Device lab or device farm for `A4` mobile, and who funds it? | Mobile Lead with CFO | **W2** | `TAF-23`; `G2-01`, `G6-06` |
| `Q-05` | Does `RQ-006` renumber the `NFR-090`/`091`/`092` collision, and when? | Enterprise Architecture | **W1** | `TAF-44`; every gate claim citing those identifiers |
| `Q-06` | Who owns the `@financial_path` annotation set, and is its cross-check against `DA-002` built? | Engineering Lead with the CFO's delegate | **W1** | `TAF-38`…`TAF-40`; the 100% gate |

---

## 16. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | Five layers are defined with a placement rule that decides ambiguous cases | §3 — `TAF-02` |
| `AC-02` | A tool is named per layer with version and verification date, or a capability class with a stated reason | §4 — 14 rows, 3 classes |
| `AC-03` | The Odoo harness is specified, including the three traps that cause most Odoo flake | §5 |
| `AC-04` | The `AR-007` `T-04` concurrency harness — required and previously unsupplied — is specified | §5.4 |
| `AC-05` | The contract and event layer adds only what `IN-008` does not own | §6.2 — 4 additions |
| `AC-06` | Coverage instrumentation makes both targets machine-decidable and gaming-resistant | §9 — `TAF-38`…`TAF-43` |
| `AC-07` | The flake policy has a mechanism, a clock and a consequence | §10 — `TAF-45`…`TAF-50` |
| `AC-08` | Pipeline requirements are stated so `PE-004` can satisfy them | §11.1 — 8 requirements |
| `AC-09` | Five execution profiles with time budgets and blocking behaviour | §11.2 |
| `AC-10` | `automated: yes` is machine-verified against emitted `tc_id`s | §8.5 — `TAF-37` |
| `AC-11` | The build is sequenced, costed and assigned | §13 — **~11.5 person-months** |

**Definition of done.** Complete when every criterion is met, stages 0–2 are built and running in
`CI`, the `pre-merge` profile holds under 20 minutes on the W1 codebase, and the approver has signed.
Approval carries the `PGD-A1-09` qualification.

---

## 17. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `QA-001` §6 | The ratio and layer strategy this framework implements |
| Upstream | `QA-003` | The cases it implements; `tc_id` reconciliation |
| Upstream | `QA-004` | Fixtures, generators, the 38 role accounts |
| Upstream | `AR-007` §9 | Test gates and `T-01`…`T-04` |
| Upstream | `BE-002` §8 | `XS-16`, `XS-17`, `PYS-26`, `PYS-27` |
| Upstream | `IN-008` §4, §5 | Pact lifecycle and event testing — the authority |
| Upstream | `BE-005`, `BE-006` | Component identity and `component.yaml` |
| Downstream | `QA-006`, `QA-007`, `QA-008` | Share fixtures, runner and result shape |
| Downstream | `QA-011` | Consumes the normalised result shape and the `tc_id` reconciliation |
| Downstream | `PE-004` | §11.1 is its requirement input |
| Lateral | `AR-012` | Fitness functions share the pipeline; different purpose (`QA-001` §4.6) |
| Lateral | `SC-005` §5 | Security gates consumed, not re-specified |

---

## 18. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` · `./_CATEGORY_OVERVIEW.md` ·
`./QA-001_Master_Test_Strategy.md` · `./QA-002_Test_Plans_per_Level.md` ·
`./QA-003_Test_Design_Specification_and_Case_Repository.md` · `./QA-004_Test_Data_Management_and_Anonymisation_Plan.md` ·
`./QA-006_Performance_and_Load_Test_Plan.md` · `./QA-007_Security_Test_Plan.md` ·
`./QA-008_Accessibility_Test_Plan.md` · `./QA-011_Requirements_to_Test_Coverage_Standard_and_Report.md` ·
`../02_Architecture_and_Design/AR-007_Odoo_Module_Architecture_and_Code_Structure_Standard.md` ·
`../02_Architecture_and_Design/AR-012_Architecture_Compliance_and_Fitness_Function_Standard.md` ·
`../04_Integration_and_API_Engineering/IN-002_API_Specification_OpenAPI_Contracts.md` ·
`../04_Integration_and_API_Engineering/IN-003_Domain_Event_Catalogue_and_Schema_Registry.md` ·
`../04_Integration_and_API_Engineering/IN-008_Integration_Test_Sandbox_and_Certification_Specification.md` ·
`../05_Security_Privacy_and_Compliance/SC-005_Secure_Development_Lifecycle_Standard.md` ·
`../07_Build_Engineering_and_Development_Standards/BE-001_Development_Environment_Setup_Guide.md` ·
`../07_Build_Engineering_and_Development_Standards/BE-002_Coding_Standards_and_Style_Guide.md` ·
`../07_Build_Engineering_and_Development_Standards/BE-004_Repository_and_Monorepo_Structure_Standard.md` ·
`../07_Build_Engineering_and_Development_Standards/BE-007_Dependency_Licence_and_SBOM_Management_Standard.md`

**Workspace**
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md` §11 ·
`../../project_content/13_Test_and_Acceptance_Content/TS-013_Regression_Pack_and_Smoke_Test_Checklist.md` ·
`../../project_content/_AUDIT/AUDIT-014_Category_13_TS_Content_Audit.md`

**External — verified 2026-08-18**
Odoo 19.0 testing documentation (`TransactionCase`, `HttpCase`, `--test-tags`, `at_install`/`post_install`) ·
Python 3.12 · PostgreSQL 16 · Node.js 20 LTS · Grafana k6 2.0 (11 May 2026) ·
OpenAPI 3.1 · AsyncAPI 3.0 · ISO/IEC/IEEE 29119-2:2021 · W3C ACT Rules Format

---

## 19. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Quality Engineering with Engineering | Initial issue. Five layers with a placement rule; a tool per layer with versions and verification dates, and **three deliberate capability-class bindings** rather than 36-month product commitments (`BEA-16` rationale); the Odoo harness with **the three traps that cause most Odoo flake**; **the `AR-007` `T-04` concurrency harness, required since `AR-007` and never supplied**; generated negative contract cases over 1,187 operations; the 379-cell parameterised negative-authorisation harness; coverage instrumentation making **both targets machine-decidable** via `@financial_path` cross-checked against `DI-01` and `DA-002`, with three anti-gaming mechanisms; a flake policy with quarantine, a 10-day clock and **no retry-until-green anywhere**; eight requirements on the unwritten `PE-004`; five execution profiles with a **hard 20-minute pre-merge budget**; `TAF-37` reconciliation making `automated: yes` machine-verified; and a sequenced, costed build of **~11.5 person-months**. Records the `NFR-090` collision position (`TAF-44`) | *Pending — `GV-002`* |

---

*`QA-005` · Category 08 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
