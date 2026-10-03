---
id: CM-008
title: Champion and Super User Network Kit
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-20
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Change Lead
author: Change Lead with L&D and Branch Operations
reviewers: [Operations Director, HR Director, Branch Operations Lead, L&D Lead, Support Lead, Localisation Lead, Content Design Lead, Programme Content Lead, Quality Manager]
approver: Content Design Lead
content_class: D
purpose: >
  Defines the champion and super-user network as a change mechanism — what a champion is and is
  not, how they are selected, what they are told and when, what they may and may not do, how they
  escalate, how the network is recognised, and how it is measured — and fixes the boundary with
  TR-023, which trains the same people for a different purpose. 51-plus branches cannot be
  supported centrally; the champion network is the delivery mechanism for adoption, and it is the
  route CM-007 depends on in the first 48 hours of every go-live.
traces_to: [TR-023, TR-002, TR-022, CM-001, CM-002, CM-005, CM-007, CM-010, CM-011, CM-012, CM-017, OP-001, 06-01, SP-005, 05-04, MD-009]
priority: P2
wave: W1
bilingual: yes
bn_counterpart: CM-008_Champion_and_Super_User_Network_Kit_BN.md
sources:
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-01 §4 business-side commitment — branch champions, one per branch, 4 hours per week during rollout, W1–W5; super-users 2–3 per module at 30% during UAT
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-01 §7 — champion network, one trained champion per branch, monthly champion forum
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-01 §6 — T−2 weeks branch champion training (train the trainer) in the per-location rollout pattern
    verified: 2026-08-20
    class: P1
  - source: primary-doc/1000FiX_ERP_System_Comprehensive_BRD.md §21.5 — train-the-trainer, one trained champion per branch, monthly champion forum
    verified: 2026-08-20
    class: P1
  - source: project_content/08_Training_and_Enablement/08B_Course_Packs/TR-023 §Open Items O-01 — the CM-008 boundary recorded as undefined and raised as audit finding TR-08
    verified: 2026-08-20
    class: P1
  - source: project_content/08_Training_and_Enablement/08B_Course_Packs/TR-023 §4 facilitator guide — champions chosen for credibility and availability, not for being the fastest user
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04 §1 — the roles champions are drawn from, with headcounts
    verified: 2026-08-20
    class: P1
supersedes: none
review_due: 2027-02-20
---

# CM-008 — Champion and Super User Network Kit

> **Boundary note — this file closes `TR-023` `O-01` and audit finding `TR-08`.**
> `TR-023` recorded that *"`CM-008` and this file describe the same network from two categories.
> The boundary is not defined in either register row and the risk is two competing champion
> programmes."* §4.2 defines the boundary. **`TR-023` owns the champion's capability; this file
> owns the champion's role in the change.** Neither owns both.
>
> **Scope note.** Champions and super-users are two populations with different jobs. §4.1
> separates them. Where this file says "champion" it means the branch-based change role, not the
> module super-user.

---

## 1. Purpose

The register's justification is exact: *"51+ branches cannot be supported centrally; the champion
network is the delivery mechanism for adoption."*

Every other file in this category assumes the network. `CM-005` K4 prints a champion's name on a
card at every site. `CM-007` `HY-02` makes the champion route 2 — the only support route with the
capacity to answer 500+ people at once in week one. `CM-010` cascades through them. If the network
does not exist, four files in this category describe a mechanism that is not there.

**Consequence of absence (`CP-03`).**

| Failure | Consequence |
|---|---|
| No champion at a site | That site's staff have route 4 and paper, and choose paper |
| Champion selected for speed rather than credibility | Colleagues do not ask them, and the role produces nothing |
| No definition of what a champion may not do | Access is granted informally, controls are worked around, and the audit trail is broken by the people trying to help |
| No briefing sequence | The champion learns about a change from the staff asking about it |
| No escalation route | Site problems accumulate locally and surface at the gate |
| Boundary with `TR-023` undefined | Two programmes, two briefings, two sets of expectations on the same 51 people |
| No time allocation | The role decays within two waves — `TR-023` `O-02` |
| No recognition | Voluntary effort with no acknowledgement stops being voluntary |

---

## 2. Scope

**In scope:** the champion and super-user definitions and their separation; the `TR-023` boundary;
selection criteria and the selection process; the briefing sequence and cadence; the champion's
authority and its limits; the escalation route; the monthly forum; recognition; network health
measurement; succession; and rules `NW-01`…`NW-18`.

**Out of scope:**

| Subject | Owned by |
|---|---|
| **Champion training, assessment and certification to deliver** | [`../08_Training_and_Enablement/08B_Course_Packs/TR-023_Train_the_Trainer_and_Super_User_Kit.md`](../08_Training_and_Enablement/08B_Course_Packs/TR-023_Train_the_Trainer_and_Super_User_Kit.md) |
| Role curricula and prerequisites | `TR-002` |
| Job aids the champion hands out | `TR-022` |
| The talking points a champion uses at a launch | [`CM-005_Wave_Launch_Communication_Kit.md`](CM-005_Wave_Launch_Communication_Kit.md) K6 |
| Objection responses | [`CM-011_Resistance_Objection_and_FAQ_Handling_Pack.md`](CM-011_Resistance_Objection_and_FAQ_Handling_Pack.md) |
| Recognition copy and its wording | [`CM-017_Recognition_Incentive_and_Gamification_Copy.md`](CM-017_Recognition_Incentive_and_Gamification_Copy.md) |
| Support tiers and the service desk | [`OP-001`](../17_Operations_Support_and_Runbooks/OP-001_Support_Model_Tiering_and_Routing_Content.md) |
| The role register and job titles | `05-04` §1 · `MD-009` — **`NW-02` prohibits creating a job title here** |
| Incentive schemes and their monetary value | HR; `M57` |

---

## 3. Audience

| Audience | Uses this file to… |
|---|---|
| **Change Lead** | Build and run the network |
| **Branch managers (`S05`)** | Select and release a champion, knowing what they are agreeing to |
| **Champions (`S06`)** | Know what the role is, and — as importantly — what it is not |
| **L&D** | Align `TR-023` delivery to a role definition it did not have to invent |
| **Support Lead** | Rely on route 2 with a defined authority limit |
| **HR Director** | Understand the time commitment being asked for, and recognise it |
| **Operations Director** | Hold branch managers to releasing their champion |

---

## 4. Content

### 4.1 Two populations, two jobs

**`NW-01`: champions and super-users are different people doing different work, and conflating
them produces a network that is accountable for neither.**

| | **Branch champion** | **Module super-user** |
|---|---|---|
| Population | **51+** — one per branch (`06-01` §7) | **40–60** — 2–3 per module (`06-01` §4) |
| Drawn from | `R08`, `R09`, `R10`, `R18`, `R27`, `R34` — the people colleagues already ask | The module's most experienced practitioner |
| Belongs to | A **site** | A **module** |
| Time commitment | **4 hours/week during rollout, W1–W5** (`06-01` §4) | **30% during UAT, 10% otherwise** (`06-01` §4) |
| Primary job | **Local adoption** — answer, demonstrate, reassure, escalate | **Acceptance** — test, decide whether a requirement is met, sign the UAT record |
| Decision right | Local training sequencing; cutover timing at their site | **Requirement acceptance at UAT** (`00-04` §5.2) |
| Risk if absent | `RSK-008`, `RSK-009` adoption failure | **`RSK-001`** — the highest-rated risk in the programme |
| Owned by | Change Lead (this file) | Module business owner; PMO |
| Trained by | `TR-023` | `TR-023` |

> **`NW-02` — neither is a job title.** Champion and super-user are **assignments** carried by
> people whose registered role is in `05-04` and `MD-009`. Creating them as roles would require a
> `MD-009` change and an access profile, and would make an adoption mechanism into an
> establishment question.

### 4.2 The `TR-023` boundary — closing `TR-08`

**`NW-03`: one network, two owners, one boundary.** Stated as a table so it cannot be read two
ways.

| Subject | Owned by `TR-023` (Category 08) | Owned by `CM-008` (this file) |
|---|:--:|:--:|
| Who may be a champion — capability prerequisites | **●** — must pass their own role pack first (`PK-13`) | ○ contributes the credibility criterion |
| **Selection process at a site** | ○ | **●** |
| Training curriculum, exercises, assessment | **●** | ○ |
| Certification to deliver training | **●** | ○ |
| **The change role definition and its limits** | ○ | **●** |
| **Briefing sequence and cadence** | ○ | **●** |
| Facilitation skills and trainer requirements | **●** | ○ |
| **The monthly champion forum** | ○ | **●** |
| Job aids the champion delivers | **●** (`TR-022`) | ○ |
| **Escalation of site issues** | ○ | **●** |
| **Recognition and network health** | ○ | **●** |
| Backfill and time allocation | ○ shares the finding | **●** raises it as `O-01` |

> **`NW-04` — a champion is briefed twice and trained once.** They attend `TR-023` once, at
> `T−2 weeks` before their site's first wave (`06-01` §6). They are **briefed** by this file's
> cadence every month for the duration of the programme. Confusing the two is what produced
> `TR-08`.

### 4.3 Selection

**`NW-05`: champions are selected for credibility and availability, not for competence with
software.** `TR-023` §4 states it in the facilitator guide; this file makes it the selection rule.

| Criterion | Test | Why |
|---|---|---|
| **Credibility** | *"Who do people at this site already ask when something goes wrong?"* | An appointed champion nobody asks is an empty chair |
| **Availability** | The branch manager confirms **4 hours/week is released**, in writing | Without release, the role is unpaid overtime and decays |
| **Language** | Speaks the site's working language | 51+ sites; most are Bengali-first |
| **Attitude to the change** | **A sceptic who engages is preferable to an enthusiast who does not listen** | `00-04` RSK-009 mitigation: *"involve resistors in design and UAT"* |
| Tenure | Long enough to know the site's real workarounds | The workarounds are what the system must replace |
| Not | The branch manager | The champion must be someone staff can admit confusion to |

**Process.** `NW-06`: selection is proposed by the branch manager, confirmed by the Change Lead,
and **published at the site**. A champion whose name is not on the K4 card is not a champion.

| Step | Owner | When |
|:--:|---|---|
| 1. Nomination | Branch manager | **W1 minus 8 weeks** for pilot sites; T−8 weeks per site thereafter |
| 2. Availability confirmation in writing | Branch manager with Operations Director | T−7 weeks |
| 3. Confirmation | Change Lead | T−6 weeks |
| 4. Training (`TR-023`) | L&D | **T−2 weeks** |
| 5. Publication at site (K4 card, notice) | Change Lead with Operations | T−1 week |
| 6. **Deputy named** | Branch manager | T−1 week |

> **`NW-07` — every site names a deputy.** One person per site, in a network of 51+, across five
> waves and thirty-six months, guarantees absence at go-live somewhere. A site with no deputy has
> no route 2 the day its champion is on leave.

### 4.4 What a champion does — and does not

| **Does** | **Does not** |
|---|---|
| Answer "how do I…" questions on the floor | Grant, extend or share system access |
| Demonstrate a task rather than describe it | Override a control, an approval or a validation |
| Hand out the job aid (`TR-022`) | Change a configuration or a master-data value |
| Log an issue on a colleague's behalf | Promise a fix or a date |
| Feed the top-ten questions back for `CM-005` K6 | Comment on pay, grading, headcount or appraisal |
| Escalate what they cannot answer, same day | Speak for the programme to customers or partners |
| Say honestly *"I don't know — I'll find out and come back today"* | Invent an answer to protect their standing |
| Cascade the wave brief within five working days | Substitute for training a colleague has not attended |

> **`NW-08` — "does not grant access" is the load-bearing prohibition.** The most common way a
> well-intentioned champion breaks a control environment is by logging in for a colleague. It
> destroys the audit trail (`G1-07`), breaches segregation of duties, and is invisible until an
> audit. It is stated in the briefing, in `TR-023`, and on the champion's own card.

### 4.5 The briefing sequence

**`NW-09`: the champion hears everything first.** Order, not volume, is what makes the network
work.

| # | Item | When | From | Owning content |
|:--:|---|---|---|---|
| 1 | Role briefing — this file §4.4 | On confirmation | Change Lead | This file |
| 2 | Programme narrative | On confirmation | Change Lead | `CM-001` |
| 3 | `TR-023` training | T−2 weeks | L&D | `TR-023` |
| 4 | **Wave talking points K6** | **T−3 weeks, before managers** | Change Lead | `CM-005` `WL-02` |
| 5 | Objection index for the wave | T−3 weeks | Change Lead | `CM-011` |
| 6 | Site readiness position | T−4 weeks onward | Branch manager | `CM-012` |
| 7 | Cutover instruction and freeze instant | T−7 days | Data Migration | `DM-014` |
| 8 | Hypercare routes and known-issue list | T−0, then daily in week 1 | Support Lead | `CM-007` |
| **Standing** | **Monthly champion forum** | Monthly, whole programme | Change Lead | §4.6 |

### 4.6 The monthly champion forum

Required by `06-01` §7 and BRD §21.5. This file specifies it.

| Element | Rule |
|---|---|
| Frequency | **Monthly, for the duration of the programme** — not only during a site's own wave |
| Duration | 60 minutes |
| Format | Remote, with a Bengali-language track. Recorded and available to those on shift |
| **Agenda, fixed** | 1. What changed this month · 2. What is coming, per wave · 3. **Questions from the floor — the largest item** · 4. What we heard last month and what happened about it · 5. Recognition |
| **Item 4 is mandatory** | A forum that collects issues and never reports back stops receiving them within three sessions |
| Attendance | Recorded. Two consecutive absences trigger a conversation with the branch manager, not with the champion |
| Output | The top-ten question list feeding `CM-005` `V6`; the resistance log feeding `CM-002` §4.7 |
| Language | **Bengali track is not optional** (`SK-08`) |

### 4.7 Escalation from the network

| Situation | Route | Commitment |
|---|---|---|
| Question the champion cannot answer | Change Lead inbox, single route | **Answered within 1 working day**, or an interim with a date |
| Issue affecting the site's ability to work | Branch manager → Support Lead | Same day |
| Repeated issue at multiple sites | Champion forum → Support Lead → known-issue list | Same day (`HY-06`) |
| Objection the champion cannot answer honestly | Change Lead → `CM-011`; classified per `SK-15` | Next forum |
| **A champion being asked to do something in §4.4's right-hand column** | Branch manager and Change Lead | **Immediately** — this is a control matter |
| Champion unable to hold the role | Branch manager, deputy activated | Within 5 working days |

> **`NW-10` — the one-working-day answer commitment is what the network runs on.** A champion who
> asks and receives nothing has to invent an answer or lose standing; both outcomes cost more than
> the answer would have.

### 4.8 Recognition

`NW-11`: recognition is **specific, public and non-monetary by default.** The monetary question
belongs to HR and `M57`, not to the change programme.

| Form | Rule |
|---|---|
| Named thanks at the forum | Every month, specific — what they did, not that they helped |
| Named in the wave exit notice at their site | `CM-007` §4.8 |
| Champion listed on the site notice | Standing, visible to colleagues and customers |
| Certificate on completing `TR-023` and a wave | Issued by L&D, recorded in `M22` |
| Reference in the appraisal | **Requires HR agreement** — the assignment must count for something in the system that decides progression, or it will not be sustained |
| **Not** | A leaderboard ranking champions against each other (`CM-017` `RN-08` — ranking individuals by adoption metrics is a monitoring boundary) |

### 4.9 Network health

**`NW-12`: the network is measured, and the measures are about the network, not about the
champions.**

| Measure | Definition | Threshold | Response |
|---|---|---|:--|
| **Coverage** | Sites with a confirmed, published champion **and deputy** | **100%** | A site below is not ready for cutover (`CM-012`) |
| Forum attendance | Champions attending, of confirmed | > 80% | Below: the time release is not real |
| Question flow | Questions logged per champion per month | **> 0** | Zero is under-use or disengagement, not success |
| Answer latency | Time from question to answer | ≤ 1 working day | Above: `NW-10` breached |
| Route 2 share | Site issues resolved by champion vs escalated | Rising over the wave | Falling: briefing inadequate |
| Turnover | Champions replaced per wave | < 15% | Above: the role is unsustainable as defined |
| **Bengali track attendance** | Share of forum attendance on the Bengali track | Tracked | A collapsing Bengali track means the network is drifting to head office |

### 4.10 Audience · channel · timing · message · call-to-action

| Audience | Channel | Timing | Message | Call to action |
|---|---|---|---|---|
| Branch managers | Direct, written | **T−8 weeks per site** | What a champion is; the 4 h/week release being asked for | **Nominate, and confirm the release in writing** |
| Nominated champions | Role briefing, 1:1 | On confirmation | §4.4 does and does not; §4.7 escalation | Accept, or decline without penalty |
| Champions | `TR-023` course | T−2 weeks | Capability | Pass the assessment |
| Champions | Talking points pack | **T−3 weeks, before managers** | `CM-005` K6, `CM-011` index | Cascade after the manager brief |
| Champions | **Monthly forum, Bengali track** | Monthly, whole programme | Fixed five-item agenda | Bring your site's questions |
| All site staff | Site notice + K4 card | T−1 week | **Who your champion and deputy are** | Ask them first |
| Champions | Forum item 4 | Monthly | What happened to last month's issues | Keep raising |
| HR | Direct | W1 | The appraisal-recognition request | Agree or decline explicitly |

### 4.11 Governing rules

| # | Rule | Class |
|---|---|:--:|
| `NW-01` | Champions and super-users are distinct populations with distinct accountabilities | **H** |
| `NW-02` | Neither is a job title; both are assignments on `05-04` roles | **H** |
| `NW-03` | The `TR-023` boundary table governs; `TR-023` owns capability, this file owns the change role | **H** |
| `NW-04` | A champion is trained once and briefed monthly | **H** |
| `NW-05` | Selection is on credibility and confirmed availability, not software competence | **H** |
| `NW-06` | A champion whose name is not published at their site is not a champion | **H** |
| `NW-07` | Every site names a deputy | **H** |
| `NW-08` | A champion never grants, extends or shares access | **H** |
| `NW-09` | Champions are briefed before managers, and managers before staff | **H** |
| `NW-10` | A champion's question is answered within one working day, or acknowledged with a date | **H** |
| `NW-11` | Recognition is specific, public and non-monetary by default; monetary recognition is HR's | **H** |
| `NW-12` | Network health is measured on the network, never as a ranking of individuals | **H** |
| `NW-13` | The monthly forum runs for the whole programme, not only during a site's own wave | **H** |
| `NW-14` | Forum agenda item 4 — what happened to last month's issues — is mandatory | **H** |
| `NW-15` | The forum has a Bengali track and it is not optional | **H** |
| `NW-16` | 100% site coverage with a champion and deputy is a cutover pre-condition (`CM-012`) | **H** |
| `NW-17` | Two consecutive absences are addressed with the branch manager, not the champion | **S** |
| `NW-18` | Any request that a champion act outside §4.4 is escalated immediately as a control matter | **H** |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| [`../08_Training_and_Enablement/08B_Course_Packs/TR-023_Train_the_Trainer_and_Super_User_Kit.md`](../08_Training_and_Enablement/08B_Course_Packs/TR-023_Train_the_Trainer_and_Super_User_Kit.md) | Capability, assessment, certification — the other half of the boundary |
| `06-01` §4, §6, §7 | The commitment, the T−2 weeks training slot, the monthly forum |
| [`CM-005_Wave_Launch_Communication_Kit.md`](CM-005_Wave_Launch_Communication_Kit.md) | K4 publishes the name; K6 supplies the talking points |
| [`CM-007_Hypercare_Communication_Pack.md`](CM-007_Hypercare_Communication_Pack.md) | Route 2 is this network |
| [`CM-011_Resistance_Objection_and_FAQ_Handling_Pack.md`](CM-011_Resistance_Objection_and_FAQ_Handling_Pack.md) | The objection index and the honest-answer script |
| [`CM-012_Branch_Readiness_Communication_Checklist.md`](CM-012_Branch_Readiness_Communication_Checklist.md) | Champion coverage is a readiness line |
| [`CM-017_Recognition_Incentive_and_Gamification_Copy.md`](CM-017_Recognition_Incentive_and_Gamification_Copy.md) | Recognition wording and the monitoring boundary |
| `05-04` §1 · `MD-009` | The roles champions are drawn from |
| [`OP-001`](../17_Operations_Support_and_Runbooks/OP-001_Support_Model_Tiering_and_Routing_Content.md) | Where route 2 hands over to route 4, and the §4.7 commitment the champion quotes |

| Depended on by |
|---|
| `CM-005` K4 and K6 · `CM-007` route 2 · `CM-010` cascade · `CM-012` readiness · `CM-016` local adoption intervention · `TR-023` delivery model · every wave's floor coverage |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **Every wave boundary**, plus a network health report monthly |
| Trigger for out-of-cycle review | Coverage below 100% at a cutover · turnover above 15% · a `NW-08` breach · a change to `TR-023` |
| Owner | Change Lead; selection co-owned with branch managers and the Operations Director |
| Change log | `RF-006`; the `TR-023` boundary table is MAJOR and requires L&D agreement to change |
| Enforcement | `NW-01`…`NW-18`; `NW-16` blocks cutover; forum attendance and answer latency reported monthly |
| Improvement loop | **The question flow is the network's pulse.** Rising questions early in a wave is health; falling questions with rising route-4 contacts is disengagement, and the response is briefing, not exhortation |

---

## 7. Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **`O-01`** | **The champion commitment is unfunded and unbackfilled.** 51+ people at 4 hours/week for W1–W5, plus four days of `TR-023` training, from people already holding a full role. `TR-023` `O-02` records the same gap and calls it *"the central risk to the delivery model"*. `NW-05` requires the release in writing at nomination; no branch has been asked, and no backfill budget exists. **Four files in this category assume this network exists** | HR Director with Operations Director | **W1 minus 8 weeks** |
| **`O-02`** | **`TR-023` `O-03` sequencing is unresolved.** Champions must pass their own role pack before certification, and both role packs and `TR-023` are W1. The T−2 weeks slot in `06-01` §6 assumes the prerequisite is already met | L&D with Operations | **W1** |
| **`O-03`** | **The appraisal-recognition question has not been put to HR.** §4.8 states that the assignment must count in the system that decides progression or it will not be sustained over five waves. No request has been made and no decision recorded | Change Lead with HR Director | **W1** |
| **`O-04`** | **The Bengali counterpart does not exist**, and `NW-15` makes the Bengali forum track mandatory. A network of 51+ branch staff briefed only in English is a head-office network | Localisation Lead | **W1 minus 4 weeks** |
| **`O-05`** | **No champion has been nominated at any site.** The selection process in §4.3 starts at T−8 weeks and W1 pilot sites are six. Coverage is currently zero, against a `NW-16` cutover pre-condition of 100% | Change Lead with Branch Operations Lead | **W1 minus 8 weeks** |
| **`O-06`** | **The forum has no platform.** Monthly, 60 minutes, 51+ remote attendees, recorded, with a Bengali track, for 36 months. `M27` omnichannel is W4 and `M22` learning management is W5 | Change Lead with CTO | **W1** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; §7 Open Items added per category convention
- [x] Category-standard audience · channel · timing · message · call-to-action table present (`CG-009` §3)
- [x] **Champions and super-users separated** with distinct populations, commitments, decision rights and risks
- [x] **`TR-023` boundary defined as a twelve-row ownership table — closes `TR-023` `O-01` and audit finding `TR-08`**
- [x] Selection criteria led by credibility and written availability, with a six-step process and named deputy
- [x] Authority limits stated, with the access prohibition made load-bearing
- [x] Briefing sequence ordered champion → manager → staff
- [x] Monthly forum specified with a fixed agenda, a mandatory feedback item and a Bengali track
- [x] Escalation routes with a one-working-day answer commitment
- [x] Recognition specified as non-monetary by default, with the monitoring boundary stated
- [x] Seven network health measures defined on the network rather than on individuals
- [x] Eighteen governing rules with enforcement classes
- [x] All internal links resolve
- [ ] **`O-01` the network is unfunded and unbackfilled — four files in this category depend on it**
- [ ] **`O-03` appraisal recognition not agreed with HR**
- [ ] **`O-04` Bengali counterpart not written; the Bengali forum track is mandatory**
- [ ] **`O-05` zero champions nominated against a 100% cutover pre-condition**
- [ ] Named approver recorded — **pending Content Design Lead**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
