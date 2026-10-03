---
id: CM-006
title: Go-Live Announcement Pack
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-20
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Change Lead with Marketing
author: Change Lead with Marketing and Content Design
reviewers: [CEO, CTO, Operations Director, Marketing Manager, Support Lead, Contact Centre Supervisor, Data Migration Lead, Legal & Compliance, Localisation Lead, Content Design Lead, Programme Content Lead]
approver: Content Design Lead, with the Programme Director releasing on the go decision
content_class: D
purpose: >
  Holds the internal and external messages that are released at the moment a wave is declared
  live — the staff start-now instruction, the customer notice that a new portal exists, the
  contact-centre briefing, the hotline hold message and the partner notices — pre-written,
  pre-translated and pre-approved, so that the only thing that happens at T−0 is a release
  decision. Customers discovering a new portal without notice generates hotline volume at the
  worst possible moment, and messages composed on the night of a go-live are composed by tired
  people under pressure.
traces_to: [P01, P02, P03, 04-00, 06-01, 06-02, CM-001, CM-003, CM-005, CM-007, CM-012, CM-013, DM-014, NT-001, NT-004, OP-001, OP-004, OP-005, HC-015, LG-008, CG-010]
priority: P1
wave: W1
bilingual: yes
bn_counterpart: CM-006_Go_Live_Announcement_Pack_BN.md
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §P01 — customer portal capability set, design requirements and KPIs including the 88% online booking target
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §3 PS-09 — every user-visible error states what happened and what to do next, in the user's language
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-01 §6 — T−0 go-live with on-site support; T+2 weeks parallel run ends; T+4 weeks hypercare ends
    verified: 2026-08-20
    class: P1
  - source: project_content/12_Data_Migration_Content/DM-014 §4.6 C7 — the GO / NO-GO checkpoint held by the CTO with the Programme Director and not delegable
    verified: 2026-08-20
    class: P1
  - source: project_content/12_Data_Migration_Content/DM-014 §4.10 — go-decision and go+1-day messages, and the P2 contact-centre holding response requirement
    verified: 2026-08-20
    class: P1
  - source: primary-doc/1000FiX_ERP_System_Comprehensive_BRD.md §6.2 item 13 — customers call the hotline 3+ times per job today; the contact centre is already overwhelmed
    verified: 2026-08-20
    class: P1
supersedes: none
review_due: 2027-02-20
---

# CM-006 — Go-Live Announcement Pack

> **Scope note.** This file owns **what is said at T−0 and T+1 day**. It does not own the decision
> to release (`DM-014` `C7`), the pre-launch build-up (`CM-005`), hypercare guidance from T−0
> onward (`CM-007`), the customer transition programme (`CM-013`) or any transactional message
> (`NT-*`). Where a message here would duplicate an `NT` template, this file **names the template**
> and does not restate it (`CP-01`, `CM-R3`).
>
> **Release note.** Every asset in this pack is **written, translated and approved before T−7
> days, and released by the go decision.** Nothing in this file is drafted on the night.

---

## 1. Purpose

The register's justification is exact: *"Customers discovering a new portal without notice
generates hotline volume at the worst possible moment."*

The BRD records that customers already call the hotline **three or more times per job**, and that
the call centre is overwhelmed today, before any change. A go-live that surprises 250,000+
customers a month adds volume to a channel that has no headroom, on the day the staff answering
it are least able to absorb it.

**Consequence of absence (`CP-03`).**

| Failure | Consequence |
|---|---|
| No pre-written pack | Messages are composed at 02:00 by whoever is awake |
| Customers unnotified | Hotline volume spikes on the day the contact centre is learning a new console |
| No contact-centre brief | Agents answer *"I don't know, it's new"* to 250,000+ customers' worth of calls |
| No hold message | The queue lengthens silently |
| Staff start-now instruction missing | Branches wait, unsure whether the go decision was taken |
| Announcement released on a schedule rather than a decision | A go-live is announced for a wave that did not pass its gate (`CA-05`) |
| No partner notice | Vendors, brands and corporate clients discover a route change by having a transaction fail |
| Untranslated at release | The 275–635 people executing the change read it second-hand |

---

## 2. Scope

**In scope:** the seven go-live assets; the release rule and its authority; the internal start-now
instruction; the customer notice and its lawful basis; the contact-centre and hotline preparation;
partner notices; the go+1-day follow-up; the no-go and delayed-go variants; and rules
`GO-01`…`GO-16`.

**Out of scope:**

| Subject | Owned by |
|---|---|
| The go / no-go decision itself | [`../12_Data_Migration_Content/DM-014_Cutover_Data_Checklist_and_Freeze_Communication.md`](../12_Data_Migration_Content/DM-014_Cutover_Data_Checklist_and_Freeze_Communication.md) `C7` |
| Pre-launch communication | [`CM-005_Wave_Launch_Communication_Kit.md`](CM-005_Wave_Launch_Communication_Kit.md) |
| Hypercare help, known issues, escalation | [`CM-007_Hypercare_Communication_Pack.md`](CM-007_Hypercare_Communication_Pack.md) |
| Customer account migration and reference continuity | [`CM-013_Customer_Migration_and_Transition_Pack.md`](CM-013_Customer_Migration_and_Transition_Pack.md) |
| Adoption campaigns after launch | [`CM-016_Adoption_Campaign_Content.md`](CM-016_Adoption_Campaign_Content.md) |
| Transactional notifications | `NT-004`, `NT-009`, `NT-015` and the `NT-001` matrix |
| Incident and outage messaging | [`OP-004`](../17_Operations_Support_and_Runbooks/OP-004_Incident_Communication_Template_Set.md) · [`OP-005`](../17_Operations_Support_and_Runbooks/OP-005_Status_Page_and_Maintenance_Notice_Copy.md) |
| Status page copy | [`OP-005`](../17_Operations_Support_and_Runbooks/OP-005_Status_Page_and_Maintenance_Notice_Copy.md) |
| Release notes | [`OP-006`](../17_Operations_Support_and_Runbooks/OP-006_Release_Notes_Standard_and_Wave_Note_Set.md) |
| Privacy notice and lawful basis text | `LG-008` |

---

## 3. Audience

| Audience | Uses this file to… |
|---|---|
| **Change Lead** | Have every asset approved before the go decision is taken |
| **Programme Director / CTO** | Release, not draft, at `C7` |
| **Contact Centre Supervisor (`R35`)** | Brief agents before the first call arrives |
| **Marketing Manager (`R23`)** | Issue the customer notice within the permitted claim set |
| **Branch managers (`S05`)** | Tell their branch to start, with authority |
| **Account managers, Procurement, Warranty** | Notify their own counterparties |
| **Support Lead** | Anticipate volume and staff against it |

---

## 4. Content

### 4.1 The seven assets

**`GO-01`: all seven exist, translated and approved, before T−7 days.** The pack is a
pre-condition of the go decision, not a consequence of it.

| # | Asset | Audience | Released | Channel | Language |
|:--:|---|---|---|---|---|
| **G1** | **Start now — internal instruction** | All staff in scope | **On the go decision** | SMS + in-app + branch manager | **BN-first** |
| **G2** | **Branch manager release note** | `S05` | On the go decision, 30 min before G1 | Direct call + written | EN + BN |
| **G3** | **Customer notice — a new way to book and track** | Individual customers | **Go + 1 day**, staged | SMS, portal banner, in-app, hotline IVR | **BN-first** |
| **G4** | **Contact centre briefing and answer set** | `R34`, `R35` | **T−2 days** | Team brief + console knowledge base | **BN + EN** |
| **G5** | **Hotline hold and IVR message** | Callers | **On the go decision** | Telephony | **BN primary** |
| **G6** | **Partner and counterparty notices** | `S19`–`S23` | T−3 days, then go + 1 day | Relationship owner + portal | EN (BN for sellers) |
| **G7** | **Go + 1 day internal follow-up** | All staff in scope | Go + 1 day | Manager + in-app | **BN-first** |

> **`GO-02` — G4 is released at T−2 days, before the go decision.** The contact centre must be
> briefed on a launch that might not happen, because it cannot be briefed on one that already has.
> The brief carries both branches: *what to say if we go* and *what to say if we do not*.

### 4.2 The release rule

| # | Rule |
|---|---|
| **`GO-03`** | **The pack is released by the `C7` go decision and by nothing else.** No scheduled send, no calendar trigger, no "it's Monday" (`CA-05`) |
| **`GO-04`** | Release authority is the **CTO with the Programme Director** — the same non-delegable pair that holds `C7` (`DM-014` `CV-14`) |
| **`GO-05`** | **G1 precedes G3 by at least 24 hours.** Staff learn from the company, never from a customer |
| **`GO-06`** | G2 precedes G1 by 30 minutes so that a branch manager is never asked a question they have not yet been told the answer to |
| **`GO-07`** | Where a wave has no cutover, the release anchor is the **wave gate result**, not a cutover checkpoint |
| **`GO-08`** | **No asset is edited after approval and before release.** A correction after approval re-enters G1 editorial and, if it touches a Bengali-first asset, `BN-018` |

### 4.3 G1 — Start now

The shortest asset in the category and the one with the highest consequence.

| Element | Rule | Example frame |
|---|---|---|
| Instruction | **Imperative, first line** | *"Start using [system] now."* |
| Scope | Named sites and roles | *"[Branch] counter and workshop, from now."* |
| What stops | The legacy artefact, named, with the instant | *"The paper intake pad and the branch spreadsheet stop now."* |
| First action | One action | *"Log in and complete one intake with your champion."* |
| **P2 catch-up** | Where a freeze occurred: the paper batch keyed before normal operation resumes (`DM-014` `CV-11`) | *"Key your paper forms from the freeze window first."* |
| Help | K4 route (`CM-005`) | *"Your champion is [name]. Service desk [number]."* |
| **Confirmation** | **Required** — `CA-07` start acknowledgement | *"Reply START when your site is running."* |
| Length | **Under 60 words in each language** | — |

> **`GO-09` — G1 is under 60 words and requires a reply.** It is read on a phone, at a counter,
> with a customer waiting. Anything longer is not read, and anything without a reply leaves the
> programme unable to say which of 51+ sites actually started.

### 4.4 G3 — the customer notice

**`GO-10`: the customer notice is a service communication, not a marketing communication, and it
is written and consented as one.**

| Element | Rule |
|---|---|
| **Lawful basis** | The notice informs customers of a change to how the service they already hold is delivered. It is **not** promotional and must not carry a promotional call to action. Where any element is promotional, it requires the marketing basis in `LG-008` and the consent state in `MD-021` (`O-02`) |
| Content | What is new · what it means for them · **that their existing reference numbers still work** · that the hotline still answers · what they need to do (usually nothing) |
| **What it must not say** | *"Faster"*, *"better"*, *"improved experience"* — unmeasured claims (`NR-10`) |
| Staging | **Staged, never a single blast.** Volume tranches sized to contact-centre capacity, largest tranche last |
| Channel order | In-app and portal banner first (lowest cost, self-selecting), then SMS to customers with an open job, then wider SMS |
| Language | **Bengali primary** (`PS-03`, `CG-010` §3.3) |
| Timing | **Go + 1 day**, after the first day's operational problems have surfaced |
| Suppression | Customers in an open complaint, an open dispute, or an active service failure are **suppressed** from the tranche |

> **`GO-11` — the notice is issued at go + 1 day, not at go.** A notice issued at the moment of
> release drives customers into a system whose first-day defects have not yet been found, and into
> a contact centre that is handling its own first day.

### 4.5 G4 — the contact centre

The asset that decides whether the hotline holds.

| Part | Content |
|---|---|
| **What changed, in one paragraph** | For agents to say aloud, not to read out |
| **Answer set** | The twelve most likely caller questions, with a two-sentence answer each, in Bengali and English |
| **"I can't see that yet"** | The honest script for the transition period, and the call-back commitment |
| **Reference lookup** | How to find a customer by their **legacy reference** (`CM-013`; `DM-006` `SH-12`, the rule that indexes the legacy reference at the counter and in `P01`) |
| **What to escalate, and to whom** | The route, and the response commitment |
| **What not to promise** | Fix dates, refunds, or that "the old system is back" |
| **Volume expectation** | The forecast tranche sizes and timings from §4.4, so supervisors staff against them |
| **No-go branch** | The script if the go decision is *no* — see §4.7 |

**`GO-12`: the answer set is loaded into the agent console knowledge base, not distributed as a
document.** An agent with a caller on the line does not open an attachment.

### 4.6 G5 — hold and IVR

| Element | Rule |
|---|---|
| Language | **Bengali first, English second**, in that order, on every message |
| Length | Hold message under 15 seconds per language |
| Content | That a change is in progress · that the caller's job is safe · expected wait · the self-service alternative |
| **What it must not do** | Direct callers to a portal that a caller on a feature phone cannot reach |
| Removal | **Withdrawn at hypercare exit**, not left running (`CM-007`) |
| Owner | Contact Centre Supervisor, with `OP-005` when it exists |

### 4.7 The no-go and delayed-go variants

**`GO-13`: a no-go has a communication pack of equal quality.** A programme that has only
prepared for success communicates its first failure badly, and that is the communication people
remember.

| Variant | Trigger | Message | Audience | Timing |
|---|---|---|---|---|
| **No-go** | `C7` decides no; or a `T1`–`T7` fallback trigger fires (`DM-014` `CV-15`) | *"We are not going live tonight. Continue exactly as you are. Here is what happens next and when you will hear."* | All staff in scope, contact centre, affected partners | **Within 1 hour of the decision** |
| **Delayed go** | Go decision deferred inside the window | *"The start is delayed to [time]. Stay on the paper contingency. Do not start."* | All staff in scope | Immediately |
| **Partial go** | Some sites go, some do not | Site-specific G1; **no general announcement** | Per site | On decision |
| **Fallback executed** | `CV-16`–`CV-18` | The fallback notice, the P2 catch-up instruction, and the commitment to a post-mortem within five working days | All staff in scope | Within 2 hours |

> **`GO-14` — a no-go message is issued within one hour and names when the next update comes.**
> Silence after a visible non-event is filled within a day by a version of the story nobody wrote.

### 4.8 G7 — go + 1 day

| Element | Content |
|---|---|
| Acknowledgement | That the first day happened, and what actually went wrong — **named, not softened** |
| Known issues | The list, with workarounds, handed to `CM-007` from here on |
| What is working | Two or three concrete things, so the message is not only problems |
| The one thing to do today | Usually: complete the P2 catch-up, or complete your first transaction |
| Thanks | To the named people who worked the night — specifically, not generically |
| Next update | When, and from whom |

### 4.9 Audience · channel · timing · message · call-to-action

| Audience | Channel | Timing | Message | Call to action |
|---|---|---|---|---|
| `S05` branch managers | Call + written | **Go decision − 30 min** | G2 release note | Prepare to instruct your branch |
| All staff in scope | SMS + in-app | **On the go decision** | G1 start now | **Reply START; key the P2 catch-up first** |
| `R34`, `R35` contact centre | Team brief + console KB | **T−2 days** | G4 answer set, both branches | Load the answer set; staff to the forecast |
| Callers | IVR + hold | On the go decision | G5 | Use self-service if you can |
| Individual customers | Portal banner → in-app → SMS, **staged** | **Go + 1 day** | G3 notice | Nothing, or register |
| `S19`–`S23` partners | Relationship owner + portal | T−3 days and go + 1 day | G6 route change | Acknowledge |
| All staff in scope | Manager + in-app | Go + 1 day | G7 follow-up | Complete the day-one action |
| All staff in scope | SMS + manager | **Within 1 hour of a no-go** | No-go variant | **Do not start; continue as you are** |

### 4.10 Governing rules

| # | Rule | Class |
|---|---|:--:|
| `GO-01` | All seven assets exist, translated and approved, before T−7 days | **H** |
| `GO-02` | The contact-centre brief is released at T−2 days and carries both the go and no-go branches | **H** |
| `GO-03` | Release is by the `C7` go decision and by nothing else | **H** |
| `GO-04` | Release authority is the CTO with the Programme Director, non-delegable | **H** |
| `GO-05` | Staff are told at least 24 hours before customers | **H** |
| `GO-06` | Branch managers are told 30 minutes before their staff | **H** |
| `GO-07` | A wave with no cutover releases on the gate result | **H** |
| `GO-08` | No asset is edited between approval and release without re-entering its gates | **H** |
| `GO-09` | The start-now instruction is under 60 words per language and requires a reply | **H** |
| `GO-10` | The customer notice is a service communication with no promotional call to action | **H** |
| `GO-11` | The customer notice is issued at go + 1 day, staged to contact-centre capacity | **H** |
| `GO-12` | The agent answer set is loaded into the console, not distributed as a document | **H** |
| `GO-13` | The no-go pack is prepared to the same standard as the go pack | **H** |
| `GO-14` | A no-go is communicated within one hour and names the next update | **H** |
| `GO-15` | Customers in an open complaint, dispute or service failure are suppressed from the notice | **H** |
| `GO-16` | The hold and IVR message is withdrawn at hypercare exit | **H** |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| [`../12_Data_Migration_Content/DM-014_Cutover_Data_Checklist_and_Freeze_Communication.md`](../12_Data_Migration_Content/DM-014_Cutover_Data_Checklist_and_Freeze_Communication.md) | `C7` release authority; `CV-11` P2 catch-up; `CV-15`–`CV-18` fallback |
| [`CM-005_Wave_Launch_Communication_Kit.md`](CM-005_Wave_Launch_Communication_Kit.md) | K4 support routes reused in G1; the frame G1 extends |
| [`CM-007_Hypercare_Communication_Pack.md`](CM-007_Hypercare_Communication_Pack.md) | Known issues pass from G7 into hypercare |
| [`CM-013_Customer_Migration_and_Transition_Pack.md`](CM-013_Customer_Migration_and_Transition_Pack.md) | Legacy reference continuity that G3 and G4 both assert |
| `04-00` §P01 | What the customer notice may accurately describe |
| `NT-001` matrix, `NT-004` | Transactional messages G3 must not duplicate |
| `LG-008` | The lawful basis and privacy notice the customer notice relies on |
| [`OP-001`](../17_Operations_Support_and_Runbooks/OP-001_Support_Model_Tiering_and_Routing_Content.md) · [`OP-004`](../17_Operations_Support_and_Runbooks/OP-004_Incident_Communication_Template_Set.md) · [`OP-005`](../17_Operations_Support_and_Runbooks/OP-005_Status_Page_and_Maintenance_Notice_Copy.md) | Support routes in G1, escalation in G4, and the status-page standard G5 must not contradict |
| `MD-021` | Customer segments and consent state for tranche selection |

| Depended on by |
|---|
| Every wave go-live W1–W9 · the contact-centre first-day plan · `CM-007` hypercare handover · `CM-016` adoption baseline (the notice is the first adoption touchpoint) |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **Before every go-live**, and immediately after — the post-go-live review corrects the next pack |
| Trigger for out-of-cycle review | A support-route change · a contact-centre capacity change · a change to the customer notice's lawful basis · a fallback |
| Owner | Change Lead; G3 co-owned with Marketing, G4 and G5 with the Contact Centre Supervisor |
| Change log | `RF-006` |
| Enforcement | `GO-01`…`GO-16`; the pack's existence is a `C7` pre-condition |
| Improvement loop | **Hotline volume in the 48 hours after each go-live is the pack's own KPI.** A volume spike above forecast means G3 or G4 was inadequate, and the next wave's tranches are resized from the actual, not the estimate |

---

## 7. Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **`O-01`** | **No contact-centre capacity forecast exists for a go-live.** §4.4 stages the customer notice to capacity and §4.5 tells supervisors to staff against a forecast; neither exists. The BRD records the hotline as already overwhelmed at current volume, and `P10` is not delivered until W4 — so the first three go-lives are absorbed by a contact centre with no new tooling | Support Lead with Contact Centre Supervisor | **W1 minus 4 weeks** |
| **`O-02`** | **The lawful basis for the customer notice is unconfirmed.** `GO-10` treats it as a service communication under the Personal Data Protection Act 2026. `RSK-032` and `DEP-34` record that PDPA-compliant transparency notice text does not exist and that enforcement activates around 13 May 2027, inside W4. A service/marketing misclassification at 250,000+ recipients is a penalty-bearing error, not an editorial one | Legal with Marketing | **W2 minus 2 months** |
| **`O-03`** | **A degraded go-live fires three message sets at once and nothing says which governs.** `OP-004` is the Sev1–Sev4 incident template set; `OP-005` is the status page and maintenance notice copy; this pack is the go-live announcement. On the case that actually happens — a go-live that degrades service — G7, an `OP-004` Sev2 notice and an `OP-005` status entry would all fire, to overlapping audiences, in different words. **The precedence between them is undefined in all three files** | Support Lead with Change Lead | **W1 minus 4 weeks** |
| **`O-04`** | **The Bengali counterpart does not exist**, and five of the seven assets are Bengali-first — including G1, which is the instruction that starts 51+ sites. `CM-R6` blocks approval | Localisation Lead | **W1 minus 3 weeks** |
| **`O-05`** | **The IVR and hold message has no production route before W4.** `P10` and the telephony integration land at W4 (`DEP-11`, `DEP-26`, decision `D-06` open). For W1–W3 go-lives, G5 must be produced through the incumbent telephony arrangement, which no file describes | CTO with Contact Centre Supervisor | **W1** |
| **`O-06`** | **No SMS tranche capability is confirmed for staged sending.** §4.4 requires staged, suppressed, segment-selected sending at 250,000+ scale. `DEP-20` SMS gateway contracts are a W1 dependency and `M27` is W4 | CTO with Marketing | **W2 minus 2 months** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; §7 Open Items added per category convention
- [x] Category-standard audience · channel · timing · message · call-to-action table present (`CG-009` §3)
- [x] **Seven assets specified, all required to exist before T−7 days** — the pack is a pre-condition of the go decision
- [x] Release bound to the non-delegable `C7` authority rather than to a schedule
- [x] Staff-before-customers and manager-before-staff ordering made explicit with intervals
- [x] Start-now instruction constrained to 60 words with a mandatory reply
- [x] **Customer notice classified as a service communication**, staged to capacity, with suppression rules
- [x] Contact-centre answer set placed in the console rather than distributed
- [x] **No-go, delayed-go, partial-go and fallback variants specified to the same standard**
- [x] Sixteen governing rules with enforcement classes
- [x] All internal links resolve
- [ ] **`O-01` no contact-centre capacity forecast**
- [ ] **`O-02` lawful basis for the customer notice unconfirmed under the PDPA 2026**
- [ ] **`O-03` precedence between this pack, `OP-004` and `OP-005` undefined for a degraded go-live**
- [ ] **`O-04` Bengali counterpart not written; five of seven assets are Bengali-first**
- [ ] **`O-05` no IVR production route before W4**
- [ ] Named approver recorded — **pending Content Design Lead with the Programme Director**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
