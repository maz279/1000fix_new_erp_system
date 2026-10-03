---
id: RF-003
title: Content-to-Requirement Traceability Matrix
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Programme Content Lead with QA Lead
author: Programme Content Lead with QA Lead and Enterprise Architecture
reviewers: [CTO, QA Lead, Enterprise Architecture, Business Process Lead, Legal & Compliance, Localisation Lead, all Category Content Owners]
approver: Programme Content Lead
content_class: E
purpose: >
  The matrix that makes `CP-04` enforceable: every content file mapped to the requirements and
  acceptance criteria it serves, and every requirement family mapped to the content that must
  exist before it can be built, tested or trained on. Without it, content with no upstream
  requirement is invisible scope creep and requirements with no content are invisible gaps —
  and "is `M43` ready to build?" has no answer that is not an opinion. It also establishes the
  one thing four prior audits could not: the counted requirement denominator, without which
  `G4-10` is unanswerable and no coverage percentage may be quoted anywhere in the programme.
traces_to: [CP-04, 05-01, 05-02, 05-04, 05-05, 05-06, 02-02, 04-00, 06-02, AF-06, TS-01, RF-001, RF-004, RF-005, RF-006, RF-007, RF-012, TS-001, CG-008]
priority: P0
wave: W1
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md — titled "~2,352 Functional Requirements Across 67 Modules"; carries 200 distinct FR identifiers in 149 table rows
    verified: 2026-08-18
    class: P1
  - source: Extraction of every FR- identifier across 1000fix_ERP_Module/, run 2026-08-18 — 2,992 distinct across the 67 M*.md files, 376 across the 12 P*.md files, 3,350 in union, 3,537 across the whole repository
    verified: 2026-08-18
    class: P1
  - source: Extraction of AC- rows from module and portal §15 Acceptance Criteria sections, run 2026-08-18 — 1,308 across 67 modules and 260 across 12 portals
    verified: 2026-08-18
    class: P1
  - source: Extraction of traces_to front matter across all 429 written content files, run 2026-08-18 — module, portal and cross-cutting targets per file
    verified: 2026-08-18
    class: P1
  - source: project_content/_AUDIT/AUDIT-014_Category_13_TS_Content_Audit.md finding TS-01 — three current denominators (2,930 / ~2,352 / 3,343); G4-10 unanswerable; no percentage may be quoted
    verified: 2026-08-18
    class: P1
  - source: project_content/_AUDIT/AUDIT-001_Content_and_Repository_Integrity_Audit.md finding AF-06 — 05-01 titled ~2,352 against README.md 2,930 counted; open, restatement required
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2026-11-18
---

# RF-003 — Content-to-Requirement Traceability Matrix

> **`P0`. This is the only blocking file in Category 99.** `CG-008` Definition of Done item
> "traceability" is answered from here. A category cannot pass gate `G2` on a file whose
> `traces_to:` does not resolve in this matrix.

---

## 1. Purpose

Two questions have no answer in this programme today.

**"Is `M43` ready to build?"** Engineering can answer the code half. Nobody can answer the
content half — whether the master data, the SOPs, the UI copy, the training and the test scripts
`M43` consumes exist and are approved. The question is asked at every wave gate and answered by
whoever is in the room.

**"What breaks if `FR-WTY-018` changes?"** Today: unknown. The requirement is cited in `M09`.
Which of the 429 written content files depend on it is discoverable only by reading them.

`CP-04` already makes traceability a rule — *"Content with no upstream requirement is scope
creep; requirements with no content are a gap. Both are audited in `RF-003`."* The rule has been
in force since the register was issued and the file that audits it has not existed. This is the
file.

It does three things, in order of consequence:

1. **Establishes the requirement denominator by enumeration** (§4.2), closing the diagnosis of
   `AF-06` and `TS-01` and making `G4-10` answerable for the first time.
2. **States the honest granularity of the traceability that actually exists** (§4.3) — module and
   portal level, not requirement level — rather than implying a precision the content set does
   not have.
3. **Maps coverage and exposes both failure directions** (§4.4–§4.7).

---

## 2. Scope

**In scope**

- The `FR-` functional-requirement space across 67 modules and 12 portals
- The `NFR-` non-functional space where content is the discharge mechanism
- The `AC-` acceptance-criteria space, and its handover to Category 13 `TS`
- The `BRU-` business-rule space where a rule cannot execute without content
- Every written content file's declared `traces_to:` target
- Both failure directions: uncovered requirements, and content with no requirement

**Out of scope**

| Excluded | Owner |
|---|---|
| Module-by-module content readiness for build | `RF-004` |
| Portal-by-portal content readiness for go-live | `RF-005` |
| Requirement-to-**test-script** coverage | `TS-001`; this file supplies its denominator |
| Restating `05-01` | CTO — `AF-06` is open and this file cannot close it |
| Whether a requirement is *correct* | The owning module specification |

---

## 3. Audience

| Reader | Uses this matrix to |
|---|---|
| **The CTO at a wave gate** | Answer `G4-10` and every "ready to build" question with a counted figure |
| **A module business owner** | See the content their module depends on, and what is missing |
| **The QA Lead** | Take a denominator that is defensible into `TS-001` |
| **A content author** | Prove at gate `G2` that their file serves a real requirement |
| **The Programme Content Lead** | Find scope creep before it is authored, not after |
| **An implementation vendor** | Understand which content must exist before their sprint can start |

---

## 4. Content

### 4.1 The traceability model

Four levels exist in this programme. Only two are populated.

| Level | Granularity | Populated? | Where declared |
|:--:|---|:--:|---|
| **L1** | Content file → **module / portal** (`Mnn`, `Pnn`) | ✅ **Yes** — 378 of 429 files | `traces_to:` front matter |
| **L2** | Content file → **cross-cutting specification section** (`05-0n §n`, `PS-nn`, `IP-nn`, `NFR-nnn`, `BRU-…`) | ✅ **Yes** — 429 of 429 files | `traces_to:` front matter |
| **L3** | Content file → **individual `FR-` requirement** | ⚠ **Partial** — 61 files, 214 distinct `FR-` citations | `traces_to:` front matter |
| **L4** | Individual `FR-` requirement → **content file** (reverse) | ❌ **No** | Would require `05-01` to be a register |

**This is the finding that governs the whole file.** `CP-04` is written as though L3 traceability
exists. It exists for 14% of the content set. For the remaining 86%, traceability is real and
declared, but at **module granularity** — `MD-022` traces to `M15` and `M43`, not to
`FR-INV-014`.

Two honest consequences follow, and both are stated rather than engineered around:

- **L1/L2 traceability is sufficient for the gate it is used at.** "Does this content serve a
  specification the programme has committed to?" is answerable today, for every file.
- **L4 is not achievable while `05-01` carries 200 of 3,350 identifiers.** A reverse index needs a
  register, and `05-01` is a summary. Building L4 against a summary would produce a matrix that is
  93% empty and would be read as 93% uncovered. Until `AF-06` is closed, this file reports
  coverage at **requirement-family** granularity, which is exact, rather than at requirement
  granularity, which would be fabricated.

---

### 4.2 The denominator — closing the diagnosis of `AF-06` and `TS-01`

`AUDIT-014` **TS-01** found three current denominators and ruled that no coverage percentage may
be quoted. That ruling was correct and is not overturned here. What is added is the count.

#### 4.2.1 What was enumerated

Extraction over `1000fix_ERP_Module/` on **2026-08-18**, pattern
`FR-[A-Za-z0-9]{2,6}-[0-9]{3}`, distinct values:

| Scope | Distinct `FR-` identifiers |
|---|---:|
| The 67 module specifications `M*.md` | **2,992** |
| The 12 portal specifications `P*.md` | **376** |
| **Modules ∪ portals — the programme requirement space** | **3,350** |
| Whole module repository, including cross-cutting specs and `_Superseded/` | 3,537 |
| Registered in `05-01_Feature_and_Function_Register.md` | **200** |

#### 4.2.2 Reconciliation against every figure in circulation

| Figure | Stated in | Reconciles as |
|---:|---|---|
| **~2,352** | `05-01` title and §Total row | The number of requirements `05-01` **describes in prose**. It carries 200 identifiers. `05-01` is a summary, not a register — this is the root cause of `AF-06` |
| **2,930** | `README.md` §Total, marked ⚠ | Within 2% of the module-only figure of **2,992**. Best explained as a module-only count taken before the last module edits. **Not wrong, but scoped to modules and never said so** |
| **3,343** | `AUDIT-014` `TS-01` | Within 0.2% of the module ∪ portal figure of **3,350**. Same enumeration, seven identifiers apart, taken on a different date |
| **3,350** | **This file, enumerated 2026-08-18** | Modules ∪ portals, distinct, scope stated |

**The three denominators were never three counts of the same thing.** They were one prose
estimate and two counts of different scopes, compared as though they were rivals. That is why
seventeen audits could not reconcile them: the reconciliation was not arithmetic, it was
definitional.

#### 4.2.3 The ruling this file makes

| # | Ruling |
|---|---|
| **TR-D1** | The programme requirement denominator is **3,350**, defined as *distinct `FR-` identifiers across the 67 module and 12 portal specifications*, enumerated 2026-08-18 |
| **TR-D2** | Any figure quoting the denominator states **scope and enumeration instant**. "2,930" without "modules only, as at date" is not admissible |
| **TR-D3** | `05-01` is cited as the **feature register**, never as the requirement register, until `AF-06` is closed |
| **TR-D4** | `TS-01`'s prohibition on quoting a coverage percentage is **lifted for content coverage** (this file, §4.4) and **stays in force for test coverage** until `TS-001` adopts `TR-D1` |
| **TR-D5** | The denominator is **regenerated at every wave boundary**, never carried forward (`CP-11`, `RG-06`) |

#### 4.2.4 Two orphan requirement families inside the denominator

| Family | Distinct IDs | Where it lives | Assessment |
|---|---:|---|---|
| `FR-SLS-` | **30** | `05-01` **and** `99_Reference/_Superseded/SUPERSEDED_Pillar_B` only. No module file uses it | v1.0 pillar-architecture residue carried into `05-01`. **Excluded from 3,350** — the figure counts module and portal files only |
| `FR-BFO-` | **3** | `M04`, `00-06`, `05-01` | `M04` was reverted to code `FRD` by audit `C-03`; three identifiers survived the revert. **Inside 3,350** via `M04`, and should be renumbered |

Both are `RF-001` finding `GL-04`. Both belong in the `05-01` restatement.

---

### 4.3 Requirement families and their owning content

Sixty-seven module families, one per module, plus the portal family. Each row states the content
categories that must exist for that family to be buildable, from the enumerated `traces_to:` map.

**Reading the "Content" column:** the number is content files whose `traces_to:` names that
module or portal, enumerated 2026-08-18. It is a coverage count, not a sufficiency judgement —
sufficiency is `RF-004`'s.

#### Category A — Service Delivery & Operations

| Module | Family | Reqs | Content | Dominant content categories |
|---|---|---:|---:|---|
| `M01` Service Request & Order | `FR-SRM-` | 73 | **53** | `DT` 8, `SP` 6, `KB` 7, `TS` 5, `LG` 5 |
| `M02` Field Service & Dispatch | `FR-FSM-` | 64 | **34** | `MD` 6, `TR` 6, `TS` 4 |
| `M03` Service Logistics | `FR-LOG-` | 42 | **22** | `DT` 5, `TS` 4 |
| `M04` Branch & Front Desk | `FR-FRD-` | 32 | **17** | `SP` 3, `DT` 3, `TS` 2 |
| `M05` Remote Support & MSP | `FR-RMS-` | 62 | **20** | `LG` 3, `TS` 3 |
| `M06` Data Services | `FR-DTS-` | 34 | **24** | `LG` 6, `DT` 4, `TS` 4 |
| `M31` Workshop & Depot Repair | `FR-WSR-` | 55 | **33** | `KB` 12, `DT` 5, `MD` 2 |

#### Category B — Customer Engagement & Experience

| Module | Family | Reqs | Content | Dominant content categories |
|---|---|---:|---:|---|
| `M07` CRM & Account Management | `FR-CRM-` | 46 | **14** | `MD` 3, `EO` 3 |
| `M10` Loyalty & Rewards | `FR-LOY-` | 44 | **12** | `MD` 2, `TS` 3 |
| `M27` Omnichannel Contact Centre | `FR-CCE-` | 58 | **37** | `NT` 9, `HC` 8, `OP` 5 |
| `M32` Conversational AI | `FR-CAI-` | 38 | **18** | `HC` 10, `KB` 4 |
| `M33` Customer & Party Master | `FR-CPM-` | 52 | **20** | `LG` 5, `DM` 6 |
| `M34` CX, Feedback & Complaints | `FR-CXM-` | 42 | **17** | `HC` 5, `LG` 4 |
| `M35` Marketing & Demand Gen | `FR-MKT-` | 40 | **11** | `EO` 2, `MD` 2 |

#### Category C — Commercial, Pricing & Revenue

| Module | Family | Reqs | Content | Dominant content categories |
|---|---|---:|---:|---|
| `M08` Contract Lifecycle | `FR-CTR-` | 62 | **29** | `DT` 7, `EO` 5, `MD` 3 |
| `M09` Warranty & Claims | `FR-WTY-` | 67 | **36** | `KB` 5, `DT` 5, `TS` 4, `MD` 4 |
| `M11` Pricing & Rate Cards | `FR-PRC-` | 52 | **17** | `MD` 4, `EO` 4 |
| `M12` Marketplace & Seller | `FR-MKP-` | 79 | **27** | `LG` 6, `EO` 7, `TS` 4 |
| `M36` Quotation & Estimation | `FR-QTE-` | 49 | **11** | `DT` 3, `SP` 3 |
| `M37` Product & Service Catalogue | `FR-CAT-` | 46 | **5** | `MD` 1, `TS` 2 ⚠ |
| `M38` E-Commerce Storefront | `FR-ECM-` | 56 | **9** | `TS` 4, `LG` 2 ⚠ |
| `M39` Subscription & Recurring | `FR-SUB-` | 44 | **9** | `TS` 3, `DT` 2 ⚠ |
| `M40` Partner, Channel & Franchise | `FR-PCM-` | 43 | **20** | `EO` 7, `LG` 3 |

#### Category D — Circular & Asset-Based Business

| Module | Family | Reqs | Content | Dominant content categories |
|---|---|---:|---:|---|
| `M13` Rental / EaaS | `FR-RNT-` | 44 | **6** | `TS` 3, `DT` 1 ⚠ |
| `M14` Trade-In & Refurbishment | `FR-TRF-` | 39 | **15** | `DT` 4, `LG` 4 |
| `M18` E-Waste & Circular Economy | `FR-ESG-` | 26 | **17** | `LG` 4, `DT` 2 |

#### Category E — Supply Chain & Inventory

| Module | Family | Reqs | Content | Dominant content categories |
|---|---|---:|---:|---|
| `M15` Spare Parts & Inventory | `FR-INV-` | 54 | **50** | `DT` 10, `SP` 8, `DM` 6 |
| `M16` Procurement & Sourcing | `FR-PRO-` | 38 | **21** | `DT` 5, `EO` 3 |
| `M41` Warehouse Management | `FR-WMS-` | 41 | **21** | `DT` 7, `SP` 4 |
| `M42` Supplier Relationship | `FR-SRM2-` | 34 | **20** | `DT` 4, `EO` 5 ⚠ *non-conformant code — `GL-02`* |
| `M43` Demand Planning | `FR-DPL-` | 32 | **7** | `TS` 2, `DM` 1 ⚠ |
| `M44` Import & Landed Cost | `FR-ITC-` | 39 | **7** | `MD` 2, `TS` 2 ⚠ |

#### Category F — Asset, Equipment & Facilities

| Module | Family | Reqs | Content | Dominant content categories |
|---|---|---:|---:|---|
| `M17` Device & Asset Registry | `FR-AST-` | 52 | **30** | `DM` 6, `SP` 5, `KB` 3 |
| `M45` Enterprise Asset & Test Equipment | `FR-EAM-` | 46 | **11** | `KB` 3, `MD` 2 |
| `M46` Fleet & Vehicle | `FR-FLT-` | 45 | **8** | `MD` 2, `SP` 2 ⚠ |
| `M47` Facility & Workplace | `FR-FAC-` | 45 | **4** | `SP` 2, `MD` 1 ⚠ **lowest coverage in the register** |
| `M48` IoT & Predictive Maintenance | `FR-IOT-` | 50 | **3** | `DM` 1, `TS` 1, `AP` 1 ⚠ |

#### Category G — Finance & Treasury

| Module | Family | Reqs | Content | Dominant content categories |
|---|---|---:|---:|---|
| `M19` Financial Accounting & GL | `FR-FIN-` | 46 | **41** | `DT` 10, `MD` 7, `DM` 6 |
| `M20` AR, Invoicing & Collections | `FR-ARB-` | 44 | **67** | `DT` 16, `LG` 10, `EO` 9 — **highest in the register** |
| `M49` Fixed Assets | `FR-FXA-` | 35 | **7** | `DM` 3, `MD` 1 ⚠ |
| `M50` Treasury, Cash & Banking | `FR-TRE-` | 42 | **24** | `SP` 5, `DM` 5 |
| `M51` Tax & Regulatory (Bangladesh) | `FR-TAX-` | 45 | **32** | `DT` 13, `MD` 3 |
| `M52` Accounts Payable | `FR-APE-` | 39 | **23** | `DT` 8, `MD` 3 |
| `M53` Revenue Recognition & Settlement | `FR-REV-` | 45 | **27** | `EO` 7, `LG` 4 |
| `M54` Cost Accounting & FP&A | `FR-FPA-` | 40 | **8** | `MD` 2, `DM` 1 ⚠ |

#### Category H — People & Workforce

| Module | Family | Reqs | Content | Dominant content categories |
|---|---|---:|---:|---|
| `M21` Core HR | `FR-HCM-` | 46 | **26** | `MD` 3, `LG` 4, `SP` 3 |
| `M22` Learning & Certification | `FR-LMS-` | 40 | **44** | `TR` 24 — the whole category |
| `M55` Time, Attendance & Scheduling | `FR-WFM-` | 52 | **22** | `TR` 6, `LG` 4 |
| `M56` Payroll & Statutory | `FR-PAY-` | 54 | **22** | `DM` 5, `MD` 4 |
| `M57` Performance & Incentives | `FR-PIC-` | 42 | **14** | `CM` 3, `DT` 2 |
| `M58` Talent Acquisition | `FR-TAO-` | 34 | **7** | `TR` 1, `DM` 1 ⚠ |
| `M59` Health, Safety & Wellbeing | `FR-HSE-` | 42 | **15** | `TR` 6, `KB` 3 |

#### Category I — Governance, Risk, Quality & Knowledge

| Module | Family | Reqs | Content | Dominant content categories |
|---|---|---:|---:|---|
| `M23` Quality Management System | `FR-QMS-` | 50 | **57** | `DT` 8, `TR` 6, `SP` 6, `EO` 7 |
| `M24` Documents & E-Signature | `FR-DMS-` | 50 | **31** | `LG` 12, `EO` 7 |
| `M60` Governance, Risk & Compliance | `FR-GRC-` | 44 | **28** | `LG` 15 |
| `M61` Knowledge Management | `FR-KMS-` | 38 | **42** | `KB` 16, `HC` 18 — both categories entire |

#### Category J — Data, Analytics & Intelligence

| Module | Family | Reqs | Content | Dominant content categories |
|---|---|---:|---:|---|
| `M25` Business Intelligence | `FR-BID-` | 34 | **19** | `RP` 7, `LG` 4 |
| `M26` AI/ML Services | `FR-AIM-` | 42 | **11** | `HC` 3, `KB` 3 |
| `M62` Data Platform & Warehouse | `FR-DAT-` | 38 | **18** | `RP` 8, `LG` 3 |
| `M63` Process Automation | `FR-BPA-` | 32 | **5** | `TS` 4, `NT` 1 ⚠ |

#### Category K — Platform & Technology

| Module | Family | Reqs | Content | Dominant content categories |
|---|---|---:|---:|---|
| `M28` Integration & Event Platform | `FR-IPF-` | 57 | **24** | `AP` 11 — the whole category |
| `M29` Identity, Access & Security | `FR-SEC-` | 52 | **48** | `LG` 11, `TS` 5, `OP` 6 |
| `M30` Platform Administration | `FR-ADM-` | 40 | **16** | `TR` 3, `TS` 3 |
| `M64` Master Data Management | `FR-MDM-` | 34 | **11** | `DM` 6, `MD` 2 |
| `M65` Multi-Entity & Localisation | `FR-GLO-` | 36 | **8** | `MD` 2, `TS` 2 ⚠ |
| `M66` Internal IT Service Management | `FR-ITS-` | 30 | **19** | `OP` 7, `LG` 3 |
| `M67` Project & Portfolio Management | `FR-PPM-` | 32 | **2** | `TS` 1, `AP` 1 ⚠ **second-lowest** |

#### The portal family

| Family | Reqs | Content | Note |
|---|---:|---:|---|
| `FR-POR-` across `P01`–`P12` | **358** | **~360 file-portal links** | Per-portal detail in `RF-005` §4.3. **No `BRU-POR-` family exists** — 358 requirements with no business rules (`RF-001` `GL-02`) |

---

### 4.4 Coverage — both directions, counted

#### 4.4.1 Requirement families with content

| Measure | Value |
|---|---:|
| Module requirement families (`FR-<CODE>-`, one per module) | **67** |
| Families with **at least one** content file tracing to them | **67 (100%)** |
| Families with **fewer than 10** content files | **13** |
| Families with **fewer than 5** content files | **4** — `M47` (4), `M48` (3), `M67` (2), `M37` (5) |
| Portal families with content | **12 of 12 (100%)** |

**No requirement family is uncovered.** That is the good news and it is genuine: the register's
design — organise content by what it *is*, then trace it — has produced complete family coverage
at L1. `TR-D4` therefore lifts the coverage-percentage prohibition **for this measure only**.

#### 4.4.2 The thin thirteen — families whose content is nominal

Coverage of 1 is coverage. It is not readiness. These thirteen families carry 484 requirements
between them and fewer than ten content files each.

| Module | Reqs | Content | Why it is thin, and whether that is acceptable |
|---|---:|---:|---|
| `M67` Project & Portfolio | 32 | **2** | Internal PMO tooling. **Acceptable** — the users are the programme office, who need no training pack |
| `M48` IoT & Predictive Maintenance | 50 | **3** | W8+ capability. **Acceptable now, a gap at W7** — no `MD` telemetry master, no `OP` runbook |
| `M47` Facility & Workplace | 45 | **4** | **Not acceptable.** 51+ branches with facility management and no SOP beyond `SP-030`/`SP-032`, no asset class beyond `MD-044` |
| `M37` Product & Service Catalogue | 46 | **5** | **Not acceptable.** `MD-019` is the spine of all fourteen revenue streams; five files is under-served for a `P0` W1 dependency |
| `M63` Process Automation | 32 | **5** | **Acceptable** — automation is specified in `05-05` `AUT-` rules, which trace through their owning modules |
| `M13` Rental / EaaS | 44 | **6** | **Marginal.** W5 capability with one `DT`, one `SP`, no `TR`, no `HC` |
| `M43` Demand Planning | 32 | **7** | **Not acceptable.** `MD-022` and `DM-007` only. No planner SOP, no `TR`, no `RP` — a planning module with no planner content |
| `M44` Import & Landed Cost | 39 | **7** | **Marginal.** Decision `D-04` (recoverable taxes) is unmade; content is correctly waiting on it |
| `M49` Fixed Assets | 35 | **7** | **Marginal** — W5, finance-internal |
| `M58` Talent Acquisition | 34 | **7** | **Acceptable** — `SP-023` and `DT-042` carry the operative process |
| `M54` Cost Accounting & FP&A | 40 | **8** | **Marginal** — no `RP` dashboard traces to `M54`, yet `RP-010` board pack depends on it |
| `M46` Fleet & Vehicle | 45 | **8** | **Marginal** — `MD-045` exists; no fleet SOP, no rider-facing `KB` |
| `M65` Multi-Entity & Localisation | 36 | **8** | **Acceptable** — `BN` category discharges the localisation half without naming `M65` |
| `M38` E-Commerce Storefront | 56 | **9** | **Not acceptable.** 56 requirements, four of them `TS` scripts and no `UI` copy pack. The storefront has no content owner |
| `M39` Subscription & Recurring | 44 | **9** | **Marginal** — `MD-033` exists; no dunning SOP beyond `DT-018` |

**Six families are assessed *not acceptable*: `M37`, `M38`, `M43`, `M47`.** They are carried to
`RF-007` as backlog items `BL-01`…`BL-04` and to `RF-004` §4.5 as build-readiness blockers.

#### 4.4.3 Content with no requirement — the reverse direction

Fifty-one written files declare **no `Mnn` and no `Pnn`** in `traces_to:`.

| Assessment | Files | Verdict |
|---|---:|---|
| **Governance content** — `CG-001`–`CG-006`, `CG-008`, `CG-009`, `CG-011`–`CG-014`, `SP-001`–`SP-003` | 15 | ✅ **Justified.** `CP-04` note admits governance content; these trace to `CP-` principles and `00-04` |
| **Design-system content** — `VB-001`, `VB-004`–`VB-008`, `VB-010` | 7 | ✅ **Justified.** Trace to `PS-06`, `04-00` §3 |
| **Localisation standards** — `BN-002`–`BN-005`, `BN-007`, `BN-008`, `BN-014`–`BN-016`, `BN-018` | 10 | ✅ **Justified.** Trace to `PS-03`, `05-02` `DM-08`/`DM-09`, CLDR |
| **Change & communications** — `CM-001`–`CM-005`, `CM-007`–`CM-010` | 9 | ✅ **Justified.** Trace to `00-02`, `00-04`, `06-01` |
| **Cross-cutting UI libraries** — `UI-002`, `UI-003`, `UI-004`, `UI-006`, `UI-007`, `UI-008`, `UI-010` | 7 | ⚠ **Justified but under-declared.** They serve *every* portal. `traces_to:` names `05-02`, `05-05` `BR-STD-04`/`06`, `PS-04`, `PS-09` — correct, but a reader cannot see that `UI-004` is consumed by all twelve portals. **Recommend adding `P01`…`P12`** |
| **Cross-cutting standards** — `DT-001`, `MD-027`, `TS-002` | 3 | ⚠ Same as above. `DT-001` governs all 43 other `DT` files; `MD-027` binds every state machine |
| **Scope creep** | **0** | ✅ **None found.** Every one of the 51 resolves to a stated upstream obligation |

**No scope creep exists in the written content set.** That is a real result and worth stating
plainly: 429 files, every one of them traceable to a commitment the programme has made.

---

### 4.5 Non-functional requirements discharged by content

`05-06` carries 104 `NFR-` identifiers. Thirty-one are discharged **wholly or partly by content**
rather than by code. If the content does not exist, the NFR is unmet regardless of the build.

| NFR | Obligation | Discharged by | Status |
|---|---|---|---|
| `NFR-007` | RPO 15 min / RTO 2 h | `OP-012` playbook | ⚠ **No `dr` environment exists** — `AUDIT-017` `OP-02` |
| `NFR-036/037/047` | Offline 24 h, sync 30 s, battery < 12% | `UI-009`, `TS-015`, `HC-004` | Content exists; field test unresourced |
| `NFR-041` | Bulk operations give progress feedback | `UI-008` | ✅ Content exists |
| `NFR-048` | Payment availability 99.95%, multi-gateway failover | `UI-039`, `AP-009`, `OP-014` | ⚠ Three availability commitments do not reconcile — `AUDIT-016` `AP-06` |
| `NFR-049` | Planned maintenance windows | `OP-005` | ✅ Content exists |
| `NFR-064` | SoD enforced at assignment | `SP-006` | ✅ `SOD-01`…`SOD-60` registered |
| `NFR-072` | Security incident response with breach assessment | `LG-021`, `OP-004`, `OP-016` | ✅ Content exists |
| `NFR-086`, `086a/b/c` | Split residency; Bangladesh-resident sensitive data | `LG-012`, `AP-012` | ⚠ **No lawful DR path exists** — `AUDIT-017` `OP-01` |
| `NFR-088`–`NFR-092` | **Used for two different requirements each** | — | ❌ **`AUDIT-016` `AP-02`.** An instruction to satisfy `NFR-092` is ambiguous |
| `NFR-095`, `097`–`100` | PDPA obligations; Mushak 9.1 filing | `LG-008`–`LG-010`, `MD-037`, `DT-014` | ⚠ Filing basis contested — `RF-008` `ST-03` |
| `PS-03` | Bengali and English throughout | Category 11 `BN` entire | ⚠ `common.*` namespace has no Bengali owner — `AUDIT-012` `BN-01` |
| `PS-04` | WCAG 2.1 AA | `CG-011`, `UI-010`, `TS-016` | ⚠ No accessibility reviewer — `AUDIT-014`. Standard one revision behind — `RF-008` `ST-11` |
| `PS-08` | Offline-capable `P02`, `P09`, `P11` | `UI-009`, `KB-016`, `TS-015` | ✅ Content exists |
| `PS-09` | Every error states what happened and what to do next, in the user's language | `UI-004`, `AP-006`, `BN-010` | ⚠ 289 Bengali strings have no English source row — `AUDIT-012` `BN-18` |
| `IP-04`, `IP-08`, `IP-09`, `IP-10` | Idempotency, versioned contracts, manual fallback, minimisation | `AP-004`, `AP-002`, `OP-014`, `AP-012` | ⚠ `INT-013` omitted from the P0 fallback register — `AUDIT-017` `OP-03` |

---

### 4.6 Acceptance criteria — and the handover to Category 13

| Measure | Value |
|---|---:|
| `AC-` rows across the 67 module §15 sections | **1,308** |
| `AC-` rows across the 12 portal §15 sections | **260** |
| **Total acceptance criteria** | **1,568** |
| Content files whose purpose is to make an `AC-` executable | 18 (`TS-001`–`TS-018`) |
| `AC-` identifiers cited in content `traces_to:` | **fewer than 40** |

**`AC-nn` is file-local, not a namespace** (`RF-001` §4.2.1). `AC-06` in `M09` and `AC-06` in
`M16` are unrelated. Any matrix built on the bare identifier would be wrong. A qualified form —
`M09/AC-06` — is required and is not in use anywhere.

**Ruling `TR-D6`:** acceptance criteria are cited as `<Mnn|Pnn>/AC-nn`. `TS-001` adopts the
qualified form before writing the first script; retrofitting it after 1,568 scripts exist is not
feasible. Carried to `RF-006` as decision `CD-05` and to `RF-007` as `BL-05`.

---

### 4.7 Business rules that cannot execute without content

`05-05` carries **1,358** distinct `BRU-` identifiers. A subset are *hard blocks* that evaluate
against a dataset or a text that is content, not code. Where that content is absent or wrong, the
rule either cannot run or runs against nothing.

| Rule | Blocks | Content it evaluates | Status |
|---|---|---|---|
| `BRU-SRM-01` | Order creation without device identity | `MD-021` device catalogue | ✅ Written |
| `BRU-SRM-02` | Warranty claim on an ineligible device | `MD-031` warranty catalogue | ✅ Written |
| `BRU-SRM-03` | Contract order outside the covered-asset list | `MD-032` contract catalogue | ✅ Written |
| `BRU-SRM-04` | Completion without a passed quality checklist | `DT-008` checklist record | ✅ Written |
| `BRU-SRM-06` | Repeat order within 30 days not flagged as rework | `MD-025` resolution codes | ✅ Written |
| `BRU-SRM-07/08` | Estimate above BDT 5,000 without documented approval | `DT-005`, `UI-038` | ✅ Written |
| `BRU-SRM-09` | Assignment of an uncertified technician to brand warranty work | `MD-011` certification register | ✅ Written |
| `BRU-SRM-10` | Gold/Diamond priority-1 SLA | `MD-034` loyalty tiers, `MD-028` SLA | ✅ Written |
| `BRU-SRM-11` | Parts issue against an unapproved paid repair | `MD-022` part master | ✅ Written |
| `BRU-SRM-16` | Uncollected device abandonment with statutory notice | `LG-013`, `DT-009` | ⚠ Limitation period undecided — `AUDIT-013` |
| `BR-STD-04` | Rule violation without cause and remedy in the user's language | `UI-004`, `BN-010` | ⚠ `PS-09` gap above |
| `BR-STD-06` | Override without a logged reason | `MD-026` reason codes, `UI-007` | ✅ Written |
| `BRU-MKP-*` | Seller transacting before verification | `LG-004`, `SP-024`, `EO-002` | ❌ **`SP-024` names `LG-018` as the seller agreement in five places** — `AUDIT-018` `EO-08` |
| `BRU-ECM-*` | — | — | ❌ **Duplicates six `BRU-MKP-` rules under different identifiers** — `AUDIT-018` `EO-02` |
| *(none)* | `M40`, `M42` | — | ❌ **`05-05` carries no rule for either module** — 40 rules governing partners, franchisees, resellers and the whole supply base do not exist |

---

### 4.8 What this matrix cannot yet do

Stated so that a reader does not credit it with more than it has.

| Cannot | Because | Unblocked by |
|---|---|---|
| Answer "what content depends on `FR-WTY-018`?" | L4 reverse index needs `05-01` to be a register | `AF-06` restatement |
| Give a requirement-level coverage percentage | Same | `AF-06` |
| Give requirement-to-**test-script** coverage | `TS-001` has not adopted `TR-D1` | `TS-001` v1.1 |
| Trace acceptance criteria unambiguously | `AC-nn` is unqualified | `TR-D6` / decision `CD-05` |
| Report `M40`/`M42` rule coverage | `05-05` has no rules for them | `AUDIT-018` `EO-02` |
| Distinguish "content exists" from "content is sufficient" | Sufficiency is a judgement | `RF-004`, `RF-005` |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `05-01` | The feature register; its restatement unblocks L4 |
| `05-05`, `05-06`, `02-02`, `04-00`, `06-02` | Own the requirement, rule, NFR, module, portal and gate spaces |
| `RF-001` | Defines the identifier families this matrix counts |
| `CG-008` | The Definition of Done item this matrix answers |

| Depended on by | Why |
|---|---|
| `RF-004`, `RF-005` | Take their coverage counts from §4.3 |
| `TS-001` | Takes `TR-D1` as its denominator |
| `06-02` `G4-10` | Answerable only from here |
| Every content file at gate `G2` | Traceability check |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **Every wave boundary**, and on any change to `05-01`, `05-05` or `05-06` |
| Regeneration rule | §4.2, §4.3 and §4.4 are **regenerated by extraction**, never edited (`CP-11`, `CM-R2`, `TR-D5`) |
| Trigger for out-of-cycle review | A new module or portal; a requirement family renamed; `AF-06` closed; a category declared complete |
| Owner | Programme Content Lead with QA Lead |
| Escalation | A requirement family falling to zero content coverage is a **wave-gate blocker**, escalated to the CTO the same day |

---

## Approval Record

| Gate | Required for Class E | Reviewer | Status |
|---|:--:|---|---|
| G1 Editorial | ● | Content Design | Not started |
| G2 Factual | ● | QA Lead with Enterprise Architecture | Not started |
| G3–G6 | ○ | — | Not required |
| Final approver | — | Programme Content Lead | **Unappointed** |

---

## Open Items

| # | Item | Owner | Blocks |
|---|---|---|---|
| `RF-003-OI-01` | **`AF-06` — `05-01` restatement.** This file supplies the counted answer; only the CTO can restate another repository's document | CTO | L4 traceability; `G4-10` at full precision |
| `RF-003-OI-02` | **`TR-D6` / `CD-05` — acceptance criteria are unqualified.** Must be fixed before `TS-001` writes the first script | QA Lead | 1,568 acceptance criteria |
| `RF-003-OI-03` | **Four families assessed *not acceptable*: `M37`, `M38`, `M43`, `M47`** | Module business owners | Build readiness at their waves |
| `RF-003-OI-04` | **`FR-POR-` has no `BRU-POR-`** — 358 portal requirements with no business rules | Enterprise Architecture | `RF-005` go-live gate |
| `RF-003-OI-05` | **`05-05` carries no rule for `M40` or `M42`** | Enterprise Architecture | `AUDIT-018` `EO-02` |
| `RF-003-OI-06` | **`NFR-088`–`NFR-092` each mean two things** | CTO | Any instruction citing them |
| `RF-003-OI-07` | **`UI-002`/`003`/`004`/`006`/`007`/`008`/`010`, `DT-001`, `MD-027`, `TS-002` under-declare their portal scope** | Content Design Lead | Impact analysis on portal change |
| `RF-003-OI-08` | **No Programme Content Lead appointed** | CEO | Final approval |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; register table and maintenance procedure added per `CG-009` §3
- [x] Requirement denominator **enumerated**, with scope and instant, and reconciled against all four figures in circulation
- [x] Traceability granularity stated honestly (§4.1) rather than implied
- [x] All 67 module families and the portal family mapped to content, with counts from extraction
- [x] Both failure directions reported — uncovered requirements (§4.4.2) and content with no requirement (§4.4.3)
- [x] NFR, acceptance-criteria and business-rule coverage stated
- [x] Limitations stated (§4.8)
- [x] Six rulings `TR-D1`…`TR-D6` recorded and carried to `RF-006`
- [x] All internal links resolve
- [x] Bengali counterpart — n/a (`bilingual: no`, `CG-010` §3.2)
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)
- [ ] **`AF-06` closed and L4 index built** — outstanding, `RF-003-OI-01`
- [ ] **Named approver recorded** — outstanding, `RF-003-OI-08`

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
