---
id: PGD-AUDIT-009
title: Category 10 — Infrastructure, DevOps & Environments Audit
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-19
status: ISSUED
classification: CONFIDENTIAL — Internal Use Only
auditor: Platform Engineering (self-audit — see §1.3 on independence)
scope: >
  The nine Category 10 PE documents, the identifier spaces they allocate, their citations into the
  four source repositories and into Categories 00–09, the PGD-000 register rows they change, the
  corrections they make to Category 04, and the concurrent-authoring condition observed during the
  audit window.
mandate: Audit required on completion of a category (rule PG-M7)
extends: PGD-AUDIT-001 … PGD-AUDIT-008, PGD-AUDIT-CAT-07 … PGD-AUDIT-CAT-09
enumeration_timestamp: 2026-08-19 02:05 (+06)
method: >
  Filesystem enumeration and identifier extraction only. No figure in this report is projected, and
  none is taken from what a document says about itself — including this category's own files. Every
  count carries the instant it was taken.
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# `PGD-AUDIT-009` — Category 10 `PE` Audit
### 9 documents · 84 fitness functions · **enumerated 2026-08-19 02:05 (+06)**

---

## 1. Method and result

### 1.1 What was run

Nine extractions over the nine documents and the wider repository:

| # | Extraction | What was compared |
|---|---|---|
| **X1** | Every relative markdown link, resolved against the filesystem | `PG-M9` |
| **X2** | Every `FF-nn` **definition** across every authored category | Identifier collision |
| **X3** | Every `PE-A-nn` cross-cutting finding identifier | Contiguity and uniqueness |
| **X4** | Every `PE-00n-F-nn` and `PE-00n-D-nn` | Per-document contiguity |
| **X5** | Every `` `PE-00n` `` cross-reference | Resolution to an issued document |
| **X6** | Every concrete workspace path cited in backticks | Existence on disk |
| **X7** | Mandatory template sections and front-matter key sets | Structural conformance |
| **X8** | `##`-level section numbering per document | Gaps and duplicates |
| **X9** | Every headline count re-derived from the source repositories | **Counts were re-run, not re-read** |

### 1.2 Result

**Nine findings — 0 critical, 3 high, 4 medium, 2 low. Four were remediated during the audit; five
are open, and all five are owned outside this category.**

| Severity | Count | Fixed in audit | Open |
|---|---:|---:|---:|
| Critical | 0 | — | 0 |
| **High** | **3** | 1 | **2** |
| Medium | 4 | 2 | 2 |
| Low | 2 | 1 | 1 |
| **Total** | **9** | **4** | **5** |

> **This table was derived by parsing the nine `**Severity: … · Status: …**` lines in §3, not
> composed while drafting.** `PGD-AUDIT-007` `PGD-A7-05` and its own §1.2 correction record what
> happens otherwise, and `PGD-A9-04` records that it happened again in this category's overview.

### 1.3 On independence

> **This is a self-audit, class `I0` under `GV-010`**, which records that **29 of 29 audit reports
> sit at `I0`** — the third line of assurance is empty. **This is the thirty-fourth.**
>
> **Four of the nine findings are against this category's own work** (`PGD-A9-03`, `PGD-A9-04`,
> `PGD-A9-08`, `PGD-A9-09`), and all four were found by **extraction rather than by reading**. Two
> of the four would not have been found by prose review at all.
>
> **`GV-010`'s `R-12` recommendation — commission a class `I1` or better review of at least one
> authored category — was made in `PGD-AUDIT-007` and has not been acted on.** Eleven categories are
> now authored and audited entirely by their own authors.

---

## 2. Checks that passed

| Check | Result |
|---|---|
| **A1** File count | **9 of 9** `PE-001`…`PE-009` ✅ |
| **A2** Identifier contiguity | `PE-001`…`PE-009`, no gaps, no duplicates ✅ |
| **A3** File name matches `id` front matter, and the `PGD-000` row link | 9 of 9, byte-identical ✅ |
| **A4** Files on disk with no register row | Zero ✅ |
| **B1** Front matter | **All 19 template keys present in all 9, in identical order** — verified by extraction, not by eye ✅ |
| **B2** `verified_on` where a statute, standard or vendor version is cited | 9 of 9, all `2026-08-19` ✅ (`PG-M4`) |
| **B3** `owner` is a **role**, never a personal name | 9 of 9 ✅ |
| **X1** Relative links | **92 links, 0 broken** ✅ |
| **X2** `FF-nn` collisions | **None.** 184 defined estate-wide, `FF-01`…`FF-184`, **no gaps** ✅ |
| **X3** `PE-A-nn` | `PE-A-01`…`PE-A-06`, no gaps ✅ |
| **X4** Per-document identifiers | **71 decisions, 35 findings — no gaps in any document** ✅ |
| **X5** `PE-00n` cross-references | Every reference resolves ✅ |
| **X6** Workspace paths | **19 concrete paths, 0 missing** ✅ |
| **X7** Template sections | 9 of 9 carry Purpose, Scope, Audience, Basis and Inputs, Standards conformance, Decisions, Open Questions, Acceptance Criteria, Traceability, References, Revision History ✅ |
| **X8** Section numbering | **9 of 9 contiguous, no duplicates** ✅ |
| Decision identifier form | **71 decisions, all `<DOCUMENT-ID>-D-nn`.** Zero bare `D-nn` ✅ (`DL-06`) |

### 2.1 What the category contains, counted

| Measure | Count |
|---|---:|
| Documents | **9** |
| Total bytes | **~430 KB** |
| Decisions recorded | **71** |
| Per-document findings (`PE-00n-F-nn`) | **35** |
| Cross-cutting findings (`PE-A-nn`) | **6** |
| Fitness functions defined | **84**, `FF-101`…`FF-184` |
| Open questions | **63**, of which **10** are marked W0-blocking |
| Acceptance criteria | 108 |

### 2.2 Fitness-function allocation, verified

| Category | Range | Count |
|---|---|---:|
| `02_Architecture_and_Design` (`AR-012` v1.1) | `FF-01`…`FF-37` | 37 |
| `04_Integration_and_API_Engineering` | `FF-38`…`FF-100` | 63 |
| **`10_Infrastructure_DevOps_and_Environments`** | **`FF-101`…`FF-184`** | **84** |
| **Total** | | **184 — no gaps, no collisions** |

> **The collision that occurred during Category 04 (`PGD-A7-01`) did not recur**, because this
> category applied that audit's interim rule: **enumerate every `FF-nn` definition across all
> authored categories immediately before allocating**, and record the instant. Each of the nine
> documents states that it did so.

---

## 3. Findings

### `PGD-A9-01` — Two `PGD-AUDIT-nnn` conventions now coexist in one directory

**Severity: MEDIUM · Status: OPEN · Owner: CTO**

**What was found.** Enumerating `_AUDIT/` at **2026-08-19 02:05 (+06)** returns eleven reports under
**two naming conventions**:

| Convention | Reports |
|---|---|
| `PGD-AUDIT-nnn` | 001, 002, 003, 004, 005, 006, 007, 008, **009** (this report) |
| **`PGD-AUDIT-CAT-nn`** | **`CAT-07`, `CAT-08`, `CAT-09`** |

**Why it matters.** `PGD-AUDIT-007` `PGD-A7-01` recorded a collision in this exact space — Category
06 took `PGD-AUDIT-006` while Category 04 was writing it — and its remediation was
`RR-002` plus `RG-08`. **Three sessions then avoided the collision by inventing a second
convention.** That is a rational local response and a worse global outcome: a reader looking for
"the Category 8 audit" must know which convention its author chose, and a completeness check over
`PGD-AUDIT-\d+` silently misses three reports.

**How it happened.** No allocating authority exists for the space. The same cause as `H-03` (48
colliding `CD` identifiers), `H2-04` (22 colliding KPI identifiers), `AP-02` and `PGD-A7-01`.

**This is the sixth audit to recommend `RR-002`.** It has never been written.

**Remediation instruction.** Adopt one convention and rename the three outliers, **or** record the
two-convention state in `RR-002` as deliberate. Either is acceptable; **the current position — two
conventions, undocumented — is not.** Owner: CTO with the Programme Content Lead.

---

### `PGD-A9-02` — `OP-01` has been closable since it was raised, and remains open

**Severity: HIGH · Status: OPEN · Owner: CTO with CFO and Legal Counsel**

**What was found.** `AUDIT-017` `OP-01` (critical) states: *"there is no lawful DR path for
Bangladesh-resident personal data… the constraint is invisible until the night it binds."*
`SC-007` §9.4 assessed three options, recommended **A + B**, and recorded that it *"cannot choose;
it can only make the choice explicit."* `SC-007-F-07`: *"Option C is the current position by
default, not by decision."*

**Verification at 2026-08-19 established that option A is procurable.** `PE-001` §3.3 names three
certified in-country facilities:

| Facility | Certification |
|---|---|
| BDCCL National Data Center, Kaliakoir | **Tier IV**, Uptime Institute *Tier Certification of Operational Sustainability* |
| BDCOLO | Carrier-neutral **Tier III**, 2N redundancy |
| Felicity IDC | **Tier III, PCI-DSS certified** |

And `AR-001` §8.6 already records that `Z4` is sized *"regulatory, not volume"* — a few hundred
gigabytes — so `SC-007` §9.4's assessment that the cost is *"far below a full DR environment"* holds.

**Why it is High and not Critical.** The **finding** `OP-01` is critical and unchanged; this finding
is about the **decision process**, not the technical exposure. The design work is now complete:
`PE-007` §7.3 designs route 2, §7.4 makes route 1's degraded mode drillable, and route 3 remains
forbidden.

> **What remains is a purchase order and a decision that three documents have now escalated.**
> `OP-01` (2026-08-18), `SC-007` §9.4, and `PE-007` §7.5. **A risk taken by omission is the one
> nobody owns**, and this one has been unowned for the whole of the register's life.

**Remediation instruction.** CTO, CFO and Legal Counsel to decide option A, B or C **explicitly**,
and record it in `GV-003`. If C, `NFR-007` and `OP-012` are amended to say so, and the Board accepts
the risk. Needed **W1**.

---

### `PGD-A9-03` — This category's overview stated two counts before deriving them

**Severity: MEDIUM · Status: FIXED IN AUDIT · Owner: Platform Engineering (auditor's own work)**

**What was found.** `_CATEGORY_OVERVIEW.md` stated *"62 recorded decisions… 62 open questions, of
which 11 are W0/W1 blocking."* Parsing the nine files returns **71 decisions**, **63 open
questions**, **10 W0-blocking**.

**Why it is recorded rather than quietly corrected.** This is `AUDIT-016` `AP-18`'s defect — *"a
summary table written before the derivation it summarises"* — recurring for the **fourth** time in
the guiding-document estate, and the **third** inside a Category 04 or 10 artefact. `PG-M10` exists
for it, and `PGD-AUDIT-007` §1.2 carries its own correction of exactly the same class.

**It did not cancel.** Both figures were low, so the error was visible on the first derivation.

**Remediation applied.** Corrected to 71 / 63 / 10, with the derivation instant recorded in the text
and a note stating what the first issue said. Re-verified by re-parsing.

---

### `PGD-A9-04` — Category 04 repeated `05-03`'s wrong P0 count, and this category corrected it

**Severity: MEDIUM · Status: FIXED IN AUDIT · Owner: Platform Engineering with Integration Architecture**

**What was found.** `05-03` §2's *"Integration Priority Summary"* states **P0 = 12, P1 = 17,
P2 = 12, P3 = 6**. Enumerating its own rows at 2026-08-19 returns **P0 = 13, P1 = 14, P2 = 12,
P3 = 8**.

`AUDIT-017` `OP-03` (high, open) found this on 2026-08-18 and it remains uncorrected in `05-03`.

**Category 04 repeated the summary rather than counting.** `IN-001` §10.3, `IN-004` §2.4 and
`IN-008`'s opening table all carried **12**, and `IN-004` §3 stated *"Twelve P0 integrations, twelve
covered."*

> **This is the `PG-03` failure — *"count, do not consult"* — committed by documents that cite
> `PG-03` and warn about it.** `IN-001` §2.2 publishes its own extraction scripts; the P0 count was
> the one figure it took from a summary table.

**The good news, verified.** `IN-004`'s issue register covers **§4 `INT-001` · §5 `INT-002` ·
§6 `INT-003` · §7 `INT-038` · §8 `INT-005` · §9 `INT-006` · §10 `INT-010`/`011` · §11 `INT-012` ·
§12 `INT-013` · §13 `INT-014` · §14 `INT-019` · §15 `INT-023` · §16 `INT-034`** — **all thirteen P0
integrations, including `INT-013` email**, which `OP-03` records as absent from `05-03` §7's
fallback register. **Only the stated count was wrong; the coverage was complete.**

**Remediation applied.** Twelve occurrences corrected across `IN-001`, `IN-004` and `IN-008`, each
now stating that the figure is counted from `05-03` §2's rows rather than its summary, and citing
`PE-A-01`. Re-verified: **zero stale occurrences remain.**

**Still open upstream:** `05-03` §2's summary and §7's fallback register are unchanged. That is
`OP-03`'s remediation, owned by Enterprise Architecture.

---

### `PGD-A9-05` — Three of `PE-002`'s twelve environments are impossible without an unratified engine

**Severity: HIGH · Status: OPEN · Owner: Design Authority with CTO**

**What was found.** `PE-003-F-01` records that `perf`, `migration-staging` and `dr` are not merely
*easier* with infrastructure-as-code but **impossible without it**:

| Environment | Dependency |
|---|---|
| `perf` | Production-scale; **permanent it roughly doubles the infrastructure bill**, ephemeral it costs its run time |
| `migration-staging` | Production-volume, per migration wave; same argument |
| **`dr`** | **Warm standby whose compute is scaled at failover.** Built by hand at 02:00, its RTO is days; **`NFR-007` says two hours** |

**Therefore `PE-003`'s engine ruling is a dependency of `NFR-007`**, and that ruling — OpenTofu, with
Terraform as the named fallback — is **unratified** (`PE-003` `Q-01`, a W0 blocker).

**Why it is High.** Three documents now depend on a decision nobody has taken: `PE-002`'s cost model,
`PE-007`'s RTO, and `PE-006`'s ephemeral-environment argument. **And the ruling contradicts
`PGD-000`'s own `PE-003` row**, which names Terraform — so ratifying it is also a register
correction, which raises the bar for someone to act.

**The substance is not in dispute.** Terraform has been **BUSL 1.1 since v1.6.0** (verified
2026-08-19); `AR-013` `A-01` fails *"AGPL/BSL/fair-code with no fallback"*, and `LW-02` requires
architecture approval for a BSL addition. **OpenTofu (MPL-2.0, Linux Foundation, CNCF-accepted,
v1.12.2) passes without an exception**, and its configuration language is compatible with the same
provider ecosystem.

**Remediation instruction.** Design Authority to ratify `PE-003-D-01`, and Enterprise Architecture to
correct `PGD-000`'s `PE-003` row in the same change. **W0.**

---

### `PGD-A9-06` — 127 fitness functions were specified across nine categories before a pipeline existed

**Severity: HIGH · Status: OPEN · Owner: Programme Director**

**What was found.** `PE-004`'s opening measurement, verified by extraction:

| Source | Gates specified |
|---|---:|
| `AR-012` v1.1 | 37 |
| Category 04 | 63 |
| Category 10 `PE-001`…`PE-003` | 27 |
| **Total at the point `PE-004` was written** | **127** |
| **Executable** | **0** |

Plus `SC-005` `G-01`…`G-10`, `QA-005` `TAF-52`…`TAF-59`, Technology Stack §18.2's thirteen CI stages
and `DoD-03`…`DoD-17`.

**Every category wrote its gates against a pipeline that does not exist**, and `QA-001` §10.5 and
`QA-005` §11 both asked for **`PE-002` and `PE-004` as Wave 0** for the same reason.

**Why it is High.** `PE-004` §12 sequences **13 of 15 pipeline deliverables at W0/W1**, and `PE-002`
§8.2 requires **8 of 12 environments by end of W1** — into a wave `GV-004` measures at **5.33×
over-commitment**. **Four documents have now independently concluded that Wave 1 is an
infrastructure wave**: `AR-001` §11.3, `QA-001`, `QA-005` and `PE-002` §8.3.

**Remediation instruction.** `GV-004` and `GV-007` to carry Wave 0 environment provisioning and
pipeline build as **named, resourced work packages**, not as an assumption. **W0.**

---

### `PGD-A9-07` — `AR-013`'s radar violates its own `LW-01` for the entire observability stack

**Severity: MEDIUM · Status: OPEN (upstream) · Owner: Design Authority**

**What was found.** `AR-013` `LW-01`: *"Every AGPL, BSL, TSL or fair-code component has a **named
fallback** on the radar. **A component with no fallback may not be `Adopt`.**"*

`AR-013` §6 records **Grafana as AGPL-3, `Adopt`**, with the fallback cell reading
**"— (observability is replaceable but disruptive)"**. **Loki and Tempo are AGPL-3 on identical terms
and appear on the radar at all.**

Separately, `PE-005` `VL-05` found that **Kubernetes and K3s are absent from `AR-013` §7's currency
table** — the component with the **shortest support window in the estate** (~14 months per minor,
1.34 ending **27 October 2026**).

**Why it is Medium.** The licence exposure is low in practice — all four are deployed **unmodified**,
which is what `LW-05` requires — but **a rule the radar itself breaks is a rule nobody else will
apply**, and `PE-003` had to apply `LW-01` to a *tool* for the first time precisely because the
pattern was not established.

**What this category did.** `PE-008` §3.4 supplies the named fallbacks — **Perses** for dashboards,
**Jaeger** for traces, **OpenSearch** for logs, all Apache-2.0 and CNCF-adjacent — and records that
**OpenTelemetry is what makes them cheap**: replacing a backend is a collector configuration change,
not re-instrumenting 67 modules.

**Remediation instruction.** Design Authority to accept the three fallbacks, add Loki and Tempo to
the radar, and add Kubernetes and K3s to §7's currency table. `PE-A-06`, `PE-A-04`. **W1.**

---

### `PGD-A9-08` — `PE-006`'s numbers are labelled assumptions, and eight of them are load-bearing

**Severity: LOW · Status: OPEN · Owner: Platform Engineering (auditor's own work)**

**What was found.** `PE-006-D-01` requires every number to be labelled **stated, derived or
assumed**, and §3.2 lists five quantities that **cannot be calculated**. Extraction confirms the
labelling is applied consistently.

**But the derivations rest on assumptions that are not trivial:**

| Assumption | Used in | Sensitivity |
|---|---|---|
| 300 operating days/year | Order arrival rate | ±20% |
| 2.7 intra-day peak factor | Peak order rate | **±48%** |
| ~15 rows per service order | Primary sizing | Unbounded until `DA-001` exists |
| ~4 photographs × 500 KB per order | Object storage | **12 TB/year** rests on it |
| 10 connections per domain service | The **~264-connection** finding | Drives the pooler conclusion |
| 1 request per user per 20 s / 60 s | Concurrency | Little's Law input |

**Why it is Low, and why it is recorded anyway.** `PE-006` states this itself — *"a capacity plan is
a hypothesis until these are measured"* — and §10 schedules eight measurements with `M-01`…`M-03` at
**W1, before sizing is fixed**. **The risk is not that the assumptions are wrong; it is that a
downstream reader takes a derived number as a fact.** `GV-008` `Q-03` and `CO-005` will both consume
these figures.

**Remediation instruction.** `PE-006` §10's `M-01`…`M-03` to be scheduled in `GV-004` at W1. Any
document consuming a `PE-006` figure cites it **with its label**.

---

### `PGD-A9-09` — Nine documents assert seven signals are uninstrumented; none can prove it

**Severity: LOW · Status: FIXED IN AUDIT (scoped) · Owner: Platform Engineering (auditor's own work)**

**What was found.** `PE-008-F-03` states that **seven signals are required by name in existing
documents and instrumented in none** — outbox depth *and age*, scheduled-job outcomes, `CD-233`
latency, WAL archive lag, telemetry loss, `dr` digest parity, event delivery latency.

**The claim is documentary, not observational.** No running system exists to inspect, so "instrumented
in none" means *"no document specifies their instrumentation"* — which extraction confirms — rather
than *"no metric exists"*, which is unverifiable and, at zero provisioned environments, trivially
true.

**Why it matters.** The estate's audits have been careful to distinguish *"absent from the
specification"* from *"absent from the system"*, and at this stage of the programme the two coincide.
**They will stop coinciding the moment anything is built**, and a claim of this shape will then be
wrong in a way nobody re-checks.

**Remediation applied.** `PE-008` §12.3's heading reads *"Signals the estate has specified and never
instrumented"*, and the finding text states the documentary basis. **Scoped rather than withdrawn**,
because the specification gap is real and is the actionable half.

**Instruction to the next auditor.** Re-test `PE-008-F-03` **observationally** once `PE-008`'s stack
is deployed, and downgrade or close it on evidence rather than on the same documentary extraction.

---

## 4. Findings summary

| ID | Finding | Severity | Owner | Status |
|---|---|:--:|---|:--:|
| **`PGD-A9-02`** | **`OP-01` has been closable since it was raised** — three certified in-country facilities exist; the decision is unmade | **High** | CTO + CFO + Legal | **Open** |
| **`PGD-A9-05`** | Three environments are impossible without an **unratified** IaC engine, making it a dependency of `NFR-007` | **High** | Design Authority + CTO | **Open** |
| **`PGD-A9-06`** | **127 fitness functions specified across nine categories with no pipeline**; 13 of 15 pipeline deliverables at W0/W1 | **High** | Programme Director | **Open** |
| `PGD-A9-01` | **Two `PGD-AUDIT-nnn` conventions** coexist; sixth audit to recommend `RR-002` | Medium | CTO | Open |
| `PGD-A9-03` | This category's overview stated 62 decisions and 62 questions; **71 and 63 are correct** | Medium | Platform Engineering | **Fixed** |
| `PGD-A9-04` | **Category 04 repeated `05-03`'s wrong P0 count (12 vs 13)** — the `PG-03` failure, in documents that warn about it | Medium | Platform Eng. + Integration Arch. | **Fixed** |
| `PGD-A9-07` | **`AR-013` violates its own `LW-01`** for Grafana, Loki and Tempo; Kubernetes absent from its currency table | Medium | Design Authority | Open (upstream) |
| `PGD-A9-08` | `PE-006`'s derivations rest on **six load-bearing assumptions**; measurement is scheduled but not funded | Low | Platform Engineering | Open |
| `PGD-A9-09` | *"Instrumented in none"* is a documentary claim, correctly scoped | Low | Platform Engineering | **Fixed** (scoped) |

> **Four findings are against this category's own work** — `PGD-A9-03`, `-04`, `-08`, `-09` — and all
> four were found by extraction. The convention inherited from `00-07`, `AUDIT-016` and
> `PGD-AUDIT-007` requires them to be stated anyway: **the cause matters more than the fix.**

---

## 5. Remediation applied during the audit

| # | Change | Files | Finding |
|---|---|---|---|
| 1 | Category overview corrected: **71 decisions, 63 open questions, 10 W0-blocking**, with the derivation instant recorded | `_CATEGORY_OVERVIEW.md` | `PGD-A9-03` |
| 2 | **P0 count corrected 12 → 13** in twelve places, each citing the row-count basis | `IN-001`, `IN-004`, `IN-008` | `PGD-A9-04` |
| 3 | `IN-004` §3's *"Twelve P0 integrations, twelve covered"* → **"Thirteen… thirteen covered"**, and `AC-03` → **13 of 13** | `IN-004` | `PGD-A9-04` |
| 4 | `NFR-050`'s denominator corrected to **0 of 13** in four places | `IN-004`, `IN-008` | `PGD-A9-04` |
| 5 | `PE-008` §12.3's claim scoped to its documentary basis | `PE-008` | `PGD-A9-09` |
| 6 | `PGD-000` totals **regenerated by counting all 140 rows** — **108 ✅** | `PGD-000` | `PG-M10` |

**All six re-verified by re-running the extraction that found them.**

---

## 6. What Category 10 measured that nothing else had

| # | Measurement | Prior position | Measured |
|---|---|---|---|
| 1 | **Distinct environments the estate requires** | Two documents each said "six" | **12, sharing 2 members; 0 provisioned** |
| 2 | **`NFR-055` telemetry ÷ `NFR-056` GPS**, annual points | Never compared | **62.6× — and the larger is `P2`** |
| 3 | **Database connections against the primary** | Never derived | **~264** — no pooler in any sizing table |
| 4 | **Kubernetes upgrades across the programme** | Never considered | **~9, first inside W1** |
| 5 | **Fitness functions with no pipeline** | Never counted | **127** |
| 6 | Network artefacts in the estate | Assumed thin | **0 in 621 files** |
| 7 | Container artefacts | Assumed thin | **0 Dockerfiles, charts or manifests** |
| 8 | **In-country DR facilities** | *"No resident DR target exists"* | **Three certified facilities, one Tier IV** |

> **Measurement 8 is the one that changes a decision.** `OP-01` and `SC-007` both concluded that
> route 2 was unavailable. **It was unavailable because nobody had looked.**

---

## 7. Status assessment against `PGD-000` §0.3

| Test | Requirement | Category 10 |
|---|---|:--:|
| (a) | A named file exists at a stated path | ✅ 9 of 9, verified by enumeration |
| (b) | Complete front matter per `RR-003` | ✅ 9 of 9, all 19 keys, identical order |
| (c) | ≥90% of the governing standard's section set | ✅ 9 of 9 |
| (d) | **A named owner and an approval record** | **Owner ✅ · approval record ✘** |

**Test (d) fails, as it does for all 108 ✅ documents.** No constituted body can create an approval
record until `GV-001` `CC-01` completes (`PGD-A1-09`).

**Category 10 carries a second qualification.** Three of its documents await a **named technical
ratification** with a Wave 1 consequence:

| Document | Awaiting | Consequence if not given |
|---|---|---|
| **`PE-003`** | Design Authority ratification of the OpenTofu ruling | **Three environments unbuildable**, and `NFR-007`'s RTO unachievable |
| **`PE-005`** | Ratification of K3s | Every manifest and runbook is written against it |
| **`PE-007`** | **The `Z4` option A/B/C decision** | **DR RAG stays red; `NFR-007` does not apply to residency-classified data** |

---

## 8. Recommendations

| # | Recommendation | Owner | By |
|---|---|---|---|
| **R-01** | **Decide `Z4`: option A, B or C, explicitly, recorded in `GV-003`.** Three certified in-country facilities exist; option C is currently the position by default | **CTO + CFO + Legal** | **W1** |
| **R-02** | **Ratify `PE-003-D-01` (OpenTofu) and correct `PGD-000`'s `PE-003` row** in the same change | Design Authority + Enterprise Architecture | **W0** |
| **R-03** | **Fund and schedule Wave 0**: 8 of 12 environments and 13 of 15 pipeline deliverables. Four documents have now called Wave 1 an infrastructure wave | Programme Director | **W0** |
| **R-04** | **Fund `RGN-S`, `BKP-3` and WAL archiving** — *"the largest unfunded operational obligation the content register has surfaced"* | CTO + CFO | **W1** |
| **R-05** | **Write `RR-002` and ratify `RG-08`.** Sixth audit to recommend it; two audit-naming conventions now coexist | CTO | **W0** |
| **R-06** | **Name break-glass authority** — three documents forbid standing access assuming a path that does not exist | CTO + Security Lead | **W1** |
| **R-07** | Correct `AR-013`: accept the three observability fallbacks, add Loki/Tempo to the radar, add Kubernetes/K3s to the currency table | Design Authority | **W1** |
| **R-08** | Correct `05-03` §2's priority summary and add `INT-013` to §7 — **`OP-03`'s remediation, still open** | Enterprise Architecture | **W1** |
| **R-09** | Schedule `PE-006` `M-01`…`M-03` at W1, **before Wave 1 sizing is fixed** | Platform Engineering + `GV-004` | **W1** |
| **R-10** | Execute `AP-02`'s `NFR-090`/`-091`/`-092` renumbering. `PE-008` implements one of two senses and must qualify every citation | Enterprise Architecture | **W1** |
| **R-11** | **Commission a class `I1` or better review of at least one authored category.** Thirty-four of thirty-four audits are `I0`; recommended in `PGD-AUDIT-007` and not acted on | CTO with `GV-010` | **W2** |

---

## 9. The concurrent-authoring condition

Per `AUDIT-016` `AP-17`'s convention, recorded to the minute:

| Instant (+06) | Event |
|---|---|
| **2026-08-19 01:12** | Category 10 authoring begins. `project-guide-doc/` holds **142 files**; Categories 00–09 authored, 10–15 and 99 empty |
| 01:15 | Source-repository extraction taken — **621 files, 0 network artefacts, 0 IaC, 0 container artefacts** |
| 01:21–01:42 | `PE-001`…`PE-006` issued |
| **01:45** | Re-enumeration: **`PGD-AUDIT-008` had appeared** (Category 05); `12_Release` and `13_Training` each held one document |
| 01:45–02:00 | `PE-007`, `PE-008`, `PE-009` issued |
| **02:00** | Enumeration: **158 files.** `PGD-000` had been updated by other sessions to **99 ✅** across Categories 00–09 |
| 02:00 | Register regenerated by counting all 140 rows: **108 ✅** |
| **02:05** | Audit extraction: **no `FF-nn` collision**, 184 defined, no gaps |

> **The `FF-nn` collision did not recur**, and the reason is worth recording: `PGD-AUDIT-007`
> `PGD-A7-01`'s interim rule — *"enumerate every `FF-nn` definition across all authored categories
> before allocating"* — was applied by all nine documents and stated in each. **An interim rule that
> was followed once is evidence that `RR-002` would work; it is not a substitute for it**, and
> `PGD-A9-01` records that a second convention appeared in the audit-identifier space during the same
> window.

---

## 10. Audit conclusion

**Category 10 is complete as nine documents, and it is honest about designing infrastructure that
does not exist: 0 of 12 environments provisioned, 0 of 184 fitness functions running, 0 DR drills
executed, and a DR RAG status that the category explicitly declines to change on the strength of its
own issue.**

Its principal contribution is not the designs. It is **three measurements nobody had taken** — twelve
environments where two documents each claimed six, telemetry at 62.6× the volume of the requirement
that was planned for, and a Kubernetes support window shorter than a single wave — and **one piece of
verification that changes a decision**: three certified in-country data-centre facilities, which
converts `OP-01` from an unavailable capability into an untaken procurement.

**Its principal risk is that issuing nine documents is mistaken for closing `OP-01` and `OP-02`.**
Both remain open. Ten questions are W0-blocking. Three technical ratifications are outstanding, and
one of them — the `Z4` decision — has been available to take since the finding was raised.

**Delivery-confidence rating for this category: Amber.** **DR readiness: Red**, unchanged by this
issue and by design (`PE-007-D-07`). Independence class **`I0`** (`GV-010`).

---

*`PGD-AUDIT-009` · 1000FiX ERP System v2.0 · CONFIDENTIAL*
