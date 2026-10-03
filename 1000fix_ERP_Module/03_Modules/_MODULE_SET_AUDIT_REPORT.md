---
id: FIX-ERP2-00-08
title: Module Set Audit & Remediation Report — 03_Modules
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: FINDINGS ISSUED — REMEDIATION APPLIED
classification: CONFIDENTIAL — Internal Use Only
auditor: Documentation Squad
scope: All 97 files under 03_Modules — 67 module specifications, 12 portal specifications, 11 category overviews, 6 prior audit reports, 1 template
regulatory_verified: 2026-08-13
supersedes: nothing; extends 00-06 and 00-07
---

# Module Set Audit & Remediation Report
### Third audit · `03_Modules` in full · Findings **and** applied corrections

---

## 1. Scope and Method

This audit covers **every file under `03_Modules`** — 97 files, ~75,000 lines, ~6.5 MB.

It differs from the two prior audits in one respect: **every finding below was machine-derived
from the files themselves and re-verified after correction.** Where a prior audit reported a
number, that number was recounted rather than accepted (rule **RG-06**).

### Checks Run

| # | Check | Method |
|---|---|---|
| 1 | Requirement identifier count, contiguity, duplication | Parse every `§5` requirement table row; compare to the count and range declared in `§1` |
| 2 | Requirement counts against `05-01` and `02-02` | Direct count of all 79 specification files |
| 3 | Module code register conformance | Frontmatter and `§1` codes against `02-02` §5 and `05-01` §1.3 |
| 4 | Role identifier integrity | Every `§13` role row against the `05-04` register R01–R38 |
| 5 | KPI, CD and SOD identifier collision | Cross-file identifier index over the whole set |
| 6 | Data-model resolution | Every `§10.2` referenced entity against the declared owner's `§10.1` catalogue |
| 7 | Event contract symmetry | Every `§12.1` consumed event against every `§12.3` published event |
| 8 | Dependency reciprocity (RG-04) | `Depends on` ↔ `Depended on by` in both directions across all 67 modules |
| 9 | Wave ordering | Every declared dependency against both modules' frontmatter wave |
| 10 | Cross-reference validity | Resolve every internal document path in every file |
| 11 | Structural conformance | Section signature of all 79 specifications against the house structure and the template |
| 12 | Regulatory and factual currency | Every statutory, standards and company-fact claim against primary or authoritative secondary sources |

### Result

**23 findings — 4 critical, 7 high, 8 medium, 4 low.**
**19 are fully corrected in this pass. 4 remain open and are escalated.**

The corrections touched **79 of the 97 files**.

---

## 2. Findings Summary

| ID | Severity | Finding | Scale | Status |
|---|:--:|---|:--:|:--:|
| **A3-01** | **CRITICAL** | Requirement counts in five Category A modules were the highest allocated identifier, not a count of requirements | 5 modules, 35 phantom requirements | ✅ **Fixed** |
| **A3-02** | **CRITICAL** | The twelve portal specifications are filed inside a module category folder, and four modules link to where they are not | 12 files + 4 broken links | ⚠ **Documented — relocation decision open** |
| **A3-03** | **CRITICAL** | 255 referenced-entity declarations did not resolve to any entity the named owner defines | 255 references, 67 modules | ✅ **Fixed — 255 → 0** |
| **A3-04** | **CRITICAL** | 15 role identifiers carried two or more different role identities across the set | 41 tokens, 16 modules | ✅ **Fixed** |
| **A3-05** | High | 48 custom-development identifiers are claimed by two or more modules | 33 modules | ⚠ **Made safe — reallocation open (Architecture)** |
| **A3-06** | High | 13 consumed events had no declared publisher anywhere | 13 contracts | ✅ **Fixed** |
| **A3-07** | High | 22 modules are scheduled in a wave earlier than a declared prerequisite | 22 modules, 5 of them P0 | ✅ **Flagged in-file — programme decision open** |
| **A3-08** | High | 48 dependency edges were declared in one direction only | 21 modules | ✅ **Fixed** |
| **A3-09** | High | Five modules stated another module's delivery wave incorrectly | 5 statements | ✅ **Fixed** |
| **A3-10** | High | `05-01` §1.3 still allocates four retired module codes, one of which collides with a live allocation | 4 codes | ⚠ **Open — `05-01` is out of this scope** |
| **A3-11** | High | Ten internal document references pointed at superseded or non-existent filenames | 10 references | ✅ **Fixed** |
| **A3-12** | Medium | `_MODULE_TEMPLATE.md` described a 16-section structure that no specification uses | 1 file vs 79 | ✅ **Fixed** |
| **A3-13** | Medium | Category A overview carried no measured scale table | 1 file | ✅ **Fixed** |
| **A3-14** | Medium | Category K overview omitted the twelve portal specifications in its own folder | 1 file | ✅ **Fixed** |
| **A3-15** | Medium | 33 database tables are declared as *owned* by two or three different modules | 33 tables | ⚠ **Open — data-model decision** |
| **A3-16** | Medium | 12 KPI identifiers are shared between modules | 12 of 247 | ✅ **Verified — 9 annotated, 3 need the register** |
| **A3-17** | Medium | Role identifiers R39–R50 are used but not registered in `05-04` | 12 roles | ⚠ **Open — `05-04` is out of this scope** |
| **A3-18** | Medium | `SOD-13 … SOD-30` are used but never registered | 18 controls | ⚠ **Open — carried from H2-06** |
| **A3-19** | Medium | Role labels drifted from the `05-04` canonical names | 203 tokens | ✅ **Fixed** |
| **A3-20** | Low | `R38` carries 17 distinct external-party identities | 17 sub-types | ⚠ **Open — needs sub-typing in `05-04`** |
| **A3-21** | Low | Frontmatter `status` uses a value the template did not permit | 79 files | ✅ **Fixed in template** |
| **A3-22** | Low | M06 uses sub-identifier `FR-DTS-008b`, undocumented in `05-01` | 1 identifier | ⚠ **Open — trivial** |
| **A3-23** | Low | Two modules retain `<placeholder>` tokens in technical text | 2 files | ⚠ **Open — cosmetic** |

---

## 3. Critical Findings

### A3-01 — Requirement counts were highest-identifier, not counts *(Fixed)*

**What was found.** Five Category A modules declared a requirement count that did not match the
number of requirement rows in the file.

| Module | Declared | **Actual rows** | Gap | Cause |
|---|---:|---:|---:|---|
| M01 `SRM` | 88 | **70** | −18 | Count taken from highest ID `FR-SRM-088` |
| M02 `FSM` | 74 | **63** | −11 | Same |
| M31 `WSR` | 58 | **53** | −5 | Same |
| M04 `FRD` | 32 | **31** | −1 | Same |
| M05 `RMS` | 61 | **62** | **+1** | Range endpoint understated — `FR-RMS-062` exists outside the declared range |

**This is the third time the same defect has been reported and the first time it has been
measured correctly.** Audit `00-07` finding H2-03 reported M01 as 72 present / 16 missing, M02
as 65 / 9 and M31 as 55 / 3. Those figures counted **every occurrence of an identifier in the
file**, including the prose sentence *"Full requirement text for FR-SRM-058 … FR-SRM-088 is held
in 05-01"*. Counting requirement **table rows** gives 70, 63 and 53.

**Consequence.** Category A's requirement total has been restated three times and has been wrong
each time:

| Source | Category A total |
|---|---:|
| `05-01` §1.3a | 388 |
| `02-02` after audit 2 | 362 |
| **Counted 2026-08-13** | **355** |

Requirement count drives effort estimation, wave sizing and the business case. The repository
total is likewise restated: **2,985 module requirements + 358 portal requirements = 3,343**,
against the 2,930 recorded in the README.

**Fixed.** All five `§1` tables now carry counted figures with the count date. Each of the four
modules with unused identifiers carries a **retired-identifier register** after `§5` listing every
retired ID explicitly, so the gaps can never again be mistaken for missing requirements:

- `FR-SRM-` 026, 032, 035, 037, 038, 058–062, 064, 067, 071, 074, 075, 079, 081, 088 — **18**
- `FR-FSM-` 044, 048–051, 054, 065, 069, 070, 073, 074 — **11**
- `FR-WSR-` 054–058 — **5**
- `FR-FRD-` 032 — **1**

M05's range was corrected to `FR-RMS-001 … 062`.

---

### A3-02 — The portal suite is filed inside a module category *(Documented; decision open)*

**What was found.** `FOLDER_STRUCTURE.md` §188–201 places `P01`–`P12` in
`04_Portals_and_Applications/`. That folder contains **only** `04-00_Portal_Suite_Overview.md`.
All twelve portal specifications, plus `_PORTAL_SUITE_AUDIT_REPORT.md`, are in
`03_Modules/K_Platform_and_Technology/`.

**Three consequences, all live:**

1. **`K_Platform_and_Technology/` holds 19 specification files, not 7.** Any count of "Category
   K" or of `03_Modules` is ambiguous — 281 requirements or 639, depending on what is included.
2. **The K category overview never mentioned them.** A reader of the overview would not know the
   files were there.
3. **Four modules link to where the files are not.** M02→P02, M03→P09, M04→P03 and M05→P04 all
   referenced `04_Portals_and_Applications/…`, which does not resolve.

The README compounds this, recording *"Portals & applications — 1 written, 12 planned"* while
twelve complete specifications exist. This is the **third recurrence of the RG-06 failure**
(H2-01 was the first, A3-01 the second): a register consulted instead of a directory counted.

**Partially fixed.** The four broken links now point at the actual location. The K overview
carries a new §2.1 stating the split with counted figures.

> **Open — this needs your decision.** Either move `P01`–`P12` and
> `_PORTAL_SUITE_AUDIT_REPORT.md` into `04_Portals_and_Applications/`, or amend
> `FOLDER_STRUCTURE.md` to record `K_Platform_and_Technology/` as their permanent home. **The
> file move was not performed** because it changes repository structure and would invalidate
> relative links in files outside this audit's scope. Moving them is the recommendation — portals
> are consumers of modules, not modules, and they carry a different identity section
> (`Portal Identity`), a different identifier space (`FR-POR-###`) and their own audit.

---

### A3-03 — The data model did not resolve *(Fixed — 255 → 0)*

**What was found.** Every module declares the entities it owns (`§10.1`) and the entities it
reads from other modules (`§10.2`). **255 of those referenced-entity declarations named an entity
that the module they attributed it to does not define.**

This was the single most consequential technical defect in the set. A build team wiring M01 to
M15 would read *"`fix.part` — owned by M15"*, look in M15, and find `fix.stock.quant`,
`fix.stock.reservation` and eighteen others — but no `fix.part` anywhere in the estate.

Two distinct failure modes were present:

**Naming drift** — the entity exists, under a different name:

| Referenced as | Attributed to | Actually |
|---|---|---|
| `fix.invoice` | M20 | `fix.ar.invoice` |
| `fix.credit.note` | M20 | `fix.ar.credit.note` |
| `fix.charge.event` | M20 | `fix.billable.event` |
| `fix.gl.control.account` | M19 | `fix.gl.account` |
| `fix.ml.model` | M26 | `fix.model` |
| `fix.qc.checklist` | M23 | `fix.checklist.template` |
| `fix.ncr` | M23 | `fix.nonconformance` |
| `fix.ewaste.batch` | M18 | `fix.recycling.batch` |
| `fix.fixed.asset` | M49 | `fix.asset` |
| `fix.warranty.claim` | M09 | `fix.brand.claim` |

**Ownership misattribution** — the entity exists, owned by a different module:

| Referenced as | Attributed to | Actually owned by |
|---|---|---|
| `fix.work.order` | M01 | **M02** |
| `fix.payroll.run` | M21 | **M56** |
| `fix.part.item` | M15 | **M37** |
| `fix.brand`, `fix.fault.taxonomy` | M17 / M23 | **M37** |
| `fix.attendance`, `fix.roster` | M21 | **M55** |
| `fix.standard.cost` | M15 | **M54** |

The second class is more serious: it points a build team at the wrong module's team, schema and
delivery wave.

**Fixed.** All 255 references now resolve. Corrections were applied in three verified passes —
first the unambiguous renames, then owner reattribution checked against each owner's actual
catalogue, then a final pass that **recomputes every `Owned By` cell from the corrected entity
names**, so the owner column is now derived from the catalogues rather than asserted. Every
correction was verified against the owning module's `§10.1` before application.

**Residual risk.** Where an entity name was genuinely ambiguous the nearest correct entity was
chosen and is recorded above; the data-model owner should confirm the semantic intent during
`05-02` assembly. The template now carries an explicit warning at `§10.2`.

---

### A3-04 — Fifteen role identifiers carried conflicting identities *(Fixed)*

**What was found.** `05-04` registers **R01 … R38**. Two clusters of modules had drifted onto a
different role map, so the same identifier meant different people in different files.

| Role | `05-04` says | Also used as | In |
|---|---|---|---|
| **R02** | Chief Technology Officer | **Chief Financial Officer** | M22, M56, M57, M58 |
| **R03** | Chief Financial Officer | **COO** / Operations Director | M22, M25, M26, M57, M59 |
| **R07** | Dispatch Manager | **Operations Manager** | M22, M57 |
| **R08** | Service Centre Agent | **Team Leader** | M22, M57, M59 |
| **R09** | Workshop Supervisor | **Service Head** | M22, M58 |
| **R21** | Sales Manager | **Chief Commercial Officer** | M07, M10, M33, M34, M35 |
| **R23** | Marketing Manager | **Sales Executive** | M07 |
| **R24** | Marketplace Operations Officer | **Marketing Head** / **Quality Manager** | M10, M22, M27, M35, M59 |
| **R25** | Retail / Refurbishment Officer | **HR Director** | 8 modules |
| **R30** | HR Manager | **Marketing Executive** / HR Director | M35, M60 |
| **R32** | Quality Manager / ISO Coordinator | **GRC / Internal Audit** | M22, M56, M57, M58, M59 |

**Why this is critical and not cosmetic.** Audit `00-07` H2-07 identified exactly this class of
defect for a single role — R60 duplicating R32 — and called it *"a live security defect, not a
documentation defect"*, because a permission rule written against one identifier does not apply
to a user granted the other. The same defect was present on **fifteen** identifiers, including
**R02 and R03, which are the CTO and CFO**. A rule granting R02 in a Category H module would have
granted the CFO's authority to the CTO.

**Fixed.** All 41 conflicting tokens were remapped in a single simultaneous pass (sequential
replacement would have cascaded — R21 had to vacate before Sales Manager could take it):

| Was | Now | Basis |
|---|---|---|
| R02 CFO | **R03** Chief Financial Officer | Registered identity |
| R03 COO · R07 Operations Manager | **R05** Operations Director | `05-04` has no COO; R05 is the operational executive |
| R21 Chief Commercial Officer | **R04** Chief Commercial Officer | Registered identity |
| R23 Sales Executive | **R21** Sales Manager | Registered identity |
| R24 Marketing Head · R30 Marketing Executive | **R23** Marketing Manager · **R50** Marketing Executive | R50 newly allocated — distinct permissions |
| R24 Quality Manager | **R32** Quality Manager / ISO Coordinator | Registered identity |
| R25 HR Director | **R30** HR Manager | Registered identity |
| R08 Team Leader | **R47** Team Leader | New — no registered equivalent |
| R09 Service Head | **R48** Service Head | New — no registered equivalent |
| R32 GRC / Internal Audit · **R60** | **R49** GRC / Internal Audit | New; closes H2-07 remediation item 5 |

R47–R50 were allocated rather than forced onto an existing identifier, following the precedent
already set by R41–R46. A further 203 label tokens were normalised to the `05-04` canonical
spelling (`R01 CEO` → `R01 Chief Executive Officer`, and so on).

**Verified:** zero role identifiers now carry conflicting identities.

---

## 4. High Findings

### A3-05 — 48 custom-development identifiers collide *(Made safe; reallocation open)*

`CD-` names **deliverable software modules**. It will appear in the build backlog, the repository
layout and the vendor statement of work. 48 of 192 allocated identifiers are claimed by two
modules — most severely between Category D/E/F/G and Category H, which allocated `CD-059`–`CD-091`
independently.

**Not renumbered, deliberately.** `CD-` identifiers are also referenced in `02-05`, `00-01`,
`00-03` and both prior audit reports. Renumbering inside `03_Modules` alone would replace one
inconsistency with a worse one. `00-07` remediation item 9 already assigns this to Architecture
with `02-05` as the sole allocator.

**Made safe.** All 33 affected modules now carry an explicit warning at `§16.2` **naming the
specific colliding identifiers and the modules that also claim them**, and instructing that no
build backlog item be created from the table until `02-05` reissues it.

### A3-06 — 13 consumed events had no publisher *(Fixed)*

Thirteen integration contracts were declared on the consuming side only:

`msp_ticket.escalated` · `msp.usage_reported` (M05) · `receivable.dunning_stage_changed` (M20) ·
`asset.model_unknown` (M17) · `quality.ncr_raised` (M23) · `data.usage_reported` (M06) ·
`rental.usage_reported` (M13) · `po.confirmed` (M16) · `billing.event` (M01, M31) ·
`complaint.quality_classified` (M34)

Each is now declared in the publisher's `§12.3` with a payload summary and consumer list. All
consumed events now resolve to a publisher.

### A3-07 — 22 modules are scheduled before their prerequisites *(Flagged; decision open)*

Every declared dependency was checked against both modules' frontmatter wave. **22 modules
declare a dependency on a module that lands in a later wave.** Five are P0:

| Module | Wave | Prerequisite landing later |
|---|:--:|---|
| **M01** Service Order | W1 **P0** | M17 Asset Registry (W2) — yet `BRU-SRM-01` forbids an order without a device |
| **M33** Party Master | W1 **P0** | M64 MDM (W2) |
| **M37** Catalogue | W1 **P0** | M64 MDM (W2) |
| **M15** Inventory | W2 **P0** | M19 GL (W3) |
| **M20** Receivables | W3 **P0** | M51 Tax (W4) — an invoice cannot be raised without VAT determination |
| M02 Field Service | W2 P0 | M22 (W5), M46 (W5), **M55 (W5)** — and M55 lists M02 as *blocking* |
| M51 Tax | W4 P0 | **M65 (W9)** — five waves later |
| M31 Workshop | W2 | M22, M23, M45 (all W5) |

**M20 → M51 and M02 → M55 are the two that should be resolved first.** A receivables module that
goes live a full wave before the tax determination service must either issue invoices without
statutory VAT treatment or not issue them at all. M55 explicitly describes itself as blocking M02,
while sitting three waves behind it.

Each of the 22 modules now carries a **wave-inversion warning** in `§16.3` naming the specific
prerequisite and requiring the programme to state which of three things is true: the dependency is
not a true prerequisite, a named interim capability covers the gap, or a wave assignment is wrong.

### A3-08 — 48 dependency edges were one-directional *(Fixed)*

Rule RG-04 requires both sides of a dependency to agree. The raw check returned 222 breaches, but
174 were satisfied by a blanket declaration (*"All 66 other modules and all 12 portals"*) on
genuine platform modules. **48 were genuine**, concentrated on M37 Catalogue (7 missing), M01 (5),
and M08/M16/M17/M20/M51/M54 (3 each). All 48 are closed; M37's roll-up count was recomputed from
27 actual dependants.

### A3-09 — Five modules mis-stated another module's wave *(Fixed)*

| File | Said | Actual |
|---|---|---|
| M51 | "M65 is W6" | **W9** — and the stated mitigation (*"refactored onto M65's contract in W6"*) was therefore impossible |
| M49 | M18 E-Waste (W6) | **W8** |
| M54 | M47 Facility (W6) | **W7** |
| M50 | M04 Front Desk (W2) | **W1** |
| M62 | M33 Party Master (W2) | **W1** |

### A3-10 — `05-01` still allocates retired module codes *(Open — outside this scope)*

`05-01` §1.3 remains on the superseded 30-module allocation and contradicts `02-02` §5, which is
authoritative:

| Module | `05-01` §1.3 says | `02-02` §5 and the module file say |
|---|---|---|
| M11 | `SLS` — **not recorded as retired anywhere** | `PRC` |
| M16 | `SCM` (retired) | `PRO` |
| M20 | `BIL` (retired) | `ARB` |
| M21 | `HRM` (retired) | `HCM` |
| **M12** | **`ECM`**, range `FR-ECM-001…079` | `MKP` — **`ECM` is M38's live code** |

The M12/M38 `ECM` overlap is a genuine collision between two governance documents. `02-02`'s
retired-code table is also incomplete: it omits `SLS`.

**Open.** `05-01` is outside this audit's scope. Recommend restating §1.3 from `02-02` §5 and
adding `SLS` to the retired-code register.

### A3-11 — Ten internal references pointed at non-existent files *(Fixed)*

| File | Was | Now |
|---|---|---|
| M53 | `B_…/M12_ECommerce_Parts_Retail_and_Marketplace.md` | `C_…/M12_Marketplace_and_Seller_Ecosystem.md` |
| M51 | `C_…/M12_ECommerce_Parts_Retail_and_Marketplace.md` | as above |
| M53 | `M39_Subscription_and_Recurring_Billing.md` | `M39_Subscription_and_Recurring_Revenue.md` |
| M49 | `M18_EWaste_and_Circular_Economy.md` | `M18_EWaste_Recycling_and_Circular_Economy.md` |
| M49 | `M47_Facility_and_Workplace_Management.md` | `M47_Facility_Branch_Infrastructure_and_Workplace.md` |
| M54 | `M21_HR_and_Payroll_Management.md` | `M21_Core_HR_and_Employee_Lifecycle.md` |
| M54 | `M62_Data_Platform_and_Warehouse.md` | `M62_Data_Platform_Warehouse_and_Governance.md` |
| M51 | `M65_Country_and_Localisation_Pack.md` | `M65_Multi_Entity_Multi_Country_and_Localisation.md` |
| M59 | `04-00_Portal_and_Application_Overview.md` | `04-00_Portal_Suite_Overview.md` |
| M31 | `02-03_Module_Boundary_and_Overlap_Rules.md` | marked *(planned)* — the file does not exist |

Note the pattern: **every one names a module by an older title.** These are the fossil record of
module renames that were never propagated.

---

## 5. Medium and Low Findings

### A3-12 — The template matched nothing *(Fixed)*

`_MODULE_TEMPLATE.md` described a **16-section** structure. All 79 specifications use a
**19-section** structure with different numbering — the template's §6 was Business Rules, the real
§6 is Technical Functions, and §7 Business Functions, §12 Interfaces and §19 References did not
exist in the template at all. Anyone writing a new module from it would have produced a
non-conforming file.

Rewritten to the real structure, with a new **§0 Identifier Rules** block placed before §1,
because the majority of findings in all three audits have been identifier-space violations rather
than content errors. It now states which spaces are module-local and which are programme-wide,
carries the RG-06 counting rule, and embeds the specific traps this audit found: count rows not
identifiers, name the owner's entity exactly, check event symmetry, check the wave of every
prerequisite.

### A3-13 / A3-14 — Category overviews *(Fixed)*

Category A carried no measured scale table, alone among the categories that have one. Added, with
the counted 355 requirements / 206 PW and an explicit note that 35 identifiers are retired.

Category K did not mention the twelve portal specifications in its own folder. Added §2.1 with the
7-module / 12-portal split.

### A3-15 — 33 tables are declared as owned by more than one module *(Open)*

The set states that one module owns each entity. 33 tables break that:

| Table | Claimed by |
|---|---|
| `fix_contract_cost` | M08, M53, M54 |
| `fix_asset`, `fix_asset_custody` | M17, M49 |
| `fix_sod_rule`, `fix_sod_exception` | M29, M60 |
| `fix_alert`, `fix_alert_rule` | M05, M48 |
| `fix_scheduled_job`, `fix_job_run`, `fix_working_calendar` | M30, M63 |
| `fix_risk_assessment`, `fix_control` | M59, M60 |
| `fix_tax_challan` | M51, M56 |
| …and 20 more | |

`fix_asset` (M17 vs M49) and `fix_tax_challan` (M51 vs M56) are the consequential ones — customer
device registry versus fixed-asset register, and the VAT challan versus the payroll tax challan.
Each needs an owner named and the other side changed to a reference. **Open** — this is a
data-model decision, not a documentation correction.

### A3-16 — 12 KPI identifiers are shared *(Verified)*

Down from the 22 reported in `00-07`. Nine of the twelve now carry an explicit co-ownership note
(*"M15 measures; M43 is the primary lever"*), which is legitimate. Three do not: **KPI-004**
(M01/M02/M31), **KPI-007** (M01/M31) and **KPI-009** (M01/M04). These are genuinely the same
metric measured at different points and should be resolved when the programme KPI register is
built.

### A3-17 / A3-18 / A3-20 — Register extensions still owed *(Open)*

- **R39–R50** are used and defined in module files but absent from `05-04`. This audit added R47,
  R48, R49 and R50. `05-04` must be extended to **R50**.
- **SOD-13 … SOD-30** remain used and unregistered (carried from H2-06).
- **R38** now carries **17 distinct external-party identities** — vendor, marketplace seller,
  brand partner, courier, recycling partner, external auditor, tax consultant, calibration
  provider and more. `05-04` defines R38 as a multi-party role, so this is by design, but eight
  modules list R38 twice in one permission table with different scopes. R38 needs formal
  sub-typing (`R38.1`, `R38.2`, …) before access control can be implemented from these documents.

### A3-19 / A3-21 / A3-22 / A3-23 — Minor

Role labels normalised (203 tokens). Template `status` enum corrected to the value all 79 files
actually use. `FR-DTS-008b` is undocumented in `05-01` §1.3, which records only `020a–020c`.
`<domain>` and `<aggregate>` placeholders remain in M62 and M28 technical text.

---

## 6. What the Set Got Right

Verified clean, and worth recording because it is the larger part of the picture:

| Check | Result |
|---|---|
| **Regulatory accuracy** | **No defects found.** Every statutory claim checked against source |
| Structural conformance | 79 of 79 specifications carry the full 19-section structure |
| Requirement contiguity | 62 of 67 modules have contiguous, duplicate-free sequences |
| Module code register | Every module file matches `02-02` §5 exactly |
| Portal identifier allocation | `FR-POR-001…358` contiguous across 12 files, no gaps, no overlaps |
| Company facts | 51+ branches, 250,000+ monthly customers, 17+ brands, 500+ employees, hotline 16743 — consistent across all 97 files |
| Business rule / automation IDs | `BRU-` and `AUT-` — zero collisions across the whole set |
| Cross-module references | No reference to a non-existent module ID anywhere |

**The regulatory work is the strongest part of this documentation set.** Every claim tested
verified against source:

- **Mushak 6.3** correctly cited under **Rule 40(1)** of the VAT & SD Rules 2016; **Mushak 9.1**
  correctly identified as the monthly return, due the 15th; the VDS exemption for manufacturer
  supply against a valid Mushak 6.3 is correctly stated *(M51)*
- **Personal Data Protection Act 2026 (Law 63 of 2026)** — correctly described as passed April
  2026 replacing the 2025 Ordinance, with enforcement activating ~13 May 2027 *(M06, M33, and 9
  others)*
- **Hazardous Waste (E-waste) Management Rules 2021** — correctly attributed to the DoE, 10 June
  2021, under the Environment Conservation Act 1995, with the EPR collection targets rising 10% →
  50% and the RoHS-aligned ten-substance restriction *(M18)*
- Bangladesh Labour Act 2006, ISO 9001:2015, ISO 45001:2018 citations carry verification dates per
  DoD-17

M56's handling of the contested AY 2026–27 tax slab — flagged as an open question with a warning
that *"the statutory pack must be built from the enacted Finance Act, not from press reporting"* —
is the correct treatment and should be the model for every statutory parameter in the set.

---

## 7. Remediation Status

| # | Action | Owner | Status |
|---|---|---|:--:|
| 1 | Restate Category A requirement counts; register retired identifiers | Documentation Squad | ✅ **Done** |
| 2 | Resolve all 255 entity references | Documentation Squad | ✅ **Done** |
| 3 | Eliminate all conflicting role identities | Documentation Squad | ✅ **Done** |
| 4 | Declare the 13 missing event contracts | Documentation Squad | ✅ **Done** |
| 5 | Close 48 dependency reciprocity gaps | Documentation Squad | ✅ **Done** |
| 6 | Correct 10 broken references and 5 wave mis-statements | Documentation Squad | ✅ **Done** |
| 7 | Rewrite the module template | Documentation Squad | ✅ **Done** |
| 8 | Flag 22 wave inversions and 48 CD collisions in-file | Documentation Squad | ✅ **Done** |
| 9 | **Decide the portal-suite location** | CTO / Documentation Squad | ⬜ **Open — needs a decision** |
| 10 | **Resolve M20→M51 and M02→M55 wave inversions** | Programme Director | ⬜ **Open — before W2 gate** |
| 11 | **Reallocate all `CD-` identifiers from `02-05`** | Architecture | ⬜ **Open — before any build contract** |
| 12 | Restate `05-01` §1.3 from `02-02` §5; add `SLS` to retired codes | Documentation Squad | ⬜ Open |
| 13 | Extend `05-04` to **R50** and **SOD-30**; sub-type R38 | GRC / IAM | ⬜ Open — before W1 build |
| 14 | Name a single owner for each of the 33 dual-owned tables | Data Architecture | ⬜ Open — before `05-02` |
| 15 | Build the programme KPI register; resolve KPI-004, 007, 009 | Documentation Squad | ⬜ Open |
| 16 | Update README: 3,343 requirements; M66/M67 written; 12 portals written | Documentation Squad | ⬜ Open |

**Items 10 and 11 are the ones that become expensive if deferred.** A wave inversion on a P0
finance module surfaces as a go-live blocker, not a documentation query.

---

## 8. Counted Figures — 2026-08-13

Every figure below was derived by direct enumeration of the files on the date shown (RG-06).

| | Counted |
|---|---:|
| Files under `03_Modules` | **97** |
| Module specifications | **67** — complete, including M66 and M67 |
| Portal specifications | **12** — complete |
| Module requirements | **2,985** |
| Portal requirements | **358** |
| **Total requirements** | **3,343** |
| Retired requirement identifiers | 35 (all Category A) |
| Owned data entities | 1,326 |
| Distinct KPI identifiers | 247 |
| Distinct CD identifiers | 192 *(48 colliding)* |
| Role identifiers in use | R01–R50 *(R38 carries 17 sub-types)* |

**These supersede the README's 2,930 requirements and its statement that M66, M67 and the twelve
portal specifications are outstanding. All are written.**

---

## 9. Sources

**Regulatory — verified 2026-08-13**
Bangladesh VAT & Supplementary Duty Act 2012 and Rules 2016 — Mushak 6.3 under Rule 40(1),
Mushak 9.1 monthly return due the 15th, 15% standard rate, VDS exemption for manufacturer supply ·
Personal Data Protection Act 2026 (Law 63 of 2026), passed April 2026, enforcement ~13 May 2027 ·
Hazardous Waste (E-waste) Management Rules 2021, Department of Environment, 10 June 2021, under
the Environment Conservation Act 1995 — EPR targets 10% → 50%, RoHS-aligned ten-substance
restriction · Bangladesh Labour Act 2006 and Labour Rules 2015 · ISO 9001:2015, ISO 45001:2018

- [NBR — VAT & SD Act 2012 framework and the 15% standard rate](https://dhakatax.com/vat-in-bangladesh-what-every-business-must-know-about-bin-returns-the-15-standard-rate/)
- [Mushak 6.3 VAT invoice — Rule 40(1) compliance guide](https://rakibhassan.eu/mushak-6-3-vat-invoice-bangladesh/)
- [VAT deduction at source — 2026 VDS guide](https://rakibhassan.eu/vat-deduction-at-source-bangladesh/)
- [Securiti — overview of Bangladesh's Personal Data Protection Act 2026](https://securiti.ai/bangladesh-personal-data-protection-act-overview/)
- [Digital Policy Alert — Personal Data Protection (Amendment) Ordinance 2026](https://digitalpolicyalert.org/event/38601-president-implemented-personal-data-protection-amendment-ordinance-2026-ordinance-no-23-of-2026)
- [ChemLinked — Bangladesh publishes E-waste Management Rules](https://chemical.chemlinked.com/news/chemical-news/bangladesh-publishes-e-waste-management-rules)
- [Enviliance ASIA — Bangladesh E-waste Management Rule](https://enviliance.com/regions/south-asia/bd/report_2900)

**Internal**
`00-06_Documentation_Audit_Report.md` (audit 1) · `00-07_Category_H_Audit_and_Repository_Integrity_Report.md` (audit 2) ·
`02-02_Module_Catalogue_Master_Register.md` §5, §6 · `05-01_Feature_and_Function_Register.md` §1.3 ·
`05-04_Role_Permission_and_Access_Matrix.md` · `FOLDER_STRUCTURE.md` §188–201 ·
`_CATEGORY_E/F/G/J/K_AUDIT_REPORT.md` · `_PORTAL_SUITE_AUDIT_REPORT.md` ·
direct enumeration of all 97 files under `03_Modules`

---

*Audit 3 · 1000FiX ERP System v2.0 · Issued 2026-08-13 · CONFIDENTIAL*
