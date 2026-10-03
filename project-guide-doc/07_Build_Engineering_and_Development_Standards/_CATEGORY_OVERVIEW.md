---
id: PGD-CAT-07
category: 07 — Build Engineering & Development Standards
code: BE
project: 1000FiX ERP System v2.0
version: 2.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
owner: Engineering Lead
enumeration_timestamp: 2026-08-18 19:48 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
audit: ../_AUDIT/PGD-AUDIT-CAT-07_Category_07_Build_Engineering_Audit.md
---

# Category 07 — Build Engineering & Development Standards (`BE`)

## Purpose

These are the documents a developer opens on **day one**.

The workspace's own `old-primary-doc/1000FiX_ERP_Missing_Implementation_Documents.md` identified five
of them as **"PRIORITY 1 — MUST-HAVE BEFORE DAY 1"** in March 2026. That checklist is the most direct
corroboration in the workspace that this category was the real blocker.

**All nine are now written**, issued 2026-08-18 and audited the same day in
[`PGD-AUDIT-CAT-07`](../_AUDIT/PGD-AUDIT-CAT-07_Category_07_Build_Engineering_Audit.md) —
**24 findings, 4 critical, 11 closed, 13 open**.

## Documents

| ID | Document | Status | Pri | Needed by | March 2026 checklist |
|---|---|:--:|:--:|:--:|:--:|
| `BE-001` | [Development Environment Setup Guide](BE-001_Development_Environment_Setup_Guide.md) | ✅ | **P0** | **Now** | ✓ Doc 1 |
| `BE-002` | [Coding Standards & Style Guide](BE-002_Coding_Standards_and_Style_Guide.md) | ✅ | **P0** | **Now** | ✓ Doc 4 |
| `BE-003` | [Git Workflow, Branching & Code Review Standard](BE-003_Git_Workflow_Branching_and_Code_Review_Standard.md) | ✅ | **P0** | **Now** | ✓ Doc 4 |
| `BE-004` | [Repository & Monorepo Structure Standard](BE-004_Repository_and_Monorepo_Structure_Standard.md) | ✅ | **P0** | **Now** | ✓ Doc 2 |
| `BE-005` | [**Custom Development (CD) Master Register**](BE-005_Custom_Development_CD_Master_Register.md) | ✅ | **P0** | **Now** | — |
| `BE-006` | [Component Build Specification Standard](BE-006_Component_Build_Specification_Standard.md) | ✅ | P1 | W1 | — |
| `BE-007` | [Dependency, Licence & SBOM Management Standard](BE-007_Dependency_Licence_and_SBOM_Management_Standard.md) | ✅ | P1 | W1 | — |
| `BE-008` | [Sprint Model, Estimation & Backlog Management Standard](BE-008_Sprint_Model_Estimation_and_Backlog_Management_Standard.md) | ✅ | **P0** | **W1** | ✓ Doc 5 |
| `BE-009` | [Technical Debt Register & Refactoring Policy](BE-009_Technical_Debt_Register_and_Refactoring_Policy.md) | ✅ | P2 | W2 | — |

**Qualified ✅.** `PGD-000` §0.3 tests (a) named file, (b) complete front matter and (c) ≥90% of the
governing standard's section set are met by all nine and verified in the audit §7. Test (d) requires
a named owner **and an approval record**; owners are named and no approval record exists, because no
constituted body can create one (`PGD-A1-09`, `PGD-A2-25`). That qualification applies to every file
in this estate, not only to these.

## What the category delivered

### `BE-005` unblocked the build backlog

`_MODULE_TEMPLATE` §16.2 carries this instruction to every module author:

> ⚠ CD identifiers are **provisional** until allocated by `02_Architecture/02-05`. **Do not create a
> build backlog item from an identifier in this table until 02-05 has issued it.**

`02-05` never issued them. Under the programme's own governance rule, **no backlog item could
lawfully be created for any of 331 components.** `BE-005` issues them, and in doing so:

| Position before | Position now |
|---|---|
| *"Two incompatible CD registers exist"* (`H-03`) | **Four**, counted — `02-05` §5.2, TSS §8.2, and two coexisting schemes inside the module estate itself |
| *"~138 CD items"* (RFP), restated to **248** (TSS §25.3.1) | **331 items across 79 delivery units**, counted at 2026-08-18 12:46 (+06) |
| *"48 identifiers currently collide"* (`_MODULE_TEMPLATE` §0) | **Confirmed exactly** — 37 held by two components, 11 by three: 48 identifiers denoting **107** distinct components, all resolved |
| Sequential allocation with no allocating authority | **`CD-<UNIT>-<nn>`** — derivable, locally allocated, collision-proof by construction |
| `FF-16` unsatisfiable (`AR-012` §5.3) | Enabled, on five stated conditions with owners |

### Four languages, one standard set

`BE-002` covers all four stacks, because the programme builds in all four:

| Stack | `BE-005` items | What the standard fixes |
|---|---:|---|
| **Python / Odoo 19** | 270 (`Odoo module` + `Odoo module + service`) | Ruff and pylint-odoo configuration, import blocks, typing boundary, `sudo()` justification, N+1 discipline |
| **Python / Go / Node services** | 33 | Timeout, retry and declared fallback on every external call; domain exceptions at the edge |
| **TypeScript / React 19 / Next.js** | 20 | Adopted from `AGENTS.md` and extended — generated API client only, no money arithmetic, bundle budget, keyboard alternatives |
| **Dart / Flutter** | 8 | One shared offline engine, append-only journal, client idempotency keys, `bn_BD` as the development locale |

The inherited standard was measured rather than assumed: **`AGENTS.md` contains 0 mentions of Odoo,
0 of Flutter, 0 of Dart and 1 of Python**, and names two technologies the ERP rejected by name
(`TD-05` Timefold, `TD-06` Rasa). It is adopted for TypeScript and for nothing else (`BEA-09`).

### Three positions the category had to take, and took

| Question | Position | Why |
|---|---|---|
| GitFlow, against the DORA evidence for trunk-based development? | **Retain GitFlow, constrain batch size explicitly instead** — a 3-day branch ceiling and a 400-line review trigger, both measured as distributions | Nine funded wave gates and six manually promoted environments need a release object; GitFlow does not constrain batch size, so the standard does |
| Conventional Commits, or OCA's `[FIX]`/`[IMP]`/`[MIG]` tags? | **Both, by destination**, with a scripted rewrite at the subtree boundary | `02-05` §3's contribute-back commitment and TSS §18.1's house convention are both binding and incompatible. Nobody had noticed |
| Sixteen TSS Block 3 cross-cutting services — issue identifiers now? | **No.** `CD-SVC` left deliberately empty, with three W0 actions and an owner | Issuing them would assert an architecture ownership decision and an estimate this register has no authority to make |

## The four critical findings

Each is against material outside this category, and each is quantified.

| # | Finding | Against |
|---|---|---|
| **`BEA-02`** | TSS §25.3.1 proposes restating the RFP's deliverable count to **248**. The counted estate is **331**, and TSS §8.2 disagrees with the specifications on **74.7%** of the flat identifier space. Restating to 248 replaces one wrong number with another | TSS §8.2, §25.3.1; RFP §5.3 |
| **`BEA-04`** | **No configuration effort exists anywhere in the estate.** For **75 of 79** delivery units the §1 effort figure equals the §16.2 custom-development sum **exactly**, against a stated 52% L1 + L2 requirement coverage. `GV-007` §7.3 excludes seven work streams; configuration is not one of them, so it is excluded by accident | `GV-007` §7.3; `02-05` §1 |
| **`BEA-06`** | With all 79 units placed in the waves **their own specifications declare**, demand is **1,842 PW against 1,088 PW effective capacity — 1.69×**, and **no wave is under capacity before W8**. `GV-004` §5.3's *"balances in aggregate and fails in shape"* holds only for the 42-unit view | `GV-004` §5.2, §5.3, §5.4 |
| **`BEA-16`** | **MinIO — the Wave 1 object store — had its open-source repository archived on 25 April 2026**, four months before this issue. TSS was version-verified on 13 August 2026 and still lists it as current. TSS §7.4 names no open-source fallback. This is `TR-09` materialising on a foundation component | TSS §7.1, §7.3, §7.4, §20.2 |

## What "done" looks like for this category

1. ✅ A developer clones the repository and reaches a **green `make doctor`** on day one — `BE-001`, measured at 1.6–2.7 hours on the `core` profile.
2. ✅ `BE-005` issues a single CD register covering all 79 delivery units, and the 48 collisions are closed.
3. ✅ `BE-002` ships with linter configuration that **enforces** it, Blocking from the first commit — there is no legacy code, so there is no promotion period to serve.
4. ✅ `BE-008` establishes an estimation unit and the conversion `RQ-008` `SU-14` deferred. *"Story point"* still occurs **zero times** in the 621-file source estate; it now occurs in a standard.
5. ✅ `BE-004` makes `02-05`'s upgrade-safety commitment structural: OCA as subtrees, Odoo as a pinned submodule, custom code physically outside `vendor/`.

**Still open, and outside this category's authority:** `BEA-16` (what replaces MinIO), `BEA-04`
(is configuration effort in the estimate or not), `BEA-06` (does Wave 1 start against a 5.87×
position), and `D-027` (one mobile framework or two).

## Dependencies

| Direction | Category | Relationship |
|---|---|---|
| Upstream | `00_Governance` | `BE-008` consumes `GV-004` capacity and `GV-007` estimates; `BE-005` reconciles against both |
| Upstream | `01_Requirements` | `BE-008` discharges `RQ-008` `SU-14`; `BE-006` consumes `RQ-010`'s Definition of Done |
| Upstream | `02_Architecture` | `BE-004` realises the `AR-001` development view; `BE-002` enforces `AR-007`; `BE-005` enables `AR-012` `FF-16` |
| Downstream | `10_Infrastructure` | `PE-004` implements the gates in `BE-002` §10, `BE-004` §12 and `BE-007` §5 |
| Downstream | `08_Quality` | `QA-005` assumes `BE-002` §8's test conventions; `QA-004` traces to `BE-006`'s `component.yaml` |
| Downstream | `12_Release` | `RL-002` and `RL-003` consume `BE-003` §8's tags and §9's hotfix path |

## Audience and change frequency

| Attribute | Value |
|---|---|
| Primary audience | Every developer; implementation vendor engineering leads |
| Change frequency | **Low once set** — except `BE-005`, which is append-only and continuous, and `BE-009`, which is continuous by nature |
| Standards basis | Odoo 19.0 conventions · OCA contributing conventions · PEP 8/257/484 · TypeScript 5 strict · Effective Dart · Conventional Commits 1.0.0 · SemVer 2.0.0 · CycloneDX 1.7 (ECMA-424) · SPDX 3.0.1 · NIST SP 800-218 · SLSA · ISO 10007:2017 · ISO/IEC 25010:2023 · ISO/IEC 5055:2021 · Scrum Guide 2020 |

## Existing material this category built from

`1000fix_ERP_Module/02_Architecture/02-05` §3, §4, §5, §9, §10 ·
`old-primary-doc/1000FiX_ERP_Missing_Implementation_Documents.md` §3 Documents 1, 2, 4, 5 ·
`primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §4.1, §7.1–§7.4, §8.1–§8.4, §18, §20, §25 ·
**`../../../AGENTS.md`** — the sibling portal programme's in-house engineering conventions ·
`../../../Intergrated_web_portal/Technical_documentation_roadmap/Architecture & Infrastructure/IMPL-18_Monorepo_Migration_Architecture_Evolution_Turborepo.md` ·
§16.2 of all 67 module and all 12 portal specifications — **the source of the 331-item register** ·
`project_content/11_Localisation_Bengali/BN-005`, `BN-006`

---

*Category 07 · `BE` · 1000FiX ERP System v2.0 · CONFIDENTIAL*
