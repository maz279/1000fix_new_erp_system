---
id: RF-011
title: Content Risk Register
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Programme Content Lead
author: Programme Content Lead with the Programme Office
reviewers: [CEO, CTO, CFO, Legal Counsel, Quality Manager, Localisation Lead, QA Lead, Programme Office, all Category Content Owners]
approver: Programme Content Lead
content_class: E
purpose: >
  The register of content-specific risk — translation capacity, legal-review throughput,
  master-data readiness, specialist availability, statutory currency and approval deadlock.
  `00-04` carries 36 programme risks and **none of them is a content risk**, yet master-data
  readiness is a credible cause of wave slippage and the bilingual obligation is the single
  largest unfunded commitment in the programme. Eighteen category audits have surfaced the same
  exposures repeatedly as findings; a finding records what is wrong today, and a risk records what
  will go wrong if nothing changes. This register holds the second, so that content exposure
  reaches the Steering Committee as risk rather than as an accumulation of audit paperwork.
traces_to: [00-04, RSK-035, CG-013, CP-05, CM-R6, AF-09, RF-006, RF-007, RF-008, RF-010, RF-012, CG-002, 06-01]
priority: P2
wave: W0
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/00_Governance_and_Charter/00-04_Risks_Assumptions_Dependencies_and_Governance.md §Risks — RSK-001…RSK-036 with Prob/Impact/Rating/Mitigation/Contingency/Owner; this register adopts the same scale and none of the 36 is a content risk
    verified: 2026-08-18
    class: P1
  - source: project_content/_AUDIT/ — AUDIT-001 through AUDIT-018, 232 findings; the exposures in §4.3 are derived from them, not re-invented
    verified: 2026-08-18
    class: P1
  - source: project_content/1000FiX_ERP_Content_Master_Index.md §7 — content effort 2,595–3,875 person-days, 520–775 person-weeks, not in the approved business case (AF-09)
    verified: 2026-08-18
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-010_Bilingual_Content_Policy.md §3.2 — 266 of 452 files require a Bengali counterpart; CM-R6 blocks approval until in-context sign-off
    verified: 2026-08-18
    class: P1
  - source: Extraction across project_content/, run 2026-08-18 — 443 content files written, 0 at status Approved, 32 Class A/B files awaiting unwaivable gate G6, 449 files with an unfilled or functional approver
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2026-11-18
---

# RF-011 — Content Risk Register

> **Identifier space.** Content risks use **`CR-nn`**, disjoint from the programme's
> `RSK-001`…`RSK-036` in `00-04` (`RF-006` `CD-10`). A content risk register that extended the
> `RSK-` space would need `00-04`'s owner to allocate every identifier — which is precisely the
> coupling that has left content risk unrepresented for the life of the programme.

---

## 1. Purpose

`00-04` is a competent risk register. It carries 36 risks with probability, impact, rating,
mitigation, contingency and a named owner. It has a critical tier, a review cadence and an
escalation route.

**Not one of its 36 risks is about content.** `RSK-001` is super-user availability; `RSK-022` is
the marketplace commercial model; `RSK-035` is regulatory citation drift — the closest it comes,
and it is scoped to the specification, not to the 443 files that cite the same instruments.

Meanwhile eighteen category audits have recorded, repeatedly and in different words:

- 266 files that **can never reach `Approved`** because their Bengali counterparts are unwritten
- 32 Class A and B files awaiting an **unwaivable** external verification that has not started
- a knowledge corpus of **775–1,545 unresourced specialist hours**
- **45 wave inversions across seven categories** — content consumed before it exists
- a content effort of **520–775 PW that is not in the business case**

Those are findings. A finding says *this is wrong now*. A risk says *this is what happens next, how
likely, how bad, and who owns preventing it*. The Steering Committee acts on the second. This
register converts eighteen audits' worth of the first into the second.

---

## 2. Scope

**In scope** — risks whose cause is content: capacity, capability, sequencing, approval,
currency, ownership, funding and quality of the content set.

**Out of scope**

| Excluded | Owner |
|---|---|
| Programme, technical and commercial risk | `00-04` `RSK-001`…`RSK-036` |
| Defects that exist today | `RF-012` |
| Unscheduled work | `RF-007` |
| Decisions not taken *(a decision not taken **is** a risk; the decision itself is not)* | `RF-006` |
| Currency of an external instrument | `RF-008` — this register carries the **risk** of the control failing |
| Operational and security risk | `M60`, `LG-021`, `OP-016` |

---

## 3. Audience

| Reader | Uses this register to |
|---|---|
| **The Steering Committee** | See content exposure as risk, with a rating and an owner, alongside `00-04` |
| **The CFO** | See the funding exposure that `AF-09` opened and this register quantifies |
| **The Programme Content Lead** | Direct mitigation effort at the exposures that will bite first |
| **A category owner** | See the risks their category carries |
| **The Programme Office** | Merge content risk into the programme risk report without renumbering |

---

## 4. Content

### 4.1 Scale

Adopted **unchanged** from `00-04` so the two registers can be read together and merged without
re-scoring.

| Probability | Meaning |
|:--:|---|
| **H** | More likely than not to occur in the next two waves |
| **M** | Credible; would not surprise an experienced observer |
| **L** | Possible; requires a specific trigger |

| Impact | Meaning |
|---|---|
| **High** | Wave slippage, statutory exposure, or a material cost the business case does not carry |
| **Medium** | Rework, quality loss, or an avoidable cost |
| **Low** | Inconvenience absorbed within the workstream |

| Rating | Governance |
|---|---|
| **Critical** | Steering Committee standing item; owner reports at every gate |
| **High** | PMO tracking; owner reports at each wave gate |
| **Medium** | Register review quarterly |
| **Low** | Reviewed at wave boundaries |

---

### 4.2 Summary

| Rating | Risks |
|---|---:|
| **Critical** | **6** |
| High | 9 |
| Medium | 6 |
| Low | 2 |
| **Total** | **23** |

| Cause class | Risks |
|---|---:|
| Capacity and funding | 6 |
| Approval and governance | 5 |
| Sequencing | 3 |
| Currency and compliance | 4 |
| Ownership and continuity | 3 |
| Quality and integrity | 2 |

---

### 4.3 The register

#### Critical

| ID | Risk | Prob | Impact | Rating | Mitigation | Contingency | Owner |
|---|---|:-:|:-:|:-:|---|---|---|
| **`CR-01`** | **The bilingual obligation is unfunded and unresourced.** 266 files require a Bengali counterpart; effectively none exists. `CM-R6` blocks approval until in-context sign-off, so **266 files can never reach `Approved`** on the current plan. `PS-03` and `P02` non-negotiable #3 both fail | **H** | High | **Critical** | Register `BN-019` for the `common.*` namespace; fund translation capacity as a named line; stagger by consuming wave; pre-qualify vendors before W2 | Portals launch English-only against an explicit non-negotiable, or waves slip. **There is no third option** | **CFO with Localisation Lead** |
| **`CR-02`** | **The content effort is not in the business case.** 520–775 PW registered (`AF-09`) plus **537–852 person-days and 1,590–3,090 specialist hours** of backlog (`RF-007`). The variance compounds the open `PD-14` TCO variance | **H** | High | **Critical** | Raise at the same Steering item as `PD-14`, not separately; present written / reviewed / approved separately (`RF-006` `CD-12`) | Content quality is sacrificed at wave boundaries — the standard failure mode, and the least visible | **CFO** |
| **`CR-03`** | **No content file can be approved.** 443 written, **0 `Approved`**. 32 Class A/B files await **unwaivable** gate G6; 26 files name an approver whose post is unfilled; 266 await Bengali sign-off | **H** | High | **Critical** | Appoint the Programme Content Lead (`RF-010` `AP-01`); commission external statutory verification for the 32; apply `OW-04` delegation | Every wave gate criterion written against approved artefacts fails on content, including for the 31 modules assessed content-`READY` | **CEO** |
| **`CR-04`** | **Statutory content is verified against instruments the company does not hold.** 1 controlled copy of 44 registered instruments; **6 files cite a repealed statute**; the Mushak 9.1 basis is stated two ways; **ISO 9001:2015 is superseded on 16 September 2026**, re-opening 38 files | **H** | High | **Critical** | `RF-008` currency cadence; `M24` holds version-stamped copies; raise `PD-21` ISO transition; correct the six PDPA citations | `RSK-035` recurs — a statutory document generated from a superseded instrument, discovered by a regulator rather than by the company | **Legal Counsel with CFO** |
| **`CR-05`** | **Master data is not ready and is the first dependency of everything.** `MD-022` part master and `DM-007` opening stock unloaded; **all 48 legacy sources unprofiled**; `06-03_Data_Migration_Strategy.md` does not exist; two migration domains have no workbook | **H** | High | **Critical** | Register `DM-015`/`DM-016`; commission source profiling as a W0 activity; write `06-03`; treat `MD-048` load order as a gate artefact | W1 configuration begins on unapproved master data — explicitly prohibited by the Phase 1 gate and the most common ERP failure mode | **CTO with MDM Lead** |
| **`CR-06`** | **The knowledge corpus does not exist and the people who must write it are billable.** 160 articles, 22 tool guides, 48 reference cards — **775–1,545 hours from 80–150 senior technicians**. `P02` ships an offline pack with nothing in it | **H** | High | **Critical** | Fund and roster authoring time explicitly; stage by device family against W2; adopt KCS capture-in-workflow so authoring is a by-product of repair | `P02` launches without offline knowledge, against a stated non-negotiable, to a workforce with high turnover and mixed literacy | **Technical Director with CFO** |

#### High

| ID | Risk | Prob | Impact | Rating | Mitigation | Contingency | Owner |
|---|---|:-:|:-:|:-:|---|---|---|
| `CR-07` | **Legal review is a single-threaded bottleneck.** Legal Counsel approves 14 Class A/B files and reviews 24 `LG` files at gate G5, none started; four upstream legal decisions are unmade | H | High | **High** | Sequence G5 by consuming wave; engage external counsel for the six G6 files; take the four decisions as a block | W2 customer-facing content ships unreviewed, or `P01` slips | **Legal Counsel** |
| `CR-08` | **45 wave inversions across seven categories** — content is consumed a wave before it is registered. `M66` is inverted five waves against a `P0` need | H | High | **High** | Re-sequence at the register level, not per category; adopt `RF-004` §4.5 as the authoritative inversion list | Each wave starts with content that does not exist and is improvised locally, which is how 51 branches acquire 51 variants | **Programme Office** |
| `CR-09` | **The specialist authoring pool is not content staff and has no protected time.** `BL-11`–`BL-15` draw on senior technicians, BI analysts and platform engineers simultaneously | H | High | **High** | Schedule by the constraint, not the deadline (`RF-007` `PR-06`); protect time in objectives as `RSK-001` does for super-users | Specialists deprioritise authoring for operational work — correctly — and the corpus never appears | **CTO with Technical Director** |
| `CR-10` | **Ownership is functional, not personal.** 449 files, **zero named owners, zero deputies**; four categories (83 files) have a single owning function | H | Medium | **High** | Name owners and deputies (`RF-010` §4.1, `AP-06`); apply `OW-07` no-orphan rule | Files silently lose their owner on a role change; review dates pass unactioned | **Programme Content Lead** |
| `CR-11` | **The KPI and benefit base is unsound.** 250 KPI identifiers in use against 95 registered; **44 of 95 baselines absent**; roughly **BDT 396 lac of the 876 lac case** rests on improvement benefits whose baselines are weak or absent | H | High | **High** | `RP-015` baseline capture as a W0 activity; re-register the KPI space; restate the benefit case on evidenced baselines only | Benefits are claimed against unmeasurable KPIs and the programme cannot prove its case at closure | **CFO with BI Lead** |
| `CR-12` | **Marketplace payout may be unlawful at launch.** Unbounded dispute block and appeal against a **10-day** settlement obligation and a **72-hour** complaint obligation; no stage SLA, no 72-hour path, **no compliance officer** | M | High | **High** | Bound every stage inside 10 days in `EO-013`/`LG-004`; appoint a compliance officer; take `PD-03` | `P07` launch is deferred, or launches into a regulatory exposure visible on the face of every payout statement | **CEO with Legal** |
| `CR-13` | **432 content reviews fall due in one week** (2027-02-15…20) | H | Medium | **High** | Apply `RF-010` `OW-03` staggering now, before the dates arrive | The first review cycle is a rubber stamp, and the review control is discredited for the rest of the programme | **Programme Content Lead** |
| `CR-14` | **Accessibility conformance is claimed and unevidenced.** `PS-04` is contractual; no accessibility reviewer exists; `TS-016` cannot be executed on any portal; the contractual standard is one W3C revision behind | H | Medium | **High** | Appoint a reviewer (`AP-05`); decide WCAG 2.1 vs 2.2 (`RF-006` `PD-22`); execute `TS-016` on `P01`/`P02` before W2 | A contractual conformance claim is made without test evidence — a claim, not a fact | **CTO with Content Design Lead** |
| `CR-15` | **The integration contract is incomplete at `W1`.** 14 event names consumed and non-existent; no webhook signature scheme; no scope vocabulary; no error-envelope ruling | H | High | **High** | Take `PD-18`, `PD-19`, `PD-20` as a W1 block; complete the `05-03` event inventory | Partners integrate against a contract that changes under them; `M28` is `BLOCKED` at a `P0`/`W1` position | **CTO** |

#### Medium

| ID | Risk | Prob | Impact | Rating | Mitigation | Contingency | Owner |
|---|---|:-:|:-:|:-:|---|---|---|
| `CR-16` | **SME availability for factual review (G2).** Every G2 needs the person who holds the knowledge; `RSK-001` already flags super-user scarcity for UAT and the same people are needed here | M | Medium | Medium | Batch G2 reviews by SME rather than by file; book against the `RSK-001` protected time | G2 becomes a formality and factual defects reach production | Business Process Lead |
| `CR-17` | **Register drift.** Four documents state four prospective totals; five IDs are cited as though registered; the `verified:` field carries 331 future dates | M | Medium | Medium | `RF-006` `CD-12` holds the total; `RF-007` §4.3 holds the IDs; add check `A7`/`RG-09` | The register loses authority, which is the one thing a register cannot lose | Programme Content Lead |
| `CR-18` | **Terminology divergence at scale.** 443 files by many hands; `CG-004` and `BN-003` exist but term scanning is manual | M | Medium | Medium | Automate the `CG-004` banned-synonym scan in CI; run at G1 | The same action is labelled four ways across four workspaces — the failure `CG-003` was written to prevent | Content Design Lead |
| `CR-19` | **Template drift.** The generic template governs 155 files (34%); five recurring section patterns justify dedicated templates and none exists | M | Low | Medium | Create the five templates identified in `CG-009` §6; enforce at G1 | Reviewers have nothing to review structure against, and `CP-09` becomes advisory | Content Design Lead |
| `CR-20` | **The archive process is untested.** `_ARCHIVE/` is empty; no content has been superseded; `CC-06` and the `RF-006` retirement process have never run | M | Low | Medium | Rehearse on the first retirement; treat it as a controlled test | The first supersession is improvised and content is deleted rather than archived, breaching `CP-10` | Programme Content Lead |
| `CR-21` | **Enumeration during authoring produces contradictory counts.** Observed twice: 427→428 in four minutes; Category 19 from 0 to 11 files during the authoring of Category 99 | H | Low | Medium | `RF-006` `CD-14` / proposed `RG-08`: every count carries an instant and is declared a floor | Counts are read as contradictions and the register's numbers are distrusted | Programme Content Lead |

#### Low

| ID | Risk | Prob | Impact | Rating | Mitigation | Contingency | Owner |
|---|---|:-:|:-:|:-:|---|---|---|
| `CR-22` | **Cross-reading the two priority scales.** The website set uses `P1`–`P4`; this set uses `P0`–`P3` (`AF-11`) | L | Medium | Low | Warning retained in the Master Index, `README.md` and `RF-007` §4.1 | Work is silently misranked between two programmes | Programme Content Lead |
| `CR-23` | **Path fragility from the misfiled portal specifications** (`AF-01`) and the identically-named `old-primary-doc/` set | L | Medium | Low | Cite by identifier, never by path (`RF-006` `CD-06`); `RF-002` `EV-04` | A citation resolves to a superseded document half the time | CTO |

---

### 4.4 What is deliberately not a risk here

Stated so the register is not read as exhaustive when it is scoped.

| Not registered | Because |
|---|---|
| "The content might be poor quality" | Not a risk; it is what the `CG-007` gates and `CG-008` DoD exist to control. A risk register that restates the absence of controls that do exist is noise |
| Individual audit findings | `RF-012`. A finding becomes a `CR-nn` only when it names a **future** consequence that mitigation could prevent |
| `PD-01`…`PD-22` themselves | `RF-006`. Their *non-decision* is captured in `CR-04`, `CR-05`, `CR-12`, `CR-14`, `CR-15` where it drives an exposure |
| Programme risks that touch content | `00-04`. `RSK-001` super-user availability is referenced by `CR-16`, not duplicated (`CP-01`) |

---

### 4.5 Relationship to `00-04`

| Property | `00-04` `RSK-` | `RF-011` `CR-` |
|---|---|---|
| Scope | Programme, technical, commercial | Content |
| Count | 36 | 23 |
| Scale | Prob / Impact / Rating | **Identical** — adopted unchanged |
| Owner | Programme Director | Programme Content Lead |
| Cadence | Quarterly; critical at every gate | **Identical** |
| Reporting | PMO risk report | **Merged into the same report**, with the `CR-` prefix preserved |

**Rule `CX-01`.** Content risks are reported **inside** the programme risk report, not as a
separate paper. A separate content risk paper is read separately, which is how content risk became
unrepresented in the first place.

**Rule `CX-02`.** A `CR-` risk that turns out to be a programme risk is **re-registered in `00-04`
by its owner** and marked `TRANSFERRED` here. It is not renumbered into the `RSK-` space by the
content workstream — that is `00-04`'s owner's act.

**Candidates for transfer today:** `CR-02` (funding) and `CR-03` (approval capacity) are
programme-level exposures that happen to have a content cause. Both are flagged for the Programme
Director's decision at the next risk review.

---

### 4.6 Escalation

| Trigger | Route | Timing |
|---|---|---|
| A `CR-` risk rated **Critical** | Steering Committee standing item; owner reports at every gate | Immediate |
| A **Critical** risk with no mitigation in progress | CEO directly | Same week |
| A risk materialising into an issue | Moves to `RF-012` as a finding **and stays here** with status `MATERIALISED` | Same day |
| A new risk raised by an audit | Registered here within 5 working days of the audit issuing | 5 days |
| A statutory-currency risk (`CR-04`) status change | Legal & Compliance same day, per `RF-008` `SC-01` | Same day |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `00-04` | The scale, cadence and reporting route adopted unchanged |
| `CG-013` | Escalation triggers into legal and tax |
| `RF-007` | Quantifies the capacity exposures behind `CR-02`, `CR-06`, `CR-09` |
| `RF-008` | Supplies the currency exposures behind `CR-04` |
| `RF-010` | Supplies the ownership exposures behind `CR-03`, `CR-10`, `CR-13` |
| `RF-012` | Where a materialised risk is recorded as a finding |

| Depended on by | Why |
|---|---|
| The PMO risk report | `CX-01` merge |
| Steering Committee papers | Six Critical risks |
| `AUDIT_Checklist_Recurring.md` check **`G5`** — *"content risks reviewed"* | Answered from here |
| Wave gate papers | Critical risks report at every gate |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **Quarterly**, and Critical risks at every wave gate |
| Update trigger | A new audit; a risk materialising; a mitigation completing; a decision taken that closes an exposure |
| Scoring rule | Re-scored at each review, **never carried forward unexamined.** A risk whose probability has not moved in three reviews is either mis-scored or unmitigated, and both need saying |
| Closure rule | A risk is closed only when the **cause** is removed, not when the current instance is handled |
| Owner | Programme Content Lead |
| Escalation | §4.6 |

---

## Approval Record

| Gate | Required for Class E | Reviewer | Status |
|---|:--:|---|---|
| G1 Editorial | ● | Content Design | Not started |
| G2 Factual | ● | Programme Office with each named risk owner | Not started |
| G3–G6 | ○ | — | Not required |
| Final approver | — | Programme Content Lead | **Post unfilled** |

---

## Open Items

| # | Item | Owner | Blocks |
|---|---|---|---|
| `RF-011-OI-01` | **Six Critical risks have no mitigation in progress.** All six require a funding or appointment decision the content workstream cannot take | CEO / CFO | Every wave gate |
| `RF-011-OI-02` | **`CR-02` and `CR-03` are candidates for transfer to `00-04`** under `CX-02` | Programme Director | Correct risk ownership |
| `RF-011-OI-03` | **No content risk has ever appeared in the PMO risk report** — `CX-01` not yet applied | Programme Office | Steering visibility |
| `RF-011-OI-04` | **`CR-01` has no owner able to act.** The CFO can fund and the Localisation Lead can execute; neither can decide the non-negotiable is waived | CEO | `P01`, `P02` launch |
| `RF-011-OI-05` | **Check `G5` cannot pass until this register has been reviewed once** | Programme Content Lead | The next recurring audit |
| `RF-011-OI-06` | **No Programme Content Lead appointed** to own the register | CEO | Every risk's review |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; register table and maintenance procedure added per `CG-009` §3
- [x] Identifier space `CR-nn` allocated disjoint from `RSK-nnn`, with the reason stated (`RF-006` `CD-10`)
- [x] Scale, cadence and reporting route **adopted unchanged** from `00-04` so the registers merge
- [x] 23 risks registered with probability, impact, rating, mitigation, contingency and a named owning **role**
- [x] Every risk derived from an audit finding or an enumerated fact — none invented
- [x] Scope boundary stated (§4.4) so the register is not read as exhaustive
- [x] Transfer rule `CX-02` stated, and two transfer candidates identified rather than silently retained
- [x] All internal links resolve
- [x] Bengali counterpart — n/a (`bilingual: no`, `CG-010` §3.2)
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)
- [ ] **First review held; check `G5` passable** — outstanding, `RF-011-OI-05`
- [ ] **Risk owners confirmed by name** — outstanding, depends on `RF-010` `AP-01`
- [ ] **Named approver recorded** — outstanding, `RF-011-OI-06`

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
