---
id: PGD-AUDIT-CAT-14
title: Category 14 — Commercial, Vendor & Contract — Integrity Audit
category: 14 — Commercial, Vendor & Contract
code: CO
finding_prefix: CVA
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-19
status: ISSUED
classification: CONFIDENTIAL — Internal Use Only
auditor: Enterprise Architecture, independent of the authoring session's conclusions
scope_audited: CO-002 · CO-003 · CO-004 · CO-005 · CO-006 (CO-001 is the RFP and is out of scope)
enumeration_timestamp: 2026-08-19 03:02 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# `PGD-AUDIT-CAT-14` — Category 14 Integrity Audit

### Commercial, Vendor & Contract · Code `CO` · Finding prefix `CVA`

---

## 1. Purpose and method

This audit tests the five documents authored into Category 14 on 2026-08-19 against `PGD-000` §0.3's
four ✅ tests, and against the estate's own authoring rules — `PG-03` (count, do not consult),
`PG-06` (cite standards), `PG-M4` (verify citations), `PG-M10` (regenerate totals from rows) and
`DL-06` (never use a bare `D-nn`).

**It is a self-audit, and self-audits have a characteristic failure mode: they confirm.** The three
prior category audits in this estate each found defects in their own category's authoring —
`MGA-04`, `CHA-02`, `QAA-12` — and the estate's own memory of this work records that *"false absence
claims, drifted roll-ups and in-category identifier collisions recur."* This audit was therefore run
as **eleven mechanical extractions from the filesystem**, not as a reading, and every claim of
absence in the five documents was **re-executed** rather than re-read.

**It found ten defects. Nine were corrected before issue; one is referred outside the category.**
Nine are in Category 14's own authoring; the tenth (`CVA-32`) is in the repository `README.md`,
found because this session had to edit it and re-summed its table before doing so.

### 1.1 What was audited

Enumerated from disk at **2026-08-19 03:02 (+06)**:

| Document | Prefix | Rules | Lines | Words | Bytes |
|---|---|---:|---:|---:|---:|
| [`CO-002`](../14_Commercial_Vendor_and_Contract/CO-002_Vendor_Evaluation_and_Selection_Report.md) — Vendor Evaluation & Selection Report | `VES-nn` | 40 | 965 | 12,736 | 79,102 |
| [`CO-003`](../14_Commercial_Vendor_and_Contract/CO-003_Statement_of_Work_and_Deliverable_Acceptance_Schedule.md) — Statement of Work & Deliverable Acceptance Schedule | `SOW-nn` · `PDoD-nn` | 74 + 7 | 906 | 12,509 | 78,162 |
| [`CO-004`](../14_Commercial_Vendor_and_Contract/CO-004_Licence_and_Open_Source_Compliance_Register.md) — Licence & Open-Source Compliance Register | `LIC-nn` | 45 | 791 | 11,302 | 71,845 |
| [`CO-005`](../14_Commercial_Vendor_and_Contract/CO-005_Total_Cost_of_Ownership_Model.md) — Total Cost of Ownership Model | `TCO-nn` | 15 | 1,488 | 19,222 | 118,422 |
| [`CO-006`](../14_Commercial_Vendor_and_Contract/CO-006_Procurement_and_Purchase_Plan.md) — Procurement & Purchase Plan | `PPP-nn` | 49 | 700 | 8,967 | 57,805 |
| **Total** | **6 prefixes** | **230** | **4,850** | **64,736** | **405,336** |

**Verification** *(regenerated from the rows per `PG-M10`)*: rules 40 + 74 + 7 + 45 + 15 + 49 =
**230** ✓ · lines 965 + 906 + 791 + 1,488 + 700 = **4,850** ✓ · words 12,736 + 12,509 + 11,302 +
19,222 + 8,967 = **64,736** ✓.

**Also audited:** 2,202 table rows · **503 distinct identifiers** cited · 47 open questions ·
39 recorded decisions · 22 findings raised (`CVA-01`…`CVA-22`).

`CO-001` is the issued RFP in `primary-doc/` and is **out of scope as a document**. It is, however,
the subject of five of the category's findings, and §7 routes them.

---

## 2. The four ✅ tests

`PGD-000` §0.3 sets four tests. Applied per document:

| Test | `CO-002` | `CO-003` | `CO-004` | `CO-005` | `CO-006` |
|---|:--:|:--:|:--:|:--:|:--:|
| **(a)** The document exists on disk at its registered path | ✅ | ✅ | ✅ | ✅ | ✅ |
| **(b)** It carries the front matter the template requires | ✅ | ✅ | ✅ | ✅ | ✅ |
| **(c)** It contains the sections its document type requires | ✅ | ✅ | ✅ | ✅ | ✅ |
| **(d)** It has a **named owner and an approval record** | ⚠ | ⚠ | ⚠ | ⚠ | ⚠ |

> **Test (d) fails for all five, and it fails for every document in this estate.** Each has a named
> owner and a named approver. **None has an approval record, because no constituted body can create
> one** until `GV-001` condition `CC-01` completes — the ERP Steering Committee's first minuted
> meeting. This is `PGD-A1-09`, recorded as `PGD-A2-25`, and it is carried here rather than resolved
> by inventing a sixth status. **The ✅ recorded in `PGD-000` for Category 14 is therefore qualified,
> on exactly the basis Categories 00–13 are qualified.**

**Test (b) detail** — all eighteen template fields present in all five: `id`, `title`, `category`,
`code`, `project`, `version`, `date`, `status`, `classification`, `owner`, `approver`,
`standards_basis`, `traces_to`, `depends_on`, `verified_on`, `priority`, `needed_by`, `register`.
Extraction returned **zero missing fields**.

**Test (c) detail** — all eight required sections present in all five: Purpose, Basis and Inputs,
Decisions Recorded, Open Questions, Acceptance Criteria, Traceability, References, Revision History.
Extraction returned **zero missing sections**.

---

## 3. Mechanical verification — eleven extractions

Every check below was run as a filesystem command across all six repositories, not read off the
page. The command is stated so the check is re-performable.

### 3.1 Rule-prefix exclusivity

`grep -rho "\b<PREFIX>-[0-9]\{1,3\}\b" --include=*.md .` across the whole workspace, then subtracted
by the same count inside Category 14.

| Prefix | Total occurrences | Inside Cat 14 | **Outside** |
|---|---:|---:|---:|
| `TCO` | 43 | 43 | **0** ✅ |
| `VES` | 128 | 128 | **0** ✅ |
| `SOW` | 168 | 168 | **0** ✅ |
| `LIC` | 92 | 92 | **0** ✅ |
| `PPP` | 87 | 87 | **0** ✅ |
| `PDoD` | 19 | 19 | **0** ✅ |
| `CVA` | 134 | 134 | **0** ✅ |

**All seven prefixes are exclusive to this category.** Each was verified to return zero occurrences
workspace-wide *before* allocation, and each document's header records the verification with its
timestamp.

### 3.2 The `CO-nn` collision — `CVA-01`, confirmed

The category code `CO` was tested against the workspace before any rule was allocated:

| Namespace | Range | Location |
|---|---|---|
| **Cost controls** | `CO-01`…`CO-06` | `PE-006` §8.4 |
| **Content operating model** | `CO-01`…`CO-12` | `project_content/00_Content_Governance_and_Standards/CG-002`, cited by name from at least fourteen further content files and from `GV-011` `CM-16` |
| **Callback ordering** | `CO-01`…`CO-03` | `IN-006` |

**Enumerated: 108 occurrences of the two-digit form, across 30 files and 3 repositories.** This is
the same defect class as `MGA-04` (Category 09) and `CHA-02` (Category 13). **No document in
Category 14 uses `CO-nn` as a local rule prefix**, and the collision is recorded in all five
document headers.

### 3.3 Rule-number sequence integrity

Distinct rule numbers extracted per prefix and compared against a complete sequence:

| Prefix | Distinct | Max | **Gaps** |
|---|---:|---:|---|
| `TCO` | 15 | 15 | **none** ✅ |
| `VES` | 40 | 40 | **none** ✅ |
| `SOW` | 74 | 74 | **none** ✅ |
| `LIC` | 45 | 45 | **none** ✅ |
| `PPP` | 49 | 49 | **none** ✅ |

No gaps and no numbers above the maximum. **`PDoD-01`…`PDoD-07`** complete.

### 3.4 Duplicate rule definitions

Row-leading definitions extracted and counted. **One genuine duplicate found and fixed — `CVA-23`,
§6.1.** The 27 apparent `VES` duplicates are the §14 consolidated rules table restating each rule
once, which is the house pattern established by `CH-001` §11 and `GV-008` §8.1, and is not a defect.

### 3.5 Undefined rule references

Every cited rule was tested against the set of defined rules. **The detector had to be broadened
twice**, and the audit records why: rules in this category are defined in **three** positions —

| Position | Example |
|---|---|
| Row-leading cell | `\| **`VES-08`** \| Every assessor scores independently… \|` |
| **Trailing rule-ID column** | `\| 1 \| 1000FiX is controller… \| `SOW-66` \|` |
| Prose blockquote | `> **`SOW-15`: milestone 5's 14% …** ` |

After broadening, **zero rules are cited without being defined** across all six prefixes. The first,
narrow pass produced 37 false positives; they are recorded here so that a future audit does not
repeat the wasted pass.

### 3.6 Finding-identifier integrity

| Check | Result |
|---|---|
| `CVA-01`…`CVA-22` present | ✅ complete, no gaps |
| Each raised in exactly one document | ✅ — `CO-005` raises 01–06, `CO-002` 07–09, `CO-003` 10–14, `CO-004` 15–18, `CO-006` 19–22 |
| Cross-references resolve to the raising document | ✅ |

### 3.7 Open-question sequence integrity

| Prefix | Questions | Gaps | *"All N escalated"* claim |
|---|---:|---|---|
| `VES-Q` | 8 | none | "All eight" ✅ |
| `SOW-Q` | 11 | none | "All eleven" ✅ |
| `LIC-Q` | 9 | none | "All nine" ✅ |
| `TCO-Q` | 10 | none | "All ten" ✅ |
| `PPP-Q` | 9 | none | "All nine" ✅ |

**47 open questions, every one with a named owner and a needed-by date.** The estate's rule — *"an
open question with no owner and no needed-by date is not an open question; it is an unrecorded
risk"* — holds in all five documents.

### 3.8 Decision-identifier form — `DL-06`

`DL-06` forbids the bare form `D-nn`, because applied across 140 documents it would produce up to
140 different decisions sharing an identifier — the defect class behind `H-03`, `H2-04` and
`PGD-A1-01`.

**39 decisions, all in the `<DOCUMENT-ID>-D-nn` form**: `CO-002-D-01`…`-07`, `CO-003-D-01`…`-09`,
`CO-004-D-01`…`-07`, `CO-005-D-01`…`-09`, `CO-006-D-01`…`-07`. **Verification**: 7 + 9 + 7 + 9 + 7 =
**39** ✓. **Zero bare `D-nn` forms.**

### 3.9 Path resolution

Every relative path in all five documents was extracted and tested for existence, with glob
expansion for the estate's established `_*.md` abbreviation *(154 occurrences of that convention
exist in other categories, so it is house style and not a defect)*.

| Pass | Result |
|---|---|
| First pass | **4 unresolved** — three elliptical `../nn_…` forms and one `project_content/17_.../`. **`CVA-29`, fixed** |
| Re-run after fix | **0 unresolved** ✅ |

### 3.10 Upstream identifier resolution

Forty-four identifiers cited by Category 14 but owned elsewhere were tested for existence outside
Category 14: `PGD-A2-25`, `RSK-001`, `RSK-008`, `MQ-06`, `DoD-13`, `SG-1`, `L6-02`, `LW-01`,
`LX-27`, `BEA-15`, `BEA-16`, `PE-006-F-07`, `PE-002-F-04`, `PE-008-F-01`, `TPD-06`, `TPD-14`,
`TPD-19`, `CC-01`, `CC-05`, `CC-09`, `D-014`, `D-016`, `D-017`, `D-018`, `W0-01`, `DEP-29`,
`DEP-31`, `OPT-12`, `CR-04`, `EM-05`, `EM-06`, `CB-01`, `CB-09`, `CB-10`, `PG-03`, `PG-06`,
`PG-M4`, `PG-M10`, `RG-08`, `SEL-04`, `SEL-05`, `ES-3`, `HD-03`, `HX-08`.

**Every one resolves.** Zero dangling upstream citations.

### 3.11 Register reconciliation

The `PGD-000` roll-up was **recounted from its own seventeen category rows** per `PG-M10`, not
derived by arithmetic on the previous issue:

| | Docs | ✅ | ◐ | ⬜ | ⛔ |
|---|---:|---:|---:|---:|---:|
| Recounted from rows | **140** | **130** | **4** | **3** | **3** |
| Sum check | | | | | **130 + 4 + 3 + 3 = 140** ✅ |

The register's stated total was **125 / 6 / 5 / 4** before this session and had **not** been updated
for Category 14 — the v1.8 note says so explicitly and correctly, declining to assert ✅ for work it
had not assessed. It is now **130 / 4 / 3 / 3**, and `PGD-000` moves to **v1.9**.

---

## 4. Arithmetic verification

`PG-M10` requires totals to be regenerated from their rows. The audit did this **mechanically**, by
parsing each table and re-summing it, rather than by re-reading the verification lines.

| Table | Rows parsed | Recomputed | Stated | |
|---|:--:|---|---|:--:|
| `CO-005` §7.1 Tier 1, Years 1–3 | 13 (A–M) | 1,488 / 2,558 / 4,330 | 1,488 / 2,558 / 4,330 | ✅ |
| `CO-005` §5.8 non-people subtotal | 6 | 344 / 611 / 1,009 | 344 / 611 / 1,009 | ✅ |
| `CO-005` §7.3 five-year Tier 1 | 2 | 1,912 / 3,249 / 5,367 | 1,912 / 3,249 / 5,367 | ✅ |
| `CO-005` §7.3 five-year Tier 2 | 3 | 2,311 / 3,977 / 6,568 | 2,311 / 3,977 / 6,568 | ✅ |
| `CO-005` §7.3 three-year Tier 2 | 2 | 1,866 / 3,239 / 5,444 | 1,866 / 3,239 / 5,444 | ✅ |
| `CO-005` §5.2 environment multiplier | 9 + 4 | 0.93–1.90; 2.20–3.34 | as stated | ✅ |
| `CO-005` §5.3 `BD-R` annual | 5 | 21.6 / 66.0 | 21.6 / 66.0 | ✅ |
| `CO-005` §6.4 hypercare | 2 pools | 538 PW; 131 / 177 / 223 | as stated | ✅ |
| `CO-005` §6.6 internal draw | 7 | 3,775 / 5,303 PW | 3,775 / 5,303 | ✅ |
| `CO-005` §10.2 payback at FX 122.70 | 5 | cum. 2,278.8; month 49.6 | as stated | ✅ |
| `CO-002` §5.3 evaluation weights | 13 | **100%**; criteria 1–4 = **50%** | 100%; 50% | ✅ |
| `CO-002` §5.5 RFP team-model capacity | 9 | 543 FTE-months → **1,834 effective PW** | 1,834 | ✅ |
| `CO-003` §5.2 register typing | 17 | registered **140**; on disk **131** | 140 / 131 | ✅ |
| `CO-003` §7.1 payment milestones | 11 | **100%**; milestones 1–5 = **58%** | 100%; 58% | ✅ |
| `CO-004` §5.2 component register | 35 | O1 22 · O2 1 · O3 7 · O4 4 · O5 1 = **35** | 35 | ✅ |
| `PGD-000` roll-up | 17 | 140 / 130 / 4 / 3 / 3 | as corrected | ✅ |

**Two reconciliation chains were checked end to end** rather than row by row:

| Chain | Result |
|---|---|
| `GV-008` §4.4 → `CO-005` §7.1 | 1,024 + 179 + 285 = **1,488** ✅ · 1,630 + 339 + 589 = **2,558** ✅ · 2,608 + 629 + 1,093 = **4,330** ✅. Expected delta **+$928K**, of which 37% is the non-people re-derivation `GV-008` requested and 63% is lines no document carried |
| `CO-005` §5 per-line Years 4–5 → §7.2 per-year | Reconciled after **`CVA-26`** was fixed; five of six lines reconciled on the first pass |

**One arithmetic defect was found: `CVA-26`.** It is recorded at §6.4.

---

## 5. Substantive verification

Mechanical checks do not test whether a claim is *true*. Six substantive claims were re-executed.

| # | Claim | Test | Result |
|:--:|---|---|---|
| 1 | *"No cost figure in the estate carries a tax line"* (`CVA-03`) | `grep` for VAT / Mushak / withholding across `GV-007`, `GV-008`, `02-05`, `06-02` | **Holds.** Every hit is VAT as a **system capability** — Category G module scope, `KPI-057` *"VAT returns filed"*, gate criterion `G3-04` *"Mushak invoices accepted"*, `G7-05` *"VAT treatment validated"*. **None is a cost line in a cost model.** The distinction is stated so a later reader does not mistake the claim for carelessness |
| 2 | *"The Company has never computed a five-year figure"* (`CO-005` §9.3) | `grep` for five-year TCO / Year 5 run rate across `00_*`, `02_*` and `1000fix_ERP_Module` | **Holds.** Zero hits, while RFP §16.2.10 requires respondents to state theirs and §17.1 Stage 6 evaluates them |
| 3 | **OCA modules are AGPL-3, not LGPL-3** (`CVA-15`) | Verified against the OCA's own published licensing position and the OCA–Odoo licence agreement, 2026-08-19 | **Confirmed.** Odoo 19 CE is LGPL-3 ✔ (the estate is right); **OCA modules are predominantly AGPLv3**, retained deliberately *"to protect users of OCA addons from being locked in by service providers."* Three estate documents record LGPL-3 |
| 4 | **Only Redis ≤ 7.2 is BSD-3** (`CVA-16`) | Verified against Redis's published licence pages and release history, 2026-08-19 | **Confirmed.** BSD-3 to 7.2; **RSALv2/SSPLv1 for 7.4–7.8**; tri-licence adding AGPLv3 from 8.0. **RSALv2 appears in no list** — allow, gated or deny — in `BE-007` §6.1's policy file |
| 5 | **MinIO archived 25 April 2026** (`BEA-16`, carried) | Independently verified against public reporting, 2026-08-19 | **Confirmed**, corroborating `BE-007` §7.1. Garage (AGPL-3, release 16 April 2026) and SeaweedFS (Apache-2.0) confirmed as maintained alternatives. **Garage is also AGPL-3**, so the swap does not remove the obligation |
| 6 | **FX 110 is 11.5% adrift** (`CVA-04`) | Market data, 2026-08-19 | **Confirmed.** USD/BDT **122.70** on 17 Aug 2026; 2026 average **122.44**; August high 123.785. `GV-008` `A1` itself marked the rate *"not verified"* and asked for verification. **110 was not the market rate at any point in 2026** |

**Two RFP-derived claims were re-read against the source** because they carry a Critical finding:

| Claim | Source text | Verdict |
|---|---|---|
| RFP §17.2 criterion 7 benchmarks capacity at **1,513 PW** | *"An **independent capacity analysis against 1,513 PW**; an honest view of whether 9 waves in 36 months is achievable"* — 8%, with a sub-50 elimination floor under §17.3 | ✅ verbatim |
| RFP §16.1 publishes **$690K–$1,150K** and warns against bids *"materially below"* it | *"A bid that is materially below the envelope will be scrutinised for scope understanding, not rewarded for price"* | ✅ verbatim |

**`CVA-02` and `CVA-09` are confirmed on the source text.**

---

## 6. Findings against the category's own authoring

Ten defects. **Nine were corrected before issue; one is referred outside the category.**

### 6.1 `CVA-23` — a duplicate rule under two identifiers · **FIXED**

**Severity: Medium · Type: In-category identifier duplication**

`CO-002` §7.3 defined `VES-26` as *"References are contacted by a panel member who did not score
that respondent's technical criteria (`VES-10`)"* — which **is `VES-10`**. The §14 consolidated
table then read *"`VES-26` — (see `VES-10`) — reference caller independence."* One rule, two
identifiers.

This is the defect class the estate has recorded three times: `H-03` (48 colliding CD identifiers),
`H2-04` (22 colliding KPI identifiers), `MGA-04`.

**Fix applied.** `VES-26` was given distinct content that the section actually needed and did not
have: *"A reference the Company cannot reach without the respondent's assistance is not a
reference"* — `VQ-41` requires written permission to contact references **directly and without the
respondent present**, so a contact reachable only through the respondent is recorded as unverified
and does not count toward the `VQ-37`…`VQ-39` minimums.

### 6.2 `CVA-24` — a drifted roll-up of the document's own table · **FIXED**

**Severity: Medium · Type: Arithmetic inconsistency**

`CO-004` §5.2's commentary claimed *"**four** are marked ⚠ … **Eleven** rows are marked ▣ carried …
a register whose rows are two-thirds unverified."* Extraction of the 35-row table returned:

| Mark | Actual |
|---|---:|
| ✔ verified, agrees | **2** |
| ⚠ verified, differs | **3** |
| ▣ carried / inferred | **30** |
| **Total** | **35** ✅ |

**Four claims were wrong**: four ⚠ (actual 3), eleven ▣ (actual 30), *"two-thirds unverified"*
(actual six-sevenths), and `LIC-Q-04`'s *"the eleven ▣ rows"*. The revision history's *"found four
to differ"* was also wrong.

> **This is exactly the failure the estate's own memory of this work predicts** — a roll-up written
> from the author's recollection of a table rather than from the table. It is the `PGD-A2-24` defect
> class: *a correct total concealing a wrong component*, except here the total was wrong too.

**Fix applied.** All five occurrences corrected, and a **regenerated verification line** added to
§5.2 so the counts are re-performable: *"35 rows · ✔ = 2 (rows 1, 8) · ⚠✔ = 3 (rows 2, 5, 10) ·
▣ = 30 (27 carried + 3 inferred). 2 + 3 + 30 = **35** ✔."*

### 6.3 `CVA-25` — an estimate superseded mid-session by its owning document · **FIXED**

**Severity: High · Type: Superseded input**

`CO-005` §6.4 originally derived hypercare itself — 4–8 weeks × 9 waves × a 4–6 person squad =
144–432 PW, expected 270 PW — because `SV-005` did not exist when the section was written.

**`SV-005` was issued during the authoring window**, and it derives the figure properly:

| `SV-005` §5.5 pool | Effort | Owner |
|---|---:|---|
| 1 — Project (ring-fenced delivery team + coordination) | **288 PW** | Programme / CTO |
| 2 — Support (T1 at 2× baseline) | **250 PW** | Head of ITSM / CFO |
| 3 — Business (floor-walking, ride-alongs) | **≈ 140 PW** | Operations Director |
| **Total** | **≈ 678 PW** | |

`CO-005`'s own rule **`TCO-02`** says: *"Effort is taken from the owning document unchanged. This
document does not re-estimate effort."* The original §6.4 breached it — defensibly at the time,
since the owning document did not exist, but not once it did.

**Fix applied.** `SV-005`'s figures adopted: pools 1 and 2 (**538 PW**) into Tier 1 line C at the
build rate and a newly-derived support rate; pool 3 (**140 PW**) into Tier 2's internal draw.
**Propagated through 27 downstream figures** — line D's escalation base, §7.1's three totals, the
`GV-008` reconciliation, §7.2, §7.3's six tier totals, the backfill bridge, §8's sensitivity, §9.1's
eight reconciliation rows, §9.2's four ratios, §10.2–§10.3 and §11's five options. **All
re-verified mechanically at §4.**

> **The finding is larger than the correction.** `SV-005` settles the duration question `CVA-06`
> raised — `OP-002` §4.3's per-wave durations sum to **56 weeks**, not 36. **RFP §14.1 prices four
> weeks per wave.** The contractual hypercare scope is understated by **20 weeks, or 56%**, and
> respondents are pricing against the lower figure. **`CVA-06` was re-graded from Medium to High**
> and joins Addendum 1.

### 6.4 `CVA-26` — an internal reconciliation failure between two sections · **FIXED**

**Severity: Low · Type: Arithmetic inconsistency**

`CO-005` §5.4 gave third-party API cost for Years 4–5 as **$46K / $84K / $132K**, while §7.2's
per-year figures were $23K / $40K / $63K — which double to $46K / **$80K** / **$126K**. Low
reconciled; expected and high did not.

Five of the six Years-4–5 lines reconciled on the first pass (`BD-R`, L6, support, training refresh,
and the regional infrastructure derived in §7.2). **Fix applied**: §5.4 restated to $46K / $80K /
$126K, matching §7.2.

### 6.5 `CVA-27` — an enumeration stale by twenty-six minutes · **FIXED**

**Severity: Medium · Type: Stale count**

`CO-003` §1.1 and §5.2 were written against a disk enumeration at **02:36** returning **123**
authored and **15** absent. The audit re-run at **03:02** returned **131 and 7**. **Eight documents
were authored by concurrent sessions in twenty-six minutes** — `SV-003`, `SV-004`, `SV-005`,
`SV-006`, `RL-005`, `RL-006`, `BM-002`, `RR-001`, `RR-002`, less this session's own.

The document was not *wrong* — it stated its enumeration timestamp, as `PG-03` requires — but a
Statement of Work whose deliverable schedule is a moving target is not a schedule.

**Fix applied.** §1.1 and §5.2 re-enumerated at 03:02 with the per-category column corrected
(Category 11: 4 → 6 · 14: 2 → 5 · 15: 0 → 1 · 99: 0 → 2), the verification line regenerated, and a
new open question raised:

> **`SOW-Q-11` — which enumeration of `PGD-000` is the contractual one?** The Statement of Work must
> name a **frozen enumeration by timestamp** as its Schedule 1. `PG-03`'s *"count, do not consult"*
> has a corollary in an estate authored concurrently: **count, state when you counted, and re-count
> before you rely on it.**

**This is the eleventh recorded baseline movement in this estate.** It also had a substantive
consequence: `SV-005` and `SV-006` had moved from absent to present, which resolved `CVA-06`
(§6.3) and discharged one of the seven documents `CO-003` §5.3 named as the supplier's to author.

### 6.6 `CVA-28` — a rendering artefact · **FIXED**

**Severity: Cosmetic** · `CO-005` §10.2 contained `$$month 47$$` — a LaTeX delimiter that would
render as literal dollar signs in a document where `$` means USD. Corrected to *"approximately
**month 47**."* Recorded rather than silently fixed, because in a cost document a stray `$` is not
purely cosmetic.

### 6.7 `CVA-29` — four unresolved paths · **FIXED**

**Severity: Low** · Three elliptical `../nn_…` forms in `CO-003` §2.2 and one
`project_content/17_.../OP-002_*`. All four expanded to real paths; re-run returned **zero
unresolved** across all five documents. The estate's own instruction — *"verify every path resolves
before issuing"* — is in every document's References section and was not self-applied until audit.

### 6.8 `CVA-30` — cross-document reference drift in the placeholder rule numbers · **FIXED**

**Severity: Medium · Type: Cross-reference integrity**

`CO-005` and `CO-002` were authored **before** `CO-003` and cited eight `SOW-nn` rules by
placeholder numbers — `SOW-08`, `SOW-19`, `SOW-20`, `SOW-24`, `SOW-27`, `SOW-31`, `SOW-32`,
`SOW-33`. When `CO-003` was written, those numbers landed on **different rules**: `SOW-31` became
*"an unnotified delay is not relievable"* rather than the no-gross-up clause, `SOW-32` became relief
reporting rather than the FX mechanism, and so on.

**Left uncorrected, `CO-005` §6.2 would have told the CFO that an $83K withholding exposure is
closed by a clause about delay notification.**

**Fix applied.** All eight remapped to the rules they were describing — `SOW-42` (no gross-up),
`SOW-44` (FX), `SOW-48` (wave re-baseline), `SOW-56` (key-personnel schedule), `SOW-40`
(substitution remedy), `SOW-53` (clean descope), `SOW-28` (Company obligations), `SOW-36` (step-in)
— and **all eight verified to resolve to real `CO-003` rules**.

> **The general lesson is worth recording.** Forward references to a document not yet written are
> unavoidable when a category is authored in one session, and they are **silently wrong** rather
> than broken: every identifier resolves, so no link checker catches it. **`CVA-30` is the argument
> for auditing cross-references by meaning, not only by resolution.**

### 6.9 `CVA-31` — `SV-005` §5.7 compares against a superseded build figure · **OPEN, referred**

**Severity: Low · Type: Superseded citation · Owner: Service Manager**

`SV-005` §5.7 compares its 678 PW hypercare derivation against a build estimate of **1,513 PW**,
giving *"≈ 45% of build"* and finding `HCT-F-04`. `GV-007` §4.1 superseded 1,513 PW with a counted
**1,842 PW** on 2026-08-18. The correct share is **678 ÷ 1,842 = 36.8%**.

**This does not change any figure in Category 14**, which uses the 678 PW directly, and it does not
weaken `HCT-F-04` — 36.8% of build is still a stabilisation effort in neither published estimate.
**Referred to `SV-005` for correction. Not fixed here**, because `SV-005` belongs to Category 11 and
editing another category's document from an audit of this one is the defect `PG-07` forbids.

### 6.10 `CVA-32` — `README.md`'s category table did not reconcile with its own total · **FIXED**

**Severity: Medium · Type: Arithmetic inconsistency, pre-existing**

Found because this session had to update `README.md`'s Category 14 row and re-summed the table
before editing it, per `PG-M10`.

The *"still missing"* column carried **stale values for four categories that had since been
completed** — `04` (3), `05` (8), `07` (5), `10` (7) — while their documents were all present on
disk. The rows summed to **26**; the stated total was **15**.

| | Before | After |
|---|---:|---:|
| Category 04, 05, 07, 10 | 3 · 8 · 5 · 7 | **0 · 0 · 0 · 0** ✅ |
| Category 15 | 1 | **3** — `BM-001` ✅ from outside plus `BM-002` on disk, of 5 registered |
| Category 99 | 2 | **4** — `RR-001` and `RR-002` on disk, of 6 registered |
| **Row sum** | **26** | **7** |
| **Stated total** | **15** | **7** ✅ |

> **This is the `PGD-A2-24` defect class in its purest form**: a total that was *nearly* defensible
> concealing six wrong components, in the file most readers of this repository open first. It
> predates this session — the four stale rows were left behind when those categories completed —
> and it survived because nobody re-summed a column they were not editing.

**Fix applied.** Six rows corrected against the filesystem enumeration, the total set to **7**, and
the headline restated to *"133 on disk · 7 still missing, 3 of them blocking."* **The re-sum now
reconciles: rows = 7, total = 7, headline = 7.**

> **What was *not* changed, deliberately.** The corrected column is *"still missing"* — a
> **filesystem fact** this session enumerated. **No ✅ status was set for any document outside
> Category 14**, because asserting ✅ for work this session has not assessed against `PGD-000`
> §0.3's four tests is the defect `PG-M2`, `PG-07` and `PGD-A1-08` forbid, and which `README.md`'s
> own warning box correctly refuses to commit. `BM-002`, `RR-001` and `RR-002` exist on disk and
> their register rows remain unset by this session.

---

## 7. Findings the category raised against the estate

Twenty-two findings, `CVA-01`…`CVA-22`. Three are Critical or High **and act on a deadline**.

### 7.1 The three that are time-limited

| # | Finding | Severity | Deadline | Owner |
|:--:|---|:--:|---|---|
| **`CVA-02`** | **The live RFP publishes a budget envelope and an effort basis that `GV-007` and `GV-008` superseded five and six days after issue, into an open procurement** | **Critical** | **17 September 2026** — the written-question deadline, the last date the RFP's own machinery can carry a correction | Head of Procurement |
| **`CVA-09`** | **Both mechanisms an evaluation has for detecting an under-scoped bid are keyed to that same superseded figure** — §17.2 criterion 7's capacity benchmark (8%, sub-50 elimination floor) and §16.1's envelope test. As published, **the instrument rewards the optimistic bidder and penalises the accurate one** | **Critical** | As above | Head of Procurement |
| **`CVA-06`** *(re-graded)* | **RFP §14.1 prices 36 hypercare weeks; `SV-005` requires 56** — a 56% understatement of a contractual scope | **High** | As above | Service Manager / CFO |
| **`CVA-11`** | **RFP §16.4 releases 0% of a milestone on a conditional pass; `GV-009` §6.3 releases 80%.** Under the RFP's reading the supplier must start the next wave unpaid, which makes CONDITIONAL PASS commercially identical to FAIL and destroys the middle outcome `GV-009` created deliberately | **High** | **Before contract signature**, and by addendum rather than at negotiation, so that all respondents price the same term | CFO with Steering Committee |

> **All four belong in one instrument: RFP Addendum 1, issued before 17 September 2026.**
> `CO-005` `CO-005-D-05` specifies it, `CO-002` §5.4 extends it, and `CO-003` `SOW-22` adds the
> conditional-pass term. **It is a two-page document that closes a Critical procurement-integrity
> exposure, and the window is twenty-nine days from issue.**

### 7.2 The remaining eighteen, by owner

| Owner | Findings | Theme |
|---|---|---|
| **Chief Architect** | `CVA-15`, `CVA-16`, `CVA-18`, `CVA-21` | **OCA is AGPL-3, not LGPL-3** · **Redis 7.x spans two licence regimes and RSALv2 is in no policy list** · two licence-review cadences · two L6-review cadences |
| **CFO** | `CVA-03`, `CVA-04`, `CVA-10`, `CVA-12` | No tax line in any cost figure · FX 11.5% adrift · retention ambiguity · the warranty tail running to Month 48 |
| **Legal Counsel** | `CVA-17` | No outbound licence position for five external populations |
| **Head of Procurement** | `CVA-07`, `CVA-08`, `CVA-19`, `CVA-20`, `CVA-22` | `MQ-06` calibrated to a superseded scope · disciplines priced but unstaffed · **the device estate is unowned** · the hub count is stated nowhere · no sustainable-procurement position |
| **Chief Architect / QA Lead** | `CVA-13`, `CVA-14` | `DoD-17` has no recurrence rule · **the twelve portals have no Definition of Done** |
| **Platform Engineering** | `CVA-05` | `PE-002` §9.1 counts `dr` twice and includes `local`, which bears no shared cost |
| **Enterprise Architecture** | `CVA-01` | The `CO-nn` rule-prefix collision |

### 7.3 The two findings with the largest financial consequence

| Finding | Consequence |
|---|---|
| **`CVA-02` / `CVA-09`** | A procurement running to award in March 2027 against an envelope its own budget baseline disowns. `CO-005` §7.1 puts the three-year expected cost at **$2,558K** against a published upper bound of **$1,150K** |
| **`CVA-15`** | **The AGPL-3 network-service obligation reaches the module layer the programme plans to modify.** The discharge already exists — RFP §19.1(4)'s upstream-contribution clause — but was recorded across three documents as community goodwill rather than as the mechanism that discharges a legal obligation. **`LIC-10` makes it non-tradeable in negotiation; `SOW-64` makes a breach material** |

---

## 8. What this audit did not check

Stated because an audit that does not bound its own coverage invites the reading that it was
exhaustive.

| Not checked | Why | Who should |
|---|---|---|
| Whether the **cost model's judgement** is right — the environment multipliers, the `BD-R` component prices, the internal rate band | They are engineering and market judgements at estimate class 4–5, not arithmetic. The audit verified that they are **labelled**, **derived in the open** and **internally consistent** | `GV-010` independent assurance; `TCO-Q-01` and `TCO-Q-04` |
| Whether **ISO 15686-5, ISO 37500, ISO 44001, ISO 20400 and ISO/IEC 5230 conformance claims** are correctly scoped | Each document declares partial conformance and names its departures, which is what `PG-06` requires. Testing the claim needs the standards themselves | A standards reviewer; `LIC-Q-05` |
| The **thirty ▣ carried licence rows** in `CO-004` §5.2 | Out of time. Five positions were verified and **three of the five differed**, which is a high enough hit rate that the remaining thirty should not be assumed correct | `LIC-Q-04`, at the Wave 1 gate |
| Whether the **Bangladesh tax positions** are right in law | §6.1 and §6.2 of `CO-005` state statutory rates from published guidance and **explicitly disclaim being a tax opinion** | `TCO-Q-02`, `TCO-Q-03`; `CO-006` §8 item 5 commissions it |
| Whether **`PGD-000`'s other sixteen categories** reconcile after this session's edits | Only Category 14's rows and the roll-up were changed, and the roll-up was recounted from all seventeen rows | The next category audit |
| **Prose quality, tone and length** | Not an integrity property | — |

---

## 9. Verdict

| Test | Result |
|---|---|
| All five documents exist, complete, at their registered paths | ✅ |
| Rule prefixes exclusive; sequences complete; no duplicates | ✅ *(after `CVA-23`)* |
| No undefined rule references; no bare `D-nn` | ✅ |
| All 503 identifiers and all paths resolve | ✅ *(after `CVA-29`)* |
| Cross-document references resolve **by meaning**, not only by form | ✅ *(after `CVA-30`)* |
| Every total regenerated from its rows and machine-verified | ✅ *(after `CVA-24`, `CVA-26`)* |
| Every absence claim re-executed against the filesystem | ✅ — all hold |
| Every volatile external fact verified with a date | ✅ — six verified 2026-08-19 |
| Owning documents' figures taken unchanged | ✅ *(after `CVA-25`)* |
| `PGD-000` reconciled and recounted from its own rows | ✅ |
| **Approval record** | ⚠ **Cannot exist until `CC-01`** — `PGD-A2-25` |

> **Category 14 is issued with a qualified ✅**, on the same basis as Categories 00–13.
>
> **The audit found ten defects and fixed nine.** Three of them —
> a duplicate rule, a drifted roll-up, and eight cross-references that resolved but pointed at the
> wrong rules — would each have survived a careful reading and were caught only by extraction. The
> fourth, `CVA-25`, was caught only because the audit **re-enumerated the filesystem** and found that
> the owning document for one of its inputs had been written in the meantime.
>
> **That is the case for running a category audit as eleven extractions rather than as a read.**

---

## 10. Recommendations

| # | Recommendation | Owner | By |
|:--:|---|---|---|
| **1** | **Issue RFP Addendum 1** covering `CVA-02`, `CVA-09`, `CVA-06` and `CVA-11`, and extend the submission deadline by the notice §18.1 requires | Head of Procurement | **17 September 2026** |
| **2** | Escalate `CVA-02` to `GV-005` as **Critical** and to `GV-003` as a decision — amending an issued RFP is a Steering Committee act | Programme Director | **Immediately** |
| 3 | Correct the **OCA licence position** in `02-05` §4, `AR-013` §6 and `BE-007` §6.2, and extend `BE-007` §6.3's AGPL-3 test table to the module layer | Chief Architect | W1 |
| 4 | Add **RSALv2** to `BE-007` §6.1's policy file, pin the Redis version, and put **Valkey** on `AR-013`'s radar as the named fallback | Chief Architect | W1 |
| 5 | Run the **verification sweep of the thirty ▣ rows** in `CO-004` §5.2 | Chief Architect | Wave 1 gate |
| 6 | Answer **`SOW-Q-11`** — name a frozen `PGD-000` enumeration as the Statement of Work's Schedule 1 | Head of Procurement with `GV-011` | Before signature |
| 7 | Adopt **`PDoD-01`…`PDoD-07`** as the portal acceptance standard into `UX-008` and `QA-001` | Chief Architect with QA Lead | Before Wave 1 |
| 8 | Add a **device-estate line** to `CO-005` once `PPP-Q-01`, `PPP-Q-02` and `PPP-Q-03` are answered | CFO | Before the Board paper |
| 9 | Correct `SV-005` §5.7's build comparator from 1,513 PW to 1,842 PW — **`CVA-31`** | Service Manager | Next `SV-005` revision |
| 10 | Commission the **`DEP-31` residency opinion** and the **Bangladesh tax opinion** from the `GV-008` §6.3 risk budget — both have long lead times and both gate Wave 1 decisions | Legal Counsel with CFO | **Now** |

---

## 11. Revision History

| Version | Date | Auditor | Change |
|---|---|---|---|
| 1.0 | 2026-08-19 | Enterprise Architecture | Initial issue. Eleven filesystem extractions across six repositories; seventeen tables machine-re-summed; six substantive claims re-executed; six external facts verified. **Ten findings, `CVA-23`…`CVA-32`; nine fixed before issue, one referred to `SV-005`.** Confirms `CVA-02` and `CVA-09` against the RFP source text. `PGD-000` reconciled and moved to v1.9; `README.md` and `FOLDER_STRUCTURE.md` reconciled |

---

*`PGD-AUDIT-CAT-14` · Category 14 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
