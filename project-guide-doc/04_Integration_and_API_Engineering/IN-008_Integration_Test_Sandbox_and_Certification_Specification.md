---
id: IN-008
title: Integration Test, Sandbox & Certification Specification
category: 04 — Integration & API Engineering
code: IN
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Integration Architect with QA Lead
approver: Design Authority (constituted under GV-002)
standards_basis: >
  ISO/IEC/IEEE 29119-2:2021 (test processes) · ISO/IEC/IEEE 29119-3:2021 (test documentation) ·
  Consumer-driven contract testing (Pact-style) · OpenAPI 3.1 · AsyncAPI 3.0 ·
  Test pyramid (Cohn) · Chaos engineering principles
traces_to: >
  PGD-000 IN-008 · M28 FR-IPF-019, AC-08, AC-13 · TS-001 §4.7 · AP-010 · AP-004 §4.12 ·
  audit AP-12 (medium), AP-03, AP-08 · NFR-050, NFR-071 · IN-001…IN-007 · QA-005
depends_on: IN-002 · IN-003 · IN-004 · IN-005 · IN-006 · IN-007 · TS-001
verified_on: 2026-08-18
priority: P1
needed_by: W2
enumeration_timestamp: 2026-08-18 17:25 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# IN-008 — Integration Test, Sandbox & Certification Specification

### Category 04 · Code `IN` · ISO/IEC/IEEE 29119 · Consumer-driven contract testing

---

> **The measured test surface, 2026-08-18 17:25 (+06):**
>
> | What must be verified | Count |
> |---|---:|
> | API operations (`IN-002`) | **1,187** |
> | Domain events (`IN-003`) | **988** |
> | External integrations (`IN-004`) | **47**, of which **13 are P0** |
> | Portals and applications consuming them | **12** |
> | Modules producing them | **67** |
> | **Provider–consumer pairs to contract-test** | **~800** measured pairs across portals and modules |
> | Environments `TS-001` §4.7 specifies | **6** |
> | Of those, **provisioned** | **0** (`TS-001` `O-03`) |
> | Environments that can serve as a **partner sandbox** | **0** (`AP-010` §4.2) |
>
> **`FR-IPF-019` requires a sandbox with representative masked data for external consumers, and
> `AUDIT-016` `AP-12` records that the partner sandbox is a seventh environment `TS-001` §4.7 does
> not have.** This document specifies it, and the certification a partner must pass before a
> production credential is issued.

---

## 1. Purpose

`IN-002` through `IN-007` specify what the integration surface **is**. This document specifies how
anyone knows it is **true**: the test layers and what belongs in each, consumer-driven contract
testing across ~800 pairs, the mock and fixture strategy that lets 67 modules and 12 portals develop
without each other, the sandbox environment and its data rules, the partner certification checklist,
and the drills that turn `NFR-050`'s "documented, tested manual fallback" from an assertion into
evidence.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | The **integration test layers**, and the rule that assigns a test to one |
| 2 | **Consumer-driven contract testing** — the mechanism, the pairs, the CI wiring |
| 3 | Mocks, stubs and **recorded fixtures** for the 47 external systems |
| 4 | Event-contract testing: schema, idempotency, ordering, replay, **`R3` refusal** |
| 5 | **The `SANDBOX` environment** — the seventh `AP-12` identified |
| 6 | Sandbox data rules, and why they are **stricter** than `NFR-071` masking |
| 7 | Test credentials and their lifecycle |
| 8 | **Partner certification** — the checklist, the evidence, the gate |
| 9 | **Fallback drills** — what `NFR-050`'s "tested" means as evidence |
| 10 | Resilience and chaos testing: induced timeout, breaker, poison, replay |
| 11 | The negative-case register consolidated from `IN-001`…`IN-007` |
| 12 | Wave-gate evidence per integration |

**Explicitly out of scope**

| Topic | Owned by | Why |
|---|---|---|
| Programme test strategy, test management, defect process | `QA-001`, `QA-003` | This is the **integration** slice |
| Unit testing standards | `BE-*` | |
| Performance and load testing | `QA-*`, `PE-*` | §10 tests *behaviour under failure*, not throughput |
| Environment provisioning and infrastructure | `PE-*`, `TS-001` | This states what `SANDBOX` must be; `PE` builds it |
| UAT scripts and business acceptance | `TS-*` content, `RQ-010` | |
| Security testing and penetration | `SC-*` | §10.6 names the overlap |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| QA Lead | §3–§5 are the integration test design |
| Module and portal developers | §4's contract tests are their CI gate |
| Partner developers | §8's certification checklist is what they must pass |
| Platform engineers | §6's `SANDBOX` specification |
| Service desk and Ops | §9's drills |
| Wave-gate assessors | §11's evidence table |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Conformance | Departure |
|---|---|---|
| **ISO/IEC/IEEE 29119-2:2021** | Test process framework; §3's layers map to its test levels | Inherits `QA-001`'s programme framing |
| **ISO/IEC/IEEE 29119-3:2021** | Test documentation — §11's evidence table is a test-completion report structure | |
| **Consumer-driven contract testing** | §4 — the consumer publishes its expectation; the provider verifies against it | Named as Pact-style because the vendor market recognises it |
| **Test pyramid** | §3.6 — the shape, and why the estate's is unusual | **Departure:** the estate's integration layer is unusually heavy because 67 modules and 12 portals communicate almost entirely through contracts |
| **Chaos engineering principles** | §10 — induced failure as a routine test, not an event | Scoped to integration failure modes only |

### 2.2 Source material

| Source | Contribution |
|---|---|
| `IN-002` | 1,187 operations; `FF-57` requires each exercised by a contract test |
| `IN-003` | 988 events; the registry is the test oracle |
| `IN-004` | Each ICD's §12 failure matrix is a **test charter** |
| `IN-006` §9 | **Sixteen negative cases**, already enumerated |
| `IN-007` §13 | Ten money-path gates |
| **`AP-010`** | Sandbox onboarding and test-credential **content** — written against a sandbox that does not exist |
| `AP-004` §4.11, §4.12 | Webhook testing and the negative cases requested of `TS-017` |
| **`TS-001` §4.7** | Six environments — `DEV`, `CI`, `SIT`, `UAT`, `PERF`, `TRAIN` — and its `O-03`: **none is specified or provisioned** |
| `AUDIT-016` `AP-12` | The sandbox is a **seventh** environment |
| `M28` `AC-08`, `AC-13`, `FR-IPF-019` | Coverage, fallback timing, sandbox requirement |
| `NFR-050`, `NFR-071` | Tested fallback; data masking |

### 2.3 Audit findings this document closes or contributes to

| Finding | Disposition |
|---|---|
| **`AP-12` (medium)** — the partner sandbox is a seventh environment `TS-001` §4.7 does not have | **Specified.** §6 defines `SANDBOX` with its own data-state row. **`TS-001` §4.7 must be amended** — a Category 13 correction requiring the QA Lead (`AP-010` `O-03`) |
| `AP-010` `P-02`, `AP-012` `RV-2` — the promotion gate | §8.4 makes it a **blocking** gate with evidence, not a checklist item |
| `AP-03` — content registered a wave after first consumption | §12 sequences this document's own outputs **one wave ahead**, deliberately |
| `AP-08` — an integration reaching production with `Undetermined` disclosure rows defeats `IP-10` silently | §8.4 `CERT-08` makes `Determined` a **certification precondition** |
| `M28` `AC-08` — 100% CI-validated OpenAPI coverage | §4.6 — measurable from the contract set; **a Wave 9 criterion, not a Wave 1 one** |
| `NFR-050` — every P0 integration has a **tested** manual fallback | §9 — **currently 0 of 13** |

---

## 3. The Test Layers

### 3.1 Six layers

| # | Layer | Verifies | Runs against | Frequency |
|---|---|---|---|---|
| **L1 Schema** | A payload matches its contract | The OpenAPI / JSON Schema | Every build |
| **L2 Contract (consumer-driven)** | A provider satisfies what a consumer actually needs | A **pact** published by the consumer | Every build, both sides |
| **L3 Component** | One module's integration behaviour, in isolation | **Mocks** of its dependencies | Every build |
| **L4 Integration** | Two or more real modules together | `SIT` | Nightly + on merge to main |
| **L5 External** | A real external counterparty | **The counterparty's sandbox** | Nightly, and before every wave gate |
| **L6 Resilience** | Behaviour under induced failure | `SIT` with fault injection | Weekly + before every wave gate |

### 3.2 The assignment rule

> **A test belongs to the highest layer at which it can fail, and no higher.**

| Question | Layer |
|---|---|
| Can this fail with a single payload? | **L1** |
| Can it fail only because a consumer expects something the provider does not give? | **L2** |
| Can it fail only when this module runs? | **L3** |
| Does it need two real modules? | **L4** |
| Does it need the real counterparty? | **L5** |
| Does it need something to break? | **L6** |

**Why the rule matters:** the estate has 1,187 operations and ~800 provider–consumer pairs. A test
placed one layer too high costs orders of magnitude more to run and is orders of magnitude flakier.
**Placing an ordering assumption at L5 instead of L2 is how a suite becomes untrustworthy.**

### 3.3 What each layer must not do

| Layer | Must not |
|---|---|
| L1 | Assert business rules. A schema says a field is a date; `RQ-009` says whether it may be in the past |
| L2 | Test the provider's internals. A pact is an **expectation**, not an implementation test |
| L3 | Use a real external system. That is L5 |
| L4 | Substitute for L2. Two modules passing together does not mean the **contract** is satisfied |
| L5 | Run against **production**. Ever |
| L6 | Run in production **without an approved game-day** |

### 3.4 The estate's unusual shape

A conventional test pyramid is unit-heavy. **This estate's is integration-heavy by construction**:
67 modules communicate almost entirely through 1,187 operations and 988 events, and 12 portals hold
no business logic at all (`LB-07`).

> **The consequence, stated because it affects resourcing:** the integration test suite is not a thin
> layer above unit tests. **It is the layer that carries most of the assurance**, and it is where
> `AR-006`'s 447 dependency edges and 18 cycles become observable. `QA-001` should size it
> accordingly.

---

## 4. Consumer-Driven Contract Testing

### 4.1 The mechanism

| Step | Actor |
|---|---|
| 1 | **The consumer** writes a test declaring what it needs — path, method, request, the fields of the response it uses |
| 2 | The test runs against a local stub and **emits a pact** |
| 3 | The pact is published to a broker, tagged with the consumer and its version |
| 4 | **The provider's CI verifies every published pact** against its real implementation |
| 5 | A provider change that breaks any pact **fails the provider's build**, before merge |

### 4.2 Why consumer-driven, and not provider-published mocks

| | Provider-published mock | **Consumer-driven pact** |
|---|---|---|
| Who states the expectation | The provider guesses | **The consumer states what it uses** |
| Detects an unused field being removed | ✘ blocks a safe change | ✅ permits it |
| Detects a **used** field being removed | Only if the mock happens to cover it | ✅ **always** |
| Answers "who breaks if I change this?" | ✘ | **✅ — it is a query over published pacts** |

> **The last row is the decisive one.** With 100 portal-consumed paths already unmatched
> (`IN-001` §11) and 69 portal-consumed events unpublished (`IN-003` §7), the estate's specific
> failure mode is **each side authored correctly and independently, with nobody running the join.**
> A pact broker *is* the join, running continuously.

### 4.3 The measured pair count

| Relationship | Pairs |
|---|---:|
| Portal → module (paths a portal consumes) | **140 distinct paths**, across 12 portals |
| Portal → module (events a portal consumes) | **102 distinct events** |
| Module → module (synchronous) | ~250 |
| Module → module (events) | **988 events with declared consumers** |
| CON-03 portal ↔ ERP | **22 endpoints + 11 webhooks** |
| **Approximate provider–consumer pairs requiring a pact** | **~800** |

### 4.4 The rules

| # | Rule |
|---|---|
| **CT-01** | **Every consumer of an internal API publishes a pact.** No pact, no dependency |
| **CT-02** | A provider's build **fails** if any published pact fails verification (`FF-95`) |
| **CT-03** | A pact declares **only the fields the consumer uses**. Over-specifying blocks safe additive change |
| **CT-04** | A pact is versioned with the consumer, and verified against **every supported provider version** (`IN-005` §8.4 — two) |
| **CT-05** | **The pact broker is the authoritative answer to "who consumes this?"** — it supersedes the module `§12` tables, which `IN-002-D-02` demoted to a human index |
| **CT-06** | Event consumers publish pacts too — **the message shape they require**, verified against the `IN-003` registry |
| **CT-07** | A **new** consumer's pact that no provider satisfies **fails the consumer's build**, not the provider's. This is what would have caught the 100 unmatched paths at authoring time |
| **CT-08** | External partner consumers do **not** publish pacts. Their equivalent is **certification** (§8) |

> **`CT-07` is the control the estate most needs.** Every one of the 100 unmatched portal paths and
> 69 unpublished events would have failed at the moment the portal specification was written.

### 4.5 Where pacts do not apply

| Surface | Instead |
|---|---|
| External counterparties (the 47) | **Recorded fixtures** (§5) and **L5 sandbox tests** |
| Outbound webhooks to partners | Partner **certification** (§8) |
| Batch file interfaces | **Golden-file tests** — a known input produces a byte-identical file |
| The public tracking view | A single L2 pact from the portal, plus L6 abuse tests |

### 4.6 Coverage measurement — `M28` `AC-08`

`M28` `AC-08` requires *"100% of published endpoints have a current, CI-validated OpenAPI 3.1
specification."* With `IN-002` issued, this becomes measurable:

| Metric | Formula | Today |
|---|---|---|
| Contract coverage | operations in a contract ÷ 1,187 | **35 / 1,187 = 2.9%** |
| Contract-test coverage | operations with ≥1 passing pact ÷ operations in a contract | 0% |
| Event registration coverage | registrations ÷ 988 | ~0% |
| Consumer pact coverage | consumers with a published pact ÷ registered consumers | 0% |

> **`AC-08` is a Wave 9 criterion, not a Wave 1 one**, and `IN-002` §14 says so. What Wave 1 must
> achieve is **100% coverage of the W1 contract set** (~405 operations), not of the estate.

---

## 5. Mocks, Stubs and Fixtures

### 5.1 Three different things

| | **Stub** | **Mock** | **Recorded fixture** |
|---|---|---|---|
| What | A canned response | A programmable double with expectations | A **real** counterparty response, captured |
| Used at | L1, L3 | L3 | **L3 and L5** |
| For | Internal dependencies | Internal dependencies | **The 47 external systems** |
| Fidelity | Low | Low | **Exact** |

### 5.2 Why fixtures are recorded, not written

> **`IN-001` `AC-10` requires every anticorruption layer to be independently testable with a recorded
> fixture set, without the counterparty.** Fixtures are **recorded from the counterparty's sandbox**,
> never hand-written, because a hand-written fixture encodes what we *believe* the counterparty
> returns — and the whole purpose of an ACL is to absorb the difference between belief and reality.

| # | Rule |
|---|---|
| **FX-01** | Fixtures are captured from the counterparty's sandbox, verbatim, including headers |
| **FX-02** | Every fixture is **dated**, and **re-captured at every wave gate**. A counterparty's response shape changes without notice |
| **FX-03** | Fixtures cover the **success case and every failure mode in the ICD's §12 matrix** — not the happy path alone |
| **FX-04** | **No real personal data in a fixture.** Values are replaced at capture, and the replacement is recorded so the shape is preserved |
| **FX-05** | A fixture that no longer matches a live sandbox response is a **finding**, not a test to update silently |

### 5.3 The mock services the estate needs

| Mock | Serves | Notes |
|---|---|---|
| **Payment rail mock** (bKash, Nagad, SSLCOMMERZ shapes) | L3, and L6's induced timeouts | **Must be able to hang for 30+ seconds** — otherwise `IN-007`'s `unknown` state is never exercised |
| **Courier mock** | L3, and the three status vocabularies | Must emit an **unmapped status** to exercise `AC-03`'s alerting `unknown` branch |
| **SMS / WhatsApp mock** | L3 | Must simulate delivery-receipt lag |
| **Webhook consumer mock** | Outbound delivery tests | Must simulate `5xx`, `410`, timeout, and **body re-serialisation** (`IN-006` N-14) |
| **Bank file mock** | L3 golden-file tests | Acknowledgement and rejection files |

> **The payment mock's ability to hang is a first-class requirement, not a nicety.** `IN-007-D-01`
> introduces `unknown` as a state reachable only by timeout. **A test suite that cannot induce a
> timeout cannot test the single most important state in the money path.**

---

## 6. The `SANDBOX` Environment

### 6.1 The finding, restated

`TS-001` §4.7 specifies six environments — `DEV`, `CI`, `SIT`, `UAT`, `PERF`, `TRAIN` — and records
at its `O-03` that **none of the six is specified or provisioned**. `FR-IPF-019` requires a sandbox
with representative masked data for external consumers. `AP-010` §4.2 tested each of the six against
the requirement: **none can serve.**

**`UAT` emphatically cannot:**

> `TS-001` §4.7 requires UAT data to be **frozen during a UAT cycle**, and `TX-08` voids a script
> whose expected results were not written before execution. **A partner exercising integration flows
> in UAT changes the data business super-users are signing against.**

### 6.2 Why `SANDBOX` is genuinely a seventh environment

Its data-state requirements are **unlike any of the six**:

| Requirement | Which of the six has it |
|---|---|
| Stable enough to build against for weeks | `TRAIN`, but `TRAIN` is not externally reachable |
| **Resettable per partner**, on demand | **None** |
| **Externally reachable** from the public internet | **None** |
| **Externally credentialled**, with partner-held secrets | **None** |
| **No real personal data at all** | `TRAIN` masks; **none holds none** |

### 6.3 The data rule, and why it is stricter than `NFR-071`

> **`SB-01`. `SANDBOX` holds no real personal data of any kind — not masked, not pseudonymised,
> not a subset. Synthetic only.**

`NFR-071` requires masking in non-production environments. **This is a stricter bar, and the reason
is the population with access:**

| Environment | Who can reach it |
|---|---|
| `SIT`, `UAT`, `TRAIN` | Employees and contracted staff, under employment obligations |
| **`SANDBOX`** | **17+ brand partners, 500–2,000 marketplace sellers, corporate client developers, courier engineers — people outside the company entirely** |

Masked data is **re-identifiable** given enough auxiliary information, and a population of thousands
of external developers is exactly the auxiliary-information-rich condition under which masking
fails. **Synthetic-only removes the question.**

### 6.4 The specification

| Property | Value |
|---|---|
| Reachability | Public internet, TLS 1.3, separate hostnames from production |
| Data | **Synthetic only** (`SB-01`), generated to a seeded, reproducible set |
| Reset | **Per partner, on demand**, without affecting others — so partner tenancy is isolated |
| Refresh | Base data set refreshed each wave; a partner's own data reset on request |
| Credentials | Partner-held, sandbox-scoped, `sandbox` rate-limit class (`IN-005` §9.2) |
| Isolation | **No path to production data.** No shared database, no shared queue, no shared vault path |
| External rails | **The counterparties' own sandboxes**, never their production endpoints |
| Availability target | Best-effort. **Explicitly not covered by production SLOs** — and partners are told so |
| Money | **No real money moves.** Rail sandboxes only |
| Retention | Partner data purged on credential revocation |

### 6.5 What must change in `TS-001`

| # | Change | Owner |
|---|---|---|
| 1 | Add `SANDBOX` to §4.7's environment inventory **with its own data-state row** | QA Lead (Category 13) |
| 2 | Carry it into whatever provisions the other six | Platform Engineering |
| 3 | Record that its data rule is **stricter** than `NFR-071`, and why | QA Lead |

> **`AP-12`'s remediation instruction, restated: this is a correction to a Category 13 file, so it
> needs the QA Lead as well as the author.** `AP-010` `O-03`.

---

## 7. Test Credentials

| # | Rule |
|---|---|
| **TC-01** | A sandbox credential is **environment-bound**; used against production it returns `401 auth.environment_mismatch` |
| **TC-02** | It carries the **same scopes** the partner's production credential will carry — so certification tests the real permission model |
| **TC-03** | It is **time-boxed** and renewable, and expiry is alerted like any other (`IN-005` §6) |
| **TC-04** | Rail test credentials (bKash sandbox, SSLCOMMERZ sandbox, Nagad test merchant) are **vault-held and rotated**, not pasted into a guide |
| **TC-05** | **`AP-010`'s published test data is synthetic and stated as such** — a partner must never be given a real card number, a real NID or a real MSISDN |
| **TC-06** | A partner's sandbox credential is **revoked on certification failure** and reissued for a retest |

---

## 8. Partner Certification

### 8.1 What certification is

**A gate, not a courtesy.** `IN-005` `FF-76` blocks the issue of a production credential to any
external consumer without a certification record.

### 8.2 Who must certify

| Consumer | Certification |
|---|---|
| Brand partners (17+) | **Required** |
| Corporate clients using the API | **Required** |
| Marketplace sellers using the seller API | **Required** — lightweight variant |
| Couriers, payment rails | **Reverse** — *we* certify against *their* sandbox (§8.6) |
| The CON-03 portal platform | **Required**, and it is the first (W1) |
| Internal portals | Contract tests (§4) instead |

### 8.3 The checklist

| # | Criterion | Evidence |
|---|---|---|
| **CERT-01** | Authenticates with the correct grant type; **does not attempt `implicit` or ROPC** | Auth logs |
| **CERT-02** | **Sends `Idempotency-Key` on every state-changing request** | Request logs |
| **CERT-03** | **Retries correctly** — honours `Retry-After`, backs off with jitter, reuses the same key | Induced `429` and `503` |
| **CERT-04** | **Handles `403` without probing.** Does not enumerate identifiers after an out-of-scope refusal | Induced `403`; request pattern |
| **CERT-05** | **Verifies webhook signatures against the raw body**, in constant time | `testWebhookEndpoint` result (`IN-006` §7.1) |
| **CERT-06** | **Rejects a replayed `webhook-id` and an out-of-window timestamp** | Deliberate replay and skewed delivery |
| **CERT-07** | **Acknowledges webhooks within 10 s**, before processing | Delivery latency |
| **CERT-08** | **Their `AP-012` disclosure register rows are `Determined`** | `AP-012` register |
| **CERT-09** | An `NFR-098` **processor contract** exists where they process personal data | Legal register |
| **CERT-10** | **Tolerates an added response field** without failing | A field is added mid-test |
| **CERT-11** | **Tolerates out-of-order webhook delivery**; discards the older by `occurred_at` | Deliberate reordering |
| **CERT-12** | Handles a **secret rotation** without a delivery gap | A rotation is performed mid-test |
| **CERT-13** | Their **notice contact** in the consumer register is a role and reachable | A test notice |
| **CERT-14** | Does **not** log or echo secrets, tokens or signatures | Their own attestation plus a scan of anything they return |

### 8.4 The gate

| # | Rule |
|---|---|
| **CG-01** | **Certification precedes a production credential.** `FF-76` blocks it |
| **CG-02** | **`CERT-08` and `CERT-09` are blocking regardless of technical readiness.** A perfectly implemented integration with `Undetermined` disclosure rows does not go live (`AP-012` `DS-01`) |
| **CG-03** | Certification is **re-run** on a `MAJOR` version migration |
| **CG-04** | A failure is **recorded with its criterion**, and the retest is a new record — not an edit |
| **CG-05** | Certification records live in the **consumer register** (`IN-005` §7) |

> **`CG-02` is the control `AP-08` said the whole disclosure register depends on.** *"Structural and
> expected — but only workable if the promotion gate actually holds. An integration reaching
> production with `Undetermined` rows defeats `IP-10` silently."* **This is the gate holding.**

### 8.5 The lightweight variant

500–2,000 marketplace sellers cannot each undergo a full certification. **Sellers integrating through
the seller API certify against `CERT-01`, `-02`, `-03`, `-05`, `-06`, `-07` only**, automated end to
end, with a self-service result. The remainder are covered by the marketplace's own terms rather than
by a per-seller assessment.

> **Stated because the alternative fails silently:** a certification process that cannot scale to its
> population will be waived in practice, and a waived gate is worse than a designed-for-scale one.

### 8.6 Reverse certification — us against them

For the 47 external systems, **we are the consumer**. Before an integration is promoted (`IN-001`
S3→S4):

| # | Criterion |
|---|---|
| Every ICD §12 failure mode has been **exercised against their sandbox** |
| Every fixture has been **captured and dated** (`FX-01`, `FX-02`) |
| The **read-back path** is proven, including under an induced timeout (`PT-05`) |
| Their **signature verification** is proven, including a deliberate bad signature |
| The **manual fallback has been run end to end by the team that will run it at 2 a.m.** |

---

## 9. Fallback Drills

### 9.1 What "tested" means

`NFR-050`: *"Every P0 integration has a documented, tested manual fallback."* `AR-001` §7.2: *"A P0
integration whose fallback has not been exercised is a **wave-gate failure**, not a risk."*

> **Measured today: 0 of 13 P0 integrations has a tested fallback** (`IN-001` §10.3). The
> denominator is **13**, counted from `05-03` §2's rows rather than its summary (`PE-A-01`).

### 9.2 The drill

| # | Rule |
|---|---|
| **DR-01** | Each P0 integration's fallback is drilled **at least once per wave gate** (`IN-001` `FB-02`) |
| **DR-02** | The drill is run by **the people who would run it in an incident**, not by the engineer who wrote it |
| **DR-03** | It is run **against a realistic volume**, not one transaction |
| **DR-04** | It is **timed**. `FB-04`: a fallback requiring more than **15 minutes of manual work per transaction** is not a fallback; it is an outage with paperwork |
| **DR-05** | The drill record — date, participants, duration, defects — is the **wave-gate evidence** |
| **DR-06** | A drill that fails **blocks the gate**. It does not become a risk-register row |
| **DR-07** | `/api/v1/platform/integrations/{id}/test-fallback` exercises a registered fallback in a scheduled drill (`M28` §12.5) |

### 9.3 The twelve

| `INT` | Integration | Fallback | Drill owner |
|---|---|---|---|
| 001–003 | bKash · Nagad · SSLCOMMERZ | Alternative gateway; **cash at counter**; link resent | Branch ops + Finance |
| 005 | BEFTN | **Manual bank-portal submission** | Treasury |
| 006 | Bank statement import | Manual statement upload | Finance |
| 010 | SMS gateway | Failover gateway → WhatsApp → push → queue | Contact centre |
| 012 | WhatsApp | SMS → email → in-app inbox | Contact centre |
| 013 | Email | Alternative relay | IT |
| 014 | Push | **SMS for critical messages** | Contact centre |
| 019 | Google Maps | Cached geocodes → OSRM → manual address entry | Dispatch |
| 023 | Traccar | Last known position; manual status updates | Dispatch |
| 034 | NID verification | **Manual document review by compliance** | Compliance |

> **`DR-04` will fail for at least two of these on first drill**, and that is the point of timing
> them. Manual bank-portal submission of a payroll file and manual document review for KYC are both
> plausibly over fifteen minutes per transaction at volume. **Discovering that in a drill is cheap;
> discovering it during an outage is not.**

---

## 10. Resilience Testing

### 10.1 The induced failures

| # | Failure | Expected behaviour | Verifies |
|---|---|---|---|
| **RT-01** | External call **times out at 30 s** | Payment enters **`unknown`**; read-back resolves it | `IN-007-D-01`, `FF-85` |
| **RT-02** | External returns `5xx` on 50% of 20 calls | **Breaker opens**; fallback engages **within seconds** | `IN-001-D-02`, `M28` `AC-13` |
| **RT-03** | Breaker open, then counterparty recovers | Half-open probe closes it; **no thundering herd** | §7.1 rung 4 |
| **RT-04** | One counterparty is slow | **Bulkhead holds**; other integrations unaffected | Rung 5 |
| **RT-05** | Bus unavailable for 10 minutes | **Outbox accumulates; state stays correct**; alert on **age**, not only depth | `AR-009` §5.3, §5.4 |
| **RT-06** | Poison message on a consumer | 3 retries → DLQ → alert; **the stream does not block** | `AR-009` C-03, C-04 |
| **RT-07** | Duplicate event delivery | Consumer is idempotent; **no double effect** | C-01 |
| **RT-08** | Events delivered out of order **across aggregates** | Consumer tolerates it | C-02 |
| **RT-09** | **Replay of an `R3` consumer without an override** | **Refused**, logged | `IN-003` §8.3, `FF-67` |
| **RT-10** | Webhook consumer fails 5 times | Endpoint auto-disabled; owner notified; events in `dlq.external` | `IN-006` §5.6 |
| **RT-11** | Signature verification fails inbound | `401`; **not processed**; security event | `IN-006` N-10 |
| **RT-12** | Read-back **disagrees** with a webhook | **The read-back wins**; break raised | `PAY-01`, N-13 |
| **RT-13** | Rate limit exceeded | `429` with `Retry-After`; correct backoff; **the retried request is not duplicated** | `RL-05` |
| **RT-14** | Batch file with a **broken control total** | **Whole file rejected**; nothing partially applied | `PT-06`, `BF-02` |
| **RT-15** | Credential expires mid-flow | `401 auth.credential_expired`; **alerting fired at 30 and 7 days** | `IN-005` §6 |

### 10.2 The consolidated negative-case register

| Source | Cases |
|---|---:|
| `IN-006` §9 — webhook | **16** |
| §10.1 — resilience | **15** |
| Per-ICD §12 failure matrices (`IN-004`) | **14 ICDs × 6–8** ≈ 100 |
| `IN-007` money path | 10 gates |
| **Total negative cases to automate** | **~140** |

### 10.3 Where this meets security testing

`SC-002`'s threat model and this document overlap at four points, and the boundary is stated so
neither assumes the other covers it:

| Case | Owned by |
|---|---|
| SSRF via endpoint registration (`IN-006` `UV-01`…`UV-08`) | **Both.** Functional test here; adversarial test in `SC-*` |
| `403` probing for record existence (`FF-51`) | **Here** — it is a contract property |
| Signature forgery and replay | **Both** |
| Secret leakage into logs (`FF-82`, `FF-90`) | **Here** — it is a build gate |

---

## 11. Wave-Gate Evidence

What an assessor must see, per integration, before a gate passes (`GV-009`):

| # | Evidence | Source |
|---|---|---|
| E-01 | ICD at **`Agreed`** or better | `IN-004` §2.6 |
| E-02 | Contract published and CI-validated | `FF-46`, `FF-56` |
| E-03 | Every operation exercised by ≥1 passing pact | `FF-57`, `FF-95` |
| E-04 | Every event registered with a schema | `FF-59` |
| E-05 | Fixtures captured and **dated within the wave** | `FX-02` |
| E-06 | Sandbox certification passed (external consumers) | §8 |
| E-07 | **Fallback drill record within the wave** (P0) | §9, `FF-93` |
| E-08 | Resilience cases RT-01…RT-15 passing | §10.1 |
| E-09 | `AP-012` rows **`Determined`** | `CERT-08` |
| E-10 | `NFR-098` processor contract where applicable | `CERT-09` |
| E-11 | Monitoring, alerting and breaker thresholds configured | `05-03` §7 |
| E-12 | No open **Critical** or **High** integration defect | `QA-001` |

### 11.1 Gates this document adds

| # | Check | Timing | Enforcement |
|---|---|---|---|
| **FF-95** | A provider's build fails if any published pact fails verification | CI | Fail |
| **FF-96** | A consumer's build fails if its pact is satisfied by **no** provider (`CT-07`) | CI | Fail |
| **FF-97** | Every external fixture is dated within the current wave | Wave gate | Fail |
| **FF-98** | No `SANDBOX` record matches a production personal-data value (`SB-01`) | Nightly scan | **Incident** |
| **FF-99** | No production credential is issued without a certification record | Issue-time | Block |
| **FF-100** | Every P0 integration has a drill record within the current wave | Wave gate | Fail |

---

## 12. Sequencing

**Deliberately one wave ahead of first consumption**, because `AP-03` found eight of twelve `AP`
files registered *after* their consumers — six of them needed at W1 — and called it *"the sixth
consecutive category with the same defect."*

| # | Deliverable | Wave | First consumed |
|---|---|:--:|:--:|
| **T-01** | Pact broker, L1/L2 wiring, `FF-95`/`FF-96` | **W1** | W1 |
| **T-02** | **`SANDBOX` specified and provisioned** | **W1** | **W3** (courier partners) |
| **T-03** | Payment-rail mock **with induced-hang capability** | **W1** | W3 |
| **T-04** | Webhook consumer mock; `IN-006`'s 16 negative cases | **W1** | W1 (CON-03) |
| **T-05** | CON-03 contract tests — 22 endpoints, 11 webhooks | **W1** | **W1** |
| **T-06** | Resilience harness RT-01…RT-15 | **W2** | W2 |
| **T-07** | Certification process and checklist | **W2** | W3 |
| **T-08** | First fallback drills — the 5 W1/W2 P0 integrations | **W2** | W2 gate |
| **T-09** | Reverse certification against the three payment rails | **W2** | **W3** (`G3-03`) |
| **T-10** | Courier certification and fixtures | **W2** | W3 |
| **T-11** | Full drill programme, all **13** P0 | **W3** | W3 gate |

> **T-02 at W1 is the item most likely to slip**, because `TS-001` `O-03` records that **none of the
> six existing environments is provisioned either**. `SANDBOX` is not an increment on an existing
> estate; it is part of building one.

---

## 13. Decisions Recorded

| # | Decision | Options | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `IN-008-D-01` | Contract testing | Provider-published mocks · **consumer-driven pacts** · none | **Consumer-driven** | Only pacts answer "who breaks if I change this?", and that join is exactly what nobody ran across 100 paths and 69 events | `FF-95`, `FF-96`; the broker supersedes the `§12` tables |
| `IN-008-D-02` | `SANDBOX` | Reuse `UAT` · reuse `TRAIN` · **a seventh environment** | **Seventh** | Its data-state requirements match none of the six, and a partner in UAT changes what super-users are signing against | `TS-001` §4.7 amended (`AP-12`) |
| `IN-008-D-03` | Sandbox data | `NFR-071` masking · **synthetic only** | **Synthetic only** | Masked data is re-identifiable, and the access population is thousands of external developers | `SB-01`; `FF-98` |
| `IN-008-D-04` | External doubles | Hand-written stubs · **recorded fixtures, re-captured each wave** | **Recorded** | A hand-written fixture encodes what we believe the counterparty returns; the ACL exists to absorb the difference | `FX-01`…`FX-05` |
| `IN-008-D-05` | Seller certification | Full · none · **automated lightweight variant** | **Lightweight, automated** | A process that cannot scale to 2,000 sellers will be waived in practice, and a waived gate is worse than a designed-for-scale one | §8.5 |
| `IN-008-D-06` | Disclosure at certification | Advisory · **blocking regardless of technical readiness** | **Blocking** | `AP-08` says the register only works if the promotion gate holds | `CG-02` |
| `IN-008-D-07` | Fallback drills | Desk-check · **timed, at volume, by the people who would run it** | **Timed and realistic** | `FB-04`'s 15-minute rule is unmeasurable from a desk check | `DR-02`…`DR-06`; a failed drill **blocks the gate** |
| `IN-008-D-08` | Payment mock | Return canned responses · **must be able to hang for 30+ s** | **Must hang** | `unknown` is reachable only by timeout; a suite that cannot induce one cannot test the money path's most important state | §5.3 |

---

## 14. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| Q-01 | **Is `SANDBOX` funded and provisioned at W1?** None of the other six environments exists either (`TS-001` `O-03`) | Platform Engineering + CTO | **W1** | W3 courier and partner onboarding |
| Q-02 | Does the QA Lead accept the `TS-001` §4.7 amendment (`AP-12`, `AP-010` `O-03`)? | QA Lead | **W1** | §6.5 |
| Q-03 | Which **pact broker**, and who operates it? The estate has no toolchain (`IN-002` Q-04) | Platform Engineering | **W1** | `FF-95`, `FF-96` |
| Q-04 | Is the **~800-pair** contract-test suite resourced? It is in no plan | Programme Director | **W1** | Every module and portal build |
| Q-05 | Who runs the **fallback drill programme** — QA, Ops, or the integration owner? | QA Lead + Head of Service | **W2** | §9, `FF-100` |
| Q-06 | Do the payment rails' sandboxes support **induced timeout**, or must the mock substitute at L5? | Integration Architect | **W2** | RT-01, `G3-03` |
| Q-07 | Does the CON-03 portal platform's team accept **CT-01** — publishing pacts as a consumer? | Portal platform owner | **W1** | T-05 |

---

## 15. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | Test layers are defined with an **assignment rule**, not merely listed | §3.1, §3.2 |
| AC-02 | Contract testing is **consumer-driven**, with the reason stated | §4.2, `IN-008-D-01` |
| AC-03 | The pair count is **measured**, not estimated loosely | §4.3 — ~800 |
| AC-04 | `CT-07` would have caught the estate's actual defect | §4.4 |
| AC-05 | **`SANDBOX` is specified**, closing `AP-12` | §6.4 |
| AC-06 | Its data rule is stricter than `NFR-071`, **and why is stated** | §6.3, `SB-01` |
| AC-07 | Certification is a **blocking gate** with enumerated criteria and evidence | §8.3, §8.4 |
| AC-08 | `AP-08`'s promotion gate is made to hold | `CG-02` |
| AC-09 | Certification **scales to 2,000 sellers** | §8.5 |
| AC-10 | "Tested fallback" is defined as evidence, and the **current position (0 of 13) is stated** | §9.1, §9.2 |
| AC-11 | Resilience cases cover every failure mode `IN-001`…`IN-007` designed for | §10.1 — 15 cases; ~140 total |
| AC-12 | Delivery is sequenced **one wave ahead** of consumption, avoiding `AP-03` | §12 |

**Definition of done.** Complete when every criterion is met, `SANDBOX` is provisioned (Q-01),
`TS-001` §4.7 is amended (Q-02), the pact broker is operating with `FF-95`/`FF-96`, the twelve P0
fallback drills have run at least once, and `PGD-000`'s `IN-008` row carries a fresh enumeration
timestamp. **`AP-12` closes when `TS-001` §4.7 is amended — a Category 13 change this document cannot
make.**

---

## 16. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | **`IN-002`** | 1,187 operations; `FF-57` |
| Upstream | **`IN-003`** | 988 events; the registry is the event-test oracle |
| Upstream | **`IN-004`** | Each ICD §12 failure matrix is a test charter |
| Upstream | **`IN-005`** | `FF-76` — certification before a production credential |
| Upstream | **`IN-006`** §9 | Sixteen negative cases |
| Upstream | **`IN-007`** §13 | Ten money-path gates |
| Upstream | `TS-001` §4.7 | **Amended by §6.5** |
| Downstream | `QA-001`, `QA-003`, `QA-005` | The integration slice of the programme test strategy |
| Downstream | `PE-*` | `SANDBOX` provisioning |
| Downstream | `GV-009` | §11's evidence table feeds wave-gate assessment |
| Downstream | `AP-010` | Sandbox onboarding content now has a sandbox to describe |
| Lateral | `../../project_content/13_Test_and_Acceptance_Content/TS-001_*.md` §4.7 | The six-environment inventory this corrects |
| Lateral | `../../project_content/15_Integration_and_Developer_Content/AP-004_*.md` §4.11–§4.12, `AP-010` | Webhook testing and sandbox content |

---

## 17. References

**Within this repository**
[`../PGD-000_Master_Register_of_Project_Guiding_Documents.md`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md) ·
[`./_CATEGORY_OVERVIEW.md`](./_CATEGORY_OVERVIEW.md) ·
[`./IN-001_Integration_Architecture_Specification.md`](./IN-001_Integration_Architecture_Specification.md) ·
[`./IN-002_API_Specification_OpenAPI_Contracts.md`](./IN-002_API_Specification_OpenAPI_Contracts.md) ·
[`./IN-003_Domain_Event_Catalogue_and_Schema_Registry.md`](./IN-003_Domain_Event_Catalogue_and_Schema_Registry.md) ·
[`./IN-004_Interface_Control_Documents.md`](./IN-004_Interface_Control_Documents.md) ·
[`./IN-005_API_Governance_Versioning_and_Deprecation_Standard.md`](./IN-005_API_Governance_Versioning_and_Deprecation_Standard.md) ·
[`./IN-006_Webhook_Callback_and_Partner_Push_Specification.md`](./IN-006_Webhook_Callback_and_Partner_Push_Specification.md) ·
[`./IN-007_Payment_and_Financial_Gateway_Integration_Design.md`](./IN-007_Payment_and_Financial_Gateway_Integration_Design.md)

**Workspace**
`../../project_content/13_Test_and_Acceptance_Content/TS-001_*.md` §4.7 ·
`../../project_content/15_Integration_and_Developer_Content/AP-004_*.md`, `AP-010_*.md` ·
`../../project_content/_AUDIT/AUDIT-016_*.md` `AP-03`, `AP-08`, `AP-12` ·
`../../1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M28_*.md` §12.5, §17

**External sources**

| Source | Verified |
|---|---|
| ISO/IEC/IEEE 29119-2:2021 — test processes | 2026-08-18 |
| ISO/IEC/IEEE 29119-3:2021 — test documentation | 2026-08-18 |
| Consumer-driven contract testing (Pact) — broker, provider verification, participant versioning | 2026-08-18 |
| Cohn, *Succeeding with Agile* — the test pyramid | 2026-08-18 |
| Principles of Chaos Engineering | 2026-08-18 |

---

## 18. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Integration Architecture with QA | Initial issue. Specifies six test layers with an assignment rule, and **consumer-driven contract testing across ~800 measured provider–consumer pairs** — whose `CT-07` would have caught all 100 unmatched portal paths and 69 unpublished events at authoring time. **Specifies the `SANDBOX` environment `AP-12` identified as a seventh**, with a **synthetic-only data rule stricter than `NFR-071`** and the reason stated. Makes partner certification a blocking gate whose `CERT-08`/`CERT-09` hold regardless of technical readiness (`AP-08`), with a **lightweight automated variant that scales to 2,000 sellers**. Defines "tested fallback" as timed, realistic, drilled evidence and records the current position: **0 of 13** | *Pending — Design Authority not constituted (`PGD-A1-09`)* |

---

*`IN-008` · Category 04 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
