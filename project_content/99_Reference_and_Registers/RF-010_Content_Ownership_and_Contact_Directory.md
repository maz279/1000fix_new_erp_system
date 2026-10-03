---
id: RF-010
title: Content Ownership and Contact Directory
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Programme Content Lead
author: Programme Content Lead with HR and the Programme Office
reviewers: [CEO, CTO, CFO, HR Director, Legal Counsel, Quality Manager, all Category Content Owners, Programme Office]
approver: Programme Content Lead
content_class: E
purpose: >
  The named owner and deputy for every content file family, with review dates. `CG-002` assigns
  accountability by **function**; a function cannot be telephoned, cannot approve a file and cannot
  be chased. Enumeration on 2026-08-18 confirms the consequence: **449 content files declare an
  owner and an approver, and not one of them names a person.** Four of the roles the register
  depends on are unfilled, including the Programme Content Lead who is the final approver of 26
  files and the ratifying authority for every content decision. Ownership stated only in a table
  column decays across a 36-month programme with technician-level turnover; a directory with named
  people, named deputies and staggered review dates is what survives it.
traces_to: [CG-002, CG-007, CG-008, CM-R7, CP-03, G4, RF-006, RF-008, RF-011, RF-012, LG-001, 00-04]
priority: P2
wave: W0
bilingual: no
bn_counterpart: n/a
sources:
  - source: project_content/00_Content_Governance_and_Standards/CG-002_Content_Operating_Model_and_RACI.md §4.1 content-class assignment and §5.1–§5.5 RACI by class — the functional accountability model this directory converts into named accountability
    verified: 2026-08-18
    class: P1
  - source: Extraction of owner, author, reviewers, approver and review_due front matter across all written content files, run 2026-08-18 — 449 files carry owner and approver; zero name an individual; 432 carry a review_due clustered in one week
    verified: 2026-08-18
    class: P1
  - source: project_content/_AUDIT/AUDIT-001_Content_and_Repository_Integrity_Audit.md recommendation R-07 — a named Content Lead has not been appointed
    verified: 2026-08-18
    class: P1
  - source: project_content/_AUDIT/AUDIT-017_Category_17_OP_Content_Audit.md finding OP-09 — the on-call rota needs ten people and has none; OP-04 — platform severity had three claimed owners and no owner
    verified: 2026-08-18
    class: P1
  - source: project_content/_AUDIT/AUDIT-018_Category_18_EO_Content_Audit.md finding EO-01 — no compliance officer is named in any programme document
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/00_Governance_and_Charter/00-04_Risks_Assumptions_Dependencies_and_Governance.md §6 D-15 — significant-data-fiduciary assessment and Chief Data Officer appointment, open
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2026-11-18
---

# RF-010 — Content Ownership and Contact Directory

> **This directory is deliberately published with its name columns empty.** Every row states the
> function, the responsibility and the review date; the person is blank because no person has been
> named. A directory filled with plausible role-holders would conceal the finding it exists to
> expose. §4.3 is the appointment list this file is really asking for.

---

## 1. Purpose

`CG-002` does the hard part well. It assigns every one of the 452 registered files to a content
class, and every class to a RACI. Ask it *who is accountable for `DT-010`* and it answers: Tax with
Finance, approved by the CFO.

Ask *who do I call about `DT-010` on Thursday afternoon* and it has no answer, because a function
has no telephone number. Over 36 months that gap does three things:

| Failure | How it shows up |
|---|---|
| **Ownership decays** | The person who authored `MD-022` moves teams. The file still says "Inventory". Nobody in Inventory knows it is theirs |
| **Approval stalls** | 449 files name an approver by title. Where the title is unfilled, the file cannot reach `Approved` — and 26 files name a title that **does not exist yet** |
| **Review never happens** | A review date with no named owner is a date, not an obligation. Check `G4` of the recurring audit — *"every content file has a named owner and a review date"* — is answered from this file and currently **fails** |

Enumeration confirms the position exactly. **449 files carry `owner:` and `approver:`. Every value
is a function. Zero name a person.** Only 11 files mention a deputy at all, and none names one.

---

## 2. Scope

**In scope** — named owner, deputy and approver per content family; the appointment gaps; review
scheduling; handover on role change; the contact directory structure and where the live contact
data is held.

**Out of scope**

| Excluded | Owner |
|---|---|
| The RACI model and content-class assignment | `CG-002` |
| Review gates and who signs which class | `CG-007` |
| The legal sign-off ledger | `LG-001` |
| Personal contact details — telephone, email, location | **`M21` HR system.** This file holds role-to-person mapping only; §4.6 explains why |
| Programme role appointments outside content | `00-04`, HR |
| Deputies for operational rotas — on-call, incident command | `OP-013` |

> **This file holds no personal data.** It maps a **role** to a **named post-holder**. Contact
> details, working patterns and absence are held in `M21` and referenced, never copied — a
> duplicated contact directory is stale within a quarter and is a `LG-009` retention problem
> nobody scoped.

---

## 3. Audience

| Reader | Uses this directory to |
|---|---|
| **A content author** | Find who reviews and who approves their file, by name |
| **A reviewer** | Confirm they are the accountable person, not merely a plausible one |
| **The Programme Office** | See which approvals are blocked on an unfilled post |
| **The CEO / Steering Committee** | See the appointment list in §4.3 — the shortest paper in this register and the most consequential |
| **HR** | Trigger content handover when a role-holder changes |
| **An auditor** | Verify that accountability is assigned to a person, which `CG-008` and check `G4` require |

---

## 4. Content

### 4.1 Ownership by category

Enumerated from `owner:` and `approver:` front matter on **2026-08-18**. The **Named** column is
the deliverable of this file and is empty by design.

| Cat | Code | Files | Owning function(s) | Approving function | Named owner | Named deputy |
|:--:|:--:|---:|---|---|:--:|:--:|
| 00 | `CG` | 14 | Programme Content Lead (6), Content Design Lead (4), Legal & Compliance (2), Localisation Lead (1) | Programme Content Lead | — | — |
| 01 | `VB` | 10 | Brand Lead (4), Content Design Lead (3), Design System Lead (2), Commercial Lead (1) | Content Design Lead / Brand Lead | — | — |
| 02 | `MD` | 48 | Finance (5), Commercial (5), Operations (3), MDM Lead (3), + 12 further functions | CFO / Operations Director / CCO | — | — |
| 03 | `UI` | 42 | **Content Design Lead (42 — all)** | Content Design Lead | — | — |
| 04 | `NT` | 26 | Content Design Lead (19) + 7 joint | Content Design Lead | — | — |
| 05 | `DT` | 44 | Tax with Finance (5), Finance (4), Quality (2), Procurement (2), + 14 further | **CFO (33)** / Legal Counsel | — | — |
| 06 | `SP` | 34 | Business Process Lead (3), Operations with Quality (2), Finance (2), + 20 further | Operations Director | — | — |
| 07 | `KB` | 16 | Technical (5), Knowledge Manager (3), + joint | Technical Director | — | — |
| 08 | `TR` | 24 | **Learning & Development (18)** + 6 joint | Quality Manager / L&D | — | — |
| 09 | `HC` | 20 | **Content Design (15)** + 5 joint | Content Design Lead | — | — |
| 10 | `LG` | 24 | Legal & Compliance (7), + with CDO (2), with CTO (2), + 13 further | **Legal Counsel (14)** | — | — |
| 11 | `BN` | 18 | **Localisation Lead (18 — all)** | Localisation Lead with Content Design Lead | — | — |
| 12 | `DM` | 14 | Data Migration Lead (3), Data Migration (3), + joint | CTO | — | — |
| 13 | `TS` | 18 | QA Lead (5), Business Owners Forum with QA Lead (4), + 9 further | QA Lead with Programme | — | — |
| 14 | `RP` | 16 | BI Lead (3) + 13 joint or domain | CTO / CFO | — | — |
| 15 | `AP` | 12 | **Platform Engineering Lead (11)**, Security Lead with Legal Counsel (1) | CTO | — | — |
| 16 | `CM` | 18 | Change Lead (8), Marketing with Change (2), Change Lead with HR (2), + 6 | Programme Office | — | — |
| 17 | `OP` | 16 | Support Lead (3), Platform Engineering (3), + 10 further | CTO | — | — |
| 18 | `EO` | 14 | Commercial (3), Procurement (2), Account Management (2), + 7 | CCO | — | — |
| 19 | `MM` | 11+ | Design System Lead (2), Brand Lead with Platform Engineering (2), + further | Brand Lead | — | — |
| 99 | `RF` | 12 | Programme Content Lead (11), Compliance (1) | Programme Content Lead / Legal Counsel | — | — |

**Two structural observations.**

**Four categories have a single owning function for every file** — `UI` (42), `BN` (18), `AP` (11
of 12), `TR` (18 of 24). That is coherent ownership and a **single point of failure**. If the
Content Design Lead is unavailable, forty-two UI copy packs have no owner; if the Localisation
Lead is, the entire bilingual obligation stops. **These four are where a named deputy matters
most, and none is named.**

**The CFO approves 33 files and Legal Counsel 14** — the two heaviest approval loads, and both fall
on the two functions with the least discretionary time. §4.5 addresses the consequence.

---

### 4.2 Ownership roles

| Role | Definition | Applies to |
|---|---|---|
| **Owner** | Accountable for the file being correct, current and reviewed. **One person, never a committee** | Every file |
| **Deputy** | Acts with the owner's authority in their absence. Named, not implied | Every file — **none named** |
| **Author** | Produces the content. May differ from the owner | Every file |
| **Reviewer** | Discharges a named gate under `CG-007` | Per gate |
| **Approver** | Sets `status: Approved`. For Class A and B this is a legal act (`CM-R7`) | Every file |
| **Custodian** | Keeps the file in the repository and its register row current | Programme Content Lead |

**Rule `OW-01`.** Owner and approver are **different people** for Class A and B files. A file whose
author, owner and approver are the same person has no review, whatever the process says.

**Rule `OW-02`.** A deputy is named at the **family** level, not per file. Forty-two `UI` files
need one deputy, not forty-two.

---

### 4.3 The appointment list

**The operative section of this file.** Seven roles the content register depends on are unfilled or
undefined. Each blocks work that is otherwise ready.

| # | Role | Status | What is blocked | Raised by | Owner |
|:--:|---|---|---|---|---|
| `AP-01` | **Programme Content Lead** | **Not appointed** | Final approver of **26 files**; ratifying authority for **all 14 content decisions** in `RF-006`; custodian of the register; the escalation point in every Category 99 file | `AUDIT-001` `R-07` | **CEO** |
| `AP-02` | **Data Protection Officer** | **Not appointed** | `LG-008`–`LG-012`, `AP-012`; the DPIA that does not exist; PDPA 2026 accountability with a ~May 2027 compliance deadline | `AP-012` `O-06`; `PD-15` | CEO with Legal |
| `AP-03` | **Chief Data Officer** *(if significant data fiduciary)* | **Assessment not done** | The assessment itself is decision `PD-15`. Penalty exposure doubles to BDT 50 lakh if classified and unappointed | `00-04` `D-15` | CEO with Legal |
| `AP-04` | **Marketplace compliance officer** | **Not named in any programme document** | `P07` launch; the 72-hour complaint path; the ten-day settlement obligation | `AUDIT-018` `EO-01` | CEO |
| `AP-05` | **Accessibility reviewer** | **Not appointed** | `TS-016` cannot be executed on any portal; `PS-04` conformance is claimed and unevidenced | `AUDIT-014` | CTO with Content Design |
| `AP-06` | **Deputies for the four single-owner categories** — `UI`, `BN`, `AP`, `TR` | **None named** | 83 files have one point of failure each | This file, `OW-02` | Category owners |
| `AP-07` | **On-call rota — ten people** | **Zero staffed** | `OP-013`; every out-of-hours incident. *(Operational, listed for completeness; owned by `OP-013`)* | `AUDIT-017` `OP-09` | Platform Engineering Lead |

> **`AP-01` is the one that unblocks the others.** The Programme Content Lead is the role that
> would chase the remaining six. Its absence is why a register that is 95% written is 0% approved.

---

### 4.4 Review scheduling — and the peak nobody planned

**What was found.** 432 of 449 files carry `review_due:` and they cluster in a single week:

| `review_due:` | Files |
|---|---:|
| 2027-02-15 | **214** |
| 2027-02-18 | 95 |
| 2027-02-20 | 50 |
| 2027-02-17 | 39 |
| 2027-02-19 | 18 |
| 2027-02-16 | 16 |
| 2026-11-15…18 *(Category 99)* | 17 |

**432 files fall due inside six days**, because each was given a six-month review at the moment it
was written and the whole set was written in one week of August 2026.

**Why it matters.** A review cycle is only a control if it can be executed. 432 reviews in one week
across 21 functions is not a review; it is a rubber stamp, and the first rubber stamp teaches
everyone that the date is decorative. The Content Design Lead alone would own **68 reviews** in
that week; the CFO would approve 33.

**Remediation — rule `OW-03`.** Review dates are **staggered by category and pinned to the wave
that consumes the content**, not set by adding six months to the authoring date.

| Trigger | Review cadence | Categories |
|---|---|---|
| **Wave boundary the content is consumed at** | Per wave | `MD`, `UI`, `DT`, `SP`, `TR`, `TS`, `OP` |
| **Statutory event** — Finance Act, statute amendment, standard revision | On `RF-008` status change | `DT` statutory, `LG`, `MD-037`, `MD-043` |
| **Quarterly** | Fixed | `RF-006`, `RF-011`, `RF-012` — the live registers |
| **Semi-annual** | Fixed | `CG`, `VB`, `BN` standards, `AP`, `RF-001`–`RF-005`, `RF-007`–`RF-010` |
| **Annual** | Fixed | `KB`, `HC`, `CM`, `EO`, `MM` |

Applying `OW-03` moves the 2027-02 peak into a distribution no week of which exceeds ~35 files.
Carried to `RF-006` as a content decision and to `RF-012` as finding `RF-06`.

---

### 4.5 Approval load

| Approver | Files | Comment |
|---|---:|---|
| Content Design Lead | **91** | Plus 8 joint with the CTO. The single largest load in the register |
| **CFO** | **33** | Almost all Class A statutory `DT` files, each also requiring **unwaivable G6** |
| Programme Content Lead | **26** | **Post unfilled — `AP-01`** |
| Operations Director | 15 | |
| **Legal Counsel** | **14** | Plus 6 joint with the CCO. Every one is Class A or B |
| CTO | 13 | |
| Chief Commercial Officer | 11 | |
| Quality Manager | 7 | |
| Others | ~239 | Across 20 further functions |

**Rule `OW-04`.** An approver holding more than 40 files names a **delegated approver per
category**, recorded here. Delegation is by name and by category, never blanket — a blanket
delegation of 91 approvals is an abdication, and `CM-R7` requires a *recorded named sign-off*, not
a recorded named delegate.

**Rule `OW-05`.** The CFO's 33 and Legal Counsel's 14 are **not delegable**. `CG-002` §5.1 and
§5.2 make the CFO and Legal Counsel the accountable approvers for Class A and B; those are the
files with statutory and contractual consequence and the approval is the control.

---

### 4.6 The directory itself

| Field | Held here | Held in `M21` |
|---|:--:|:--:|
| Role name | ● | ● |
| Post-holder name | ● | ● |
| Category and file families owned | ● | ○ |
| Named deputy | ● | ○ |
| Approval authority and delegation | ● | ○ |
| Review obligations | ● | ○ |
| Email, telephone, location | ○ | ● |
| Working pattern, absence, leave | ○ | ● |
| Employment record | ○ | ● |

**Rule `OW-06`.** Contact details are **referenced from `M21`, never copied here.** A duplicated
directory is stale within a quarter, and copying employee contact data into a content register
creates a personal-data holding with no lawful basis stated and no retention rule — a `LG-009`
problem this file will not create.

---

### 4.7 Handover on role change

Triggered by HR, not by the departing person.

| Step | Action | Owner | Timing |
|:--:|---|---|---|
| 1 | HR notifies the Programme Content Lead of any change affecting a content-owning role | HR | On notice |
| 2 | Files owned by the outgoing role are listed from this directory | Programme Content Lead | 2 working days |
| 3 | **Deputy assumes ownership immediately** — this is what `OW-02` exists for | Deputy | Same day |
| 4 | Open items, decisions and reviews on those files are listed from `RF-006` and `RF-012` | Programme Content Lead | 5 working days |
| 5 | Handover meeting; incoming owner confirms acceptance **in writing** | Both | Before last working day |
| 6 | Directory updated; `owner:` front matter unchanged — **it names the function, not the person** | Programme Content Lead | 2 working days |
| 7 | Where no successor exists, files move to the **category owner** and the gap is added to §4.3 | Programme Content Lead | Immediately |

**Rule `OW-07`.** A file is **never left without an owner**, even temporarily. Step 7 is
mandatory, and the escalation is that the category owner absorbs the load and it becomes visible
in §4.3 rather than invisible in a departed person's inbox.

---

### 4.8 Statistics

| Measure | Value |
|---|---:|
| Content files with an `owner:` | **449** |
| Content files with an `approver:` | **449** |
| Owners naming an **individual** | **0** |
| Deputies named | **0** |
| Files mentioning a deputy at all | 11 |
| Distinct owning functions | **~60** |
| Distinct approving functions | **~25** |
| Roles unfilled that the register depends on | **7** (§4.3) |
| Files whose approver's post is **unfilled** | **26** |
| Files carrying a `review_due:` | **432** |
| Files whose `review_due:` falls in the week of 2027-02-15 | **432** |
| Check `G4` — *"every content file has a named owner and a review date"* | ❌ **FAILS** on the owner half |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `CG-002` | The functional accountability this directory names |
| `CG-007`, `CM-R7` | Approval authority and the recorded-sign-off rule |
| `M21` | Holds the contact data referenced under `OW-06` |
| `RF-008` | Fires statutory-event reviews under `OW-03` |
| `00-04` `D-15` | The CDO appointment in `AP-03` |

| Depended on by | Why |
|---|---|
| `AUDIT_Checklist_Recurring.md` check **`G4`** | Answered from §4.8 |
| Every file at `CG-008` Definition of Done | "Named approver recorded" |
| `RF-011` | Single-owner and unfilled-post risks |
| `RF-012` | Finding `RF-06`, the review peak |
| `LG-001` | Sign-off log; needs a named signatory |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **Quarterly**, and immediately on any role change |
| Update trigger | Appointment; resignation; delegation; a new content family; a category owner change |
| Naming rule | A role is named to **one person**. Two names in an owner cell is an unresolved ownership dispute, not shared ownership (`OW-01`) |
| Privacy rule | No contact detail is stored here (`OW-06`) |
| Owner | Programme Content Lead — **the post this file is asking to be filled** |
| Escalation | A file with no owner for more than **5 working days** goes to the CTO. A category with no owner goes to the Steering Committee |

---

## Approval Record

| Gate | Required for Class E | Reviewer | Status |
|---|:--:|---|---|
| G1 Editorial | ● | Content Design | Not started |
| G2 Factual | ● | HR Director with Programme Office | Not started |
| G3–G6 | ○ | — | Not required |
| Final approver | — | Programme Content Lead | **Post unfilled — `AP-01`** |

---

## Open Items

| # | Item | Owner | Blocks |
|---|---|---|---|
| `RF-010-OI-01` | **`AP-01` — no Programme Content Lead.** Final approver of 26 files; ratifying authority for 14 decisions; owner of this file | **CEO** | Every Class E approval; `RF-006` ratification |
| `RF-010-OI-02` | **`AP-02`/`AP-03` — no DPO, no CDO, no fiduciary assessment.** Compliance deadline ~May 2027 | CEO with Legal | 12 `LG`/`AP` files; the absent DPIA |
| `RF-010-OI-03` | **`AP-04` — no marketplace compliance officer** | CEO | `P07` launch |
| `RF-010-OI-04` | **`AP-05` — no accessibility reviewer.** `TS-016` unexecutable on all twelve portals | CTO | `PS-04` conformance evidence |
| `RF-010-OI-05` | **`AP-06` — no deputies.** Four categories (83 files) have a single point of failure | Category owners | Continuity |
| `RF-010-OI-06` | **Zero named individuals across 449 files.** Check `G4` fails | Programme Content Lead | Every recurring audit |
| `RF-010-OI-07` | **432 reviews fall due in one week (2027-02-15…20).** `OW-03` staggering not yet applied | Programme Content Lead | The first review cycle |
| `RF-010-OI-08` | **Content Design Lead approves 91 files; `OW-04` delegation not recorded** | Content Design Lead | Approval throughput |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; register table and maintenance procedure added per `CG-009` §3
- [x] All 21 categories mapped to owning and approving functions, enumerated from front matter
- [x] Name columns published **empty**, because no person is named — the finding is not concealed
- [x] Appointment list `AP-01`–`AP-07` stated with what each blocks and who must act
- [x] Review-date peak found, quantified and given a remediation rule (`OW-03`)
- [x] Approval load quantified; delegation rules `OW-04`, `OW-05` stated
- [x] Handover process defined with a no-orphan rule (`OW-07`)
- [x] **No personal data held** (`OW-06`)
- [x] Check `G4` answered honestly as failing
- [x] All internal links resolve
- [x] Bengali counterpart — n/a (`bilingual: no`, `CG-010` §3.2)
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)
- [ ] **Named owners and deputies recorded** — outstanding, `RF-010-OI-06`. **This file is not complete until §4.1 has names in it**
- [ ] **Named approver recorded** — outstanding, `AP-01`

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
