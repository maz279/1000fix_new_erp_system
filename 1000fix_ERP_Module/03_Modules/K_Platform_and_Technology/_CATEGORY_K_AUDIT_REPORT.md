---
id: FIX-ERP2-CAT-K-AUDIT
title: Category K Specification Audit Report
category: K — Platform & Technology
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: COMPLETE
classification: CONFIDENTIAL — Internal Use Only
auditor: Specification authoring pass, self-audit
scope: M28, M29, M30, M64, M65, M66, M67
---

# Category K — Specification Audit Report

**Mandatory audit following creation of all seven Category K module specifications.**

> **Audit advantage over Category E.** When Category E was audited, only five sibling module
> specifications existed, so 38 outbound boundary claims could not be verified. Categories A–J
> were written in parallel during this session and **all 19 counterpart modules referenced by
> Category K now exist**. This audit therefore performs **real cross-category boundary
> verification**, which surfaced three conflicts that a within-category audit could not have
> found.

---

## 1. Audit Scope & Method

| Check | Method |
|---|---|
| Structural conformance | Section count and heading sequence against the M03/M33 house pattern |
| Frontmatter integrity | Field-by-field comparison against `02-02` §2 Category K |
| Requirement ID integrity | Contiguity, uniqueness, prefix correctness, declared-versus-actual count |
| Custom-development ID integrity | Ownership collision detection across Category K **and against Category E's block** |
| Role reference validity | Every `Rnn` checked against `05-04` §1 |
| Module reference validity | Every `Mnn` checked against `02-02` §2 |
| File reference validity | Every `*.md` reference resolved on disk |
| **Boundary symmetry — intra-category** | All 7 × 7 pairs: every §3.2 deferral checked for a reciprocal §3.1 claim |
| **Boundary symmetry — cross-category** | **All 19 counterpart modules checked for reciprocity** |
| Category obligation coverage | Every promise, KPI and risk in `_CATEGORY_OVERVIEW.md` traced to an owner |
| Cross-cutting conformance | NFR, AS, OPS, DI, IP, API and EA obligations traced |

---

## 2. Deliverables Produced

| File | Module | Lines | Reqs | Rules | Automations | Entities | Events | AC |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `M28_Integration_API_and_Event_Platform.md` | M28 `IPF` | 903 | 57 | 22 | 20 | 20 | 15 | 23 |
| `M29_Identity_Access_and_Information_Security.md` | M29 `SEC` | 992 | 52 | 25 | 25 | 20 | 21 | 27 |
| `M30_Platform_Administration_and_Configuration.md` | M30 `ADM` | 956 | 40 | 23 | 25 | 26 | 24 | 24 |
| `M64_Master_Data_Management_and_Configuration.md` | M64 `MDM` | 925 | 34 | 22 | 20 | 22 | 19 | 24 |
| `M65_Multi_Entity_Multi_Country_and_Localisation.md` | M65 `GLO` | 963 | 36 | 20 | 21 | 24 | 19 | 25 |
| `M66_Internal_IT_Service_Management.md` | M66 `ITS` | 1,009 | 30 | 22 | 26 | 22 | 19 | 24 |
| `M67_Project_Program_and_Portfolio_Management.md` | M67 `PPM` | 964 | 32 | 22 | 24 | 24 | 19 | 24 |
| **Total** | **7 modules** | **6,712** | **281** | **156** | **161** | **158** | **136** | **171** |

---

## 3. Checks Passed

| # | Check | Result |
|---|---|---|
| P-01 | **Structural conformance** — full 19-section house structure | ✅ 19/19 in every file |
| P-02 | **Frontmatter vs register** — code, priority, wave, business owner | ✅ 7/7 exact match to `02-02` §2 |
| P-03 | **FR ID contiguity** — no gaps in any range | ✅ 0 gaps across 281 requirements |
| P-04 | **FR ID uniqueness and prefix** | ✅ No duplicates; all use the register's allocated code |
| P-05 | **Declared vs actual requirement count** | ✅ 7/7 match |
| P-06 | **CD ID collisions** — within K and against Category E's CD-139…156 | ✅ None; ownership disjoint (see §5) |
| P-07 | **Role reference validity** — 22 distinct `Rnn` referenced | ✅ All exist in `05-04` §1 (R39/R40 appear only as a labelled *proposal*) |
| P-08 | **Module reference validity** — 65 distinct `Mnn` referenced | ✅ All exist in `02-02` §2 |
| P-09 | **File reference validity** — 47 distinct `*.md` referenced | ✅ 42 resolve; 5 are portal specs not yet written (see A-07) |
| P-10 | **Boundary symmetry — intra-category** — all 7 × 7 pairs | ✅ Every deferral reciprocated |
| P-11 | **Boundary symmetry — cross-category** — 19 counterpart modules | ⚠️ **16 clean, 3 conflicts** (see §4) |
| P-12 | **Platform contract coverage** — the 7 promises in `_CATEGORY_OVERVIEW.md` §7 | ✅ All 7 claimed by their named owner |
| P-13 | **Category KPI coverage** — the 21 KPIs in §9 | ✅ All 21 claimed by their named module |
| P-14 | **Category risk coverage** — the 7 risks in §11 | ✅ All 7 addressed by a named control |
| P-15 | **Country pack coverage** — the 9 components in §8 | ✅ All 9 modelled in M65 FR-GLO-008 and FR-GLO-012 |
| P-16 | **Architecture standards** — AS-01…AS-15 | ✅ Each traced to an enforcing module and a CI check |
| P-17 | **Operability standards** — OPS-01…OPS-08 | ✅ All 8 implemented in M30 |
| P-18 | **Integration principles** — IP-01…IP-10, API-01…API-12 | ✅ All traced to M28 requirements |
| P-19 | **PDPA 2026 obligations** — NFR-090…NFR-099, NFR-086a–c | ✅ Split between M29 (enforcement), M33 (consent), M60 (notification), M65 (jurisdiction rule) |
| P-20 | **SoD and external access** — SOD-01…SOD-12, EA-01…EA-12 | ✅ Enforcement claimed by M29; consumed correctly by M64, M66, M67 |

### P-11 detail — cross-category reciprocity verified

| Counterpart | Its reciprocal claim | Category K side | Status |
|---|---|---|---|
| **M63** Process Automation | §3.1 claims the workflow engine, approval routing and business-rule repository; §3.2 defers "Parameter storage and master data → **M64**" | M28 §3.2, M64 §3.2 | ✅ |
| **M60** GRC | §3.2: "Enforcement of access rules, SoD and permissions at runtime → **M29**. M60 defines and tests; M29 enforces" | M29 §3.2 | ✅ **Exact** |
| **M33** Party Master | Owns consent, transparency notice, data-subject rights, `cd_consent` | M29 §3.2, M64 §3.2 | ✅ |
| **M37** Catalogue | §3.2: "Master-data workflow engine, survivorship and golden-record rules → **M64**. M64 provides the governance machinery; M37 is its largest tenant" | M64 §3.2 | ✅ **Exact** |
| **M62** Data Platform | §3.2: "Master data authorship, golden records, survivorship and match/merge rules → **M64**" | M64 §3.2 | ✅ **Exact** |
| **M51** Tax | Owns the Bangladesh tax engine, Mushak forms, registers, returns and withholding | M65 §3.2 | ✅ |
| **M56** Payroll | Owns payroll calculation and statutory compliance | M65 §3.2 | ✅ |
| **M54** FP&A / **M19** GL | Own consolidation execution and the ledger | M65 §3.2 | ✅ |
| **M55** Workforce | "publishes the availability" — the authoritative source | M67 §3.2, BRU-PPM-08 | ✅ **Exact** |
| **M22** Certification | Owns certification status | M67 §3.2 | ✅ |
| **M08** Contracts / **M20** Receivable | Own the contract and the invoice; M20 uses "billable event" throughout | M67 §3.2, BRU-PPM-02 | ✅ |
| **M05** Managed Services | §3.2: "1000FiX's own internal IT support → **M66**" | M66 §3.2 | ✅ **Exact** |
| **M21** Core HR | §3.2: "Employee IT assets → **M66**"; FR-HCM-039 emits JML events | M66 §3.2, M29 §5.3 | ⚠️ **See F-02** |
| **M45** Enterprise Asset | §3.1 claims "every company-owned tool, instrument, **IT asset**…"; §3.2 defers only the service desk, licences and builds to M66 | M66 §3.1, §3.2 | ❌ **See F-01** |
| **M06** Data Services | No reciprocal claim for M66's destruction gate | M66 BRU-ITS-14 | ⚠️ **See F-03** |
| **M18** E-Waste | Owns certified disposal | M66 §3.2 | ✅ |
| **M01** / **M02** / **M31** | Own service orders and work orders | M67 §3.2, BRU-PPM-01 | ✅ |

---

## 4. Conflicts Found — Cross-Category

> **These are not defects in the Category K files.** Each is a genuine two-sided disagreement
> between Category K and a module in another category. **I have not edited files outside
> Category K**, because Categories A–J were being written in parallel during this session and
> unilateral edits would risk colliding with that work. Each finding states the conflict, the
> governing authority, and a recommended resolution.

| ID | Sev | Conflict | Governing authority | Recommended resolution |
|---|:--:|---|---|---|
| **F-01** | **High** | **M45 and M66 both claim company IT assets.** M45 §3.1 item 1 claims "every company-owned tool, instrument, **IT asset** and item of branch equipment", item 2 lists "IT asset" as a classification, and its purpose names "laptops, phones, scanners, printers". M66 §3.1 items 13–17 claim the IT asset register and lifecycle for exactly those items. M45 §3.2 defers only "internal IT service desk, software licences and endpoint configuration" to M66, drawing the line at *"M45 owns the IT asset as a physical, custodied, retired object; M66 owns the ticket, the licence and the build"* | **`_CATEGORY_OVERVIEW.md` §6 is explicit**: "Internal employee IT support and company IT assets → **M66** — **not M05, not M45**" | **Resolve in favour of M66** per the category boundary map, and amend M45 §3.1 to exclude IT assets. *Alternative*: if the M45 split (physical custody vs service) is preferred on delivery grounds, `_CATEGORY_OVERVIEW.md` §6 must be amended and M66 §3.1/§5.5 narrowed. **Either way both sides and the overview must be changed together — the current state has two owners for ~2,500 laptops and phones** |
| **F-02** | **Medium** | **Leaver revocation window disagreement.** M21 FR-HCM-039 states access is "**revoked within 24 hours** of exit". M29 BRU-SEC-06, `05-05` §11 and `05-04` §9 all state **within one hour** | `05-05` BRU-SEC-06 and `05-04` §9 §Deprovision both say **1 hour**; the *24-hour* figure in `_CATEGORY_OVERVIEW.md` §9 is the **zero-orphaned-accounts** measure, a different thing | **Correct M21 FR-HCM-039 to one hour.** The 24-hour figure appears to be a misreading of the orphaned-account KPI. M29 §5.3 FR-SEC-029, AUT-SEC-03 and AC-08 are all built to the one-hour rule |
| **F-03** | **Medium** | **Unreciprocated destruction gate.** M66 BRU-ITS-14 and AC-16 make an M06 data destruction certificate a hard precondition for IT asset disposal. M45 §3.2 makes the same assumption ("An IT asset being retired routes to M06 for erasure"). **M06 references neither M45 nor M66** | RG-04 requires the receiving module to claim the capability | **Amend M06 §3.1/§12.2 to claim certificate issuance for internal asset retirement**, serving both M45 and M66 as consumers. Without it, two modules depend on a gate nobody has undertaken to provide |
| **F-04** | **Low** | **M63 mis-states the SoD ownership chain.** M63 §3.3 records "Segregation of duties — Enforces in routing — **M29 defines**". M29 and M60 both state that **M60 defines and tests, M29 enforces** | `_CATEGORY_OVERVIEW.md` §6: "Segregation-of-duties enforcement → **M29** — M60 (defines and tests the rules)"; M60 §3.2 agrees verbatim | **Correct M63 §3.3** to "M60 defines; M29 enforces; M63 applies within routing." A three-actor chain recorded as two actors will produce an ownership gap during build |

**No conflicts were found within Category K itself** — all 7 × 7 intra-category boundary pairs
reciprocate correctly.

---

## 5. Custom-Development ID Allocation

No collisions within Category K, and none against **Category E's CD-139…156 block**. IDs remain
**provisional** pending the unified CD register required by audit finding **M-01** in `02-05`.

| Module | CD IDs owned | Provenance |
|---|---|---|
| M28 | CD-125 … CD-129 | All five retained from `02-05` §5.2 unchanged |
| M29 | CD-130 … CD-132, **CD-157, CD-158** | Three retained; two new for the v2.1 PDPA and split-residency extension |
| M30 | CD-133, CD-135, CD-138, **CD-159** | Three retained; one new for the job registry |
| M64 | **CD-134**, **CD-160, CD-161** | CD-134 `cd_mdm` **reallocated from M30**; two new |
| M65 | **CD-136, CD-137**, **CD-162** | CD-136 `cd_locale_pack` and CD-137 `cd_country_pack` **reallocated from M30**; one new |
| M66 | **CD-163, CD-164** | New; M66 did not exist in the 30-module register |
| M67 | **CD-165 … CD-167** | New; M67 did not exist in the 30-module register |

**Reallocations within Category K:** M30 surrendered CD-134 to M64 and CD-136/137 to M65,
reflecting the v2.1 split of master data governance and localisation out of platform
administration. This matches the entity reallocation in `05-02` §M30 (17 entities → 12 retained,
2 to M64, 3 to M65).

---

## 6. Cross-Cutting Obligation Coverage

| Obligation set | Source | Coverage |
|---|---|---|
| **Platform contract, 7 promises** | `_CATEGORY_OVERVIEW.md` §7 | 1, 2 → M28 · 3, 4 → M29 · 5 → M30 + M65 · 6 → M64 + M63 · 7 → M65. **7/7** |
| **Category KPIs, 21 metrics** | §9 | M28 ×6 · M29 ×5 · M64 ×2 · M65 ×3 · M30 ×2 · M66 ×2 · M67 ×1. **21/21** |
| **Category risks, 7** | §11 | Point-to-point mesh → M28 BRU-IPF-01/T-15 · identity defect → M29 §5.2/AC-04 · governance bypassed → M64 BRU-MDM-01/T-01 · multi-country retrofit → M65 §16.3 W1 obligations · platform bottleneck → M28 FR-IPF-057 · WhatsApp IT → M66 §2 · spreadsheet projects → M67 §2. **7/7** |
| **Country pack, 9 components** | §8 | M65 FR-GLO-008, FR-GLO-012. **9/9** |
| **Architecture standards AS-01…15** | `05-06` §12 | AS-01/07/08 → M28 · AS-02/14 → M29 · AS-03/12 → M30 + M65 · AS-10/11 → M65 · AS-13 → M28 · AS-05/06/09/15 → cross-cutting. **15/15** |
| **Operability OPS-01…08** | `05-06` §7 | All eight → M30 §5.2–§5.6. **8/8** |
| **Integration IP-01…10, API-01…12** | `05-03` §1, §5.2 | All → M28 §5.1–§5.7. **22/22** |
| **Data integrity DI-01…08** | `05-06` §8 | DI-03/06 → M64 · DI-04/05/07 → M28 · DI-01 → M65 · DI-08 → M30. **8/8** |
| **PDPA 2026 NFR-090…099** | `05-06` §6.3 | 090–092 → M33 · 093 → M33 + M29 · 094 → M60 + M29 · 095 → M24 + M29 · 096 → M60 · 097 → M29 · 098 → M42 + M60 · 099 → M29 + M65. **10/10** |
| **Split residency NFR-086, 086a–c** | `05-06` §6.4 | M65 defines (FR-GLO-015); **M29 enforces** (FR-SEC-047…050). **4/4** |
| **Localisation standard** | `05-06` §9 | M65 §5.3, FR-GLO-020…028. **Full** |
| **47 external integrations** | `05-03` §2 | M28 owns the register and connector shape (FR-IPF-039, FR-IPF-055); business meaning stays with the named module. **47/47** |

---

## 7. Findings Raised for Programme-Level Action

Not defects in the seven specifications — consequences of writing them, each requiring a change
outside Category K.

| ID | Sev | Finding | Owner | Action Required |
|---|:--:|---|---|---|
| **A-01** | **High** | **Register figures superseded.** `02-02` §2 estimates Category K at **220 requirements / 124 PW**. Measured totals are **281 / 151 PW** — +28% and +22%. Combined with Category E (+43 reqs / +17 PW), the programme totals in `02-02` §3 are materially understated | CTO / Architect | Update `02-02` §2 Category K rows and §3 totals; mark Category K measured; set Spec 7/7 |
| **A-02** | **High** | **`05-01` §1.3 FR ranges superseded for two modules.** The register allocates FR-IPF-001…058, FR-SEC-001…044 and FR-ADM-001…035. **M29 measured 52 (exceeds 44)** and **M30 measured 40 (exceeds 35)**, both extending into the documented headroom (045–065 and 036–050). M28's 57 fits within its 58. Ranges for M64, M65, M66 and M67 were **newly allocated** under `05-01` §1.3a | CTO / Architect | Update `05-01` §1.3 to the measured ranges and record the four new allocations |
| **A-03** | **High** | **KPI register has no platform section.** `06-02` §2.6 ends at KPI-049. **All 122 metrics across the seven files carry `—`**, including the 21 named as category KPIs in `_CATEGORY_OVERVIEW.md` §9. Category E raised the same finding for ~60 metrics | CFO / Architect | Allocate KPI-060+ and add platform, security, data-governance, localisation, ITSM and project sections to `06-02` |
| **A-04** | **High** | **`05-04` role register is a 30-module artefact and does not carry the roles the 67-module architecture implies.** Four gaps identified across two categories: **Demand Planner** (Category E), **Data Steward** (M64), **IT Service Desk agent** (M66), **Project Manager** (M67). A fifth — *module developer / platform engineer* — is implied by M28's self-service model. Each is currently a grant layered on an existing business role, which weakens least privilege and leaves accountability unnamed | HR Director / CTO | **A `05-04` refresh is now the better answer than four individual additions.** Recommend a single review pass adding R39+ for the missing functions |
| **A-05** | **Medium** | **Unified CD register still missing.** `02-05` audit finding M-01 remains open. Category K claims CD-157…167 and reallocates CD-134, CD-136 and CD-137 across module boundaries; Category E claims CD-139…156 | CTO | Produce the unified CD register covering all 67 modules; ratify or renumber |
| **A-06** | **Medium** | **DEP-31 blocks the Wave 1 architecture.** `05-06` §6.4 states the split-residency legal opinion is required **before the Wave 1 architecture is fixed**, and NFR-086a puts residency enforcement in the platform — so the answer changes the data model, not a configuration. M29 cannot be built to a final design without it | Legal / CTO | Obtain the DEP-31 opinion. **This is the single most time-critical external dependency in Category K** |
| **A-07** | **Medium** | **P01–P07 portal specifications are filed in `03_Modules/K_Platform_and_Technology/`.** Per `FOLDER_STRUCTURE.md` and the existing `04-00_Portal_Suite_Overview.md`, portal specs belong in `04_Portals_and_Applications/`, which currently holds only the overview. P08–P12 do not yet exist anywhere | CTO / Architect | **Relocate P01–P07 to `04_Portals_and_Applications/`.** Not actioned here: those files were being written during this session and moving them would risk collision |
| **A-08** | **Medium** | **PDPA localisation scope may be narrower than NFR-086 assumes.** Research for M29 found that **Amendment Ordinance No. 23 of 2026 (5 February 2026) narrowed data localisation to *restricted* and *critical information infrastructure* data**. The residency-classified field list in `05-06` §6.4 may therefore be broader than the statute now requires — narrowing it would materially reduce architectural cost | Legal / CTO | Verify against the current statute and re-scope NFR-086 if confirmed. Tracked as **M29 Q-01** |
| **A-09** | **Medium** | **Regulator name unconfirmed.** `05-06` §6.3 names the **National Data Management Authority**; external sources describe a **Data Protection Office / Board**. The breach-notification channel and format depend on which is correct | Legal / M60 owner | Confirm and correct `05-06` §6.3. Tracked as **M29 Q-04** |
| **A-10** | **Low** | **M28's effort estimate covers the framework only.** The 30 PW covers the platform framework and W1–W2 integrations. The remaining **40 of 47 integrations** are delivered across W3–W9 and are costed with their owning modules. Reading 30 PW as the total cost of integration would understate the programme | CTO / Programme Manager | State the convention explicitly in `02-02` and `06-01`. Tracked as **M28 Q-10** |
| **A-11** | **Low** | **Three deferred ownership hand-offs must be scheduled, not discovered.** M30 ships in W1 holding capabilities that transfer to **M64 (W2 — business parameters)**, **M66 (W6 — the change process)** and **M65 (W9 — locale, country pack, translation)**. Each is a migration of live configuration | CTO | Schedule each hand-off in `06-01`. Tracked as **M30 Q-10**, **M64 Q-01/Q-07** |

---

## 8. Design Positions Recorded

Six positions material enough that reversing them would change the architecture.

| # | Position | Module | Consequence if Reversed |
|---|---|---|---|
| D-01 | **The transactional outbox is mandatory estate-wide; no module publishes an event from business logic** (AS-08, BRU-IPF-02) | M28 | Business writes and their events diverge; downstream systems observe incomplete state. This is the pattern the whole event architecture rests on |
| D-02 | **M28 contains no business logic and imports no business module; workflow lives in M63** (BRU-IPF-20, verified by dependency analysis) | M28 | The integration layer accumulates business rules and becomes an unmaintainable ESB — the outcome the 67-module architecture exists to avoid |
| D-03 | **Authorisation is evaluated inside the transaction, not only at the API edge**; audit is inherited by base-model inheritance and cannot be opted out of | M29 | An edge-only permission check is one crafted request from a cross-branch data exposure — rated **Critical** in the category risk register |
| D-04 | **Residency is a field-level classification enforced at write time**, not an operational convention (NFR-086a) | M29 | PDPA exposure up to **BDT 50 lakh**, and a retrofit of the data model after Wave 1. Gated on **DEP-31** |
| D-05 | **The stewardship workflow is the only path to governed master data; direct edits are blocked in the ORM** (BRU-MDM-01) | M64 | Governance becomes advisory, is routed around, and "the system runs perfectly on wrong data" — the category's own words |
| D-06 | **M65 delivers in W9 but its design obligations bind Waves 1–8** — no jurisdiction literals, dimensions on every model, Bangladesh as pack `BD` v1, 100% translation gating (§16.3 W1-A…W1-G) | M65 | Retrofitting multi-country costs **3–5×** designing for it — the category's stated risk. Every module built without the country dimension must be rewritten |

---

## 9. Audit Conclusion

| Question | Answer |
|---|---|
| Are all seven specifications complete? | **Yes.** 19/19 sections each; 281 requirements; every category promise, KPI, risk and country-pack component claimed |
| Do they conform to the house structure? | **Yes.** Verified against the M03 and M33 precedents |
| Are they internally consistent? | **Yes.** All 7 × 7 intra-category boundary pairs reciprocate; no fixes were required within Category K |
| Are they consistent with the governing documents? | **Yes** for `02-02`, `05-01`, `05-02`, `05-03`, `05-04`, `05-05`, `05-06` and `_CATEGORY_OVERVIEW.md`. Eleven findings (A-01…A-11) require changes to those documents, not to these seven |
| Is boundary symmetry satisfied? | **Within Category K, yes.** **Across categories, 16 of 19 counterparts reciprocate cleanly; three conflicts (F-01…F-03) and one mis-statement (F-04) require resolution outside Category K** |
| Can these files be issued for approval? | **Yes**, subject to F-01 being resolved before M66 build. Status `DRAFT FOR APPROVAL` on all seven, consistent with precedent |

**Blocking before Wave 1 architecture is fixed:** A-06 (DEP-31 split-residency legal opinion) —
M29's data model depends on it. A-08 may narrow its scope.

**Blocking before Wave 1 build:** F-04 (SoD ownership chain) — a three-actor chain recorded as
two will produce an ownership gap between M60, M29 and M63.

**Blocking before Wave 5 build:** F-02 (leaver revocation window) — M21 and M29 must agree
before joiner–mover–leaver automation is built.

**Blocking before Wave 6 build:** F-01 (M45/M66 IT asset ownership) and F-03 (M06 destruction
gate) — M66 cannot be built against a contested asset register or an unclaimed dependency.

**Not blocking but should be actioned now:** A-04 — the `05-04` role register needs a single
refresh pass rather than four separate additions, and the gap is now visible across two
categories.

---

*Category K Audit Report · 1000FiX ERP System v2.0 · CONFIDENTIAL*
