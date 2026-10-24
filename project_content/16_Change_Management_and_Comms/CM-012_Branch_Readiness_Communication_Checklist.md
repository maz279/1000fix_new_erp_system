---
id: CM-012
title: Branch Readiness Communication Checklist
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-20
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Change Lead with Operations
author: Change Lead with Branch Operations and the Data Migration Lead
reviewers: [Operations Director, Branch Operations Lead, CTO, Data Migration Lead, IT Administrator, L&D Lead, Support Lead, Warehouse Manager, Financial Controller, Localisation Lead, Content Design Lead, Programme Content Lead]
approver: Content Design Lead, with the Operations Director accepting the readiness definition
content_class: D
purpose: >
  Gives all 51-plus branches one definition of ready — the eight readiness domains, the evidence
  each requires, who confirms it, and the escalation when a branch cannot — and supplies the
  communication sequence that carries it from T minus 4 weeks to the go decision in Bengali and
  English. Fifty-one branches going live in waves need a single readiness definition, not
  fifty-one interpretations, and the C2 checkpoint in DM-014 cannot be passed without confirmations
  from every site in scope.
traces_to: [DM-014, OP-002, 06-01, 06-02, CM-003, CM-005, CM-007, CM-008, CM-010, TR-002, TR-023, DM-011, DM-013, MD-004, M15, M50, 05-04]
priority: P1
wave: W1
bilingual: yes
bn_counterpart: CM-012_Branch_Readiness_Communication_Checklist_BN.md
sources:
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-01 §6 — rollout pattern per location; T−4 weeks site readiness assessment covering connectivity, hardware and staffing
    verified: 2026-08-20
    class: P1
  - source: project_content/12_Data_Migration_Content/DM-014 §4.6 C2 — readiness checkpoint requiring CM-012 branch confirmations received from every site, counts scheduled and staff briefed in Bengali
    verified: 2026-08-20
    class: P1
  - source: project_content/12_Data_Migration_Content/DM-014 §4.9 — the 51-branch coordination problem; counting done by branch staff; a single missed branch is a hole in the opening position
    verified: 2026-08-20
    class: P1
  - source: project_content/12_Data_Migration_Content/DM-014 §4.4 — last-transaction rules by function, each with a named confirmation
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/00_Governance_and_Charter/00-04 §3.1 DEP-07 — branch connectivity and hardware readiness per rollout site, owned by the IT Administrator, blocking site rollout if late
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/00_Governance_and_Charter/00-04 §2 ASM-01, ASM-02 — 3G connectivity during operating hours; Company-issued Android 11+ technician devices
    verified: 2026-08-20
    class: P1
supersedes: none
review_due: 2027-02-20
---

# CM-012 — Branch Readiness Communication Checklist

> **Scope note.** This file owns **the readiness definition, the confirmation mechanism and the
> communication that carries it**. It does not own the freeze windows, the last-transaction rules
> or the runsheet — those are `DM-014`, and this file **consumes** them (`CP-01`). It does not own
> hypercare (`CM-007`), training (`TR-002`) or the champion role (`CM-008`).
>
> **Checkpoint note.** `DM-014` `C2` is the readiness checkpoint and it is decided by the **Change
> Lead with the Branch Operations Lead**. This file supplies the evidence that decision is taken
> on.

---

## 1. Purpose

The register's justification is exact: *"Fifty-one branches going live in waves need a single
readiness definition, not fifty-one interpretations."*

`DM-014` §4.9 states the consequence in one line: **"a single missed branch is a hole in the
opening position."** A branch that reports itself ready on a different definition from the other
fifty is not reporting readiness; it is reporting confidence.

**Consequence of absence (`CP-03`).**

| Failure | Consequence |
|---|---|
| No single definition | Fifty-one branch managers each decide what "ready" means, and the weakest definition wins |
| No evidence requirement | Readiness is a verbal assurance, and verbal assurances are given by people under pressure to be ready |
| No named confirmer per domain | The branch manager confirms things they cannot personally verify |
| No escalation for "not ready" | A branch that is not ready says it is, because saying so is easier than the conversation |
| Confirmations not counted | `DM-014` `C2` requires confirmations from **every** site and there is no count |
| Communication in English | The people confirming are branch managers at 51 sites, not head office |
| No partial-readiness route | A site with one open item is treated identically to a site with six |
| Readiness confused with training completion | A briefed branch is recorded as a trained branch (`RD-18`) |

---

## 2. Scope

**In scope:** the eight readiness domains and their evidence; the confirmation mechanism and its
named confirmers; the T−4 to T−0 communication sequence; the partial-readiness and not-ready
routes; the readiness dashboard and its counting rule; the re-confirmation rule; the post-cutover
confirmations; and rules `RB-01`…`RB-18`.

**Out of scope:**

| Subject | Owned by |
|---|---|
| Freeze windows, last-transaction rules, the runsheet, fallback triggers | [`../12_Data_Migration_Content/DM-014_Cutover_Data_Checklist_and_Freeze_Communication.md`](../12_Data_Migration_Content/DM-014_Cutover_Data_Checklist_and_Freeze_Communication.md) |
| Data quality rules and cleansing | `DM-011`; reconciliation `DM-013` |
| Training curriculum and assessment | `TR-002`, `TR-004` |
| Champion selection and role | [`CM-008_Champion_and_Super_User_Network_Kit.md`](CM-008_Champion_and_Super_User_Network_Kit.md) |
| Hypercare and first-day support | [`CM-007_Hypercare_Communication_Pack.md`](CM-007_Hypercare_Communication_Pack.md) |
| Go-live release messages | [`CM-006_Go_Live_Announcement_Pack.md`](CM-006_Go_Live_Announcement_Pack.md) |
| Hardware procurement and provisioning | IT Administration; `DEP-07`, `DEP-08` |
| Physical stock counting procedure | `M15` §16.4; `DM-007` |
| Cash counting procedure | `M50` §16.4; `DM-008` |

---

## 3. Audience

| Audience | Uses this file to… |
|---|---|
| **Branch managers (`S05`, 51+)** | Know exactly what they are confirming, and what evidence is required |
| **Change Lead** | Count confirmations and hold `C2` |
| **Branch Operations Lead** | Chase, escalate and decide with the Change Lead at `C2` |
| **Data Migration Lead** | Know which sites are ready to freeze |
| **IT Administrator (`R33`)** | Own the connectivity, hardware and access domains |
| **L&D** | Own the training-completion evidence |
| **Warehouse Manager / Financial Controller** | Own the count-readiness domains |
| **Champions (`S06`)** | Support their site through the checklist |

---

## 4. Content

### 4.1 The eight readiness domains

**`RB-01`: readiness is eight domains and a site is ready only when all eight are confirmed.**
Seven of eight is not ready; it is a specific, named exposure.

| # | Domain | What "ready" means | Evidence | Confirmed by | Deadline |
|:--:|---|---|---|---|:--:|
| **D1** | **Connectivity** | The site sustains the required bandwidth during operating hours, tested at the busiest hour, not at 07:00 | Test result with timestamp | **IT Administrator (`R33`)** | T−4 weeks |
| **D2** | **Hardware** | Counter terminals, label and receipt printers, scanners, and — where applicable — technician devices, present, enrolled and working | Asset list with serials, signed | IT Administrator with branch manager | T−3 weeks |
| **D3** | **Access** | Every person who needs an account has one, with the right role, and has logged in once | Login evidence per named person | IT Administrator with branch manager | **T−1 week** |
| **D4** | **Training** | Every person in scope has **completed and passed** their role pack — not attended a briefing (`RD-18`) | `M22` assessment record per person | **L&D** | T−1 week |
| **D5** | **Champion** | A confirmed, trained, published champion **and deputy** on site (`NW-16`) | Names on the K4 card and the site notice | Change Lead | T−1 week |
| **D6** | **Data** | Legacy data for this site extracted, profiled, cleansed to the `DM-011` threshold, and the branch's own review completed | `DM-013` site reconciliation extract, signed by the branch | **Branch manager with Data Migration** | T−3 weeks |
| **D7** | **Physical count readiness** | Counters identified and rehearsed (`DM-014` `CV-20`), count sheets received, store closure scheduled, van recall scheduled | Count schedule signed | **Warehouse Manager with branch manager** | T−2 weeks |
| **D8** | **Cash and finance** | Period position agreed, drawer count scheduled and witnessed, last invoice and Mushak numbers recorded per sequence | Finance confirmation | **Financial Controller with branch manager** | T−1 week |

> **`RB-02` — D1 is tested at the busiest hour of the busiest day.** `ASM-01` assumes at least 3G
> during operating hours. A connectivity test at a quiet moment tells you the line exists, not that
> it carries the branch.

> **`RB-03` — D4 is completion and assessment, never attendance.** `TR-004` sets the pass
> requirement, and training precedes access (`TR-002`). A branch that has been briefed
> (`CM-010` T3) has not satisfied D4, and `RD-18` exists so the two are not conflated.

### 4.2 Who confirms what — and why the branch manager does not confirm everything

**`RB-04`: each domain is confirmed by the person who can verify it, not by the person who is
accountable for the site.**

A branch manager cannot personally verify a bandwidth test, an `M22` assessment record or a
`DM-013` reconciliation. Asking them to confirm all eight produces a signature that means *"I have
been told"*, which is the failure mode this checklist exists to remove.

| Confirmer | Domains | Confirms into |
|---|:--:|---|
| IT Administrator (`R33`) | D1, D2, D3 | Readiness dashboard |
| L&D | D4 | Readiness dashboard, from `M22` |
| Change Lead | D5 | Readiness dashboard |
| Data Migration with the branch | D6 | `DM-013` site extract |
| Warehouse Manager with the branch | D7 | Count schedule |
| Financial Controller with the branch | D8 | Finance confirmation |
| **Branch manager** | **The site-level declaration** — that the confirmations are true of the site as they know it, and that the site can operate on the day | The `C2` submission |

### 4.3 The communication sequence

Anchored to `06-01` §6 and `CM-003` §4.4. **Bengali and English throughout** (`SK-08`).

| Offset | Message | To | Requires reply | Content |
|---|---|---|:--:|---|
| **T−6 weeks** | Champion nomination request | Branch manager | **Yes** | `CM-008` §4.3 |
| **T−4 weeks** | **Readiness notice — the checklist itself** | Branch manager | **Yes — acknowledgement** | The eight domains, the deadlines, who confirms each, and what the branch itself must do |
| T−4 weeks | Site readiness assessment scheduled | Branch manager + IT | No | Date and who attends |
| **T−3 weeks** | Data review request | Branch manager | **Yes** | The site's `DM-013` extract, in a form a branch manager can check |
| T−3 weeks | Manager cascade brief (`CM-005` K5) | Branch manager | No | The wave |
| **T−2 weeks** | Count rehearsal instruction | Branch manager + storekeeper | **Yes** | `DM-014` `CV-20` |
| T−2 weeks | Champion training (`TR-023`) | Champion | No | — |
| **T−1 week** | **Readiness confirmation request** | Branch manager | **Yes — the `C2` submission** | The eight-domain form, with each confirmer's status pre-populated |
| T−1 week | All-staff training and access | All site staff | Attendance | `TR-002` |
| **T−3 days** | **`C2` result to the site** | Branch manager | No | Ready / conditional / not ready, and what happens next |
| **T−7 days → freeze** | The `DM-014` §4.10 cutover sequence | All site staff | **Four replies** | `DM-014` owns; delivered through this file's channel |
| **Go decision** | Start now (`CM-006` G1) | All site staff | **Yes** | — |
| **Go + 2 weeks** | Parallel-run exit confirmation | Branch manager | **Yes** | `DM-014` `C8` |
| **Go + 4 weeks** | **Legacy withdrawal confirmation** | Branch manager | **Yes** | `DM-014` `C9`; BRD §6.5 |

> **`RB-05` — eight of these require a reply.** `DM-014` `CV-21` establishes that a communication
> with no confirmation is not a communication; readiness is the domain where that matters most,
> because the whole checkpoint is made of replies.

### 4.4 The readiness form

**`RB-06`: one form, pre-populated, returned by the branch manager.** A branch manager should
spend their time on the two lines that are wrong, not on transcribing the six that are right.

```
BRANCH READINESS CONFIRMATION — [Branch] — Wave [n] — Cutover [date]
────────────────────────────────────────────────────────────────────
                                    Status    Confirmed by      Date
D1 Connectivity (busiest hour)      [ ✔ / ✘ ]  IT Admin          ....
D2 Hardware and devices             [ ✔ / ✘ ]  IT Admin          ....
D3 Access — all staff logged in     [ ✔ / ✘ ]  IT Admin          ....
D4 Training completed and passed    [ ✔ / ✘ ]  L&D               ....
D5 Champion and deputy published    [ ✔ / ✘ ]  Change Lead       ....
D6 Data reviewed by the branch      [ ✔ / ✘ ]  Branch + Migration....
D7 Count readiness and rehearsal    [ ✔ / ✘ ]  Warehouse         ....
D8 Cash and finance position        [ ✔ / ✘ ]  Fin. Controller   ....
────────────────────────────────────────────────────────────────────
OPEN ITEMS (any ✘ — one line each, with owner and date)
1. ..........................................................
2. ..........................................................

BRANCH MANAGER DECLARATION
I confirm the above is true of this site as far as I am able to
verify it, and that anything I cannot verify is listed above.

Name .................  Signature .............  Date ..........
────────────────────────────────────────────────────────────────────
এই ফর্মটি বাংলাতেও পাওয়া যাচ্ছে — শাখা ব্যবস্থাপক যে ভাষায় স্বচ্ছন্দ, সেই ভাষায় পূরণ করুন
```

> **`RB-07` — the declaration is deliberately limited to what the manager can verify.** A
> declaration that overstates a manager's knowledge is signed anyway and means nothing. One that
> matches what they can actually see gets an honest answer.

### 4.5 Not ready — the route that must exist

**`RB-08`: a branch that is not ready must have a route that is less costly than pretending.**
This is the single most important rule in the file.

| State | Definition | Route | Decision |
|---|---|---|---|
| **Ready** | Eight of eight confirmed | Proceeds to cutover | `C2` pass |
| **Conditional** | Seven or eight confirmed with **named open items that do not touch D1, D3, D6 or D8** | Proceeds with a **dated remediation plan and a named owner per item** | `C2` conditional — Change Lead with Branch Operations Lead |
| **Not ready** | Any of **D1 connectivity, D3 access, D6 data, D8 cash** unconfirmed | **The site does not cut over.** It joins the next window | `C2` fail — **and this is a normal outcome, not a failure of the manager** |
| **Withdrawn** | The site raises a material issue after `C2` | Immediate escalation to the Operations Director; `DM-014` `T7` may apply | Programme Director |

> **`RB-09` — D1, D3, D6 and D8 are non-negotiable.** A site with no connectivity cannot
> transact. A site whose staff cannot log in cannot work. A site whose data is unreviewed
> contributes an unknown opening position. A site whose cash position is unagreed cannot be
> reconciled. The other four domains can carry a dated open item; these four cannot.

> **`RB-10` — a branch reporting "not ready" is acknowledged, not investigated.** The moment the
> first branch to say so is treated as a problem, every subsequent branch says it is ready.
> `06-01` §9 already provides the contingency: *"adoption failure at a location — pause rollout,
> diagnose, remediate, re-pilot before continuing."*

### 4.6 The readiness dashboard

| Element | Rule |
|---|---|
| **Unit** | The **site**, not the region. `DM-014` §4.9: a single missed branch is a hole |
| **Count** | Sites confirmed / sites in scope — **counted, never estimated** (`CP-11`) |
| Granularity | Per domain, per site, so the pattern is visible: eleven sites failing D2 is a procurement problem, not eleven branch problems |
| **Zero-tolerance line** | `C2` requires confirmations from **every** site in scope (`DM-014` `C2`) |
| Refresh | Daily from T−2 weeks |
| Escalation | Any site without an acknowledgement at T−3 weeks → Branch Operations Lead; without a submission at T−5 days → **Operations Director** |
| Reporting | Weekly to `S02` via `CM-004` Section 1; the **worst site**, not the average (`EP-06`) |

### 4.7 Re-confirmation

**`RB-11`: readiness expires.** A confirmation given at T−1 week for a cutover that slips by four
weeks is not evidence about the new date.

| Slip | Action |
|---|---|
| ≤ 5 working days | Confirmations stand; D3 access re-checked |
| 6–20 working days | **D3, D4, D7 and D8 re-confirmed**; the rest stand |
| > 20 working days | **Full re-confirmation.** Staff have changed, stock has moved, and training has decayed |
| Any slip | The branch is told the new date and the re-confirmation requirement **in the same message** |

### 4.8 Post-cutover confirmations

Readiness does not end at go-live. Three confirmations close the site's cutover:

| # | Confirmation | When | Why | Source |
|:--:|---|---|---|---|
| **1** | **Start acknowledgement** | On the go decision | The programme cannot otherwise say which of 51+ sites started | `CM-006` G1 |
| **2** | **Parallel-run exit** | Go + 2 weeks | `DM-014` `C8` — *"a parallel run that is simply allowed to lapse has not been exited"* | `DM-014` §4.8 |
| **3** | **Legacy withdrawal** | Go + 4 weeks | `DM-014` `CV-03`, BRD §6.5 — *"a wave gate is not passed while its legacy process is still running"* | `DM-014` `C9` |

> **`RB-12` — confirmation 3 is a wave-gate input, not a site formality.** A branch still using
> its spreadsheet fails the wave gate for every branch.

### 4.9 Audience · channel · timing · message · call-to-action

| Audience | Channel | Timing | Message | Call to action |
|---|---|---|---|---|
| Branch manager | **Written, EN + BN** | **T−4 weeks** | The eight domains, deadlines, confirmers | **Acknowledge within 3 working days** |
| Branch manager | Pre-populated form | **T−1 week** | Readiness form with confirmer statuses | **Return signed; list every open item** |
| IT Administrator | Task list per site | T−4 to T−1 weeks | D1, D2, D3 | Confirm into the dashboard |
| L&D | `M22` extract | T−1 week | D4 completion per person | Confirm into the dashboard |
| Warehouse Manager | Count schedule | T−2 weeks | D7 | Confirm; run the rehearsal |
| Financial Controller | Finance confirmation | T−1 week | D8 | Confirm; record last numbers per sequence |
| Branch manager | Written, EN + BN | **T−3 days** | `C2` result and what happens next | Act on the remediation plan, or stand down |
| Branch manager | Written, EN + BN | Go + 2 weeks, Go + 4 weeks | Parallel exit; legacy withdrawal | **Confirm** |
| `S02` Steering | `CM-004` Section 1 | Weekly in wave | Sites confirmed / in scope; worst site | Unblock the named constraint |

### 4.10 Governing rules

| # | Rule | Class |
|---|---|:--:|
| `RB-01` | Readiness is eight domains; all eight are confirmed or the site is not ready | **H** |
| `RB-02` | Connectivity is tested at the busiest hour, not at a convenient one | **H** |
| `RB-03` | Training readiness is completion and assessment, never attendance or briefing | **H** |
| `RB-04` | Each domain is confirmed by the person who can verify it | **H** |
| `RB-05` | Eight communications in the sequence require a reply | **H** |
| `RB-06` | One pre-populated form, returned by the branch manager | **H** |
| `RB-07` | The declaration is limited to what the manager can personally verify | **H** |
| `RB-08` | A "not ready" route exists that is less costly than pretending | **H** |
| `RB-09` | D1, D3, D6 and D8 cannot be carried as open items | **H** |
| `RB-10` | A branch reporting "not ready" is acknowledged, not investigated | **H** |
| `RB-11` | Readiness expires on slip, with re-confirmation scaled to the slip | **H** |
| `RB-12` | Legacy-withdrawal confirmation is a wave-gate input | **H** |
| `RB-13` | Every readiness communication is issued in Bengali and English (`SK-08`) | **H** |
| `RB-14` | The dashboard counts sites, never regions, and reports the worst site | **H** |
| `RB-15` | A domain failing at many sites is escalated as a programme problem, not as many site problems | **H** |
| `RB-16` | No site is declared ready on a verbal assurance; every domain carries named evidence | **H** |
| `RB-17` | Confirmations are counted, never estimated (`CP-11`) | **H** |
| `RB-18` | `C2` is decided by the Change Lead with the Branch Operations Lead, and the decision is recorded with its evidence | **H** |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| [`../12_Data_Migration_Content/DM-014_Cutover_Data_Checklist_and_Freeze_Communication.md`](../12_Data_Migration_Content/DM-014_Cutover_Data_Checklist_and_Freeze_Communication.md) | `C2` is the checkpoint this file evidences; `C8` and `C9` the closing confirmations; §4.10 the cutover message set |
| `06-01` §6 | The T−4 to T+4 pattern the sequence is anchored to |
| `DM-011`, `DM-013` | The data-quality threshold and site reconciliation extract D6 rests on |
| [`CM-008_Champion_and_Super_User_Network_Kit.md`](CM-008_Champion_and_Super_User_Network_Kit.md) | D5; `NW-16` makes coverage a cutover pre-condition |
| `TR-002`, `TR-004` | D4 completion and pass evidence from `M22` |
| [`CM-010_Town_Hall_and_Roadshow_Content.md`](CM-010_Town_Hall_and_Roadshow_Content.md) §4.7 | `RD-18` keeps briefing separate from training in D4 |
| `M15` §16.4 · `M50` §16.4 · `DM-007` · `DM-008` | The count and cash procedures D7 and D8 confirm readiness for |
| `DEP-07`, `DEP-08` · `ASM-01`, `ASM-02` | Connectivity, hardware and device assumptions D1 and D2 test |
| [`CM-006_Go_Live_Announcement_Pack.md`](CM-006_Go_Live_Announcement_Pack.md) · [`CM-007_Hypercare_Communication_Pack.md`](CM-007_Hypercare_Communication_Pack.md) | What follows a passed `C2` |
| [`OP-002`](../17_Operations_Support_and_Runbooks/OP-002_Hypercare_Plan_and_Exit_Criteria.md) | §4.2 entry conditions, which a conditional site enters on; `HX-18` requires a champion at 100% of live sites at exit — D5 seen from the other end |

| Depended on by |
|---|
| `DM-014` `C2`, `C8`, `C9` · every wave gate's site count · `CM-004` Section 1 sites-live figure · `CM-016` adoption baseline per site · the `06-01` §9 adoption-failure contingency |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **Before every wave's first cutover, and after every wave** — the domains that failed become the next wave's early focus |
| Trigger for out-of-cycle review | A site that confirmed ready and was not · a new readiness domain (for example device management from W2) · a change to `DM-014` `C2` |
| Owner | Change Lead with the Branch Operations Lead; each domain co-owned by its confirmer |
| Change log | `RF-006`; adding or removing a domain is MAJOR and re-translates |
| Enforcement | `RB-01`…`RB-18`; `C2` cannot pass without a confirmation from every site in scope |
| Improvement loop | **A site that confirmed ready and failed on the day is the most valuable finding available.** The post-cutover review asks which domain was confirmed on assurance rather than evidence, and that domain's evidence requirement is strengthened |

---

## 7. Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **`O-01`** | **No readiness dashboard exists.** §4.6 requires per-site, per-domain counting refreshed daily across up to 51 sites, with weekly reporting to Steering. `CM-002` `O-05` and `CM-003` `O-06` record the same absence of a communication and scheduling system. A checklist with no register is fifty-one emails | Change Lead with PMO | **W1 minus 6 weeks** |
| **`O-02`** | **D7 count readiness cannot currently be confirmed anywhere.** `DM-014` `O-02` records that the W2 count window has no schedule, that 200–400 van recalls and 17+ brand confirmations are unscheduled, and that branch staff who will do the counting have not been trained (`CV-20`). D7 is a domain with no underlying activity | Warehouse Manager with Branch Operations Lead | **W2 minus 3 months** |
| **`O-03`** | **D5 champion coverage is zero.** `CM-008` `O-05` records no champion nominated at any site, against a `NW-16` 100% cutover pre-condition that this file enforces as D5 | Change Lead with Operations Director | **W1 minus 8 weeks** |
| **`O-04`** | **The Bengali counterpart does not exist**, and `RB-13` makes every readiness communication bilingual. `DM-014` `CV-09` and `O-04` record the same requirement from the migration side and note that Category 12 is English-only by design, which places the entire Bengali obligation on this file | Localisation Lead | **W1 minus 4 weeks** |
| **`O-05`** | **D1 has no defined bandwidth threshold.** `ASM-01` assumes *"at least 3G during operating hours"*; `RB-02` requires a test at the busiest hour. No number exists to test against, so D1 is currently confirmed on judgement | CTO with IT Administration | **W1 minus 6 weeks** |
| **`O-06`** | **The `RB-10` culture commitment has not been made by management.** The rule that a "not ready" branch is acknowledged rather than investigated is a management undertaking, not a content rule. Without it stated by the Operations Director, the first honest branch will be the last | Operations Director | **W1 — before the first readiness notice** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; §7 Open Items added per category convention
- [x] Category-standard audience · channel · timing · message · call-to-action table present (`CG-009` §3)
- [x] **Eight readiness domains with evidence, named confirmer and deadline** — one definition for all 51+ sites
- [x] Confirmation split from accountability so no manager signs for what they cannot verify
- [x] Communication sequence anchored to `06-01` §6, with the eight reply-requiring messages identified
- [x] Worked readiness form with a bounded declaration
- [x] **"Not ready" route defined and made less costly than pretending**, with four non-negotiable domains
- [x] Dashboard counting rule at site granularity, reporting the worst site
- [x] Re-confirmation scaled to slip length
- [x] Post-cutover confirmations bound to `DM-014` `C8` and `C9` and to the wave gate
- [x] Eighteen governing rules with enforcement classes
- [x] All internal links resolve
- [ ] **`O-01` no readiness dashboard**
- [ ] **`O-02` D7 has no underlying count schedule or trained counters**
- [ ] **`O-03` D5 champion coverage is zero**
- [ ] **`O-04` Bengali counterpart not written; the whole bilingual obligation for cutover sits here**
- [ ] **`O-05` D1 has no bandwidth threshold**
- [ ] **`O-06` the `RB-10` management undertaking has not been given**
- [ ] Named approver recorded — **pending Content Design Lead with the Operations Director**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
