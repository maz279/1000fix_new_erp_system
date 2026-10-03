---
id: CM-007
title: Hypercare Communication Pack
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-20
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Change Lead with Support
author: Change Lead with the Support Lead and Content Design
reviewers: [Support Lead, Operations Director, CTO, Contact Centre Supervisor, Branch Operations Lead, Localisation Lead, Content Design Lead, Quality Manager, Programme Content Lead]
approver: Content Design Lead
content_class: D
purpose: >
  Tells every user, on the first day and for the four weeks that follow, exactly where to go when
  something does not work — the four routes in order, the floor-walker's presence, the known-issue
  list and how it is refreshed, the expected disruption stated honestly in advance, and the exit
  notice. Hypercare succeeds or fails on whether users know where to go in the first 48 hours; a
  user who cannot get an answer in the first two days reverts to paper and does not come back
  without being pulled back.
traces_to: [OP-001, OP-002, OP-003, OP-004, OP-016, 06-01, 06-02, CM-001, CM-003, CM-005, CM-006, CM-008, CM-012, CM-016, DM-014, HC-015, HC-016, TR-022, SP-005, CG-011]
priority: P1
wave: W1
bilingual: yes
bn_counterpart: CM-007_Hypercare_Communication_Pack_BN.md
sources:
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-01 §5 — hypercare of four weeks of elevated support after every wave go-live
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-01 §6 — T−0 go-live with on-site support; T+4 weeks hypercare ends and the adoption review occurs
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-01 §7 — floor-walkers during go-live; dedicated internal support channel; escalation path
    verified: 2026-08-20
    class: P1
  - source: primary-doc/1000FiX_ERP_System_Comprehensive_BRD.md §21.6 — hypercare four weeks after every wave go-live, with a named lead and daily triage
    verified: 2026-08-20
    class: P1
  - source: primary-doc/1000FiX_ERP_System_Comprehensive_BRD.md §21.5 — support at go-live: floor-walkers, dedicated internal channel, published escalation path
    verified: 2026-08-20
    class: P1
  - source: project_content/12_Data_Migration_Content/DM-014 §4.8 — the parallel run, its declared primacy, its daily comparison and its exit checkpoint C8
    verified: 2026-08-20
    class: P1
supersedes: none
review_due: 2027-02-20
---

# CM-007 — Hypercare Communication Pack

> **Scope note.** This file owns **what users are told during hypercare**. It does not own the
> hypercare model itself — duration, staffing, floor-walking, triage cadence and exit criteria are
> [`OP-002`](../17_Operations_Support_and_Runbooks/OP-002_Hypercare_Plan_and_Exit_Criteria.md),
> which is written and at `Draft`. This file consumes `OP-002` and does not restate it (`CP-01`).
>
> **Boundary note.** **`OP-002` governs the model; this file governs the wording.** Where the two
> differ, `OP-002` governs and this file is corrected — including on duration: `06-01` §5 and BRD
> §21.6 state four weeks, and `OP-002` §4.3 sets **4–8 weeks per wave, as a minimum rather than a
> target** (`HD-01`). §4.6 of this file is expressed in phases, not in fixed weeks, for that
> reason.

---

## 1. Purpose

The register's justification is exact: *"Hypercare succeeds or fails on whether users know where
to go in the first 48 hours."*

A branch agent whose intake screen behaves unexpectedly at 10:00 on day one has three options: ask
someone, wait, or reach for the paper pad. Which one they choose is decided entirely by whether a
route they trust is visible from where they are standing. Nothing else in the hypercare plan
matters until that is true.

**Consequence of absence (`CP-03`).**

| Failure | Consequence |
|---|---|
| No visible route | Staff revert to paper on day one, and the wave's gate criteria become unmeasurable |
| Routes exist but are not published where the work happens | The route is used by head office and not by 51+ branches |
| No known-issue list | Every site raises the same defect independently; the service desk drowns in duplicates |
| Disruption not stated in advance | Normal transition friction is experienced as system failure |
| No refresh cadence | The known-issue list is trusted for two days and abandoned |
| No exit notice | Hypercare ends by exhaustion; staff notice the floor-walkers have gone and conclude support has been withdrawn |
| Floor-walker presence unannounced | The most expensive support resource in the programme is under-used |
| English-only | The people at the counter and in the field cannot read their own support routes |

---

## 2. Scope

**In scope:** the four support routes and their publication; the first-48-hours communication; the
floor-walker presence notice; the known-issue list, its format, refresh cadence and language; the
expected-disruption statement; the daily and weekly rhythm; the parallel-run instruction; the
hypercare exit notice; and rules `HY-01`…`HY-16`.

**Out of scope:**

| Subject | Owned by |
|---|---|
| Hypercare duration, staffing, floor-walking ratios, triage cadence, the known-issue **log** and exit criteria | [`OP-002`](../17_Operations_Support_and_Runbooks/OP-002_Hypercare_Plan_and_Exit_Criteria.md) §4.3, §4.4, §4.5, §4.6, §4.8 |
| The support model, tiers, routing and response commitments | [`OP-001`](../17_Operations_Support_and_Runbooks/OP-001_Support_Model_Tiering_and_Routing_Content.md) §4.7 |
| Canned responses and macros | [`OP-003`](../17_Operations_Support_and_Runbooks/OP-003_Service_Desk_Macro_and_Canned_Response_Library.md) |
| Incident severity messaging | [`OP-004`](../17_Operations_Support_and_Runbooks/OP-004_Incident_Communication_Template_Set.md) |
| Post-incident review | [`OP-016`](../17_Operations_Support_and_Runbooks/OP-016_Post_Incident_Review_Template_and_Register.md) |
| The go-live announcement and day-one follow-up | [`CM-006_Go_Live_Announcement_Pack.md`](CM-006_Go_Live_Announcement_Pack.md) |
| The champion's role and briefing | [`CM-008_Champion_and_Super_User_Network_Kit.md`](CM-008_Champion_and_Super_User_Network_Kit.md) |
| Self-service help content | `HC-015` FAQ bank, `HC-016` in-product help |
| Job aids | `TR-022` |
| Parallel-run mechanics, primacy and exit checkpoint | [`../12_Data_Migration_Content/DM-014_Cutover_Data_Checklist_and_Freeze_Communication.md`](../12_Data_Migration_Content/DM-014_Cutover_Data_Checklist_and_Freeze_Communication.md) §4.8 |

---

## 3. Audience

| Audience | Uses this file to… |
|---|---|
| **Branch and field staff (`S07`–`S10`)** | Know where to go, in the first hour |
| **Champions (`S06`)** | Know what they handle and what they pass on |
| **Floor-walkers** | Know what to say, and what they are not authorised to promise |
| **Service desk** | Recognise a known issue rather than log a new one |
| **Branch managers (`S05`)** | Run the daily huddle from a known-issue list |
| **Support Lead** | Publish one issue list rather than answer 51 versions of one question |
| **Change Lead** | Hold the exit notice to criteria rather than to a date |

---

## 4. Content

### 4.1 The four routes, in order

**`HY-01`: there are four routes and they are used in order.** Every published artefact states
them in the same order, with the same numbering, in both languages.

| # | Route | Use it when | Response commitment | Published on |
|:--:|---|---|---|---|
| **1** | **Look it up** — in-product help and the job aid | You are unsure how to do something you have been trained on | Immediate | `HC-016`, `TR-022` |
| **2** | **Ask your champion** — named person, on site | The system did something you did not expect | **While you wait, in person** | `CM-005` K4 card |
| **3** | **Floor-walker** — on site for the period in `OP-002` §4.4 | Route 2 is busy or cannot resolve it | Immediate, in person | This file, §4.3 |
| **4** | **Service desk** — the dedicated internal channel | Nobody on site can resolve it, or it affects other sites | **`OP-001` §4.7**: `Sev2` 30 min in hours · `Sev3` 4 working hours · `Sev4` 1 working day | `CM-005` K4 card |
| **E** | **Escalation** — when route 4 has not answered within its commitment | The work is stopped | Named person, named interval | This file, §4.7 |

> **`HY-02` — route 2 exists because route 4 cannot scale to 51+ sites in week one.** The champion
> is not a convenience; they are the only route with the capacity to answer 500+ people
> simultaneously. `CM-008` `O-01` records that the network is unfunded, which means route 2 is
> currently a route on paper.

### 4.2 The first 48 hours

**`HY-03`: the first-48-hours message is delivered face to face at every site, not sent.**

| When | Delivered by | Content |
|---|---|---|
| **Day 1, start of shift** | Branch manager, in the huddle | The four routes; who the champion is; where the floor-walker is; **that reverting to paper is not the answer, and what to do instead** |
| Day 1, midday | Champion | Walk the floor; ask, do not wait to be asked |
| **Day 1, end of shift** | Branch manager | What went wrong today, what is already known, what is fixed by tomorrow |
| Day 2, start of shift | Branch manager | **The known-issue list, in Bengali**, and the day's one thing to watch |
| Day 2, end of shift | Branch manager → Change Lead | Site report: what is still stopping work |

> **`HY-04` — "do not go back to paper" is stated with its alternative, never alone.** An
> instruction that removes the only fallback a person has, without giving them another, is not
> followed. The alternative is the numbered manual voucher and the catch-up batch where a genuine
> contingency applies (`DM-014` `CV-11`), and route 2 or 3 in every other case.

### 4.3 Floor-walker presence

`06-01` §7 and BRD §21.5 require floor-walkers at go-live; **`OP-002` §4.4 sets the model** —
coverage, duration and ratio per site type, from 10 working days at 1 per 8–10 users at a pilot
branch to 5 shifts of ride-along at 1 per 6 field technicians. `FW-02` draws them from the
champion network plus the project team. **This file owns only what must be communicated about
them:**

| Element | Rule |
|---|---|
| **Who** | Named, with a photograph on the site notice — 51+ sites, staff who have never met them |
| **Where** | The physical location they are based at, per site |
| **When** | Days and hours of presence, per site, for the full period |
| **What they can do** | Answer, demonstrate, raise a defect, request an escalation |
| **What they cannot do** | Grant access · change a configuration · override a control · promise a fix date |
| **When they leave** | **Announced in advance** — a floor-walker who simply stops appearing removes a route without notice |
| Language | The floor-walker at a Bengali-first site **speaks Bengali** or is paired with someone who does |

> **`HY-05` — floor-walker withdrawal is announced three days in advance.** It is the most
> visible signal in the hypercare period and its unannounced removal is read as abandonment.

### 4.4 The known-issue bulletin

The single highest-leverage artefact in hypercare — and **the published face of `OP-002` §4.6's
known-issue log**, not a second list.

> **`HY-06` — `OP-002` §4.6 owns the log; this file owns the bulletin.** The log carries the defect
> reference, the affected `OP-001` §4.1 population, the target release and the owner. The bulletin
> carries none of those. `OP-002`'s log has a **communication state** field naming this bulletin as
> a publication destination, which is the join between the two.

| Element | Rule |
|---|---|
| **Format** | One line per issue: **what you will see · why · what to do instead · when it will be fixed** |
| **What it is not** | A defect register. Defect references, severities, populations and release numbers stay in the `OP-002` log |
| **Entry** | An issue is bulletined when the log entry has a **workaround** — `OP-002` `KI-01` makes a workaround mandatory, and an entry without one is escalated rather than published |
| **Refresh** | **At every evening triage** (`OP-002` `KI-01`, 17:30 BST daily), published at a fixed time |
| **Publication** | In-product banner + the branch noticeboard + the champion's copy. **Not** email |
| **Language** | **Bengali primary** for any issue affecting `S07`–`S10` |
| **Customer-affecting issues** | Mirrored to the status page (`OP-005`) and to `HC` content — `OP-002` `KI-03` |
| **Removal** | A fixed issue is removed **and the fix is stated**, so the list shrinking is visible |
| **Ageing** | At **20 working days** the log entry becomes a problem record (`OP-002` `KI-02`, `SP-031` §8) and **leaves the bulletin**, with the reader told where it went |
| **At exit** | The log is **handed to BAU, not closed** (`OP-002` `KI-04`); the bulletin says so |
| **Ownership** | Support Lead compiles the log; **Change Lead approves the bulletin wording**; the champion distributes |

### 4.5 Expected disruption, stated in advance

**`HY-07`: what will get worse before it gets better is published before go-live, not explained
afterwards.**

| What degrades | For how long | Why | Said as |
|---|---|---|---|
| **Intake time** | Days 1–5 | Unfamiliarity, not system speed | *"Intake will be slower this week than it was on paper. It gets faster than paper by week three, and we measure it"* |
| **Job documentation time** | Weeks 1–2 | New evidence requirements | *"You are recording more than before. Some of it replaces a form you used to fill in later"* |
| **Status enquiries** | Days 1–3 | Customers unfamiliar with the new tracking | Contact-centre volume forecast (`CM-006` `O-01`) |
| **Double entry** | **The full parallel-run period** | `DM-014` `CV-19` — two weeks on service and finance, one full close for finance | *"You will record in both systems until [date]. The new system is the record; the old one is the comparison"* |
| Reporting | Weeks 1–4 | Data accumulating; comparisons unavailable | *"Trend reports need four weeks of data. Do not read week-one numbers as a trend"* |
| Van stock accuracy | Weeks 1–3 after a count | Consumption patterns re-establishing | Named in the W2 pack |

> **`HY-08` — the parallel run is the most under-communicated cost in the programme.**
> `DM-014` `O-03` records it as unresourced: two weeks of double entry for service and finance
> staff plus one full parallel month-end close, appearing in no plan. Staff will discover it on
> day one. Telling them in advance is the difference between a known cost and a broken promise.

### 4.6 The hypercare rhythm

**`HY-17`: the rhythm is expressed against the floor-walking period and the exit, not against a
fixed number of weeks.** `OP-002` §4.3 sets hypercare at **4–8 weeks per wave as a minimum**
(`HD-01`), and `HD-03` runs the wave clock from the **last** branch tranche. A communication
rhythm written to a fixed four weeks would end while half the sites were still in their first
fortnight.

| Cadence | Item | Audience | Owner |
|---|---|---|---|
| **Every evening triage** | Known-issue bulletin refresh (`OP-002` `KI-01`) | All sites | Support Lead |
| **Daily, floor-walking period** | Site huddle, start and end of shift | Per site | Branch manager |
| **Twice daily, whole period** | Morning and evening triage (`OP-002` §4.5) | Support, Change, Engineering, domain leads | Support Lead |
| **Daily, parallel run** | Comparison report between systems | Change Lead | `DM-014` §4.8 |
| **Weekly, whole period** | Site status summary to all sites | All staff in scope | Change Lead |
| Weekly | Adoption position by site and role (`00-04` §5.5) | `S02`, `S05` | Change Lead |
| **At parallel-run end** | Parallel-run exit reminder | Affected functions | Change Lead |
| **Exit − 3 working days** | Exit notice (§4.8) | All staff in scope | Change Lead |

### 4.7 Escalation

| Situation | Escalates to | Within |
|---|---|---|
| Route 4 has not responded within its commitment | Named support escalation contact | The commitment interval, once |
| **Work is stopped at a site** | Branch manager → Operations Director | **Immediately** |
| A site has reverted to paper | **Change Lead and Support Lead jointly** | Same day — this is an adoption failure, not a support ticket |
| The same issue is reported from more than five sites | Support Lead → Engineering, and it enters the `OP-002` §4.6 log | Same day |
| A log entry passes **20 working days** | Becomes a problem record (`OP-002` `KI-02`, `SP-031` §8); **the bulletin says where it went** | At the triage that day |
| Hypercare duration passes **150% of its `OP-002` §4.3 baseline** | **Steering Committee** (`OP-002` `HD-04`, `EP-10`) | The next meeting |
| A safety or data-protection concern | Security Lead / Legal, per `CG-013` | Immediately |

> **`HY-09` — reverting to paper is escalated as an adoption event.** `06-01` §9 gives the
> contingency: *"adoption failure at a location — pause rollout, diagnose, remediate, re-pilot
> before continuing."* That decision cannot be taken if the reversion is logged as a support ticket
> and closed.

### 4.8 The exit notice

**`HY-10`: hypercare ends on criteria, not on the calendar.** The criteria are `OP-002` §4.8
`HX-01`…`HX-18`, each measured and each required to hold for a stated consecutive period; this
file owns the notice and does not issue it until the exit form in `OP-002` §4.9 is signed.

| Element | Content |
|---|---|
| That it is ending | Stated three working days in advance |
| **What changes** | Floor-walkers leave; the service desk becomes the primary route; `OP-001` §4.7 baseline response commitments resume |
| **What does not change** | The champion stays — `OP-002` `HX-18` requires a named, trained champion at **100% of live sites at exit**. Routes 1, 2 and 4 continue |
| Open items | Bulletined issues still open, with owners — **the log is handed to BAU, not closed** (`OP-002` `KI-04`) |
| **Any waived criterion** | Named, with its compensating control. `HX-01`, `HX-09`, `HX-12` and `HX-17` are **not waivable**; any other may be waived once, jointly, and the waiver is recorded in `RF-006` |
| Adoption position | What the site achieved, by name (`CM-016`; `HX-08`) |
| **Thanks** | Named, per site |
| Next | The adoption review (`06-01` §6) |

> **`HY-11` — an exit notice that closes the known-issue list is a false notice.** Issues open at
> exit transfer to the standard support process with their owners intact, and the notice says so.

### 4.9 Audience · channel · timing · message · call-to-action

| Audience | Channel | Timing | Message | Call to action |
|---|---|---|---|---|
| All staff in scope | **Face to face, huddle** | **Day 1, start of shift** | The four routes; the champion; the floor-walker; do not revert to paper | Use route 2 before route 4 |
| All staff in scope | Site notice + in-product banner | **After every evening triage**, fixed time | Known-issue bulletin, **Bengali primary** | Check before you raise |
| All sites | Site notice with photograph | T−1 week and day 1 | Floor-walker name, place, hours | Approach them |
| Affected functions | Manager brief | Day 1 and weekly | **Parallel-run instruction and its end date** | Record in both until [date] |
| All staff in scope | Weekly summary | Weekly, whole period | What is fixed, what is known, what is next | None |
| `S05`, `S02` | Adoption report | Weekly | Site and role position, worst first | Intervene where lagging |
| All staff in scope | Manager brief + notice | **Exit − 3 working days** | Exit notice, with any waived criterion named | Use the service desk from [date] |
| Support, Change, Engineering | Morning and evening triage | **Twice daily, whole period** | Issue flow | Assign and date every issue |

### 4.10 Governing rules

| # | Rule | Class |
|---|---|:--:|
| `HY-01` | Four routes, used in order, published identically in both languages | **H** |
| `HY-02` | The champion is route 2 and carries the volume the service desk cannot | **H** |
| `HY-03` | The first-48-hours message is delivered face to face at every site | **H** |
| `HY-04` | "Do not revert to paper" is never stated without its alternative | **H** |
| `HY-05` | Floor-walker withdrawal is announced three working days in advance | **H** |
| `HY-06` | `OP-002` §4.6 owns the log; this file owns the bulletin, and an entry is bulletined only when it has a workaround | **H** |
| `HY-07` | Expected disruption is published before go-live, with duration and reason | **H** |
| `HY-08` | The parallel-run double-entry cost is stated explicitly to the staff who bear it | **H** |
| `HY-09` | Reverting to paper is escalated the same day as an adoption event, not closed as a ticket | **H** |
| `HY-10` | Hypercare exits on `OP-002` §4.8 `HX-01`…`HX-18`; the notice is not issued before the `OP-002` §4.9 exit form is signed | **H** |
| `HY-11` | Open issues carry through the exit with owners intact; the log is handed to BAU, not closed (`KI-04`) | **H** |
| `HY-12` | The bulletin is written in user language, never in defect-register language | **H** |
| `HY-13` | A log entry passing 20 working days leaves the bulletin as a problem record (`KI-02`), and the reader is told where it went | **H** |
| `HY-14` | Every artefact reaching `S07`–`S10` is Bengali-primary (`SK-08`, `CG-010`) | **H** |
| `HY-15` | Floor-walkers at Bengali-first sites speak Bengali or are paired with someone who does | **H** |
| `HY-16` | Notices meet `CG-011` — 12 pt minimum, 4.5:1 contrast, no colour-only meaning | **H** |
| `HY-17` | The rhythm runs against the floor-walking period and the exit, never against a fixed four weeks | **H** |
| `HY-18` | Any waived exit criterion is named in the exit notice with its compensating control | **H** |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| [`../17_Operations_Support_and_Runbooks/OP-002_Hypercare_Plan_and_Exit_Criteria.md`](../17_Operations_Support_and_Runbooks/OP-002_Hypercare_Plan_and_Exit_Criteria.md) | **Governs the model** — §4.3 duration, §4.4 floor-walking, §4.5 cadence, §4.6 the log, §4.8 `HX-01`…`HX-18`, §4.9 exit form |
| [`../17_Operations_Support_and_Runbooks/OP-001_Support_Model_Tiering_and_Routing_Content.md`](../17_Operations_Support_and_Runbooks/OP-001_Support_Model_Tiering_and_Routing_Content.md) | §4.7 response commitments printed as route 4; §4.1 populations |
| [`../17_Operations_Support_and_Runbooks/OP-003_Service_Desk_Macro_and_Canned_Response_Library.md`](../17_Operations_Support_and_Runbooks/OP-003_Service_Desk_Macro_and_Canned_Response_Library.md) · [`../17_Operations_Support_and_Runbooks/OP-004_Incident_Communication_Template_Set.md`](../17_Operations_Support_and_Runbooks/OP-004_Incident_Communication_Template_Set.md) · [`../17_Operations_Support_and_Runbooks/OP-016_Post_Incident_Review_Template_and_Register.md`](../17_Operations_Support_and_Runbooks/OP-016_Post_Incident_Review_Template_and_Register.md) | Canned responses, incident messaging, post-incident review |
| [`../17_Operations_Support_and_Runbooks/OP-005_Status_Page_and_Maintenance_Notice_Copy.md`](../17_Operations_Support_and_Runbooks/OP-005_Status_Page_and_Maintenance_Notice_Copy.md) | Where customer-affecting bulletin entries are mirrored (`KI-03`) |
| [`CM-005_Wave_Launch_Communication_Kit.md`](CM-005_Wave_Launch_Communication_Kit.md) | K4 is where routes 1, 2 and 4 are already printed |
| [`CM-006_Go_Live_Announcement_Pack.md`](CM-006_Go_Live_Announcement_Pack.md) | G7 hands the day-one known issues into this pack |
| [`CM-008_Champion_and_Super_User_Network_Kit.md`](CM-008_Champion_and_Super_User_Network_Kit.md) | Route 2 exists only if the network does |
| [`../12_Data_Migration_Content/DM-014_Cutover_Data_Checklist_and_Freeze_Communication.md`](../12_Data_Migration_Content/DM-014_Cutover_Data_Checklist_and_Freeze_Communication.md) §4.8 | Parallel run, primacy, daily comparison, `C8` exit |
| `HC-015`, `HC-016`, `TR-022` | Route 1 content |
| `06-01` §5, §6, §7 · BRD §21.5, §21.6 | Floor-walkers, daily triage, and the four-week figure **that `OP-002` §4.3 supersedes** |
| `CG-011` | Accessibility of printed and on-screen notices |

| Depended on by |
|---|
| Every wave's hypercare period · `OP-002` §4.6 log publication route · `CM-016` adoption baseline · the post-hypercare adoption review · `CM-012` post-cutover confirmation |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **After every hypercare exit** — the known-issue themes become the next wave's expected-disruption list |
| Trigger for out-of-cycle review | An `OP-002` revision · a support-route or response-commitment change · an adoption failure at a location · a change to the parallel-run period |
| Owner | Change Lead; the bulletin co-owned with the Support Lead, who owns the `OP-002` log behind it |
| Change log | `RF-006` |
| Enforcement | `HY-01`…`HY-18`; the exit notice is blocked by `HY-10` until the `OP-002` §4.9 exit form is signed |
| Improvement loop | **The count of route-4 contacts that route 2 could have answered is this pack's KPI.** A high count means the champion network is under-briefed, not that staff are escalating unnecessarily |

---

## 7. Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **`O-01`** | **`HX-08` — the most important exit criterion — is not currently measurable.** `OP-002` §4.8 requires *"≥ 90% of expected volume transacting in the system, not on paper or in legacy"*, sustained 10 working days. `OP-002-OI-05` records that this needs a **modelled expected volume per population** that does not exist. The exit notice this file issues therefore reports an adoption position it cannot evidence | BI Lead with the Programme Office | **W1** |
| **`O-02`** | **`HD-02` requires a full business cycle inside hypercare, and W1's is a month-end.** `OP-002` sets W1 at **8 weeks minimum** containing one full month-end; `06-01` §5 and BRD §21.6 both say four weeks, and `06-01` §6's rollout pattern ends hypercare at **T+4 weeks**. **Two source documents and one content file state a four-week window that `OP-002` doubles for three of nine waves.** Communication planned to `06-01` §6 will stop halfway through hypercare | Programme Manager with the Support Lead | **W1 minus 6 weeks** |
| **`O-03`** | **Floor-walker headcount is unresolved.** `OP-002` §4.4 sets ratios of 1 per 8–15 users; `OP-002-OI-04` records that this implies **20–40 people at a full branch tranche** and calls the ratios *"aspirational"* until the headcount is agreed. §4.3 of this file requires named people, per site, with published hours — which cannot be published until they exist | Change Lead with HR and the Operations Director | **W1 minus 6 weeks** |
| **`O-04`** | **Route 2 depends on an unfunded network** (`CM-008` `O-01`, `TR-023` `O-02`), and `OP-002` `FW-02` makes it worse: floor-walkers are drawn *from* the champion network, so routes 2 and 3 share one unfunded population. `HX-18` then requires a named, trained champion at **100% of live sites at exit** | HR Director with Operations Director | **W1** |
| **`O-05`** | **The Bengali counterpart does not exist**, and the bulletin refreshes **at every evening triage** — daily, in Bengali, at a same-night turnaround, against `CM-003` §4.5's stated 3-working-day minimum for a short notice. **The lead time and the refresh cadence are in direct conflict**, and the conflict is now sharper than the original four-week reading suggested | Localisation Lead with Support Lead | **W1 minus 3 weeks** |
| **`O-06`** | **The parallel run is unresourced** (`DM-014` `O-03`). `HY-08` requires it to be communicated honestly; communicating an unfunded double-entry period without a plan to staff it converts a resourcing gap into a credibility problem | Programme Director with CFO | **W2 / W3 minus 2 months** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; §7 Open Items added per category convention
- [x] Category-standard audience · channel · timing · message · call-to-action table present (`CG-009` §3)
- [x] **Four routes fixed in order** and published identically in both languages
- [x] First 48 hours specified as face-to-face delivery at every site, shift by shift
- [x] Floor-walker presence, limits and **announced withdrawal** specified
- [x] **Known-issue bulletin separated from the `OP-002` §4.6 log**, with the workaround entry condition, triage refresh, `KI-02` ageing and `KI-03` customer mirroring taken from `OP-002` rather than re-invented
- [x] **Expected disruption published in advance**, including the parallel-run double-entry cost
- [x] Reverting to paper made an escalated adoption event rather than a support ticket
- [x] Exit notice bound to `OP-002` §4.8 `HX-01`…`HX-18` and the §4.9 exit form, including named waivers
- [x] Rhythm expressed against the floor-walking period and exit rather than a fixed four weeks
- [x] Eighteen governing rules with enforcement classes
- [x] All internal links resolve
- [ ] **`O-01` `HX-08` adoption exit criterion not measurable**
- [ ] **`O-02` four-week and eight-week hypercare windows both current in the repository**
- [ ] **`O-03` floor-walker headcount unresolved (`OP-002-OI-04`)**
- [ ] **`O-04` routes 2 and 3 share one unfunded population**
- [ ] **`O-05` nightly Bengali bulletin refresh conflicts with the stated translation lead time**
- [ ] Named approver recorded — **pending Content Design Lead**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
