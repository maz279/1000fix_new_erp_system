---
id: RF-004
title: Content-to-Module Coverage Map
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Programme Content Lead
author: Programme Content Lead with Enterprise Architecture
reviewers: [CTO, Enterprise Architecture, QA Lead, all Module Business Owners, Programme Office]
approver: Programme Content Lead
content_class: E
purpose: >
  Answers "is `Mnn` ready to build?" as a content question. All 67 modules mapped to the content
  files they require, with the gaps named and owned. Engineering can assess module readiness from
  the specification; nobody can currently assess whether the master data, SOPs, copy, documents,
  training and test scripts a module consumes exist and are approved. Without this map a wave gate
  is passed on the code half of the question, and the content half surfaces during hypercare as
  "the system works but nobody can use it".
traces_to: [02-02, 05-01, 05-05, 06-01, 06-02, CP-04, RF-001, RF-003, RF-005, RF-007, RF-012, CG-008]
priority: P1
wave: W1
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/02_Architecture/02-02_Module_Catalogue_Master_Register.md §Register — 67 modules with code, priority, wave, owner, requirement count and effort
    verified: 2026-08-18
    class: P1
  - source: Extraction of traces_to front matter across all 429 written content files for Mnn targets, run 2026-08-18 — produced the per-module content lists in §4.3
    verified: 2026-08-18
    class: P1
  - source: Extraction of distinct FR- identifiers per module file, run 2026-08-18 — 2,992 across the 67 M*.md files
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md — nine waves. NOTE the Master Index §1 wave windows disagree with 06-01 §3 in all nine rows (AUDIT-018 EO-04)
    verified: 2026-08-18
    class: P1
  - source: project_content/_AUDIT/AUDIT-018_Category_18_EO_Content_Audit.md finding EO-04 — Master Index §1 wave windows disagree with 06-01 §3 and 02-02 in all nine rows, by two to six months
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2026-11-18
---

# RF-004 — Content-to-Module Coverage Map

---

## 1. Purpose

A wave gate asks two questions and answers one.

*"Is the build ready?"* — engineering answers from the module specification, the test results and
the defect profile.

*"Is the content ready?"* — nobody answers. There is no artefact that says `M43 Demand Planning`
consumes `MD-022`, `DM-007`, `KB-009`, `TR-012`, `DT-021`, `TS-004` and `TS-008`, that six of the
seven are written and none is approved, and that **no planner SOP, no planner training and no
planner report exists at all**.

This file is that artefact. It states, for each of the 67 modules:

- the content it consumes, enumerated from declared `traces_to:`
- the content it consumes that **does not exist**
- whether the content it consumes arrives **before or after** the module's own wave
- a single readiness verdict a gate can act on

It is deliberately a **coverage** map, not a completeness map. Every one of the 429 written files
is at status `Draft`; **not one content file in the entire register is `Approved`**. A module
whose content is complete is a module whose content is completely unapproved. §4.6 states what
that means for every gate between now and the first approval.

---

## 2. Scope

**In scope** — all 67 modules `M01`–`M67`; the content files that declare them in `traces_to:`;
the content types each module requires by class; wave alignment between module and content;
readiness verdicts and named gaps.

**Out of scope**

| Excluded | Owner |
|---|---|
| Portal content readiness | `RF-005` |
| Requirement-level traceability and the denominator | `RF-003` |
| Whether a module specification is itself complete | `02-02`, `_MODULE_SET_AUDIT_REPORT.md` |
| Build effort and sequencing | `06-01`, `02-02` |
| Content that is not module-scoped (governance, brand, localisation standards) | `RF-003` §4.4.3 |

---

## 3. Audience

| Reader | Uses this map to |
|---|---|
| **The CTO / Steering Committee at a wave gate** | Take a content verdict per module, with named gaps and owners |
| **A module business owner** | See exactly what content their module depends on and what is missing |
| **The Programme Office** | Sequence content authoring against `06-01` |
| **An implementation vendor** | Know what must exist before their sprint on `Mnn` can start |
| **The Programme Content Lead** | Direct authoring capacity at the modules that will gate first |

---

## 4. Content

### 4.1 How to read the map

| Column | Meaning |
|---|---|
| **Module** | Identifier and name from `02-02` |
| **Pri / Wave** | From `02-02` §Register. Where `02-02` gives a split wave (`W1 / W4`) both are shown |
| **Reqs** | Distinct `FR-` identifiers in that module file, enumerated 2026-08-18 |
| **Content** | Files declaring this module in `traces_to:`, enumerated 2026-08-18 |
| **Verdict** | `READY` · `THIN` · `GAP` · `BLOCKED` — defined below |

**Verdict definitions**

| Verdict | Means |
|---|---|
| **`READY`** | Every content type the module requires exists in draft, and no consuming content arrives after the module's wave |
| **`THIN`** | Content exists but a content type the module genuinely needs is absent. Buildable; not operable at full quality |
| **`GAP`** | A content type the module cannot function without is absent, or the module has fewer than five content files against more than 30 requirements |
| **`BLOCKED`** | A named upstream decision, missing specification or missing register prevents the content from being authored at all |

> **No module can be `APPROVED-READY`.** That verdict does not exist in this file, because no
> content file has passed gate `G5`/`G6` and none is at status `Approved`. §4.6.

---

### 4.2 Summary

| Verdict | Modules | Share |
|---|---:|---:|
| `READY` | **31** | 46% |
| `THIN` | **20** | 30% |
| `GAP` | **10** | 15% |
| `BLOCKED` | **6** | 9% |
| **Total** | **67** | 100% |

| Measure | Value |
|---|---:|
| Modules with **zero** content coverage | **0** |
| Modules with fewer than 5 content files | 4 — `M67`, `M48`, `M47`, `M37` |
| Modules whose consuming content arrives **after** their own wave | **17** — §4.5 |
| Modules blocked by an **unmade decision** | 6 |
| Modules blocked by a **missing specification** | 3 — `M64`/`M33`/`M17` via absent `06-03` |
| Content files that are module-scoped | **378 of 429** |
| Modules at `P0` priority | 12 |
| `P0` modules **not** `READY` | **5** — `M09`, `M15`, `M20`, `M37`, `M51` |

**The headline for a gate.** Five of the twelve `P0` modules are not content-ready, and one of
them — `M37 Product & Service Catalogue`, the spine of all fourteen revenue streams — is a `GAP`
at `W1`.

---

### 4.3 The map

#### Category A — Service Delivery & Operations

| Module | Pri / Wave | Reqs | Content | Verdict | Gap or note |
|---|:--:|---:|---:|:--:|---|
| `M01` Service Request & Order | P0 / W1–W2 | 73 | **53** | `READY` | The most densely covered module in the register |
| `M02` Field Service & Dispatch | P0 / W2 | 64 | **34** | `READY` | `MD-005` zones, `UI-024`, `SP-008`, `TR-009` all present |
| `M03` Service Logistics | P1 / W3 | 42 | **22** | `READY` | |
| `M04` Branch & Front Desk | P1 / W1 | 32 | **17** | `THIN` | No `KB` branch reference set; `SP-032` checklists carry the load alone |
| `M05` Remote Support & MSP | P1 / W5 | 62 | **20** | `THIN` | 62 requirements, one SOP (`SP-011`), no `TR` pack for MSP engineers |
| `M06` Data Services | P2 / W6 | 34 | **24** | `READY` | Strong `LG` coverage — 6 files — appropriate for the risk |
| `M31` Workshop & Depot Repair | P1 / W2 | 55 | **33** | `READY` | 12 `KB` files; the best-served technical module |

#### Category B — Customer Engagement & Experience

| Module | Pri / Wave | Reqs | Content | Verdict | Gap or note |
|---|:--:|---:|---:|:--:|---|
| `M07` CRM & Account Management | P1 / W1 / W4 | 46 | **14** | `THIN` | No `UI` workspace copy traces to `M07`; `UI-032` covers contracts only |
| `M10` Loyalty & Rewards | P1 / W2 | 44 | **12** | `THIN` | `MD-034` tiers exist; no loyalty `HC` article set, no `TR` |
| `M27` Omnichannel Contact Centre | P1 / W4 | 58 | **37** | `READY` | |
| `M32` Conversational AI | P1 / W4 | 38 | **18** | `BLOCKED` | `HC-017` transcript-derived work has **no confirmed lawful basis** under PDPA 2026 — `AUDIT-010` `HC-01` |
| `M33` Customer & Party Master | P0 / W1 | 52 | **20** | `BLOCKED` | `06-03_Data_Migration_Strategy.md` does not exist; all 48 legacy sources unprofiled — `AUDIT-011` `DM-01` |
| `M34` CX, Feedback & Complaints | P1 / W4 | 42 | **17** | `READY` | |
| `M35` Marketing & Demand Gen | P2 / W5 | 40 | **11** | `THIN` | `NT-023` campaign library exists; no `RP` campaign reporting |

#### Category C — Commercial, Pricing & Revenue

| Module | Pri / Wave | Reqs | Content | Verdict | Gap or note |
|---|:--:|---:|---:|:--:|---|
| `M08` Contract Lifecycle | P1 / W4 | 62 | **29** | `BLOCKED` | `DT-031` maps **nine `MD-028` fields that do not exist**, and `MD-028` has no clock start/stop event field — `AUDIT-013` `LG-01`. Service credits cannot be computed |
| `M09` Warranty & Claims | P0 / W4 | 67 | **36** | `THIN` | Strong content; **`MD-017` "17+ brands" remains unverified** (`00-07` H2-12) and `EO-004` per-brand rules depend on it |
| `M11` Pricing & Rate Cards | P1 / W3 / W7 | 52 | **17** | `THIN` | `MD-029` exists; no pricing `SOP`, no approval `TR` beyond `SP-004` |
| `M12` Marketplace & Seller | P1 / W7 | 79 | **27** | `BLOCKED` | Decision `D-03` principal-or-agent unmade; **the marketplace may be unable to pay lawfully** — `AUDIT-018` `EO-01` |
| `M36` Quotation & Estimation | P1 / W3 | 49 | **11** | `THIN` | 49 requirements, three `DT`, no `TR` for estimators |
| `M37` Product & Service Catalogue | **P0 / W1** | 46 | **5** | **`GAP`** | **`MD-019` alone carries a `P0` W1 module feeding all fourteen revenue streams.** No `SP`, no `TR`, no `RP`, no `UI`. `RF-007` `BL-01` |
| `M38` E-Commerce Storefront | P1 / W7 | 56 | **9** | **`GAP`** | 56 requirements; **no `UI` copy pack, no `HC` set, no `NT` templates.** The storefront has no content owner. `RF-007` `BL-02` |
| `M39` Subscription & Recurring | P1 / W4 | 44 | **9** | `THIN` | `MD-033` exists; dunning ladder lives only in `DT-018` |
| `M40` Partner, Channel & Franchise | P2 / W7 | 43 | **20** | `BLOCKED` | **`05-05` carries no business rule for `M40`** — `AUDIT-018` `EO-02` |

#### Category D — Circular & Asset-Based Business

| Module | Pri / Wave | Reqs | Content | Verdict | Gap or note |
|---|:--:|---:|---:|:--:|---|
| `M13` Rental / EaaS | P2 / W6 | 44 | **6** | **`GAP`** | One `DT`, one `SP`, three `TS`. No `UI`, `TR`, `HC` or `MD` beyond `MD-044` |
| `M14` Trade-In & Refurbishment | P2 / W6 | 39 | **15** | `THIN` | Good `DT`/`LG`; no grading `TR` for assessors |
| `M18` E-Waste & Circular Economy | P3 / W8 | 26 | **17** | `THIN` | E-waste **regulated-entity question is undecided** — `AUDIT-013`. EPR targets reach 50% in 2026 — `RF-008` `ST-14` |

#### Category E — Supply Chain & Inventory

| Module | Pri / Wave | Reqs | Content | Verdict | Gap or note |
|---|:--:|---:|---:|:--:|---|
| `M15` Spare Parts & Inventory | P0 / W2 | 54 | **50** | `THIN` | Content is dense; **`MD-022` part master and `DM-007` opening stock both unloaded**, and Category E decision `D-03` (physical count at cutover) is unmade |
| `M16` Procurement & Sourcing | P1 / W3 | 38 | **21** | `READY` | |
| `M41` Warehouse Management | P1 / W3 | 41 | **21** | `READY` | |
| `M42` Supplier Relationship | P1 / W4 | 34 | **20** | `BLOCKED` | **`05-05` carries no business rule for `M42`**; requirement code `FR-SRM2-` is non-conformant — `RF-001` `GL-02` |
| `M43` Demand Planning | P2 / W6 | 32 | **7** | **`GAP`** | **No planner SOP, no planner training, no planning report.** A planning module with no planner content. `RF-007` `BL-03` |
| `M44` Import & Landed Cost | P2 / W6 | 39 | **7** | `THIN` | Correctly waiting on decision `D-04` (recoverable taxes in landed cost) |

#### Category F — Asset, Equipment & Facilities

| Module | Pri / Wave | Reqs | Content | Verdict | Gap or note |
|---|:--:|---:|---:|:--:|---|
| `M17` Device & Asset Registry | P1 / W2 | 52 | **30** | `THIN` | `MD-021` exists; **NEIR/IMEI handling unspecified in content** |
| `M45` Enterprise Asset & Test Equipment | P2 / W5 | 46 | **11** | `THIN` | `MD-046` calibration exists — the ISO 9001 clause 7.1.5 obligation is met |
| `M46` Fleet & Vehicle | P2 / W5 | 45 | **8** | **`GAP`** | `MD-045` only. No fleet SOP, no driver `KB`, no fuel/maintenance `DT` |
| `M47` Facility & Workplace | P3 / W7 | 45 | **4** | **`GAP`** | **Lowest coverage in the register.** 51+ branches, 45 requirements, four content files. `RF-007` `BL-04` |
| `M48` IoT & Predictive Maintenance | P2 / W8 | 50 | **3** | **`GAP`** | No telemetry `MD`, no `OP` runbook, no `RP`. Acceptable at W8; a blocker if pulled forward |

#### Category G — Finance & Treasury

| Module | Pri / Wave | Reqs | Content | Verdict | Gap or note |
|---|:--:|---:|---:|:--:|---|
| `M19` Financial Accounting & GL | P0 / W3 | 46 | **41** | `READY` | `MD-035` CoA, `MD-040` sequences, ten `DT` |
| `M20` AR, Invoicing & Collections | P0 / W3 | 44 | **67** | `READY` | **Highest coverage in the register** — 16 `DT`, 10 `LG`, 9 `EO` |
| `M49` Fixed Assets | P2 / W5 | 35 | **7** | `THIN` | Finance-internal; `MD-044` carries it |
| `M50` Treasury, Cash & Banking | P1 / W3 | 42 | **24** | `READY` | |
| `M51` Tax & Regulatory (Bangladesh) | **P0 / W4** | 45 | **32** | `THIN` | Thirteen `DT` statutory templates written; **26 `DT` files await unwaivable G6 external verification** and the Mushak 9.1 filing basis is contested — `RF-008` `ST-03` |
| `M52` Accounts Payable | P1 / W3 | 39 | **23** | `READY` | |
| `M53` Revenue Recognition & Settlement | P1 / W4 / W7 | 45 | **27** | `BLOCKED` | Depends on `D-03` marketplace principal-or-agent; settlement terms unresolved against the ten-day statutory obligation |
| `M54` Cost Accounting & FP&A | P2 / W6 | 40 | **8** | `THIN` | **No `RP` dashboard traces to `M54`**, yet `RP-010` board pack depends on it |

#### Category H — People & Workforce

| Module | Pri / Wave | Reqs | Content | Verdict | Gap or note |
|---|:--:|---:|---:|:--:|---|
| `M21` Core HR | P1 / W5 | 46 | **26** | `READY` | |
| `M22` Learning & Certification | P2 / W5 | 40 | **44** | `THIN` | All 24 `TR` files trace here. **The Layer 1 statutory induction curriculum for 800+ employees has no owning file** — `TR-025` unregistered |
| `M55` Time, Attendance & Scheduling | P1 / W5 | 52 | **22** | `READY` | |
| `M56` Payroll & Statutory | **P0 / W5** | 54 | **22** | `READY` | `MD-043`, `DT-041`, `SP-021`, `DM-009` all present |
| `M57` Performance & Incentives | P1 / W5 | 42 | **14** | `THIN` | Incentive scheme copy exists (`CM-017`); no incentive `RP` |
| `M58` Talent Acquisition | P2 / W6 | 34 | **7** | `THIN` | `SP-023` and `DT-042` carry the operative process; acceptable |
| `M59` Health, Safety & Wellbeing | P2 / W6 | 42 | **15** | `READY` | `KB-013` ESD/chemical/battery safety is substantial |

#### Category I — Governance, Risk, Quality & Knowledge

| Module | Pri / Wave | Reqs | Content | Verdict | Gap or note |
|---|:--:|---:|---:|:--:|---|
| `M23` Quality Management System | P1 / W5 | 50 | **57** | `THIN` | Densely covered; **ISO 9001:2026 publishes September 2026** and every clause citation re-opens — `RF-008` `ST-12` |
| `M24` Documents & E-Signature | P1 / W3 | 50 | **31** | `THIN` | **No controlled copy of any statutory instrument is held** — `RF-002` `RF-004-OI-04`. `M24` is the system that should hold them |
| `M60` Governance, Risk & Compliance | P2 / W6 | 44 | **28** | `READY` | |
| `M61` Knowledge Management | P2 / W6 | 38 | **42** | `GAP` | All 16 `KB` and 18 `HC` files trace here — but **every `KB` file specifies content that does not exist**: 160 articles, 22 tool guides, 48 reference cards, **775–1,545 specialist hours, unresourced** — `AUDIT-008` `R-07` |

#### Category J — Data, Analytics & Intelligence

| Module | Pri / Wave | Reqs | Content | Verdict | Gap or note |
|---|:--:|---:|---:|:--:|---|
| `M25` Business Intelligence | P1 / W4 | 34 | **19** | `THIN` | **250 KPI identifiers in use against 95 registered**; 44 of 95 baselines absent — `AUDIT-015` `RP-01`, `RP-02` |
| `M26` AI/ML Services | P2 / W6–W8 | 42 | **11** | `THIN` | `SP-033` decision trees and `MD-024` fault codes are the grounding corpus; both exist |
| `M62` Data Platform & Warehouse | P1 / W4 / W8 | 38 | **18** | `READY` | |
| `M63` Process Automation | P1 / W3 | 32 | **5** | `THIN` | Automation lives in `05-05` `AUT-` rules traced through owning modules; acceptable |

#### Category K — Platform & Technology

| Module | Pri / Wave | Reqs | Content | Verdict | Gap or note |
|---|:--:|---:|---:|:--:|---|
| `M28` Integration & Event Platform | **P0 / W1** | 57 | **24** | `BLOCKED` | **14 event names are consumed and do not exist**; no webhook signature scheme; no scope vocabulary; no error-envelope ruling — `AUDIT-016` `AP-01`, `AP-04`, `AP-05` |
| `M29` Identity, Access & Security | **P0 / W1** | 52 | **48** | `THIN` | **Break-glass is documented and does not exist; the 38 access profiles do not exist** — `AUDIT-017` `OP-08`, `OP-10` |
| `M30` Platform Administration | P0 / W1 | 40 | **16** | `READY` | |
| `M64` Master Data Management | P1 / W2 | 34 | **11** | `THIN` | `MD-001` charter and `MD-048` load index exist; **`06-03` absent** blocks the load |
| `M65` Multi-Entity & Localisation | P2 / W9 | 36 | **8** | `THIN` | Category 11 `BN` discharges localisation without naming `M65` — a declaration gap, not a content gap |
| `M66` Internal IT Service Management | P2 / W6 | 30 | **19** | `GAP` | **`M66` lands at W6 while the `P0` support model it carries is needed at W1**, and no paging platform exists at all — `AUDIT-017` `OP-06`. **`NFR-091` requires 67 module runbooks and the register contains none** — `OP-07` |
| `M67` Project & Portfolio Management | P2 / W7 | 32 | **2** | `THIN` | PMO-internal; the users are the programme office. Acceptable |

---

### 4.4 The `P0` modules — the gate that matters first

Twelve modules carry `P0`. Seven are content-ready.

| Module | Wave | Verdict | What blocks it |
|---|:--:|:--:|---|
| `M01` Service Request & Order | W1–W2 | `READY` | — |
| `M02` Field Service & Dispatch | W2 | `READY` | — |
| `M09` Warranty & Claims | W4 | `THIN` | `MD-017` "17+ brands" unverified; `EO-004` depends on it |
| `M15` Spare Parts & Inventory | W2 | `THIN` | Part master and opening stock unloaded; Category E `D-03` unmade |
| `M19` Financial Accounting | W3 | `READY` | — |
| `M20` AR & Collections | W3 | `READY` | — |
| `M28` Integration Platform | **W1** | **`BLOCKED`** | 14 missing events; no signature scheme; no scope vocabulary |
| `M29` Identity & Security | **W1** | `THIN` | Break-glass and 38 access profiles do not exist |
| `M30` Platform Administration | W1 | `READY` | — |
| `M33` Customer & Party Master | **W1** | **`BLOCKED`** | `06-03` absent; 48 legacy sources unprofiled |
| `M37` Product & Service Catalogue | **W1** | **`GAP`** | Five content files against 46 requirements |
| `M51` Tax & Regulatory | W4 | `THIN` | 26 `DT` files await unwaivable G6; Mushak 9.1 basis contested |
| `M56` Payroll & Statutory | W5 | `READY` | — |

**Four of the five `P0` modules scheduled at `W1` are `BLOCKED`, `GAP` or `THIN`.** `W1` is the
Core Platform and Admin Portal wave. This is the single most consequential statement in this file.

---

### 4.5 Wave inversion — content that arrives after the module that consumes it

Seventeen modules consume content registered at a **later** wave than the module itself. This is
the same defect the category audits have now recorded **45 times across seven categories**
(`AUDIT-018` `EO-03`). This file states it per module, which no prior document did.

| Module | Module wave | Content arriving later | Lag |
|---|:--:|---|---|
| `M04` Branch & Front Desk | W1 | `EO-010` franchise pack (W8) | 7 waves |
| `M15` Spare Parts | W2 | `EO-003`/`EO-004` brand packs (W4); `EO-006` (W3) | 1–2 waves |
| `M17` Device Registry | W2 | `AP-007`/`AP-008` partner guides (W4); `EO-007` (W4) | 2 waves |
| `M19` Financial Accounting | W3 | `RP-009` statutory reports (W3) — aligned | — |
| `M20` AR & Collections | W3 | `EO-009`–`EO-014` (W7–W8) | 4–5 waves |
| `M23` Quality Management | W5 | `EO-010`/`EO-012` (W7–W8) | 2–3 waves |
| `M24` Documents & E-Signature | W3 | `EO-013`/`EO-014` (W7–W8); `RP-014` (W4) | 1–5 waves |
| `M27` Contact Centre | W4 | `HC-020` video scripts (W6) | 2 waves |
| `M28` Integration Platform | **W1** | **`AP-001`–`AP-012` at W3–W4** — eight of twelve arrive after the module | **2–3 waves** |
| `M29` Identity & Security | **W1** | `AP-005` (W3), `AP-012` (W3), `TS-017` (W2) | 1–2 waves |
| `M30` Platform Administration | W1 | `OP-006` release notes (W1) — aligned | — |
| `M33` Customer Master | **W1** | `UI-042` consent copy (W2); `LG-008`–`LG-012` (W2) | 1 wave |
| `M37` Catalogue | **W1** | `SP-025` (W5) | 4 waves |
| `M40` Partner & Franchise | W7 | `EO-014` exit content (W8) | 1 wave — **but exit is possible from W7** |
| `M53` Revenue Recognition | W4 | `EO-013` disputes (W7); `DT-039`/`DT-040` (W7) | 3 waves |
| `M61` Knowledge Management | W6 | `KB-004`–`KB-008` at W2 — **inverted the other way**, content before module | −4 waves |
| `M66` Internal IT Service Management | W6 | **`OP-001` support model needed at W1** | **−5 waves** |

**Two directions of failure appear here and they are not the same problem.**
`M28` and `M33` consume content that arrives *later* — the module is built against content that
does not yet exist. `M61` and `M66` are the reverse: content is required *earlier* than the module
that implements it, so the content has no system to describe. `AUDIT-017` `OP-06` states the
consequence for `M66` exactly: *the programme has operational content and no operational
capability.*

---

### 4.6 The approval position — why no module is `READY` in the sense a gate means

| Fact | Value |
|---|---:|
| Content files written | **429** |
| Content files at status `Draft` | **429** |
| Content files at status `Approved` | **0** |
| Class A files awaiting unwaivable G6 external statutory verification | **26 `DT` + 6 `LG` = 32** |
| Files awaiting a Bengali counterpart before `CM-R6` permits approval | **266 registered bilingual; ~0 counterparts written** |
| Categories where `RF-006`'s absence blocked Definition of Done | **5** — now unblocked by this category |

**What this means for a wave gate.** `06-02` gate criteria are written against approved artefacts.
On the enumeration date, a gate applying its own criteria strictly would fail on content for
**every module**, including the 31 marked `READY` here. `READY` in this file means *the content
exists and is coherent*, which is the strongest statement available today. It is not a substitute
for `CG-007` gate evidence, and no gate paper should quote it as one.

---

### 4.7 Content types by module class — what "complete" would mean

A readiness verdict needs a definition of the content set a module type requires. This is that
definition, derived from the register rather than asserted.

| Module class | Required content types | Example |
|---|---|---|
| **Customer-facing transactional** | `MD` seed · `UI` copy · `NT` templates · `DT` documents · `SP` SOP · `TR` course · `HC` help · `LG` terms · `TS` scripts · `BN` bundle | `M01`, `M20` |
| **Field / mobile** | + `KB` offline pack · `UI-009` offline copy · Bengali-native `TR` | `M02`, `M03` |
| **Back-office operational** | `MD` seed · `UI` workspace copy · `SP` SOP · `TR` course · `TS` scripts | `M15`, `M41` |
| **Statutory / finance** | `MD` seed · `DT` statutory template · `SP` SOP · `LG` terms · `TS` finance scripts · **G6 verification** | `M51`, `M56` |
| **Platform / technical** | `AP` developer content · `OP` runbook · `TS` scripts · `NT` alert library | `M28`, `M29` |
| **Ecosystem-facing** | + `EO` onboarding kit · `LG` counterparty terms · `AP` integration guide | `M12`, `M40`, `M42` |
| **Analytical** | `RP` dictionary/dashboard · `MD` dimensions · `HC` definitional help | `M25`, `M62` |
| **Internal-only** | `SP` SOP · `TS` scripts. **No `TR`, `HC`, `BN` or `NT` required** | `M67`, `M63` |

Applying this definition is what produces the `THIN` verdicts: `M43` is `GAP` not because seven
files is a small number but because a **back-office operational** module with no `SP` and no `TR`
is missing two of its five required types.

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `02-02` | The module register — priority, wave, owner, requirement count |
| `06-01` | Wave definitions. ⚠ Master Index §1 wave windows disagree with `06-01` §3 in **all nine rows** (`AUDIT-018` `EO-04`); this file uses `02-02` |
| `RF-003` | Supplies the requirement counts and the traceability model |
| `05-05` | Business rules per module — absent for `M40` and `M42` |
| Every category audit `AUDIT-002`…`AUDIT-018` | Supplies the blockers named in the verdict column |

| Depended on by | Why |
|---|---|
| Wave gate papers | The content half of "ready to build" |
| `RF-007` | Receives `BL-01`…`BL-04` from §4.3 |
| `RF-011` | Receives the coverage risks |
| Module business owners | Their own module's row |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **Every wave boundary**, and before any gate paper quoting module readiness |
| Regeneration rule | Content counts in §4.3 are **regenerated by extraction from `traces_to:`**, never edited (`CP-11`, `CM-R2`) |
| Verdict rule | A verdict is **re-derived**, not carried forward. A module moves out of `BLOCKED` only when the named blocker is evidenced closed |
| Trigger for out-of-cycle review | A new module; a wave re-plan; a blocker closed; a category declared complete |
| Owner | Programme Content Lead |
| Escalation | A `P0` module at `BLOCKED` within one wave of its build start goes to the Steering Committee, not to the CTO alone |

---

## Approval Record

| Gate | Required for Class E | Reviewer | Status |
|---|:--:|---|---|
| G1 Editorial | ● | Content Design | Not started |
| G2 Factual | ● | Enterprise Architecture with each Module Business Owner | Not started |
| G3–G6 | ○ | — | Not required |
| Final approver | — | Programme Content Lead | **Unappointed** |

---

## Open Items

| # | Item | Owner | Blocks |
|---|---|---|---|
| `RF-004-OI-01` | **Four of five `W1` `P0` modules are `BLOCKED`, `GAP` or `THIN`** — `M28`, `M33`, `M37`, `M29` | CTO | Wave 1 gate |
| `RF-004-OI-02` | **`M37` Catalogue is a `GAP` at `P0`/`W1`** with five content files against 46 requirements | Commercial Director | All fourteen revenue streams |
| `RF-004-OI-03` | **`M38`, `M43`, `M47` are `GAP`** — `RF-007` `BL-02`–`BL-04` | Module business owners | W6–W7 |
| `RF-004-OI-04` | **Seventeen modules carry wave inversion**; `M66` is inverted five waves against a `P0` need | Programme Office | Every affected wave |
| `RF-004-OI-05` | **`05-05` has no rules for `M40` or `M42`** | Enterprise Architecture | Both modules remain `BLOCKED` |
| `RF-004-OI-06` | **No content file is `Approved`; 32 Class A/B files await unwaivable G6** | Legal & Compliance, Finance | Every gate criterion written against approved artefacts |
| `RF-004-OI-07` | **`NFR-091` requires 67 module runbooks; the register contains none** | Platform Engineering | `M66`, `OP-007` |
| `RF-004-OI-08` | **Master Index §1 wave windows disagree with `06-01` in all nine rows** — this file used `02-02` to avoid propagating it | Programme Office | Any wave-based content plan |
| `RF-004-OI-09` | **No Programme Content Lead appointed** | CEO | Final approval |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; register table and maintenance procedure added per `CG-009` §3
- [x] All **67** modules mapped, none omitted
- [x] Content counts produced by extraction with a stated enumeration instant (`CP-11`, `RG-06`)
- [x] Verdict scheme defined before use, and applied against a stated required-content-set definition (§4.7)
- [x] Wave inversion reported per module (§4.5) — not previously stated at module granularity anywhere
- [x] The approval position stated plainly (§4.6) rather than allowing `READY` to be misread
- [x] Every blocker names its audit finding and owner
- [x] All internal links resolve
- [x] Bengali counterpart — n/a (`bilingual: no`, `CG-010` §3.2)
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)
- [ ] **`RF-004-OI-01` `W1` `P0` blockers cleared** — outstanding
- [ ] **Named approver recorded** — outstanding, `RF-004-OI-09`

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
