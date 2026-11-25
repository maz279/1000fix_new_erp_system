---
id: SV-004
title: On-Call, Paging and Escalation Design
category: 11 — Service Operations & Support
code: SV
project: 1000FiX ERP System v2.0
version: 1.1
date: 2026-08-19
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Head of IT Service Management
approver: Chief Technology Officer, with HR Director co-approval for §6 and §9
standards_basis: >
  ISO/IEC 20000-1:2018 + Amd 1:2024 §8.6.1 incident management, §7.1 resources, §7.2 competence ·
  ITIL 4 incident management and monitoring-and-event-management practices · Google SRE on-call
  practice — multi-window burn-rate paging, page-worthiness, on-call load limits · PE-008 §8
  alerting and routing, adopted · OP-013 §4.1–§4.11, adopted by citation and extended
traces_to: >
  PGD-000 SV-004 row (⛔, P0, W1) · AUDIT-017 OP-06 (no paging platform), OP-09 (rota needs ten,
  has none), OP-08 (break-glass), §4 (NFR-045 unevidenceable) · OP-013 §4.3, §4.4, §4.7, §4.8,
  §4.9, §4.11, OI-01, OI-03, OI-05, OI-06 · NT-021 §2.3 AL-01…AL-07 · PE-008 §8 · PE-009 §8 ·
  05-06 NFR-045, NFR-006, KPI-088 · M66 §18 Q-02
depends_on: >
  SV-001 (this category — establishment §8.4, severity ruling §6.7) · SV-002 (burn-rate tiers) ·
  SV-003 (runbook reachable from the alert) · SV-006 (what happens after the page) ·
  PE-001 (issued) · PE-005 (issued) · PE-008 (issued — produces the alert) ·
  PE-009 (issued — break-glass, and the rule that emergency access must not depend on the estate) ·
  SC-003 DPIA (issued) · SC-004 (issued) · CO-003 (ISSUED 2026-08-19, during authoring) ·
  HR on-call policy (DOES NOT EXIST) · 38 access profiles (DO NOT EXIST)
verified_on: 2026-08-19
enumeration_timestamp: 2026-08-19 02:15 (+06)
rule_prefix: OCP — verified to return zero occurrences in identifier form across all 777 markdown files of the workspace before allocation, at 2026-08-19 02:15 (+06); re-verified against the 786-file baseline at 02:56 (+06). Conforms to RR-002 IDC-08
priority: P0
needed_by: W1
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# SV-004 — On-Call, Paging and Escalation Design

### Category 11 · Code `SV` · Rule space `OCP` · ISO/IEC 20000-1:2018 §8.6.1 · `PE-008` §8 · `OP-013` §4

---

> **`PGD-000` states the gap this document fills:** *"Audit **OP-06**: **no paging platform at all**.
> Audit **OP-09**: the on-call rota is documented and does not exist. A 24/7 service business with an
> unpaged platform is a business with a nightly outage risk."*
>
> **Both halves were re-verified independently at 2026-08-19 02:15 (+06) and both hold.** Searching
> all **777** markdown files of the workspace for every major on-call product name returns **two
> hits, and neither is a procurement**: `OP-005` cites PagerDuty's published guidance on status-page
> practice, and `RF-008` lists PagerDuty among external standards consulted. **No paging platform is
> named as a component of this estate anywhere.**
>
> This document is `P0` at `W1` because of a specific and unpleasant arithmetic. `PE-008` §8 now
> designs an excellent alerting system — eight SLOs, multi-window burn-rate detection, alert
> discipline, dashboards. **Every alert it produces currently terminates in a notification channel
> with no acknowledgement tracking and no escalation.** At 14:00 that is a minor gap. At 03:00, when
> `S-07` and `S-08` are committed 24×7 and the service desk is closed, **a designed alert that
> nobody is woken by is indistinguishable from no monitoring at all.**
>
> §5 makes the platform decision. §6 shows that the rota `OP-013` §4.3 specifies is **one person
> short of its own sustainability rule** once annual leave is counted.

---

## 1. Purpose

This document specifies **the mechanism by which a machine wakes a human, and the human structure
that receives it**: the paging platform and why it was chosen, the rota and how many people it
actually needs, which events page and which do not, what acknowledgement means and what happens
when it does not arrive, the authority the person woken already holds, and the employment terms
without which none of it survives its second month.

It exists because `AUDIT-017` found sixteen files describing a support service in 500 KB of correct
detail, and **one missing component that renders the out-of-hours half of all of it inoperative**.

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | The **paging platform decision** — requirements, market scan, ruling, and the two disqualified options (§5) |
| 2 | The **independence rule** — why the pager must not share a failure domain with what it pages about (§5.5) |
| 3 | The **rota**: structure, the corrected staffing arithmetic, shift pattern, holidays and Ramadan (§6) |
| 4 | **Severity-to-page mapping** — which events page, at what hour, to whom (§7) |
| 5 | **Acknowledgement, auto-escalation and the ladder** (§8) |
| 6 | **Page-worthiness and alert hygiene** — the discipline that keeps a pager trusted (§9) |
| 7 | **Terms and welfare** — allowance, time in lieu, load limits, and what happens without them (§10) |
| 8 | The **implementation plan**: eight weeks from decision to a page that has been acknowledged (§11) |
| 9 | **Measurement** — the six numbers that show whether on-call is working (§12) |

**Explicitly out of scope:**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| **The severity scale** `Sev1`–`Sev4` | [`OP-013`](../../project_content/17_Operations_Support_and_Runbooks/OP-013_On_Call_Escalation_and_Handover_Content.md) §4.1 | Canonical there, adjudicated by `AUDIT-017` `OP-04`, and re-adjudicated against `PE-008` §8.5 in `SV-001` §6.7. **This document maps severity to paging; it does not define severity** |
| **The alert set, SLIs, burn-rate thresholds, alert content** | [`PE-008`](../10_Infrastructure_DevOps_and_Environments/PE-008_Observability_and_Monitoring_Design.md) §7, §8 | `PE-008` produces the alert; this delivers it to a human. `PE-008` §1.1 draws the same line from the other side |
| Business, commercial, safety and legal escalation destinations | [`SP-005`](../../project_content/06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-005_Escalation_Matrix.md) | A different ladder for a different class of event |
| Support tiers and routing of ordinary contacts | [`OP-001`](../../project_content/17_Operations_Support_and_Runbooks/OP-001_Support_Model_Tiering_and_Routing_Content.md) | `T3` is paged; `T0`–`T2` are queued |
| **What happens after the page** — command, roles, communication, review | `SV-006` | This document ends at *"the engineer is awake and has the runbook open"* |
| Break-glass credential mechanics and the vault path | [`PE-009`](../10_Infrastructure_DevOps_and_Environments/PE-009_Configuration_and_Secrets_Management_Standard.md) §8 | §8.5 states the seam: **the pager must reach someone who can act** |
| The handover **format** | `OP-013` §4.9 | Adopted whole by citation (`OCP-02`); §8.7 adds only the enforcement |
| Incident communication wording, status page | `OP-004`, `OP-005` | A page is not a communication |
| Salary, grading and the value of the allowance | HR | §10 specifies the **shape** of the terms and explicitly declines to set the number |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| **Chief Technology Officer** | §5's platform decision and its cost; §6.3's finding that the rota is one person short; §14's four decisions |
| **HR Director** | §6 and §10 — this is the document that says what is being asked of ten people, and what must be agreed before it is |
| **CFO** | §5.6's cost comparison and §10.4's allowance shape |
| On-call engineers | §7 (what will wake you), §8 (what you must do in five minutes), §10 (what protects you) |
| Platform, Security, Integration and Data Engineering leads | §6's rota structure and the escalation ladder they sit on |
| Security Lead | §7.4's security path, which bypasses tiering by design, and §8.5's access precondition |
| Head of IT Service Management | §9's alert hygiene, §12's measures |
| Procurement / Legal | §5.4's supplier-longevity test and the `PSL-22` clause it implements |
| DPO | §5.7 — an on-call rota is a set of personal mobile numbers, and where they are held is a PDPA question |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause / section | How this document conforms | Departure and rationale |
|---|---|---|---|
| **ISO/IEC 20000-1:2018 + Amd 1:2024** | §8.6.1 incident management — incidents recorded, classified, prioritised, escalated where necessary against documented procedures | §7's mapping and §8's ladder are the escalation procedure; §12 measures it | **None in specification. In operation the clause is unmet**, because §6.3's rota is unstaffed |
| Same | §7.1 resources · §7.2 competence | §6.5's establishment; §10's terms; `OP-013` `RT-06`'s shadowing rule | None |
| **ITIL 4** | Monitoring and event management — events are detected, filtered and **acted on by the right party** | §9's page-worthiness test is the filter; §7 is the routing | None |
| **`PE-008` §8** | Burn-rate tiers, `AL-01`…`AL-04`, `RT-01`…`RT-04`, `AD-01`…`AD-05` | **Adopted whole and unmodified** (§7.3). This document adds only the delivery mechanism and the human structure | **One departure, `SV-001` §6.7**: `PE-008` §8.5's three-level severity model is mapped, not adopted; the four-level `OP-013` §4.1 scale governs |
| **`OP-013` §4.1–§4.11** | Severity, rota, paging, declaration, roles, ladder, authority, handover, out-of-band, load | **Adopted by citation** (`OCP-02`). §6.3 corrects one arithmetic consequence of §4.3 that `OP-013` did not follow through | Stated as a correction, not a contradiction |
| **Google SRE** | On-call practice — pages must be actionable, novel and urgent; load limits; the multi-window burn rate | §9.2's three-part page-worthiness test; §10.3's load limits | **Departure: no error-budget-driven release freeze** (`SV-001-D-05`) |

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| **`OP-013`** | [`../../project_content/17_.../OP-013`](../../project_content/17_Operations_Support_and_Runbooks/OP-013_On_Call_Escalation_and_Handover_Content.md) | §4.1 severity · **§4.3 the rota and its arithmetic, `RT-01`…`RT-08`** · §4.4 paging and auto-escalation, 8 steps · §4.5 declaration · §4.6 roles · §4.7 the L0–L5 ladder and the parallel escalations · **§4.8 the authority table** · §4.9 handover · §4.10 out-of-band tiers · **§4.11 load and welfare** · OI-01, OI-03, OI-05, OI-06 |
| **`PE-008` §8** | [`../10_.../PE-008`](../10_Infrastructure_DevOps_and_Environments/PE-008_Observability_and_Monitoring_Design.md) | §8.1 alerts fire on user-visible harm · §8.2 the three burn-rate tiers · §8.3 routing `RT-01`…`RT-04`, including **`RT-04`: alert delivery is itself monitored** · §8.4 alert discipline `AD-01`…`AD-05` · §8.5 the severity model this category maps rather than adopts |
| **`PE-009` §8** | [`../10_.../PE-009`](../10_Infrastructure_DevOps_and_Environments/PE-009_Configuration_and_Secrets_Management_Standard.md) | The break-glass design, and **`BF-01`: break-glass must not depend on the system being available** — the rule §5.5 generalises to paging |
| `NT-021` §2.3 | [`../../project_content/04_.../NT-021`](../../project_content/04_Notification_and_Messaging/04D_In_App_Voice_and_System/NT-021_System_Integration_and_Job_Failure_Alert_Library.md) | `AL-01`…`AL-07`: every alert names its runbook; suppression rules; `AL-06` immediate `Sev1` page; `AL-07` mandatory review |
| `PE-001` §6, §9 | [`../10_.../PE-001`](../10_Infrastructure_DevOps_and_Environments/PE-001_Infrastructure_and_Network_Architecture_Design.md) | Ingress topology; HA by tier; the four availability targets and their scopes |
| `SV-001` §5.2, §6.7, §8.4 | This category | The 21 services a page is routed against; the severity adjudication; the establishment this rota belongs to |
| `SV-002` §6.4 | This category | The burn-rate tiers as **service commitments**, and `PSL-16`/`PSL-17`'s content requirements for a burn-rate page |
| `SV-003` §9.1 | This category | The dependency register that answers *"who else do I page?"* |
| `AUDIT-017` `OP-06`, `OP-09`, §4 | [`../../project_content/_AUDIT/AUDIT-017`](../../project_content/_AUDIT/AUDIT-017_Category_17_OP_Content_Audit.md) | The two findings this document exists to close, and the statement that `NFR-045` cannot be evidenced |
| `M66` §18 Q-02 | [`../../1000fix_ERP_Module/.../M66`](../../1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M66_Internal_IT_Service_Management.md) | *"How many IT staff are there…? A tiered model with escalation paths requires enough people to have tiers."* |

### 2.3 External sources — the market scan

**Every row verified 2026-08-19.** Product lifecycle claims are the reason this section exists:
`PSL-22` requires every underpinning contract to state what happens on **product withdrawal**, and
two of the six candidates below are being withdrawn.

| Product | Model | Licence / cost | Lifecycle position | Class |
|---|---|---|---|:--:|
| **Atlassian Opsgenie** | SaaS | Commercial | **End of sale 2025-06-04. Full shutdown 2027-04-05. Non-migrated data deleted thereafter.** Capability split between Jira Service Management and Compass | P2 |
| **Grafana OnCall (OSS)** | Self-hosted | AGPL/OSS | **Maintenance mode from 2025-03-11; repository archived 2026-03-24.** Its OSS build relied on Grafana Cloud as the SMS and voice relay, **also deprecated** | P2 |
| **Grafana Cloud IRM** | SaaS | Free ≤ 3 active users, then ≈ USD 20 / active user / month | Current — the supported successor to OnCall | P2 |
| **PagerDuty** | SaaS | Commercial, per-user | Current; the reference implementation of the category | P3 |
| **incident.io** | SaaS | Commercial | Current; on-call bundled with incident management | P3 |
| **GoAlert** | **Self-hosted** | **Apache-2.0** | Current — built and maintained by Target's engineering team; **repository updated 2026-07-27**; single Go binary plus PostgreSQL; Docker images per release; escalation policies, schedules, rotations; SMS and voice via a configurable provider | P2 |
| **OneUptime** | Self-hosted or SaaS | Apache-2.0 | Current; bundles monitoring, status page and on-call | P3 |

> **The two disqualifications matter more than the seven rows.** **Grafana OnCall OSS is the option
> this estate would most naturally have reached for** — `PE-008` §3.3 already deploys Grafana, and
> the integration would have been near-zero. It was archived **on 2026-03-24, five months before
> this document**, and its OSS notification relay was deprecated with it. **Opsgenie shuts down on
> 2027-04-05, which falls inside this programme's 36-month horizon**: a Wave 1 procurement would have
> required a migration at roughly Month 20, in the middle of Wave 5.
>
> Neither fact is discoverable from the estate. Both are exactly the class of fact `RR-005`
> (Standards and Regulatory Currency Register) exists to catch and does not, being unwritten.

### 2.4 Audit findings this document closes or contributes to

| Finding | Source | Severity | How this document acts on it |
|---|---|:--:|---|
| **`OP-06`** — *"no paging platform at all"* | `AUDIT-017` | HIGH | **Closed in specification.** §5 selects a platform against twelve requirements, prices it, and §11 gives an eight-week implementation. Closes in fact on the first acknowledged test page |
| **`OP-09`** — *"the on-call rota needs ten people and has none"* | `AUDIT-017` | HIGH | **Closed in specification and sharpened.** §6.3 shows the true requirement is **eleven, not ten**, once annual leave is counted against `OP-013` `RT-04`. §6.5 places it in one establishment line |
| **`AUDIT-017` §4** — `NFR-045` (99.7% 24×7) cannot be evidenced | `AUDIT-017` | — | **Contributes.** §12's measures are the evidence; none can be produced before §11 completes |
| `OP-013` **OI-01** — rota unstaffed | `OP-013` §4.13 | — | §6.5 and `OCP-Q-01` |
| `OP-013` **OI-03** — on-call terms unagreed with HR | `OP-013` §4.13 | — | **§10 specifies the terms in full except the number**, so HR has a document to price rather than a request to interpret |
| `OP-013` **OI-05** — paging tooling unconfirmed | `OP-013` §4.13 | — | **Closed** by `SV-004-D-01` |
| `OP-013` **OI-06** — branch participation in out-of-band channels unconfirmed | `OP-013` §4.13 | — | §5.5's independence design depends on it; carried as `OCP-Q-06` |
| **`OP-08`** — break-glass documented, does not exist | `AUDIT-017` | HIGH | **Contributes.** §8.5: `RT-07`'s *"a pager with no hands"* is unenforceable until the 38 access profiles and `PE-009` §8's vault path are provisioned |
| **`PSL-F-07`** (`SV-002`) — a request-ratio SLI reports success by measuring nothing at 03:00 | This category | HIGH | **Contributes.** §9.4 requires a **heartbeat page** independent of traffic volume |

### 2.5 The rule space

**`OCP`**, verified at **2026-08-19 02:15 (+06)** to return **zero occurrences in identifier form**
across all **777** markdown files. The form `SV-nn` is not used (`SV-001` §2.4), and every
cross-document rule citation in this document names its owning file (`SMF-26`) — which matters more
here than anywhere else in the estate, because **`RT-04` currently has six distinct current meanings
across `OP-013`, `PE-007`, `PE-008`, `PE-009`, `IN-008` and `KB-014`**, and one of them is a rota
rule this document depends on.

---

## 3. The Gap, Enumerated

### 3.1 What exists

| Component | State | Evidence |
|---|:--:|---|
| **Alert generation** | ✅ **Designed** | `PE-008` §8 — burn-rate tiers, alert discipline, routing rules |
| **Alert content** | ✅ **Designed** | `PE-008` `RT-02`: what broke, which SLO, budget remaining, a runbook link, a correlation id |
| **Alert catalogue** | ✅ **Issued** | `NT-021` — the system, integration and job-failure alert library |
| **Notification transport** | ◐ **Partial** | `Novu` (`PE-008` `RT-01`, routes *"via Grafana → Novu"*); SMS gateway with `INT-011` failover; email `INT-013` |
| **Severity scale** | ✅ **Issued** | `OP-013` §4.1 |
| **Escalation rules on paper** | ✅ **Issued** | `OP-013` §4.4 steps 3–4, §4.7's L0–L5 ladder |
| **Runbooks to act on** | ✅ **Issued** (5 of 21 services; `SV-003` §5.3) | `OP-007`…`OP-012` |
| **Authority to act at 02:00** | ✅ **Issued** | `OP-013` §4.8 |

### 3.2 What does not

| Component | State | Consequence |
|---|:--:|---|
| **A paging platform** | ⛔ **None. Named nowhere in 777 files** | An alert reaches a channel. **A channel does not wake anybody, does not know who is on duty, and does not notice that nobody replied** |
| **Acknowledgement tracking** | ⛔ | `OP-013` §4.4 step 2's *"I am awake, I have seen it, I am acting"* has no recipient and no clock |
| **Auto-escalation** | ⛔ | §4.4 steps 3–4 — secondary at 5 min, lead at 10, CTO at 15 — is a description of a system nobody has built |
| **A rota** | ⛔ **Zero identified members** | *"The team"* is not a rota entry (`OP-013` `RT-02`), and at 03:00 there is no team |
| **On-call terms** | ⛔ | `RT-04`'s load ceiling and `RT-05`'s late-start protection are unenforceable |
| **Weekly test page** | ⛔ | `OP-013` §4.4 step 8. **An untested paging path is discovered on the night it fails** |
| **Delivery monitoring** | ⛔ | `PE-008` `RT-04` — *"a paging system that has not delivered in a week is tested, not trusted"* |

### 3.3 The sentence this reduces to

> **`OCP-01`. A notification is not a page.** A notification is sent to an address. **A page is
> delivered to a person who is on duty, escalates when they do not answer, and records that they
> did.** The estate has designed the first and specified the second, and owns neither.

The distinction is not pedantic. `PE-008` `RT-01` routes alerts *"via Grafana → Novu"*, and `Novu`
is a notification infrastructure component: it delivers messages across channels reliably and well.
**It has no concept of who is on call this week, of a five-minute acknowledgement deadline, or of
waking a second person when the first does not answer.** Those three concepts are the entire subject
of this document.

---

## 4. Requirements for the Platform

Twelve requirements, each traced. `M` = mandatory; a candidate failing any `M` is disqualified.

| # | Requirement | M/S | Source |
|---|---|:--:|---|
| **`PR-01`** | Deliver a page to a **named individual on duty** within 60 s of alert receipt, 24×7 | **M** | `OP-013` §4.4 step 3 (5-minute acknowledgement leaves no delivery budget) |
| **`PR-02`** | **Escalate across channels**: push → SMS → **voice call**. A silent push to a sleeping phone is not a page | **M** | `NFR-045`; `OP-013` §4.1 `Sev1` acknowledgement |
| **`PR-03`** | Track acknowledgement and **auto-escalate** at 5 / 10 / 15 min (`Sev1`) and 15 / 30 min (`Sev2`) | **M** | `OP-013` §4.4 steps 3–4 |
| **`PR-04`** | **Schedule and rotation management**, with overrides and swaps **recorded before the shift** | **M** | `OP-013` `RT-01`, `RT-03` |
| **`PR-05`** | **API ingestion** from Prometheus Alertmanager and Grafana | **M** | `PE-008` §3.3, §8.3 |
| **`PR-06`** | **Independent of the estate it pages about** — no shared failure domain with `S-01`…`S-21` | **M** | §5.5; `PE-009` `BF-01` by analogy |
| **`PR-07`** | Reliable delivery of SMS **and voice** to Bangladeshi (+880) mobile numbers at 03:00 | **M** | 51+ branches, 500–1,000 staff, a rota of Bangladeshi engineers |
| **`PR-08`** | Hold personal mobile numbers **under a recorded lawful basis**, with any cross-border transfer assessed | **M** | `OP-013` `OB-04`; `NFR-090`; `NFR-086b`; `SC-003` DPIA |
| **`PR-09`** | **Audit trail**: who was paged, when, by what channel, acknowledged when, escalated to whom | **M** | `NFR-014`; §12's measures |
| **`PR-10`** | Licence permissive under `AR-013` `LW-01` / `A-01`, **or** a funded commercial contract carrying §8.4's eight `SV-002` clauses | **M** | `AR-013`; `CO-004` |
| **`PR-11`** | **Survives the programme's 36-month horizon** without a forced migration | **M** | `PSL-22`; the Opsgenie precedent |
| **`PR-12`** | Supports a **scheduled weekly test page** that must be acknowledged, and exposes delivery metrics | **M** | `OP-013` §4.4 step 8; `PE-008` `RT-04` |
| `PR-13` | Mobile application with reliable background delivery, and a web console | S | Usability |
| `PR-14` | Bidirectional chat integration for the incident channel | S | `OP-013` §4.10 tier 1 |
| `PR-15` | Total cost of ownership under USD 5,000/year at 11 rota members | S | §5.6 |

> **`PR-06` and `PR-07` are the two that decide this**, and neither is obvious. §5.5 and §5.7
> explain why.

---

## 5. The Platform Decision

### 5.1 Assessment against the mandatory requirements

| Candidate | `PR-06` independence | `PR-07` +880 delivery | `PR-08` personal data | `PR-10` licence/cost | **`PR-11` longevity** | Verdict |
|---|:--:|:--:|:--:|:--:|:--:|---|
| **Opsgenie** | ✅ SaaS | ◐ international routes | ◐ cross-border | Commercial | ⛔ **Shutdown 2027-04-05** | **Disqualified — `PR-11`** |
| **Grafana OnCall OSS** | ◐ self-hosted | ⛔ relay deprecated | ✅ | AGPL | ⛔ **Archived 2026-03-24** | **Disqualified — `PR-11`, `PR-02`** |
| **Grafana Cloud IRM** | ✅ SaaS | ◐ international routes | ◐ cross-border | ≈ USD 2,600/yr at 11 users | ✅ | **Viable — the named fallback** |
| **PagerDuty** | ✅ SaaS | ◐ international routes | ◐ cross-border | Higher | ✅ | Viable, costlier |
| **incident.io** | ✅ SaaS | ◐ international routes | ◐ cross-border | Commercial | ✅ | Viable; overlaps `SV-006` |
| **GoAlert** | ✅ **if separately hosted (§5.5)** | ✅ **drives the local gateway** | ✅ **held in country** | **Apache-2.0** | ✅ **No vendor to withdraw** | **Chosen** |
| OneUptime | ✅ if separately hosted | ✅ | ✅ | Apache-2.0 | ✅ | Viable; broader than needed |

### 5.2 The ruling

> **`SV-004-D-01`. GoAlert, self-hosted in a separate cloud provider account from the production
> estate, driving the local SMS gateway for text and a voice provider for call escalation.
> Grafana Cloud IRM is named as the fallback, and the decision is **re-tested at the W2 gate against
> measured delivery rates**.**

| Consideration | Weight |
|---|---|
| **`PR-07`.** The rota is Bangladeshi engineers on Bangladeshi numbers. An international SaaS pager delivers SMS and voice to +880 over international carrier routes — the least predictable delivery path available, at the hour it matters most. **The estate already operates a local SMS gateway with an `INT-011` failover path**, and a self-hosted pager can drive it directly | **Decisive** |
| **`PR-11`.** Two of six candidates are being withdrawn, one of them inside this programme's horizon. Apache-2.0 with a single binary has no vendor that can withdraw it, and `PE-005` §5.3 already applied exactly this test to K3s | **Decisive** |
| **`PR-06`.** Self-hosting is only acceptable **because §5.5 puts it in a separate account.** A pager inside the estate is not a pager | Enabling condition |
| **`PR-08`.** Ten to eleven personal mobile numbers stay in country, which removes a `NFR-086b` cross-border assessment rather than answering one | Strong |
| **`PR-10`.** Apache-2.0 passes `AR-013` `LW-01` / `A-01` with **no exception required** — the same finding `PE-005` §5.3 recorded for K3s and containerd | Strong |
| Operational burden | **The honest counterweight.** One more thing to run, patch and back up, operated by a team that does not yet exist. §5.6 prices it and §5.8 states the exit |
| `PR-13` mobile app | GoAlert's push story is weaker than PagerDuty's. **Mitigated by `PR-02`'s escalation to SMS and voice**, which is the channel that actually wakes people |

### 5.3 What is being bought, concretely

| Element | Choice | Note |
|---|---|---|
| Application | GoAlert, single Go binary, container image per release | `PE-005` §3 image standard applies |
| Database | **A dedicated PostgreSQL instance in the pager's own account** | **Not** the estate's `S-02`. Sharing it would defeat `PR-06` in one line |
| Hosting | **A separate cloud provider account**, minimal footprint | §5.5 |
| SMS | The local gateway, with the `INT-011` failover path as second choice | `PR-07` |
| Voice | A voice-capable provider reaching +880 — **procurement item, `OCP-Q-03`** | `PR-02` |
| Push | GoAlert mobile/web push, **as the first escalation step only** | Never the last |
| Ingestion | Prometheus Alertmanager and Grafana webhooks | `PE-008` §8.3 |
| Chat | Incident channel webhook, one direction | `OP-013` §4.10 tier 1 |

### 5.4 The supplier-longevity test, applied

`PSL-22` requires every underpinning contract to state what happens on **product withdrawal**. This
decision is the first application of that rule, and it changed the outcome.

| # | Rule |
|---|---|
| **`OCP-03`** | **Every operational tool is assessed against the programme's 36-month horizon before selection, not at renewal.** Opsgenie would have passed every functional requirement in §4 and required replacement in Wave 5 |
| **`OCP-04`** | **A tool whose data cannot be exported in a documented format is not selected**, whatever its lifecycle position. Opsgenie's integrations, chat configuration and per-user notification preferences **cannot be exported** and must be rebuilt by hand — which is what turns a withdrawal into an outage of the paging system itself |
| **`OCP-05`** | **The paging platform is reviewed annually against its own market**, and the review is a standing item at the Service Management Board (`SV-001` §8.2) |

### 5.5 The independence rule — the one that decides self-hosting

> **`OCP-06`. The paging platform shares no failure domain with anything it pages about.** Not the
> same cloud account, not the same cluster, not the same database, not the same identity provider,
> not the same DNS zone, not the same on-call engineer's credentials.

This generalises `PE-009` `BF-01` — *"break-glass must not depend on the system being available"* —
from credentials to notification, and it is the reason self-hosting is acceptable here when it would
otherwise be a liability.

**The dependency that will be missed if it is not written down:**

| Tempting design | Failure |
|---|---|
| Pager authenticates via Keycloak (`S-03`) | `S-03` is a `P0` service and a **total-outage dependency** (`PE-001` §9.2). **An identity outage is a `Sev1` — and the pager that must announce it cannot authenticate anyone to acknowledge it** |
| Pager uses the estate's PostgreSQL (`S-02`) | A database incident silences the pager that reports database incidents |
| Pager runs in the production K3s cluster | A cluster or ingress failure removes both the service and the notification of it |
| Pager sends via the estate's own notification service | `S-11` is itself a monitored service |
| Pager uses the same DNS zone | A DNS misconfiguration takes both out — and DNS is a change, so this fails during a deployment |

| # | Rule |
|---|---|
| **`OCP-07`** | **The paging platform has its own local accounts**, not federated identity. This is a deliberate and documented exception to `SC-004`'s single-identity-provider rule, with MFA enforced locally, and it is registered as such rather than tolerated |
| **`OCP-08`** | **The paging platform's own health is monitored from the production estate**, and the estate's health is monitored by the paging account. **Each watches the other**; neither watches itself |
| **`OCP-09`** | **The out-of-band channels in `OP-013` §4.10 are the fallback when the pager itself fails** — SMS via the failover gateway, then the printed telephone tree. A pager with no fallback is a single point of failure in the mechanism that exists to survive single points of failure |

### 5.6 Cost

| Line | GoAlert self-hosted | Grafana Cloud IRM (fallback) |
|---|---|---|
| Licence | **Nil** — Apache-2.0 | ≈ USD 20 / active user / month × 11 ≈ **USD 2,640 / yr** |
| Hosting | One small instance + managed PostgreSQL in a separate account | Nil |
| SMS | Per message, **local gateway rates** | Bundled or per message, **international rates** |
| Voice | Per call, provider TBD (`OCP-Q-03`) | Bundled or per call, international |
| **Operational effort** | **≈ 0.5 PW to stand up, then ≈ 1 day / quarter** | ≈ 0.2 PW to configure |
| Data export on exit | Native PostgreSQL — trivially exportable | Vendor-dependent (`OCP-04`) |

> **The cost difference is not the argument, and pretending it is would be dishonest.** Both options
> are small against a 1,513 PW programme. **The argument is `PR-07` and `PR-11`** — delivery to +880
> at 03:00, and not repeating the Opsgenie migration in Wave 5. The cost table exists so nobody
> reopens the decision on a false economy in either direction.

### 5.7 The personal-data question

An on-call rota is a list of names, roles, shift times and **personal mobile numbers**. That is
personal data, and `OP-013` `OB-04` already requires it to be held under a stated lawful basis and
removed when someone leaves the role.

| Question | Position |
|---|---|
| Is it residency-classified under `NFR-086`? | **No.** `NFR-086` names NID, passport, TIN, biometric templates and recovered customer data. A staff mobile number is not in that set |
| Does `NFR-086b` apply to a SaaS pager? | **Yes, to the transfer.** A SaaS platform holding staff mobile numbers abroad is a cross-border transfer of personal data and needs a lawful basis and an assessment |
| What does self-hosting change? | **It removes the question rather than answering it.** The numbers stay in country. This is a benefit of `SV-004-D-01`, not its justification |
| What is still required? | A **`SC-003` DPIA entry** covering the rota: lawful basis (legitimate interest, contract), retention, and removal on role change — `OCP-10` |

| # | Rule |
|---|---|
| **`OCP-10`** | The rota's personal data is registered in `SC-003`, and a number is **removed within one working day** of a person leaving the rota — not the company. Leaving the rota and leaving the company are different events and the first is far more common |
| **`OCP-11`** | **Personal numbers held for continuity (`OP-013` §4.10 tier 4) are held under the same basis and reviewed quarterly** with the contact-detail verification `OP-013` `OB-02` already requires |

### 5.8 The exit

> **`OCP-12`. The decision is re-tested at the W2 gate against three measured numbers**, and the
> fallback is taken without renegotiation if any fails:

| Measure | Threshold to continue |
|---|---|
| SMS delivered within 60 s of alert | **≥ 99%** over the weekly test pages of the preceding 8 weeks |
| Voice call connected within 90 s on escalation | ≥ 95% |
| Paging platform's own availability | ≥ 99.9%, measured from the production estate (`OCP-08`) |

**This is what makes self-hosting a decision rather than a preference.** A pager that does not
deliver is worse than no pager, because the organisation believes it is covered.

---

## 6. The Rota

### 6.1 Structure — adopted from `OP-013` §4.3

`OP-013` §4.3 defines six rotas and this document adopts them unchanged. Restated here **only** in
summary, because §6.3 corrects one number in it and the correction is unreadable without the table.

| Rota | Covers | Hours | `OP-013` §4.3 minimum |
|---|---|:--:|:--:|
| **Platform primary** | ERP core, integration, portals, apps | 24×7 | **6** |
| **Platform secondary** | Backup; second pair of hands on `Sev1` | 24×7 | 6 — *"same pool, offset"* |
| **Security on-call** | Identity, suspected compromise, data incidents | 24×7 | **4** |
| Business escalation | Ops Director / duty manager | 24×7 | 4 |
| Executive escalation | CTO + named deputy | 24×7 | 2 |
| Data engineering | Warehouse and pipelines | Business hours, extended at close | 2 |

**`OP-013` `RT-01`…`RT-08` are adopted whole** (`OCP-02`) and are not restated: four-week
publication, named primary and secondary, swaps recorded before the shift, the one-in-three ceiling,
the late-start protection, two shadowed shifts, the access precondition, and explicit holiday
planning.

### 6.2 The arithmetic `OP-013` states

> *"A 24×7 primary rota on one-week shifts needs **six people** for a one-in-six rotation. At four it
> is one-in-four, which is the point at which people leave; at three it is unsafe and the rota
> becomes two people plus a fiction."* — `OP-013` §4.3

That is correct **for the primary rota considered alone**, and it is where `OP-013` stops.

### 6.3 The arithmetic `OP-013` does not follow through

`OP-013` §4.3 also requires a **platform secondary** rota, staffed from the *same pool of six,
offset*. Following that through:

| Step | Calculation | Result |
|---|---|---|
| Positions to fill every week | Primary + secondary | **2** |
| On-call person-weeks per year | 2 × 52 | **104** |
| Per person, from a pool of 6 | 104 ÷ 6 | **17.3 weeks/year** |
| As a rotation | 52 ÷ 17.3 | **1 in 3.0** |
| **`OP-013` `RT-04` ceiling** | *"Nobody is on call for more than **one week in three** sustained"* | **1 in 3.0** |

**A pool of six lands exactly on its own ceiling, with zero headroom** — before anybody takes a
day's leave.

Now count leave. Assume ~20 days annual leave plus public holidays ≈ **5 weeks/year** during which a
person cannot hold a rota position:

| Step | Calculation | Result |
|---|---|---|
| Available weeks per person | 52 − 5 | **47** |
| Pool of 6: available person-weeks | 6 × 47 | 282 |
| Load | 104 ÷ 282 | **1 in 2.7 — `RT-04` breached** |
| **Pool required to stay inside 1-in-3** | 104 ÷ (47 ÷ 3) | **6.6 → 7 people** |
| Pool of 7: check | 104 ÷ (7 × 47) = 104 ÷ 329 | **1 in 3.16 ✓** |

> **`OCP-F-01`. The platform rota needs seven people, not six.** `OP-013` §4.3's figure of six is
> correct for a single 24×7 rotation and is **one short** once its own secondary rota and ordinary
> annual leave are counted against its own `RT-04` ceiling. At six, every period of leave, sickness
> or resignation puts the rota into breach of a rule the same document sets.
>
> This is not a criticism of `OP-013`, which states the primary arithmetic correctly and completely.
> It is the arithmetic nobody carried to the second rota — the same class of oversight as
> `SV-002` `PSL-F-01`'s maintenance window, found the same way.

**The revised total:**

| Rota | `OP-013` §4.3 | **Required** | Δ |
|---|:--:|:--:|:--:|
| Platform (primary + secondary, one pool) | 6 | **7** | **+1** |
| Security on-call | 4 | 4 | — *(one 24×7 rotation; 52 ÷ 4 = 13 weeks each = 1 in 3.6 of available weeks ✓, and `OP-013` is right that four is where people start leaving)* |
| **Total engineering rota headcount** | **10** | **11** | **+1** |

### 6.4 Shift pattern

| Attribute | Value | Basis |
|---|---|---|
| Shift length | **One week**, Sunday 09:00 → Sunday 09:00 BST | `OP-013` §4.3; handover lands in a working hour, not at midnight |
| Handover | At shift change **and at 08:00 after any overnight activity**, in the `OP-013` §4.9 format | `OCP-02` |
| Publication | **≥ 4 weeks ahead**, visible to Support, Operations and the executive | `OP-013` `RT-01` |
| Swaps | Allowed; **recorded before the shift**, never after the page | `OP-013` `RT-03` |
| Secondary | **A different person from the primary, always** | `OP-013` `RT-02` |
| New joiners | **Two full shadowed shifts** before holding a position | `OP-013` `RT-06` |

### 6.5 Holidays, Ramadan and Eid

`OP-013` `RT-08` requires public holidays and Ramadan/Eid periods to be planned **explicitly** rather
than inherited from the ordinary pattern. Making that operational:

| # | Rule |
|---|---|
| **`OCP-13`** | **Eid-ul-Fitr and Eid-ul-Adha rotas are published eight weeks ahead**, not four, and are volunteered for before they are assigned |
| **`OCP-14`** | **No single person holds both Eid periods in the same year** |
| **`OCP-15`** | During Ramadan the shift boundary moves to accommodate Sehri and Iftar, and the **secondary is explicitly awake** during Iftar for `P0` services. This is a real availability window and pretending otherwise produces an unacknowledged page |
| **`OCP-16`** | The holiday calendar used by the rota is **`M30`'s Bangladesh holiday set** — the same source `M66` `T-04` uses for SLA clocks, so a public holiday means the same thing in both systems |

### 6.6 The establishment

**Eleven engineering rota positions, plus six escalation positions**, all inside `SV-001` §8.4's
single establishment table so the CFO prices one number.

| Rota | Headcount | Additive or allocated? |
|---|:--:|---|
| Platform (primary + secondary) | **7** | **Allocated** from the delivery squad — `SMF-15` |
| Security on-call | **4** | Allocated |
| Data engineering (business hours) | 2 | Allocated |
| Business escalation (duty managers) | 4 | Allocated — existing roles |
| Executive escalation | 2 | Existing roles |
| **Additive headcount this document creates** | **0** | **The cost is the allowance (§10), not the salary** |

> **`OCP-F-02`. This rota adds no headcount and it is not free.** Eleven engineers give up their
> evenings and weekends on a rotation, and the cost is an **allowance, time in lieu, and the delivery
> capacity lost to `RT-05` late starts**. `SV-001` `SMF-15` records that these are the same people
> hypercare wants ring-fenced (`OP-002-OI-01`). **Two documents are asking eleven people for the
> same time, and neither has been funded.**

---

## 7. What Pages, and When

### 7.1 The principle

> **`OCP-17`. A page interrupts a person's sleep. It is justified only when a human must act now and
> the action cannot wait until morning.** Everything else is a ticket. `PE-008` `AD-01` says the same
> from the alert side: *an alert with no action is removed.*

### 7.2 Severity to paging behaviour

Severity is `OP-013` §4.1's four-level scale (`SV-001` `SMF-27`). This table states only what the
**pager** does with each level; every other column of `OP-013` §4.1 — definitions, cadence, comms,
restoration targets, review obligations — is unchanged and not restated.

| | **`Sev1`** | **`Sev2`** | **`Sev3`** | **`Sev4`** |
|---|---|---|---|---|
| **Pages?** | **Yes, 24×7** | **In hours; out of hours only if customer-affecting** | No — ticket | No — dashboard |
| Channel sequence | Push → **SMS at 60 s** → **voice at 120 s** | Push → SMS at 120 s | — | — |
| Acknowledge within | **5 min** | 15 min in hours · 60 min out of hours | 4 working hours | — |
| Unacknowledged → | **Secondary at 5 min · lead at 10 · CTO at 15** | Secondary at 15 · lead at 30 | — | — |
| Also pages | Security on-call **if** suspected compromise; Business Decision Owner at declaration | — | — | — |
| Basis | `OP-013` §4.4 steps 1–4; `NT-021` `AL-06` | `OP-013` §4.1, §4.4 | `OP-013` §4.1 | `OP-013` §4.1 |

> **`OCP-18`. The channel sequence is not configurable per person for `Sev1`.** An engineer may
> choose their `Sev2` preferences. **`Sev1` always reaches voice**, because the failure mode of a
> per-person preference is one person whose phone is on silent, and that person is discovered at
> 03:00 during a payment outage.

### 7.3 Burn-rate alerts — adopted from `PE-008` §8.2

`PE-008` §8.2's three tiers are adopted unchanged. This document adds only the routing column, and
`SV-002` §6.4 adds the content requirements.

| Tier | Burn rate | Windows | Budget | `PE-008` action | **Routes to** |
|---|---:|---|:--:|---|---|
| **Fast** | 14.4× | 1 h / 5 min | 2% | **Page** | On-call primary. **`Sev1` for a `P0` service in its measurement window; `Sev2` otherwise** (`PSL-16`) |
| **Medium** | 6× | 6 h / 30 min | 5% | **Page** | On-call primary in hours; **ticket + service owner out of hours** (`PE-008` `AL-03`) |
| **Slow** | 1× | 3 d / 6 h | 10% | **Ticket** | Service owner, and the next Board agenda |

**Every burn-rate page carries what `PSL-17` requires**: the service, the SLO, the budget consumed
**and the budget remaining** — plus `PE-008` `RT-02`'s runbook link and correlation id.

### 7.4 Two paths that bypass the rota by design

| Trigger | Behaviour | Basis |
|---|---|---|
| **Suspected security or personal-data incident** | Pages the **security on-call and the platform on-call simultaneously**, and notifies the DPO. Does not wait for triage | `OP-001` §4.3; `OP-013` §4.7 parallel escalations; the `NFR-094` clock runs from **detection** |
| **Safety of a person** | **Leaves the paging system entirely** and follows `SP-030`. Support's only duty is to route it there within the same contact | `OP-013` §4.7; `OP-001` §4.3 |

> **`OCP-19`. A suspected data incident pages both rotas at once.** Sequencing them costs the
> difference between the two acknowledgement windows, and that difference is taken out of a statutory
> assessment clock. **`SC-011` owns the classification; the pager makes no judgement** (`M66`
> `BRU-ITS-21`).

### 7.5 What must **not** page

| Condition | Why not | Where it goes |
|---|---|---|
| CPU, memory or disk above a threshold, with no user impact | `PE-008` §8.1: *"a CPU alert at 80% pages someone about a number"* | Ticket → `PE-006` §7 scaling triggers |
| A `Sev4` threshold approached | Informational by definition | Dashboard |
| Slow-burn budget consumption | `PE-008` `AL-02` | Ticket |
| A failed job that will retry successfully, and does | `OPS-05` requires the outcome reported; a self-healing failure is not a page | Job dashboard |
| Anything in a **declared and announced** maintenance window | `PSL-19`; suppression un-suppresses automatically at the stated end | Suppressed, with expiry |
| An alert with no runbook | `PE-008` `AD-01`, `NT-021` `AL-01`, `OPS-03` — **the alert is the defect** | Removed or fixed |

---

## 8. Acknowledgement and Escalation

### 8.1 What acknowledgement means

> **`OCP-20`. Acknowledged means *"I am awake, I have seen it, I am acting."* It does not mean
> resolved, and it does not mean understood.** — `OP-013` §4.4 step 2, adopted verbatim.

### 8.2 The auto-escalation ladder, as configured

`OP-013` §4.4 steps 3–4 and §4.7's L0–L5 ladder, expressed as escalation-policy steps the platform
executes without a human deciding to escalate.

| Step | At | Notifies | Channels | Basis |
|:--:|:--:|---|---|---|
| 0 | 0 s | **On-call primary** | Push, then SMS at 60 s, then voice at 120 s | `OP-013` §4.4 |
| 1 | **5 min** unacknowledged | **On-call secondary** | Push + SMS + voice | `OP-013` §4.4 step 3 |
| 2 | **10 min** | **Platform lead** (or Security Lead for a security event) | SMS + voice | `OP-013` §4.4 step 3, §4.7 L2 |
| 3 | **15 min** | **CTO** | SMS + voice | `OP-013` §4.4 step 3, §4.7 L3 |
| 4 | **2 h** into an unresolved `Sev1` | **Crisis Management Team** | Per `OP-012` §4.2 | `OP-013` §4.7 L4 |
| 5 | On CTO judgement | **CEO / Board** | Direct | `OP-013` §4.7 L5 |

| # | Rule |
|---|---|
| **`OCP-21`** | **Escalation is automatic and requires no decision.** The commonest failure of an escalation ladder is that escalating feels like an admission, so nobody does it. **Removing the decision removes the reluctance** |
| **`OCP-22`** | **An acknowledged page stops escalation; it does not stop the incident clock.** `OP-013` §4.1's restoration targets and `OP-004`'s communication clock run from declaration regardless |
| **`OCP-23`** | **A page acknowledged and then abandoned re-escalates.** If no incident record exists 15 minutes after acknowledgement of a `Sev1`, step 1 fires again. Acknowledgement from a half-asleep engineer who then falls back asleep is a real and documented failure mode |
| **`OCP-24`** | **The escalation ladder is tested end to end, to the CTO step, once per quarter**, out of hours, announced to the participants but not scheduled to the minute |

### 8.3 Declaration

`OP-013` §4.5 owns declaration and is adopted whole. The one thing this document adds is mechanical:

> **`OCP-25`. Acknowledging a `Sev1` page opens an incident record automatically.** `OP-013` §4.5
> requires the record; making it a side effect of acknowledgement removes the step most often skipped
> in the first ten minutes, when it is the step that makes the timeline possible (`OP-016` §4.3).

### 8.4 Who else gets paged — reading the dependency register

When a `P0` service pages, the on-call needs to know **what else is affected** without deriving it at
03:00. `SV-003` §9.1's register has a *depended-on-by* column for exactly this.

| # | Rule |
|---|---|
| **`OCP-26`** | **Every page names the affected service's `S-nn` identifier and its depended-on-by set.** A page for `S-03` (identity) states that every service depends on it, because at 03:00 nobody reconstructs that |
| **`OCP-27`** | **Owners of dependent services are notified, not paged**, unless their own service is independently alerting. Paging twelve people for one root cause is how a rota is destroyed |

### 8.5 The precondition nobody can configure around

> **`OCP-28`. A rota member who cannot act is a pager with no hands.** — `OP-013` `RT-07`.

| Requirement | State | Consequence if unmet |
|---|:--:|---|
| The 38 standard access profiles | **⛔ Do not exist** (`AUDIT-017` `OP-10`) | Every W1 grant is bespoke; an on-call engineer's production authority is decided per person |
| The break-glass vault path | **⛔ Designed (`PE-009` §8), not provisioned** | An identity outage at 03:00 is recovered by improvisation — *"which is precisely the circumstance in which improvised privileged access becomes an unattributable production change"* (`AUDIT-017` `OP-08`) |
| Emergency spend delegation | **⛔ Proposed only** (`OP-013` §4.8 `AU-01`) | The CTO is the only spend authority at 02:00 |

**These three are not this document's to close** — they belong to `SC-004`, `PE-009` and the CFO.
**They are stated here because they are the difference between a paged engineer and an effective
one**, and because a paging project that reports "done" while all three are open has delivered an
alarm clock.

---

## 9. Alert Hygiene

### 9.1 Why a section on hygiene sits in a paging document

A pager's value decays with its precision. Two noisy weeks and every page is read as probably
nothing, which is the state that precedes the missed one. `PE-008` §8.4 owns alert discipline;
this section owns the **paging-specific** half.

### 9.2 The page-worthiness test

> **`OCP-29`. An alert may page only if it passes all three: *actionable*, *novel*, *urgent*.**

| Test | Question | Fails if |
|---|---|---|
| **Actionable** | Is there a documented action a woken engineer can take now? | The runbook says *"investigate"* |
| **Novel** | Is this different from what is already known and being worked? | It duplicates an open incident, or fires per-node for one cause |
| **Urgent** | Does waiting until 09:00 make it materially worse? | It does not — then it is a ticket |

**Applying this is a service owner's obligation (`SV-001` §5.3) and is reviewed quarterly with the
`RBS-14` alert↔runbook correspondence check.**

### 9.3 The disciplines, adopted from `PE-008` §8.4

`PE-008` `AD-01`…`AD-05` are adopted unchanged: every alert has a runbook entry; alert volume is
reviewed at every wave gate; an alert that has never fired is reviewed; an alert acknowledged and
not acted on three times is deleted or fixed; silencing requires a reason and an expiry.

`OP-013` §4.4 steps 5–7 add suppression-with-count, the 20-per-week deletion review, and the
runbook-link requirement. **All are adopted. None is restated.**

> **`OCP-30`. The one addition: an alert that has paged out of hours three times in a quarter without
> producing an incident record is removed from the paging path** — demoted to a ticket — **by the
> service owner, without a meeting.** Three false wake-ups is where trust goes, and requiring a
> forum to fix it guarantees a fourth.

### 9.4 The heartbeat — closing `PSL-F-07`

`SV-002` `PSL-F-07` records that a real-request-ratio SLI **reports success by measuring nothing**
during low-traffic hours — precisely the 03:00 window in which `S-07` and `S-08` are committed 24×7
and no human is watching.

> **`OCP-31`. A synthetic heartbeat journey runs against every `P0` service every 60 seconds from
> outside the estate, and two consecutive failures page as a `Sev1` regardless of request volume.**

This is the paging-side implementation of `SV-002` `PSL-06` and it is the only alert in the estate
that fires on **absence** rather than on error rate. It is also the only one that would detect a
total ingress failure at 04:00 on a Friday.

### 9.5 The dead man's switch

| # | Rule |
|---|---|
| **`OCP-32`** | **A scheduled test page is sent weekly and must be acknowledged.** An unacknowledged test page is investigated as a paging failure, not repeated | `OP-013` §4.4 step 8 |
| **`OCP-33`** | **The paging platform's delivery is monitored from the production estate** (`PE-008` `RT-04`, `OCP-08`). A paging system that has not delivered in a week is **tested, not trusted** |
| **`OCP-34`** | **If the paging platform is unreachable for more than 15 minutes, the estate notifies the on-call via the `OP-013` §4.10 tier-2 SMS path directly**, and the incident channel says so. The failure of the pager is itself a `Sev2` |

---

## 10. Terms and Welfare

### 10.1 Why this section decides whether any of the rest works

> **`OCP-35`. An unpaid, unrecognised rota does not survive contact with the second month.** —
> `OP-013` §4.11, adopted.

`OP-013` §4.13 OI-03 records the terms as unagreed with HR, and `AUDIT-017` `OP-09` records the
consequence: *"an unstaffed rota does not degrade gracefully — it degrades into two people, and then
into one."* **This document specifies the terms in full except the money**, so HR has something to
price rather than a request to interpret.

### 10.2 What is being asked of a rota member

| Obligation | Detail |
|---|---|
| Availability | Reachable and able to reach a laptop with connectivity within **15 minutes**, for one week in three |
| Response | Acknowledge a `Sev1` within **5 minutes**, 24×7 |
| Constraint | No travel beyond connectivity, no alcohol, no unreachable periods, for the whole shift week |
| Competence | Able to execute every `P0` procedure for the services covered (`SV-001` §8.5) |
| Preparation | Two shadowed shifts before the first held shift; handover written before leaving (`OP-013` `HO-04`) |

**That is a material constraint on a person's week, and it is what the allowance compensates.**

### 10.3 The protections, and how each is enforced

| Protection | Rule | Enforcement |
|---|---|---|
| **Load ceiling** | No more than **one week in three** sustained, never two consecutive | `OP-013` `RT-04`; §6.3's pool of seven is what makes it achievable; **breach is reported to HR automatically** |
| **Late start** | An engineer who worked a `Sev1` past 01:00 **does not start the next working day before 12:00** | `OP-013` `RT-05`. **`OCP-36`: this is applied automatically from the incident record, not requested by the engineer.** Requiring the request is how it stops happening |
| **Page volume** | > 5 pages/shift-week, or > 2 out-of-hours pages/shift, triggers an alert-quality review — **an engineering problem, not a staffing one** | `OP-013` §4.11 |
| **Quarterly load** | > 5 shifts by the same person in a quarter → **the rota is under-staffed and it is reported to the Steering Committee** | `OP-013` §4.11 |
| **Compensating rest** | Time in lieu for hours worked out of hours, taken within 4 weeks | **`OCP-37` — proposed; HR to ratify** |

### 10.4 The allowance — shape specified, amount deferred

> **`SV-004-D-02`. This document specifies the *shape* of the on-call allowance and explicitly
> declines to set its amount.**

| Element | Specification | Amount |
|---|---|---|
| Standby allowance | Paid **per shift week held**, whether or not paged | **HR to set** |
| Call-out payment | Paid **per out-of-hours page worked**, above the standby allowance | **HR to set** |
| Time in lieu | Hours worked out of hours, at minimum hour-for-hour, taken within 4 weeks | `OCP-37` |
| Eid premium | An enhanced rate for the two Eid periods (§6.5) | **HR to set** |
| Applies to | **All eleven engineering rota positions**, at the same rate for the same rota | `OCP-38` |

| # | Rule |
|---|---|
| **`OCP-38`** | **The allowance is the same for everyone on the same rota, regardless of grade.** The constraint on a Friday evening is identical for a senior and a junior engineer, and differentiating it is the fastest available way to make the junior stop volunteering |
| **`OCP-39`** | **The standby allowance is paid for holding the shift, not for being paged.** A quiet week is the outcome the organisation wants; paying only for pages rewards an unreliable platform |
| **`OCP-40`** | **The terms are agreed before the first shift is worked, not after.** `OP-013` OI-03 has been open since 2026-08-20 and the first shift is due at W1 |

---

## 11. Implementation — Eight Weeks

**From decision to a page that has been acknowledged.** Timed backwards from W1 go-live.

| Week | Activity | Owner | Output | Depends on |
|:--:|---|---|---|---|
| **W-8** | `SV-004-D-01` ratified; separate provider account opened; voice provider selected (`OCP-Q-03`) | CTO + Procurement | Account, contract | Steering decision |
| **W-8** | **HR terms agreed** (§10.4) — *this is the long pole and it is not technical* | HR Director + CTO | Signed policy | `OCP-Q-02` |
| **W-7** | **Rota members named** — 7 platform, 4 security | CTO + engineering leads | Eleven names | §6.6; `OCP-Q-01` |
| **W-6** | GoAlert deployed in the separate account; local accounts + MFA (`OCP-07`); PostgreSQL provisioned and backed up | Platform Engineering | Running instance | Account |
| **W-6** | SMS gateway and voice provider integrated; **first manual test page to one engineer** | Platform Engineering | Delivery confirmed | Providers |
| **W-5** | Schedules and rotations configured; escalation policies built to §8.2's six steps | Head of ITSM | Rota live in the tool | Names |
| **W-5** | `PE-008` Alertmanager and Grafana webhooks wired; severity → escalation-policy mapping per §7.2 | Platform Engineering | Alerts arriving | `PE-008` instrumented |
| **W-4** | **Every `NT-021` alert reviewed against `OCP-29`'s three-part test**; the paging set fixed and the rest demoted to tickets | Service owners | The paging alert set | `SV-003` runbooks |
| **W-4** | Heartbeat probes (`OCP-31`) deployed from outside the estate | Platform Engineering | Synthetic paging path | Independence |
| **W-3** | **Shadow shifts begin** — every member shadows two (`OP-013` `RT-06`) | Engineering leads | Competence record | Names, tool |
| **W-3** | Handover format (`OP-013` §4.9) in use; daily service review starts (`SMF-13`) | Head of ITSM | Handover log | — |
| **W-2** | **First full ladder test to the CTO step** (`OCP-24`); weekly test page scheduled (`OCP-32`) | Head of ITSM | Escalation proven | All above |
| **W-2** | Out-of-band fallback exercised (`OCP-09`); printed on-call pack issued (`RBS-30`) | Head of ITSM | Pack at head office and branches | `OP-013` §4.10 |
| **W-1** | **Game day** — an injected `Sev1` in `staging`, worked from page to runbook to resolution (`SV-003` §8.3) | Exercise lead | Ledger rows, corrections | `SV-003` |
| **W-1** | Delivery metrics reviewed against `OCP-12`'s three thresholds; **go / fallback decision** | CTO | Decision | 8 weeks of data |
| **W1** | **Go live.** Rota published 4 weeks ahead; first real shift | Head of ITSM | An unpaged platform becomes a paged one | Everything |

> **`OCP-F-03`. The critical path is not the software.** GoAlert is a container and a database and
> can be running in an afternoon. **The critical path is `W-8`'s HR agreement and `W-7`'s eleven
> names**, and both have been open as `OP-013` OI-01 and OI-03 since 2026-08-20 with no owner
> movement recorded. **An eight-week plan that starts at W-8 must start now.**

---

## 12. Measurement

Adopted from `OP-013` §4.12, with the two additions this design makes measurable.

| Measure | Definition | Target | Source |
|---|---|:--:|---|
| **Time to acknowledge (`Sev1`)** | Page → acknowledgement | **≤ 5 min, 95th percentile** | Paging platform |
| **Auto-escalations** | Pages escalated because unacknowledged ÷ all pages | **< 5%** | Paging platform |
| **Page delivery** | Pages delivered within 60 s ÷ all pages | **≥ 99%** | Paging platform + `OCP-08` |
| **Test page acknowledgement** | Weekly test pages acknowledged ÷ sent | **100%** | Paging platform |
| Pages per shift week | Total pages ÷ shifts | **≤ 5**, and ≤ 2 out of hours | Paging platform |
| Detection source | Monitoring vs human report | **≥ 90% by monitoring** (`KPI-088` context) | Incident record |
| Rota health | Members, one-in-N, `RT-04` breaches | **≥ 7 platform, ≥ 4 security, zero breaches** | Rota |
| **False-wake rate** *(new)* | Out-of-hours pages producing **no** incident record ÷ out-of-hours pages | **< 10%**, and any alert exceeding it three times a quarter is demoted (`OCP-30`) | Paging + incident register |
| **Ladder integrity** *(new)* | Quarterly end-to-end escalation tests completed and reaching the CTO step | **100%** | Test record |

> **`OCP-41`. The false-wake rate is reported to the Service Management Board every month, beside
> the acknowledgement time.** Acknowledgement time measures whether people are responding; the
> false-wake rate measures whether they should have been asked to. **Reporting the first without the
> second produces a rota that is fast and resentful, and then a rota that is neither.**

---

## 13. Governing Rules — Consolidated

| # | Rule | § |
|---|---|:--:|
| **`OCP-01`** | **A notification is not a page.** A page reaches a person on duty, escalates when unanswered, and records the answer | 3.3 |
| **`OCP-02`** | `OP-013` §4.1, §4.3's `RT-01`…`RT-08`, §4.5, §4.6, §4.7, §4.9 and §4.11 are **adopted by citation and never restated** | 6.1 |
| **`OCP-03`** | Every operational tool is tested against the **36-month horizon before selection**, not at renewal | 5.4 |
| **`OCP-04`** | A tool whose data cannot be exported in a documented format is not selected | 5.4 |
| **`OCP-05`** | The paging platform is reviewed annually against its market, at the Service Management Board | 5.4 |
| **`OCP-06`** | **The pager shares no failure domain with anything it pages about** — account, cluster, database, identity, DNS | 5.5 |
| **`OCP-07`** | The pager has **local accounts with local MFA**, a registered exception to `SC-004`'s single-IdP rule | 5.5 |
| **`OCP-08`** | **Each watches the other**: the estate monitors the pager, the pager's account monitors the estate | 5.5 |
| **`OCP-09`** | `OP-013` §4.10's out-of-band channels are the fallback when the pager itself fails | 5.5 |
| **`OCP-10`** | The rota's personal data is registered in `SC-003`; a number is removed within **one working day** of leaving the rota | 5.7 |
| **`OCP-11`** | Continuity numbers are held on the same basis and verified quarterly | 5.7 |
| **`OCP-12`** | The platform decision is **re-tested at the W2 gate** against three delivery thresholds | 5.8 |
| **`OCP-13`** | **Eid rotas are published eight weeks ahead** and volunteered for before assignment | 6.5 |
| **`OCP-14`** | No single person holds both Eid periods in one year | 6.5 |
| **`OCP-15`** | Ramadan shift boundaries move; the secondary is explicitly awake at Iftar for `P0` services | 6.5 |
| **`OCP-16`** | The rota uses **`M30`'s Bangladesh holiday set** — the same source as the SLA clock | 6.5 |
| **`OCP-17`** | **A page is justified only when a human must act now.** Everything else is a ticket | 7.1 |
| **`OCP-18`** | **The `Sev1` channel sequence is not per-person configurable.** `Sev1` always reaches voice | 7.2 |
| **`OCP-19`** | A suspected data incident **pages both rotas simultaneously** and notifies the DPO | 7.4 |
| **`OCP-20`** | Acknowledged means *"awake, seen, acting"* — not resolved | 8.1 |
| **`OCP-21`** | **Escalation is automatic and requires no decision** | 8.2 |
| **`OCP-22`** | Acknowledgement stops escalation; it does not stop the incident clock | 8.2 |
| **`OCP-23`** | **A page acknowledged and then abandoned re-escalates** at 15 minutes | 8.2 |
| **`OCP-24`** | The ladder is tested end to end to the CTO step **quarterly** | 8.2 |
| **`OCP-25`** | **Acknowledging a `Sev1` opens the incident record automatically** | 8.3 |
| **`OCP-26`** | Every page names the service `S-nn` and its **depended-on-by** set | 8.4 |
| **`OCP-27`** | Dependent-service owners are **notified, not paged** | 8.4 |
| **`OCP-28`** | **A rota member who cannot act is a pager with no hands** (`OP-013` `RT-07`) | 8.5 |
| **`OCP-29`** | An alert may page only if **actionable, novel and urgent** | 9.2 |
| **`OCP-30`** | Three out-of-hours pages in a quarter with no incident record → **demoted, without a meeting** | 9.3 |
| **`OCP-31`** | **A 60-second synthetic heartbeat pages `Sev1` on two consecutive failures, regardless of traffic volume** | 9.4 |
| **`OCP-32`** | A **weekly test page** is sent and must be acknowledged | 9.5 |
| **`OCP-33`** | A paging system that has not delivered in a week is **tested, not trusted** | 9.5 |
| **`OCP-34`** | A pager unreachable for 15 minutes is a **`Sev2`**, and the estate falls back to tier-2 SMS | 9.5 |
| **`OCP-35`** | **An unpaid, unrecognised rota does not survive its second month** | 10.1 |
| **`OCP-36`** | **`RT-05`'s late start is applied automatically from the incident record**, not requested | 10.3 |
| **`OCP-37`** | Time in lieu, minimum hour-for-hour, taken within 4 weeks — proposed, HR to ratify | 10.3 |
| **`OCP-38`** | **The allowance is identical for everyone on the same rota, regardless of grade** | 10.4 |
| **`OCP-39`** | The standby allowance is paid **for holding the shift, not for being paged** | 10.4 |
| **`OCP-40`** | **Terms are agreed before the first shift is worked** | 10.4 |
| **`OCP-41`** | The **false-wake rate is reported beside acknowledgement time**, every month | 12 |

**Findings raised by this document**

| # | Finding | Severity | Owner |
|---|---|:--:|---|
| **`OCP-F-01`** | **The platform rota needs seven people, not six.** `OP-013` §4.3's figure is correct for the primary rotation alone; with its own secondary rota and ordinary annual leave it lands at **1 in 2.7**, breaching its own `RT-04` ceiling. Total engineering rota headcount is **eleven, not ten** | **HIGH** | CTO + HR Director |
| **`OCP-F-02`** | **The rota adds no headcount and is not free.** Eleven engineers are asked for their evenings, and `SMF-15` records that hypercare wants the same people ring-fenced. **Two documents are asking eleven people for the same time and neither is funded** | **HIGH** | CFO + Programme Office |
| **`OCP-F-03`** | **The critical path is HR agreement and eleven names, not software.** Both have been open as `OP-013` OI-01 and OI-03 since 2026-08-20. An eight-week plan due at W1 must start now | **HIGH** | CTO + HR Director |
| **`OCP-F-04`** | **The two most natural paging choices for this estate are dead or dying** — Grafana OnCall OSS archived 2026-03-24, Opsgenie shutting down 2027-04-05 inside the programme horizon. Neither fact is discoverable from the estate, because `RR-005` (currency register) is unwritten | MEDIUM | Enterprise Architecture |
| **`OCP-F-05`** | **Three preconditions of an *effective* page are absent**: the 38 access profiles, the break-glass vault path, and emergency spend delegation. A paging project can report "done" with all three open and will have delivered an alarm clock | **HIGH** | Security Lead + CFO |
| **`OCP-F-06`** | **`Novu` is the estate's only current notification path for alerts (`PE-008` `RT-01`) and it has no concept of duty, acknowledgement or escalation.** The gap is architectural, not a configuration oversight | MEDIUM | Platform Engineering |

---

## 14. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| **`SV-004-D-01`** | The paging platform | (a) Opsgenie; (b) Grafana OnCall OSS; (c) Grafana Cloud IRM; (d) PagerDuty; (e) incident.io; (f) **GoAlert self-hosted in a separate account**; (g) OneUptime | **(f)**, with (c) as the named fallback | (a) and (b) fail `PR-11` outright — one shuts down inside the programme horizon, the other is archived. Among the survivors, **`PR-07` (+880 delivery at 03:00) and `PR-11` (no vendor to withdraw) decide it.** Apache-2.0 passes `AR-013` `A-01` with no exception, as K3s did | A separate provider account, a voice provider procurement, ≈ 0.5 PW to stand up. **Re-tested at W2 against `OCP-12`'s thresholds** |
| **`SV-004-D-02`** | The on-call allowance | (a) Set an amount here; (b) **specify the shape and defer the amount to HR**; (c) leave it entirely to HR | **(b)** | (a) is outside this document's authority and would be ignored; (c) is what produced `OP-013` OI-03, open since 2026-08-20 with no movement. **Specifying five elements and one rule gives HR something to price** | HR ratifies §10.4 before the first shift (`OCP-40`) |
| **`SV-004-D-03`** | Platform rota size | (a) Six, per `OP-013` §4.3; (b) **seven** | **(b)** | §6.3's arithmetic: two positions × 52 weeks ÷ (6 × 47 available weeks) = **1 in 2.7**, breaching `RT-04`. Seven gives 1 in 3.16 | +1 allocated position; the establishment in `SV-001` §8.4 is updated to **eleven** engineering rota members |
| **`SV-004-D-04`** | Identity for the paging platform | (a) Federate to Keycloak like everything else; (b) **local accounts with local MFA** | **(b)** | **An identity outage is a `Sev1`.** A pager that authenticates through the failed identity provider cannot be used to respond to its own outage — `PE-009` `BF-01`'s reasoning, applied to notification | A registered, documented exception to `SC-004`'s single-IdP rule, reviewed at each access certification |
| **`SV-004-D-05`** | Heartbeat paging | (a) Rely on burn-rate alerts alone; (b) **add a synthetic heartbeat that pages on absence** | **(b)** | `SV-002` `PSL-F-07`: a request-ratio SLI reports success by measuring nothing at 03:00 — the exact hour `S-07` and `S-08` are committed and nobody is watching | `OCP-31`; the only alert in the estate that fires on absence rather than error rate |

---

## 15. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|:--:|---|
| **`OCP-Q-01`** | **Who are the eleven people?** Seven platform, four security, named | CTO + engineering leads | **W-7 (i.e. now)** | Every subsequent step of §11 |
| **`OCP-Q-02`** | **What is the on-call allowance, the call-out rate and the Eid premium?** | HR Director + CFO | **W-8 (i.e. now)** | `OCP-40`; the rota is unenforceable without it |
| `OCP-Q-03` | Which voice provider reaches +880 mobiles reliably at 03:00, and is it contracted? | Procurement + Platform Engineering | W-8 | `PR-02`; `Sev1` escalation |
| `OCP-Q-04` | Is a separate cloud provider account funded for the pager — **and can it host the `PE-007` `BKP-3` out-of-account immutable backup too**? | CTO + CFO | W-8 | `OCP-06`. **The two requirements are the same account and should be bought once** |
| `OCP-Q-05` | Does the Steering Committee accept the platform rota at **seven** rather than six (`SV-004-D-03`)? | Steering Committee | W1 | `OCP-F-01`; `RT-04` compliance |
| `OCP-Q-06` | Do branch managers accept being on the tier-2 SMS list and the tier-3 telephone tree? | Operations Director | W1 | `OP-013` OI-06; `OCP-09`'s fallback is untested without it |
| `OCP-Q-07` | Does `SC-004` accept the local-account exception for the pager (`SV-004-D-04`)? | Security Lead | W-6 | `OCP-07` |
| `OCP-Q-08` | Does the DPO accept the rota's `SC-003` DPIA entry, and the continuity numbers' basis? | DPO | W-6 | `OCP-10`, `OCP-11` |
| `OCP-Q-09` | **Is the emergency spend delegation set** (`OP-013` §4.8 `AU-01`), or is the CTO the sole 02:00 authority? | CFO | W1 | `OCP-F-05` |

---

## 16. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | The paging gap is verified independently, not inherited from the audit | §3.2; 777 files searched at 02:15 (+06); two hits, both citations not procurements |
| `AC-02` | Twelve mandatory requirements are stated and traced | §4 — `PR-01`…`PR-12` mandatory, `PR-13`…`PR-15` desirable |
| `AC-03` | At least five candidates assessed, each with a verified lifecycle position | §2.3, §5.1 — seven candidates, two disqualified on lifecycle |
| `AC-04` | The decision states its rationale, its cost and its exit | §5.2, §5.6, §5.8 |
| `AC-05` | The independence requirement is stated as a rule with its failure modes enumerated | §5.5 — five tempting designs, each with its failure |
| `AC-06` | The rota's staffing arithmetic is **derived and shown**, not asserted | §6.3 — 104 person-weeks ÷ (N × 47 available weeks) against `RT-04` |
| `AC-07` | Severity-to-page mapping restates nothing from `OP-013` §4.1 except the paging columns | §7.2; `OCP-02` |
| `AC-08` | Every `PE-008` §8 rule is adopted or its departure is stated | §7.3, §9.3; the one departure is `SV-001` §6.7's severity ruling |
| `AC-09` | On-call terms are specified completely except the monetary amounts | §10.4; `SV-004-D-02` |
| `AC-10` | An implementation plan exists with owners, outputs and dependencies | §11 — sixteen activities across eight weeks |
| `AC-11` | The document states what a completed paging project still would not deliver | §8.5; `OCP-F-05` |
| `AC-12` | Every relative link resolves; no rule uses the form `SV-nn` | Verified at issue; §2.5 |

**Definition of done.** Complete when every criterion is met, `PGD-000` is updated with a fresh
enumeration timestamp, and the approver has signed **with HR Director co-approval of §6 and §10**.
**`AC-06`'s finding requires a Steering decision** (`OCP-Q-05`) and **`AC-09` requires HR to supply
four numbers** (`OCP-Q-02`) — neither is within this document's authority.

---

## 17. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `SV-001` §5.2, §6.7, §8.4 | The service index pages are routed against; the severity adjudication; the establishment |
| Upstream | `SV-002` §6.4 | The burn-rate tiers as commitments, and `PSL-16`/`PSL-17` |
| Upstream | `SV-003` §9.1, §10.3 | The dependency register `OCP-26` reads; `RBS-33`'s *reachable from the alert* |
| Upstream | [`PE-008`](../10_Infrastructure_DevOps_and_Environments/PE-008_Observability_and_Monitoring_Design.md) §8 | **Produces the alert this document delivers.** `AL-01`…`AL-04`, `RT-01`…`RT-04`, `AD-01`…`AD-05` adopted |
| Upstream | [`PE-009`](../10_Infrastructure_DevOps_and_Environments/PE-009_Configuration_and_Secrets_Management_Standard.md) §8 | `BF-01`, generalised to paging by `OCP-06`; the break-glass precondition in §8.5 |
| Upstream | [`PE-001`](../10_Infrastructure_DevOps_and_Environments/PE-001_Infrastructure_and_Network_Architecture_Design.md) §9 | HA by tier; why `S-03` is a total-outage dependency |
| Upstream | [`SC-003`](../05_Security_Privacy_and_Compliance/SC-003_Data_Protection_Impact_Assessment_PDPA_2026.md), [`SC-004`](../05_Security_Privacy_and_Compliance/SC-004_Identity_Authentication_and_Authorisation_Design.md) | §5.7's DPIA entry; `SV-004-D-04`'s registered exception |
| Downstream | `SV-006` | **Begins where this document ends** — the engineer is awake; command, roles and review follow |
| Downstream | `SV-005` | Hypercare requires the rota to cover its period with no gaps and no single-person weeks (`HE-09`) |
| Downstream | [`RL-003`](../12_Release_Deployment_and_Transition/RL-003_Go_Live_Readiness_Assessment_and_Gate_Criteria.md) | An acknowledged test page is go-live readiness evidence |
| Downstream | `GV-007`, `GV-008` | The eleven positions and the allowance |
| Lateral | [`OP-013`](../../project_content/17_Operations_Support_and_Runbooks/OP-013_On_Call_Escalation_and_Handover_Content.md) | Adopted by citation; **§6.3 corrects one arithmetic consequence of §4.3** |
| Lateral | [`NT-021`](../../project_content/04_Notification_and_Messaging/04D_In_App_Voice_and_System/NT-021_System_Integration_and_Job_Failure_Alert_Library.md) | The alert set reviewed against `OCP-29` at W-4 |
| Lateral | [`SP-005`](../../project_content/06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-005_Escalation_Matrix.md), [`SP-030`](../../project_content/06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-030_SOP_Health_Safety_and_Incident_Reporting.md) | The two ladders that are not this one |

---

## 18. References

**Within this repository**
[`PGD-000`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md) ·
[`_CATEGORY_OVERVIEW.md`](_CATEGORY_OVERVIEW.md) ·
`SV-001`, `SV-002`, `SV-003`, `SV-005`, `SV-006` ·
[`PE-001`](../10_Infrastructure_DevOps_and_Environments/PE-001_Infrastructure_and_Network_Architecture_Design.md) ·
[`PE-005`](../10_Infrastructure_DevOps_and_Environments/PE-005_Containerisation_and_Orchestration_Design.md) ·
[`PE-007`](../10_Infrastructure_DevOps_and_Environments/PE-007_Backup_Disaster_Recovery_and_Business_Continuity_Design.md) ·
[`PE-008`](../10_Infrastructure_DevOps_and_Environments/PE-008_Observability_and_Monitoring_Design.md) ·
[`PE-009`](../10_Infrastructure_DevOps_and_Environments/PE-009_Configuration_and_Secrets_Management_Standard.md) ·
[`SC-003`](../05_Security_Privacy_and_Compliance/SC-003_Data_Protection_Impact_Assessment_PDPA_2026.md) ·
[`SC-004`](../05_Security_Privacy_and_Compliance/SC-004_Identity_Authentication_and_Authorisation_Design.md) ·
[`SC-011`](../05_Security_Privacy_and_Compliance/SC-011_Security_Incident_Response_Plan.md) ·
[`AR-013`](../02_Architecture_and_Design/AR-013_Technology_Radar_and_Build_vs_Buy_Register.md) ·
[`RL-003`](../12_Release_Deployment_and_Transition/RL-003_Go_Live_Readiness_Assessment_and_Gate_Criteria.md)

**Workspace**
[`OP-013`](../../project_content/17_Operations_Support_and_Runbooks/OP-013_On_Call_Escalation_and_Handover_Content.md) ·
[`OP-001`](../../project_content/17_Operations_Support_and_Runbooks/OP-001_Support_Model_Tiering_and_Routing_Content.md) ·
[`OP-012`](../../project_content/17_Operations_Support_and_Runbooks/OP-012_Disaster_Recovery_and_Continuity_Playbook.md) ·
[`NT-021`](../../project_content/04_Notification_and_Messaging/04D_In_App_Voice_and_System/NT-021_System_Integration_and_Job_Failure_Alert_Library.md) ·
[`SP-005`](../../project_content/06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-005_Escalation_Matrix.md) ·
[`M66`](../../1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M66_Internal_IT_Service_Management.md) ·
[`05-06`](../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md) ·
[`AUDIT-017`](../../project_content/_AUDIT/AUDIT-017_Category_17_OP_Content_Audit.md)

**External standards and sources** *(each verified 2026-08-19)*

| Source | Verified |
|---|:--:|
| ISO/IEC 20000-1:2018 §8.6.1, §7.1, §7.2 | 2026-08-19 |
| ISO/IEC 20000-1:2018/Amd 1:2024 · https://www.iso.org/standard/88434.html | 2026-08-19 |
| Google SRE Workbook — on-call, alerting on SLOs · https://sre.google/workbook/alerting-on-slos/ | 2026-08-19 |
| **Atlassian Opsgenie lifecycle** — end of sale 2025-06-04; **shutdown 2027-04-05**; non-migrated data deleted; capability split to Jira Service Management and Compass | 2026-08-19 |
| **Grafana OnCall (OSS)** — maintenance mode 2025-03-11; **repository archived 2026-03-24**; Grafana Cloud SMS/voice relay deprecated; successor is Grafana Cloud IRM (free ≤ 3 active users, then ≈ USD 20/active user/month) | 2026-08-19 |
| **GoAlert** — Apache-2.0; on-call scheduling, escalation policies and notifications; single Go binary with PostgreSQL; Docker images per release; **repository updated 2026-07-27**; maintained by Target · https://github.com/target/goalert | 2026-08-19 |
| OneUptime — Apache-2.0; monitoring, status pages and on-call in one package | 2026-08-19 |

---

## 19. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-19 | Head of IT Service Management | Initial issue. Rule space `OCP` allocated after verification against 777 files. Paging platform selected against twelve mandatory requirements from a seven-candidate scan, **two candidates disqualified on verified lifecycle grounds**. Rota arithmetic re-derived, finding the platform pool **one person short of `OP-013`'s own `RT-04` ceiling**. Eight-week implementation plan. Five decisions, six findings, nine open questions — of which two are the critical path and both have been open since 2026-08-20 | Chief Technology Officer, **with HR Director co-approval of §6 and §10** *(both pending)* |
| **1.1** | **2026-08-19** | Head of IT Service Management | **Conformance to `RR-002` `IDC-08`** (timestamp and denominator in `rule_prefix:`). **`CO-003` was issued during authoring** and the front matter is corrected. `RR-002` itself is now issued, which does **not** affect `OCP-F-04` — `RR-005`, the standards-currency register that would have caught the Opsgenie and Grafana OnCall lifecycle facts, remains unwritten. | As above |

---

*`SV-004` · Category 11 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
