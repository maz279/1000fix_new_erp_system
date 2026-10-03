---
id: FIX-ERP2-CAT-F-AUDIT
title: Category F Module Specification Audit Report
category: F — Asset, Equipment & Facilities
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: FINDINGS ISSUED — REGISTER UPDATES REQUIRED
classification: CONFIDENTIAL — Internal Use Only
auditor: Enterprise Architecture
scope: M17, M45, M46, M47, M48 as issued 2026-08-13
---

# Category F — Module Specification Audit Report
### Five module files · 4,841 lines · 471 KB

---

## 1. Purpose and Method

This audit examined the five Category F module specification files issued on 2026-08-13
against the governance rules in `02-02` §1, the category boundary map in
`_CATEGORY_OVERVIEW.md`, the house template in `_MODULE_TEMPLATE.md`, and the sibling
specifications already issued in Categories A–E.

Four methods were applied.

| Method | What Was Checked |
|---|---|
| **Structural consistency** | Section completeness against the house structure; frontmatter against the master register; filename convention against siblings |
| **Identifier integrity** | FR, BRU, AUT, T-, AC- and CD identifier continuity, uniqueness, gaps and collisions — within each file, across Category F, and against Categories A–E |
| **Boundary symmetry (RG-04)** | Every out-of-scope claim checked for a reciprocal claim in the owning module; every claim made *against* Category F by an already-issued module checked for reciprocation here |
| **Arithmetic and evidence** | Layer allocation totals; requirement and effort roll-ups; every regulatory and standards claim checked against a primary or authoritative secondary source; every `OOS-n` reversal checked against the BRD text |

**Result: 0 critical, 0 high, 6 medium and 3 low findings.** One defect was found and
corrected during the audit. The six medium findings are all **register updates required in
documents outside Category F** — they are consequences of these specifications being the first
measured statement of scope for four new modules, not defects within them.

---

## 2. Findings Summary

| Severity | Count | Definition |
|---|---:|---|
| **Critical** | 0 | Would cause an incorrect decision, legal exposure, or a build against the wrong specification |
| **High** | 0 | Materially misleading or missing; caught in build but at cost |
| **Medium** | 6 | Register or cross-document updates required before these files can be treated as authoritative |
| **Low** | 3 | Precision improvements and decisions to be confirmed |
| **Corrected during audit** | 1 | Found and fixed before issue |
| **Total** | **10** | |

---

## 3. Checks Passed

| # | Check | Result |
|---|---|---|
| P-01 | All 19 house sections present, in order, in all five files | **Pass** — matches the structure of `M15` and `M13` |
| P-02 | Frontmatter module ID, code, priority, wave and business owner match `02-02` §2 Category F | **Pass** — 5/5 exact (role titles expanded, e.g. "CTO" → "Chief Technology Officer") |
| P-03 | Filename convention matches Categories A–E | **Pass** — `M<nn>_<Name>.md` |
| P-04 | FR identifier ranges contiguous, no gaps, no duplicate definitions | **Pass** — 232 requirements across five modules, zero gaps |
| P-05 | Declared requirement range and count match the requirements actually specified | **Pass** — 5/5 |
| P-06 | BRU, AUT and T- identifiers unique within each module | **Pass** — 110 business rules, 98 automations, 79 technical functions |
| P-07 | Acceptance-criteria count matches the definition-of-done statement | **Pass** — 5/5 (22, 22, 23, 23, 27) |
| P-08 | CD identifiers unique within Category F | **Pass** — 22 components, no duplicates |
| P-09 | CD identifiers do not collide with any allocation in Categories A–E | **Pass** — CD-157…173 claimed cleanly after CD-156, the highest ID claimed by Category E |
| P-10 | The Category F CD block statement is identical in all five files | **Pass** — each file states the full block; M48 marks it complete and names CD-174 as next free |
| P-11 | §16.1 layer allocation totals 100% | **Pass** — 5/5 |
| P-12 | Every internal document cross-reference resolves to a file that exists | **Pass** — the only unresolved reference is `06-02`, correctly and repeatedly flagged as *not yet issued* |
| P-13 | All 14 category KPI targets in `_CATEGORY_OVERVIEW.md` §7 are adopted verbatim by their owning module | **Pass** — 14/14 |
| P-14 | All 15 boundary-map assignments in `_CATEGORY_OVERVIEW.md` §5 are claimed by the module named | **Pass** — 15/15 |
| P-15 | Claims made against Category F by issued modules (M01–M06, M31, M07, M33, M37, M13, M15) are reciprocated | **Pass** after correcting **X-01** below |
| P-16 | No module declares a dependency on itself | **Pass** |
| P-17 | Every `OOS-n` reversal claim matches the BRD text | **Pass** — OOS-4 (M46), OOS-5 (M47), OOS-6 (M48) verified verbatim at BRD §4.2 lines 312–314 |
| P-18 | Every regulatory and standards claim traced to a source cited in §19 | **Pass** — ISO 9001 clause 7.1.5 and 7.1.3, ISO/IEC 17025, ISO 55001, ISO 13374, ISO 17359, ISO 15143-3, IFRS 16, BRTA fitness and tax token, FSCD fire licence and its trade-licence dependency |
| P-19 | Architecture standards AS-01, AS-03, AS-08, AS-12, AS-13, AS-14 addressed in §6 of each module | **Pass** |
| P-20 | Cross-module technical positions held consistent | **Pass** — the ISO 15143-3 telematics interface shape is stated identically in `M13` §6 T-11, `M46` §6 T-03 and `M48` §4 |

---

## 4. Defect Found and Corrected

### X-01 — M45 did not reciprocate an event M31 publishes to it

**Severity: Medium (as found) · Status: CORRECTED before issue · Type: Boundary asymmetry**

`M31_Workshop_and_Depot_Repair_Management.md` §12.3 publishes
`equipment.calibration_exception` with consumers listed as **M45, M23**. The first draft of
`M45` §12.1 named M31 only as a source of "internal repair progress and completion" and did not
name the calibration-exception event. Under rule **RG-04 (boundary symmetry)** a declared
consumer must claim what it consumes.

**Correction applied.** `M45` §12.1 now carries an explicit row:

> `| M31 Workshop | Instrument used on a repair, and any attempted use of an unfit instrument | Event equipment.calibration_exception (declared in M31 §12.3) |`

No change was required in `M31`.

---

## 5. Medium Findings — Register Updates Required

These are not defects in the Category F files. Each is a consequence of these specifications
being the **first measured statement of scope** for one re-scoped and four new modules, and each
requires an update to a document outside this category. All five module files record their own
share of these as an audit action in the relevant section.

### M-01 — Category F requirement and effort totals in `02-02` are superseded

**Owner: Enterprise Architecture · Target: `02_Architecture/02-02` §2 Category F**

The register carries estimates marked *(est.)*, which rule **RG-05** states must not be used
for contractual commitment. Measurement supersedes them.

| Module | Register *(est.)* | Measured | Δ reqs | Δ effort |
|---|---|---|---:|---:|
| M17 | 34 reqs · 18 PW | **52 reqs · 26 PW** | +18 | +8 PW |
| M45 | 26 reqs · 14 PW | **46 reqs · 22 PW** | +20 | +8 PW |
| M46 | 24 reqs · 12 PW | **44 reqs · 20 PW** | +20 | +8 PW |
| M47 | 22 reqs · 11 PW | **44 reqs · 20 PW** | +22 | +9 PW |
| M48 | 28 reqs · 18 PW | **46 reqs · 26 PW** | +18 | +8 PW |
| **Category F** | **134 reqs · 73 PW** | **232 reqs · 114 PW** | **+98** | **+41 PW** |

The increase is consistent in shape with the M15 precedent (48 → 54 reqs, 24 → 27 PW) but
larger in proportion, because four of the five modules were estimated before any specification
existed. The programme total in `02-02` §3 requires recomputation.

**This finding is material to the delivery plan and should be resolved before Wave 5 planning.**

### M-02 — `05-01` requirement-prefix allocations required for four new modules

**Owner: Enterprise Architecture · Target: `05_Cross_Cutting_Specifications/05-01`**

`05-01` allocates `FR-AST-001…042` to M17 with `043–065` reserved. M17 now specifies **52**
requirements, which sits inside the reserved block — no conflict, but the allocation line must
be updated.

`05-01` carries **no allocation at all** for `EAM`, `FLT`, `FAC` or `IOT`. The four prefixes are
used here on the authority of the code assignments in `02-02` §2 and the code table at `02-02`
§293–296, and require formal allocation:

| Prefix | Module | Range used | Suggested reservation |
|---|---|---|---|
| `EAM` | M45 | FR-EAM-001…046 | 047–070 |
| `FLT` | M46 | FR-FLT-001…044 | 045–065 |
| `FAC` | M47 | FR-FAC-001…044 | 045–065 |
| `IOT` | M48 | FR-IOT-001…046 | 047–070 |

> Rule **RG-01 (register-first)** states that no module specification may be created until its
> requirement range is allocated in `05-01`. These four files were created ahead of that
> allocation. This is recorded here rather than concealed; the allocation is a formality given
> the codes are already permanent under RG-02, but the sequence was not followed.

### M-03 — `05-02` entity allocations must be split across four modules

**Owner: Enterprise Architecture · Target: `05_Cross_Cutting_Specifications/05-02` §M17 AST**

`05-02` lists 18 owned entities under M17, of which eight belong elsewhere under the v2.1
re-scope:

| Entity in `05-02` under M17 | Correct owner | Recorded in |
|---|---|---|
| `fix.brand`, `fix.model` | **M37** Catalogue | `M17` §10.2 note |
| `fix.calibration.record`, `fix.tool.register` | **M45** | `M17` §10.2 note · `M45` §10.1 |
| `fix.telemetry.stream`, `fix.telemetry.point` | **M48** | `M17` §10.2 note · `M48` §10.1 |
| `fix.asset.health`, `fix.failure.prediction` | **M48** | `M17` §10.2 note · `M48` §10.1 |

M17 now specifies 23 owned entities, M45 17, M46 21, M47 27 and M48 18 — **106 entities across
Category F**, against 18 currently registered. `05-02` requires substantial extension.

### M-04 — CD register reallocations and new claims require ratification

**Owner: Enterprise Architecture · Target: `02_Architecture/02-05` §5.2**

| Action | Detail |
|---|---|
| **Reallocated** | CD-078 `cd_telemetry` and CD-079 `cd_asset_health` move **M17 → M48**, retaining their IDs |
| **Retained** | CD-075 `cd_asset_registry`, CD-076 `cd_asset_estate`, CD-077 `cd_maintenance_plan` stay with M17 |
| **Newly claimed** | **CD-157…173** (17 IDs) from the extension block reserved for M31–M67 |
| **Next free ID** | **CD-174** for any category specified after this one |

All CD IDs remain provisional pending the unified CD register required by audit finding **M-01
in `02-05`**. No collision exists with any ID claimed by Categories A–E (verified
mechanically).

### M-05 — "Branch Operations Lead" is named as a business owner but is not in the role register

**Owner: Enterprise Architecture · Target: `05_Cross_Cutting_Specifications/05-04` §1**

`02-02` §2 names **Branch Operations Lead** as the business owner of both **M04** and **M47**,
and `M47` §13 assigns it estate-wide create, read, update, delete and approve rights — the
broadest scope in that module. The role does not appear in the 38-role register at `05-04` §1.

It requires either a new role ID or an explicit mapping to an existing role. `M47` §13 records
this inline. **This is a permissions gap, not a documentation nicety**: the module's most
privileged role is currently undefined.

### M-06 — Category F KPIs require identifier allocation

**Owner: Enterprise Architecture · Target: `06-02` (not yet issued)**

None of the five modules has a `KPI-0nn` identifier allocated. **69 unnumbered metrics** are
specified across the five modules, of which the 14 category-level targets in
`_CATEGORY_OVERVIEW.md` §7 are adopted verbatim. Existing numbered KPIs (KPI-004, KPI-011,
KPI-041) are cited as **supported**, never claimed — the M15 convention.

`06-02_KPI_Benefits_and_Acceptance_Criteria.md` is referenced by `M15` and by all five Category
F files but **does not exist in the repository**. Until it is issued, no module can allocate a
KPI identifier, and this finding will recur for every category.

---

## 6. Low Findings

### L-01 — Five modules carry no line in the Scope Charter benefit register

**Severity: Low · Type: Traceability**

`00-02` §6.2 attributes benefit to M09, M02, M15, M07, M10, M27, M08, M19, M20, M05, M13, M14,
M12, M06, M18 and M11. **No Category F module appears.** This is correct — all five are
enabling, protective or cost-control modules — but it creates a decision hazard: a reader
consulting only the benefit register would conclude Category F returns nothing.

Each file states its dependency explicitly rather than inventing a benefit line. `M17` §7.2 goes
furthest, noting that a decision to descope M17 is visibly a decision to forgo the **BDT 100
lac/year** warranty recovery attributed to M09.

**Recommendation:** add an "enables" column to `00-02` §6.2 rather than fabricating benefit
lines for Category F.

### L-02 — Two deliberate asymmetries between M46 and M47 should be confirmed by their owners

**Severity: Low · Type: Design decision requiring ratification**

| | M46 vehicles | M47 sites |
|---|---|---|
| Document expiry | **Automatic off-road**, no override on insurance | **Operating-risk exception**, no automatic suspension |

The rationale is stated in `M46` §4 and `M47` §4: a vehicle is substitutable within a day, a
branch is not, and automatically suspending a branch would cause more harm than the lapse it
responds to. Both positions are recorded as open questions for explicit sign-off —
`M46` Q-03 (Operations Director / CEO / CFO) and `M47` Q-04 (CEO / Legal / CFO).

**This asymmetry is intentional and defensible, but it must be a decision, not an artefact.**

### L-03 — M48's Wave 8 placement conflicts with M05's Wave 5 need for a time-series store

**Severity: Low as a documentation matter · High as a delivery decision · Type: Sequencing**

`M05` (Wave 5) requires telemetry three waves before `M48` (Wave 8) delivers the platform.
`M05` §16.3 already notes the shared platform; `M48` §16.3 states the resolution explicitly —
the storage layer, schema and retention policy are built at M05's time **under M48's design
authority**, and M48 adds the registry, rules, health scoring and prediction on top of a store
that already exists.

This is raised as `M48` Q-01 and marked *"the single most consequential decision in Category
F"*, needed at **W5 planning**. It is a Low documentation finding because it is correctly
recorded on both sides; it becomes a High delivery risk if the decision is not taken explicitly.

---

## 7. Category-Level Observations

### 7.1 The four-population rule holds

`_CATEGORY_OVERVIEW.md` §1 asserts that conflating asset populations is the classic ERP mistake.
The specifications hold the line mechanically:

| Population | Owner | Enforced by |
|---|---|---|
| Customer devices | M17 | BRU-AST-23, BRU-EAM-18 |
| Company tools and test equipment | M45 | BRU-EAM-17, BRU-EAM-18 |
| Vehicles | M46 | BRU-FLT-22, BRU-FAC-21 |
| Premises and fixed building services | M47 | BRU-FAC-21 |
| Telemetry from any of them | M48 | BRU-IOT-02, BRU-IOT-12 |

Every one of these is a hard-block rule with a named owner, and each appears on **both** sides
of its boundary.

### 7.2 The platform-protection rule is enforced at the right layer

`_CATEGORY_OVERVIEW.md` §9 names telemetry volume overwhelming the transactional database as a
high-impact, platform-wide risk. `M48` implements this as **BRU-IOT-01** (a hard rule),
**T-01** (schema separation asserted in CI) and **AC-01** (a full-database scan plus a build-
failing check). This is the strongest available form of the control — it fails the build rather
than the production system.

### 7.3 The calibration gate is the only wave-gating control in the category

**BRU-EAM-21** makes 100% calibration compliance a **Wave 5 gate criterion**, per
`_CATEGORY_OVERVIEW.md` §6. `M45` §15 flags it, §17 AC-17 requires three consecutive compliant
months before the gate, and §16.4 states the migration position that follows from it: an
instrument without a verifiable certificate enters the register **out of service**.

The audit notes that this places a real, unbudgeted cost on Wave 5 — calibrating every
measurement-critical instrument that cannot produce a certificate. `M45` Q-02 asks for that
number and it is **not yet known**.

### 7.4 Migration positions are consistently strict, and consistently expensive

Four of the five modules take a deliberately strict opening position, each following the M15
precedent that loading unverifiable data makes the target metric permanently unmeasurable.

| Module | Position | Cost |
|---|---|---|
| M17 | Legacy devices load as **provisional** unless carrying a verified identifier | A twelve-month clearance programme on up to 600,000 records |
| M45 | Register established by **physical audit** at every branch; instruments without a verifiable certificate load **out of service** | 51+ site visits plus unplanned calibration |
| M46 | Documents load **with scanned evidence**; without evidence they load **expired** | Vehicles off-road at cutover |
| M47 | Licences and leases load from **physical documents**; infrastructure by **physical survey** | 51+ site surveys |

**`M47` §16.4 and `M45` §16.4 both propose combining the two site surveys into one visit.** The
audit endorses this: scheduled separately they are 102 branch visits, scheduled together they
are 51.

---

## 8. Register Update Worklist

| # | Action | Target document | Owner | Priority |
|---|---|---|---|---|
| 1 | Update Category F requirement and effort totals; recompute programme totals | `02-02` §2, §3 | Enterprise Architecture | **Before Wave 5 planning** |
| 2 | Allocate `EAM`, `FLT`, `FAC`, `IOT` requirement ranges; update the `AST` allocation | `05-01` | Enterprise Architecture | High |
| 3 | Reallocate eight entities out of M17; register 104 Category F entities | `05-02` | Enterprise Architecture | High |
| 4 | Ratify CD-078/079 reallocation and CD-157…173 claims | `02-05` §5.2 | Enterprise Architecture | High |
| 5 | Define or map the **Branch Operations Lead** role | `05-04` §1 | CTO / HR Director | High |
| 6 | Issue `06-02` and allocate KPI identifiers for 57 new metrics | `06-02` | Enterprise Architecture | Medium |
| 7 | Add an "enables" column to the benefit register for enabling modules | `00-02` §6.2 | CFO | Medium |
| 8 | Confirm the M46/M47 enforcement asymmetry as a decision | `M46` Q-03, `M47` Q-04 | CEO / CFO / Ops Director | Medium |
| 9 | Decide the shared time-series store at Wave 5 planning | `M48` Q-01 | CTO | **Wave 5 planning** |
| 10 | Combine the M45 equipment audit and M47 facility survey into one site visit | Wave 5 / Wave 7 plans | Operations Director | Medium |

---

## 9. Open Questions Raised Across Category F

Sixty open questions are recorded across the five modules — twelve per module. Those needing an
answer **earliest**, before their module's own design phase, are:

| Question | Module | Owner | Needed by |
|---|---|---|---|
| Is the shared time-series store built at Wave 5 under M48's design authority? | M48 Q-01 | CTO | **W5 planning** |
| What is the current compliance state of the 51+ site estate? | M47 Q-03 | Branch Ops Lead | **As early as possible** |
| How many devices exist in the legacy system, and what proportion carry a usable serial? | M17 Q-01 | CTO / Ops Director | W1 − 2 months |
| Is the twelve-month provisional-clearance programme a business commitment? | M17 Q-02 | Ops Director / CEO | W1 |
| How many measurement-critical instruments exist, and what is the annual calibration cost? | M45 Q-02 | Quality Mgr / CFO | W5 − 4 months |
| Which ISO/IEC 17025-accredited providers exist in Bangladesh, and is BSTI capacity sufficient? | M45 Q-03 | Quality Mgr / Procurement | W5 − 4 months |
| How many vehicles, of what class, on what ownership basis? | M46 Q-01 | Logistics Mgr | W5 − 4 months |
| What is the consent model for telemetry from customer-owned assets? | M48 Q-04 | CCO / Legal | W8 − 6 months |
| Should the M47 compliance slice be pulled forward ahead of Wave 7? | M47 Q-12 | Ops Director / CEO | **W4 planning** |

---

## 10. Audit Conclusion

The five Category F specifications are **structurally sound, internally consistent, and
consistent with the five module specifications already issued in Categories A–E**. Every
identifier set is clean, every boundary is symmetrical, every category KPI and boundary-map
assignment is honoured, and every regulatory claim is sourced.

One defect was found and corrected. No critical or high finding remains.

The six medium findings are all register updates in documents **outside** Category F, and they
share one cause: four of these five modules were estimated before any specification existed, so
this is the first occasion on which their scope has been measured rather than guessed. The
+98 requirement and +41 person-week delta in **M-01** is the material one and should be resolved
before Wave 5 planning.

Two decisions are flagged as needing explicit sign-off rather than inheritance: the deliberate
M46/M47 enforcement asymmetry (**L-02**) and the shared time-series store at Wave 5 (**L-03**).

**Recommendation: accept the five specifications, and open the ten-item register worklist in
§8.**

---

*Category F Audit · 1000FiX ERP System v2.0 · CONFIDENTIAL*
