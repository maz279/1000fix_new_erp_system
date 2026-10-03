---
id: GV-007
title: Estimation Model & Resource Plan
category: 00 — Programme Governance & Control
code: GV
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Programme Director
approver: ERP Steering Committee, for Board noting
standards_basis: ISO 21502:2020 §7.6 resources · PMBOK Guide 7th Edition (Planning & Measurement) · PRINCE2 7th Edition (2023) · AACE International Recommended Practice 17R-97 estimate classification · Three-point / PERT estimation
traces_to: PGD-000 GV-007 · findings PGD-A1-05 (OPEN), AF-08, AF-09, H2-08, R-04 · decisions D-014, D-016, D-021
depends_on: GV-001, GV-003, GV-004, GV-006
verified_on: 2026-08-18
enumerated_on: 2026-08-18 02:06 (+06)
priority: P0
needed_by: Now
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# GV-007 — Estimation Model & Resource Plan
# 1000FiX ERP System & Portal Suite v2.0

### Category 00 · Code `GV` · AACE 17R-97 · PMBOK 7 · ISO 21502:2020

---

> **This document sizes the two work streams that audit `PGD-A1-05` records as
> *"commissioned and unbudgeted"*, and it is the precondition for `GV-008` and for the Board taking
> `D-014`.** `AUDIT-001` recommendation `R-04` requires exactly this: *"size the two unbudgeted work
> streams — 127 guiding documents and ~660–1,500 screens — in `GV-007`, and absorb them into
> `CO-005` before `GV-008` goes to the Board."*
>
> The estate already carries four effort figures. **This document does not add a fifth.** It states
> the method, applies it to work nobody has sized, and labels every output with its estimate class
> and its uncertainty band.

---

## 1. Purpose

This document states how the programme derives effort, applies that method to everything the
programme must do, and converts the result into a resource plan — who is needed, when, and where
they come from.

It exists because the programme has an effort *number* with no *method*. Three audits have found
the number wrong in the same direction each time, and none could say why, because there was no
model to interrogate. A number without a method cannot be corrected; it can only be replaced by
another number, which is what has happened three times.

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | The estimation method, its classes, and the accuracy band claimable at each class |
| 2 | **Calibration against the programme's own estimating history** — the observed bias and its cause |
| 3 | The build estimate: 1,842 PW, counted |
| 4 | The content estimate: 520–775 PW, carried and reviewed |
| 5 | **The guiding-document estimate — new. `PGD-A1-05` work stream 1** |
| 6 | **The screen-design estimate — new. `PGD-A1-05` work stream 2** |
| 7 | The consolidated programme effort position |
| 8 | The resource plan: squad model, role mix, ramp, hiring lead times |
| 9 | Demand against supply, and the gap |
| 10 | **Business-side capacity** — the binding constraint nobody has sized |
| 11 | Re-estimation triggers and estimation governance |

**Explicitly out of scope:**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| Converting effort to money | `GV-008` | Effort and cost are separate baselines. A rate change must not look like a scope change |
| The schedule these resources execute | `GV-004` | `GV-004` consumes this document's output |
| Total cost of ownership including run costs | `CO-005` | TCO includes licences, infrastructure and third-party costs beyond people |
| Sprint estimation, story points, velocity | `BE-008` | Programme estimation and sprint estimation are different instruments at different altitudes |
| Vendor pricing and commercial rates | `CO-002`, `CO-003` | This document estimates effort; the contract prices it |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| **Board** | The evidence for `D-014`. The counted position, its method, and its uncertainty |
| **CFO** | The input to `GV-008` and `CO-005` |
| **Steering Committee** | The resource plan they must fund, and the gap they must close |
| **Programme Director** | The operating plan for hiring and squad formation |
| **HR Director** | The hiring ramp and its lead times |
| **Implementation vendor** | The basis on which the Company believes the work is sized |

---

## 2. Basis and Method

### 2.1 Standards conformance

| Standard | Concept | How this document conforms | Departure |
|---|---|---|---|
| **AACE International RP 17R-97** | Estimate classification 1–5 by definition maturity, with an accuracy range per class | §3.2 assigns every estimate in this document a class and publishes its band. **No estimate is quoted without its class** | AACE is a process-industry practice. Adopted for its discipline — the accuracy bands are re-derived for software in §3.2 rather than taken from the standard |
| **PMBOK Guide 7th Edition** | *Planning* and *Measurement* performance domains; analogous, parametric and bottom-up estimating; three-point estimation | §3.1 names the technique used per work stream | None |
| **ISO 21502:2020** §7.6 | Resource planning: identify, acquire, develop, manage | §7 resource plan | None |
| **PRINCE2 7th Edition (2023)** | Tolerance; the *People* integrated element | §7.5 capacity gap expressed against tolerance | None |
| **Three-point / PERT** | `E = (O + 4M + P) / 6`; σ = (P − O) / 6 | §5.3 and §6.3 for the two new estimates | Applied to the two unestimated streams only. The build figure is **counted**, not estimated, and PERT does not apply to a count |

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| Module and portal specifications | `../../1000fix_ERP_Module/03_Modules/**/M*.md`, `P*.md` | **The `Effort estimate` row of all 79 files, directly summed** |
| Category H Audit | `../../1000fix_ERP_Module/00_Governance_and_Charter/00-07` H2-08 | 1,513 PW measured; **the per-category variance analysis that calibrates §4** |
| Executive Summary §2 | `../../1000fix_ERP_Module/00_Governance_and_Charter/00-02` | The 23% Category A under-estimate; the correction-factor mechanism |
| Content & Repository Integrity Audit | `../../project_content/_AUDIT/AUDIT-001` `AF-09` | 452 content files at 2,595–3,875 person-days |
| Content Master Index | `../../project_content/1000FiX_ERP_Content_Master_Index.md` | The content register and its effort basis |
| Implementation Roadmap §4 | `../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-01` | Team composition by wave and business-side commitment |
| Register Integrity Audit | `../_AUDIT/PGD-AUDIT-001` `PGD-A1-05` | The two unbudgeted work streams and the ~660–1,500 screen inference |
| Master Register | `../PGD-000_Master_Register_of_Project_Guiding_Documents.md` | The 140-document set to be sized |

### 2.3 Audit findings this document closes

| Finding | Source | Severity | How this document closes it |
|---|---|:--:|---|
| **`PGD-A1-05`** | `PGD-AUDIT-001` | **High, OPEN** | §5 sizes the 127 guiding documents at **225–520 PW**; §6 sizes screen design at **95–325 PW**. Both were previously *"not estimated, in no plan"* |
| `R-04` | `PGD-AUDIT-001` | — | Both streams sized and handed to `GV-008` and `CO-005` |
| `AF-08` | `AUDIT-001` | High | §4.2 retires the 1,302 PW figure and states one counted position with its method |
| `AF-09` | `AUDIT-001` | High, escalated | §5.1 carries the content estimate into the consolidated position rather than leaving it escalated |
| `H2-08` | `00-07` | High | §4.4 supplies the estimation *model* whose absence made the variance unarbitrable |
| `D-016` | `GV-003` | — | §4.3 answers whether portal effort is inside or outside the baseline: **outside every figure ever published** |
| `RSK-036` | `00-04` | Critical | Provides the estimation basis the risk's mitigation requires |

---

## 3. The Estimation Model

### 3.1 Techniques, and when each is used

| Technique | When used | Applied to |
|---|---|---|
| **Direct count** | A specification exists and carries an effort figure | Build — 79 specifications, `Effort estimate` row |
| **Analogous** | A comparable body of work has a measured rate | Content — calibrated against the 452-file content register |
| **Parametric** | A driver quantity and a rate per unit exist | Guiding documents (per document by class); screens (per screen by uniqueness) |
| **Bottom-up** | Work can be decomposed to task level | Resource plan §7; wave capacity `GV-004` §5 |
| **Three-point / PERT** | Uncertainty is material and must be published | The two new estimates, §5.3 and §6.3 |
| **Reserve analysis** | Contingency must be derived, not asserted | §8.2 |

> **Rule `EM-01` — count before you estimate.** Where a specification exists, its effort figure is
> **counted**, not re-estimated. Rule `RG-06`. This is why §4.1 is a sum and not a model.

### 3.2 Estimate classes

Every effort figure in this document carries a class. **A figure quoted without its class is not a
figure from this document.**

| Class | Definition maturity | Accuracy band | Use |
|:--:|---|---|---|
| **1** | Specification complete and counted | **−5% / +10%** | Contractual commitment |
| **2** | Specification complete, effort estimated by the specifier | **−10% / +25%** | Budget baseline |
| **3** | Scope enumerated, effort parametric from a calibrated rate | **−25% / +50%** | Planning; funding envelope |
| **4** | Scope enumerated, rate uncalibrated | **−35% / +75%** | Order of magnitude; **not for commitment** |
| **5** | Scope inferred, not enumerated | **−50% / +100%** | Awareness only |

> The bands are the accuracy that may be *claimed*, not the accuracy that has been *achieved*. §3.3
> shows the achieved accuracy, which is worse.

### 3.3 Calibration — what this programme's estimates have actually done

The single most valuable estimating asset the programme has is its own error history, recorded in
`00-07` H2-08. It is used here as a correction factor rather than as an apology.

| Observation | Estimated | Actual | Variance |
|---|---:|---:|---:|
| Category A effort (`00-02` §2) | 168 PW | **206 PW** | **+23%** |
| Programme requirements (`SB-2` → counted) | 1,180 | **2,930** | **+148%** |
| Programme build effort (`SB-2` → counted, 65 files) | 834 PW | **1,513 PW** | **+81%** |
| Programme build effort (`SB-2` → counted, 79 files incl. portals) | 834 PW | **1,842 PW** | **+121%** |

**Per-category requirement variance** — the pattern that makes this correctable:

| Category | Nature | Variance |
|---|---|---:|
| F — Asset, Equipment & Facilities | Asset lifecycle, statutory registers | **+73%** |
| H — People & Workforce | Labour Act, payroll, statutory returns | **+52%** |
| I — Governance, Risk, Quality | ISO 9001, GRC, records | **+44%** |
| C — Commercial, Pricing & Revenue | Contractual, VAT, settlement | **+39%** |
| G — Finance & Treasury | NBR, Mushak, BEFTN | **+29%** |
| J — Data, Analytics & Intelligence | Operational | **+12%** |
| D — Circular & Asset-Based | Operational | **0%** |

> **Calibration factor `CF-01`.** *Requirement counts are under-estimated by 29–73% wherever a
> category carries statutory, contractual or master-data obligations, and are accurate where the
> work is purely operational.* Effort tracked closer than count (+15% aggregate at H2-08) because
> statutory requirements are numerous but individually small — most resolve to configuration in a
> versioned rule pack rather than to new code.
>
> **Applied in this document:** the guiding-document estimate (§5) is weighted toward the upper
> band for the `SC` (security, privacy, compliance), `DA` (data governance) and `CO` (commercial)
> categories, because those are the statutory-obligation categories where `CF-01` predicts
> under-estimation.

### 3.4 The unit

| Unit | Definition |
|---|---|
| **PD** — person-day | One person, one working day, net of leave and public holidays |
| **PW** — person-week | **5 PD.** The programme's stated unit |
| **Team-week** | One FTE for one calendar week, **gross** — before the delivery factor |
| **Effective PW** | Team-weeks × the delivery factor (`GV-004` §5.1: **0.78**, assumption `GV-004-A1`) |

> **Rule `EM-02` — never compare PW to team-weeks directly.** The estate's plans do exactly this,
> which is why `M-09` went unanswered for six days: 1,842 PW of work against 1,395 team-weeks of
> people looks like a 32% gap and is actually a 69% gap once the delivery factor is applied.

---

## 4. Work Stream 1 — Build

### 4.1 The counted position

Directly summed from the `Effort estimate` row of every specification, enumerated
**2026-08-18 02:06 (+06)**. **Estimate class 2** — the specifications are complete; the effort
figures within them were estimated by their specifiers.

| Component | Files | Effort | Class |
|---|---:|---:|:--:|
| Category A — Service Delivery & Operations | 7 | 206 PW | 2 |
| Category B — Customer Engagement & Experience | 7 | 148 PW | 2 |
| Category C — Commercial, Pricing & Revenue | 9 | 262 PW | 2 |
| Category D — Circular & Asset-Based Business | 3 | 60 PW | 2 |
| Category E — Supply Chain & Inventory | 6 | 119 PW | 2 |
| Category F — Asset, Equipment & Facilities | 5 | 114 PW | 2 |
| Category G — Finance & Treasury | 8 | 185 PW | 2 |
| Category H — People & Workforce | 7 | 124 PW | 2 |
| Category I — Governance, Risk, Quality & Knowledge | 4 | 78 PW | 2 |
| Category J — Data, Analytics & Intelligence | 4 | 97 PW | 2 |
| Category K — Platform & Technology | 7 | 151 PW | 2 |
| **Module subtotal** | **67** | **1,544 PW** | **2** |
| **Portals and applications `P01`–`P12`** | **12** | **298 PW** | **2** |
| **Build total** | **79** | **1,842 PW** | **2** |

**Verification** *(regenerated from the rows above per `PG-M10`)*: 206 + 148 + 262 + 60 + 119 +
114 + 185 + 124 + 78 + 97 + 151 = 1,544 ✓; 1,544 + 298 = **1,842** ✓.

Applying the class 2 band (−10% / +25%): **1,658 – 2,303 PW**.

### 4.2 Reconciling the four figures

| Figure | Source | Basis | Disposition |
|---:|---|---|---|
| 834 PW | Approved business case | 30 modules, estimated | **Superseded.** It is `SB-2`'s figure and `SB-2` is superseded |
| ~1,302 PW | `02-05` revision note | 206 PW measured + remainder estimated | **Retired** at this issue, per `AF-08` remediation |
| 1,513 PW | `00-07` H2-08 | 65 module files, counted | **Superseded** — it excludes `M66`, `M67` and all 12 portals |
| **1,842 PW** | This document | **79 files, counted 2026-08-18 02:06** | **Current** |

> **There is now one build figure, not four.** The others are recorded here so that a reader
> encountering them elsewhere can place them, which is what `AF-08` asked for.

### 4.3 The portal finding — answering `D-016`

Every effort figure the programme has published was derived from **module** identity tables. The
twelve portal specifications each carry their own `Effort estimate` row:

| Portal | PW | | Portal | PW |
|---|---:|---|---|---:|
| `P01` Customer Self-Service Portal & Mobile App | 42 | | `P07` Marketplace Seller Portal | 34 |
| `P02` Technician Mobile Application | 40 | | `P08` Brand Partner Portal | 18 |
| `P03` Admin Operations Portal | 30 | | `P09` Logistics & Rider Application | 22 |
| `P04` Corporate B2B Portal | 26 | | `P10` Contact Centre Agent Console | 22 |
| `P05` Vendor & Supplier Portal | 18 | | `P11` Field Auditor & Quality Application | 16 |
| `P06` Analytics & Executive Dashboard | 16 | | `P12` Partner & Referral Portal | 14 |
| | | | **Total** | **298** |

**These are not double-counted inside the module figures.** `06-01` §4 staffs Flutter/Mobile and
Frontend developers as distinct roles across seven waves, and `02-05` §5.4 lists the four Flutter
applications and six Next.js portals as separate custom-development deliverables. The work is real,
specified, staffed and estimated — and it has never been in a total.

> **Answer to `D-016`: outside.** The 298 PW is additional to 1,544 PW, not contained within it.
> The build baseline is understated by **22%** before content, documents or design are considered.

### 4.4 Why the original model failed

Recorded because `H2-08` diagnosed it and the diagnosis is reusable:

| Cause | Evidence | Correction |
|---|---|---|
| **Scope grew; the model did not re-run** | 11 → 30 → 67 modules against one 834 PW model | `EM-03`: re-estimate at every scope baseline change (`GV-006`) |
| **Statutory obligations were under-counted** | `CF-01` — +29% to +73% in statutory categories | Weight statutory categories upward at estimate time |
| **A correction factor was applied to estimates instead of counting** | `00-02` §2 applied Category A's +23% to the remaining categories | `RG-06` / `EM-01`: count once specifications exist |
| **Deliverables outside the module set were never in the model** | Portals (298 PW), content (520–775 PW), documents, design | `EM-04`: the estimate covers the **WBS** (`GV-004` §3), not the module register |

---

## 5. Work Stream 2 — Content, and Work Stream 3 — Guiding Documents

### 5.1 Content — carried and reviewed

| Attribute | Value |
|---|---|
| Source | `AUDIT-001` `AF-09` |
| Scope | **477 content files** *(the register estimated 452; enumerated 477 at 2026-08-18 02:06)* |
| Effort | **2,595 – 3,875 PD = 520 – 775 PW** |
| Estimate class | **3** — scope enumerated, parametric from a rate |
| Implied rate | 5.7 – 8.6 PD per file |
| Sanity check | 520–775 PW against 1,842 PW build = **28–42%**. Published ERP practice puts data, training, change and documentation at a third to a half of total programme effort. **Consistent** |
| Status | ✅ Carried into §7. `AF-09` moves from *escalated* to *absorbed* |

> **Note on the file count.** The estimate was built against 452 files; 477 exist. Rather than
> re-scale (which would create a new figure with no new method), the band is retained and the
> 25-file difference is absorbed within the class 3 band (−25% / +50%). Recorded so the discrepancy
> is visible.

### 5.2 Guiding documents — sizing `PGD-A1-05` work stream 1

**127 documents unwritten** of the 140 registered — 140 less 2 that exist elsewhere
(`CO-001` RFP, `BM-001` `06-02`) and less the 11 Category 00 documents issued at this date.

**Method:** parametric, by document class, with a rate band per class. **Estimate class 3.**

| Class | Definition | Documents | PD each (O / M / P) |
|:--:|---|---:|---|
| **H** — heavyweight | Requires derivation across the whole estate: consolidation, tracing, or machine-readable output. `RQ-001` SRS, `RQ-003` fit-gap, `RQ-004` RTM, `AR-001` SAD, `AR-003` SDD, `DA-001` schema, `DA-002` data dictionary, `IN-002` OpenAPI, `IN-003` event catalogue, `SC-002` threat model, `SC-003` DPIA, `SC-004` IAM design, `QA-001` test strategy, `QA-003` test design, `MG-001` migration strategy, `MG-002` legacy profiling, `MG-003` ETL design, `PE-001` network, `PE-003` IaC, `PE-004` CI/CD, `UX-001` design system, `UX-003` screen inventory, `BE-005` CD register, `RR-006` cross-reference index | **24** | 15 / 24 / 40 |
| **S** — standard | A designed artefact for one domain, derived from existing material | **55** | 8 / 11 / 15 |
| **L** — register or standard | A controlled list, convention or policy | **48** | 3 / 5 / 8 |
| | | **127** | |

**Three-point calculation** `E = (O + 4M + P) / 6`:

| Class | n | O (PD) | M (PD) | P (PD) | E per doc | **Total E (PD)** | σ per doc |
|:--:|---:|---:|---:|---:|---:|---:|---:|
| H | 24 | 15 | 24 | 40 | **25.2** | **604** | 4.2 |
| S | 55 | 8 | 11 | 15 | **11.2** | **613** | 1.2 |
| L | 48 | 3 | 5 | 8 | **5.2** | **248** | 0.8 |
| **Authoring** | **127** | | | | | **1,465 PD** | |
| **Review & approval @ 20%** | | | | | | **293 PD** | |
| **Total** | | | | | | **1,758 PD** | |

**= 352 PW expected.** Applying the class 3 band (−25% / +50%): **264 – 528 PW**.

**Cross-check against `CF-01`.** The `SC` (11 documents), `DA` (9) and `CO` (6) categories carry
statutory and contractual obligations where the calibration factor predicts under-estimation of
29–73%. Those 26 documents contribute roughly 300 PD at the expected value; a +40% correction on
that share adds ~120 PD ≈ 24 PW, which sits inside the upper band. **The band is not widened
further** — publishing a wider band to be safe is how an estimate stops constraining anything.

> **Result: 264 – 528 PW, expected 352 PW, estimate class 3.**
> This is **14–29% of the build effort**, which is high for documentation and correct for a
> programme that must produce an SRS, a SAD, an SDD, a database schema, API contracts, a threat
> model, a DPIA, a test strategy, a migration strategy, an IaC standard and a CI/CD design **from
> scratch**, against 2,996 requirements, under a statutory deadline.

### 5.3 What that estimate assumes

| # | Assumption | If false |
|---|---|---|
| 1 | The requirements already exist to derive from — `PGD-000` §2.4: *"specification depth cannot be bought; SRS, SAD, SDD, schema, contracts and pipelines can be produced quickly because the requirements already exist"* | The heavyweight class doubles |
| 2 | The sibling portal SRS (91 KB, January 2026) is reusable as a template and its author is available — `OPP-01` | `RQ-001` moves from 25 PD to 40+ PD and lands later on the critical path |
| 3 | Authors are architects and senior engineers, not technical writers | The rate is wrong in both directions: cheaper people, more rework |
| 4 | Review is 20% of authoring | Understated for `SC` and `DA`, where external legal and security review is required |
| 5 | Machine-readable artefacts (OpenAPI, DDL, Terraform) are counted as authoring | **`IN-002` alone may be 40+ PD**: the estate contains **zero** `.yaml`, `.json`, `.sql`, `.tf` or `.py` files, so every contract is written from nothing |

---

## 6. Work Stream 4 — Screen Design

### 6.1 The driver quantity

`PGD-A1-05` records ~660–1,500 screens as *"an order-of-magnitude inference from 12 portal
specifications and 14 admin workspace copy packs, not a count."* That inference is retained and
labelled: **estimate class 5 on the driver quantity**, which caps the whole estimate's class.

| Input | Value | Class |
|---|---|:--:|
| Screen count | 660 – 1,500 | **5** — inferred, not enumerated |
| Portals and applications | 12 | 1 — counted |
| UI copy packs | 42 | 1 — counted |

> **`UX-003` must convert this to a count before `GV-008` is baselined.** Enumerating the screen
> inventory is itself in the §5.2 heavyweight class and is one of the 24 `H` documents.

### 6.2 Method — reuse-adjusted

A flat rate per screen ignores that portal screens cluster into families. The model separates them:

| Component | Basis | Low | High |
|---|---|---:|---:|
| Design system and component library (`UX-001`) | One-off | 40 PD | 80 PD |
| **Unique screens** — 35% of N, at 1.0–1.5 PD | Wireframe, states (empty/loading/error/populated/offline), field-level spec, review | 231 PD | 788 PD |
| **Variant screens** — 65% of N, at 0.2–0.4 PD | Composed from existing components | 86 PD | 390 PD |
| Interaction prototypes for critical flows (`UX-004`) | 6 flows | 30 PD | 60 PD |
| Bengali layout adaptation (`UX-007`) | +15% on screen work | 48 PD | 177 PD |
| Accessibility conformance pass (`UX-005`) | +10% on screen work | 32 PD | 118 PD |
| **Total** | | **467 PD** | **1,613 PD** |

**= 93 – 323 PW.** Expected value at the PERT mid-point: **~180 PW**.

> **Why Bengali is a separate line and not an afterthought.** Bengali strings run 15–30% longer
> than English (`UX-007`). That is a *layout* consequence, not a translation consequence — it
> changes how many screens must be re-laid out after the copy lands. `CON-05` makes Bengali a
> definition-of-done item, so this line is not optional.

### 6.3 Result

| Attribute | Value |
|---|---|
| Effort | **95 – 325 PW** *(rounded from 93–323)* |
| Expected | ~180 PW |
| Estimate class | **5** on the driver, **3** on the rate → **published as class 5** |
| Precondition for improvement | `UX-003` screen inventory — converts class 5 to class 3 |

> **Rule `EM-05` — an estimate is no better than its worst input.** The rate model here is class 3
> and the screen count is class 5, so the estimate is class 5. Publishing it as class 3 because the
> method is good would be exactly the kind of unearned precision that produced `AF-02`.

---

## 7. The Consolidated Position

### 7.1 Total programme effort

| # | Work stream | Effort (expected) | Band | Class | Status before this document |
|---|---|---:|---|:--:|---|
| 1 | **Build** — 67 modules + 12 portals | **1,842 PW** | 1,658 – 2,303 | 2 | Counted at 1,513 (module-only) |
| 2 | **Content** — 477 files | **~648 PW** | 520 – 775 | 3 | Escalated, never absorbed (`AF-09`) |
| 3 | **Guiding documents** — 127 | **352 PW** | 264 – 528 | 3 | **Not estimated** (`PGD-A1-05`) |
| 4 | **Screen design** — ~660–1,500 screens | **~180 PW** | 95 – 325 | 5 | **Not estimated** (`PGD-A1-05`) |
| | **Programme total** | **~3,022 PW** | **2,537 – 3,931** | **mixed** | |

**Verification** *(regenerated per `PG-M10`)*: expected 1,842 + 648 + 352 + 180 = **3,022** ✓;
low 1,658 + 520 + 264 + 95 = **2,537** ✓; high 2,303 + 775 + 528 + 325 = **3,931** ✓.

### 7.2 Against the approved plan

| Comparison | Ratio |
|---|---:|
| Programme total (expected 3,022 PW) ÷ approved 834 PW | **3.6×** |
| Low band 2,537 PW ÷ 834 PW | **3.0×** |
| High band 3,931 PW ÷ 834 PW | **4.7×** |
| Build alone 1,842 PW ÷ 834 PW | **2.2×** |
| Programme total ÷ the escalated 1,513 PW figure | **2.0×** |

> **`D-014` was escalated on a 1.8× variance. The true variance is 3.0×–4.7×.** Not because the
> earlier measurement was careless — it measured what it set out to measure, module build — but
> because three of the four work streams were outside every model the programme has ever run.
> **This is the number the Board must have before `GV-008` goes to it.**

### 7.3 What is still not in this estimate

Stated so the position is not read as complete:

| Excluded | Why | Owner |
|---|---|---|
| Data migration execution beyond the `MG-*` documents | 48 sources are unprofiled; execution effort is unknowable until `MG-002` completes | Migration lead |
| Infrastructure build and operation | `PE-001`…`PE-009` do not exist; sizing is a shopping list (`02-05` §8) | Platform Engineering |
| Test **execution** effort | `QA-001` does not exist; automation ratio undecided | QA Lead |
| Training **delivery** — 800+ employees, 51+ branches | `CH-002` schedule does not exist | HR Director |
| Hypercare — four weeks after **every** wave go-live, nine times | `SV-005`; recurs at every wave boundary | Service Manager |
| Vendor management, procurement, contract administration | `CO-002`, `CO-003` | CFO |
| **Business-side effort** — §7.5 | Never sized by anyone | HR Director |

> **This estimate covers what can be sized from artefacts that exist.** Seven work streams remain
> outside it. `GV-008` must carry an explicit allowance for them, and `CO-005` must state that the
> TCO is bounded below, not bounded.

### 7.4 Delivery capacity against demand

From `GV-004` §5.2: total effective build capacity across the nine waves is **1,088 PW**.

| | PW |
|---|---:|
| Effective delivery capacity, 36 months, current team model | **1,088** |
| Build demand alone | **1,842** |
| **Build shortfall** | **754** |
| Programme demand (all four streams) | **3,022** |
| **Total shortfall against the current team model** | **1,934** |

> The current team model delivers **59% of the build** and **36% of the programme**.

**Converting the shortfall to headcount**, with the working shown:

| Gap | PW | ÷ 0.78 delivery factor = team-weeks | ÷ 156.5 programme weeks = FTE |
|---|---:|---:|---:|
| Build only | 754 | 967 | **+6.2 build FTE**, sustained 36 months |
| Whole programme | 1,934 | 2,479 | **+15.8 FTE**, sustained 36 months |

The programme-wide figure is the less alarming of the two, because content, documentation and
design roles are cheaper per head than senior Odoo developers and are more parallelisable. The
**+6.2 build FTE** is the harder number: `GV-004` §5.2 shows the shortfall concentrated in Waves 1,
2 and 4, and §8.3 shows a 10–16 week hiring lead time for the scarcest of those roles.

### 7.5 Business-side capacity — the constraint nobody has sized

`CON-12` and `RSK-001` both state that **UAT capacity, not developer capacity, paces the
programme**. Nobody has computed it.

| Role | Commitment (`06-01` §4) | Population | Derived demand |
|---|---|---:|---|
| Module business owners | 20% of time | 67 modules across 11 category owners | Each category owner carries **6 modules on average** at 20% — i.e. ~3.3% of their time per module |
| Super-users | 30% during UAT, 10% otherwise | 2–3 per module × 67 modules = **134–201 people** | At 30% during UAT: **40–60 FTE-equivalents concentrated in UAT windows** |
| Branch champions | 4 h/week during rollout | 51+ branches | ~5 FTE sustained W1–W5 |
| Data owners | 20% during migration | ~10 domains | ~2 FTE W1–W5 |

> **134–201 named super-users is the number.** The estate does not contain an organisation chart
> supporting it, `D-002` has not been taken, and `RSK-001` is rated **Critical** with the
> mitigation *"named super-users with time formally protected in their objectives."* **Not one
> super-user has been named.**
>
> A UAT window demanding 40–60 FTE-equivalents from a 500-person organisation is a **10–12%
> organisation-wide productivity draw**, concentrated in a few weeks per wave. That has never been
> put to the CEO, and `D-002` cannot be taken sensibly without it.

---

## 8. Resource Plan

### 8.1 Squad model

| Squad | Scope | Core roles | Waves |
|---|---|---|---|
| Service | Categories A, F | Odoo × 2–3, BA, QA | W1–W8 |
| Commercial | Categories B, C | Odoo × 2–3, BA, QA | W1–W8 |
| Supply Chain | Category E | Odoo × 1–2, BA, QA | W2–W7 |
| Finance | Category G | Odoo finance specialist × 2, BA, QA | W3–W9 |
| People | Categories H, I | Odoo × 1–2, BA, QA | W5–W8 |
| Platform | Category K | Odoo × 2, DevOps × 2, Security | W1–W9 |
| Data | Category J | Data engineer, BI, AI/ML | W4–W9 |
| **Portals & Applications** | 12 `P*` deliverables, **298 PW** | Flutter × 2–3, Next.js × 1–2, UX | W1–W7 |
| **Content** *(workstream 5)* | 477 files | Content designers, localisation, MDM, L&D | W0–W9 |
| **Engineering Definition** *(new)* | 127 guiding documents | Architects, security, data, QA leads | **W0–W3, front-loaded** |

> **The Engineering Definition squad is the one the programme does not have.** 352 PW expected,
> front-loaded because `RQ-001`, `AR-001`, `DA-001`, `BE-005` and `IN-002` are on the critical path
> (`GV-004` §4.2). Staffing it from the delivery squads delays build; not staffing it means build
> proceeds without specifications. That trade-off is `D-021`.

### 8.2 Contingency

Derived, not asserted:

| Component | Basis | Contingency |
|---|---|---|
| Build, Waves 1–4 | v1.0 scope, precedent exists, class 2 estimate | **10%** |
| Build, Waves 5–8 | New business lines, **no delivery precedent** (`RSK-005`) | **20%** — as `00-04` §1.1 already requires |
| Content | Class 3, 25 files above the estimated base | **15%** |
| Guiding documents | Class 3, five stated assumptions (§5.3) | **20%** |
| Screen design | **Class 5** driver quantity | **35%** |
| **Weighted programme contingency** | | **~16%** |

### 8.3 Hiring ramp and lead time

| Role | Additional FTE needed | Lead time | Source |
|---|---:|---|---|
| Senior Odoo developer | +4 to +6 | **10–16 weeks** | Local market; scarce |
| Flutter developer | +1 to +2 | 8–12 weeks | Local market |
| Next.js developer | +1 to +2 | 6–10 weeks | Local market |
| Solution / data architect | +1 | 12–20 weeks | **Scarce.** May require the implementation vendor |
| Security lead | +1 | 12–20 weeks | Scarce; `SC-001`–`SC-011` depend on it |
| Technical authors / architects for engineering definition | +3 to +5 | 8–12 weeks, or vendor | `D-021` |
| Content authors and translators | +4 to +6 | 4–8 weeks | `AF-09` |
| UX designers | +2 to +3 | 6–10 weeks | `UX-001`–`UX-008` |

> **Hiring lead time is on the critical path and is not in `06-01`.** A senior Odoo developer
> needed in Wave 1 must be recruited **before charter approval** to arrive on time. `GV-004` §4.3
> shows a 10–14 week pre-kickoff runway; that runway is exactly long enough to recruit into, and
> only if recruitment starts now.

### 8.4 Build, buy or borrow

| Work stream | Recommendation | Rationale |
|---|---|---|
| Build — Categories A, B, E | **Vendor-led with internal BAs** | Volume work; internal capacity is the constraint |
| Build — Category G Finance | **Internal + Odoo finance specialist** | NBR, Mushak and BEFTN knowledge is local and not transferable |
| Build — Category K Platform | **Internal** | Identity, integration and security are the durable capability |
| Portals & applications | **Vendor-led** | 298 PW of Flutter and Next.js; the skills are hireable and the work is separable |
| Content | **Internal + external translation** | `CG-010` forbids machine translation on customer- and field-facing content |
| Engineering definition | **Internal architects + external review** | Cannot be outsourced — it *is* the specification the vendor builds against |
| Screen design | **External design partner** | 95–325 PW, bounded, and a design system is a transferable artefact |

---

## 9. Estimation Governance

### 9.1 Rules

| Rule | Provision |
|---|---|
| `EM-01` | **Count before you estimate.** Where a specification exists, its effort is counted |
| `EM-02` | Never compare PW to team-weeks without applying the delivery factor |
| `EM-03` | **Re-estimate at every scope baseline change** (`GV-006`) |
| `EM-04` | The estimate covers the **WBS**, not the module register |
| `EM-05` | An estimate is no better than its worst input; publish the worst class |
| `EM-06` | **Every published figure carries its class and its band.** A bare number is not an estimate |
| `EM-07` | A figure is never carried forward between documents. It is recounted, with a timestamp (`RG-06`, `PG-M11`) |
| `EM-08` | Estimate variance is **measured at every wave gate** and fed back as a calibration factor |

### 9.2 Re-estimation triggers

| # | Trigger | Which streams re-estimate |
|---|---|---|
| 1 | `UX-003` screen inventory issued | Stream 4 — class 5 → class 3 |
| 2 | `RQ-003` fit-gap complete | Stream 1 — determines what Odoo already does; **could reduce build materially** |
| 3 | `MG-002` legacy profiling complete | The excluded migration-execution stream becomes estimable |
| 4 | `QA-001` test strategy issued | Test execution becomes estimable |
| 5 | Wave 1 completes | Delivery factor `GV-004-A1` replaced by measurement; all streams re-run |
| 6 | Scope baseline changes | All streams (`EM-03`) |
| 7 | Every wave gate | Variance measured and `CF-01` updated |

> **Trigger 2 is the one that could move the number downward.** `RQ-003` determines, requirement by
> requirement, whether Odoo 19 CE / OCA delivers a capability as-is, by configuration, by extension
> or by build. `02-05` allocates coverage at *layer* granularity (L1 28%, L2 24%, L5 25%) with no
> requirement-level determination. If L1+L2 coverage is higher than the module specifiers assumed,
> build effort falls. **It is the single highest-value estimate-reducing activity available, and it
> is ⛔.**

---

## 10. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `GV-007-D-01` | Whether to publish a fifth effort figure | Refuse (as `PGD-A1-05` warns) · Publish with method and class | **Publish, with method, class and band** | `PGD-A1-05` warns against an *uncontrolled* estimate. An estimate with a stated method, class and band is the opposite. And `R-04` explicitly requires it | One figure, four streams, every component classed |
| `GV-007-D-02` | Whether portal effort is inside or outside | Assume inside · Assume outside · Evidence it | **Outside, evidenced** | `06-01` §4 staffs Flutter and Next.js as distinct roles; `02-05` §5.4 lists them as separate deliverables | Answers `D-016`; build baseline rises 22% |
| `GV-007-D-03` | How to size the guiding documents | Analogous to content (5.7–8.6 PD) · Parametric by class | **Parametric by class** | Content files and an SRS are not the same artefact. A flat rate would put `RQ-001` at 8 PD | 264–528 PW, class 3 |
| `GV-007-D-04` | Whether to publish screen design at class 3 or class 5 | Class 3 (the rate model is good) · Class 5 (the driver is inferred) | **Class 5** | `EM-05`. Unearned precision is the defect `AF-02` describes | The band is wide and honestly so; `UX-003` narrows it |
| `GV-007-D-05` | Whether to size the business-side draw | Leave to `CH-001` · Derive it here | **Derive it here** | `CON-12` names it the binding constraint and `D-002` cannot be taken without it | 134–201 super-users; 40–60 FTE-equivalents in UAT windows |
| `GV-007-D-06` | Whether to state what the estimate excludes | Present as complete · State the seven exclusions | **State them** | An estimate presented as complete when it excludes migration execution, infrastructure, test execution, training delivery and hypercare is the `AF-09` failure repeating | The position is bounded below, and says so |

---

## 11. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | What does `RQ-003` fit-gap actually return? If Odoo 19 CE / OCA covers more than the specifiers assumed, build effort falls materially | Enterprise Architecture | Week 8 | The single largest downward lever on §7.1 |
| `Q-02` | Are the 79 specification `Effort estimate` figures internally consistent in method? They were written by different authors in different cycles | ARB | Week 6 | The class 2 assignment in §4.1 |
| `Q-03` | Is the implementation vendor's rate card compatible with the $348–$564/PW implied by the approved case? | CFO | Before `CO-003` | `GV-008` |
| `Q-04` | Can 134–201 super-users be named from a 500-person organisation? | HR Director + CEO | Week 4 | `D-002`; `RSK-001`; every UAT |
| `Q-05` | Does the effort figure in each module specification include its own testing, or only build? | Module owners | Week 6 | Whether `QA` execution is additive or included |
| `Q-06` | Is hypercare (4 weeks × 9 waves) staffed from the delivery team or separately? `06-01` §5 requires it; no resource line exists | Service Manager | Week 8 | §7.3 exclusion 5 |

---

## 12. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | Both `PGD-A1-05` work streams are sized | §5.2 — 264–528 PW; §6.3 — 95–325 PW |
| `AC-02` | Every figure carries an estimate class and a band | §3.2; §7.1 table |
| `AC-03` | The method is stated per work stream and is reproducible | §3.1; §5.2 three-point table; §6.2 component model |
| `AC-04` | The model is calibrated against the programme's own error history | §3.3; `CF-01` |
| `AC-05` | Counted figures are recounted at the time of writing with a timestamp | §4.1 — 2026-08-18 02:06 (+06) |
| `AC-06` | Every roll-up is regenerated from its rows | §4.1 and §7.1 verification notes |
| `AC-07` | Exclusions are stated | §7.3 — seven work streams |
| `AC-08` | The business-side constraint is quantified | §7.5 — 134–201 super-users |
| `AC-09` | Contingency is derived, not asserted | §8.2 |
| `AC-10` | Re-estimation triggers exist and the downward lever is identified | §9.2; trigger 2 |

**Definition of done.** Complete when every criterion is met, `GV-008` has absorbed §7.1, the Board
has taken `D-014` on this evidence, `UX-003` has converted stream 4 from class 5 to class 3, and
`PGD-000` records `GV-007` as ✅ with a fresh enumeration timestamp.

---

## 13. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | [`GV-001`](GV-001_Programme_Charter_and_Mandate.md) §7 | The charter declines to fix a figure and conditions approval on this document (`CC-04`) |
| Upstream | [`GV-004`](GV-004_Integrated_Programme_Plan_and_Master_Schedule.md) §5 | Supplies the capacity side of §7.4 |
| Upstream | [`GV-006`](GV-006_Scope_Management_and_Baseline_Control_Procedure.md) | `SB-3` is what is being estimated |
| Downstream | [`GV-008`](GV-008_Programme_Budget_and_Cost_Baseline.md) | Converts §7.1 to money |
| Downstream | `CO-005` | TCO absorbs both new streams — `R-04` |
| Downstream | `BM-003` | Business case restates the ratio |
| Downstream | `CO-003` | Statement of Work priced from this |
| Downstream | `BE-008` | Must supply the measured delivery factor and velocity |
| Downstream | `UX-003` | Converts stream 4 from class 5 |
| Downstream | `RQ-003` | The largest downward lever, §9.2 trigger 2 |
| Lateral | `../../1000fix_ERP_Module/00_Governance_and_Charter/00-07` H2-08 | The variance analysis that calibrates §3.3 |
| Lateral | `../../project_content/1000FiX_ERP_Content_Master_Index.md` | The content effort basis |

---

## 14. References

**Within this repository**
[`PGD-000`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md) ·
[`PGD-AUDIT-001`](../_AUDIT/PGD-AUDIT-001_Register_Integrity_Audit.md) `PGD-A1-05` ·
[`PGD-AUDIT-002`](../_AUDIT/PGD-AUDIT-002_Category_00_Governance_Audit.md) ·
[`GV-004`](GV-004_Integrated_Programme_Plan_and_Master_Schedule.md) · [`GV-008`](GV-008_Programme_Budget_and_Cost_Baseline.md)

**Workspace**
`../../1000fix_ERP_Module/03_Modules/**/M*.md`, `P*.md` — `Effort estimate` rows, directly summed ·
`../../1000fix_ERP_Module/00_Governance_and_Charter/00-02` §2, `00-07` H2-08 ·
`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-01` §4 ·
`../../project_content/_AUDIT/AUDIT-001` `AF-09`

**External standards** *(all verified 2026-08-18)*

| Source | Used for |
|---|---|
| AACE International Recommended Practice 17R-97 — cost estimate classification by definition maturity, with an accuracy range per class | §3.2 |
| PMBOK Guide 7th Edition — analogous, parametric, bottom-up and three-point estimating; *Planning* and *Measurement* performance domains | §3.1 |
| ISO 21502:2020 §7.6 — resource planning | §8 |
| PRINCE2 7th Edition (2023) — tolerance; the *People* integrated element | §7.5 |
| PERT — `E = (O + 4M + P) / 6`; σ = (P − O) / 6 | §5.2 |

---

## 15. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Programme Director | Initial issue. **Closes `PGD-A1-05`** by sizing both unbudgeted work streams. Establishes the estimation model, its classes and its calibration factor `CF-01`. States the consolidated programme position at **2,537–3,931 PW (expected 3,022)** against 834 PW approved — **3.0×–4.7×**. Answers `D-016`: portal effort is outside every published figure. Quantifies the business-side draw at 134–201 super-users | *pending Steering Committee* |

---

*`GV-007` · Category 00 · 1000FiX ERP System v2.0 · CONFIDENTIAL — Internal Use Only*
*1000FiX Services Limited · Hotline 16743 · info@1000fix.com · ISO 9001:2015 Certified*
