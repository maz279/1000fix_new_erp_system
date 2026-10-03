---
id: RF-007
title: Content Backlog and Prioritisation Register
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Programme Content Lead
author: Programme Content Lead
reviewers: [CTO, CFO, Programme Office, Learning & Development, Localisation Lead, Knowledge Manager, Platform Engineering Lead, QA Lead, all Category Content Owners]
approver: Programme Content Lead
content_class: E
purpose: >
  The register of content that is needed and not scheduled — requested, discovered or implied by a
  specification, sized, justified and prioritised, but not in the 452. Over 36 months and nine
  waves, new content demand arrives continuously. Without a backlog it is either absorbed silently
  by whoever is nearest, which destroys the effort baseline, or refused arbitrarily, which pushes
  the work into shadow documents. This register also holds the five identifiers already being cited
  as though registered, and the single largest unfunded content commitment in the programme: a
  knowledge corpus of 230 artefacts estimated at 775–1,545 specialist hours that no budget covers.
traces_to: [06-01, CM-R1, CP-02, CG-005, CG-002, AF-09, RF-003, RF-004, RF-005, RF-006, RF-011, RF-012]
priority: P2
wave: W1
bilingual: no
bn_counterpart: n/a
sources:
  - source: project_content/_AUDIT/AUDIT-008_Category_07_KB_Content_Audit.md finding R-07 — 160 articles, 22 tool guides and 48 reference cards enumerated and unwritten, 775–1,545 specialist hours, unresourced
    verified: 2026-08-18
    class: P1
  - source: project_content/_AUDIT/AUDIT-009_Category_08_TR_Content_Audit.md finding TR-01 and R-01 — TR-025 Mandatory Induction and Statutory Compliance must be registered; Layer 1 statutory induction for 800+ employees has no owning file
    verified: 2026-08-18
    class: P1
  - source: project_content/_AUDIT/AUDIT-012_Category_11_BN_Content_Audit.md finding BN-01 and R-4 — BN-019 Bengali String Bundle Cross-Cutting and Critical Flows must be registered; Category 11 becomes 19 files
    verified: 2026-08-18
    class: P1
  - source: project_content/_AUDIT/AUDIT-011_Category_12_DM_Content_Audit.md finding DM-02 and R-02 — register DM-015 catalogue/parts/pricing and DM-016 documents/paper archive, taking the register to 454
    verified: 2026-08-18
    class: P1
  - source: project_content/_AUDIT/AUDIT-014_Category_13_TS_Content_Audit.md finding TS-13 and R-11 — SP-035 cited in TS-006 O-05 as an unallocated identifier; three categories have now proposed a file by citing an unallocated ID
    verified: 2026-08-18
    class: P1
  - source: project_content/_AUDIT/AUDIT-017_Category_17_OP_Content_Audit.md finding OP-07 — NFR-091 requires 67 module runbooks and the register contains none
    verified: 2026-08-18
    class: P1
  - source: project_content/1000FiX_ERP_Content_Master_Index.md §7 — content effort 2,595–3,875 person-days, 520–775 person-weeks, not in the approved business case (AF-09)
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2026-11-18
---

# RF-007 — Content Backlog and Prioritisation Register

---

## 1. Purpose

The 452-file register answers *what content the programme owes*. It does not answer *what content
the programme has discovered it owes since*.

Four mechanisms generate that demand, and all four are active:

| Mechanism | Example already live |
|---|---|
| **An audit finds a file that must exist** | `TR-025` — the statutory induction curriculum for 800+ employees has no owning file |
| **A registered file specifies content it does not contain** | All sixteen `KB` files specify a corpus of 230 artefacts that does not exist |
| **A requirement demands content the register never scoped** | `NFR-091` requires **67 module runbooks**; the register contains none |
| **A gap analysis shows a module or portal under-served** | `M37`, `M38`, `M43`, `M47` — `RF-004` §4.3 |

Without a backlog, each of these has exactly two outcomes: silently absorbed, which corrupts the
520–775 PW effort baseline that is **already not in the business case** (`AF-09`); or refused by
whoever is asked, which produces a shadow document that nobody governs.

This register is the third option: **recorded, sized, justified, prioritised, and visible to the
committee that can fund it.**

---

## 2. Scope

**In scope** — content needed and not registered; proposed-but-unallocated identifiers; content
implied by a specification but never scoped; under-served modules and portals from `RF-004` and
`RF-005`; sizing, justification, requester and priority; the promotion route into the register.

**Out of scope**

| Excluded | Owner |
|---|---|
| Content already in the 452 | Master Index §4 |
| Whether an ID may be allocated | `CG-005`; the Steering Committee decides |
| Effort estimation method | Master Index §7 |
| Risk arising from unscheduled content | `RF-011` |
| The decision to register a backlog item | `RF-006` |
| Defect remediation on written files | `RF-012` |

---

## 3. Audience

| Reader | Uses this register to |
|---|---|
| **The Steering Committee** | Take register-change and funding decisions on one paper, not five |
| **The Programme Content Lead** | Refuse, defer or schedule demand against a stated priority |
| **A category owner** | See what their category is missing beyond its registered files |
| **The CFO** | See unfunded content commitment alongside the `AF-09` variance |
| **An author** | Find out whether the file they are about to invent already has a backlog entry |

---

## 4. Content

### 4.1 How to read the register

| Column | Meaning |
|---|---|
| **`BL-nn`** | Permanent backlog identifier. Never reused. Survives promotion — a promoted item keeps its `BL-` number in its history |
| **Size** | `XS` < 1 day · `S` 1–3 days · `M` 4–10 days · `L` 11–25 days · `XL` > 25 days · `PROG` a programme of work, sized in hours or PW |
| **Pri** | `P0`–`P3`, the register scale (`README.md` convention) — **not** the website `P1`–`P4` scale (`AF-11`) |
| **Requester** | Who raised it. An audit is a legitimate requester |
| **State** | `RAISED` · `SIZED` · `APPROVED` · `SCHEDULED` · `PROMOTED` · `REJECTED` · `DEFERRED` |

**Promotion route.** `RAISED` → sized and justified → **Steering Committee decision** → `PROMOTED`
into the Master Index with a new ID under `CG-005`, **before** authoring begins (`CM-R1`,
register-first). No backlog item is authored while still on the backlog.

---

### 4.2 Summary

| Class of demand | Items | Estimated effort |
|---|---:|---|
| Proposed identifiers already being cited | 5 | 34–68 days |
| Content specified but never scoped | 4 | **1,047–2,105 hours + 67 runbooks** |
| Under-served modules and portals | 6 | 96–190 days |
| Governance and register debt | 5 | 47–92 days |
| Bengali deliverable | 1 | **`PROG`** — see §4.6 |
| **Total registered backlog** | **21** | **Not fundable from the current baseline** |

| Priority | Items |
|---|---:|
| `P0` | **3** |
| `P1` | 8 |
| `P2` | 7 |
| `P3` | 3 |

---

### 4.3 The five proposed identifiers

These are cited in written files as though they were registered. Under `CM-R1` they are not, and
under `RF-006` `CD-12` they are held here rather than silently added. **The register total stays
452 until the Steering Committee acts.**

| `BL` | Proposed ID | Title | Raised by | Why it must exist | Size | Pri | State |
|---|---|---|---|---|:--:|:--:|:--:|
| `BL-07` | **`TR-025`** | Mandatory Induction and Statutory Compliance Curriculum | `AUDIT-009` `TR-01` | The **Layer 1 statutory induction for 800+ employees has no owning file.** `LG-020` §4.12 and `LG-022` §4.9.5 both depend on it as the attestation and understanding-evidence vehicle — two consumers for a file that does not exist. It is also the access precondition for every wave | `L` | **`P0`** | `SIZED` |
| `BL-08` | **`BN-019`** | Bengali String Bundle — Cross-Cutting and Critical Flows | `AUDIT-012` `BN-01` | The **`common.*` namespace — 154 shared strings loading on every portal — has no registered Bengali owner.** `P02`'s non-negotiable Bengali completeness is counted at **44%**. Without it **no portal can claim `PS-03` conformance** | `L` | **`P0`** | `SIZED` |
| `BL-09` | **`DM-015`** | Field Mapping Workbook — Catalogue, Parts and Pricing | `AUDIT-011` `DM-02` | `M37` and `M11` catalogue and pricing have **no migration workbook**. `MD-019` is the spine of all fourteen revenue streams and there is no route to load its legacy data | `M` | **`P0`** | `SIZED` |
| `BL-10` | **`DM-016`** | Field Mapping Workbook — Documents and Paper Archive | `AUDIT-011` `DM-02` | `M24` holds **500,000+ document records** with no workbook. Statutory retention under `LG-009` cannot begin from an unmigrated archive | `M` | `P1` | `SIZED` |
| `BL-11` | **`SP-035`** | *(title not settled)* — the SOP `TS-006` `O-05` requires | `AUDIT-014` `TS-13` | `TS-006` cites `SP-035` conditionally — *"either `SP-035` is registered or the register records the gap"*. Today neither is true | `M` | `P2` | `RAISED` |

**If all five are promoted the register moves 452 → 457.** `AUDIT-011` `R-02` computed 454,
`AUDIT-012` computed 453, `AUDIT-014` `R-11` computed 455 — **each audit counted only the
proposals it knew about.** This is the first place all five appear together, and it is exactly the
failure `CM-R1` exists to prevent: five categories each proposing a file, none able to see the
others.

> **Governance gap.** `CG-005` does not say **how a proposed-but-unallocated ID is written**.
> `AUDIT-014` `TS-13` raised it and it is unresolved. Until then, authors cite bare `TR-025` and a
> reader cannot tell a live ID from a proposal. Carried as `BL-19`.

---

### 4.4 Content specified but never scoped

The most expensive class. These are not new ideas — they are commitments already made by
registered files, whose *contents* were never counted as deliverables.

#### `BL-12` — the knowledge corpus · `PROG` · `P1`

| | |
|---|---|
| **Raised by** | `AUDIT-008` `R-07` |
| **What** | All sixteen `KB` files are **specifications for content that does not exist**: **160 articles, 22 tool guides, 48 reference cards** |
| **Estimate** | **775–1,545 specialist hours**, unresourced |
| **Who can write it** | 80–150 senior technicians — the scarcest authoring resource in the programme, and the same people who must be on the bench |
| **Consequence** | `KB-016` is *the offline pack shipped inside `P02`* and has nothing to package. `M32` AI assistant has **no grounding corpus**. `P02`, `P03` and `P11` all depend on it |
| **Why it is not in the 452** | The register counted `KB-001`…`KB-016` as sixteen files. Sixteen specifications were written. The 230 artefacts they specify were never register entries |
| **State** | `SIZED` — **not funded, not scheduled, not owned** |

**This single item is larger than eight entire content categories.** At the register's own basis
of roughly 7.5 hours per person-day, 775–1,545 hours is **103–206 person-days**, against the
`KB` category's registered estimate of 130–210 person-days for the *specifications alone*.

#### `BL-13` — the 67 module runbooks · `PROG` · `P1`

| | |
|---|---|
| **Raised by** | `AUDIT-017` `OP-07` |
| **What** | **`NFR-091` requires a runbook per module. The register contains none** — Category 17 holds seven platform runbooks (`OP-007`–`OP-013`), not 67 module runbooks |
| **Estimate** | 67 × 1.5–3 days = **100–200 person-days** |
| **Consequence** | `NFR-091` is unmet at every wave gate. `M66` internal IT has no per-module operational content. Every incident on a module with no runbook depends on one person being reachable |
| **State** | `RAISED` |

#### `BL-14` — the `05-01` requirement register · `L` · `P1`

| | |
|---|---|
| **Raised by** | `AUDIT-001` `AF-06`, confirmed by `RF-003` §4.2 and `RF-001` `GL-04` |
| **What** | `05-01` is a **summary** carrying 200 identifiers and describing ~2,352 requirements, against **3,350 enumerated**. It also carries 30 `FR-SLS-` and 3 `FR-BFO-` orphans whose only other home is superseded |
| **Consequence** | L4 traceability impossible; `G4-10` answerable only at family granularity; test coverage cannot be reported |
| **Note** | **This is engineering's file, not content's.** It is on the content backlog because content cannot deliver `RF-003` L4 without it |
| **State** | `RAISED` — **owner is the CTO** |

#### `BL-15` — the 38 access profiles · `M` · `P0`

| | |
|---|---|
| **Raised by** | `AUDIT-017` `OP-10` |
| **What** | **The 38 role-based access profiles do not exist**, and the `SOD-` space they would be checked against is unharmonised between `05-04` (12 registered) and `SP-006` (61 registered) |
| **Consequence** | `OP-015` joiner-mover-leaver content describes profiles that cannot be requested. `M29` cannot enforce `SOD` at assignment (`NFR-064`). `P03` cannot scope its fourteen workspaces |
| **State** | `RAISED` — **`P0`, needed W1** |

---

### 4.5 Under-served modules and portals

From `RF-004` §4.3 and `RF-005` §4.4. Each is a *content* gap, not a specification gap.

| `BL` | For | What is missing | Size | Pri | State |
|---|---|---|:--:|:--:|:--:|
| `BL-01` | **`M37` Product & Service Catalogue** — `P0`/`W1`, 46 requirements, **5 content files** | Catalogue maintenance SOP; catalogue-administrator training; catalogue quality report; catalogue admin `UI` copy | `L` | **`P0`** | `RAISED` |
| `BL-02` | **`M38` E-Commerce Storefront** — 56 requirements, **9 content files** | `UI` copy pack; `HC` help set; `NT` order/shipping templates; storefront `LG` terms. **The storefront has no content owner** | `XL` | `P1` | `RAISED` |
| `BL-03` | **`M43` Demand Planning** — 32 requirements, **7 content files** | Planner SOP; planner training; replenishment-parameter governance content; planning accuracy report | `L` | `P2` | `RAISED` |
| `BL-04` | **`M47` Facility & Workplace** — 45 requirements, **4 content files**, lowest in the register | Facility management SOP; branch infrastructure standard; workplace `MD` asset classes | `M` | `P3` | `RAISED` |
| `BL-05` | **Acceptance-criteria qualification** — `RF-006` `CD-05` | Re-cite **1,568** criteria as `<Mnn\|Pnn>/AC-nn` across `TS-001`–`TS-018` before the first script is written | `M` | `P1` | `APPROVED` |
| `BL-16` | **`M46` Fleet, `M13` Rental, `M54` Cost Accounting** — `THIN` in `RF-004` | Fleet SOP and driver `KB`; rental `UI`/`TR`/`HC`; an `RP` dashboard tracing to `M54` for the `RP-010` board pack | `L` | `P3` | `RAISED` |

---

### 4.6 The Bengali deliverable — `BL-17` · `PROG` · `P0`

| | |
|---|---|
| **Raised by** | `RF-006` `CD-08`, on the enumeration behind `CG-010` §3.2 |
| **What** | **266 of 452 registered files are bilingual. Approximately none has a written Bengali counterpart.** `BN-009`–`BN-017` are bundles and packs, not the 266 counterparts |
| **Register basis** | Master Index §7 estimates `BN` at 180–280 person-days for **the Category 11 files**. The 266 counterparts are **not in that line** |
| **Consequence** | `CM-R6`: a bilingual file cannot reach `Approved` without in-context sign-off. **266 files therefore cannot be approved.** That is 59% of the register and includes every `UI` pack, 34 `DT` documents, 20 `NT` template sets and 16 `LG` documents |
| **Compounding** | **289 Bengali strings have no English source row** (`AUDIT-012` `BN-18`); the `UI` packs are representative, not complete. Machine translation is **prohibited** on customer- and field-facing content (`CP-05`) |
| **State** | `SIZED` at `PROG` — **must be estimated properly and taken to the Steering Committee with `AF-09`** |

**This is the largest single item on the backlog and it is not new work.** It is the second half of
work already counted as done. `CD-08` exists precisely so that a category is never again reported
"complete" on its English half alone.

---

### 4.7 Governance and register debt

| `BL` | Item | Why | Size | Pri | State |
|---|---|---|:--:|:--:|:--:|
| `BL-06` | **Retrospective decision capture** across `CG`, `VB`, `MD`, `NT`, `DT`, `BN` — 160 files carrying **zero recorded decisions** | Decisions were taken and not logged. `MD` and `DT` have no answer to "why is it like this?" — `AF-04`'s failure mode inside the content set | `L` | `P2` | `RAISED` |
| `BL-18` | **`CD-02` remediation** — correct 331 future-dated `verified:` values across 68 files, and add check `A7` / rule `RG-09` | A verification date in the future is not a verification. `RF-002` §4.7 | `S` | `P1` | `APPROVED` |
| `BL-19` | **`CG-005` v1.1** — state how a proposed-but-unallocated ID is written, and add the module-code allocation rule reserving the `FR-<CODE>-` space | `AUDIT-014` `TS-13`; `RF-001` `GL-02` (`FR-SRM2-`, 34 non-conformant identifiers) | `S` | `P2` | `RAISED` |
| `BL-20` | **`CD-07` migration** — qualify 1,177 file-local `O-nn` open items as `<ID>-OI-nn` | Unqualified open items cannot be consolidated, escalated or closed centrally. `RF-006` §4.6 | `M` | `P2` | `APPROVED` |
| `BL-21` | **Master Index §1 wave-window correction** — the windows disagree with `06-01` §3 and `02-02` **in all nine rows**, by two to six months, while stating they are taken from `06-01` | `AUDIT-018` `EO-04`. Never audited in seventeen prior reports. Every wave-based content plan reads from it | `XS` | `P1` | `RAISED` |

---

### 4.8 Rejected and deferred

Recorded so they are not re-raised.

| Item | Decision | Why |
|---|---|---|
| Merge the ERP and website content sets | **Rejected** | Different audiences, lifecycles, priority scales and approval authorities. Master Index §11; four defined interfaces, all ERP-owned |
| Adopt the website `P1`–`P4` priority scale | **Rejected** | `AF-11`. The scales look identical and mean different things; converging them would silently re-rank 452 files |
| Split the generic template into five dedicated templates | **Deferred** to after the first approval cycle | `CG-009` §6 observes it governs 155 files (34%). Splitting now re-templates 155 written files for no reader benefit |
| Build the `RF-003` L4 reverse index against `05-01` as it stands | **Deferred** to `AF-06` closure | It would be 94% empty and read as 94% uncovered — worse than absent. `RF-006` §4.5 |
| Renumber the `KPI-` space | **Deferred** to `AUDIT-015` `RP-01` remediation | 291 in use, 95 registered; renumbering touches `06-02`, 79 specifications and all 16 `RP` files |

---

### 4.9 The funding position

| | Person-days | Person-weeks |
|---|---:|---:|
| Registered content estimate — Master Index §7 | 2,595–3,875 | **520–775** |
| **`BL-12` knowledge corpus** | 103–206 | 21–41 |
| **`BL-13` module runbooks** | 100–200 | 20–40 |
| `BL-01`–`BL-04`, `BL-16` under-served modules | 96–190 | 19–38 |
| `BL-07`–`BL-11` proposed identifiers | 34–68 | 7–14 |
| `BL-05`, `BL-06`, `BL-15`, `BL-18`–`BL-21` governance debt | 47–92 | 9–18 |
| **`BL-17` Bengali counterparts** | **not yet sized** | **not yet sized** |
| **Backlog subtotal, excluding `BL-17`** | **380–756** | **76–151** |
| **Register + backlog, excluding `BL-17`** | **2,975–4,631** | **596–926** |

**Read against the programme's own numbers.** Master Index §7 already states that 520–775 PW is
**34–51% of the measured 1,513 PW build effort** and is **not in the approved business case**
(`AF-09`). The backlog adds **76–151 PW before the Bengali deliverable is sized at all**.

**`RF7-01`. This register goes to the Steering Committee on the same agenda item as `AF-09` and
`PD-14`, not separately.** Three papers arriving independently — the content estimate, the TCO
restatement and the backlog — will be read as three surprises rather than one number. That is how
content quality gets sacrificed at a wave boundary.

---

### 4.10 Intake

| # | Rule |
|---|---|
| `BK-01` | Any person may raise a backlog item. An **audit finding is a legitimate requester** and raises items directly |
| `BK-02` | An item is not `SIZED` until it names **what stops working without it** — the same `CP-03` test the register applies |
| `BK-03` | An item that duplicates a registered file is **rejected with a pointer**, never merged into the existing file's scope (`CP-01`, `CM-R3`) |
| `BK-04` | **No backlog item is authored before promotion.** `CM-R1` is register-first, and a file written against a backlog entry has no ID, no owner and no review path |
| `BK-05` | An item open for **three consecutive wave boundaries** without a decision is escalated to the Steering Committee as a standing item |
| `BK-06` | A promoted item **keeps its `BL-` number in its history**, so the register can answer "when was this file first requested?" |
| `BK-07` | A rejected item is recorded in §4.8 with its reason. Rejection is a decision and goes to `RF-006` |
| `BK-08` | Sizing is a **range with a basis** (`RG-05`). A single-point estimate is not accepted |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `CG-005` | ID allocation on promotion. **`BL-19` is a gap in it** |
| `CM-R1` | Register-first; the promotion route exists to honour it |
| `RF-004`, `RF-005` | Supply the under-served items |
| `RF-006` | Promotion is a decision and is logged there |
| Master Index §7 | The effort baseline §4.9 extends |

| Depended on by | Why |
|---|---|
| Steering Committee register-change papers | `RF7-01` |
| `RF-011` | Unscheduled `P0` content is a risk |
| `RF-012` | Audit findings requiring new content land here |
| Category owners | Their own category's unscheduled demand |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **Every wave boundary**, and at every Steering Committee that takes a register change |
| Trigger for out-of-cycle review | Any audit raising a new-file finding; any category completion revealing unscoped content |
| Sizing rule | Range with a basis (`BK-08`, `RG-05`). Re-sized when scope changes materially |
| Promotion rule | Steering Committee decision → Master Index entry → **then** authoring (`BK-04`) |
| Owner | Programme Content Lead |
| Escalation | A `P0` backlog item within one wave of its need-by date goes to the Steering Committee immediately, not at the next boundary |

---

## Approval Record

| Gate | Required for Class E | Reviewer | Status |
|---|:--:|---|---|
| G1 Editorial | ● | Content Design | Not started |
| G2 Factual | ● | Programme Office with CFO | Not started |
| G3–G6 | ○ | — | Not required |
| Final approver | — | Programme Content Lead | **Unappointed** |

---

## Open Items

| # | Item | Owner | Blocks |
|---|---|---|---|
| `RF-007-OI-01` | **Three `P0` backlog items are unfunded and unscheduled** — `BL-07` `TR-025`, `BL-08` `BN-019`, `BL-15` access profiles | Steering Committee | Statutory induction; `PS-03` on all twelve portals; `W1` access control |
| `RF-007-OI-02` | **`BL-12` — 230 knowledge artefacts, 775–1,545 hours, unresourced** | Knowledge Manager with CTO | `P02` offline pack; `M32` AI grounding |
| `RF-007-OI-03` | **`BL-17` Bengali deliverable not sized.** 266 files cannot reach `Approved` without it | Localisation Lead with CFO | 59% of the register |
| `RF-007-OI-04` | **`BL-13` — `NFR-091` requires 67 module runbooks; none exists** | Platform Engineering Lead | `NFR-091` at every gate |
| `RF-007-OI-05` | **`RF7-01` — backlog not yet on the `AF-09` / `PD-14` agenda item** | Programme Content Lead | Three separate surprises instead of one number |
| `RF-007-OI-06` | **`BL-19` — `CG-005` cannot express a proposed ID**, so five proposals are indistinguishable from live IDs in citations | Programme Content Lead | `CM-R1` integrity |
| `RF-007-OI-07` | **No Programme Content Lead appointed** to hold intake authority | CEO | `BK-01`–`BK-08` |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; register table and maintenance procedure added per `CG-009` §3
- [x] All five proposed identifiers held in one place for the first time, with the corrected total (452 → 457)
- [x] Content specified but never scoped identified and sized, including the two `PROG` items
- [x] Under-served modules and portals carried from `RF-004` and `RF-005` with named gaps
- [x] Bengali deliverable registered as backlog rather than assumed complete (`CD-08`)
- [x] Rejected and deferred items recorded so they are not re-raised
- [x] Funding position stated against the existing `AF-09` variance, with `RF7-01`
- [x] Intake rules `BK-01`–`BK-08` stated; sizing is a range with a basis (`RG-05`)
- [x] Uses the qualified open-item form (`RF-006` `CD-07`)
- [x] All internal links resolve
- [x] Bengali counterpart — n/a (`bilingual: no`, `CG-010` §3.2)
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)
- [ ] **Three `P0` items funded** — outstanding, `RF-007-OI-01`
- [ ] **Named approver recorded** — outstanding, `RF-007-OI-07`

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
