---
id: PGD-CAT-06
category: 06 — Experience & Interface Design
code: UX
project: 1000FiX ERP System v2.0
version: 2.0
date: 2026-08-18
status: COMPLETE — 8 of 8 authored and audited
owner: Head of Product Design
audit: ../_AUDIT/PGD-AUDIT-006_Category_06_Experience_and_Interface_Design_Audit.md
last_enumerated: 2026-08-18 21:47 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# Category 06 — Experience & Interface Design (`UX`)

> ### ✅ ALL EIGHT AUTHORED AND ISSUED 2026-08-18
>
> Audited the same day in
> [`PGD-AUDIT-006`](../_AUDIT/PGD-AUDIT-006_Category_06_Experience_and_Interface_Design_Audit.md) —
> **26 findings · 6 critical · 19 closed · 7 open.**
>
> **The ✅ is qualified**, as it is for Categories 00, 01, 02 and 03. §0.3 test (d) of `PGD-000`
> requires *"a named owner **and an approval record"***. Owners are named; no approval record exists
> and none can, until `GV-002` constitutes a body that can create one (`PGD-A1-09`, `PGD-A2-25`).

## Purpose

The programme had written **42 UI copy packs** and **had not designed a single screen**. Copy without
layout is a script without a stage: developers invent the interface, twelve portals diverge, and the
copy does not fit the screens it was written for.

This category is the stage. It specifies what every surface renders from, what every screen is, how
every interaction behaves, what accessible means and how it is proved, how the field applications
behave with no connection, how Bengali reshapes every container, and how any of it gets validated
with a real user.

## Documents

| ID | Document | What it delivered | Status | Pri | Needed by |
|---|---|---|:--:|:--:|:--:|
| `UX-001` | **Design System & Component Library Specification** | **Rules `NFR-080` unsatisfiable as written** — five runtimes cannot share one library — and specifies the form that is: *one token source, one contract, five realisations, one conformance suite*. Three-tier DTCG token architecture with a **measured contrast ratio on every colour token**, a Bengali token family with its own floors, a **counted inventory of 68 components**, and twelve checks `CFM-01`…`CFM-12` that make it binding | ✅ | **P0** | **Now** |
| `UX-002` | **Information Architecture & Navigation Model** | Thirteen surface architectures, each ≤ 7 top-level items. Converts `NFR-077` from an unfalsifiable claim into a **route-graph assertion computed per role**. Supplies the estate's **first deep-link scheme** — a route grammar and destinations for fourteen notification classes | ✅ | **P1** | W1 |
| `UX-003` | **Wireframe & Screen Inventory** | **The counted answer to `PGD-A1-05`: 1,404 screens**, from counted drivers. Four-class model finds the estate **56% generated** by `AR-007`'s Odoo view conventions, restating effort at **88–146 PW, expected 109, class 3** — down 39% with the band narrowed from 230 PW to 58. Names all **130 bespoke screens**; allocates the **371 functional areas** across 14 workspaces | ✅ | **P0** | **Now** |
| `UX-004` | **Interaction & Prototype Specification** | **Closes `U-09`** — every drag in the estate enumerated with a single-pointer and a keyboard path, and finds the SC 2.5.7 remedy is also the fix for the < 10-minute dispatch target. Establishes the estate's **first prototype programme**: eight prototypes with a real-user evaluation gate | ✅ | **P1** | W1 |
| `UX-005` | **Accessibility Conformance Design (WCAG 2.2 AA)** | Fixes the target at **55 of WCAG 2.2's 86 criteria** and allocates every one — **44 design-time, 11 build-time, 11 additionally requiring human evaluation**. **Closes `TS-016` `O-05`** by ruling all thirteen surfaces in scope via WCAG2ICT. Specifies the ACR the programme cannot currently produce | ✅ | **P1** | W2 |
| `UX-006` | **Mobile Application UX Specification (offline-first)** | **Closes `AR-010` `Q-02`**, the blocking dependency on APP-01. The two-indicator sync model, the offline capability matrix across four applications, and the **five-element conflict disclosure** with worked cases. Writes the estate's first ISO 9241-210 §5.4 **context-of-use specification** | ✅ | **P0** | W2 |
| `UX-007` | **Bilingual & Bengali Interface Design Standard** | Converts `L-07` from a statement about translation into a **buildable layout standard**: Bengali-first design on the eight Bengali-default surfaces, `VB-007` `BL-02`'s +40% **given a derivation**, the measurement harness four documents have deferred to, and build-time proof by pseudo-localisation | ✅ | **P1** | W1 |
| `UX-008` | **Usability Test Plan & Findings Log** | The validation instrument the `URD`'s user-experience vision has never had. **Every success criterion taken from an existing KPI or NFR**, not invented alongside one. Field-condition and assisted-user protocols; a findings log closed only by re-observation; ISO 25062:2025 reporting | ✅ | **P2** | W2 |

## The five results worth carrying to the Steering Committee

| # | Result | Consequence |
|---|---|---|
| 1 | **`NFR-080` cannot be met as written** (`UXA-01`) | Five runtimes cannot share one component library. The restatement — one token source, one contract, five realisations, one conformance suite — is raised to `GV-003`. **Without the ruling, the requirement would have been marked satisfied and silently breached** |
| 2 | **The screen count went up; the effort went down** (`UX-003` §11) | 1,404 screens against an inferred 660–1,500 — but **782 are generated** by conventions that already exist. **88–146 PW, expected 109**, against `GV-007`'s 95–325 PW expected 180 |
| 3 | **The three most exposed surfaces were outside accessibility scope** (`UXA-12`) | `P02`, `P09`, `P11` — one hand, sunlight, gloves, a helmet — excluded by a requirement phrased *"web portals"*. Now in scope via WCAG2ICT |
| 4 | **The copy pack estate covers ~8%, not "every label"** (`UXA-07`) | 696 keys and 114 screen sections against 1,404 screens. `GV-007` stream 2 was sized against 477 files; the remaining string work was never counted |
| 5 | **Several KPI baselines become unmeasurable at cutover** (`UXA-19`) | Booking conversion, self-service rate, MAU, app rating and AHT all carry targets with no baseline, while `BM-001` claims benefit against them. **The only finding here with an irreversible deadline** |

## What this category found in other people's work

| Finding | Against | Status |
|---|---|---|
| `UI-009` offers a conflict choice `AR-010`'s authority matrix forbids | `UI-009` §3.3 | **Closed by ruling**; 2 keys withdrawn |
| 100 files cite WCAG 2.1 against `RQ-006`'s ruling of 2.2 | 100 files incl. `TS-016` | Open — one coordinated change |
| Deep linking required in 11 files, specified in none | `NT-*`, `P03`, `P06`, `M10` | **Closed** — `UX-002` §7 |
| 920 report definitions, no report-viewing screen | 67 modules `§14` | **Closed** for design; parameter sets escalated |
| Four different values for the entity population | `AR-001`, `RQ-004`, `05-02` | Open — `DA-002` to publish one |
| `CG-010` §12 carries a decision `BN-007` §3 closed | `CG-010` | **Closed** — correction raised |
| Storage-full behaviour specified architecturally, never designed | `AR-010` `F-04` | **Closed** — `UX-006` §7.6 |

## What this category found in its own work

Recorded because a category that hides its own error history cannot ask the programme to disclose
theirs. **Seven defects, all corrected before issue:**

| ID | Defect |
|---|---|
| `UXA-20` | An absence claim overstated — 11 files discuss deep links; none supplies a scheme |
| `UXA-16` | An absence claim wrong — `VB-007` `BL-02` **does** state +40% rendered width. Adopted unchanged and given a derivation |
| `UXA-22` | A roll-up that did not match its rows — the 55-criterion split was 23/21/11 asserted against 44/11 counted |
| `UXA-23` | A register that omitted a row and mis-derived a subtotal |
| `UXA-24` | **Four identifier collisions** — three external (`DC-`, `PD-`, `MV-`), one **internal** (`TYP-` defined twice within the category) |
| `UXA-25` | An estate figure that moved from 680 to 731 during authoring |
| `UXA-26` | `PGD-AUDIT-005` claimed by a concurrent session; this audit yielded to `006` |

## Dependencies

| Direction | Category | Relationship |
|---|---|---|
| Upstream | `01_Requirements` | `RQ-006` `NFR-073`/`077`/`080`; `RQ-008` stories define the screens `UX-003` inventories |
| Upstream | `02_Architecture` | `AR-001` surface set · `AR-007` view conventions (**782 Class G screens depend on them**) · **`AR-010` §6, which this category closes** |
| Upstream | `04_Integration` | `IN-002` API contracts determine what a screen can show |
| Downstream | `07_Build` | Front-end development cannot begin without `UX-001` and `UX-003` |
| Downstream | `08_Quality` | `QA-008` derives from `UX-005`; `TS-016` needs three new script sets |
| Downstream | `13_Training` | Training material describes the screens `UX-003` enumerates |
| Downstream | `15_Benefits` | `BM-001` baselines are `UX-008`'s to establish before cutover |
| Peer | `project_content` | 42 `UI-*` packs, 5 `VB-*` design standards, 18 `BN-*` localisation files, `CG-011`, `TS-015`, `TS-016` |

## The blockers this category cannot clear itself

| # | Blocker | Owner | By |
|---|---|---|---|
| 1 | **No accessibility reviewer** — blocks 68 component contracts, 148 wireframes, every release gate | CTO | **W0** |
| 2 | **W0 token pipeline** into a Wave 1 already at 5.33× capacity | Programme Manager | **W0** |
| 3 | **Participant recruitment has no owner** — every `UX-008` session is unscheduled | HR + Change Lead | **W1** |
| 4 | **Reference-device fleet** (mid-range Android 11, 3 GB) not confirmed procured | Programme Manager | **W1** |
| 5 | **Pre-cutover baselines** have no owner and an irreversible deadline | `BM-001` owner | Before cutover |

## Audience and change frequency

| Attribute | Value |
|---|---|
| Primary audience | Designers, front-end and mobile engineers, business owners, QA, accessibility reviewer |
| Change frequency | **High during W1–W2, then per-surface** |
| Standards basis | WCAG 2.2 AA · WCAG2ICT · DTCG 2025.10 · ISO 9241-11:2018 · ISO 9241-210:2019 · ISO 25062:2025 · Unicode 17.0 · ISO/IEC 25010:2023 |

---

*Category 06 · `UX` · 1000FiX ERP System v2.0 · CONFIDENTIAL*
