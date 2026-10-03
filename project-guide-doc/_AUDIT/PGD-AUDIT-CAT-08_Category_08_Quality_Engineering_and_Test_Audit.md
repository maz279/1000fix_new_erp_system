---
id: PGD-AUDIT-CAT-08
title: Category 08 — Quality Engineering & Test Audit
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: ISSUED
classification: CONFIDENTIAL — Internal Use Only
auditor: Quality Engineering (self-assessment — independence class I0, per GV-010)
scope: >
  The eleven QA documents of Category 08, their citations into the guiding, module and content
  estates, their internal identifier spaces, their arithmetic, their standards currency, and the
  PGD-000 register rows they produced.
mandate: Audit required on completion of a guiding category, per the convention established by
  PGD-AUDIT-002 and continued through PGD-AUDIT-CAT-07 and PGD-AUDIT-CAT-09.
extends: PGD-AUDIT-001 … PGD-AUDIT-008 · PGD-AUDIT-CAT-07 · PGD-AUDIT-CAT-09
enumeration_timestamp: 2026-08-18 22:20 (+06)
method: >
  Filesystem enumeration, identifier extraction and arithmetic re-derivation only. No figure in this
  report is projected, and none is taken from what a document says about itself — including what this
  category's own documents say about themselves. Every derivation was recomputed from its stated
  inputs rather than read from its stated output.
---

# Category 08 `QA` — Quality Engineering & Test Audit

### 11 documents · 7,776 lines · 422 tables · issued 2026-08-18
### 18 findings — 2 critical, 6 high, 6 medium, 4 low · 6 fixed, 12 open

---

## 1. Method and result

Six extraction passes were run against the eleven documents, and every arithmetic derivation in the
category was **recomputed from its inputs**.

| Pass | What was compared |
|---|---|
| **X1** | Every relative path cited, resolved against the filesystem |
| **X2** | Every markdown table's row cell-count against its header |
| **X3** | Every Category-08-local identifier — contiguity, duplication, zero-padding, and whether each has a definition |
| **X4** | **Every identifier cited from outside the category**, resolved against a 739-file, 23.7 MB corpus of the rest of the workspace |
| **X5** | **Every arithmetic derivation recomputed** — the capacity model, the volumetric model, the script counts, the gate-criteria totals |
| **X6** | Every standard cited, against its current published edition, verified 2026-08-18 |

**Eighteen findings — 2 critical, 6 high, 6 medium, 4 low.** Six were remediated during the audit;
twelve are open, and **ten of the twelve are owned outside this category**.

| Severity | Count | Fixed | Open |
|---|---:|---:|---:|
| **Critical** | **2** | 0 | **2** |
| High | 6 | 1 | 5 |
| Medium | 6 | 3 | 3 |
| Low | 4 | 2 | 2 |
| **Total** | **18** | **6** | **12** |

> **Four findings in this report are against the auditor's own authoring** — `QAA-A1` … `QAA-A4`.
> That is stated because the convention inherited from `AUDIT-014` and `PGD-AUDIT-CAT-07` requires
> it: **where the auditor's prior work caused a finding, the cause matters more than the fix.**
> `QAA-A2` is the most instructive of the four and is written up at length in §4.2, because the
> defect it represents — an asserted figure inside a derivation that was never recomputed — is
> precisely the defect this whole category exists to prevent elsewhere.

---

## 2. Checks that passed

| Check | Result |
|---|---|
| **A1** Document count | **11 of 11** registered `QA-001`…`QA-011`, all on disk ✅ |
| **A2** File name matches ID | 11 of 11 ✅ |
| **A3** ID contiguity `QA-001`…`QA-011` | No gaps, no duplicates ✅ |
| **A4** Documents on disk with no register row | Zero ✅ |
| **B1** Front matter completeness | **All 19 keys present in all 11**, against the 18 `TPL_Guiding_Document.md` requires plus `enumeration_timestamp` ✅ |
| **B2** `verified_on` present where a standard, statute or vendor version is cited | 11 of 11 ✅ (`PG-M4`) |
| **B3** `traces_to` and `depends_on` present | 11 of 11 ✅ |
| **C1** Section numbering contiguity | **11 of 11 contiguous**, no gaps, no repeats ✅ |
| **C2** Template section coverage — Purpose, Scope, Basis & Inputs, Decisions, Open Questions, Acceptance Criteria, Traceability, References, Revision History | **9 of 9 in all 11** ✅ |
| **X1** Relative links | **60 distinct paths, zero broken**, both `../` and `../../` ✅ |
| **X2** Table integrity | **422 tables; 2 malformed rows found and fixed** (`QAA-A3`); **0 remaining** ✅ |
| **X3** Local identifier spaces | **11 prefixes, 501 distinct identifiers, all contiguous, all defined.** One zero-padding inconsistency found and fixed (`QAA-A4`) ✅ |
| **X3b** Prefix collision sweep | **`MTS`, `LVP`, `TDS`, `TDM`, `TAF`, `PLT`, `STP`, `ATP`, `UAP`, `DMG`, `RTC` — all eleven returned 0 prior occurrences** across all five repositories before allocation ✅ |
| **X4** External identifier resolution | **414 distinct identifiers cited from outside the category; 409 resolve.** The five exceptions are literal scheme templates — `E2E-nn`, `OFF-nnn`, `SEC-SOD-nn`, `SIT-E-nnn`, `TC-nnnn` — not citations ✅ |
| **X5a** Gate-criteria total | `QA-002` §11.2's per-wave counts sum to **12+10+9+10+7+6+6+5+5 = 70**, against `06-02` §4's counted 70 ✅ |
| **X5b** Capacity model | `QA-001` §10.2 recomputed from `06-01` §4's FTE profile and §3's wave lengths: **1·4 + 1·4 + 2·5 + 2·5 + 2·4 + 2·4 + 2·4 + 2·4 + 1·2 = 62 QA FTE-months** ✅ |
| **X5c** Denial-cell arithmetic | `05-04` §2: 456 cells, 77 granted, **379 denied**. Matches `AUDIT-014` `X8`'s independent enumeration exactly ✅ |
| **X6** Standards currency | **9 of 9 verified against their current published editions.** Four corrections applied — §3 ✅ |
| **D1** Denominator consistency | **3,389 used in every coverage context across all eleven documents**; 2,930 and 3,343 appear **only** in explicitly-superseded contexts ✅ |
| **D2** No identifier collision with a concurrently-authored category | `PGD-AUDIT-CAT-08` is category-keyed; the numeric space `001`–`008` was fully claimed at authoring time ✅ |

### 2.1 Cross-document consistency

Every figure used in more than one document was checked for agreement.

| Figure | Value | Documents | Agree? |
|---|---|---:|:--:|
| Coverage denominator | **3,389** | 4 | ✅ |
| QA capacity | **62 FTE-months** | 5 | ✅ |
| Components | **331 across 79 units** | 5 | ✅ |
| Denied portal cells | **379** | 7 | ✅ |
| Portal matrix | **456 / 77 granted** | 4 | ✅ |
| Threats · abuse cases | **97 · 32** | 4 | ✅ |
| API operations · events | **1,187 · 988** | 4 | ✅ |
| Role accounts | **38** | 7 | ✅ |
| Gate criteria | **70** | 3 | ✅ |
| Distinct case identifiers | **620** | 4 | ✅ *(after `QAA-A1`)* |
| UAT scripts | **352** | 4 | ✅ *(after `QAA-A1`)* |
| Peak load at 1.5× | **~241 req/s** | 3 | ✅ *(after `QAA-A2`)* |

---

## 3. Standards currency — four corrections *(`PG-M4`)*

`_CATEGORY_OVERVIEW.md` v1.0 named four standards. **Three were cited at a superseded or undated
edition**, and a fourth in the same family was withdrawn.

| Cited as | **Current, verified 2026-08-18** | Consequence had it stood |
|---|---|---|
| *"ISO/IEC/IEEE 29119-1…5"*, undated | **29119-1:2022 · -2:2021 · -3:2021 · -4:2021 · -5:2024**. **29119-5:2016 is withdrawn** | A conformance claim against a withdrawn part |
| *"ISO/IEC 25010"*, undated | **ISO/IEC 25010:2023** — adds *Safety*, restructures the characteristics | A quality model missing a characteristic that applies to field technicians and hazardous stock |
| *"OWASP ASVS 4"* | **ASVS 5.0.0, 30 May 2025** — ~350 requirements in 17 chapters, up from 286 in 14 | ~64 requirements never verified. `SC-005` §2.1 had already made this correction; the overview had not |
| *"TMMi"*, undated | **TMMi 2.0 (2026)**. **Release 1.3 assessments end 1 August 2027** | A maturity baseline bought against a model retiring inside the programme's own timeline |

`WCAG 2.2 AA` was correctly cited, and is confirmed as W3C Recommendation 5 October 2023, updated
12 December 2024, adopted as **ISO/IEC 40500:2025** on 21 October 2025.

> **This is the fourth consecutive category to find superseded standards citations** — after `C-04`
> (DSA 2018 repealed twice), `H-01` (NIST SP 800-88 r1 withdrawn) and `M-01` (Odoo release date).
> **`RR-005` (Standards & Regulatory Currency Register) has now been recommended by five separate
> audits and remains unwritten.** It is ⛔ `P0` `Now` in `PGD-000`.

---

## 4. Findings against this category's own authoring

### 4.1 `QAA-A1` — the `TS-011` undercount

**Severity: MEDIUM · Status: FIXED · Owner: Quality Engineering**

**What was found.** `QA-001` §4.4's count of distinct case identifiers per pack recorded `TS-011` as
**33**. Re-extraction under `X5` returned **72**.

**Cause.** The first extraction used the pattern `(UAT|SIT|…)-[A-Z0-9]+-[0-9]+`, which matches
two-segment identifiers. **`TS-011` alone uses a three-segment form — `UAT-R38-P05-002`** — because
its scripts are scoped by role *and* portal. The pattern silently matched none of them and the
count was taken as complete.

**Cascade.** Two totals inherited it:

| Figure | Stated | **Actual** | Appeared in |
|---|---:|---:|---|
| Distinct case identifiers across the 15 script packs | 581 | **620** | `QA-001`, `QA-003`, `QA-011` |
| UAT scripts across the six UAT packs | 331 | **352** | `QA-002`, `QA-009` |

**Why it matters more than its size.** The corrected UAT figure — **352** — matches `AUDIT-014`
`TS-07`'s independently enumerated 352 exactly. **The error was detectable at authoring time by
comparing against a figure already in the estate, and it was not compared.** That is the same
failure mode as `PG-M10`'s: a total that looks plausible is not checked against an independent
count.

**Remediation applied.** All 26 occurrences corrected across five documents; per-pack figures in
`QA-009` §2.2 and §4.2 restated to the UAT-prefixed counts (80/60/58/46/36/72). Re-verified: the six
per-pack figures now sum to 352 ✓.

### 4.2 `QAA-A2` — the portal-traffic derivation was wrong by ~37×

**Severity: HIGH · Status: FIXED · Owner: Quality Engineering**

**What was found.** `QA-006` §4.3 derives a peak request rate from business volumes in eight steps.
Step 6 stated:

> *"Portal browse traffic: 250,000 customers/month, 30% self-service, 6 page views each, peak factor
> 3 → **~46 page views/s at peak**"*

**Recomputed from those exact inputs:**

```text
250,000 × 0.30 × 6  =    450,000 page views / month
                     ÷ 30 days      =  15,000 / day
                     ÷ 10 hours     =   1,500 / hour average
                     × 3 peak factor =  4,500 / hour peak
                                     =    1.25 / s
```

**1.25/s, not 46/s.** Steps 7 and 8 summed the components and inherited the error:

| Step | Stated | **Actual** |
|---|---:|---:|
| 7 — sum at expected peak | ~205 req/s | **~161 req/s** |
| 8 — × 1.5, *"the number every gate tests at"* | **~308 req/s** | **~241 req/s** |

**Why this is HIGH rather than MEDIUM.** Step 8 is the figure the `PERF` environment is sized
against and the figure `WP-4` — the gate profile for all nine gates — runs at. A 28% overstatement
of the gate load is a 28% overstatement of the most expensive environment in the estate.

**Why it happened, stated plainly.** The other seven steps were computed. **Step 6 was estimated and
written in the same table as if it had been computed**, and the table's own rule — `PLT-04`, *"every
load figure in this plan is derived, and its derivation is shown"* — was satisfied in form by
listing the inputs and not in substance by multiplying them. **A derivation whose steps are not
recomputed is an assertion with arithmetic decoration**, and this category's `PG-03` obligation
exists precisely to prevent that.

**Remediation applied.** Step 6 restated with the division chain shown explicitly; steps 7 and 8
recomputed; `WP-2`, `WP-3` and `WP-4` rates corrected; **§4.5's transaction mix rebuilt so that it
derives from the four components rather than asserting thirteen percentages**; `AC-03` restated.

**And it surfaced a larger finding.** Correcting the portal figure made `QAA-11b` visible — see
§5.2. **A wrong number concealed a wrong requirement.**

### 4.3 `QAA-A3` — two malformed table rows

**Severity: LOW · Status: FIXED · Owner: Quality Engineering**

**What was found.** Of **422 tables**, two rows carried 2 cells against a 3-cell header —
`QA-007` `STP-25` and `QA-008` `ATP-17`. Both were rule rows whose third column (the source
citation) was omitted when the rule text ran long.

**Why it is reported at all.** `AUDIT-014` `X7` ran the same check and found **zero** malformed rows
across 18 files; `PGD-AUDIT-001` `PGD-A1-02` records malformed rows as a defect class. A malformed
row renders as a short row and its missing cell is invisible rather than obviously absent.

**Remediation applied.** Both rows completed with their source citations. Re-verified: 422 tables,
**0 malformed rows**.

### 4.4 `QAA-A4` — one identifier written unpadded

**Severity: LOW · Status: FIXED · Owner: Quality Engineering**

**What was found.** `QA-005` §10.3 cited **`TAF-9`** where the rule is defined as **`TAF-09`** —
one rule with two identifiers, which is the defect class behind `H-03` (48 colliding CD identifiers)
in its mildest form.

**Remediation applied.** Corrected. Re-verified: **501 distinct local identifiers, zero
inconsistencies, all eleven series contiguous.**

---

## 5. Critical findings

### 5.1 `QAA-05` — nine of thirteen test levels are defined as running in a pipeline that has no design

**Severity: CRITICAL · Status: OPEN · Owner: CTO with Platform Engineering**

**What was found.** `QA-001` §4.2 defines thirteen test levels. **Nine of them — L1, L2, L3, L4, L6,
L8, L9, L10, L12 — are specified as automated, running in CI.** `QA-005` specifies the framework
that would run there and states eight requirements on the pipeline.

**`PE-004` CI/CD Pipeline Design does not exist.** Nor does `PE-002` Environment Strategy.
Enumerated at 22:20 (+06):

| Element | Required | **Provisioned** |
|---|---:|---:|
| Environments (`QA-001` §7.1) | **7** | **0** |
| CI/CD pipeline design | 1 | **0** |
| IaC standard — `PE-003` records **zero occurrences of "Terraform"** across the estate | 1 | **0** |
| Pact broker and schema registry (`IN-008` `CT-02`, `FF-95`) | 1 each | **0** |

**Why it is Critical.** `PGD-000` §0.3 defines a document as ⛔ *blocking* when *"a dependency
already rests on it."* Every one of the following rests on `PE-002` and `PE-004`:

| Dependent | Consequence today |
|---|---|
| `QA-001` §6.4's W1 automation targets | **Unachievable** |
| `QA-002` `LP-2`, `LP-3`, `LP-4` entry criteria | **Cannot be met** |
| `QA-004` §7's provisioning matrix | Specifies seven environments that do not exist |
| `QA-005` stages 0–7, ~11.5 person-months | Cannot start stage 2 without a broker in `CI` |
| `QA-006` `G1-10` at Month 4 | **Not evidenceable** — `PLT-19` |
| `QA-007` §5's authorisation suite | Blocked on `SIT` and the 38 accounts |
| `QA-011`'s entire measurement | No result set to measure |
| `AR-012`'s fitness functions | Same dependency, recorded independently |
| `GV-009` `EN-06` | A gate entry criterion that fails today |

**This is not a Category 08 finding that Category 08 can close.** It is recorded here because
**Category 08 is the first category whose deliverables are unusable without it** — `AR-012` recorded
the same dependency and could still be executed manually; a test strategy cannot.

**Remediation instruction.** Sequence `PE-002` and `PE-004` as **Wave 0**, ahead of the remaining
guiding categories. `QA-005` §11.1 already states the eight requirements `PE-004` must satisfy, so
the input exists. Recorded as `QA-001` `Q-03`, `QA-005` `Q-02`, `QA-006` `Q-01`.

### 5.2 `QAA-11b` — `NFR-004` has no volumetric basis and is ~3,000× above what the estate's own volumes support

**Severity: CRITICAL · Status: OPEN · Owner: Enterprise Architecture with the CCO**

**What was found.** `QA-006` §4.3's corrected derivation (§4.2 above) produces **1.25 customer-portal
page views per second at peak**, which at a 20-second think time is **~25 concurrent portal users**.

**`NFR-004`, a `P0` requirement, states: *"Concurrent customer portal users: 75,000+ (was 50,000)"*,
measured by load test.**

| Think time | Requests/s implied by 75,000 concurrent |
|---:|---:|
| 15 s | ~5,000 |
| **20 s** | **~3,750** |
| 30 s | ~2,500 |

**~3,750 req/s is roughly 3,000× the derived portal load, and roughly 23× the load of the entire
rest of the system combined** (161 req/s).

**Three readings are possible and the estate does not say which is intended:**

| # | Reading | Consequence |
|:--:|---|---|
| 1 | A **headroom target**, deliberately over-provisioned | Legitimate — but then it belongs with `NFR-009`/`NFR-010` **scalability**, not with performance, and `WP-4` should not be sized from it |
| 2 | The **registered customer base is far larger** than 250,000/month | Plausible — **but no registered-base figure exists anywhere in the estate**, so a `P0` requirement rests on an unstated number |
| 3 | It is an **error**, inherited from *"was 50,000"* without derivation | Also plausible — and `NFR-003` (*"800+, was 500"*) has the same shape |

**Why it is Critical.** Three consequences, each independently material:

1. **It sizes the most expensive environment in the estate.** `PERF` at 75,000 concurrent is a
   materially different machine from `PERF` at 241 req/s, and the cost difference is caused by a
   requirement with no stated basis.
2. **It is a `P0` gate criterion.** `G9-03` requires *"full-scale load test passed at 1.5× projected
   peak"*. 1.5 × 75,000 = 112,500 concurrent users, and nothing states what makes 75,000 the peak.
3. **`AUDIT-014` `TS-01` is the same defect class in a different space.** `TS-01` was Critical
   because a *coverage* figure had no agreed denominator. This is a *load* figure with no agreed
   derivation, and it is verified at every one of nine gates.

**The wider pattern.** `05-06` §1–§2 contains **six** targets annotated *"(was N)"* — `NFR-001`
3 s→2 s, `NFR-002` 500→400 ms, `NFR-003` 500→800, `NFR-004` 50,000→75,000, `NFR-005` 30→20 s,
`NFR-007` 1 h/4 h→15 min/2 h. **None of the six states what changed to justify the tightening.**
Recorded separately as `QAA-13`.

**Remediation instruction.** Enterprise Architecture to state `NFR-004`'s basis — headroom,
registered base, or correction — under `RQ-005` change control, and to do the same for the other
five tightenings. **`QA-006` `PLT-37` tests `NFR-004` as written in the meantime**, because a test
plan does not descope a requirement; **`PLT-38` records that the environment cost is caused by the
gap.** Recorded as `QA-006` `Q-07`.

---

## 6. High findings

### 6.1 `QAA-14` — the capacity arithmetic does not close, and this is the category's headline

**Severity: HIGH · Status: OPEN · Owner: CFO with the CTO and Programme Manager**

**What was found.** Recomputed under `X5b`:

| Side | Counted |
|---|---|
| **Supply** | **62 QA FTE-months** across 36 months — **8 of them in W1–W2** |
| **Demand** | ~1,700 executable items · 379 denial cells per wave · 189 accessibility checks per portal release · 1,187 contract tests · 988 event tests · ~33 production releases each needing regression and smoke |
| **`QA-002` §12.2's allocation** | The 62 months allocated across six level plans, **leaving ~67 further FTE-months unfunded** |
| **`QA-005` §13** | A further **~11.5 person-months** to build the automation, spent **before** the surface it automates exists |

**`AUDIT-014` `TS-07` raised this and it has not moved.** What has changed is that it is now
**derived rather than asserted**, and that three closure routes are costed (`QA-001` §10.5).

**Why it stays High rather than becoming Critical.** It is a **decision**, not a defect. The
programme can resource it, automate ahead of it, or reduce scope with the reduction logged. **What it
cannot do is nothing** — because the third route happens by default and without the record that makes
it acceptable. Recorded as `QA-001` `Q-01`, due at the Wave 1 gate.

### 6.2 `QAA-01` — `TS-016` is registered `P2` on a contractual requirement, and nine packs are mis-waved

**Severity: HIGH · Status: OPEN · Owner: Programme Content Lead**

Inherited from `AUDIT-014` `TS-02` and unchanged. `QA-001` §4.5 and `QA-002` §4.2 correct all of
them **once, by rule `MTS-R6`**, as `AUDIT-014` explicitly instructed — but the correction requires a
**Category 13 register change** this category cannot make. Nine wave corrections and one priority
correction are pending.

### 6.3 `QAA-03` — 620 case identifiers in six incompatible schemes, and three packs with none

**Severity: HIGH · Status: OPEN · Owner: QA Lead with the Programme Content Lead**

**What was found.** Counted at 22:20 (+06) across the fifteen script packs:

| Scheme | Form | Packs |
|---|---|---|
| SIT | `SIT-<category>-nnn` | 4 |
| UAT | `UAT-R<nn>-nnn` **and** `UAT-R<nn>-P<nn>-nnn` | 6 |
| E2E | `E2E-nn` | 1 |
| Performance | `PERF-NFR-nnn-nn` | 1 |
| Offline | `OFF-nnn` | 1 |
| Security | `SEC-nnn`, `SEC-SOD-nn` | 1 |
| **None** | — | **`TS-013`, `TS-016`, `TS-018`** |

**620 identified cases against `AUDIT-014` `TS-07`'s ~1,700 executable items** — so roughly **two
thirds of the test estate carries no addressable identifier**, and `CV-M5` cannot see it.

`QA-003` §5 supplies a derivable scheme requiring no allocator and a crosswalk that **renumbers none
of the 620**, but the three schemeless packs need identifiers allocated, which is content work.

> The two-scheme UAT split is what caused `QAA-A1`. **A category whose identifier forms differ
> between files will produce a wrong count in any tool written against it**, and it did.

### 6.4 `QAA-04` — the accessibility conformance target is stated two ways across the estate

**Severity: HIGH · Status: OPEN · Owner: CCO with Enterprise Architecture**

**Counted at 22:20 (+06): 100 files cite WCAG 2.1; 4 cite WCAG 2.2.** `PS-04` (contractual),
`NFR-073` and `05-06` §11 say **2.1**; `UX-005`, `PGD-000` and `_CATEGORY_OVERVIEW.md` say **2.2**.

`QA-008` §3 rules **2.2 AA** and lists four propagation changes — one of which is a **restatement of
a contractual requirement**, which no test plan can make unilaterally.

### 6.5 `QAA-06` — three of the eleven roles this category depends on do not exist

**Severity: HIGH · Status: OPEN · Owner: CTO with the Content Design Lead**

| Role | State | Consequence |
|---|---|---|
| **Head of Quality Engineering** | **Not in `06-01` §4's team model** | Owns the strategy, the automation ratio and the gate quality opinion. `MTS-S4`'s independence rule has no holder |
| **QA Lead** | **Not in `06-01` §4's team model** | Owns L5, L6, triage and the case repository |
| **Accessibility reviewer** | **Absent** | `TS-016` **cannot be executed** — `AUDIT-014` `TS-06` |

`06-01` §4 provides *QA Engineer* only, at 1 FTE in W1. **`GV-009` §5.3 already records four
*assessor* roles that do not exist; this is the same defect on the execution side.**

### 6.6 `QAA-02` — `TS-001` §4.1 is titled *"the twelve test levels"* and tables thirteen

**Severity: MEDIUM → reported under High's neighbours for context · Status: OPEN · Owner: Programme Content Lead**

Counted: `05-06` §11 has **12** data rows; `TS-001` §4.1 has **13** numbered rows. `TS-001` correctly
added SIT, which `05-06` omits, and did not update its own heading. **The content is right and the
heading is wrong**, and `QA-001` `QA-001-D-01` rules thirteen. A heading correction in `TS-001` is
required; **the row must not be deleted.**

---

## 7. Medium and low findings

| # | Finding | Sev | Status | Owner |
|---|---|:--:|:--:|---|
| **`QAA-07`** | **No duty-of-care cover exists for test personnel.** `TS-015` requires testers at six locations, in a moving vehicle and on customer premises, **deliberately without connectivity and therefore without a means of contact**. `SP-030` governs technicians and does not mention test personnel. **This is a safety matter before it is a test-logistics matter** | **MED** | OPEN | HSE Lead with the Programme Manager |
| **`QAA-08`** | **`AUDIT-014` `TS-02`'s nine mis-waved packs is a lower bound; the true figure is twelve.** `QA-002` §4.2's derivation adds `TS-011` (`P03` ships W1 and `G1-11` requires UAT sign-off on it), `TS-013` (the monthly production cadence begins at W1 go-live) and `TS-018` (triage begins with the first test cycle). **`TS-02` derived its list from gate criteria only, and missed the three whose consumer is a release event rather than a gate** | MED | OPEN | Programme Content Lead |
| **`QAA-09`** | **No pack holds the Bengali expansion-layout test cases.** `UX-007` specifies that Bengali runs 15–30% longer and sets the layout rule; `TS-002` supplies a text stress set and `TS-016` assistive technology. **Nothing verifies that a layout survives the expansion**, and `G1-08` requires 100% Bengali on delivered screens | MED | OPEN | Localisation Lead |
| **`QAA-10`** | **The `TS-02` sequencing defect exists in `PGD-000` itself.** `QA-006`, `QA-007`, `QA-008` and `QA-009` were registered at `W2`/`W3` while `G1` consumes all four at Month 4. **A defect found and corrected twice in the *content* register was never checked against the *guiding* register.** Corrected in this issue | MED | **FIXED** | Enterprise Architecture |
| **`QAA-13`** | **None of `05-06` §1–§2's six *"(was N)"* tightenings states what justified it** — `NFR-001`, `-002`, `-003`, `-004`, `-005`, `-007`. A target tightened without a basis is as unverifiable as one set without one, and the programme pays the difference in `PERF` hardware | MED | OPEN | Enterprise Architecture |
| **`QAA-11`** | **`PE-006` should adopt `QA-006` §4's volumetric model rather than derive a second.** `PE-006` is ◐ and prior finding `M-09` records that wave capacity was never validated. **Two volumetric models would be `TS-08`'s defect repeated on the infrastructure side** | LOW | OPEN | Platform Engineering |
| **`QAA-15`** | **The table-integrity check, run across `_AUDIT/`, finds one malformed row outside this category** — `PGD-AUDIT-CAT-09` line 960 carries 2 cells against a 3-cell header. **It is reported and deliberately not corrected**: editing another session's audit report during concurrent authoring is the interference pattern behind five identifier collisions in this repository. Raised to its owner instead | LOW | OPEN (referred) | Category 09 author |
| **`QAA-12`** | **`PGD-000` §0.5's prose read *"27 do not exist at all, of which 23 are marked ⛔"* while its table showed ⬜ 7 and ⛔ 20.** 7 + 20 = 27 ✓ but 23 ≠ 20 — **a correct total concealing a wrong component**, which is the `PGD-A2-24` defect class and the reason `PG-M10` requires regeneration. Corrected in this issue | LOW | **FIXED** | Enterprise Architecture |

---

## 8. Register reconciliation — gate F7 equivalent

**All eight dimensions reconcile.**

| Dimension | Expected by | Expected | Actual | Result |
|---|---|---|---:|:--:|
| Document count | `PGD-000` Category 08 | 11 | 11 | ✅ |
| Priority `P0`/`P1` | `PGD-000` rows | 6 / 5 | 6 / 5 | ✅ |
| Front matter `priority` matches the register row | per document | 11 | 11 | ✅ |
| Status symbol | `PGD-000` §0.5 vs the Category 08 table | 11 ✅ | 11 ✅ | ✅ |
| Category totals | ✅ 99 / ◐ 18 / ⬜ 7 / ⛔ 16 | 140 | 140 | ✅ |
| Regeneration method | `PG-M10` — counted, not arithmetic | recount of 17 rows | recount of 17 rows | ✅ |
| Audit identifier | Not already claimed | free | `PGD-AUDIT-CAT-08` | ✅ |
| `MGA-07` discharge | *"Category 08 holds 7 QA documents on disk"* | now 11, row updated | 11 | ✅ |

> **`needed_by` deliberately diverges from the register in four documents**, and the divergence is
> the finding rather than an error: `QA-006`, `QA-007`, `QA-008` and `QA-009` are issued at `Now`
> against register rows of `W2`/`W3`. `QAA-10` records why, and `PGD-000` is corrected in this issue.

---

## 9. What this category did well, stated for balance

An audit that reports only faults is not credible.

| Asset | Assessment |
|---|---|
| **The denominator is closed, not argued** | `QA-011` consumed `RQ-001` `CR-01` and `RQ-004` `CV-01` unchanged rather than re-deriving a twelfth figure. **A category whose central problem was competing denominators resisted adding one** |
| **Boundaries are drawn before content** | `QA-007` §3's ten-row split with `SC-005`, `SC-009` and `QA-005` claims no activity twice; `QA-005` §6.2 defers the pact layer entirely to `IN-008`. Five identifier collisions in this repository were caused by two authorities on one subject, and this category avoided a sixth |
| **Every prefix was swept before allocation** | Eleven prefixes, all returning zero prior occurrences across five repositories. `RR-002` still does not exist, and the sweep was done anyway |
| **Derived identifiers over allocated ones** | `QA-003`'s `TC-<LEVEL>-<SCOPE>-<nnn>` follows `BE-005`'s solution to the same problem, and **renumbers nothing** |
| **The capacity gap is stated, not absorbed** | `QA-001` §10 and `QA-002` §12.2 publish demand against supply and offer three costed routes. `AUDIT-014` `TS-07` praised the content packs for the same honesty; the guiding layer held the line |
| **Unmeasurable measures are published as unmeasurable** | `QA-011` `RTC-05` refuses both omission and a misleading zero. This is the discipline that would have prevented `TS-01` |
| **The `GV-009` instruction was obeyed** | `GA-12` asked not to be adopted, *"because the numbers here are conventional, not derived."* `QA-010` §5.4 derives all nine, and §5.2 shows why a flat number was wrong — a **2.4× spread across gates** |

---

## 10. Remediation summary

| # | Action | Owner | By |
|---|---|---|:--:|
| **R-01** | **Sequence `PE-002` and `PE-004` as Wave 0.** Nine of thirteen test levels rest on them and 0 of 7 environments exist | CTO | **W0** |
| **R-02** | **State `NFR-004`'s basis** — headroom, registered base, or correction — and do the same for the other five *"(was N)"* tightenings | Enterprise Architecture with CCO | **W1** |
| **R-03** | **Decide the capacity route** at the Wave 1 gate: resource, automate ahead, or reduce with the reduction logged | CFO with CTO | **W1 gate** |
| **R-04** | **Fund `MTS-D1`…`D5`** — 38 role accounts, an accessibility reviewer, the branch kit, staged stock, field logistics | Programme Manager | **T−6 of `G1`/`G2`** |
| **R-05** | **Appoint the Head of Quality Engineering, the QA Lead and the accessibility reviewer** | CTO with Content Design Lead | **W1** |
| **R-06** | **Correct Category 13's register once**: twelve wave corrections and `TS-016`'s priority | Programme Content Lead | **W1** |
| **R-07** | **Rule the WCAG target** and restate `PS-04` contractually | CCO | **W1** |
| **R-08** | **Write `RR-002` and `RR-005`.** Recommended by five audits; the standards-currency defect recurred a fourth time in this category | PMO | **Now** |
| **R-09** | **Resolve the duty-of-care question** for off-site test personnel before any field execution | HSE Lead | **before W2** |
| **R-10** | **Allocate identifiers to `TS-013`, `TS-016` and `TS-018`**, and unify the two UAT forms | QA Lead with Content | **W1** |

---

## 11. Audit control

| Attribute | Value |
|---|---|
| Audit ID | **`PGD-AUDIT-CAT-08`** — category-keyed, following `PGD-AUDIT-CAT-07` and `PGD-AUDIT-CAT-09`. The numeric space `001`–`008` was fully claimed at authoring time; the category-keyed form is the only one computable without reference to another session's work |
| Scope | 11 documents, 7,776 lines, 422 tables |
| Enumeration timestamp | **2026-08-18 22:20 (+06)** — a timestamp, not a date (`PG-M11` / `RG-08`) |
| Estate at that moment | **621 source files** · `project-guide-doc/` **141 files** |
| Findings | **18 — 2 critical, 6 high, 6 medium, 4 low. 6 fixed, 12 open** |
| Findings against the auditor's own authoring | **4** — `QAA-A1`…`QAA-A4`, all fixed |
| Independence class | **`I0` — self-assessment.** `GV-010` records 29 of 29 prior audit reports at `I0`; this is the thirtieth, and it says so |
| Method | Filesystem enumeration, identifier extraction, and **arithmetic re-derivation of every model in the category** |
| Next review | At the Wave 1 gate, with the first `QA-011` coverage report |

> **On independence.** This audit was performed by the function that authored the category, and
> `QAA-A2` — a derivation step estimated and presented as computed — is exactly the class of defect
> a self-assessment is least likely to find. **It was found by recomputing rather than by reading**,
> which is the only method that would have found it, and it is recorded here so that the value of an
> independent pass at the Wave 4 gate is not argued from principle alone.

---

*`PGD-AUDIT-CAT-08` · Category 08 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
