---
id: TS-001
title: Test Strategy and Content Traceability Standard
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-19
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: QA Lead
author: QA Lead with Programme Content Lead
reviewers: [CTO, Solution Architect, Programme Manager, Quality Manager, Security Lead, Localisation Lead, Business Owners Forum]
approver: CTO with Quality Manager
content_class: E
purpose: >
  The rules that make the word "tested" mean something on this programme — the test levels and who
  owns each, the requirement-to-script traceability model, script identifiers, entry and exit
  criteria, evidence and retention, and the mapping of the seventeen other Category 13 files onto
  the nine wave gates. Without it the programme holds 2,900-odd requirements, seventeen test packs
  and no way to state what proportion of the system has been proven, so "tested" is an assertion at
  every gate and a Go decision is taken on confidence rather than coverage.
traces_to: [06-04, 05-06, 05-06 §11, 05-06 §12, 05-01, 05-04, 05-05, 06-01, 06-02, 06-02 §4, M23, M28, M29, M63, CG-006, CG-008, CG-012, TS-002, TS-003, TS-004, TS-005, TS-006, TS-007, TS-008, TS-009, TS-010, TS-011, TS-012, TS-013, TS-014, TS-015, TS-016, TS-017, TS-018, DM-013, RF-003]
priority: P1
wave: W1
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md §11 Testing Standards — the twelve test levels, their coverage standards and their tooling standards; §11 Critical Journeys (15); §12 AS-01…AS-15 architecture standards restated as testable rules
    verified: 2026-08-19
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md §4 Wave Gate Acceptance Criteria G1-01…G9-05 — the gates this category must evidence
    verified: 2026-08-19
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md §4 Team Model (1 QA Engineer FTE at W1 and W2; super-users 2–3 per module at 30% during UAT); §5 Delivery Method (definition of ready, wave gate); §6 Parallel Running
    verified: 2026-08-19
    class: P1
  - source: 1000fix_ERP_Module/FOLDER_STRUCTURE.md §62 and §236–237 — `06-03` and `06-04` are marked planned and are absent from `06_Delivery_and_Implementation/`, which holds only `06-01` and `06-02`; §386 directs a QA engineer to read `06-04`
    verified: 2026-08-19
    class: P1
supersedes: none
review_due: 2027-02-19
---

# Test Strategy and Content Traceability Standard

| Item | Value |
|---|---|
| Test level | **All** — this file governs the other seventeen |
| Role executing | `R02` CTO and QA Lead own it; every `Rnn` executes under it |
| Modules covered | All 67 |
| Portals covered | All 12 |
| Environment | Governed here; **provisioned by nobody** — open item `O-03` |
| Test data set | `TS-002` is the only permitted source (`TX-05`) |
| Wave | W1 — the standard precedes the first gate |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3).
> All six sections retained in order. §4 carries the substance and is subdivided; the
> subdivision is the addition and is justified by volume — twenty-four rules, twelve levels and
> nine gates do not fit one undifferentiated section.

---

## 1. Purpose

Every one of the 67 module specifications carries a §17 Acceptance Criteria block, a §15 KPI block and a §14 Reports & Analytics block. `06-02` §4
sets nine formal Go/No-Go gates with 70 named criteria (counted 2026-08-19: 12 · 10 · 9 · 10 · 7 · 6 · 6 · 5 · 5). `05-06` §11 sets twelve test levels with
coverage standards. **None of those three documents says how a criterion becomes a script, how a
script becomes evidence, or how evidence becomes a coverage figure a Steering Committee can
trust.**

That is this file. It exists because of a specific failure mode: at a wave gate, someone says
"it's tested", and the only available challenge is "how do you know?". Without a traceability
model the honest answer is *we tested what we thought of*. `06-02` §4 requires **all** criteria to
be met and records partial passes as conditional with a dated remediation plan — a discipline that
cannot operate on an unmeasured base.

**What stops working without this file.** Three things, concretely:

| Absent | Consequence |
|---|---|
| Traceability model | Coverage cannot be stated, so gate decisions are taken on demonstration. `06-02` G4-10 requires *every* v1.0 BRD requirement demonstrated as delivered or formally superseded — that is a traceability query, and there is nothing to query |
| Script identifier standard | Seventeen packs authored by QA, six business functions and Security produce seventeen incompatible numbering schemes; a defect cannot be traced back to a requirement |
| Level ownership map | Four of the twelve `05-06` §11 levels are engineering-owned and have no Category 13 file. Unstated, that reads as a coverage gap rather than a deliberate boundary |

---

## 2. Scope

**In scope.** Test levels and their owners; the requirement-to-script traceability model; script
identifier format; entry and exit criteria; the evidence standard and its retention; the bilingual
and accessibility test obligations that apply across every pack; the mapping of the seventeen
packs onto gates `G1`–`G9`; coverage measurement; and the boundary against the three neighbouring
taxonomies (`M23` non-conformance, `M66` incident, `TS-018` defect).

**Out of scope — and this boundary matters more than usual.**

| Out of scope | Owned by | Note |
|---|---|---|
| Test tooling, automation framework, CI pipeline configuration | `06-04_Testing_and_Quality_Strategy.md` | **The file does not exist.** `FOLDER_STRUCTURE.md` marks it planned and its §386 reading path sends a QA engineer to it. Open item `O-01` |
| Environment topology, provisioning, refresh and masking mechanics | `06-04` (planned) with `M30` platform administration | This file states the *requirement* for six environments; it cannot provision them. Open item `O-03` |
| Unit, integration, contract and event testing | Engineering, in CI | Governed by `05-06` §11 and `AS-01`…`AS-15`; **no Category 13 file, deliberately** — §4.1 |
| Non-conformance and CAPA workflow | `M23` | A defect is not a non-conformance; §4.10 |
| IT incident management | `M66` | A production incident is not a defect; §4.10 |
| Migration reconciliation content | `DM-013` | Reciprocal: `DM-013` traces to `TS-018`; this file does not restate it (`CP-01`) |
| Linguistic quality sign-off | `BN-018` | `TS-016` verifies *rendering and assistive technology*; `BN-018` signs off *wording* |

---

## 3. Audience

| Reader | Uses it for |
|---|---|
| **QA Lead** (accountable, `CG-002` §6) | The operating standard for all seventeen packs |
| **Test analysts** | Script authoring: identifiers, expected-result discipline, evidence |
| **Business super-users** (2–3 per module, `06-01` §4) | Understanding what signing a UAT script commits them to |
| **CTO and Programme Manager** | The basis of every gate coverage statement |
| **Solution Architect and engineers** | Where CI-level testing ends and Category 13 begins |
| **Quality Manager** | ISO 9001 evidence chain (`NFR-024`) and the `M23` boundary |
| **Steering Committee** | Reading a coverage figure and knowing what it is a percentage *of* |

---

## 4. Content

### 4.1 The twelve test levels and who owns each

**These twelve levels are not invented here.** They are `05-06` §11 verbatim, mapped to their
owning artefact. Inventing a thirteenth taxonomy over an existing one is the drift `CP-01` exists
to prevent.

| # | Level (`05-06` §11) | Coverage standard | Owning artefact | Category 13 file |
|---:|---|---|---|---|
| 1 | **Unit** | ≥ 80% custom code; **100% of financial and tax calculations** | Engineering, every commit | **None — engineering-owned** |
| 2 | **Integration** | All module-to-module contracts; all external integrations against sandboxes | Engineering CI | **None** at contract level; business-visible chains in `TS-003`–`TS-005` |
| 3 | **Contract** | Every published API validated against its OpenAPI specification (`AS-07`) | Engineering CI | **None** — `AP` category (unwritten) carries the reference content |
| 4 | **Event** | Every producer/consumer pair for schema compatibility and idempotency (`AS-08`, `DI-05`) | Engineering CI | **None** |
| 5 | **SIT** *(see note)* | Category-boundary business chains | QA | **`TS-003`, `TS-004`, `TS-005`** |
| 6 | **End-to-end** | Every critical business journey, automated, run nightly | QA + Programme | **`TS-012`** |
| 7 | **UAT** | Every `P0` and `P1` requirement, executed by named business super-users | Business Owners + QA | **`TS-006`…`TS-011`** |
| 8 | **Performance** | Every NFR performance target, **at 1.5× expected peak**, before each wave gate | QA + Platform | **`TS-014`** |
| 9 | **Security** | SAST, DAST, dependency scanning every build; annual penetration test | Security + QA | **`TS-017`** (access, scope, consent, residency, audit-log completeness) |
| 10 | **Accessibility** | WCAG 2.1 AA automated scan **plus manual audit per portal**, before each portal release | QA + Content Design | **`TS-016`** |
| 11 | **Localisation** | Translation completeness, Bengali rendering, formatting, layout under text expansion, before each wave gate | **Split — no single owner** | `TS-002` (data), `TS-016` (assistive technology), `BN-018` (wording) — **`O-05`** |
| 12 | **Offline** | 24-hour offline operation with a scripted conflict scenario set, before each mobile release | QA + Mobile | **`TS-015`** |
| 13 | **Data migration** | Reconciliation and control totals on every load, before every cutover | Data Migration | **`DM-013`**; sign-off forms in `TS-018` |

**Note on SIT.** `05-06` §11 has no SIT row, yet the register allocates three files to it. The
gap is real and the resolution is stated here so it is not re-litigated: **CI "Integration"
proves that a contract holds; SIT proves that a business chain crossing a category boundary
produces the right business outcome.** A contract test confirms `M15` accepted the stock movement
`M01` sent. An SIT scenario confirms the ledger in `M19` moved by the right amount as a result.
The first is a schema question; the second is a business question, and only the second can be
signed by an owner. `TS-003` §2 carries the full definition; `TS-004` and `TS-005` reference it.

**Four levels have no Category 13 file, and that is deliberate.** Unit, Integration, Contract and
Event testing produce no content a business user reads or signs. They are governed by `05-06` §11
and `AS-01`…`AS-15`, verified in CI, and reported into gate criteria as tool output. Recording the
boundary here prevents a future auditor reading four blank rows as a coverage failure.

### 4.2 Rules

| # | Rule | Consequence if broken |
|---|---|---|
| **TX-01** | A requirement with no script resolving to it is **untested**. "Tested" is a claim only when a script identifier resolves to a requirement identifier | Coverage becomes opinion |
| **TX-02** | Every script traces to at least one `FR-<MOD>-nnn` **or** a module §17 acceptance criterion, and names the business rule (`BRU-*`) it exercises where one applies | Orphan scripts; unowned failures |
| **TX-03** | Traceability is **bidirectional**: forward requirement → script → run → evidence; backward defect → script → requirement → owning module and business owner | A defect cannot be routed or its blast radius assessed |
| **TX-04** | A script is written in the language of the person who executes it. UAT scripts use business language; SIT scripts may use system language | `TS-006`'s own register justification: scripts written by testers are signed without being read |
| **TX-05** | **No script uses production data.** Test data comes from `TS-002` | `NFR-071`, `NFR-086c`, `BRU-SEC-08`; and under the Personal Data Protection Act 2026 a non-production copy of personal data is processing |
| **TX-06** | Every negative case is a **script**, not a note. A hard rule (`05-05` class `H`) is proven by attempting to breach it and being blocked | An unbreached hard rule is an untested hard rule |
| **TX-07** | A hard rule is not verified by a UI test alone. `BR-STD-01` states that a rule bypassed by an API call is not a rule, so **every class `H` rule carries an API-level negative script** | The most damaging class of defect ships |
| **TX-08** | Expected results are written **before** execution. A script whose expected-result cell is completed after the run is void | Confirmation bias recorded as evidence |
| **TX-09** | Evidence is attached at the step that produces it, not assembled afterwards | Unverifiable pass records |
| **TX-10** | On a bilingual surface a pass requires **both languages**. English-only execution is a partial pass, recorded as such | `NFR-016`, `PS-03`; `KPI-092` is 100%, not 100% of English |
| **TX-11** | Pass/fail is binary. "Pass with comment" does not exist; a comment that qualifies a pass is a defect raised under `TS-018` | Deferred defects invisible at the gate |
| **TX-12** | Exit criteria are **numeric and agreed before the level starts** | Exit negotiated under schedule pressure |
| **TX-13** | Every level has entry criteria. A level does not start on a build that fails the previous level's exit | Defect masking; wasted business time |
| **TX-14** | **UAT is executed by the business, not demonstrated to it.** A script executed by a tester with a business user watching is a demonstration and is recorded as such | `06-02` G1-11 signed without being exercised |
| **TX-15** | Every script version is pinned to the release it was executed against (`CG-006` §5) | Evidence attributed to code that no longer exists |
| **TX-16** | A deferred defect is a **recorded decision** with a named owner, a severity, a justification and a date (`TS-018`) | Gate decisions taken against an unknown open-defect profile |
| **TX-17** | Regression scope is derived from change impact, never from habit (`TS-013`) | The suite grows until it is skipped |
| **TX-18** | Non-functional targets are tested **at 1.5× expected peak** (`05-06` §11), never at expected peak | A target met at peak fails at peak plus a promotion |
| **TX-19** | Field conditions are tested **in the field** (`TS-015`) | `NFR-036`/`-037`/`-047`/`-082` pass in a lab and fail in Gazipur |
| **TX-20** | Statutory output is verified by the function that signs it, not by QA (`TS-009`) | An unlawful invoice with a QA pass against it |
| **TX-21** | Accessibility and localisation conformance require **test evidence**. A conformance claim with no script is a claim, not a fact | `PS-04` is contractual |
| **TX-22** | Every script names its executor as an `Rnn` from `05-04`, not as a job title | Scripts unassignable; access negative tests unverifiable |
| **TX-23** | Test content is content. `CG-008` Definition of Done applies to every file in this category, including its `TS-` block | Unreviewable packs |
| **TX-24** | Coverage figures are **counted from the traceability matrix**, never estimated (`CP-11`, `RG-06`) | The failure mode gate `F7` exists to stop |

### 4.3 Script identifier standard

```
<LEVEL>-<SCOPE>-<nnn>[<variant>]
```

| Element | Values |
|---|---|
| `LEVEL` | `SIT` · `UAT` · `E2E` · `REG` · `SMK` · `PERF` · `OFF` · `ACC` · `SEC` |
| `SCOPE` | SIT → module category letter `A`…`K` · UAT → the executing role `R01`…`R38` · REG → module `Mnn` · SMK → portal `Pnn` · PERF → the target `NFR-nnn` · ACC → portal `Pnn` · E2E, OFF, SEC → none |
| `nnn` | Sequence within the scope, permanent, never reused (`CP-02` applied to scripts) |
| variant | Lower-case suffix for a delivery-mode or channel variant of the same scenario: `E2E-02a` |

| Example | Reads as |
|---|---|
| `SIT-A-007` | Seventh SIT scenario in module category A |
| `UAT-R08-014` | Fourteenth UAT script executed by a Service Centre Agent |
| `E2E-04` | Fourth end-to-end business scenario |
| `PERF-NFR-037-02` | Second performance scenario against the 30-second sync target |
| `SEC-041` | Forty-first security and privacy case |
| `SMK-P03-05` | Fifth post-deployment smoke check on the Admin Operations Portal |

**Why the UAT scope is a role and not a module.** A UAT script is assigned to a person, and
`05-04` is the only register that says which people exist and what they may do. Keying UAT scripts
to `Rnn` makes two audits mechanical: every role has scripts, and every script has an executor
who actually holds the permission it exercises. It also makes `TS-017`'s negative-test derivation
a set difference rather than a judgement.

### 4.4 The traceability model

```
FR-<MOD>-nnn ──┐
               ├──▶ Script (§4.3) ──▶ Run (release-pinned) ──▶ Evidence ──▶ Gate criterion
Mnn §17 AC ────┤                            │
BRU-* rule ────┘                            └──▶ Defect (TS-018) ──▶ back to requirement
```

Four registers are the authorities and none of them is restated here:

| Authority | Supplies |
|---|---|
| `05-01` + module §5 tables | Requirement identifiers |
| Module §17 | Acceptance criteria |
| `05-05` | Business rules and their class `H`/`A`/`S`/`C` |
| `05-06` | Non-functional targets, `AS-01`…`AS-15`, `DI-01`…`DI-08` |

**The matrix lives in `RF-003`**, not here. `RF-003` is the traceability register in Category 99
and is unwritten. Until it exists, each pack carries its own §1 Traceability table and the
programme has no consolidated coverage view. Open item `O-02`.

#### The denominator problem — stated, not solved

`TX-24` requires coverage to be counted. **Counted against what?** The repository currently holds
three live requirement totals:

| Figure | Source | Basis |
|---:|---|---|
| **2,930** | `README.md`; `02-02` §3; the v2.0 BRD | Counted by enumeration, 2026-08-13 |
| **~2,352** | `05-01` title | Superseded 30-module basis; audit finding `AF-06`, **open** |
| **2,985 + 358 = 3,343** | `03_Modules/_MODULE_SET_AUDIT_REPORT.md` §115, §522 | Recounted; explicitly states it supersedes the README's 2,930 |

The Master Index's own Category 13 preamble says "2,900+ requirements". **A coverage percentage
computed on 2,930 and one computed on 3,343 differ by 12 points at the same level of testing** —
enough to move a gate decision. Category 13 cannot resolve this; it is `AF-06` plus the
`_MODULE_SET_AUDIT_REPORT` restatement, and it belongs to Enterprise Architecture. Open item
`O-04`, and the first finding in the Category 13 audit.

**Until it is resolved, every coverage figure this category produces carries its denominator
inline** — "1,412 of 2,930 (counted 05-01 revision 2.1 basis)" — never a bare percentage.

### 4.5 Entry and exit criteria by level

| Level | Entry | Exit |
|---|---|---|
| **SIT** | Unit and integration green in CI; `TS-002` data loaded; environment at the declared release; all scenario preconditions establishable | 100% of `P0` scenarios pass; ≥ 95% of `P1`; zero open Critical or High defects; every class `H` rule in scope breached and blocked |
| **UAT** | SIT exit met; named super-users trained (`TR` pack delivered) and access provisioned; scripts reviewed by the business owner **before** execution | 100% of `P0` scripts pass; ≥ 98% of `P1`; zero open Critical; High defects either fixed or deferred by named decision (`TX-16`); business owner signature per pack |
| **E2E** | All modules in the journey deployed at the same release; `TS-002` data spanning the journey | All 18 scenarios (`TS-012`) pass at least once in the target wave; the nightly automated suite green for five consecutive nights |
| **Performance** | Production-shaped data volumes; monitoring instrumented; **1.5× peak profile agreed** | Every in-scope numeric target met at 1.5× peak; no target met by degrading another |
| **Security** | Roles and record rules configured for every delivered `Rnn`; audit logging on | Zero Critical or High findings (`06-02` G1-09); every denied portal cell negative-tested; row-level scope proven per `05-04` §4 tier |
| **Accessibility** | Portal feature-complete for the release; both languages populated | WCAG 2.1 AA automated scan clean of AA violations **and** manual audit passed per portal, in both languages |
| **Localisation** | Translation at 100% (`KPI-092`) | Rendering, formatting, expansion-layout and assistive-technology passes recorded; `BN-018` linguistic sign-off held |
| **Offline** | Release on target device class (Android 11, 3 GB RAM); field sites and SIMs available | 24 h offline with zero data loss; sync ≤ 30 s on 3G; conflict set resolved server-authoritatively; battery ≤ 12% per shift |
| **Regression** | Change-impact analysis complete | Full pack green; smoke checklist green on every affected portal post-deployment |
| **Migration** | Load complete | `DM-013` reconciliation signed |

### 4.6 Evidence and retention

| Rule | Detail |
|---|---|
| **EV-01** | Evidence is the artefact the system produced — a record identifier, a rendered document, a screen capture, a log excerpt, a monitoring chart, a device video. A tester's assertion is not evidence |
| **EV-02** | Every evidence item carries the release identifier, the environment, the executing `Rnn`, the UTC timestamp and the script identifier |
| **EV-03** | Evidence containing personal data is prohibited. `TS-002` data only, so a screen capture is safe by construction (`TX-05`) |
| **EV-04** | Statutory-output evidence (`TS-009`) is retained as a **compliance record**, not a test record, and is filed through `M24` |
| **EV-05** | Gate evidence packs are assembled per gate and referenced from the `TS-018` sign-off form, never re-created |

**Retention — proposed, requires ratification.** No retention period for test evidence exists in
any programme document. The proposal below is derived from adjacent obligations and is **not yet
approved**; `O-06`.

| Evidence class | Proposed retention | Derived from |
|---|---|---|
| Statutory output verification (`TS-009`, Mushak, payroll, BEFTN) | **7 years** | `NFR-030` monthly-backup 7-year tier; `NFR-088` statutory schedule |
| Security, privacy, residency (`TS-017`) | **5 years minimum** | `NFR-095` — processing records for a minimum of five years |
| Gate acceptance packs `G1`–`G9` | **Programme life + 3 years** | `NFR-024` ISO 9001 audit trail |
| All other test evidence | **3 years** | Programme convention; no external driver |

### 4.7 Environments — the requirement

`05-06` gives three environment constraints (`NFR-071` masked data only in non-production;
`OPS-02` configuration promoted, never hand-edited; `NFR-086c` no unmasked residency-classified
data in any region) but **no environment inventory exists anywhere in the repository.** Six are
required by the levels above:

| # | Environment | Purpose | Data | Refresh |
|---|---|---|---|---|
| 1 | `DEV` | Engineering | Synthetic subset | On demand |
| 2 | `CI` | Unit, integration, contract, event | Fixtures | Per commit |
| 3 | `SIT` | `TS-003`–`TS-005` | Full `TS-002` set | Per release |
| 4 | `UAT` | `TS-006`–`TS-012`, `TS-016` | Full `TS-002` set, **frozen during a UAT cycle** | Per wave |
| 5 | `PERF` | `TS-014` | Production-shaped volumes (`NFR-053`, `-054`) | Per wave gate |
| 6 | `TRAIN` | `TR` practical exercises, `TR-003` `DS-14` screenshots | Full `TS-002` set, resettable per cohort | Per cohort |

**`SIT` and `UAT` cannot be the same environment.** A UAT cycle needs frozen data and a stable
release; SIT needs a moving one. Sharing them means either UAT executes against changing data —
voiding `TX-08` — or SIT stops for the duration of UAT. **`TRAIN` cannot be `UAT` either**, because
`TR-003` `DS-14` requires screenshots from a sandbox and trainees destroy data by design.

This file can state the requirement. It cannot provision it: that is `06-04` and `M30`. `O-03`.

### 4.8 Pack-to-gate mapping

`06-02` §4 sets nine gates. This is which pack evidences which — the table a Programme Manager
needs six weeks before a gate.

| Gate | Month | Wave | Evidencing packs | Named gate criteria they answer |
|---|---:|:--:|---|---|
| **G1 Foundation** | 4 | W1 | `TS-006`, `TS-009`, `TS-013`, `TS-014`, `TS-016`, `TS-017`, `TS-018`, `DM-013` | G1-03 timed intake · G1-04 SLA clocks · G1-05 reconciliation · G1-06 SSO and roles · G1-07 audit trail · G1-08 translation coverage · G1-09 zero Critical/High security · G1-10 performance · G1-11 UAT signature |
| **G2 Field Operations** | 8 | W2 | `TS-003`, `TS-006`, `TS-008`, `TS-012`, `TS-015`, `TS-013` | G2-02 24 h offline zero loss · G2-03 sync ≤ 30 s on 3G · G2-04 travel-time reduction · G2-06 inventory accuracy by count · G2-07 van-stock variance |
| **G3 Money & Movement** | 13 | W3 | `TS-004`, `TS-008`, `TS-009`, `TS-012`, `TS-017` | G3-01 auto-invoicing · G3-02 auto-match ≥ 90% · G3-04 **Mushak accepted, zero NBR exceptions** · G3-07 unbroken custody · G3-08 trial-balance reconciliation |
| **G4 Agreements & Contact** | 18 | W4 | `TS-005`, `TS-007`, `TS-011`, `TS-012` | G4-01 claim timings · G4-02 first-submission approval · G4-08 consolidated invoicing · **G4-10 every v1.0 requirement demonstrated or superseded** |
| **G5 People, Quality & MSP** | 22 | W5 | `TS-010`, `TS-012`, `TS-013`, `TS-016` | G5-01 **first payroll, zero errors** · G5-02 BEFTN accepted · G5-03 zero uncertified technicians assignable · G5-07 attendance completeness |
| **G6 New Asset Businesses** | 26 | W6 | `TS-005`, `TS-012`, `TS-015`, `TS-017` | G6-02 zero units released without a destruction certificate · G6-03 zero custody exceptions · G6-06 native apps adopted |
| **G7 Marketplace** | 30 | W7 | `TS-007`, `TS-011`, `TS-012`, `TS-017` | G7-02 payout accuracy 100% · G7-03 marketplace parity of standards · G7-06 pricing guard rails with a complete decision audit |
| **G8 Intelligence & Sustainability** | 34 | W8 | `TS-005`, `TS-012`, `TS-014` | G8-01 zero manual packs · G8-03 automation ≥ 85% · G8-04 zero uncertified disposals |
| **G9 Expansion Readiness** | 36 | W9 | `TS-014`, `TS-013`, `TS-017` | G9-01 second-country entity by configuration · **G9-03 full-scale load test at 1.5× projected peak** |

**Read the W1 column against the register.** `TS-014`, `TS-016`, `TS-017` and `TS-013` are all
registered at **W2** and all four are required at **`G1`, Month 4, in W1**. That is not an
interpretation; `G1-09`, `G1-10` and `G1-08` name them. Open item `O-07` and the second finding in
the Category 13 audit.

### 4.9 Coverage measurement

| Measure | Definition | Reported |
|---|---|---|
| **Requirement coverage** | Distinct requirement identifiers with ≥ 1 script ÷ requirements in the wave's scope | Per wave, with the denominator inline (§4.4) |
| **`P0`/`P1` coverage** | Same, restricted by priority | Weekly during a test cycle |
| **Hard-rule coverage** | Class `H` rules in `05-05` with a passing negative script ÷ class `H` rules in scope | Per wave. Target 100%, no tolerance |
| **Role coverage** | `Rnn` with ≥ 1 executed UAT script ÷ roles delivered in the wave | Per wave. `05-04` §10 criterion 6 makes this a role-release condition |
| **Portal-cell coverage** | Denied `role × portal` cells with a passing negative test ÷ 379 denied cells | `TS-017`; per wave |
| **Journey coverage** | `TS-012` scenarios passing ÷ 18 | Per wave |
| **Bilingual pass rate** | Scripts passed in both languages ÷ scripts on bilingual surfaces | Per wave (`TX-10`) |
| **Execution progress** | Executed ÷ planned, and passed ÷ executed | Daily during a cycle |

**Not measured, deliberately:** script count. A pack with 400 thin scripts is not better tested
than one with 120 that breach every hard rule. Counting scripts creates the incentive to write
them.

### 4.10 The three-way taxonomy boundary

`CG-004` reserves the term **defect** for a software or product defect and binds it to `M23` and
`TS-018`. Three neighbouring records exist and they are routinely confused:

| Record | Owner | Is | Is not |
|---|---|---|---|
| **Defect** | `TS-018` | The system does not do what a requirement says | A process failure, or a live outage |
| **Non-conformance** | `M23` (`fix.nonconformance`) | A process or output departed from a specified requirement — ISO clause bound, needs root cause and CAPA | A code bug |
| **Incident** | `M66` | A live service is degraded or unavailable for users now | A test-cycle finding |

**Where they meet.** A defect found in production becomes an incident *and* stays a defect. A
defect whose root cause is a process failure (an untested configuration change) raises a
non-conformance under `BRU-QMS-02` *and* stays a defect. **The records are linked, never merged**:
`M23` severity is clause-driven, `M66` severity is impact-driven, `TS-018` severity is
requirement-driven, and forcing one scale across three purposes produces a scale that fits none.
`TS-018` §4 carries the mapping table.

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `05-01`, module §5 tables | The requirement identifiers every script must resolve to |
| Module §17 blocks | Acceptance criteria — the other traceable target |
| `05-05` | Business rules and their `H`/`A`/`S`/`C` class, which drives `TX-06`/`TX-07` |
| `05-06` §11, §12 | The twelve levels, the 1.5× rule, `AS-01`…`AS-15`, `DI-01`…`DI-08` |
| `05-04` | Roles for `TX-22`, and the whole `TS-017` derivation |
| `06-02` §4 | The 70 gate criteria this category evidences — counted 2026-08-19 |
| `06-01` §4, §5, §6 | QA capacity, super-user commitment, parallel-run periods |
| **`TS-002`** | The only permitted data source (`TX-05`). `P0`/W1 |
| **`RF-003`** | The consolidated traceability matrix — **unwritten** |
| **`06-04`** | Tooling, environments, automation — **does not exist** |
| `CG-006`, `CG-008`, `CG-012` | Release pinning, Definition of Done, evidence rules |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | At every wave gate, before the gate paper is written |
| Trigger for out-of-cycle review | A change to `05-06` §11; a new test level; a gate criterion added or removed in `06-02`; resolution of the `O-04` denominator; publication of `06-04` |
| Owner | QA Lead (`CG-002` §6 names QA Lead accountable for Category 13) |
| Change control | Rule changes (`TX-*`) require CTO and Quality Manager approval, as this file's approver block records |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **`06-04_Testing_and_Quality_Strategy.md` does not exist.** `FOLDER_STRUCTURE.md` marks it planned and its §386 reading path sends a QA engineer to it. Category 13 is the *content* half; tooling, automation and CI remain unowned | CTO | **W1 — before the first script is executed** |
| **O-02** | **`RF-003` traceability register is unwritten** (Category 99 unstarted). Without it, seventeen packs carry seventeen local §1 tables and no consolidated coverage view exists — so `TX-24` cannot be discharged and `G4-10` cannot be answered | Programme Content Lead with QA Lead | **W1** |
| **O-03** | **Six environments are required and none is specified or provisioned.** `SIT`, `UAT`, `PERF` and `TRAIN` have conflicting data-state needs (§4.7). `TR-001` `O-06` and `TR-003` `O-01` already record the `TRAIN` half from the training side | CTO with `M30` owner | **W1 — blocking SIT entry** |
| **O-04** | **The requirement denominator is contested: 2,930 vs ~2,352 vs 3,343** (§4.4). Coverage cannot be reported as a percentage until one governs. This is audit finding `AF-06` plus the `_MODULE_SET_AUDIT_REPORT` restatement | Enterprise Architecture with CTO | **W1 — before the first coverage figure is quoted** |
| **O-05** | **Level 11 Localisation has no owning file.** It is split across `TS-002`, `TS-016` and `BN-018`, and *truncation and layout under text expansion* — the `05-06` §11 requirement — is owned by nobody. `VB-007` states the 20–40% Bengali expansion allowance but does not test it | Localisation Lead with QA Lead | **W2** |
| **O-06** | **Test evidence retention is unratified** (§4.6). Statutory verification evidence is a compliance record under `NFR-088`/`NFR-095`; treating it as a test artefact risks destroying it inside its statutory window | Quality Manager with Legal Counsel | **W1** |
| **O-07** | **Four packs are registered at W2 and required at `G1` in W1** — `TS-013`, `TS-014`, `TS-016`, `TS-017` (§4.8). `G1-08`, `G1-09` and `G1-10` name their outputs | Programme Content Lead with QA Lead | **W1 — register correction** |
| **O-08** | **QA capacity is 1 FTE at W1 and W2** (`06-01` §4) against eighteen packs, twelve portals, 2,930-odd requirements and six gate-evidencing obligations at `G1` and `G2`. **The arithmetic does not close**; `06-01` §4 already names business availability as the binding constraint, and QA capacity is the second | Programme Manager with CTO | **W1** |
| **O-09** | **No super-user register exists.** `06-01` §4 commits 2–3 super-users per module at 30% during UAT — 134–201 named people across 67 modules — and `G1-11` requires UAT signed by *named* super-users. `TS-006`–`TS-011` cannot name their executors | Business Owners Forum with Programme Manager | **W1** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; the §4 subdivision is the only addition and is justified
- [x] **The twelve test levels adopted from `05-06` §11 rather than re-invented (`CP-01`)**
- [x] The four engineering-owned levels declared as deliberate boundaries, not gaps
- [x] SIT's absence from `05-06` §11 resolved and the contract-versus-outcome distinction stated once
- [x] Twenty-four rules stated with the consequence of breaking each
- [x] Script identifier standard defined, with the `Rnn` keying rationale recorded
- [x] **The denominator problem stated rather than papered over; every coverage figure must carry its basis inline**
- [x] Entry and exit criteria numeric per level (`TX-12`)
- [x] Six environments specified with their conflicting data-state needs made explicit
- [x] All nine gates mapped to evidencing packs against named `06-02` criteria
- [x] The `M23` / `M66` / `TS-018` boundary stated before `TS-018` is written
- [x] All internal links resolve
- [x] Nine open items recorded with owners and blocking consequences
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` `06-04` absent — outstanding; this file cannot substitute for a delivery strategy**
- [ ] **`O-03` environments unprovisioned — outstanding; blocks SIT entry**
- [ ] **`O-04` requirement denominator contested — outstanding; blocks coverage reporting**
- [ ] Named approvers recorded — **pending CTO and Quality Manager**
- [ ] Bengali counterpart — n/a; internal governance, English-only per `CG-010` §3.2

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
