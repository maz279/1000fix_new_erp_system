---
id: CM-002
title: Stakeholder Map and Communication Plan
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-20
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Change Lead
author: Change Lead with the Programme Management Office
reviewers: [CEO, CTO, CCO, Operations Director, HR Director, Quality Manager, Marketing Manager, Account Management Lead, Procurement Manager, Localisation Lead, Programme Content Lead]
approver: Programme Content Lead
content_class: E
purpose: >
  Registers every internal and external stakeholder group the programme changes, with its
  population, influence, stated concern, decision rights, owning communicator, channel and
  minimum contact frequency — and derives the standing communication plan from that register
  rather than from the delivery schedule. Communication planned per wave rather than per
  stakeholder leaves whole groups surprised repeatedly, because a wave plan only reaches the
  people that wave touches and says nothing to the people it worries.
traces_to: [00-04, 00-04 §5, 05-04, 04-00, 06-01, CM-001, CM-003, CM-010, CM-011, CM-018, CG-002, RSK-001, RSK-008, RSK-009, RSK-010, RSK-011, RSK-012]
priority: P1
wave: W0
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04 §1 — the 38 registered roles with headcount ranges, R01…R38, across seven groupings
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/00_Governance_and_Charter/00-04 §5.1 governance structure and §5.3 forum cadence — Board quarterly, Steering monthly, PMO weekly, ARB and Business Owners Forum fortnightly
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/00_Governance_and_Charter/00-04 §1.2 RSK-008…RSK-012 — the five adoption and change risks with their owners
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/00_Governance_and_Charter/00-04 §1.1 RSK-001 — business super-user availability, rated Critical, owned by the CEO
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §2 — portal populations and volumes for the six external audiences
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-01 §4 business-side commitment — executive sponsor 4 h/month, module owners 20%, super-users 30% during UAT, branch champions 4 h/week W1–W5, data owners 20%
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-01 §7 — stakeholder map maintained and reviewed each wave, resistance actively tracked
    verified: 2026-08-20
    class: P1
supersedes: none
review_due: 2027-02-20
---

# CM-002 — Stakeholder Map and Communication Plan

> **Scope note.** This file owns **who, why, through what, and how often**. It does not own
> **when** — that is `CM-003`, which schedules against the delivery milestones — and it does not
> own **what is said**, which is `CM-001` for framing and `CM-005`…`CM-017` for delivered content.
> A stakeholder group that appears here and nowhere in `CM-003` is a planning defect, and `SK-16`
> makes it detectable.

---

## 1. Purpose

`06-01` §7 requires a stakeholder map *"maintained and reviewed each wave, with resistance
actively tracked"*. It does not supply one. This file is that map, and the standing communication
plan derived from it.

The register's justification is exact: *"Communication planned per wave rather than per stakeholder
leaves groups repeatedly surprised."*

**Consequence of absence (`CP-03`).**

| Failure | Consequence |
|---|---|
| Planning by wave only | Groups outside the current wave hear nothing for months and conclude the programme has stalled or is hiding something |
| No influence or concern recorded | Effort is spent evenly rather than where refusal would stop the programme |
| No named communicator per group | Communication defaults to the Change Lead, who does not have the relationships |
| No minimum frequency | Contact happens when there is news; silence is read as bad news |
| No resistance tracking | `RSK-008`…`RSK-012` are managed by anecdote |
| External groups omitted | 1,000–3,000 external party users and 250,000+ customers are changed by the programme and hear about it from the change itself |
| No decision-rights column | Groups are consulted on matters already decided, and not consulted on matters still open — the fastest route to disengagement |

---

## 2. Scope

**In scope:** the stakeholder register (internal and external); the influence-and-concern
assessment; decision rights per group; the owning communicator; channel selection; minimum
contact frequency; the standing forum plan; the resistance tracking method; the escalation route;
and rules `SK-01`…`SK-18`.

**Out of scope:**

| Subject | Owned by |
|---|---|
| The story told to each group | [`CM-001_Programme_Narrative_and_Change_Story.md`](CM-001_Programme_Narrative_and_Change_Story.md) §4.4 |
| The calendar and its milestone dependencies | [`CM-003_Communication_Calendar_by_Wave.md`](CM-003_Communication_Calendar_by_Wave.md) |
| The objections themselves and their answers | [`CM-011_Resistance_Objection_and_FAQ_Handling_Pack.md`](CM-011_Resistance_Objection_and_FAQ_Handling_Pack.md) |
| Per-role change impact | [`CM-018_Change_Impact_Statement_Template.md`](CM-018_Change_Impact_Statement_Template.md) |
| The role register itself | `05-04` §1 · `MD-009` — **`SK-02` prohibits inventing a role here** |
| Programme governance forums and their decision rights | `00-04` §5 — this file schedules communication *into* them, it does not constitute them |
| Content-function RACI | `CG-002` §5 |
| Customer marketing segmentation | `MD-021` segments; campaign use in [`CM-016_Adoption_Campaign_Content.md`](CM-016_Adoption_Campaign_Content.md) |
| Ecosystem onboarding journeys | Category 18 `EO` — [`EO-001`](../18_Ecosystem_Onboarding_Content/EO-001_Marketplace_Seller_Onboarding_Kit.md), [`EO-003`](../18_Ecosystem_Onboarding_Content/EO-003_Brand_Partner_Onboarding_Pack.md), [`EO-005`](../18_Ecosystem_Onboarding_Content/EO-005_Vendor_and_Supplier_Onboarding_Pack.md), [`EO-007`](../18_Ecosystem_Onboarding_Content/EO-007_Corporate_Client_Onboarding_and_Welcome_Kit.md), [`EO-009`](../18_Ecosystem_Onboarding_Content/EO-009_Referral_and_Alliance_Partner_Kit.md) |

---

## 3. Audience

| Audience | Uses this file to… |
|---|---|
| **Change Lead** | Run the plan; report coverage and resistance |
| **PMO** | Assure that every group has an owner and a frequency |
| **Steering Committee** | See which groups are under-communicated and which are resisting |
| **Branch managers** | Know what they owe their own staff, and when |
| **Account managers, Procurement, Marketplace Ops** | Know they own external-group communication, not Marketing |
| **HR Director** | Coordinate people-sensitive messages that must precede or follow programme messages |
| **Marketing Manager** | Know the boundary between programme communication and market communication |

---

## 4. Content

### 4.1 How groups are assessed

**`SK-01`: every group is scored on two axes and nothing else.** More axes produce a matrix nobody
maintains.

| Axis | Scale | What it decides |
|---|---|---|
| **Influence** | `H` / `M` / `L` — can this group stop, delay or materially degrade a wave? | Frequency and seniority of the communicator |
| **Impact felt** | `H` / `M` / `L` — how much does this group's daily work change? | Depth of content, and whether two-way channels are required |

| Influence \ Impact | **High impact** | Medium impact | Low impact |
|---|---|---|---|
| **High influence** | **Partner** — co-design, two-way, named executive owner | **Satisfy** — decision-focused, scheduled | **Satisfy** — brief, scheduled |
| Medium influence | **Support** — training-led, champion-mediated, two-way | Support | Inform |
| Low influence | **Support** — heavy support, floor presence | Inform | Inform |

> **`SK-03` — high impact with low influence is the most dangerous cell, not the safest.** Field
> technicians sit there. They cannot stop the programme in a committee; they stop it by not using
> the app, which `00-04` §8 identifies as the second of five ways this programme fails.

### 4.2 Internal stakeholder register

Populations are from `05-04` §1; commitments from `06-01` §4.

| # | Group | Roles | Population | Infl | Impact | Treatment | Stated concern | Owning communicator | Channel | Min. frequency |
|:--:|---|---|---|:--:|:--:|---|---|---|---|---|
| **S01** | Board | — | 5–9 | **H** | L | Satisfy | Investment, benefit realisation, the restated TCO (`D-14`) | CEO | Board pack (`CM-004` extract) | Quarterly |
| **S02** | ERP Steering Committee | `R01`–`R05`, `R30`, `R32` | 7 | **H** | M | **Partner** | Gate decisions, scope control, risk | Programme Director | Steering pack (`CM-004`) | **Monthly** |
| **S03** | Business Owners Forum | 17 module owners | 17 | **H** | **H** | **Partner** | Requirement decisions, UAT scheduling, adoption | PMO | Forum, fortnightly | **Fortnightly** |
| **S04** | Super-users | 2–3 per module | 40–60 | **H** | **H** | **Partner** | Time protection — this is `RSK-001`, rated **Critical** | Module business owner | Direct, plus UAT sessions | **Weekly in their wave** |
| **S05** | Branch managers | `R06` | 51+ | **H** | **H** | **Partner** | Being measured on a dashboard they did not design | Operations Director | Manager briefing + branch console demo | **Monthly**, weekly in their wave |
| **S06** | Champions | drawn from `R08`–`R10`, `R18`, `R27`, `R34` | 51+ | M | **H** | **Partner** | Four hours a week on top of a full role, unbackfilled | Change Lead | **Champion forum, monthly** (`06-01` §7) | **Monthly** |
| **S07** | Field technicians | `R10`–`R12` | 200–400 | L | **H** | **Support** | Monitoring, earnings, device cost, being timed | Operations Director via supervisors | **Bengali video, toolbox talk, in-app** | **Fortnightly in W2**, monthly otherwise |
| **S08** | Branch counter staff | `R08` | 150–250 | L | **H** | **Support** | Queue pressure while learning; intake speed | Branch manager | Branch huddle + champion | **Weekly in their wave** |
| **S09** | Workshop and store staff | `R09`, `R18`, `R20` | 86–121 | L | **H** | Support | Count accountability; bench discipline | Branch manager | Huddle + job aid | Weekly in their wave |
| **S10** | Logistics and riders | `R15`, `R16` | 60–175 | L | **H** | Support | POD capture time; cash reconciliation | Logistics Coordinator | App notice + toolbox talk | Fortnightly in W3 |
| **S11** | Finance and cashiers | `R26`–`R29` | 63–85 | **H** | **H** | **Partner** | Control tightening; close deadline; parallel-run workload | CFO | Finance forum | **Fortnightly in W3** |
| **S12** | HR and payroll | `R30`, `R31` | 4–8 | M | **H** | Support | Payroll accuracy; two parallel cycles | HR Director | Direct | Fortnightly in W5 |
| **S13** | Contact centre | `R34`, `R35` | 34–70 | M | **H** | Support | Handling time during transition; hotline volume at go-live | Contact Centre Supervisor | Team brief + console training | **Weekly in W4** |
| **S14** | Quality and audit | `R32` | 2–4 | M | M | Satisfy | ISO 9001 evidence continuity through change | Quality Manager | QMS review | Monthly |
| **S15** | IT administration | `R33` | 4–8 | M | **H** | Support | Access provisioning volume; JML load | CTO | Direct | Weekly in each wave |
| **S16** | Commercial and account management | `R21`–`R25` | 22–55 | M | M | Support | Client-facing credibility during transition | CCO | Commercial meeting | Monthly |
| **S17** | Wider workforce not otherwise listed | — | remainder of 500–900 | L | L | **Inform** | *"Does this affect me, and when?"* | Change Lead | **`CM-009` newsletter** | **Monthly, without exception** |

> **`SK-04` — S17 exists because "everyone else" is a stakeholder group.** It is the group that
> generates rumour, and the only group whose communication requirement is unconditional: a monthly
> item goes out whether or not there is news, because a skipped month is itself a message.

### 4.3 External stakeholder register

| # | Group | Population | Infl | Impact | Treatment | Stated concern | Owning communicator | Channel | Min. frequency |
|:--:|---|---|:--:|:--:|---|---|---|---|---|
| **S18** | Individual customers | 250,000+/month | L | M | Inform | *"Will my job be lost in the change? Is my old reference still valid?"* | Marketing with Contact Centre | Portal, SMS, hotline, in-app | **At W2 transition, then per change** (`CM-013`) |
| **S19** | Corporate and government clients | 500–2,000 users, 10+ contracted | **H** | **H** | **Partner** | Contractual SLA continuity; invoice format change | Account Manager (`R22`) | **1:1, account-manager-led** | **Per account, before W4** (`CM-014`) |
| **S20** | Brand partners | 17+ | **H** | **H** | **Partner** | Claim format change; reconciliation continuity | Warranty + Commercial | Partner meeting + `P08` bulletin | **Per brand, before W4** (`EO-003`) |
| **S21** | Vendors and suppliers | 200–500 | M | **H** | Support | PO and invoice route change; payment timing | Procurement Officer (`R19`) | Vendor letter + `P05` onboarding | **Per vendor, before W3** (`CM-015`) |
| **S22** | Marketplace sellers | 500–2,000 | M | **H** | Support | Commission, payout speed, scoring transparency — `RSK-010` | Marketplace Ops (`R24`) | `P07` + seller comms | **Per cohort, W7** (`CM-015`) |
| **S23** | Courier and logistics partners | 10–40 firms | M | M | Support | Manifest and POD integration | Logistics Coordinator | Partner briefing | Before W3 |
| **S24** | Referral and alliance partners | 100–500 | L | M | Inform | Attribution and commission accuracy | Partnerships | `P12` | W7 |
| **S25** | Recycling and disposal partners | 3–10 | L | M | Inform | Certificate submission route | Quality Manager | Direct | W8 |
| **S26** | Regulators and external auditors | NBR, NDMA, ISO certification body | **H** | L | Satisfy | Continuity of statutory records through migration | CFO / Quality Manager | Formal correspondence | **On statutory trigger only** |
| **S27** | Implementation vendor and contractors | 7–19 FTE | M | M | Support | Requirement stability; UAT availability | Programme Manager | Sprint ceremonies | Fortnightly |

> **`SK-05` — S26 is communicated to on trigger, never on cadence.** Volunteering programme
> narrative to a regulator creates a record the programme must then live inside. Statutory
> communication is drafted by Legal or Finance and is out of this file's scope by design.

### 4.4 Decision rights — what each group may actually decide

**`SK-06`: a group is consulted only on what it can decide or materially shape.** Consulting a
group on a settled matter is the fastest way to lose it.

| Group | May decide | Is consulted on | Is informed of |
|---|---|---|---|
| Board (`S01`) | Investment, continuation | The restated TCO | Progress, benefits |
| Steering (`S02`) | Wave Go/No-Go; `P0`/`P1` scope change; Critical risk acceptance | Sequencing, descope options | Everything |
| Business owners (`S03`) | Requirement acceptance at UAT | Design, sequencing within their module | Cross-module decisions |
| Super-users (`S04`) | Whether a requirement is accepted in practice | Screen design, workflow order | Wave scope |
| Branch managers (`S05`) | Local readiness confirmation (`CM-012`) | KPI design for branch dashboards | Wave dates |
| Champions (`S06`) | Local training sequencing | Job-aid content, cutover timing at their site | Everything staff receive |
| Technicians (`S07`) | Nothing formally — **and this is the risk in `SK-03`** | **App design, through the field pilot** | Their wave, their training, their support route |
| Customers (`S18`) | Nothing | Nothing | Change, before it reaches them |
| Corporate clients (`S19`) | Their own portal configuration and approval chains | Transition timing | Format changes |
| Brand partners (`S20`) | Their own claim rules and rate cards | Claim format, evidence standard | Portal timing |

> **`SK-07` — the technician row is a designed exposure.** Technicians hold no formal decision
> right and carry the highest impact. The field pilot in `RSK-008`'s mitigation is the *only*
> mechanism that gives them influence, which makes it a communication obligation, not an
> engineering nicety. Recorded as `O-03`.

### 4.5 Channel rules

| # | Rule |
|---|---|
| **`SK-08`** | **Every channel reaching S07–S10 is Bengali-first.** English-only communication to field, branch, workshop, store or rider audiences does not count as having communicated (`CG-010` §3.3) |
| **`SK-09`** | Email is not a channel for S07–S10. Branch and field staff are reached through their manager, their champion, a toolbox talk, an in-app notice or an SMS |
| **`SK-10`** | Any message with a call to action names **one** action and **one** contact |
| **`SK-11`** | WhatsApp is used for **notification only**, never as the system of record for an instruction. The programme is removing WhatsApp-based dispatch (`BRD §6.2` item 3); it may not simultaneously institutionalise it |
| **`SK-12`** | Every external group is communicated to by the person who already owns the relationship — account manager, procurement officer, warranty officer — never by the programme directly |
| **`SK-13`** | Two-way channels are mandatory for every `Partner` and `Support` group; broadcast-only is permitted for `Inform` |
| **`SK-14`** | Every communication records **what was sent, to whom, by whom, in which language, and on what date**, in the communication log (§4.7) |

### 4.6 Audience · channel · timing · message · call-to-action

The category-standard table (`CG-009` §3), at the level this file owns: **the standing plan**.
Wave-specific instances are in `CM-003`.

| Audience | Channel | Timing | Message type | Call to action |
|---|---|---|---|---|
| `S02` Steering | Steering pack | Monthly | Status, decisions required, risk, benefits | Take the listed decisions |
| `S03` Business owners | Forum | Fortnightly | Requirement and UAT decisions | Confirm acceptance or raise |
| `S04` Super-users | Direct + UAT | Weekly in wave | Session scheduling, script readiness | Attend; sign the UAT record |
| `S05` Branch managers | Manager briefing | Monthly / weekly in wave | Wave position, readiness | Confirm branch readiness (`CM-012`) |
| `S06` Champions | Champion forum | **Monthly** | Everything, first | Cascade within five working days |
| `S07` Technicians | Bengali video, toolbox talk, in-app | Fortnightly in W2 | What changes on the phone | Attend training; join the pilot |
| `S08`–`S10` Branch, workshop, rider | Huddle + job aid | Weekly in wave | Task-level change | Complete training before access |
| `S11` Finance | Finance forum | Fortnightly in W3 | Close, controls, parallel run | Staff the parallel close |
| `S17` Wider workforce | `CM-009` newsletter | **Monthly, unconditional** | Programme position | None — awareness only |
| `S18` Customers | Portal, SMS, hotline | At change | Transition, reference continuity | Register on the portal |
| `S19` Corporate | Account manager 1:1 | Per account, pre-W4 | Transition, invoice format | Book the setup session |
| `S20`–`S22` Partners, vendors, sellers | Relationship owner + portal | Per counterparty, pre-wave | Route change, timelines | Complete portal registration |

### 4.7 Resistance tracking

`06-01` §7 requires resistance to be *"actively tracked"*. The mechanism:

| Element | Definition |
|---|---|
| **Source** | Champion forum notes · branch huddle escalations · UAT session observations · support ticket themes (`OP-003`) · adoption telemetry (`CM-016`) |
| **Unit** | One **objection instance**, attributed to a group (`S01`–`S27`), not to an individual |
| **Classification** | `Capability` (cannot) · `Clarity` (does not understand) · `Belief` (does not accept the reason) · `Interest` (understands and is worse off) |
| **Rule `SK-15`** | **`Interest` objections are escalated to the Steering Committee, not answered by communication.** A person who is genuinely worse off is not persuaded by a better message |
| **Owner** | Change Lead, reported monthly to `S02` |
| **Link** | Every recurring objection becomes an entry in `CM-011`; every unanswerable one becomes a risk in `RF-011` |

> **`SK-16` — a group with no logged objection for two consecutive waves is under-communicated,
> not content.** Silence from a `Support` group is investigated as a coverage failure.

### 4.8 Escalation

| Situation | Escalates to | Within |
|---|---|---|
| A group has missed its minimum frequency twice | PMO | The next weekly report |
| A branch has not confirmed readiness (`CM-012`) | Operations Director | 48 hours of the confirmation deadline |
| An `Interest` objection from a `Partner` group | **Steering Committee** | The next monthly meeting |
| Super-user availability shortfall | **CEO** — this is `RSK-001`, rated Critical, and the CEO is its named owner | Immediately |
| An external counterparty escalates commercially | Relationship owner, then CCO | 5 working days |
| Any communication that breached `NR-10` prohibited claims | Change Lead + Content Design | Same day; correction issued within 2 working days |

### 4.9 Governing rules

| # | Rule | Class |
|---|---|:--:|
| `SK-01` | Groups are assessed on influence and impact only | **H** |
| `SK-02` | No role or group is invented here; `05-04` and `MD-009` govern | **H** |
| `SK-03` | High-impact / low-influence groups receive the heaviest support, not the lightest | **H** |
| `SK-04` | The wider workforce receives a monthly item unconditionally | **H** |
| `SK-05` | Regulators are communicated to on statutory trigger only, by Legal or Finance | **H** |
| `SK-06` | A group is consulted only on what it can decide or shape | **H** |
| `SK-07` | Technician influence is exercised through the field pilot; the pilot is a communication obligation | **H** |
| `SK-08` | Every channel reaching field, branch, workshop, store or rider audiences is Bengali-first | **H** |
| `SK-09` | Email does not reach S07–S10 and does not count as communication to them | **H** |
| `SK-10` | One action, one contact, per message | **H** |
| `SK-11` | WhatsApp notifies; it never instructs | **H** |
| `SK-12` | External groups are communicated to by their existing relationship owner | **H** |
| `SK-13` | Two-way channels are mandatory for Partner and Support groups | **H** |
| `SK-14` | Every communication is logged with recipient, sender, language and date | **H** |
| `SK-15` | `Interest` objections escalate; they are not answered with better messaging | **H** |
| `SK-16` | Two waves of silence from a Support group is a coverage failure, not consent | **S** |
| `SK-17` | The register is reviewed at every wave boundary; populations are re-counted, not carried forward | **H** |
| `SK-18` | Every group in this register appears in `CM-003`; a group absent from the calendar is a planning defect | **H** |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `05-04` §1 | The 38 roles and their populations — the internal register is derived from it |
| `00-04` §5.1, §5.3 | Governance forums, their membership and cadence |
| `00-04` §1.1, §1.2 | `RSK-001` and `RSK-008`…`RSK-012`, which set influence and concern |
| `06-01` §4 | The business-side commitments this plan assumes people can honour |
| `04-00` §2 | External populations |
| [`CM-001_Programme_Narrative_and_Change_Story.md`](CM-001_Programme_Narrative_and_Change_Story.md) | The eleven audience translations map onto S01–S27 |
| [`CM-003_Communication_Calendar_by_Wave.md`](CM-003_Communication_Calendar_by_Wave.md) | Where this plan becomes dated |
| `CG-010` §3.3 | The bilingual audience rule that `SK-08` enforces |
| **`06-05`** | **Does not exist** — the change plan this register should sit inside |

| Depended on by |
|---|
| `CM-003` calendar · `CM-005` kit distribution lists · `CM-009` newsletter circulation · `CM-010` roadshow audiences · `CM-011` objection attribution · `CM-016` campaign targeting · `RF-010` ownership directory |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **Every wave boundary** (`06-01` §7 requirement; rule `SK-17`) |
| Trigger for out-of-cycle review | A new external counterparty class · an organisational change · a role added to `05-04` or `MD-009` · an `Interest` objection from a Partner group |
| Owner | Change Lead; external rows co-owned with their relationship owners |
| Change log | `RF-006` |
| Enforcement | `SK-01`…`SK-18`; monthly coverage report to `S02`; `SK-18` reconciliation against `CM-003` |
| Improvement loop | Objection classification distribution per group is reviewed each wave; a group shifting from `Clarity` to `Interest` is an early warning, not a communication failure |

---

## 7. Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **`O-01`** | **`RSK-001` is unresolved and this plan assumes it is not.** Super-user availability (`S04`) is rated **Critical**, owned by the CEO, and `06-01` §4 calls business availability *"the binding constraint on the programme"*. Weekly communication to a group whose time is not protected is communication into a vacuum. Decision `D-02` is open | CEO with department heads | **W0 — before kickoff** |
| **`O-02`** | **The champion commitment is unfunded.** `S06` is 51+ people at 4 h/week for W1–W5; `TR-023` `O-02` records the same gap from the training side. No backfill is planned. The monthly champion forum — the single highest-leverage channel in this plan — depends on it | HR Director with Operations Director | **W1** |
| **`O-03`** | **The technician field pilot has no owner or date.** `SK-07` makes it the only channel giving `S07` influence, and `RSK-008` is one of five Critical risks. It appears in `00-04` as a mitigation and in no plan as an activity | Operations Director with Change Lead | **W2 minus 3 months** |
| **`O-04`** | **Two external-population enumerations now exist and they do not match.** `S18`–`S27` here are derived from `04-00` §2 and `05-04` §1.7; [`OP-001`](../17_Operations_Support_and_Runbooks/OP-001_Support_Model_Tiering_and_Routing_Content.md) §4.1 independently enumerates **eleven external audiences** and declares its own enumeration *“the definitive one”*, adding **seller technicians (1,000–4,000)** and splitting corporate **end users** from corporate **administrators** — neither of which appears here. A stakeholder map missing a 1,000–4,000-person population is missing a population | Change Lead with the Support Lead | **W1 — before the first external communication** |
| **`O-05`** | **The communication log required by `SK-14` has no system.** Recording recipient, sender, language and date for 27 groups over 36 months is a register, not a habit. `M27` is W4; the log is needed at W0 | Change Lead with PMO | **W0** |
| **`O-06`** | **No named Change Lead** (shared with `CM-001` `O-05`). This file names the Change Lead as owning communicator for `S06`, `S17` and the whole resistance mechanism | CEO with HR Director | **W0** |
| **`O-07`** | **`06-05` does not exist**, so the stakeholder map has no owning plan and `06-01` §7's requirement that it be *"maintained and reviewed each wave"* has no procedural home | CTO with Programme Director | **W0** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; §7 Open Items added per category convention
- [x] Category-standard audience · channel · timing · message · call-to-action table present (`CG-009` §3)
- [x] **All 38 registered roles accounted for across S01–S17**, with populations taken from `05-04` §1 rather than restated
- [x] Six external portal populations plus regulators, couriers and the delivery vendor registered as S18–S27
- [x] Influence and impact assessed on a two-axis model with a stated treatment per cell
- [x] **Decision rights stated per group**, including the deliberate null for technicians
- [x] Owning communicator named per group; no group defaults to the programme
- [x] Minimum contact frequency stated, including the unconditional monthly item for the wider workforce
- [x] Resistance tracking defined with a classification and an escalation rule for `Interest`
- [x] Eighteen governing rules with enforcement classes
- [x] All internal links resolve
- [x] Bengali counterpart — n/a for this file, `bilingual: no` per `CG-010` §3.2 (PMO planning instrument); **`SK-08` carries the Bengali obligation for the communications this plan schedules**
- [ ] **`O-01` `RSK-001` unresolved — the plan's most important group has no protected time**
- [ ] **`O-04` external population enumeration diverges from `OP-001` §4.1**
- [ ] **`O-02` champion commitment unfunded**
- [ ] **`O-03` technician field pilot unowned and undated**
- [ ] **`O-05` no communication log system**
- [ ] Named approver recorded — **pending Programme Content Lead**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
