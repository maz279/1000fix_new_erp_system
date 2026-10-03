---
id: CM-001
title: Programme Narrative and Change Story
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-20
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Change Lead
author: Change Lead with the Programme Content Lead
reviewers: [CEO, CTO, CFO, CCO, Operations Director, HR Director, Quality Manager, Content Design Lead, Localisation Lead, Brand]
approver: Content Design Lead, with CEO endorsement of the narrative claims
content_class: D
purpose: >
  Fixes the single story the programme tells for thirty-six months — why the Company is doing this,
  what changes, what deliberately does not, what it means for each of eleven audiences, and which
  claims may never be made. Nine waves told as nine unrelated announcements are perceived as nine
  disruptions; every other file in this category and every training pack, town hall and go-live
  message derives its framing from here, so without it the framing is re-invented per wave by
  whoever is speaking.
traces_to: [00-02, 00-04, 06-01, CM-002, CM-003, CM-005, CM-010, CM-011, CM-018, TR-001, VB-001, VB-002, CG-003, CG-004, CON-10, RSK-003, RSK-008, RSK-009, RSK-012]
priority: P1
wave: W0
bilingual: yes
bn_counterpart: CM-001_Programme_Narrative_and_Change_Story_BN.md
sources:
  - source: 1000fix_ERP_Module/00_Governance_and_Charter/00-02 §1 — the decision being documented; the expansion from 11 modules and 6 portals to 67 modules and 12 portals, taken before build starts
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/00_Governance_and_Charter/00-02 §2 — v1.0 versus v2.1 dimensions; 36 months, 9 waves; "the first 18 months of v2.0 deliver everything v1.0 promised, on the same dates"
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/00_Governance_and_Charter/00-04 §4 CON-10 — automation must augment roles, not displace staff without approval
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/00_Governance_and_Charter/00-04 §1.2 RSK-008, RSK-009, RSK-012 and §8 — what would make this programme fail, stated plainly
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-01 §7 — change management activities; §6 rollout pattern per location
    verified: 2026-08-20
    class: P1
  - source: primary-doc/1000FiX_ERP_System_Comprehensive_BRD.md §6.2 — the fifteen current-state process failures, each with its measured consequence
    verified: 2026-08-20
    class: P1
  - source: primary-doc/1000FiX_ERP_System_Comprehensive_BRD.md §6.3 — performance baseline against industry benchmark, eleven measures
    verified: 2026-08-20
    class: P1
supersedes: none
review_due: 2027-02-20
---

# CM-001 — Programme Narrative and Change Story

> **Identifier note (`CG-005` §3.3).** `CM-001` is a **content** identifier. `CM-R1`…`CM-R10`
> in the Master Index §9 are *register maintenance rules* that share the `CM` letters and are
> unrelated to this category's files. This file's own rules carry the `NR-` prefix.
>
> **Scope note.** This file owns **the story and the claim discipline**. It does not own the
> schedule (`CM-003`), the audience analysis (`CM-002`), or any delivered message (`CM-005`…`CM-017`).
> Every one of those quotes from here; none of them re-writes it.

---

## 1. Purpose

A thirty-six-month programme is not experienced by staff as a programme. It is experienced as a
sequence of things that arrive: a new screen, a device, a rule that used to be optional, a report
their manager now reads. Whether that sequence is understood as **one intended change** or as
**nine unrelated disruptions** is decided by whether a consistent story exists before the first
wave, not after it.

The register's justification is exact: *"Nine waves of change with no consistent story becomes
nine unrelated disruptions in staff perception."*

**Consequence of absence (`CP-03`).**

| Failure | Consequence |
|---|---|
| No agreed "why" | Each speaker invents one. Field staff hear cost-cutting, branch staff hear surveillance, finance hears audit |
| No agreed "what does not change" | Every rumour about redundancy, pay and transfer is unfalsifiable |
| No per-audience translation of the story | The programme talks about modules; a technician wants to know what happens to their day |
| No claim discipline | Someone promises a benefit the system will not deliver in W2, and the whole story loses credibility at W3 |
| Nine wave announcements with nine framings | The workforce concludes there is no plan, which is `RSK-003` programme fatigue arriving early |
| No Bengali narrative | The 275–635 people whose adoption decides `RSK-008` receive the story second-hand |

> **`NR-01` — the narrative is a governed artefact, not a marketing asset.** It is versioned,
> reviewed and quoted verbatim. A speaker who improves it on stage has forked it.

---

## 2. Scope

**In scope:** the programme's stated reason for existing; the honest current-state position; what
changes and what explicitly does not; the eleven audience translations; the benefit claims that may
be made and the dates they become true; the claims that are prohibited; the vocabulary; the
narrative's own failure modes; and rules `NR-01`…`NR-18`.

**Out of scope:**

| Subject | Owned by |
|---|---|
| Who the audiences are, their influence, concerns and channels | [`CM-002_Stakeholder_Map_and_Communication_Plan.md`](CM-002_Stakeholder_Map_and_Communication_Plan.md) |
| When anything is said | [`CM-003_Communication_Calendar_by_Wave.md`](CM-003_Communication_Calendar_by_Wave.md) |
| The wave announcement itself | [`CM-005_Wave_Launch_Communication_Kit.md`](CM-005_Wave_Launch_Communication_Kit.md) |
| Spoken delivery and slides | [`CM-010_Town_Hall_and_Roadshow_Content.md`](CM-010_Town_Hall_and_Roadshow_Content.md) |
| Answers to objections the narrative provokes | [`CM-011_Resistance_Objection_and_FAQ_Handling_Pack.md`](CM-011_Resistance_Objection_and_FAQ_Handling_Pack.md) |
| Per-role impact detail | [`CM-018_Change_Impact_Statement_Template.md`](CM-018_Change_Impact_Statement_Template.md) |
| Brand voice, tone and lexical rules | `VB-001`, `VB-002`; mechanics in `CG-003` |
| Approved terminology and its Bengali equivalents | `CG-004`, `BN-003` |
| Customer-facing marketing positioning | The corporate website content set — **separate register, Master Index §11** |
| The change management *plan* | **`06-05` — does not exist** (`O-01`) |

---

## 3. Audience

| Audience | Uses this file to… |
|---|---|
| **Change Lead** | Hold every communication to one story |
| **CEO and Steering Committee** | Say the same thing the programme says, without briefing notes |
| **Branch managers (51+)** | Explain the programme to their own staff in their own words, correctly |
| **Champions (one per branch)** | Answer the question they are asked most: *"why are we doing this?"* |
| **L&D** | Open every course pack on the same framing (`TR-001`) |
| **Content Design** | Review any programme communication against a stated position |
| **Localisation Lead** | Translate one narrative once, rather than nine framings nine times |
| **HR** | Ensure nothing said about roles contradicts `CON-10` |

---

## 4. Content

### 4.1 The story in six sentences

**`NR-02`: the short form is the governing form.** Everything longer is an expansion of it, and
anything that contradicts it is wrong regardless of length.

> 1000FiX runs fourteen revenue streams on spreadsheets, paper job cards, whiteboards and
> WhatsApp. That worked at one branch. At 51+ branches, 250,000+ customers a month and nine new
> business lines it does not, and the evidence is measured: 15–20% of warranty revenue is never
> recovered, month-end takes 15–20 days, and a third of a technician's day is spent travelling.
> We are building one system of record so that every job, part, invoice, claim and contract lives
> in one place — delivered in nine waves over three years, not in one switch-over.
> **Your job is not being replaced by the system; the paper around your job is.**
> We will tell you what is coming before it comes, train you in Bengali before you are given
> access, and support you on the floor for four weeks after every launch.

**`NR-03` — the fifth sentence is the one that carries the programme.** It is a commitment under
`CON-10`, not a reassurance. If the Company later intends a role reduction, this narrative is
withdrawn and re-approved before that intention is communicated; it is not quietly softened.

### 4.2 The current state, stated honestly

`NR-04`: **the story opens on measured failure, not on aspiration.** Staff already know the
current state; a narrative that describes it politely loses credibility in its first paragraph.

| # | What we do today (BRD §6.2) | What it costs |
|:--:|---|---|
| 1 | Walk-in intake on paper or a spreadsheet | ~10-minute intake; no service-history lookup at the counter |
| 3 | Dispatch by phone and WhatsApp from a paper job list | ~35% of the working day in travel; no skill or certification matching |
| 4 | Paper service forms keyed 1–3 days later | Forms lost; photos non-standard; QC not enforced |
| 6 | Each branch tracks stock in its own spreadsheet | Stockout at one branch, excess at another; **van stock entirely untracked** |
| 7 | Warranty claims prepared and chased manually by email | 30–90 day submission delay; **15–20% revenue leakage**; 60–120 days to reimbursement |
| 10 | Branch spreadsheets consolidated monthly in Excel | **15–20 day close**; decisions on stale data |
| 12 | Certification tracked manually, if at all | **Lapses are discovered when a brand rejects a claim** |
| 15 | Nine new revenue streams | **No system whatsoever** |

**The eleven baseline measures in BRD §6.3 are the narrative's evidence base.** Where a
communication states a current-state figure it takes it from there, cites it, and does not round it
in the flattering direction (`NR-14`).

### 4.3 What changes, and what does not

| | Changes | Does not change |
|---|---|---|
| **The work** | Where it is recorded, and that it is recorded once | What a good repair is; who the customer is; the standard expected |
| **The tools** | Paper, spreadsheets and whiteboards are withdrawn per wave | The hotline number **16743**; the branches; the brands we are authorised on |
| **Visibility** | Jobs, stock, cash and claims become visible in real time to the roles entitled to see them | Who your manager is; who decides your appraisal |
| **Pay** | Incentives become **calculable** from recorded work (`M57`) | The incentive scheme itself — any change to it is an HR change, announced by HR, not by the programme |
| **Language** | Field and branch surfaces become Bengali-first, complete | That Bengali is the working language at the counter and in the field |
| **Headcount** | **Nothing.** `CON-10` binds the programme | Roles are augmented; displacement requires separate approval outside this programme |

> **`NR-05` — the right-hand column is the more important one.** In every change programme the
> unstated is assumed to be at risk. The list of what does not change is published with the same
> prominence as the list of what does.

### 4.4 Audience translations

**`NR-06`: the narrative is delivered in the audience's own terms or it is not delivered.**
Eleven translations exist. Each is one paragraph, each answers *"what does this mean for me on a
Tuesday"*, and none of them uses the word "module".

| # | Audience | Population | The story, in their terms | The one thing they most need to hear |
|:--:|---|---|---|---|
| A1 | **Field technicians** (`R10`–`R12`) | 200–400 | The paper form and the phone call disappear. Your jobs, the device history, the van stock and the customer's signature are all on one phone, and it works with no signal | **Your earnings become visible and calculable, on the same phone** |
| A2 | **Branch counter staff** (`R08`) | 150–250 | Intake stops being retyping. The customer is found, the device is found, the token prints, the SMS goes out | **Intake is designed to be faster than today, and it is measured** (`G1-03`, under 3 minutes) |
| A3 | **Branch managers** (`R06`) | 51+ | You stop assembling your own numbers. Today's position — WIP, cash, staff, uncollected devices — is on one screen | **The dashboard is your tool, not surveillance of you** (`00-04` RSK mitigation) |
| A4 | **Workshop supervisors and storekeepers** (`R09`, `R18`) | 20–40 · 51+ | The bench board and the stock book become the same record, and the count is a scan | **You stop being blamed for variances you could not see** |
| A5 | **Finance and cashiers** (`R26`–`R29`) | 51+ cashiers, 12–24 finance | Invoices come from closed jobs automatically; the close moves from 15–20 days towards 5 | **Controls tighten. This is the point, and it protects you personally** |
| A6 | **HR and people** (`R30`, `R31`) | 4–8 | Attendance, leave and payroll stop being three spreadsheets | **Payroll runs in parallel for two full cycles before it is trusted** |
| A7 | **Contact centre** (`R34`, `R35`) | 34–70 | The caller is identified before you speak, with their jobs, contracts and dues on the screen | **Fewer "let me check and call you back" conversations** |
| A8 | **Executives** (`R01`–`R05`) | 5–8 | Fourteen revenue streams become measurable; nine of them become operable at all | **The date the last v1.0 commitment lands does not move: Month 18** |
| A9 | **Customers** | 250,000+/month | Book, track, approve and pay without calling. Your history stays yours | **Your existing reference numbers remain searchable** (`CM-013`) |
| A10 | **Corporate clients** | 500–2,000 users | Your estate, your requests, your consolidated invoice, your SLA position — self-served | **Your account manager does not disappear** (`CM-014`) |
| A11 | **Vendors, sellers and brand partners** | 1,000–3,000 | Interaction moves from email to a portal with a status you can see | **Payment and claim timelines become visible, and therefore arguable with evidence** |

> **`NR-07` — A1 is the load-bearing translation.** `RSK-008` (technician rejection of the mobile
> app) is one of five Critical programme risks and is rated `H`/`Critical`. `00-04` §8 states it
> without hedging: *"Four hundred people in the field decide whether this programme works."* The
> A1 paragraph is reviewed by working technicians before it is used, not only by the Change Lead.

### 4.5 The claim schedule — what may be said, and from when

**`NR-08`: a benefit may be claimed only from the wave that delivers it, and only in the form the
gate criterion states.** A benefit promised early and delivered late is the mechanism by which a
programme's communications stop being believed.

| Claim | May be made from | Basis | Form it must take |
|---|:--:|---|---|
| Walk-in intake under 3 minutes | **W1 gate passed** | `G1-03`, timed observation over 20 samples | *"Measured at under 3 minutes at pilot sites"* — never *"intake is now instant"* |
| Bengali on every delivered screen | W1 gate passed | `G1-08` translation coverage report | Scoped to **delivered** screens only |
| The technician app works offline for a full day | **W2 gate passed** | `G2-02`, demonstrated with zero data loss | 24 hours; not "always works" |
| Travel time down 15% | W2 gate passed | `G2-04`, measured | Percentage against the measured baseline, with the baseline stated |
| Inventory accuracy ≥ 95% | W2 gate passed | `G2-06`, verified by count | **At migrated locations**, not network-wide |
| Invoices generated automatically from closed jobs | W3 gate passed | `G3-01` | 100% of closed jobs, from the wave's live branches |
| Month-end close in 5 days | W3 gate passed | `G3-05`, first full month | *"First full month closed within 5 days"* — a single observation, said as one |
| Warranty claims submitted within 72 hours | W4 gate passed | `G4-01` | Auto-created within 24 h, submitted within 72 h |
| v1.0 scope complete | **W4 gate passed, Month 18** | `G4-10` | The single most protected claim in the programme (`00-02` §2) |
| Payroll runs without error | W5 gate passed | `G5-01`, first run validated and paid | Never claimed before the second parallel cycle completes |
| All 51+ centres live | W5 gate passed | `G5-06` | Counted, not projected |

> **`NR-09` — `G4-10` cannot currently be evidenced.** *"Every v1.0 BRD requirement demonstrated as
> delivered or formally superseded"* is a traceability query against a requirement baseline the
> repository does not agree on — 2,930 / ~2,352 / 3,343 (`AUDIT-014` TS-01, `AF-06`). The
> *"v1.0 scope complete"* claim at Month 18 is the programme's most quoted milestone and it rests
> on a number that has three current values. Recorded as `O-03`.

### 4.6 Prohibited claims

**`NR-10`: these are not discouraged. They are prohibited, in every language and every channel.**

| Prohibited | Why | Say instead |
|---|---|---|
| *"No one will lose their job"* as an unqualified promise | The programme cannot bind future Company decisions; an unqualified promise that is later broken destroys every other statement | *"This programme is required to augment roles, not displace staff. Any change to that requires separate approval outside the programme"* (`CON-10`) |
| *"The system will be easier"* | Unfalsifiable and, in the first fortnight, false | *"Intake is designed to be faster than today, and we measure it"* |
| *"Everything goes live in [month]"* | Nine waves; nothing goes live all at once | *"Your branch goes live in [wave], and here is the four-week pattern before it"* |
| *"AI will handle it"* | `RSK-020`; models are W6–W8 and human-in-the-loop on material decisions | Name the specific capability and its wave |
| Any number without a source | `CM-R8`, `CG-012` | Cite `06-02`, `04-00` or the BRD baseline, with the verification date |
| Any comparison against a named competitor | Outside this programme's remit; belongs to the website content set | Silence |
| *"The old system will be switched off on [date]"* before `C9` | Legacy withdrawal is a gate, not a date (`DM-014` `CV-03`) | *"Legacy stops when your wave's withdrawal criteria are confirmed"* |
| Any statement about pay, grading or incentive scheme changes | Belongs to HR, not to the programme | Route to HR; `CM-011` §objections |

### 4.7 Vocabulary

`NR-11`: the narrative uses the operational word, not the programme word.

| Do not say | Say | Because |
|---|---|---|
| Module, `M15`, `P02` | The stock system · the technician app | Internal identifiers mean nothing outside the programme |
| Go-live | The day your branch starts using it | "Go-live" is a programme event; staff experience a Monday |
| User | Technician · agent · cashier · manager | `CG-003`; name the person |
| Rollout | Your wave | Rollout is something done *to* people |
| Legacy | The spreadsheets and paper forms we use today | Nobody calls their own tool legacy |
| Adoption | Using it for the real job | Adoption is a measurement word, correct in `CM-016`, wrong in a town hall |
| Resource | Person, or the role name | `CG-003` |

**Bengali equivalents are fixed in `BN-003`, not chosen per translation** (`NR-12`). Where no
approved Bengali term exists, the English term is used untranslated per `BN-004` rather than a new
coinage being invented in a town hall.

### 4.8 Audience · channel · timing · message · call-to-action

The category-standard table (`CG-009` §3). **This file supplies the message column's *content*;
`CM-002` supplies the channel and `CM-003` supplies the timing.**

| Audience | Channel | Timing | Message from this file | Call to action |
|---|---|---|---|---|
| All staff | Town hall + branch cascade | **W0, before any build communication** | §4.1 six sentences, §4.3 what does not change | Ask your question — every one is answered in `CM-011` |
| Branch managers | Manager briefing | W0 | §4.1 plus §4.4 A3 | Brief your branch within five working days |
| Champions | Champion forum | W0 and monthly | Full file | Use §4.4, do not improvise |
| Field technicians | Bengali video + toolbox talk | W0, repeated at W2−4 weeks | §4.4 A1 | Volunteer for the field pilot |
| Steering Committee | Steering pack | Monthly | §4.5 claim schedule, current position | Approve or correct the claims before they are made |
| Customers | Portal, SMS, hotline hold message | **W2 only** — not before | §4.4 A9 | None until the portal exists |
| Corporate clients | Account manager | W4 | §4.4 A10 | Schedule the transition session |
| Vendors, sellers, brands | Portal onboarding | W3 / W4 / W7 | §4.4 A11 | Complete portal registration |

### 4.9 How this narrative fails

`NR-13`: the failure modes are listed so they are recognised early, not diagnosed late.

| Failure mode | Early signal | Response |
|---|---|---|
| **Drift** — each wave's story diverges from this file | Two wave kits describe the benefit differently | `NR-01`; the kit is corrected, not the narrative |
| **Inflation** — claims grow with each retelling | A number appears without a source | `NR-14`; withdraw and re-issue |
| **Silence** — nothing is said between waves | Rumour volume rises at the champion forum | `CM-009` cadence exists precisely for this |
| **Contradiction** — an HR or ops decision contradicts §4.3 | A branch hears about a change from its manager first | Narrative is re-approved before the decision is communicated |
| **Fatigue** — the story is true but nobody is listening | Town hall attendance falls; `RSK-003` | Shorten to §4.1; stop repeating W1 content in W5 |
| **English-only delivery** | The Bengali counterpart lags the English | `NR-16`; the wave communication does not go out |

### 4.10 Governing rules

| # | Rule | Class |
|---|---|:--:|
| `NR-01` | The narrative is versioned and quoted, never improvised or "improved" in delivery | **H** |
| `NR-02` | The six-sentence short form governs; longer forms expand it and may not contradict it | **H** |
| `NR-03` | The `CON-10` commitment is withdrawn and re-approved before any contrary intention is communicated | **H** |
| `NR-04` | The story opens on the measured current state, cited to BRD §6.2 and §6.3 | **H** |
| `NR-05` | What does not change is published with equal prominence to what does | **H** |
| `NR-06` | Every audience receives the story in its own terms; eleven translations exist | **H** |
| `NR-07` | The technician translation (A1) is reviewed by working technicians before use | **H** |
| `NR-08` | A benefit is claimed only from the wave that delivers it, in the form its gate criterion states | **H** |
| `NR-09` | Any claim resting on requirement coverage is suspended until the baseline is agreed (`O-03`) | **H** |
| `NR-10` | The eight prohibited claims are prohibited in every language and channel | **H** |
| `NR-11` | Operational vocabulary only; no module, portal or programme jargon in staff-facing narrative | **H** |
| `NR-12` | Bengali terms come from `BN-003`; no term is coined in delivery | **H** |
| `NR-13` | The six failure modes are reviewed at each wave boundary against their early signals | **S** |
| `NR-14` | Every figure carries a source and a verification date (`CM-R8`, `CG-012`) | **H** |
| `NR-15` | The narrative is re-verified at every wave gate; superseded claims are removed, not left standing | **H** |
| `NR-16` | No programme communication is released in English ahead of its Bengali counterpart to a Bengali-first audience (`CG-010`, `CM-R6`) | **H** |
| `NR-17` | Changes to §4.1, §4.3 or §4.6 are MAJOR (`CG-006`) and require CEO endorsement, not editorial approval | **H** |
| `NR-18` | Every downstream `CM` file names the narrative section it derives from | **H** |

> Class: **H** hard block · **A** approved override · **S** soft warning · **C** computed — the same
> scale as `05-05` §1.

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `00-02` Executive Summary and Scope Charter | The decision being narrated; **still `DRAFT FOR APPROVAL`** (`O-02`) |
| `00-04` §4 `CON-10` | The single most consequential sentence in §4.3 |
| `00-04` §1.2 and §8 | The adoption risks the narrative is written against |
| `06-01` §7 | The change-management activities this narrative feeds |
| `06-02` §4 gate criteria | The claim schedule in §4.5 |
| BRD §6.2, §6.3 | The measured current state |
| [`CM-002_Stakeholder_Map_and_Communication_Plan.md`](CM-002_Stakeholder_Map_and_Communication_Plan.md) | Who each translation is aimed at |
| `BN-003` · `CG-004` | Terminology, both languages |
| `VB-001`, `VB-002` | Voice and tone the narrative is written in |
| **`06-05`** | **Does not exist** — the change plan this narrative should sit inside (`O-01`) |

| Depended on by |
|---|
| Every file in Category 16 · `TR-001` course framing · `CM-018` per-role statements · the `CM-004` steering pack's benefits section · `HC-015` FAQ tone · `CM-016` campaign propositions |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **At every wave gate** — the claim schedule in §4.5 changes at each one |
| Trigger for out-of-cycle review | A gate criterion missed · a scope change under `00-04` §5.4 · any HR decision touching §4.3 · a `CON-10` change |
| Owner | Change Lead; §4.5 claims co-owned with the PMO |
| Change log | `RF-006`; §4.1, §4.3 and §4.6 changes are MAJOR (`NR-17`) |
| Enforcement | `NR-01`…`NR-18`; gate G1 editorial review of every derived communication against this file |
| Improvement loop | Objections captured in `CM-011` that the narrative did not anticipate are added at the next wave boundary |

---

## 7. Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **`O-01`** | **`06-05_Change_Management_and_Training_Plan.md` does not exist.** `FOLDER_STRUCTURE.md` line 62 lists `06-03`…`06-06` as planned. This entire category is content for a plan that has not been written, so the narrative has no owning specification to sit inside and no approved change approach to reference. This is the `DM` category's `06-03` defect (`AUDIT-011` DM-01) repeating in `CM` | CTO with Programme Director | **W0 — before the first town hall** |
| **`O-02`** | **The charter being narrated is itself unapproved.** `00-02` is `DRAFT FOR APPROVAL` and decisions `D-01`, `D-13` and `D-14` are open. A narrative that states the programme's scope and budget as settled would be inaccurate; §4.1 avoids both, but the first town hall cannot honestly answer *"is this approved?"* | CEO with the Board | **W0** |
| **`O-03`** | **The `G4-10` claim has no denominator.** *"v1.0 scope complete"* at Month 18 is the programme's most protected claim and rests on a requirement baseline with three current values (`AUDIT-014` TS-01, `AF-06`). `NR-09` suspends the claim; the suspension is a mitigation, not a fix | Enterprise Architecture with CTO | **W4 minus 6 months** |
| **`O-04`** | **The Bengali counterpart does not exist.** `bilingual: yes`; 275–635 field and branch staff are the audience whose adoption decides `RSK-008`, and `NR-16` blocks release. `BN-018` in-context sign-off applies | Localisation Lead | **W0 — with the English** |
| **`O-05`** | **No named Change Lead has been appointed.** `06-01` §4 budgets 0.5 FTE of a *"Change & Training Lead"* at W1, and this file is `W0`. The owner column of this file, and of eleven others in the category, currently names a role nobody holds | CEO with HR Director | **W0** |
| **`O-06`** | **The A1 technician translation has not been tested with technicians** (`NR-07`). The field pilot with senior technicians that `RSK-008` mitigates through is a W2 activity; the narrative is needed at W0 | Change Lead with Operations Director | **W0 — a sample of six is sufficient** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; §7 Open Items added per category convention
- [x] Category-standard audience · channel · timing · message · call-to-action table present (`CG-009` §3)
- [x] Six-sentence short form fixed as the governing form
- [x] Current state stated from measured BRD baselines, not characterised
- [x] **What does not change published with equal prominence to what does**
- [x] Eleven audience translations, none using programme vocabulary
- [x] **Claim schedule bound to gate criteria with the permitted wording for each**
- [x] Eight prohibited claims stated, each with the sanctioned alternative
- [x] Vocabulary table aligned to `CG-003` and `CG-004`
- [x] Failure modes named with early signals
- [x] Eighteen governing rules with enforcement classes
- [x] All internal links resolve
- [ ] **`O-01` `06-05` does not exist — the category has no owning specification**
- [ ] **`O-02` the charter being narrated is unapproved**
- [ ] **`O-03` the `G4-10` claim has no agreed denominator**
- [ ] **`O-04` Bengali counterpart not written; `NR-16` blocks release**
- [ ] **`O-05` no Change Lead appointed**
- [ ] Named approver recorded — **pending Content Design Lead with CEO endorsement**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
